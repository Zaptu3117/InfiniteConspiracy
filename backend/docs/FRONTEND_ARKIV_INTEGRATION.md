# Frontend Arkiv Integration Guide
## Querying Conspiracy Mysteries & Documents

> **Last Updated:** November 2025  
> **Arkiv SDK:** v0.1.19  
> **Network:** Mendoza Testnet

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Setup & Installation](#setup--installation)
4. [Querying Mysteries](#querying-mysteries)
5. [Document Structure](#document-structure)
6. [Code Examples](#code-examples)
7. [React Hooks](#react-hooks)
8. [Best Practices](#best-practices)

---

## Overview

### What's Stored on Arkiv?

Each conspiracy mystery consists of:
- **1 Metadata Entity:** Mystery info (name, difficulty, world, etc.)
- **N Document Entities:** Mystery documents (emails, logs, reports, etc.)
- **M Image Entities:** Visual clues (encrypted images)

### Entity Structure

```typescript
interface ConspiracyMetadata {
  entity_type: "metadata"
  mystery_id: string
  conspiracy_name: string
  world: string
  difficulty: number
  total_documents: number
  created_at: string
}

interface ConspiracyDocument {
  entity_type: "document"
  mystery_id: string
  document_id: string
  document_type: string
  fields: Record<string, any>
}

interface ConspiracyImage {
  entity_type: "image"
  mystery_id: string
  image_id: string
  // payload is raw PNG bytes
}
```

### Arkiv Attributes (Queryable)

All entities have these **searchable attributes**:
- `mystery_id` (string) - Groups all entities for a mystery
- `entity_type` (string) - "metadata", "document", or "image"
- `document_id` (string) - Unique document identifier (documents only)

---

## Quick Start

### 1. Install SDK

```bash
npm install @arkiv-network/sdk
# or
bun add @arkiv-network/sdk
```

### 2. Create Read-Only Client

```typescript
import { createPublicClient, http } from "@arkiv-network/sdk"
import { mendoza } from "@arkiv-network/sdk/chains"

// No wallet needed for reading!
const arkiv = createPublicClient({
  chain: mendoza,
  transport: http(),
})
```

### 3. Query Mystery

```typescript
import { eq } from "@arkiv-network/sdk/query"

// Get all entities for a mystery
const query = arkiv.buildQuery()
const entities = await query
  .where(eq('mystery_id', '07a99a47-2a67-426a-b28d-5c26a39fe1d4'))
  .withPayload(true)
  .withAttributes(true)
  .fetch()

// Separate by type
const metadata = entities.filter(e => e.attributes.entity_type === "metadata")[0]
const documents = entities.filter(e => e.attributes.entity_type === "document")
const images = entities.filter(e => e.attributes.entity_type === "image")
```

---

## Setup & Installation

### Network Configuration

```typescript
// Arkiv Mendoza Testnet
const ARKIV_CONFIG = {
  chainId: '0xe0087f840', // 60138453056 in hex
  chainName: 'Arkiv Mendoza Testnet',
  rpcUrl: 'https://mendoza.hoodi.arkiv.network/rpc',
  wsUrl: 'wss://mendoza.hoodi.arkiv.network/rpc/ws',
  explorer: 'https://explorer.mendoza.hoodi.arkiv.network',
  nativeCurrency: {
    name: 'ETH',
    symbol: 'ETH',
    decimals: 18
  }
}
```

### Add Network to MetaMask (Optional)

If users want to create/update mysteries (not needed for just reading):

```typescript
async function addArkivNetwork() {
  try {
    await window.ethereum.request({
      method: 'wallet_addEthereumChain',
      params: [{
        chainId: ARKIV_CONFIG.chainId,
        chainName: ARKIV_CONFIG.chainName,
        nativeCurrency: ARKIV_CONFIG.nativeCurrency,
        rpcUrls: [ARKIV_CONFIG.rpcUrl],
        blockExplorerUrls: [ARKIV_CONFIG.explorer]
      }]
    })
  } catch (error) {
    console.error('Failed to add network:', error)
  }
}
```

---

## Querying Mysteries

### 1. 🔍 Discover All Available Conspiracies

**This is the main entry point!** Query all conspiracies by filtering for metadata entities:

```typescript
import { eq } from "@arkiv-network/sdk/query"

// ✅ DISCOVERY QUERY: Get all conspiracies (semantic attribute!)
const query = arkiv.buildQuery()
const metadataEntities = await query
  .where(eq('resource_type', 'conspiracy'))
  .withPayload(true)
  .fetch()

// Parse and sort by most recent
const conspiracies = metadataEntities
  .map(entity => {
    const data = JSON.parse(entity.payload)
    return {
      mystery_id: data.mystery_id,
      name: data.conspiracy_name,
      world: data.world,
      difficulty: data.difficulty,
      totalDocuments: data.total_documents,
      createdAt: new Date(data.created_at)
    }
  })
  .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())

console.log(`🔍 Discovered ${conspiracies.length} conspiracies!`)

// Example output:
// 🔍 Discovered 3 conspiracies!
// [
//   {
//     mystery_id: "07a99a47-2a67-426a-b28d-5c26a39fe1d4",
//     name: "Operation Abyssal Convergence",
//     world: "Eclipsed Dominion",
//     difficulty: 6,
//     totalDocuments: 46,
//     createdAt: Date
//   },
//   ...
// ]
```

**Why this works:**
- Each conspiracy has **exactly 1 metadata entity**
- Metadata entities have `resource_type = "conspiracy"` (semantic!)
- No need to know mystery IDs in advance!
- Perfect for building a conspiracy list/browser UI

**Bonus filters available:**
- `world` - Filter by game world
- `difficulty` - Filter by difficulty level
- `conspiracy_type` - Filter by theme (occult, political, etc.)
- `status` - Filter by active/completed state

### 2. Get Full Mystery (Metadata + Documents)

```typescript
async function getMystery(mysteryId: string) {
  const query = arkiv.buildQuery()
  const entities = await query
    .where(eq('mystery_id', mysteryId))
    .withPayload(true)
    .withAttributes(true)
    .fetch()
  
  // Separate entities by resource_type
  const metadataEntity = entities.find(e => 
    e.attributes.resource_type === "conspiracy"
  )
  
  const documentEntities = entities.filter(e => 
    e.attributes.resource_type === "document"
  )
  
  const imageEntities = entities.filter(e => 
    e.attributes.resource_type === "image"
  )
  
  // Parse metadata
  const metadata = JSON.parse(metadataEntity.payload)
  
  // Parse documents
  const documents = documentEntities.map(entity => {
    const doc = JSON.parse(entity.payload)
    return {
      document_id: doc.document_id,
      document_type: doc.document_type,
      fields: doc.fields,
      entityKey: entity.entityKey
    }
  })
  
  // Parse images (payload is raw bytes)
  const images = imageEntities.map(entity => ({
    image_id: entity.attributes.document_id,
    imageData: entity.payload, // Uint8Array
    entityKey: entity.entityKey
  }))
  
  return {
    metadata,
    documents,
    images
  }
}

// Usage
const mystery = await getMystery('07a99a47-2a67-426a-b28d-5c26a39fe1d4')
console.log(`Mystery: ${mystery.metadata.conspiracy_name}`)
console.log(`Documents: ${mystery.documents.length}`)
```

### 3. Get Single Document

```typescript
async function getDocument(mysteryId: string, documentId: string) {
  const query = arkiv.buildQuery()
  const entities = await query
    .where(eq('mystery_id', mysteryId))
    .where(eq('document_id', documentId))
    .withPayload(true)
    .fetch()
  
  if (entities.length === 0) {
    throw new Error(`Document ${documentId} not found`)
  }
  
  const doc = JSON.parse(entities[0].payload)
  return {
    document_id: doc.document_id,
    document_type: doc.document_type,
    fields: doc.fields
  }
}

// Usage
const email = await getDocument(mysteryId, 'doc_5_email')
console.log(`From: ${email.fields.from}`)
console.log(`Subject: ${email.fields.subject}`)
```

### 4. Filter Documents by Type

```typescript
async function getDocumentsByType(mysteryId: string, docType: string) {
  const query = arkiv.buildQuery()
  const entities = await query
    .where(eq('mystery_id', mysteryId))
    .where(eq('entity_type', 'document'))
    .withPayload(true)
    .fetch()
  
  // Filter in-memory (Arkiv doesn't support nested attribute queries)
  const filtered = entities
    .map(e => JSON.parse(e.payload))
    .filter(doc => doc.document_type === docType)
  
  return filtered
}

// Usage
const emails = await getDocumentsByType(mysteryId, 'email')
const logs = await getDocumentsByType(mysteryId, 'network_log')
```

---

## Document Structure

### Common Document Types

```typescript
type DocumentType = 
  | "email"
  | "internal_memo"
  | "witness_statement"
  | "diary"
  | "report"
  | "network_log"
  | "vpn_log"
  | "door_access_log"
  | "login_history"
  | "call_log"
  | "encrypted"

interface EmailDocument {
  document_id: string
  document_type: "email"
  fields: {
    from: string
    to: string[]
    subject: string
    body: string
    date: string
    attachments?: string[]
  }
}

interface NetworkLogDocument {
  document_id: string
  document_type: "network_log"
  fields: {
    network_segment: string
    log_date: string
    entries: Array<{
      timestamp: string
      source_ip: string
      destination_ip: string
      protocol: string
      notes: string
    }>
  }
}

interface EncryptedDocument {
  document_id: string
  document_type: "encrypted"
  fields: {
    from: string  // Contains "[Encrypted]: ..." text
    to: string[]
    subject: string
    content: string
  }
}
```

### Parsing Document Fields

```typescript
function parseDocument(entity: Entity) {
  const doc = JSON.parse(entity.payload)
  
  // Type-specific parsing
  switch (doc.document_type) {
    case 'email':
      return {
        ...doc,
        parsedDate: new Date(doc.fields.date),
        isEncrypted: doc.fields.from.includes('[Encrypted]')
      }
    
    case 'network_log':
      return {
        ...doc,
        entries: doc.fields.entries.map(e => ({
          ...e,
          timestamp: new Date(e.timestamp)
        }))
      }
    
    case 'witness_statement':
      return {
        ...doc,
        statementDate: new Date(doc.fields.statement_date)
      }
    
    default:
      return doc
  }
}
```

---

## Code Examples

### Example 1: Mystery Browser UI

```typescript
import { createPublicClient, http } from "@arkiv-network/sdk"
import { mendoza } from "@arkiv-network/sdk/chains"
import { eq } from "@arkiv-network/sdk/query"

const arkiv = createPublicClient({
  chain: mendoza,
  transport: http(),
})

async function loadMysteryList() {
  const query = arkiv.buildQuery()
  const entities = await query
    .where(eq('entity_type', 'metadata'))
    .withPayload(true)
    .fetch()
  
  return entities.map(e => {
    const data = JSON.parse(e.payload)
    return {
      id: data.mystery_id,
      name: data.conspiracy_name,
      world: data.world,
      difficulty: data.difficulty,
      documentCount: data.total_documents,
      created: new Date(data.created_at)
    }
  }).sort((a, b) => b.created.getTime() - a.created.getTime())
}

// Render
const mysteries = await loadMysteryList()
mysteries.forEach(m => {
  console.log(`${m.name} (${m.difficulty}/10) - ${m.documentCount} docs`)
})
```

### Example 2: Document Explorer

```typescript
async function loadMysteryDocuments(mysteryId: string) {
  const query = arkiv.buildQuery()
  const entities = await query
    .where(eq('mystery_id', mysteryId))
    .where(eq('entity_type', 'document'))
    .withPayload(true)
    .withAttributes(true)
    .fetch()
  
  const documents = entities.map(e => ({
    ...JSON.parse(e.payload),
    entityKey: e.entityKey,
    attributes: e.attributes
  }))
  
  // Group by type
  const grouped = documents.reduce((acc, doc) => {
    const type = doc.document_type
    if (!acc[type]) acc[type] = []
    acc[type].push(doc)
    return acc
  }, {} as Record<string, any[]>)
  
  return grouped
}

// Usage
const docs = await loadMysteryDocuments(mysteryId)
console.log('Emails:', docs.email?.length || 0)
console.log('Logs:', docs.network_log?.length || 0)
console.log('Memos:', docs.internal_memo?.length || 0)
```

### Example 3: Real-time Updates

```typescript
function watchMysteries(onNewMystery: (mystery: any) => void) {
  const unwatch = arkiv.watchEntities({
    onCreated: async (event) => {
      // Check if it's a metadata entity
      if (event.attributes?.entity_type === 'metadata') {
        // Fetch full entity
        const entity = await arkiv.getEntity(event.entityKey)
        const mystery = JSON.parse(entity.payload)
        onNewMystery(mystery)
      }
    },
    pollingInterval: 5000 // Check every 5 seconds
  })
  
  return unwatch // Call to stop watching
}

// Usage
const stopWatching = watchMysteries((mystery) => {
  console.log(`New mystery: ${mystery.conspiracy_name}`)
  // Update UI
})

// Later: stopWatching()
```

---

## React Hooks

### useArkivClient Hook

```typescript
import { createPublicClient, http } from "@arkiv-network/sdk"
import { mendoza } from "@arkiv-network/sdk/chains"
import { useMemo } from 'react'

export function useArkivClient() {
  const client = useMemo(() => 
    createPublicClient({
      chain: mendoza,
      transport: http(),
    }), []
  )
  
  return client
}
```

### useMysteries Hook

```typescript
import { useState, useEffect } from 'react'
import { eq } from "@arkiv-network/sdk/query"

export function useMysteries() {
  const [mysteries, setMysteries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const arkiv = useArkivClient()
  
  useEffect(() => {
    async function load() {
      try {
        const query = arkiv.buildQuery()
        const entities = await query
          .where(eq('entity_type', 'metadata'))
          .withPayload(true)
          .fetch()
        
        const parsed = entities.map(e => JSON.parse(e.payload))
        setMysteries(parsed)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    
    load()
  }, [arkiv])
  
  return { mysteries, loading, error }
}

// Usage in component
function MysteryList() {
  const { mysteries, loading, error } = useMysteries()
  
  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  
  return (
    <ul>
      {mysteries.map(m => (
        <li key={m.mystery_id}>
          {m.conspiracy_name} - {m.difficulty}/10
        </li>
      ))}
    </ul>
  )
}
```

### useMysteryDocuments Hook

```typescript
export function useMysteryDocuments(mysteryId: string) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const arkiv = useArkivClient()
  
  useEffect(() => {
    if (!mysteryId) return
    
    async function load() {
      try {
        const query = arkiv.buildQuery()
        const entities = await query
          .where(eq('mystery_id', mysteryId))
          .where(eq('entity_type', 'document'))
          .withPayload(true)
          .fetch()
        
        const parsed = entities.map(e => JSON.parse(e.payload))
        setDocuments(parsed)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    
    load()
  }, [mysteryId, arkiv])
  
  return { documents, loading, error }
}
```

---

## Best Practices

### 1. Caching

```typescript
// Cache mysteries in localStorage
const CACHE_KEY = 'arkiv_mysteries_cache'
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

async function getCachedMysteries() {
  const cached = localStorage.getItem(CACHE_KEY)
  if (cached) {
    const { data, timestamp } = JSON.parse(cached)
    if (Date.now() - timestamp < CACHE_TTL) {
      return data
    }
  }
  
  // Fetch fresh data
  const mysteries = await loadMysteryList()
  localStorage.setItem(CACHE_KEY, JSON.stringify({
    data: mysteries,
    timestamp: Date.now()
  }))
  
  return mysteries
}
```

### 2. Error Handling

```typescript
async function safeQuery<T>(queryFn: () => Promise<T>): Promise<T | null> {
  try {
    return await queryFn()
  } catch (error) {
    if (error.message.includes('network')) {
      console.error('Network error - check Arkiv connection')
    } else if (error.message.includes('not found')) {
      console.error('Entity not found')
    } else {
      console.error('Unknown error:', error)
    }
    return null
  }
}

// Usage
const mystery = await safeQuery(() => getMystery(mysteryId))
if (!mystery) {
  // Handle error in UI
}
```

### 3. Pagination

```typescript
async function getMysteryDocumentsPaginated(
  mysteryId: string,
  page: number = 1,
  pageSize: number = 10
) {
  const query = arkiv.buildQuery()
  const entities = await query
    .where(eq('mystery_id', mysteryId))
    .where(eq('entity_type', 'document'))
    .withPayload(true)
    .fetch()
  
  const documents = entities.map(e => JSON.parse(e.payload))
  
  // Paginate in-memory (Arkiv doesn't support offset/limit yet)
  const start = (page - 1) * pageSize
  const end = start + pageSize
  
  return {
    documents: documents.slice(start, end),
    total: documents.length,
    page,
    pageSize,
    totalPages: Math.ceil(documents.length / pageSize)
  }
}
```

### 4. Type Safety

```typescript
// Define strict types
interface Mystery {
  mystery_id: string
  conspiracy_name: string
  world: string
  difficulty: number
  total_documents: number
  created_at: string
}

interface Document {
  document_id: string
  document_type: string
  fields: Record<string, any>
}

// Type-safe query
async function getMysteryTyped(mysteryId: string): Promise<Mystery | null> {
  const query = arkiv.buildQuery()
  const entities = await query
    .where(eq('mystery_id', mysteryId))
    .where(eq('entity_type', 'metadata'))
    .withPayload(true)
    .fetch()
  
  if (entities.length === 0) return null
  
  return JSON.parse(entities[0].payload) as Mystery
}
```

---

## Performance Tips

1. **Use `withPayload(false)` when you only need metadata:**
   ```typescript
   const keys = await query
     .where(eq('entity_type', 'document'))
     .withPayload(false) // Faster!
     .fetch()
   ```

2. **Batch queries instead of sequential:**
   ```typescript
   // ❌ Slow
   for (const id of mysteryIds) {
     await getMystery(id)
   }
   
   // ✅ Fast
   await Promise.all(mysteryIds.map(id => getMystery(id)))
   ```

3. **Use real-time watching sparingly:**
   ```typescript
   // Only watch when user is actively viewing
   useEffect(() => {
     if (isActive) {
       const unwatch = watchMysteries(onUpdate)
       return unwatch
     }
   }, [isActive])
   ```

---

## Example: Complete Mystery Viewer

```typescript
import { useState } from 'react'
import { useArkivClient } from './hooks/useArkivClient'
import { eq } from "@arkiv-network/sdk/query"

function MysteryViewer({ mysteryId }: { mysteryId: string }) {
  const [mystery, setMystery] = useState(null)
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const arkiv = useArkivClient()
  
  useEffect(() => {
    async function load() {
      setLoading(true)
      
      // Query all entities for this mystery
      const query = arkiv.buildQuery()
      const entities = await query
        .where(eq('mystery_id', mysteryId))
        .withPayload(true)
        .withAttributes(true)
        .fetch()
      
      // Separate metadata and documents
      const meta = entities.find(e => e.attributes.entity_type === 'metadata')
      const docs = entities.filter(e => e.attributes.entity_type === 'document')
      
      setMystery(JSON.parse(meta.payload))
      setDocuments(docs.map(e => JSON.parse(e.payload)))
      setLoading(false)
    }
    
    load()
  }, [mysteryId, arkiv])
  
  if (loading) return <div>Loading mystery...</div>
  if (!mystery) return <div>Mystery not found</div>
  
  return (
    <div>
      <h1>{mystery.conspiracy_name}</h1>
      <p>World: {mystery.world}</p>
      <p>Difficulty: {mystery.difficulty}/10</p>
      
      <h2>Documents ({documents.length})</h2>
      <ul>
        {documents.map(doc => (
          <li key={doc.document_id}>
            <strong>{doc.document_id}</strong> ({doc.document_type})
          </li>
        ))}
      </ul>
    </div>
  )
}
```

---

## Resources

- **Arkiv SDK Docs:** https://docs.arkiv.network/
- **TypeScript SDK:** https://www.npmjs.com/package/@arkiv-network/sdk
- **GitHub:** https://github.com/arkiv-network
- **Discord:** https://discord.gg/arkiv
- **Mendoza Explorer:** https://explorer.mendoza.hoodi.arkiv.network

---

## Need Help?

Contact the backend team or check:
- Backend integration: `/backend/test_query_arkiv.py`
- Upload script: `/backend/test_push_conspiracy.py`
- Entity structure: `/backend/src/arkiv_integration/entity_builder.py`

