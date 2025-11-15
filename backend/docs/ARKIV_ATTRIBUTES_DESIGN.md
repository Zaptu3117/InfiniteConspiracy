# Arkiv Attributes Design
## From Generic to Semantic

---

## ❌ Poor Attributes (Generic, No Meaning)

```typescript
// Current implementation
attributes: {
  "entity_type": "metadata",  // ❌ Generic technical term
  "mystery_id": "07a99a47..."
}

// Query
query.where(eq('entity_type', 'metadata'))  // ❌ What is "metadata"?
```

**Problems:**
- ❌ "metadata" is a generic technical term
- ❌ No semantic meaning for users
- ❌ Can't filter by world, difficulty, theme
- ❌ Not descriptive

---

## ✅ Good Attributes (Semantic, Meaningful)

```typescript
// Improved implementation
attributes: {
  "resource_type": "conspiracy",  // ✅ Clear purpose!
  "mystery_id": "07a99a47...",
  "world": "Eclipsed Dominion",  // ✅ Filterable by game world
  "difficulty": "6",              // ✅ Filterable by difficulty
  "conspiracy_type": "occult",    // ✅ Filterable by theme
  "status": "active",             // ✅ Filterable by state
  "total_docs": "46"              // ✅ Quick stats
}

// Queries
query.where(eq('resource_type', 'conspiracy'))  // ✅ Discover conspiracies
query.where(eq('world', 'Eclipsed Dominion'))   // ✅ Filter by world
query.where(eq('difficulty', '7'))              // ✅ Find hard mysteries
query.where(eq('conspiracy_type', 'occult'))    // ✅ Filter by theme
```

**Benefits:**
- ✅ Semantic, descriptive naming
- ✅ Multiple useful filters
- ✅ Self-documenting
- ✅ Better UX for frontend

---

## Comparison Table

| Use Case | Poor Approach | Good Approach |
|----------|--------------|---------------|
| **Discover all conspiracies** | `entity_type = "metadata"` ❌ | `resource_type = "conspiracy"` ✅ |
| **Filter by world** | ❌ Not possible | `world = "Eclipsed Dominion"` ✅ |
| **Filter by difficulty** | ❌ Not possible | `difficulty = "7"` ✅ |
| **Filter by theme** | ❌ Not possible | `conspiracy_type = "occult"` ✅ |
| **Get all emails** | ❌ Query all docs, filter in-memory | `doc_type = "email"` ✅ |
| **Find active mysteries** | ❌ Not possible | `status = "active"` ✅ |

---

## Recommended Attribute Schema

### Conspiracy (Metadata)

```typescript
{
  // Identity
  "resource_type": "conspiracy",  // Discovery
  "mystery_id": string,           // Unique ID
  
  // Filters
  "world": string,                // "Eclipsed Dominion", "The Commonwealth"
  "difficulty": string,           // "1" to "10"
  "conspiracy_type": string,      // "occult", "political", "corporate"
  "status": string,               // "active", "completed", "archived"
  
  // Stats (optional)
  "total_docs": string,           // "46"
  "creator": string,              // "0x1234..." (wallet address)
  "created_date": string          // "2025-11-15"
}
```

### Document

```typescript
{
  // Identity
  "resource_type": "document",    // Type
  "mystery_id": string,           // Parent mystery
  "document_id": string,          // Unique ID
  
  // Filters
  "doc_type": string,             // "email", "network_log", "diary"
  "world": string,                // Same as parent mystery
  
  // Optional
  "is_encrypted": string,         // "true" | "false"
  "character": string             // Character who authored it
}
```

### Image

```typescript
{
  // Identity
  "resource_type": "image",       // Type
  "mystery_id": string,           // Parent mystery
  "image_id": string,             // Unique ID
  
  // Filters
  "world": string,                // Same as parent mystery
  "image_type": string            // "clue", "character", "location"
}
```

---

## Frontend Query Examples

### Discovery & Browse

```typescript
// 1. Discover all conspiracies
const conspiracies = await query
  .where(eq('resource_type', 'conspiracy'))
  .withPayload(true)
  .fetch()

// 2. Filter by world
const eclipsedMysteries = await query
  .where(eq('resource_type', 'conspiracy'))
  .where(eq('world', 'Eclipsed Dominion'))
  .fetch()

// 3. Filter by difficulty (hard mysteries)
const hardMysteries = await query
  .where(eq('resource_type', 'conspiracy'))
  .where(eq('difficulty', '7'))
  .fetch()

// 4. Filter by theme
const occultMysteries = await query
  .where(eq('resource_type', 'conspiracy'))
  .where(eq('conspiracy_type', 'occult'))
  .fetch()

// 5. Only active mysteries
const activeMysteries = await query
  .where(eq('resource_type', 'conspiracy'))
  .where(eq('status', 'active'))
  .fetch()
```

### Document Queries

```typescript
// 1. Get all emails in a mystery
const emails = await query
  .where(eq('mystery_id', mysteryId))
  .where(eq('doc_type', 'email'))
  .fetch()

// 2. Get all logs
const logs = await query
  .where(eq('mystery_id', mysteryId))
  .where(eq('doc_type', 'network_log'))
  .fetch()

// 3. Get encrypted documents
const encrypted = await query
  .where(eq('mystery_id', mysteryId))
  .where(eq('is_encrypted', 'true'))
  .fetch()
```

---

## Migration Plan

### Phase 1: Add Semantic Attributes (Now)
- ✅ Update `test_push_conspiracy.py` to use semantic attributes
- ✅ Keep backwards compatibility (keep old attributes)

### Phase 2: Update Docs (Now)
- ✅ Update frontend guide with semantic queries
- ✅ Show examples of world/difficulty/type filtering

### Phase 3: Deprecate Generic Attributes (Future)
- Remove `entity_type` attribute
- Use only `resource_type`

---

## Code Implementation

See: `/backend/test_push_conspiracy_semantic.py`

**Before:**
```python
"attributes": {
    "entity_type": "metadata",  # ❌
    "mystery_id": mystery_id
}
```

**After:**
```python
"attributes": {
    "resource_type": "conspiracy",  # ✅
    "mystery_id": mystery_id,
    "world": world_name,
    "difficulty": str(difficulty),
    "conspiracy_type": "occult",
    "status": "active"
}
```

---

## Benefits Summary

1. **Semantic Discovery:** `resource_type = "conspiracy"` is self-explanatory
2. **Rich Filtering:** Filter by world, difficulty, theme, status
3. **Better UX:** Frontend can build rich filters
4. **Self-Documenting:** Attributes explain themselves
5. **Scalable:** Easy to add new filters (tags, characters, etc.)

---

## Next Steps

1. Run `test_push_conspiracy_semantic.py` to upload with new attributes
2. Update frontend queries to use semantic filters
3. Build rich UI with world/difficulty/theme selectors
4. Consider adding more attributes:
   - `tags` (comma-separated: "mystery,noir,cyberpunk")
   - `language` ("en", "fr", "es")
   - `rating` (community ratings)
   - `plays` (number of times played)

