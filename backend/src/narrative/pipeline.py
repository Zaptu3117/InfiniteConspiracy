"""Main LLM Narrative Pipeline - orchestrates complete mystery generation."""

import logging
from typing import Dict, Any
from pathlib import Path

from ..models import Mystery, MysteryMetadata
from .narrator import NarratorOrchestrator
from .document_gen import ParallelDocumentGenerator
from .graph import NarrativeGraph
from .crypto_integrator import CryptoIntegrator
from .red_herrings import RedHerringGenerator
from ..images import ImageGenerator, VLMValidator
from ..utils import OpenAIClient


logger = logging.getLogger(__name__)


class LLMNarrativePipeline:
    """
    Complete LLM-based narrative generation pipeline.
    
    Flow:
    1. Create proof tree (external, provides clues)
    2. Narrator: Build narrative graph (5 LLM steps)
    3. Document Generation: Generate all documents (parallel LLM calls)
    4. Package into Mystery object
    """
    
    def __init__(self, llm_client, config: Dict[str, Any], replicate_token: str = None, openai_key: str = None):
        """
        Initialize pipeline.
        
        Args:
            llm_client: LLM client (Cerebras)
            config: Complete configuration dictionary
            replicate_token: Replicate API token (optional, for image generation)
            openai_key: OpenAI API key (optional, for image validation)
        """
        self.llm = llm_client
        self.config = config
        
        # Initialize subsystems
        narrator_config = config.get("narrator", {})
        self.narrator = NarratorOrchestrator(llm_client, narrator_config)
        
        doc_gen_config = config.get("document_generation", {})
        self.doc_generator = ParallelDocumentGenerator(llm_client, doc_gen_config)
        
        # Image generation (optional)
        self.image_generator = None
        self.vlm_validator = None
        
        if replicate_token:
            image_config = config.get("image_generation", {})
            model = image_config.get("replicate_model", "black-forest-labs/flux-schnell")
            self.image_generator = ImageGenerator(replicate_token, model)
            
        if openai_key:
            openai_client = OpenAIClient(openai_key)
            self.vlm_validator = VLMValidator(openai_client)
    
    async def generate_mystery_with_llm(
        self,
        difficulty: int = 5,
        num_docs: int = 20
    ) -> Mystery:
        """
        Generate complete mystery using LLM pipeline.
        
        Args:
            difficulty: Mystery difficulty (1-10)
            num_docs: Target number of documents
        
        Returns:
            Complete Mystery object ready for Arkiv/blockchain
        """
        logger.info("╔" + "="*58 + "╗")
        logger.info("║" + " "*15 + "LLM MYSTERY GENERATION" + " "*21 + "║")
        logger.info("╚" + "="*58 + "╝")
        logger.info("")
        
        # PHASE 1: NARRATOR (7 steps including premise and proof tree)
        # Note: Premise generation happens inside narrator now
        narrative_graph, proof_tree, question, answer = await self.narrator.build_narrative_graph(
            mystery_question=None,  # Let narrator generate it
            mystery_answer=None,    # Let narrator generate it
            difficulty=difficulty,
            num_documents=num_docs
        )
        
        # Save narrative graph
        self._save_narrative_graph(narrative_graph)
        
        # PHASE 2: DOCUMENT GENERATION (parallel)
        documents = await self.doc_generator.generate_all_documents(
            narrative_graph
        )
        
        # PHASE 2.5: APPLY CRYPTOGRAPHY (with cross-referenced keys)
        crypto_config = self.config.get("cryptography", {})
        if crypto_config.get("enabled", True):
            crypto_integrator = CryptoIntegrator()
            documents = crypto_integrator.apply_cryptography(documents, crypto_config)
        else:
            logger.info("="*60)
            logger.info("⏭️  SKIPPING CRYPTOGRAPHY")
            logger.info("="*60)
            logger.info("   Reason: Disabled in config")
            logger.info("")
        
        # PHASE 2.6: ADD RED HERRINGS (subtle false leads)
        red_herring_config = self.config.get("red_herrings", {})
        if red_herring_config.get("enabled", True):
            red_herring_gen = RedHerringGenerator()
            documents = red_herring_gen.add_red_herrings(documents, red_herring_config)
        else:
            logger.info("="*60)
            logger.info("⏭️  SKIPPING RED HERRINGS")
            logger.info("="*60)
            logger.info("   Reason: Disabled in config")
            logger.info("")
        
        # PHASE 3: IMAGE GENERATION (optional, parallel)
        images = []
        if self.image_generator:
            images = await self._generate_images(narrative_graph, num_docs)
        else:
            logger.info("="*60)
            logger.info("⏭️  SKIPPING IMAGE GENERATION")
            logger.info("="*60)
            logger.info("   Reason: No Replicate API token provided")
            logger.info("")
        
        # STEP 4: Package into Mystery
        logger.info("="*60)
        logger.info("📦 PACKAGING MYSTERY")
        logger.info("="*60)
        
        mystery = self._package_mystery(
            question=question,
            answer=answer,
            difficulty=difficulty,
            proof_tree=proof_tree,
            documents=documents,
            images=images,
            narrative_graph=narrative_graph
        )
        
        logger.info(f"   ✅ Mystery packaged: {mystery.metadata.mystery_id}")
        logger.info(f"   Documents: {len(mystery.documents)}")
        logger.info(f"   Images: {len(mystery.images)} (planned)")
        logger.info("")
        
        logger.info("="*60)
        logger.info("✅ LLM GENERATION COMPLETE!")
        logger.info("="*60)
        logger.info("")
        
        return mystery
    
    
    def _save_narrative_graph(self, graph: NarrativeGraph):
        """Save narrative graph for reference."""
        import json
        
        # Create outputs directory
        outputs_dir = Path("outputs/narratives")
        outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Save graph
        graph_file = outputs_dir / f"{graph.mystery_question[:30].replace(' ', '_')}.json"
        with open(graph_file, 'w') as f:
            json.dump(graph.to_dict(), f, indent=2)
        
        logger.info(f"   💾 Narrative graph saved: {graph_file.name}")
    
    async def _generate_images(
        self,
        narrative_graph: NarrativeGraph,
        num_docs: int
    ) -> list:
        """Generate images for the mystery."""
        logger.info("="*60)
        logger.info("🖼️  GENERATING IMAGES")
        logger.info("="*60)
        
        # Decide how many images (roughly 1 per 3 documents)
        num_images = max(3, min(10, num_docs // 3))
        logger.info(f"   Target images: {num_images}")
        
        # Create image specifications from document plan
        image_specs = []
        for i, doc_plan in enumerate(narrative_graph.document_plan[:num_images]):
            # Create prompt based on document content
            prompt = self._create_image_prompt(doc_plan, narrative_graph)
            
            image_specs.append({
                "image_id": f"img_{doc_plan.doc_id}",
                "prompt": prompt
            })
        
        # Generate images
        output_dir = Path("outputs/images")
        images = await self.image_generator.generate_batch(image_specs, output_dir)
        
        # Validate with VLM if available
        if self.vlm_validator and images:
            logger.info("")
            logger.info("🔍 Validating images with VLM...")
            
            validation_specs = []
            for img in images:
                # Extract required elements from prompt
                required = ["evidence", "clue"]  # Simplified
                validation_specs.append({
                    "image_id": img["image_id"],
                    "image_url": img["url"],
                    "required_elements": required
                })
            
            validations = await self.vlm_validator.validate_batch(validation_specs)
            
            # Filter to validated images only
            validated_images = []
            for img, validation in zip(images, validations):
                if validation.get("passed", False):
                    img["validation"] = validation
                    validated_images.append(img)
            
            logger.info(f"   ✅ {len(validated_images)}/{len(images)} images passed validation")
            images = validated_images
        
        return images
    
    def _create_image_prompt(
        self,
        doc_plan,
        narrative_graph: NarrativeGraph
    ) -> str:
        """Create image generation prompt from document plan."""
        # Get document context
        doc_type = doc_plan.doc_type
        author = doc_plan.author
        
        # Create contextual prompt
        prompts_by_type = {
            "email": "A computer screen showing an email with visible text",
            "diary": "A handwritten diary page with legible entries",
            "police_report": "An official police document with stamps and signatures",
            "badge_log": "A security access log showing entry times and badge numbers",
            "newspaper": "A newspaper article with headline and text",
            "receipt": "A receipt with itemized purchases and prices visible",
            "surveillance_log": "Security monitoring log with timestamps",
        }
        
        base_prompt = prompts_by_type.get(
            doc_type,
            f"A {doc_type} document with visible details"
        )
        
        return f"{base_prompt}, professional, high quality, photorealistic"
    
    def _package_mystery(
        self,
        question: str,
        answer: str,
        difficulty: int,
        proof_tree: Dict[str, Any],
        documents: list,
        images: list,
        narrative_graph: NarrativeGraph
    ) -> Mystery:
        """Package everything into Mystery object."""
        
        # Create metadata
        metadata = MysteryMetadata(
            question=question,
            difficulty=difficulty,
            total_documents=len(documents),
            total_images=len(images)
        )
        
        # Create mystery
        mystery = Mystery(
            metadata=metadata,
            answer=answer,
            proof_tree=proof_tree,
            documents=documents,
            images=images,
            validation_passed=True,  # Would need validation step
            validation_details={
                "narrative_graph_generated": True,
                "documents_generated": len(documents),
                "images_generated": len(images),
                "characters": len(narrative_graph.characters),
                "timeline_events": len(narrative_graph.timeline)
            }
        )
        
        # Generate hashes
        mystery.generate_hashes()
        
        return mystery

