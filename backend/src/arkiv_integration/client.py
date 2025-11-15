"""Arkiv SDK client wrapper for v1.0.0a8 (corrected API based on package exploration)."""

import logging
from typing import List, Dict, Any, Optional
from arkiv import AsyncArkiv, NamedAccount
from arkiv.types import Attributes, Entity, QueryOptions, QueryResult


logger = logging.getLogger(__name__)


class ArkivClient:
    """
    Wrapper for Arkiv SDK v1.0.0a8 operations using AsyncArkiv.
    
    Uses the actual installed API from arkiv package (v1.0.0a8).
    Based on complete package exploration.
    """
    
    def __init__(
        self, 
        private_key: str, 
        rpc_url: str = "https://kaolin.hoodi.arkiv.network/rpc",
        ws_url: str = "wss://kaolin.hoodi.arkiv.network/rpc/ws"
    ):
        """
        Initialize Arkiv client (async initialization happens in __aenter__).
        
        Args:
            private_key: Hex private key (with or without 0x prefix)
            rpc_url: RPC endpoint URL (not used for async, kept for compatibility)
            ws_url: WebSocket URL (required for AsyncArkiv)
        """
        self.rpc_url = rpc_url
        self.ws_url = ws_url
        
        # Prepare private key and create account
        hex_key = private_key[2:] if private_key.startswith('0x') else private_key
        if not hex_key.startswith('0x'):
            hex_key = f'0x{hex_key}'
        
        self.account = NamedAccount.from_private_key("mystery_oracle", hex_key)
        
        # Client will be created in async context manager
        self.client: Optional[AsyncArkiv] = None
    
    async def __aenter__(self):
        """Enter async context manager - create AsyncArkiv client."""
        from arkiv.provider import ProviderBuilder
        
        # Build async HTTP provider (simpler than WebSocket, no connection management needed)
        # Use .http().async_mode() to get AsyncHTTPProvider
        provider = ProviderBuilder().custom(self.rpc_url).http().async_mode().build()
        
        # Create async client - AsyncArkiv has its own context manager
        self.client = AsyncArkiv(provider=provider, account=self.account)
        
        # Enter the AsyncArkiv context manager
        await self.client.__aenter__()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager - cleanup."""
        if self.client:
            # Exit the AsyncArkiv context manager
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
        return False
    
    async def create_entity(
        self,
        payload: bytes,
        content_type: str,
        attributes: Dict[str, Any],
        expires_in: int = 43200,  # seconds (converted to blocks)
        btl: int = None  # blocks to live (alternative to expires_in)
    ) -> str:
        """
        Create a single entity in Arkiv.
        
        Args:
            payload: Entity data as bytes
            content_type: MIME type (e.g., 'application/json', 'text/plain', 'image/png')
            attributes: Dictionary of string attributes for querying
            expires_in: Time to live in seconds (default: 43200 = 12 hours), converted to blocks
            btl: Blocks to live (alternative to expires_in, takes priority if set)
        
        Returns:
            Entity key (hex string)
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'async with ArkivClient() as client:'")
        
        # Convert string values to Attributes
        attrs = Attributes({k: str(v) for k, v in attributes.items()})
        
        # Convert seconds to blocks (assuming ~12 second block time)
        if btl is None:
            btl = expires_in // 12
        
        # Create entity using the arkiv module
        # Returns tuple: (entity_key, receipt)
        entity_key, receipt = await self.client.arkiv.create_entity(
            payload=payload,
            content_type=content_type,
            attributes=attrs,
            btl=btl
        )
        
        return entity_key
    
    async def create_entities_batch(
        self, 
        entities: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Create multiple entities in a single transaction.
        
        Args:
            entities: List of entity specifications with keys:
                - payload: bytes
                - content_type: str
                - attributes: Dict[str, Any]
                - expires_in: int (optional, defaults to 43200 seconds)
                - btl: int (optional, blocks to live - overrides expires_in)
        
        Returns:
            List of entity keys
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'async with ArkivClient() as client:'")
        
        # For batch creation, we need to use Operations
        from arkiv.types import CreateOp, Operations
        
        creates = []
        for entity in entities:
            attrs = Attributes({k: str(v) for k, v in entity["attributes"].items()})
            
            # Convert expires_in to btl if not provided
            btl = entity.get("btl")
            if btl is None:
                expires_in = entity.get("expires_in", 43200)
                btl = expires_in // 12
            
            creates.append(CreateOp(
                payload=entity["payload"],
                content_type=entity["content_type"],
                attributes=attrs,
                btl=btl
            ))
        
        receipt = await self.client.arkiv.execute(Operations(creates=creates))
        
        # Extract entity keys from receipt create events
        entity_keys = [event.entity_key for event in receipt.creates]
        return entity_keys
    
    async def query_entities(self, query_string: str, limit: int = 100) -> List[Entity]:
        """
        Query entities using Arkiv query language.
        
        Args:
            query_string: Query in format 'key = "value" and key2 = "value2"'
            limit: Maximum number of results (default 100)
        
        Returns:
            List of matching Entity objects
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'async with ArkivClient() as client:'")
        
        # query_entities returns QueryResult, not a list directly!
        options = QueryOptions(max_results_per_page=limit)
        query_result: QueryResult = await self.client.arkiv.query_entities(
            query_string, 
            options=options
        )
        
        # Return the entities list from the QueryResult
        return query_result.entities
    
    async def get_entity(self, entity_key: str) -> Optional[Entity]:
        """
        Get a specific entity by its key.
        
        Args:
            entity_key: The unique entity key (hex string)
        
        Returns:
            Entity object or None if not found
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'async with ArkivClient() as client:'")
        
        try:
            # get_entity may raise ValueError if not found
            entity = await self.client.arkiv.get_entity(entity_key)
            return entity
        except (ValueError, Exception) as e:
            logger.error(f"Failed to get entity {entity_key}: {e}")
            return None
