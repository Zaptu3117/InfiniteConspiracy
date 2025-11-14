# Arkiv Integration Guide

## Overview

Arkiv serves as the **primary data layer** for Infinite Conspiracy, storing all mystery documents, images, and metadata in a decentralized, queryable, and time-scoped manner.

## Why Arkiv?

### Traditional Approach (What We Avoided)

```
Backend API (Express/FastAPI)
    ↓
Database (PostgreSQL/MongoDB)
    ↓
Frontend queries backend
```

**Problems:**
- Centralized single point of failure
- Backend must always be online
- Scaling costs for storage
- Data persistence concerns

### Arkiv Approach (What We Built)

```
Backend (Push-Only)
    ↓
Arkiv (Decentralized Storage)
    ↓
Frontend queries Arkiv directly
```

**Benefits:**
- ✅ Decentralized storage
- ✅ No backend API needed
- ✅ Automatic TTL cleanup
- ✅ Queryable with annotations
- ✅ Cost-efficient
- ✅ Immutable entities

## Arkiv SDK Usage

### Installation

```bash
pip install arkiv-sdk>=0.1.19
```

### Client Setup

```python
from arkiv_sdk import create_client, Tagged, Annotation, ArkivCreate

# Load private key
raw_key = os.getenv('ARKIV_PRIVATE_KEY', '')
hex_key = raw_key[2:] if raw_key.startswith('0x') else raw_key
key = Tagged("privatekey", bytes.fromhex(hex_key))

# Create client
client = await create_client(
    60138453056,  # Chain ID
    key,
    "https://mendoza.hoodi.arkiv.network/rpc",
    "wss://mendoza.hoodi.arkiv.network/rpc/ws"
)
```

### Creating Entities

#### Document Entity

```python
import json

document_data = {
    "document_id": "doc_5_email",
    "document_type": "email",
    "fields": {
        "from": "john.doe@company.com",
        "to": ["sarah@company.com"],
        "subject": "Meeting Notes",
        "body": "Encrypted text...",
        "timestamp": "2024-11-13T02:30:00Z"
    }
}

creates = [
    ArkivCreate(
        data=json.dumps(document_data).encode('utf-8'),
        expires_in=604800,  # 7 days in seconds
        string_annotations=[
            Annotation("mystery_id", "warehouse_leak_001"),
            Annotation("document_type", "email"),
            Annotation("document_id", "doc_5_email")
        ],
        numeric_annotations=[
            Annotation("created_at", 1730000000)
        ]
    )
]

receipts = await client.create_entities(creates)
print(f"Created entity: {receipts[0].entity_key}")
```

#### Image Entity

```python
with open('surveillance_photo.png', 'rb') as f:
    image_bytes = f.read()

creates = [
    ArkivCreate(
        data=image_bytes,
        expires_in=604800,
        string_annotations=[
            Annotation("mystery_id", "warehouse_leak_001"),
            Annotation("document_type", "image"),
            Annotation("document_id", "img_12_surveillance")
        ],
        numeric_annotations=[]
    )
]

receipts = await client.create_entities(creates)
```

### Querying Entities

#### Read-Only Client

```python
from arkiv_sdk import create_ro_client

ro_client = await create_ro_client(
    60138453056,
    "https://mendoza.hoodi.arkiv.network/rpc",
    "wss://mendoza.hoodi.arkiv.network/rpc/ws"
)
```

#### Query by Mystery ID

```python
# Get all documents for a mystery
query = 'mystery_id = "warehouse_leak_001" && document_type != "image"'
entities = await ro_client.query_entities(query)

for entity in entities:
    doc_data = json.loads(entity.data.decode('utf-8'))
    print(f"Document: {doc_data['document_id']}")
```

#### Query by Document Type

```python
# Get all emails
query = 'mystery_id = "warehouse_leak_001" && document_type = "email"'
emails = await ro_client.query_entities(query)
```

#### Query Images

```python
# Get all images
query = 'mystery_id = "warehouse_leak_001" && document_type = "image"'
images = await ro_client.query_entities(query)

for img in images:
    # img.data contains raw image bytes
    with open(f"{img.annotations['document_id']}.png", 'wb') as f:
        f.write(img.data)
```

## Annotation Strategy

### What We Include (Non-Spoilers)

```python
string_annotations=[
    Annotation("mystery_id", "..."),      # For filtering
    Annotation("document_type", "..."),   # For categorization
    Annotation("document_id", "...")      # Unique identifier
]

numeric_annotations=[
    Annotation("created_at", timestamp),  # For sorting
    Annotation("difficulty", 7)           # For metadata only
]
```

### What We DON'T Include (Spoilers)

```python
# ❌ These would make the mystery too easy
Annotation("contains_clue", "badge_number")
Annotation("hop_level", 3)
Annotation("cipher_key", "13")
Annotation("from_person", "John Doe")
Annotation("to_person", "Sarah Martinez")
Annotation("contains_visual_clue", "red_jacket")
```

**Why?** Players could filter for clues directly, bypassing investigation.

## TTL (Time-To-Live) Strategy

### Mystery Lifecycle

```
Day 0: Mystery created (TTL = 7 days)
Day 1-6: Players investigate
Day 7: Mystery expires
        ├─ Solved: Proof revealed
        └─ Unsolved: Proof revealed
Day 7+: Arkiv auto-deletes entities
```

### Setting TTL

```python
expires_in=604800  # 7 days in seconds

# Alternative durations:
# 3 days: 259200
# 14 days: 1209600
# 30 days: 2592000
```

### Benefits

- **Cost Efficiency**: Old data auto-deleted
- **Storage Management**: No manual cleanup
- **Game Design**: Fixed time pressure
- **Resource Optimization**: Pay only for active mysteries

## Query Patterns for Frontend

### Get Mystery Metadata

```typescript
const metadata = await arkivClient.queryEntities(
    'mystery_id = "warehouse_leak_001" && document_type = "mystery_metadata"'
)

const info = JSON.parse(metadata[0].data)
console.log(`Question: ${info.question}`)
console.log(`Difficulty: ${info.difficulty}`)
```

### Get All Documents (No Images)

```typescript
const docs = await arkivClient.queryEntities(
    'mystery_id = "warehouse_leak_001" && document_type != "mystery_metadata" && document_type != "image"'
)

const documents = docs.map(entity => {
    return JSON.parse(new TextDecoder().decode(entity.data))
})
```

### Get Specific Document Type

```typescript
// Get all emails
const emails = await arkivClient.queryEntities(
    'mystery_id = "warehouse_leak_001" && document_type = "email"'
)

// Get all police reports
const reports = await arkivClient.queryEntities(
    'mystery_id = "warehouse_leak_001" && document_type = "police_report"'
)
```

### Get Images

```typescript
const images = await arkivClient.queryEntities(
    'mystery_id = "warehouse_leak_001" && document_type = "image"'
)

images.forEach(img => {
    const blob = new Blob([img.data], { type: 'image/png' })
    const url = URL.createObjectURL(blob)
    // Display image
})
```

## Entity Structure Examples

### Mystery Metadata Entity

```json
{
  "data": {
    "mystery_id": "warehouse_leak_001",
    "question": "Who leaked the classified documents?",
    "difficulty": 7,
    "total_documents": 23,
    "total_images": 8,
    "created_at": 1730000000
  },
  "expires_in": 604800,
  "annotations": {
    "string": [
      {"key": "mystery_id", "value": "warehouse_leak_001"},
      {"key": "document_type", "value": "mystery_metadata"}
    ],
    "numeric": [
      {"key": "difficulty", "value": 7}
    ]
  }
}
```

### Email Document Entity

```json
{
  "data": {
    "document_id": "doc_5_email",
    "document_type": "email",
    "fields": {
      "from": "john.doe@company.com",
      "to": ["sarah@company.com"],
      "subject": "Re: Meeting Notes - ENCRYPTED",
      "body": "Zr unir gb zrrg ng 02:47nz ng jnerfubhfr 4O...",
      "timestamp": "2024-11-13T02:30:00Z",
      "attachments": ["doc_6_encrypted_memo"]
    },
    "cipher_info": {
      "encrypted": true,
      "cipher_type": "caesar",
      "encrypted_sections": ["body"],
      "hint": "Check badge access logs for the key"
    }
  },
  "expires_in": 604800,
  "annotations": {
    "string": [
      {"key": "mystery_id", "value": "warehouse_leak_001"},
      {"key": "document_type", "value": "email"},
      {"key": "document_id", "value": "doc_5_email"}
    ]
  }
}
```

### Badge Log Document Entity

```json
{
  "data": {
    "document_id": "doc_9_badge_log",
    "document_type": "badge_log",
    "fields": {
      "facility_name": "Warehouse District",
      "log_period": "2024-11-12 to 2024-11-13",
      "entries": [
        {
          "badge_number": "4217",
          "name": "John Doe",
          "entry_time": "2024-11-13T02:43:00Z",
          "location": "Warehouse 4B"
        },
        {
          "badge_number": "5829",
          "name": "Sarah Martinez",
          "entry_time": "2024-11-13T03:15:00Z",
          "location": "Warehouse 3A"
        }
      ]
    }
  },
  "expires_in": 604800,
  "annotations": {
    "string": [
      {"key": "mystery_id", "value": "warehouse_leak_001"},
      {"key": "document_type", "value": "badge_log"},
      {"key": "document_id", "value": "doc_9_badge_log"}
    ]
  }
}
```

## Cost Optimization

### Storage Costs

Arkiv pricing is based on:
- Data size
- Duration (TTL)

**Our optimization strategies:**

1. **JSON over HTML**: Smaller payload
   - HTML email: ~15 KB
   - JSON email: ~5 KB
   - **Savings: 66%**

2. **7-Day TTL**: Automatic cleanup
   - No accumulation of old data
   - Pay only for active mysteries

3. **Efficient Annotations**: Minimal metadata
   - Only 3-4 annotations per entity
   - No redundant information

4. **Image Compression**: Optimized images
   - PNG compression
   - Target: ~500 KB per image
   - vs uncompressed: ~2 MB

### Cost Estimate Per Mystery

```
20 documents × 5 KB = 100 KB
8 images × 500 KB = 4 MB
Total: ~4.1 MB × 7 days = ~$0.01
```

**Extremely cost-efficient!**

## Best Practices

### 1. Batch Entity Creation

```python
# ✅ Good: Batch create
creates = [entity1, entity2, entity3, ...]
receipts = await client.create_entities(creates)

# ❌ Bad: Individual creates
for entity in entities:
    await client.create_entities([entity])
```

### 2. Query Optimization

```python
# ✅ Good: Specific query
query = 'mystery_id = "..." && document_type = "email"'

# ❌ Bad: Overly broad query
query = 'mystery_id = "..."'  # Returns everything
```

### 3. Error Handling

```python
try:
    receipts = await client.create_entities(creates)
except Exception as e:
    logger.error(f"Arkiv push failed: {e}")
    # Retry logic or fallback
```

### 4. Verification

```python
# Always verify after push
entities = await ro_client.query_entities(f'mystery_id = "{mystery_id}"')
assert len(entities) == expected_count
```

## Troubleshooting

### Entity Not Found

**Problem:** Query returns empty result

**Solutions:**
1. Check annotation spelling
2. Verify entity was created (check receipts)
3. Wait a few seconds for indexing
4. Use read-only client for queries

### TTL Expired Prematurely

**Problem:** Entity disappeared before expected time

**Solutions:**
1. Check `expires_in` value (should be in seconds)
2. Verify server time vs client time
3. Check Arkiv network status

### Query Too Slow

**Problem:** Query takes multiple seconds

**Solutions:**
1. Add more specific filters
2. Use indexed annotations
3. Batch queries when possible
4. Cache results on frontend

---

**Next**: See [SMART_CONTRACT.md](./SMART_CONTRACT.md) for blockchain integration.

