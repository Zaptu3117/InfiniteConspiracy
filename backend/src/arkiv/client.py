"""Arkiv SDK client wrapper for v1.0.0a5."""

import logging
from typing import List, Dict, Any, Optional
from arkiv_sdk import Arkiv, NamedAccount, HTTPProvider, Attributes, CreateOp, Operations, QueryOptions


logger = logging.getLogger(__name__)


class ArkivClient:
    """
    Wrapper for Arkiv SDK v1.0.0a5 operations.
    
    Uses context manager pattern with proper account and provider setup.
    """
    
    def __init__(self, private_key: str, rpc_url: str, account_name: str = "mystery_oracle"):
        """
        Initialize Arkiv client.
        
        Args:
            private_key: Hex private key (with or without 0x prefix)
            rpc_url: RPC endpoint URL (e.g., https://mendoza.hoodi.arkiv.network/rpc)
            account_name: Name for the account (for logging/identification)
        """
        self.rpc_url = rpc_url
        self.account_name = account_name
        
        # Prepare private key (ensure 0x prefix)
        if not private_key.startswith('0x'):
            private_key = f'0x{private_key}'
        
        # Create named account
        self.account = NamedAccount.from_private_key(account_name, private_key)
        
        # Create HTTP provider
        self.provider = HTTPProvider(rpc_url)
        
        # Client will be created in context manager
        self.client = None
    
    def __enter__(self):
        """Enter context manager - create Arkiv client."""
        self.client = Arkiv(provider=self.provider, account=self.account)
        self.client.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - cleanup."""
        if self.client:
            self.client.__exit__(exc_type, exc_val, exc_tb)
        return False
    
    def create_entity(
        self,
        payload: bytes,
        content_type: str,
        attributes: Dict[str, Any],
        btl: int = 7200  # blocks to live (~7 days assuming 12s blocks)
    ) -> tuple:
        """
        Create a single entity in Arkiv.
        
        Args:
            payload: Entity data as bytes
            content_type: MIME type (e.g., 'application/json', 'text/plain', 'image/png')
            attributes: Dictionary of attributes for querying
            btl: Blocks to live (TTL in blocks)
        
        Returns:
            Tuple of (entity_key, receipt)
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'with ArkivClient() as client:'")
        
        entity_key, receipt = self.client.arkiv.create_entity(
            payload=payload,
            content_type=content_type,
            attributes=Attributes(attributes),
            btl=btl
        )
        
        return entity_key, receipt
    
    def create_entities_batch(self, entities: List[Dict[str, Any]]) -> Any:
        """
        Create multiple entities in a single transaction.
        
        Args:
            entities: List of entity specifications with keys:
                - payload: bytes
                - content_type: str
                - attributes: Dict[str, Any]
                - btl: int (optional, defaults to 7200)
        
        Returns:
            Receipt with list of created entity keys
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'with ArkivClient() as client:'")
        
        creates = []
        for entity in entities:
            creates.append(CreateOp(
                payload=entity["payload"],
                content_type=entity["content_type"],
                attributes=Attributes(entity["attributes"]),
                btl=entity.get("btl", 7200)
            ))
        
        receipt = self.client.arkiv.execute(Operations(creates=creates))
        return receipt
    
    def query_entities(self, query_string: str, limit: int = 100) -> List[Any]:
        """
        Query entities using Arkiv query language.
        
        Args:
            query_string: Query in format 'key = "value" and key2 = "value2"'
            limit: Maximum number of results (default 100)
        
        Returns:
            List of matching entities
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'with ArkivClient() as client:'")
        
        options = QueryOptions(limit=limit)
        entities = self.client.arkiv.query_entities(query_string, options=options)
        return entities
    
    def get_entity(self, entity_key: str) -> Optional[Any]:
        """
        Get a specific entity by its key.
        
        Args:
            entity_key: The unique entity key
        
        Returns:
            Entity object or None if not found
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'with ArkivClient() as client:'")
        
        try:
            entity = self.client.arkiv.get_entity(entity_key)
            return entity
        except Exception as e:
            logger.error(f"Failed to get entity {entity_key}: {e}")
            return None
    
    def extend_entity(self, entity_key: str, number_of_blocks: int) -> Any:
        """
        Extend the TTL of an entity.
        
        Args:
            entity_key: The entity to extend
            number_of_blocks: Number of blocks to extend by
        
        Returns:
            Receipt with extension details
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'with ArkivClient() as client:'")
        
        receipt = self.client.arkiv.extend_entity(entity_key, number_of_blocks=number_of_blocks)
        return receipt

