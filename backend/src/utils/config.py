"""Configuration management for the backend."""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration management."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.outputs_dir = self.project_root / "outputs"
        
        # Load configurations
        self.document_types = self._load_json("document_types.json")
        self.cipher_configs = self._load_json("cipher_configs.json")
        self.narrator_config = self._load_yaml("narrator_config.yaml")
        
        # Environment variables
        self.cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
        
        # Arkiv configuration (Mendoza testnet)
        self.arkiv_rpc_url = os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc")
        self.arkiv_private_key = os.getenv("ARKIV_PRIVATE_KEY")
        
        # Blockchain configuration (Kusama Asset Hub - separate from Arkiv)
        self.kusama_rpc_url = os.getenv("KUSAMA_RPC_URL", "https://testnet-passet-hub-eth-rpc.polkadot.io")
        self.kusama_chain_id = int(os.getenv("KUSAMA_CHAIN_ID", "420420422"))  # Paseo testnet
        self.oracle_private_key = os.getenv("ORACLE_PRIVATE_KEY")
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_dir = self.outputs_dir / "logs"
        
        # Ensure directories exist
        self.outputs_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        (self.outputs_dir / "mysteries").mkdir(exist_ok=True)
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON configuration file."""
        file_path = self.config_dir / filename
        if not file_path.exists():
            return {}
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        file_path = self.config_dir / filename
        if not file_path.exists():
            return {}
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    def validate(self) -> bool:
        """Validate that required configurations are present."""
        required_env_vars = [
            ("CEREBRAS_API_KEY", self.cerebras_api_key),
            ("OPENAI_API_KEY", self.openai_api_key),
            ("REPLICATE_API_TOKEN", self.replicate_api_token),
            ("ARKIV_PRIVATE_KEY", self.arkiv_private_key),
        ]
        
        missing = [name for name, value in required_env_vars if not value]
        
        if missing:
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            return False
        
        return True


# Global configuration instance
config = Config()


def load_config() -> Config:
    """Load and return the global configuration."""
    return config

