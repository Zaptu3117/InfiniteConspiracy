# End-to-End Testing Guide
## Generate → Deploy → Fetch on Arkiv

---

## Overview

Complete end-to-end test that validates the entire conspiracy pipeline:
1. ✅ **Generate** conspiracy mystery with LLM
2. ✅ **Deploy** to Arkiv with semantic attributes
3. ✅ **Fetch** data back to verify deployment
4. ✅ **Tag** with environment (dev/prod) for filtering

---

## Quick Start

### Run E2E Test (Dev Environment)

```bash
uv run python test_e2e_conspiracy_arkiv.py
```

### Run E2E Test (Production)

```bash
uv run python test_e2e_conspiracy_arkiv.py --env prod
```

### Custom Configuration

```bash
uv run python test_e2e_conspiracy_arkiv.py \
  --env prod \
  --difficulty 8 \
  --docs 30 \
  --type secret_society
```

---

## Environment Tagging

### Why Environment Tags?

The `environment` attribute allows you to:
- ✅ Filter dev data vs production data
- ✅ Show only production mysteries in presentations
- ✅ Test with dev data without polluting production
- ✅ Easily clean up dev data

### Usage

#### Upload with Dev Tag (Default)

```bash
# E2E test
uv run python test_e2e_conspiracy_arkiv.py --env dev

# Or simple upload
uv run python test_push_conspiracy.py --env dev
```

#### Upload with Prod Tag

```bash
# E2E test
uv run python test_e2e_conspiracy_arkiv.py --env prod

# Or simple upload
uv run python test_push_conspiracy.py --env prod
```

---

## Command Line Options

### test_e2e_conspiracy_arkiv.py

```bash
Options:
  --env {dev,prod}        Environment tag (default: dev)
  --difficulty {1-10}     Mystery difficulty (default: 6)
  --docs N                Number of documents (default: 20)
  --type {occult,secret_society,underground_network}
                         Conspiracy type (default: occult)
```

### Examples

```bash
# Dev mystery, easy difficulty
uv run python test_e2e_conspiracy_arkiv.py --env dev --difficulty 3

# Prod mystery, hard, with many docs
uv run python test_e2e_conspiracy_arkiv.py --env prod --difficulty 9 --docs 50

# Secret society conspiracy
uv run python test_e2e_conspiracy_arkiv.py --env prod --type secret_society
```

---

## E2E Test Flow

### Step 1: Generate Conspiracy

```
🎲 Generating conspiracy with LLM...
   - Political context
   - Conspiracy premise
   - Sub-graphs (identity, psychological, crypto)
   - Documents
   - Characters
   - Crypto keys

✅ Generation complete (45.2s)
```

### Step 2: Deploy to Arkiv

```
📤 Deploying to Arkiv...
   - 1 conspiracy metadata entity
   - 20 document entities
   - Attributes:
     • resource_type: conspiracy
     • environment: dev ← FILTERABLE!
     • world: Eclipsed Dominion
     • difficulty: 6
     • conspiracy_type: occult

✅ Deployment complete (3.1s)
```

### Step 3: Fetch & Verify

```
🔍 Fetching from Arkiv...
   - Query by mystery_id
   - Query all dev conspiracies
   - Verify attributes

✅ Verification complete
   Found 21 entities (1 metadata + 20 docs)
```

---

## Frontend Queries with Environment

### Get Only Production Conspiracies

```typescript
// For presentations, demos, public access
const prodConspiracies = await query
  .where(eq('resource_type', 'conspiracy'))
  .where(eq('environment', 'prod'))
  .withPayload(true)
  .fetch()
```

### Get Only Dev Conspiracies

```typescript
// For testing, development
const devConspiracies = await query
  .where(eq('resource_type', 'conspiracy'))
  .where(eq('environment', 'dev'))
  .withPayload(true)
  .fetch()
```

### Combined Filters

```typescript
// Production conspiracies, difficulty 7+, in specific world
const hardProdMysteries = await query
  .where(eq('environment', 'prod'))
  .where(eq('world', 'Eclipsed Dominion'))
  .where(eq('difficulty', '7'))
  .withPayload(true)
  .fetch()
```

---

## Attribute Schema (Updated)

### Conspiracy Metadata

```typescript
{
  // Identity
  "resource_type": "conspiracy",
  "mystery_id": string,
  
  // Filters
  "world": string,              // Game world
  "difficulty": string,         // 1-10
  "conspiracy_type": string,    // occult, secret_society, underground_network
  "environment": "dev" | "prod",  // ✅ NEW: Dev or Prod tag
  "status": "active"            // active, completed, archived
}
```

### Document

```typescript
{
  // Identity
  "resource_type": "document",
  "mystery_id": string,
  "document_id": string,
  
  // Filters
  "doc_type": string,           // email, network_log, diary, etc.
  "world": string,              // Same as parent mystery
  "environment": "dev" | "prod" // ✅ NEW: Same as parent mystery
}
```

---

## Testing Scenarios

### 1. Basic E2E Test

```bash
# Generate, deploy, verify
uv run python test_e2e_conspiracy_arkiv.py

# Expected output:
# ✅ Generation complete
# ✅ Deployment complete (21 entities)
# ✅ Verification complete
# 🎉 E2E test passed!
```

### 2. Production Deploy

```bash
# Deploy to production environment
uv run python test_e2e_conspiracy_arkiv.py --env prod --difficulty 7

# Frontend can now filter:
# environment = "prod"
```

### 3. Multiple Environments

```bash
# Create dev mystery
uv run python test_e2e_conspiracy_arkiv.py --env dev

# Create prod mystery
uv run python test_e2e_conspiracy_arkiv.py --env prod

# Frontend sees both, can filter by environment
```

---

## Verification Queries

The E2E test runs these verification queries:

### Query 1: Get Specific Mystery

```
mystery_id = "07a99a47-2a67-426a-b28d-5c26a39fe1d4"
```

Expected: 21 entities (1 conspiracy + 20 docs)

### Query 2: Get All Environment Conspiracies

```
environment = "dev"
```

Expected: All dev conspiracies in the system

### Query 3: Verify Attributes

```
Checks:
  ✅ resource_type = "conspiracy"
  ✅ environment = "dev" or "prod"
  ✅ world = "Eclipsed Dominion"
  ✅ difficulty = "6"
  ✅ conspiracy_type = "occult"
```

---

## Output Example

```
============================================================
🚀 END-TO-END CONSPIRACY PIPELINE TEST
============================================================

Environment: DEV
Difficulty: 6/10
Documents: 20
Type: occult

============================================================
STEP 1: GENERATING CONSPIRACY
============================================================

✅ GENERATION COMPLETE
   Time: 45.2s
   Mystery: Operation Abyssal Convergence
   World: Eclipsed Dominion
   Documents: 20
   Sub-graphs: 8
   Characters: 4
   Crypto keys: 2
   Mystery ID: 07a99a47-2a67-426a-b28d-5c26a39fe1d4

============================================================
STEP 2: DEPLOYING TO ARKIV
============================================================

   Metadata attributes:
      resource_type: conspiracy
      world: Eclipsed Dominion
      difficulty: 6
      conspiracy_type: occult
      environment: dev ← FILTERABLE!
      status: active

   Pushing 21 entities...
      Batch 1: 10 entities
      Batch 2: 10 entities
      Batch 3: 1 entities

✅ DEPLOYMENT COMPLETE
   Time: 3.1s
   Total entities: 21
   - 1 conspiracy metadata
   - 20 documents

============================================================
STEP 3: FETCHING FROM ARKIV (Verification)
============================================================

   Query 1: Fetching mystery 07a99a47-2a67...
   ✅ Found 21 entities
      - 1 conspiracy metadata
      - 20 documents

   Query 2: All dev conspiracies...
   ✅ Found 1 dev conspiracies total
      1. Operation Abyssal Convergence (diff: 6)

   Query 3: Verifying attributes...
   ✅ Attributes verified:
      resource_type: conspiracy
      environment: dev ✓
      world: Eclipsed Dominion
      difficulty: 6
      conspiracy_type: occult

============================================================
✅ E2E TEST COMPLETE
============================================================

Summary:
  Mystery: Operation Abyssal Convergence
  Mystery ID: 07a99a47-2a67-426a-b28d-5c26a39fe1d4
  Environment: dev
  World: Eclipsed Dominion
  Difficulty: 6/10
  Type: occult
  Documents: 20
  Generation time: 45.2s
  Upload time: 3.1s

Frontend Queries:
  // Get all dev conspiracies
  query.where(eq("environment", "dev"))

  // Get this specific mystery
  query.where(eq("mystery_id", "07a99a47-2a67-426a-b28d-5c26a39fe1d4"))

  // Get dev conspiracies in this world
  query.where(eq("environment", "dev"))
       .where(eq("world", "Eclipsed Dominion"))

🎉 E2E test passed!
```

---

## Best Practices

### 1. Use Dev for Testing

```bash
# Always use dev for development/testing
uv run python test_e2e_conspiracy_arkiv.py --env dev
```

### 2. Use Prod for Demos/Releases

```bash
# Only use prod for presentations, demos, releases
uv run python test_e2e_conspiracy_arkiv.py --env prod --difficulty 7
```

### 3. Clean Up Dev Data

```typescript
// Frontend: Delete old dev mysteries
const oldDevMysteries = await query
  .where(eq('environment', 'dev'))
  .where(lt('created_at', oneWeekAgo))
  .fetch()

// Delete these entities
for (const mystery of oldDevMysteries) {
  await client.deleteEntity(mystery.entityKey)
}
```

### 4. Filter in UI

```typescript
// Show environment selector in UI
<select onChange={(e) => setEnv(e.target.value)}>
  <option value="prod">Production</option>
  <option value="dev">Development</option>
</select>

// Query based on selection
const conspiracies = await query
  .where(eq('environment', selectedEnv))
  .fetch()
```

---

## Troubleshooting

### E2E Test Fails at Generation

```
❌ Generation failed: ...

Solution:
- Check CEREBRAS_API_KEY is set
- Check API rate limits
- Reduce num_documents
```

### E2E Test Fails at Deployment

```
❌ Arkiv deployment failed: ...

Solution:
- Check ARKIV_PRIVATE_KEY is set
- Check network connection
- Verify RPC URL is correct
```

### E2E Test Fails at Fetch

```
❌ Fetch verification failed: ...

Solution:
- Wait a few seconds (propagation delay)
- Check query syntax
- Verify mystery_id is correct
```

---

## Files

- `test_e2e_conspiracy_arkiv.py` - Full E2E test script
- `test_push_conspiracy.py` - Simple upload (supports --env)
- `test_query_arkiv.py` - Query examples
- `test_discover_all.py` - Discovery script

---

## Next Steps

1. Run E2E test: `uv run python test_e2e_conspiracy_arkiv.py`
2. Verify on Arkiv explorer
3. Update frontend to filter by environment
4. Create cleanup script for old dev data



