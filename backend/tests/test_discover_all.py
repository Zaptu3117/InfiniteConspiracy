"""Test discovering all conspiracies on Arkiv."""
import asyncio
import os
import json
from dotenv import load_dotenv
load_dotenv()

import sys
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from arkiv_integration import ArkivClient

async def discover_all_conspiracies():
    arkiv_key = os.getenv("ARKIV_PRIVATE_KEY")
    
    print("🔍 DISCOVERING ALL CONSPIRACIES ON ARKIV\n")
    
    async with ArkivClient(
        private_key=arkiv_key,
        rpc_url="https://mendoza.hoodi.arkiv.network/rpc",
        ws_url="wss://mendoza.hoodi.arkiv.network/rpc/ws"
    ) as client:
        
        # Query: resource_type = "conspiracy" (semantic!)
        query_string = 'resource_type = "conspiracy"'
        print(f"Query: {query_string} (semantic attribute!)\n")
        
        entities = await client.query_entities(query_string, limit=100)
        
        print(f"✅ Found {len(entities)} conspiracies:\n")
        
        for i, entity in enumerate(entities, 1):
            data = json.loads(entity.payload.decode('utf-8'))
            
            print(f"{i}. {data['conspiracy_name']}")
            print(f"   World: {data['world']}")
            print(f"   Difficulty: {data['difficulty']}/10")
            print(f"   Documents: {data['total_documents']}")
            print(f"   Created: {data['created_at']}")
            print(f"   Mystery ID: {data['mystery_id'][:16]}...")
            print()
        
        print(f"🎉 Discovery complete! Total: {len(entities)} conspiracies")

if __name__ == "__main__":
    asyncio.run(discover_all_conspiracies())
