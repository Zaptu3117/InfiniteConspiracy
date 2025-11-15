# Frontend Quick Reference - Arkiv Queries

## 🚀 Setup (30 seconds)

```bash
npm install @arkiv-network/sdk
```

```typescript
import { createPublicClient, http } from "@arkiv-network/sdk"
import { mendoza } from "@arkiv-network/sdk/chains"
import { eq } from "@arkiv-network/sdk/query"

const arkiv = createPublicClient({
  chain: mendoza,
  transport: http(),
})
```

---

## 📚 Common Queries

### 🔍 Discover All Conspiracies (Main Entry Point)

```typescript
// ✅ DISCOVERY: Get all available conspiracies
const query = arkiv.buildQuery()
const entities = await query
  .where(eq('entity_type', 'metadata'))
  .withPayload(true)
  .fetch()

const conspiracies = entities
  .map(e => JSON.parse(e.payload))
  .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

// Each has: mystery_id, conspiracy_name, world, difficulty, total_documents
```

### Get Full Mystery

```typescript
const query = arkiv.buildQuery()
const entities = await query
  .where(eq('mystery_id', mysteryId))
  .withPayload(true)
  .withAttributes(true)
  .fetch()

const metadata = entities.find(e => e.attributes.entity_type === 'metadata')
const documents = entities.filter(e => e.attributes.entity_type === 'document')
```

### Get Single Document

```typescript
const query = arkiv.buildQuery()
const entities = await query
  .where(eq('mystery_id', mysteryId))
  .where(eq('document_id', documentId))
  .withPayload(true)
  .fetch()

const doc = JSON.parse(entities[0].payload)
```

---

## 📦 Entity Types

| Entity Type | Attributes | Payload |
|------------|-----------|---------|
| `metadata` | `entity_type`, `mystery_id` | JSON: mystery info |
| `document` | `entity_type`, `mystery_id`, `document_id` | JSON: document data |
| `image` | `entity_type`, `mystery_id`, `document_id` | Binary: PNG bytes |

---

## 🔍 Document Types

```
email, internal_memo, witness_statement, diary, report,
network_log, vpn_log, door_access_log, login_history,
call_log, encrypted
```

---

## ⚡ React Hook

```typescript
function useMysteries() {
  const [mysteries, setMysteries] = useState([])
  const arkiv = useArkivClient()
  
  useEffect(() => {
    async function load() {
      const query = arkiv.buildQuery()
      const entities = await query
        .where(eq('entity_type', 'metadata'))
        .withPayload(true)
        .fetch()
      
      setMysteries(entities.map(e => JSON.parse(e.payload)))
    }
    load()
  }, [arkiv])
  
  return mysteries
}
```

---

## 🌐 Network Config

```typescript
Chain ID: 60138453056 (0xe0087f840)
RPC: https://mendoza.hoodi.arkiv.network/rpc
WebSocket: wss://mendoza.hoodi.arkiv.network/rpc/ws
Explorer: https://explorer.mendoza.hoodi.arkiv.network
```

---

## 💾 Example Mystery Data

### Metadata
```json
{
  "mystery_id": "07a99a47-2a67-426a-b28d-5c26a39fe1d4",
  "conspiracy_name": "Operation Abyssal Convergence",
  "world": "Eclipsed Dominion",
  "difficulty": 6,
  "total_documents": 46,
  "created_at": "2025-11-15T19:59:44.627608"
}
```

### Document
```json
{
  "document_id": "doc_5_email",
  "document_type": "email",
  "fields": {
    "from": "john@example.com",
    "to": ["sarah@example.com"],
    "subject": "Meeting Notes",
    "body": "...",
    "date": "2025-11-13"
  }
}
```

---

## 📘 Full Documentation

See: `/backend/docs/FRONTEND_ARKIV_INTEGRATION.md`

