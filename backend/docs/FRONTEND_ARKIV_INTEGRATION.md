# Frontend Arkiv Integration Guide
## Querying Conspiracy Mysteries & Documents

> **Last Updated:** November 2025  
> **Arkiv SDK:** v0.1.19  
> **Network:** Mendoza Testnet

---

## 🎯 Document Structure Update (November 2025)

**IMPORTANT:** Narrative documents (`email`, `diary`, `internal_memo`) now use **pure narrative text** structure:

✅ **Clean Structure:**
- Email: `{ from, to, subject, body }`
- Diary: `{ date, author, content, mood }`
- Internal Memo: `{ from, to, subject, date, content }`

❌ **No Technical Arrays:**
- No `entries` arrays in diaries
- No `sections` arrays in memos
- No `logs`, `emails`, `diaries` contamination

Narrative documents contain only flowing text in their content fields. Technical documents (server logs, network logs, etc.) continue to use structured arrays as appropriate.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Setup & Installation](#setup--installation)
4. [Querying Mysteries](#querying-mysteries)
5. [Test Conspiracy Example](#test-conspiracy-example)
6. [Document Structure](#document-structure)
7. [Complete Document Type Reference](#complete-document-type-reference)
8. [Code Examples](#code-examples)
9. [React Hooks](#react-hooks)
10. [Best Practices](#best-practices)

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

## Test Conspiracy Example

### Current Dev Test Mystery

There's currently a test mystery deployed on Arkiv for development/testing:

```typescript
// Test Mystery Metadata
{
  mystery_id: "6e7c6a60-adf7-4219-a3fe-4acd82e54889",
  conspiracy_name: "Operation Eclipse Veil",
  world: "The Veiled Republic",
  difficulty: 6,
  conspiracy_type: "occult",
  total_documents: 50,
  environment: "dev"
}
```

### Query This Test Mystery

```typescript
// Method 1: Query by mystery_id directly
const query = arkiv.buildQuery()
const entities = await query
  .where(eq('mystery_id', '6e7c6a60-adf7-4219-a3fe-4acd82e54889'))
  .withPayload(true)
  .withAttributes(true)
  .fetch()

// Method 2: Query all dev conspiracies
const devQuery = arkiv.buildQuery()
const devConspiracies = await devQuery
  .where(eq('environment', 'dev'))
  .where(eq('resource_type', 'conspiracy'))
  .withPayload(true)
  .fetch()

// Method 3: Filter by world
const worldQuery = arkiv.buildQuery()
const veiledRepublicMysteries = await worldQuery
  .where(eq('world', 'The Veiled Republic'))
  .where(eq('resource_type', 'conspiracy'))
  .withPayload(true)
  .fetch()
```

### Expected Response Structure

```typescript
// Metadata entity
{
  entityKey: "0x...",
  owner: "0x4deb2cb051a82b51a7fdc8a9b3aafb081723a5de",
  payload: {
    mystery_id: "6e7c6a60-adf7-4219-a3fe-4acd82e54889",
    conspiracy_name: "Operation Eclipse Veil",
    world: "The Veiled Republic",
    difficulty: 6,
    conspiracy_type: "occult",
    total_documents: 50,
    premise: "An occult conspiracy involving...",
    created_at: "2025-11-15T..."
  },
  attributes: {
    resource_type: "conspiracy",
    mystery_id: "6e7c6a60-adf7-4219-a3fe-4acd82e54889",
    world: "The Veiled Republic",
    difficulty: "6",
    conspiracy_type: "occult",
    environment: "dev",
    status: "active"
  }
}

// Document entities (50 total)
{
  entityKey: "0x...",
  owner: "0x4deb2cb051a82b51a7fdc8a9b3aafb081723a5de",
  payload: {
    document_id: "doc_0_encrypted",
    document_type: "internal_memo",
    fields: {
      from: "High Priestess Nyx Armand...",
      to: ["Head of Arcane Infrastructure..."],
      subject: "Operational Update...",
      date: "2025-11-06",
      content: "..."
    }
  },
  attributes: {
    resource_type: "document",
    mystery_id: "6e7c6a60-adf7-4219-a3fe-4acd82e54889",
    document_id: "doc_0_encrypted",
    doc_type: "internal_memo",
    world: "The Veiled Republic",
    environment: "dev"
  }
}
```

### Document Types in This Mystery

The test mystery contains these document types:
- `internal_memo` - Official memos with bureaucratic language
- `diary` - Personal diary entries with introspection
- `witness_statement` - Formal witness testimonies
- `email` - Email correspondence
- `network_log` - Technical network activity logs
- `server_log` - Server system logs
- `access_control` - Badge access and security logs
- `vpn_log` - VPN connection logs

---

## Document Structure

### All Document Types

```typescript
type DocumentType = 
  | "email"                  // Email correspondence
  | "internal_memo"          // Official internal memos
  | "witness_statement"      // Formal witness testimonies
  | "diary"                  // Personal diary entries
  | "police_report"          // Police incident reports
  | "badge_log"              // Badge access logs
  | "login_history"          // System authentication logs
  | "server_log"             // Server system logs
  | "firewall_log"           // Firewall activity logs
  | "network_log"            // Network traffic logs
  | "access_control"         // Security access control logs
  | "vpn_log"                // VPN connection logs
  | "door_access_log"        // Physical door access logs
  | "it_inventory"           // IT asset inventory
  | "security_scan"          // Security vulnerability scans
  | "device_registry"        // Device registration records
  | "asset_database"         // Asset database records
  | "phone_record"           // Phone call records
```

### Common Document Interfaces

```typescript
// Base document structure
interface BaseDocument {
  document_id: string
  document_type: DocumentType
  timestamp?: string
  author?: string
  fields: Record<string, any>
}

// Email
interface EmailDocument extends BaseDocument {
  document_type: "email"
  fields: {
    from: string
    to: string | string[]
    subject: string
    body: string
    date?: string
    attachments?: string[]
  }
}

// Internal Memo
interface InternalMemoDocument extends BaseDocument {
  document_type: "internal_memo"
  fields: {
    from: string
    to: string | string[]
    subject: string
    date: string
    content: string              // Pure narrative text
  }
}

// Diary
interface DiaryDocument extends BaseDocument {
  document_type: "diary"
  fields: {
    date: string
    author: string
    content: string              // Pure narrative text
    mood?: string
  }
}

// Witness Statement
interface WitnessStatementDocument extends BaseDocument {
  document_type: "witness_statement"
  fields: {
    witness_name: string
    statement_date: string
    interviewer: string
    location: string
    statement: string
    details?: Array<{
      question: string
      answer: string | any[]
    }>
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

## Complete Document Type Reference

### Communication Documents

#### 1. Email (`email`)

```typescript
interface EmailDocument {
  document_id: string
  document_type: "email"
  fields: {
    from: string                    // Sender email
    to: string | string[]           // Recipient(s)
    subject: string                 // Email subject
    body: string                    // Pure narrative email body (3-5 paragraphs)
    date?: string                   // Send date
    attachments?: string[]          // Attachment names
  }
}
```

**Example:**
```json
{
  "document_id": "doc_5_email",
  "document_type": "email",
  "fields": {
    "from": "john.doe@company.com",
    "to": ["jane.smith@company.com", "admin@company.com"],
    "subject": "Q4 Security Review",
    "body": "Hello team,\n\nI've reviewed the latest security logs...",
    "date": "2025-11-15",
    "attachments": ["security_report_q4.pdf"]
  }
}
```

#### 2. Internal Memo (`internal_memo`)

```typescript
interface InternalMemoDocument {
  document_id: string
  document_type: "internal_memo"
  fields: {
    from: string                    // Sender
    to: string | string[]           // Recipients
    subject: string                 // Memo subject
    date: string                    // Issue date
    content: string                 // Pure narrative memo text (multiple paragraphs)
  }
}
```

**Example:**
```json
{
  "document_id": "doc_12_memo",
  "document_type": "internal_memo",
  "fields": {
    "from": "Director of Operations",
    "to": ["All Department Heads"],
    "subject": "New Security Protocols",
    "date": "2025-11-15",
    "content": "To: All Department Heads\nFrom: Director of Operations\nSubject: New Security Protocols\nDate: 2025-11-15\n\nBackground:\nRecent security assessments have identified several areas requiring immediate attention. After consultation with the security team, we have developed a comprehensive set of protocols to address these concerns.\n\nNew Requirements:\nEffective immediately, all staff must comply with the following:\n1. All badge access must be logged and reviewed weekly\n2. Two-factor authentication is now mandatory for all systems\n3. Quarterly security training is required for all personnel\n\nThese measures are critical to maintaining the integrity of our operations."
  }
}
```

### Personal Documents

#### 3. Diary (`diary`)

```typescript
interface DiaryDocument {
  document_id: string
  document_type: "diary"
  fields: {
    date: string                    // Entry date
    author: string                  // Diary owner
    content: string                 // Pure narrative diary text (3-5 paragraphs)
    mood?: string                   // Optional mood
  }
}
```

**Example:**
```json
{
  "document_id": "doc_8_diary",
  "document_type": "diary",
  "fields": {
    "date": "2025-11-15",
    "author": "Dr. Sarah Chen",
    "content": "Tonight I can't shake the feeling that something is wrong. The lab was empty when I arrived at 22:30, which is unusual for a Thursday evening. The fluorescent lights hummed with their usual indifference, but the silence felt heavier than normal.\n\nI went straight to my workstation and began reviewing the day's data. Everything seemed normal at first, but then I noticed something odd in the file timestamps. Someone had accessed the secure server at 23:15 last night—long after everyone should have left.\n\nI found an encrypted file on the server that I don't recognize. The filename is innocuous enough, but the encryption method isn't standard. I'm going to need to investigate this further, but I can't shake the paranoia that someone is watching. I've locked my office door and I'm backing up everything to my personal drive before I leave tonight.",
    "mood": "anxious"
  }
}
```

#### 4. Witness Statement (`witness_statement`)

```typescript
interface WitnessStatementDocument {
  document_id: string
  document_type: "witness_statement"
  fields: {
    witness_name: string            // Witness name
    statement_date: string          // Statement date
    interviewer: string             // Interviewer name
    location: string                // Interview location
    statement: string               // Main statement text
    details?: Array<{               // Q&A format
      question: string
      answer: string | any[]        // Can be text or structured data
    }>
  }
}
```

### Law Enforcement

#### 5. Police Report (`police_report`)

```typescript
interface PoliceReportDocument {
  document_id: string
  document_type: "police_report"
  fields: {
    case_number: string             // Case identifier
    officer_name: string            // Reporting officer
    report_date: string             // Report date
    incident_date: string           // Incident date
    incident_location: string       // Incident location
    report: string                  // Report narrative
    evidence_noted: string[]        // Evidence list
    witnesses?: Array<{             // Witness info
      name: string
      statement: string
    }>
    status: string                  // Case status
  }
}
```

### Technical Logs

#### 6. Badge/Access Log (`badge_log`)

```typescript
interface BadgeLogDocument {
  document_id: string
  document_type: "badge_log"
  fields: {
    facility: string                // Facility name
    log_date: string                // Log date
    system_version?: string         // System version
    entries: Array<{                // 10-15 log entries
      timestamp: string             // ISO format with milliseconds
      badge_id: string              // Badge identifier
      user: string                  // Username
      location: string              // Location/door
      event: string                 // Event type
      status: string                // Result (GRANTED/DENIED)
    }>
  }
}
```

**Example:**
```json
{
  "document_id": "doc_3_badge",
  "document_type": "badge_log",
  "fields": {
    "facility": "Building 7, Floor 3",
    "log_date": "2025-11-15",
    "system_version": "v2.4.1",
    "entries": [
      {
        "timestamp": "2025-11-15T08:15:23.456Z",
        "badge_id": "BD-4532",
        "user": "J.Smith",
        "location": "Lab A - Door 3",
        "event": "BADGE_SCAN",
        "status": "GRANTED"
      },
      {
        "timestamp": "2025-11-15T08:17:45.789Z",
        "badge_id": "BD-7721",
        "user": "M.Chen",
        "location": "Server Room",
        "event": "BADGE_SCAN",
        "status": "DENIED"
      }
    ]
  }
}
```

#### 7. Login History (`login_history`)

```typescript
interface LoginHistoryDocument {
  document_id: string
  document_type: "login_history"
  fields: {
    system: string                  // System name
    log_period_start: string        // Period start
    log_period_end: string          // Period end
    authentication_events: Array<{  // 8-12 auth events
      timestamp: string
      user_id: string
      username: string
      ip_address: string
      device: string
      event: string                 // LOGIN/LOGOUT/FAILED
      status: string                // SUCCESS/FAILED
      notes?: string
    }>
  }
}
```

#### 8. Server Log (`server_log`)

```typescript
interface ServerLogDocument {
  document_id: string
  document_type: "server_log"
  fields: {
    server_name: string             // Server identifier
    log_date: string                // Log date
    log_level: string               // INFO/DEBUG/WARNING
    entries: Array<{                // 8-12 log entries
      timestamp: string             // ISO format with milliseconds
      level: string                 // INFO/DEBUG/WARNING/ERROR/CRITICAL
      service: string               // Service/process name
      message: string               // Log message
      details?: string              // Additional context
    }>
  }
}
```

**Example:**
```json
{
  "document_id": "doc_15_serverlog",
  "document_type": "server_log",
  "fields": {
    "server_name": "WEB-SERVER-03",
    "log_date": "2025-11-15",
    "log_level": "INFO",
    "entries": [
      {
        "timestamp": "2025-11-15T10:23:45.123Z",
        "level": "INFO",
        "service": "nginx",
        "message": "Server started successfully",
        "details": "port: 8080"
      },
      {
        "timestamp": "2025-11-15T10:25:12.456Z",
        "level": "WARNING",
        "service": "auth-service",
        "message": "Failed login attempt",
        "details": "user: admin, ip: 192.168.1.100"
      }
    ]
  }
}
```

### Network Logs

#### 9. Firewall Log (`firewall_log`)

```typescript
interface FirewallLogDocument {
  document_id: string
  document_type: "firewall_log"
  fields: {
    firewall_id: string             // Firewall device ID
    log_date: string                // Log date
    entries: Array<{                // 8-12 firewall events
      timestamp: string
      source_ip: string
      dest_ip: string
      source_port: string | number
      dest_port: string | number
      protocol: string              // TCP/UDP/ICMP/HTTPS
      action: string                // ALLOW/BLOCK/DROP
      rule: string                  // Rule ID
      bytes?: string | number       // Bytes transferred
    }>
  }
}
```

#### 10. Network Log (`network_log`)

```typescript
interface NetworkLogDocument {
  document_id: string
  document_type: "network_log"
  fields: {
    network_segment: string         // Network segment ID
    log_date: string                // Log date
    entries: Array<{                // 8-12 network events
      timestamp: string
      source: string                // Source device/IP
      destination: string           // Destination device/IP
      protocol: string              // HTTP/HTTPS/SSH/FTP
      bytes_sent: string | number
      bytes_received: string | number
      status: string                // ESTABLISHED/CLOSED/TIMEOUT
      connection_id: string         // Unique connection ID
    }>
  }
}
```

#### 11. VPN Log (`vpn_log`)

```typescript
interface VPNLogDocument {
  document_id: string
  document_type: "vpn_log"
  fields: {
    vpn_gateway: string             // VPN gateway ID
    log_date: string                // Log date
    entries: Array<{                // 8-12 VPN events
      timestamp: string
      user_id: string
      client_ip: string
      server_ip: string
      event: string                 // CONNECT/DISCONNECT/AUTH_SUCCESS/AUTH_FAILED
      protocol: string              // OpenVPN/IPSec/WireGuard
      encryption: string            // Encryption method
      bytes_transferred?: string | number
      duration?: string | number
    }>
  }
}
```

### Security & Access

#### 12. Access Control Log (`access_control`)

```typescript
interface AccessControlDocument {
  document_id: string
  document_type: "access_control"
  fields: {
    facility: string                // Facility name
    log_date: string                // Log date
    system_version: string          // System version
    entries: Array<{                // 8-12 access events
      timestamp: string
      event_type: string            // ACCESS_GRANTED/ACCESS_DENIED/BADGE_SCAN
      badge_id: string
      user: string
      clearance_level: string | number
      zone: string                  // Security zone
      door: string                  // Door identifier
      result: string                // GRANTED/DENIED/ERROR
      notes?: string
    }>
    system_events?: Array<{         // 3-5 system events
      timestamp: string
      event: string
    }>
  }
}
```

#### 13. Door Access Log (`door_access_log`)

```typescript
interface DoorAccessLogDocument {
  document_id: string
  document_type: "door_access_log"
  fields: {
    facility: string                // Facility name
    log_date: string                // Log date
    entries: Array<{                // 8-12 door events
      timestamp: string
      door_id: string
      badge_id: string
      user: string
      action: string                // OPENED/DENIED/FORCED
      duration_open?: string        // How long door was open
      sensor_status?: string        // Sensor status
    }>
  }
}
```

### IT & Assets

#### 14. IT Inventory (`it_inventory`)

```typescript
interface ITInventoryDocument {
  document_id: string
  document_type: "it_inventory"
  fields: {
    department: string              // Department name
    inventory_date: string          // Inventory date
    items: Array<{                  // 5-10 inventory items
      asset_id: string
      device_type: string           // Laptop/Desktop/Server/etc
      assigned_to: string
      location: string
      serial_number: string
      status: string                // ACTIVE/RETIRED/MISSING
      notes?: string
    }>
  }
}
```

#### 15. Device Registry (`device_registry`)

```typescript
interface DeviceRegistryDocument {
  document_id: string
  document_type: "device_registry"
  fields: {
    registry_date: string           // Registry date
    devices: Array<{                // 5-10 devices
      device_id: string
      device_name: string
      device_type: string           // Computer/Phone/IoT/etc
      mac_address: string
      ip_address: string
      owner: string
      location: string
      last_seen: string             // Last activity timestamp
      status: string                // ACTIVE/OFFLINE/UNKNOWN
    }>
  }
}
```

#### 16. Asset Database (`asset_database`)

```typescript
interface AssetDatabaseDocument {
  document_id: string
  document_type: "asset_database"
  fields: {
    database: string                // Database name
    query_date: string              // Query date
    records: Array<{                // 5-10 asset records
      asset_id: string
      asset_type: string            // Equipment/Software/License/etc
      owner: string
      location: string
      value?: string | number
      status: string                // ACTIVE/RETIRED/DISPOSED
      acquisition_date: string
      notes?: string
    }>
  }
}
```

### Security Analysis

#### 17. Security Scan (`security_scan`)

```typescript
interface SecurityScanDocument {
  document_id: string
  document_type: "security_scan"
  fields: {
    scan_id: string                 // Scan identifier
    scan_date: string               // Scan date
    scan_type: string               // VULNERABILITY/COMPLIANCE/PENETRATION
    results: Array<{                // 5-10 findings
      timestamp: string
      target: string                // Target system/IP
      finding: string               // Finding description
      severity: string              // LOW/MEDIUM/HIGH/CRITICAL
      description: string
    }>
  }
}
```

### Telecommunications

#### 18. Phone Record (`phone_record`)

```typescript
interface PhoneRecordDocument {
  document_id: string
  document_type: "phone_record"
  fields: {
    record_date: string             // Record date
    calls: Array<{                  // 8-12 call records
      timestamp: string
      caller: string                // Caller ID/number
      recipient: string             // Recipient ID/number
      duration: string | number     // Call duration (seconds)
      call_type: string             // INCOMING/OUTGOING/MISSED
      notes?: string
    }>
  }
}
```

### Parsing Examples

#### Type-Safe Document Parser

```typescript
function parseDocument(entity: Entity): BaseDocument {
  const doc = JSON.parse(entity.payload)
  
  // Type-specific parsing
  switch (doc.document_type) {
    case 'email':
      return {
        ...doc,
        fields: {
          ...doc.fields,
          date: doc.fields.date ? new Date(doc.fields.date) : undefined
        }
      } as EmailDocument
    
    case 'server_log':
    case 'firewall_log':
    case 'network_log':
      return {
        ...doc,
        fields: {
          ...doc.fields,
          entries: doc.fields.entries?.map((e: any) => ({
            ...e,
            timestamp: new Date(e.timestamp)
          })) || []
        }
      }
    
    case 'diary':
      return {
        ...doc,
        fields: {
          ...doc.fields,
          date: new Date(doc.fields.date)
        }
      } as DiaryDocument
    
    default:
      return doc
  }
}
```

#### Extract Key Information

```typescript
function extractKeyInfo(doc: BaseDocument) {
  switch (doc.document_type) {
    case 'email':
      return {
        type: 'Communication',
        from: doc.fields.from,
        to: Array.isArray(doc.fields.to) ? doc.fields.to.join(', ') : doc.fields.to,
        preview: doc.fields.subject || doc.fields.body?.substring(0, 100)
      }
    
    case 'badge_log':
    case 'login_history':
    case 'access_control':
      return {
        type: 'Access Log',
        facility: doc.fields.facility || doc.fields.system,
        entryCount: doc.fields.entries?.length || 0,
        date: doc.fields.log_date
      }
    
    case 'server_log':
    case 'network_log':
    case 'firewall_log':
      return {
        type: 'Technical Log',
        source: doc.fields.server_name || doc.fields.network_segment || doc.fields.firewall_id,
        entryCount: doc.fields.entries?.length || 0,
        date: doc.fields.log_date
      }
    
    case 'diary':
      return {
        type: 'Personal Document',
        author: doc.fields.author,
        date: doc.fields.date,
        preview: doc.fields.content?.substring(0, 100)
      }
    
    default:
      return {
        type: 'Document',
        content: JSON.stringify(doc.fields).substring(0, 100)
      }
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

