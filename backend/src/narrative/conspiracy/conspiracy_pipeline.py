"""Conspiracy Pipeline - orchestrates complete conspiracy mystery generation."""

import logging
import asyncio
from typing import Dict, Any, List
from pathlib import Path
import json

from models.conspiracy import ConspiracyMystery, SubGraph
from .political_context_generator import PoliticalContextGenerator
from .conspiracy_generator import ConspiracyGenerator
from .answer_template_generator import AnswerTemplateGenerator
from .question_generator import QuestionGenerator
from .document_name_generator import DocumentNameGenerator
from .subgraph_generator import SubGraphGenerator
from .nodes import (
    IdentityNodeGenerator,
    PsychologicalNodeGenerator,
    CryptoNodeGenerator
)
from .document_subgraph_mapper import DocumentSubGraphMapper
from .document_generator import ConstrainedDocumentGenerator
from .document_narrative_planner import DocumentNarrativePlanner
from .document_renderer import DocumentRenderer
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
        self.answer_template_gen = AnswerTemplateGenerator(llm_client)  # Now uses LLM for semantic extraction
        self.doc_name_gen = DocumentNameGenerator()
        self.subgraph_gen = SubGraphGenerator()
        
        self.identity_gen = IdentityNodeGenerator()
        self.psychological_gen = PsychologicalNodeGenerator(llm_client)
        self.crypto_gen = CryptoNodeGenerator(llm_client)
        
        self.doc_mapper = DocumentSubGraphMapper()
        self.doc_generator = ConstrainedDocumentGenerator(llm_client)
        self.doc_planner = DocumentNarrativePlanner(llm_client)  # NEW: Planning layer with LLM
        self.doc_renderer = DocumentRenderer(llm_client)  # NEW: Rendering layer
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
        
        # PHASE 3: Answer Template Extraction
        logger.info("="*60)
        logger.info("PHASE 3: ANSWER TEMPLATE EXTRACTION")
        logger.info("="*60)
        answer_template = await self.answer_template_gen.extract_from_premise(premise)
        logger.info(f"   WHO: {answer_template.who}")
        logger.info(f"   WHAT: {answer_template.what}")
        logger.info(f"   WHY: {answer_template.why}")
        logger.info(f"   HOW: {answer_template.how}")
        logger.info(f"   Hash: {answer_template.combined_hash[:16]}...")
        
        # PHASE 3.5: Question Generation
        logger.info("="*60)
        logger.info("PHASE 3.5: QUESTION GENERATION")
        logger.info("="*60)
        question_gen = QuestionGenerator(self.llm)
        questions = await question_gen.generate_questions(premise, answer_template)
        logger.info(f"   WHO Question: {questions['who']}")
        logger.info(f"   WHAT Question: {questions['what']}")
        logger.info(f"   WHY Question: {questions['why']}")
        logger.info(f"   HOW Question: {questions['how']}")
        
        # PHASE 4: Sub-Graph Generation (renumbered)
        logger.info("="*60)
        logger.info("PHASE 4: SUB-GRAPH GENERATION")
        logger.info("="*60)
        subgraphs = self.subgraph_gen.generate_subgraphs(
            premise=premise,
            political_context=political_context,
            difficulty=difficulty,
            num_documents=num_documents
        )
        
        # PHASE 4: Character Generation (must come before evidence nodes)
        logger.info("="*60)
        logger.info("PHASE 4: CHARACTER GENERATION")
        logger.info("="*60)
        characters = await self._generate_characters(premise, political_context, answer_template, difficulty)
        
        # PHASE 5: Evidence Node Population (uses characters for distribution)
        logger.info("="*60)
        logger.info("PHASE 5: EVIDENCE NODE GENERATION")
        logger.info("="*60)
        await self._populate_evidence_nodes(subgraphs, premise, political_context, difficulty, answer_template, characters)
        
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
        
        # PHASE 7: Document Narrative Planning (NEW - Intelligence Layer with LLM)
        logger.info("="*60)
        logger.info("PHASE 7: DOCUMENT NARRATIVE PLANNING (LLM-based fact extraction)")
        logger.info("="*60)
        document_plans = await self.doc_planner.create_narrative_plans(
            subgraphs=subgraphs,
            answer_template=answer_template,
            characters=characters,
            political_context=political_context,
            premise=premise,
            num_documents=num_documents,
            difficulty=difficulty
        )
        logger.info(f"   ✅ Created {len(document_plans)} narrative plans")
        
        # PHASE 8: Document Rendering (NEW - Pure Rendering)
        logger.info("="*60)
        logger.info("PHASE 8: DOCUMENT RENDERING")
        logger.info("="*60)
        documents = await self.doc_renderer.render_documents(
            plans=document_plans,
            characters=characters,
            premise=premise,
            political_context=political_context,
            config=self.config.get("document_generation", {})
        )
        logger.info(f"   ✅ Rendered {len(documents)} documents")
        
        # PHASE 8b: Generate Neutral Document Names (for on-chain)
        logger.info("="*60)
        logger.info("PHASE 8B: GENERATING NEUTRAL DOCUMENT NAMES")
        logger.info("="*60)
        # Generate simple names based on document type
        for doc in documents:
            doc_id = doc.get("document_id", "unknown")
            doc_type = doc.get("document_type", "document")
            # Simple name generation based on type
            doc["document_name"] = f"{doc_type}_{doc_id}.json"
        
        logger.info(f"   ✅ Generated neutral document names for {len(documents)} documents")
        
        # PHASE 8c: Populate Inference Node Document IDs
        logger.info("="*60)
        logger.info("PHASE 8C: LINKING INFERENCE NODES TO DOCUMENTS")
        logger.info("="*60)
        self._populate_inference_node_document_ids(subgraphs, document_plans, documents)
        logger.info(f"   ✅ Linked inference nodes to documents")
        
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
        
        # Legacy assignments not used in new architecture
        assignments = []
        
        mystery = self._package_mystery(
            political_context,
            premise,
            answer_template,
            questions,
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
        difficulty,
        answer_template,
        characters
    ):
        """Populate evidence nodes for all sub-graphs using discoverable answer values."""
        
        logger.info("   Populating evidence nodes...")
        logger.info(f"   ⚠️  Using answer template values in evidence:")
        logger.info(f"      WHO: {answer_template.who}")
        logger.info(f"      WHAT: {answer_template.what}")
        logger.info(f"      WHY: {answer_template.why}")
        logger.info(f"      HOW: {answer_template.how}")
        logger.info(f"   📋 Distributing identity chains across {len(characters)} characters")
        
        # Get architectures (simplified - would normally use from subgraph_types)
        from .subgraph_types import get_architecture_for_type
        
        # Track identity chain index for distribution
        identity_chain_index = 0
        
        for sg in subgraphs:
            if sg.is_red_herring:
                continue  # Skip detailed generation for red herrings
            
            architecture = get_architecture_for_type(sg.subgraph_type.value, difficulty)
            
            if sg.subgraph_type.value == "identity":
                # ✅ Distribute identity chains across different characters
                target_character = self._select_target_for_identity_chain(
                    characters,
                    identity_chain_index,
                    answer_template
                )
                logger.info(f"   🔍 Identity chain {identity_chain_index} → {target_character['name']} ({target_character['involvement_level']})")
                evidence_nodes, inference_nodes = self.identity_gen.generate_identity_chain(
                    sg.subgraph_id,
                    target_character,
                    difficulty,
                    architecture
                )
                sg.evidence_nodes = evidence_nodes
                sg.inference_nodes = inference_nodes
                identity_chain_index += 1
            
            elif sg.subgraph_type.value == "psychological":
                evidence_nodes, inference_nodes = await self.psychological_gen.generate_psychological_chain(
                    sg.subgraph_id,
                    premise,
                    political_context,
                    architecture,
                    answer_template,
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
                    answer_template,
                    self.config.get("cryptographic", {})
                )
                sg.evidence_nodes = evidence_nodes
                sg.inference_nodes = inference_nodes
                # Store crypto keys in subgraph for later collection
                if not hasattr(sg, 'crypto_keys'):
                    sg.crypto_keys = []
                sg.crypto_keys.extend(crypto_keys)
        
        logger.info(f"   ✅ Populated {len(subgraphs)} sub-graphs")
    
    async def _generate_characters(self, premise, political_context, answer_template, difficulty):
        """
        Generate 10-15 diverse characters.
        
        Strategy:
        - 1 primary conspirator (THE answer to WHO)
        - 3-4 secondary conspirators (involved but not the leader)
        - 5-8 innocent characters (witnesses, colleagues, red herrings)
        
        Args:
            premise: Conspiracy premise
            political_context: Political context
            answer_template: Answer template with WHO answer
            difficulty: Difficulty level
        
        Returns:
            List of character dictionaries
        """
        import random
        
        characters = []
        
        # 1. PRIMARY CONSPIRATOR (THE answer)
        primary_name = answer_template.who
        primary_char = {
            "name": primary_name,
            "is_primary": True,
            "involvement_level": "leader",
            "clearance_level": "top_secret",
            "role": "Chief Orchestrator",
            "background": f"Mastermind behind {premise.conspiracy_name}. Commands the operation.",
            "personality": random.choice(["calculating", "charismatic", "ruthless", "visionary"])
        }
        characters.append(primary_char)
        logger.info(f"      Primary conspirator: {primary_name}")
        
        # 2. SECONDARY CONSPIRATORS (3-4)
        num_secondary = random.randint(3, 4)
        secondary_conspirators = await self._generate_secondary_conspirators(
            premise, 
            political_context, 
            num_secondary
        )
        characters.extend(secondary_conspirators)
        logger.info(f"      Secondary conspirators: {len(secondary_conspirators)}")
        
        # 3. INNOCENT CHARACTERS (5-8)
        num_innocents = random.randint(5, 8)
        innocent_characters = await self._generate_innocent_characters(
            political_context,
            num_innocents
        )
        characters.extend(innocent_characters)
        logger.info(f"      Innocent characters: {len(innocent_characters)}")
        
        # NORMALIZE all character names (replace en-dashes with regular hyphens)
        for char in characters:
            if "name" in char:
                char["name"] = self._normalize_to_ascii(char["name"])
        
        logger.info(f"   Generated {len(characters)} total characters (1 primary, {len(secondary_conspirators)} secondary, {len(innocent_characters)} innocent)")
        return characters
    
    async def _generate_secondary_conspirators(
        self, 
        premise, 
        political_context, 
        num_characters
    ):
        """Generate secondary conspirator characters using LLM."""
        
        prompt = f"""Generate {num_characters} secondary conspirator characters for a conspiracy mystery.

CONSPIRACY CONTEXT:
- Operation: {premise.conspiracy_name}
- Goal: {premise.what[:200]}...
- World: {political_context.world_name}

REQUIREMENTS:
- These are SECONDARY conspirators (members, not leaders)
- Each should have a distinct role and personality
- Names should be diverse and realistic
- Roles: Operative, Specialist, Handler, Coordinator, Agent, Technician, etc.

Generate {num_characters} characters.

OUTPUT FORMAT (JSON array):
[
  {{
    "name": "Full name (e.g., 'Marcus Chen', 'Elena Volkov')",
    "role": "Specific role in conspiracy",
    "background": "Brief background (1-2 sentences)",
    "personality": "One-word personality trait"
  }}
]"""
        
        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=0.8,
                max_tokens=1000
            )
            
            if isinstance(response, list):
                characters_data = response
            else:
                characters_data = response.get("characters", [])
            
            characters = []
            for data in characters_data[:num_characters]:
                char = {
                    "name": data.get("name", f"Agent {len(characters)}"),
                    "is_primary": False,
                    "involvement_level": "conspirator",
                    "clearance_level": "secret",
                    "role": data.get("role", "Operative"),
                    "background": data.get("background", "Member of the conspiracy."),
                    "personality": data.get("personality", "loyal")
                }
                characters.append(char)
            
            return characters
            
        except Exception as e:
            logger.error(f"   ❌ Secondary conspirator generation failed: {e}, using fallback")
            return self._generate_fallback_conspirators(num_characters)
    
    async def _generate_innocent_characters(
        self,
        political_context,
        num_characters
    ):
        """Generate innocent/witness characters using LLM."""
        
        prompt = f"""Generate {num_characters} innocent characters for a conspiracy mystery.

WORLD CONTEXT:
- World: {political_context.world_name}
- Setting: {political_context.public_narrative[:200]}...

REQUIREMENTS:
- These are INNOCENT people (not conspirators)
- Roles: Witness, Colleague, Technician, Administrator, Security Guard, Analyst, Journalist, etc.
- Some may have seen suspicious activity but are not involved
- Names should be diverse and realistic
- They create red herrings and add complexity

Generate {num_characters} innocent characters.

OUTPUT FORMAT (JSON array):
[
  {{
    "name": "Full name",
    "role": "Job/position (not conspirator)",
    "background": "Brief background (1-2 sentences)",
    "personality": "One-word personality trait"
  }}
]"""
        
        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=0.8,
                max_tokens=1000
            )
            
            if isinstance(response, list):
                characters_data = response
            else:
                characters_data = response.get("characters", [])
            
            characters = []
            for data in characters_data[:num_characters]:
                char = {
                    "name": data.get("name", f"Person {len(characters)}"),
                    "is_primary": False,
                    "involvement_level": "innocent",
                    "clearance_level": "unclassified",
                    "role": data.get("role", "Witness"),
                    "background": data.get("background", "Innocent bystander."),
                    "personality": data.get("personality", "observant")
                }
                characters.append(char)
            
            return characters
            
        except Exception as e:
            logger.error(f"   ❌ Innocent character generation failed: {e}, using fallback")
            return self._generate_fallback_innocents(num_characters)
    
    def _generate_fallback_conspirators(self, num_characters):
        """Fallback secondary conspirators if LLM fails."""
        import random
        
        names = ["Marcus Chen", "Elena Volkov", "James Torres", "Sophia Rahman"]
        roles = ["Operative", "Specialist", "Handler", "Coordinator"]
        
        characters = []
        for i in range(num_characters):
            char = {
                "name": names[i % len(names)],
                "is_primary": False,
                "involvement_level": "conspirator",
                "clearance_level": "secret",
                "role": roles[i % len(roles)],
                "background": "Member of the conspiracy.",
                "personality": random.choice(["loyal", "cautious", "ambitious"])
            }
            characters.append(char)
        
        return characters
    
    def _generate_fallback_innocents(self, num_characters):
        """Fallback innocent characters if LLM fails."""
        import random
        
        names = ["Sarah Mitchell", "David Park", "Rachel Cohen", "Ahmed Hassan", "Lisa Wong", "Tom Anderson"]
        roles = ["Analyst", "Technician", "Administrator", "Security", "Journalist", "Witness"]
        
        characters = []
        for i in range(num_characters):
            char = {
                "name": names[i % len(names)],
                "is_primary": False,
                "involvement_level": "innocent",
                "clearance_level": "unclassified",
                "role": roles[i % len(roles)],
                "background": "Innocent bystander.",
                "personality": random.choice(["observant", "nervous", "professional"])
            }
            characters.append(char)
        
        return characters
    
    def _select_target_for_identity_chain(self, characters, chain_index, answer_template):
        """
        Distribute identity chains across characters strategically.
        
        Strategy:
        - Chains 0-1: Primary conspirator (THE answer)
        - Chains 2-3: Secondary conspirators  
        - Chains 4+: Innocent characters (red herrings)
        
        This ensures the WHO answer name appears in only 2 chains (fewer documents),
        while other characters create complexity and require inference.
        
        Args:
            characters: List of character dicts
            chain_index: Current chain index
            answer_template: Answer template with WHO answer
        
        Returns:
            Character dict for this chain
        """
        import random
        
        # Separate characters by involvement level
        primary = [c for c in characters if c.get("is_primary")]
        secondary = [c for c in characters if c.get("involvement_level") == "conspirator"]
        innocent = [c for c in characters if c.get("involvement_level") == "innocent"]
        
        if chain_index < 2:
            # First 2 chains → Primary conspirator (the answer)
            return primary[0] if primary else characters[0]
        elif chain_index < 4:
            # Chains 2-3 → Secondary conspirators
            return random.choice(secondary) if secondary else characters[chain_index % len(characters)]
        else:
            # Chains 4+ → Innocent characters (red herrings)
            return random.choice(innocent) if innocent else characters[chain_index % len(characters)]
    
    def _collect_crypto_keys(self, subgraphs):
        """Collect all crypto keys from sub-graphs."""
        crypto_keys = []
        for sg in subgraphs:
            if hasattr(sg, 'crypto_keys') and sg.crypto_keys:
                crypto_keys.extend(sg.crypto_keys)
        return crypto_keys
    
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
        answer_template,
        questions,
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
            answer_template=answer_template,
            questions=questions,
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
    
    def _populate_inference_node_document_ids(
        self,
        subgraphs: List[SubGraph],
        document_plans: List,
        documents: List[Dict[str, Any]]
    ):
        """
        Populate required_document_ids for all inference nodes.
        
        This maps inference nodes to the documents that contain their required evidence.
        Used by the validator to test multi-hop reasoning chains.
        
        Args:
            subgraphs: List of subgraphs containing inference nodes
            document_plans: List of document narrative plans (with facts assigned)
            documents: List of rendered documents (with document_ids)
        """
        # Build map: evidence_node_id -> document_id
        # For each document plan, map its facts' source nodes to the document_id
        evidence_node_to_doc_id = {}
        for plan in document_plans:
            for fact in plan.required_facts:
                # Use fact's source_node_id to link evidence nodes to documents
                evidence_node_to_doc_id[fact.source_node_id] = plan.document_id
        
        logger.info(f"   Mapped {len(evidence_node_to_doc_id)} evidence nodes to documents")
        
        # For each inference node, find required documents based on parent evidence nodes
        updated_count = 0
        for sg in subgraphs:
            for inference_node in sg.inference_nodes:
                required_doc_ids = set()
                
                # Get documents containing parent evidence nodes
                for parent_id in inference_node.parent_node_ids:
                    if parent_id in evidence_node_to_doc_id:
                        required_doc_ids.add(evidence_node_to_doc_id[parent_id])
                
                # If no parents found, try to find any document from this subgraph's evidence
                if not required_doc_ids:
                    for evidence_node in sg.evidence_nodes:
                        if evidence_node.node_id in evidence_node_to_doc_id:
                            required_doc_ids.add(evidence_node_to_doc_id[evidence_node.node_id])
                            # Just add first 1-2 documents from this subgraph
                            if len(required_doc_ids) >= 2:
                                break
                
                # Update the inference node
                if required_doc_ids:
                    inference_node.required_document_ids = list(required_doc_ids)
                    updated_count += 1
        
        logger.info(f"   ✅ Updated {updated_count} inference nodes with document IDs")
    
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
        
        # Save individual documents (using neutral names for files)
        for doc in mystery.documents:
            doc_id = doc.get("document_id", "unknown")
            doc_name = doc.get("document_name", doc_id)  # Use neutral name if available
            doc_file = docs_dir / doc_name  # Use neutral name for filename
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
            
            # Answer Template (for smart contract submission)
            if mystery.answer_template:
                f.write(f"## Answer Template (Smart Contract Submission)\n\n")
                f.write(f"**WHO:** {mystery.answer_template.who}\n\n")
                f.write(f"**WHAT:** {mystery.answer_template.what}\n\n")
                f.write(f"**WHY:** {mystery.answer_template.why}\n\n")
                f.write(f"**HOW:** {mystery.answer_template.how}\n\n")
                f.write(f"**Combined Hash:** `{mystery.answer_template.combined_hash}`\n\n")
            
            f.write(f"## The Conspiracy (Full Details)\n\n")
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
        logger.info(f"      🔐 Documents use neutral names (e.g., System_Report_2024_11_23_7F3A.txt)")
    
    def _normalize_to_ascii(self, text: str) -> str:
        """
        Normalize text to ASCII - replace en-dashes, em-dashes with regular hyphens.
        """
        import unicodedata
        
        # Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        
        # Replace ALL types of dashes/hyphens with regular hyphen
        text = text.replace('\u2010', '-')  # hyphen
        text = text.replace('\u2011', '-')  # non-breaking hyphen
        text = text.replace('\u2012', '-')  # figure dash
        text = text.replace('\u2013', '-')  # en dash
        text = text.replace('\u2014', '-')  # em dash
        text = text.replace('\u2015', '-')  # horizontal bar
        text = text.replace('\u2212', '-')  # minus sign
        text = text.replace('\u00ad', '')    # soft hyphen
        text = text.replace('\u200b', '')    # zero-width space
        text = text.replace('\u2043', '-')  # hyphen bullet
        text = text.replace('\ufe63', '-')  # small hyphen-minus
        text = text.replace('\uff0d', '-')  # fullwidth hyphen-minus
        
        return text

