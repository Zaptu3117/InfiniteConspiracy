"""Conspiracy Pipeline - orchestrates complete conspiracy mystery generation."""

import logging
import asyncio
from typing import Dict, Any
from pathlib import Path
import json

from models.conspiracy import ConspiracyMystery
from .political_context_generator import PoliticalContextGenerator
from .conspiracy_generator import ConspiracyGenerator
from .subgraph_generator import SubGraphGenerator
from .nodes import (
    IdentityNodeGenerator,
    PsychologicalNodeGenerator,
    CryptoNodeGenerator
)
from .document_subgraph_mapper import DocumentSubGraphMapper
from .document_generator import ConstrainedDocumentGenerator
from .character_enhancer import CharacterEnhancer
from .image_clue_mapper import ImageClueMapper
from .red_herring_builder import RedHerringBuilder
from validation.conspiracy_validator import ConspiracyValidator


logger = logging.getLogger(__name__)


class ConspiracyPipeline:
    """Complete conspiracy mystery generation pipeline."""
    
    def __init__(self, llm_client, config: Dict[str, Any], replicate_token: str = None):
        """
        Initialize pipeline.
        
        Args:
            llm_client: LLM client for generation
            config: Configuration dictionary
            replicate_token: Optional Replicate API token for image generation
        """
        self.llm = llm_client
        self.config = config
        
        # Initialize components
        self.political_gen = PoliticalContextGenerator(llm_client)
        self.conspiracy_gen = ConspiracyGenerator(llm_client)
        self.subgraph_gen = SubGraphGenerator()
        
        self.identity_gen = IdentityNodeGenerator()
        self.psychological_gen = PsychologicalNodeGenerator(llm_client)
        self.crypto_gen = CryptoNodeGenerator(llm_client)
        
        self.doc_mapper = DocumentSubGraphMapper()
        self.doc_generator = ConstrainedDocumentGenerator(llm_client)
        self.char_enhancer = CharacterEnhancer(llm_client)
        self.image_mapper = ImageClueMapper()
        self.red_herring_builder = RedHerringBuilder()
        self.validator = ConspiracyValidator(llm_client)
        
        # Image generation (optional)
        self.image_generator = None
        if replicate_token:
            from images import ImageGenerator
            image_config = config.get("image_generation", {})
            model = image_config.get("replicate_model", "black-forest-labs/flux-schnell")
            self.image_generator = ImageGenerator(replicate_token, model)
    
    async def generate_conspiracy_mystery(
        self,
        difficulty: int = 7,
        num_documents: int = 20,
        conspiracy_type: str = "occult"
    ) -> ConspiracyMystery:
        """
        Generate complete conspiracy mystery.
        
        Args:
            difficulty: Mystery difficulty (1-10)
            num_documents: Target number of documents
            conspiracy_type: Type of conspiracy (occult, secret_society, underground_network)
        
        Returns:
            Complete ConspiracyMystery object
        """
        logger.info("╔" + "="*58 + "╗")
        logger.info("║" + " "*12 + "CONSPIRACY MYSTERY GENERATION" + " "*17 + "║")
        logger.info("╚" + "="*58 + "╝")
        logger.info("")
        
        # PHASE 1: Political Context
        logger.info("="*60)
        logger.info("PHASE 1: POLITICAL CONTEXT")
        logger.info("="*60)
        political_context = await self.political_gen.generate_political_context(
            conspiracy_type=conspiracy_type,
            difficulty=difficulty,
            config=self.config.get("political_context", {})
        )
        
        # PHASE 2: Conspiracy Premise (4 dimensions)
        logger.info("="*60)
        logger.info("PHASE 2: CONSPIRACY PREMISE")
        logger.info("="*60)
        premise = await self.conspiracy_gen.generate_conspiracy(
            political_context=political_context,
            difficulty=difficulty,
            conspiracy_type=conspiracy_type,
            config=self.config.get("conspiracy", {})
        )
        
        # PHASE 3: Sub-Graph Generation
        logger.info("="*60)
        logger.info("PHASE 3: SUB-GRAPH GENERATION")
        logger.info("="*60)
        subgraphs = self.subgraph_gen.generate_subgraphs(
            premise=premise,
            political_context=political_context,
            difficulty=difficulty,
            num_documents=num_documents
        )
        
        # PHASE 4: Evidence Node Population
        logger.info("="*60)
        logger.info("PHASE 4: EVIDENCE NODE GENERATION")
        logger.info("="*60)
        await self._populate_evidence_nodes(subgraphs, premise, political_context, difficulty)
        
        # PHASE 5: Character Generation (will be enhanced later)
        logger.info("="*60)
        logger.info("PHASE 5: CHARACTER GENERATION")
        logger.info("="*60)
        characters = await self._generate_characters(premise, political_context, difficulty)
        
        # PHASE 6: Crypto Key Enhancement
        logger.info("="*60)
        logger.info("PHASE 6: CHARACTER CRYPTO ENHANCEMENT")
        logger.info("="*60)
        crypto_keys = self._collect_crypto_keys(subgraphs)
        characters = await self.char_enhancer.enhance_characters_with_keys(
            characters,
            crypto_keys,
            political_context,
            self.config.get("character_enhancement", {})
        )
        
        # PHASE 7: Document Mapping
        logger.info("="*60)
        logger.info("PHASE 7: DOCUMENT MAPPING")
        logger.info("="*60)
        assignments = self.doc_mapper.map_subgraphs_to_documents(
            subgraphs,
            num_documents,
            self.config.get("document_mapping", {})
        )
        
        # PHASE 8: Document Generation
        logger.info("="*60)
        logger.info("PHASE 8: DOCUMENT GENERATION")
        logger.info("="*60)
        documents = await self.doc_generator.generate_documents(
            assignments,
            subgraphs,
            premise,
            political_context,
            crypto_keys,
            characters,
            self.config.get("document_generation", {})
        )
        
        # PHASE 9: Red Herring Integration
        logger.info("="*60)
        logger.info("PHASE 9: RED HERRING INTEGRATION")
        logger.info("="*60)
        red_herring_subgraphs = [sg for sg in subgraphs if sg.is_red_herring]
        documents = self.red_herring_builder.integrate_red_herrings(
            documents,
            red_herring_subgraphs,
            self.config.get("red_herrings", {})
        )
        
        # PHASE 10: Image Clue Mapping
        logger.info("="*60)
        logger.info("PHASE 10: IMAGE CLUE MAPPING")
        logger.info("="*60)
        num_images = self.config.get("num_images", 5)
        image_clues = self.image_mapper.map_evidence_to_images(subgraphs, num_images)
        
        # PHASE 11: Image Generation (optional)
        generated_images = []
        if self.image_generator and image_clues:
            logger.info("="*60)
            logger.info("PHASE 11: IMAGE GENERATION")
            logger.info("="*60)
            generated_images = await self._generate_images(image_clues, premise)
        
        # PHASE 12: Package Mystery
        logger.info("="*60)
        logger.info("PHASE 12: PACKAGING MYSTERY")
        logger.info("="*60)
        mystery = self._package_mystery(
            political_context,
            premise,
            subgraphs,
            crypto_keys,
            assignments,
            documents,
            characters,
            image_clues,
            difficulty
        )
        
        logger.info(f"   ✅ Mystery packaged")
        logger.info(f"      ID: {mystery.mystery_id}")
        logger.info(f"      Documents: {len(mystery.documents)}")
        logger.info(f"      Sub-graphs: {len(mystery.subgraphs)}")
        logger.info(f"      Crypto keys: {len(mystery.crypto_keys)}")
        logger.info("")
        
        # PHASE 13: Validation
        logger.info("="*60)
        logger.info("PHASE 13: VALIDATION")
        logger.info("="*60)
        validation_result = await self.validator.validate_conspiracy(
            mystery,
            self.config.get("validation", {})
        )
        
        # Save mystery (with generated images)
        self._save_mystery(mystery, validation_result, generated_images)
        
        logger.info("="*60)
        logger.info("✅ CONSPIRACY MYSTERY GENERATION COMPLETE")
        logger.info("="*60)
        logger.info("")
        
        return mystery
    
    async def _populate_evidence_nodes(
        self,
        subgraphs,
        premise,
        political_context,
        difficulty
    ):
        """Populate evidence nodes for all sub-graphs."""
        
        logger.info("   Populating evidence nodes...")
        
        # Get architectures (simplified - would normally use from subgraph_types)
        from .subgraph_types import get_architecture_for_type
        
        for sg in subgraphs:
            if sg.is_red_herring:
                continue  # Skip detailed generation for red herrings
            
            architecture = get_architecture_for_type(sg.subgraph_type.value, difficulty)
            
            if sg.subgraph_type.value == "identity":
                # Get target name from premise WHO
                target_name = premise.who.split()[0] if premise.who else "Agent"
                evidence_nodes, inference_nodes = self.identity_gen.generate_identity_chain(
                    sg.subgraph_id,
                    target_name,
                    difficulty,
                    architecture
                )
                sg.evidence_nodes = evidence_nodes
                sg.inference_nodes = inference_nodes
            
            elif sg.subgraph_type.value == "psychological":
                evidence_nodes, inference_nodes = await self.psychological_gen.generate_psychological_chain(
                    sg.subgraph_id,
                    premise,
                    political_context,
                    architecture,
                    self.config.get("psychological", {})
                )
                sg.evidence_nodes = evidence_nodes
                sg.inference_nodes = inference_nodes
            
            elif sg.subgraph_type.value == "cryptographic":
                evidence_nodes, inference_nodes, crypto_keys = await self.crypto_gen.generate_crypto_chain(
                    sg.subgraph_id,
                    premise,
                    [],  # Characters not yet generated
                    architecture,
                    sg.contributes_to,
                    self.config.get("cryptographic", {})
                )
                sg.evidence_nodes = evidence_nodes
                sg.inference_nodes = inference_nodes
                # Crypto keys will be collected later
        
        logger.info(f"   ✅ Populated {len(subgraphs)} sub-graphs")
    
    async def _generate_characters(self, premise, political_context, difficulty):
        """Generate initial characters."""
        import random
        
        # Extract conspirator names from premise
        names = premise.who.split(",")[:4]  # Up to 4 conspirators
        
        characters = []
        for name in names:
            name = name.strip()
            char = {
                "name": name,
                "role": random.choice(["Agent", "Director", "Operative", "Analyst"]),
                "background": f"Member of the conspiracy. Connected to {political_context.world_name}.",
                "personality": random.choice(["calculating", "paranoid", "idealistic", "ruthless"])
            }
            characters.append(char)
        
        logger.info(f"   Generated {len(characters)} characters")
        return characters
    
    def _collect_crypto_keys(self, subgraphs):
        """Collect all crypto keys from sub-graphs."""
        # In full implementation, would extract from crypto nodes
        # For now, return empty list (keys are embedded in nodes)
        return []
    
    async def _generate_images(self, image_clues, premise):
        """Generate actual images from image clue prompts."""
        logger.info(f"🖼️  Generating {len(image_clues)} images...")
        
        # Create temporary output directory
        temp_dir = Path("outputs/temp_images")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        generated_images = []
        
        for img_clue in image_clues:
            img_id = "unknown"
            try:
                # ImageClue is a dataclass, access attributes directly
                img_id = img_clue.image_id
                prompt = img_clue.prompt
                
                # Enhance prompt with conspiracy context
                enhanced_prompt = f"{prompt}. Dark atmosphere, mysterious, cinematic lighting, high quality, detailed"
                
                logger.info(f"   Generating: {img_id}")
                
                result = await self.image_generator.generate_image(
                    prompt=enhanced_prompt,
                    image_id=img_id,
                    output_dir=temp_dir
                )
                
                if result:
                    generated_images.append(result)
                    logger.info(f"   ✅ Generated: {img_id}")
                
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to generate {img_id}: {e}")
        
        logger.info(f"   ✅ Generated {len(generated_images)}/{len(image_clues)} images")
        logger.info("")
        
        return generated_images
    
    def _package_mystery(
        self,
        political_context,
        premise,
        subgraphs,
        crypto_keys,
        assignments,
        documents,
        characters,
        image_clues,
        difficulty
    ):
        """Package everything into ConspiracyMystery object."""
        import uuid
        from datetime import datetime
        
        mystery_id = str(uuid.uuid4())
        
        mystery = ConspiracyMystery(
            mystery_id=mystery_id,
            political_context=political_context,
            premise=premise,
            subgraphs=subgraphs,
            crypto_keys=crypto_keys,
            document_assignments=assignments,
            image_clues=image_clues,
            characters=characters,
            documents=documents,
            difficulty=difficulty,
            created_at=datetime.now().isoformat()
        )
        
        return mystery
    
    def _save_mystery(self, mystery, validation_result, generated_images=None):
        """Save mystery to output directory with organized structure."""
        import re
        import shutil
        
        # Create folder name from conspiracy name + short UUID
        conspiracy_name = mystery.premise.conspiracy_name
        # Sanitize name for folder
        safe_name = re.sub(r'[^\w\s-]', '', conspiracy_name).strip()
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        short_uuid = mystery.mystery_id[:8]
        folder_name = f"{safe_name}_{short_uuid}"
        
        # Create mystery folder
        mystery_dir = Path("outputs/conspiracies") / folder_name
        mystery_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        docs_dir = mystery_dir / "documents"
        images_dir = mystery_dir / "images"
        docs_dir.mkdir(exist_ok=True)
        images_dir.mkdir(exist_ok=True)
        
        # Save main mystery file
        mystery_file = mystery_dir / "mystery.json"
        with open(mystery_file, 'w') as f:
            json.dump(mystery.to_dict(), f, indent=2)
        
        # Save individual documents
        for doc in mystery.documents:
            doc_id = doc.get("document_id", "unknown")
            doc_file = docs_dir / f"{doc_id}.json"
            with open(doc_file, 'w') as f:
                json.dump(doc, f, indent=2)
        
        # Save image clue prompts
        for img_clue in mystery.image_clues:
            img_id = img_clue.image_id
            img_file = images_dir / f"{img_id}_prompt.json"
            with open(img_file, 'w') as f:
                json.dump(img_clue.to_dict(), f, indent=2)
        
        # Copy generated images
        if generated_images:
            for img_result in generated_images:
                try:
                    source_path = Path(img_result["path"])
                    if source_path.exists():
                        dest_path = images_dir / source_path.name
                        shutil.copy2(source_path, dest_path)
                        logger.info(f"   📸 Copied image: {source_path.name}")
                except Exception as e:
                    logger.warning(f"   ⚠️  Failed to copy image: {e}")
        
        # Save validation
        validation_file = mystery_dir / "validation.json"
        with open(validation_file, 'w') as f:
            json.dump({
                "is_valid": validation_result.is_valid,
                "reason": validation_result.reason,
                "who_solvable": validation_result.who_solvable,
                "what_solvable": validation_result.what_solvable,
                "why_solvable": validation_result.why_solvable,
                "how_solvable": validation_result.how_solvable,
                "single_llm_failed": validation_result.single_llm_failed,
                "multi_hop_succeeded": validation_result.multi_hop_succeeded,
                "crypto_discoverable": validation_result.crypto_discoverable
            }, f, indent=2)
        
        # Save summary README
        readme_file = mystery_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(f"# {conspiracy_name}\n\n")
            f.write(f"**Mystery ID:** {mystery.mystery_id}\n\n")
            f.write(f"**World:** {mystery.political_context.world_name}\n\n")
            f.write(f"**Difficulty:** {mystery.difficulty}/10\n\n")
            f.write(f"## The Conspiracy\n\n")
            f.write(f"**WHO:** {mystery.premise.who[:200]}...\n\n")
            f.write(f"**WHAT:** {mystery.premise.what[:200]}...\n\n")
            f.write(f"**WHY:** {mystery.premise.why[:200]}...\n\n")
            f.write(f"**HOW:** {mystery.premise.how[:200]}...\n\n")
            f.write(f"## Evidence Structure\n\n")
            f.write(f"- **Documents:** {len(mystery.documents)}\n")
            f.write(f"- **Sub-graphs:** {len(mystery.subgraphs)}\n")
            f.write(f"- **Image clues:** {len(mystery.image_clues)}\n")
            f.write(f"- **Characters:** {len(mystery.characters)}\n\n")
            f.write(f"## Files\n\n")
            f.write(f"- `mystery.json` - Complete mystery data\n")
            f.write(f"- `validation.json` - Validation results\n")
            f.write(f"- `documents/` - Individual document files\n")
            f.write(f"- `images/` - Image clue prompts\n")
        
        logger.info(f"   💾 Mystery saved: {folder_name}")
        logger.info(f"      📁 {len(mystery.documents)} documents")
        logger.info(f"      🖼️  {len(mystery.image_clues)} image prompts")

