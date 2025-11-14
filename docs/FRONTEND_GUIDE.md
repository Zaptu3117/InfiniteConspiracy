# Frontend Integration Guide

## Overview

The Infinite Conspiracy frontend is a **serverless** React application that:
- Queries Arkiv directly for documents
- Interacts with smart contract for submissions
- Reconstructs UI from JSON documents
- No traditional backend API

## Architecture

```
┌─────────────────────────────────────┐
│         React Frontend              │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ Arkiv Client │  │ Web3 Client │ │
│  └──────────────┘  └─────────────┘ │
└────────┬───────────────────┬────────┘
         │                   │
         ↓                   ↓
    ┌────────┐         ┌──────────┐
    │ Arkiv  │         │ Contract │
    └────────┘         └──────────┘
```

## Required Libraries

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "ethers": "^6.8.0",
    "@arkiv/client": "^0.1.19",
    "react-router-dom": "^6.18.0"
  }
}
```

## Setup

### 1. Arkiv Client

```typescript
// src/lib/arkiv.ts
import { createROClient } from '@arkiv/client';

export const arkivClient = await createROClient(
  60138453056,  // Chain ID
  "https://mendoza.hoodi.arkiv.network/rpc",
  "wss://mendoza.hoodi.arkiv.network/rpc/ws"
);
```

### 2. Web3 Client

```typescript
// src/lib/web3.ts
import { ethers } from 'ethers';

export const provider = new ethers.JsonRpcProvider(
  process.env.REACT_APP_RPC_URL
);

export const contract = new ethers.Contract(
  process.env.REACT_APP_CONTRACT_ADDRESS,
  CONTRACT_ABI,
  provider
);
```

## Data Fetching

### Get Active Mysteries

```typescript
// src/hooks/useActiveMysteries.ts
import { useEffect, useState } from 'react';
import { arkivClient } from '../lib/arkiv';

export function useActiveMysteries() {
  const [mysteries, setMysteries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMysteries() {
      try {
        // Query all mystery metadata
        const entities = await arkivClient.queryEntities(
          'document_type = "mystery_metadata"'
        );

        const parsed = entities.map(entity => {
          const data = JSON.parse(
            new TextDecoder().decode(entity.data)
          );
          return {
            ...data,
            entity_key: entity.entity_key
          };
        });

        setMysteries(parsed);
      } catch (error) {
        console.error('Failed to fetch mysteries:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchMysteries();
  }, []);

  return { mysteries, loading };
}
```

### Get Mystery Documents

```typescript
// src/hooks/useMysteryDocuments.ts
import { useEffect, useState } from 'react';
import { arkivClient } from '../lib/arkiv';

export function useMysteryDocuments(mysteryId: string) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDocuments() {
      try {
        const query = `mystery_id = "${mysteryId}" && document_type != "mystery_metadata" && document_type != "image"`;
        const entities = await arkivClient.queryEntities(query);

        const parsed = entities.map(entity => {
          return JSON.parse(new TextDecoder().decode(entity.data));
        });

        setDocuments(parsed);
      } catch (error) {
        console.error('Failed to fetch documents:', error);
      } finally {
        setLoading(false);
      }
    }

    if (mysteryId) {
      fetchDocuments();
    }
  }, [mysteryId]);

  return { documents, loading };
}
```

### Get Mystery Images

```typescript
// src/hooks/useMysteryImages.ts
import { useEffect, useState } from 'react';
import { arkivClient } from '../lib/arkiv';

export function useMysteryImages(mysteryId: string) {
  const [images, setImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchImages() {
      try {
        const query = `mystery_id = "${mysteryId}" && document_type = "image"`;
        const entities = await arkivClient.queryEntities(query);

        const imageUrls = entities.map(entity => {
          const blob = new Blob([entity.data], { type: 'image/png' });
          return URL.createObjectURL(blob);
        });

        setImages(imageUrls);
      } catch (error) {
        console.error('Failed to fetch images:', error);
      } finally {
        setLoading(false);
      }
    }

    if (mysteryId) {
      fetchImages();
    }

    // Cleanup
    return () => {
      images.forEach(url => URL.revokeObjectURL(url));
    };
  }, [mysteryId]);

  return { images, loading };
}
```

## Document Rendering

### Document Type Router

```typescript
// src/components/DocumentRenderer.tsx
import React from 'react';
import EmailDocument from './documents/EmailDocument';
import BadgeLogDocument from './documents/BadgeLogDocument';
import DiaryDocument from './documents/DiaryDocument';
// ... other document types

interface Props {
  document: any;
}

export default function DocumentRenderer({ document }: Props) {
  switch (document.document_type) {
    case 'email':
      return <EmailDocument data={document} />;
    case 'badge_log':
      return <BadgeLogDocument data={document} />;
    case 'diary':
      return <DiaryDocument data={document} />;
    case 'police_report':
      return <PoliceReportDocument data={document} />;
    default:
      return <GenericDocument data={document} />;
  }
}
```

### Email Document Component

```typescript
// src/components/documents/EmailDocument.tsx
import React from 'react';

interface Props {
  data: {
    document_id: string;
    fields: {
      from: string;
      to: string[];
      subject: string;
      body: string;
      timestamp: string;
      cc?: string[];
      attachments?: string[];
    };
    cipher_info?: {
      encrypted: boolean;
      cipher_type: string;
      hint: string;
    };
  };
}

export default function EmailDocument({ data }: Props) {
  const { fields, cipher_info } = data;

  return (
    <div className="email-document">
      <div className="email-header">
        <div className="email-row">
          <span className="label">From:</span>
          <span>{fields.from}</span>
        </div>
        <div className="email-row">
          <span className="label">To:</span>
          <span>{fields.to.join(', ')}</span>
        </div>
        {fields.cc && (
          <div className="email-row">
            <span className="label">CC:</span>
            <span>{fields.cc.join(', ')}</span>
          </div>
        )}
        <div className="email-row">
          <span className="label">Subject:</span>
          <span>{fields.subject}</span>
        </div>
        <div className="email-row">
          <span className="label">Date:</span>
          <span>{new Date(fields.timestamp).toLocaleString()}</span>
        </div>
      </div>

      <div className="email-body">
        {fields.body}
      </div>

      {cipher_info?.encrypted && (
        <div className="cipher-hint">
          🔒 This content is encrypted ({cipher_info.cipher_type})
          <br />
          💡 Hint: {cipher_info.hint}
        </div>
      )}

      {fields.attachments && fields.attachments.length > 0 && (
        <div className="attachments">
          <span className="label">Attachments:</span>
          {fields.attachments.map(att => (
            <span key={att} className="attachment">{att}</span>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Badge Log Document Component

```typescript
// src/components/documents/BadgeLogDocument.tsx
import React from 'react';

interface Props {
  data: {
    fields: {
      facility_name: string;
      log_period: string;
      entries: Array<{
        badge_number: string;
        name: string;
        entry_time: string;
        location: string;
      }>;
    };
  };
}

export default function BadgeLogDocument({ data }: Props) {
  const { fields } = data;

  return (
    <div className="badge-log-document">
      <h3>Badge Access Log</h3>
      <div className="log-info">
        <div>Facility: {fields.facility_name}</div>
        <div>Period: {fields.log_period}</div>
      </div>

      <table className="badge-log-table">
        <thead>
          <tr>
            <th>Badge #</th>
            <th>Name</th>
            <th>Time</th>
            <th>Location</th>
          </tr>
        </thead>
        <tbody>
          {fields.entries.map((entry, idx) => (
            <tr key={idx}>
              <td>{entry.badge_number}</td>
              <td>{entry.name}</td>
              <td>{new Date(entry.entry_time).toLocaleTimeString()}</td>
              <td>{entry.location}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## Smart Contract Integration

### Player Inscription

```typescript
// src/hooks/useInscription.ts
import { useState } from 'react';
import { ethers } from 'ethers';
import { contract } from '../lib/web3';

export function useInscription() {
  const [loading, setLoading] = useState(false);

  async function inscribe() {
    setLoading(true);
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const contractWithSigner = contract.connect(signer);

      const tx = await contractWithSigner.inscribePlayer({
        value: ethers.parseEther("10")
      });

      await tx.wait();
      return true;
    } catch (error) {
      console.error('Inscription failed:', error);
      return false;
    } finally {
      setLoading(false);
    }
  }

  return { inscribe, loading };
}
```

### Answer Submission

```typescript
// src/hooks/useAnswerSubmission.ts
import { useState } from 'react';
import { ethers } from 'ethers';
import { contract } from '../lib/web3';

export function useAnswerSubmission(mysteryId: string) {
  const [loading, setLoading] = useState(false);

  async function submitAnswer(answer: string) {
    setLoading(true);
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const contractWithSigner = contract.connect(signer);

      // Convert mystery ID to bytes32
      const mysteryIdBytes = ethers.keccak256(
        ethers.toUtf8Bytes(mysteryId)
      );

      // Get submission cost
      const cost = await contract.getSubmissionCost(
        await signer.getAddress(),
        mysteryIdBytes
      );

      // Submit
      const tx = await contractWithSigner.submitAnswer(
        mysteryIdBytes,
        answer,
        { value: cost }
      );

      const receipt = await tx.wait();

      // Check if solved (look for MysterySolved event)
      const solvedEvent = receipt.logs.find(
        log => log.topics[0] === ethers.id("MysterySolved(bytes32,address,uint256)")
      );

      return {
        success: true,
        solved: !!solvedEvent
      };
    } catch (error) {
      console.error('Submission failed:', error);
      return { success: false, solved: false };
    } finally {
      setLoading(false);
    }
  }

  return { submitAnswer, loading };
}
```

### Get Player Stats

```typescript
// src/hooks/usePlayerStats.ts
import { useEffect, useState } from 'react';
import { contract } from '../lib/web3';

export function usePlayerStats(address: string) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const playerStats = await contract.getPlayerStats(address);
        setStats({
          inscribed: playerStats.inscribed,
          mysteriesSolved: Number(playerStats.mysteriesSolved),
          totalBountyWon: playerStats.totalBountyWon,
          totalSubmissions: Number(playerStats.totalSubmissions),
          reputation: Number(playerStats.reputation)
        });
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    }

    if (address) {
      fetchStats();
    }
  }, [address]);

  return { stats, loading };
}
```

## Page Components

### Mystery List Page

```typescript
// src/pages/MysteryList.tsx
import React from 'react';
import { useActiveMysteries } from '../hooks/useActiveMysteries';
import { Link } from 'react-router-dom';

export default function MysteryList() {
  const { mysteries, loading } = useActiveMysteries();

  if (loading) return <div>Loading mysteries...</div>;

  return (
    <div className="mystery-list">
      <h1>Active Mysteries</h1>
      
      {mysteries.map(mystery => (
        <Link 
          key={mystery.mystery_id} 
          to={`/mystery/${mystery.mystery_id}`}
          className="mystery-card"
        >
          <h3>{mystery.question}</h3>
          <div className="mystery-meta">
            <span>Difficulty: {mystery.difficulty}/10</span>
            <span>{mystery.total_documents} documents</span>
            <span>{mystery.total_images} images</span>
          </div>
        </Link>
      ))}
    </div>
  );
}
```

### Mystery Detail Page

```typescript
// src/pages/MysteryDetail.tsx
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMysteryDocuments } from '../hooks/useMysteryDocuments';
import { useMysteryImages } from '../hooks/useMysteryImages';
import { useAnswerSubmission } from '../hooks/useAnswerSubmission';
import DocumentRenderer from '../components/DocumentRenderer';

export default function MysteryDetail() {
  const { mysteryId } = useParams();
  const { documents, loading: docsLoading } = useMysteryDocuments(mysteryId!);
  const { images, loading: imgsLoading } = useMysteryImages(mysteryId!);
  const { submitAnswer, loading: submitting } = useAnswerSubmission(mysteryId!);
  const [answer, setAnswer] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const result = await submitAnswer(answer);
    
    if (result.solved) {
      alert('🎉 Congratulations! You solved the mystery!');
    } else if (result.success) {
      alert('❌ Incorrect answer. Try again!');
      setAnswer('');
    }
  }

  if (docsLoading || imgsLoading) {
    return <div>Loading mystery data...</div>;
  }

  return (
    <div className="mystery-detail">
      <div className="documents-section">
        <h2>Documents ({documents.length})</h2>
        {documents.map(doc => (
          <DocumentRenderer key={doc.document_id} document={doc} />
        ))}
      </div>

      <div className="images-section">
        <h2>Evidence Photos ({images.length})</h2>
        <div className="image-grid">
          {images.map((url, idx) => (
            <img key={idx} src={url} alt={`Evidence ${idx + 1}`} />
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="answer-form">
        <h2>Submit Answer</h2>
        <input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Enter your answer..."
          disabled={submitting}
        />
        <button type="submit" disabled={submitting}>
          {submitting ? 'Submitting...' : 'Submit Answer'}
        </button>
      </form>
    </div>
  );
}
```

## Styling

### Basic CSS

```css
/* src/styles/documents.css */

.email-document {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: white;
}

.email-header {
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.email-row {
  display: flex;
  margin-bottom: 8px;
}

.label {
  font-weight: bold;
  min-width: 80px;
  color: #666;
}

.email-body {
  white-space: pre-wrap;
  font-family: monospace;
  background: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
}

.cipher-hint {
  margin-top: 15px;
  padding: 10px;
  background: #fff3cd;
  border-left: 4px solid #ffc107;
}

.badge-log-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.badge-log-table th,
.badge-log-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.badge-log-table th {
  background: #f5f5f5;
  font-weight: bold;
}
```

## Environment Variables

```env
# .env.local
REACT_APP_RPC_URL=wss://kusama-rpc.polkadot.io
REACT_APP_CONTRACT_ADDRESS=0x...
```

## Best Practices

### 1. Caching

```typescript
// Cache Arkiv queries
const cache = new Map();

async function fetchWithCache(query: string) {
  if (cache.has(query)) {
    return cache.get(query);
  }
  
  const result = await arkivClient.queryEntities(query);
  cache.set(query, result);
  return result;
}
```

### 2. Error Handling

```typescript
try {
  const entities = await arkivClient.queryEntities(query);
} catch (error) {
  if (error.message.includes('network')) {
    // Handle network error
  } else if (error.message.includes('timeout')) {
    // Handle timeout
  }
}
```

### 3. Loading States

```typescript
// Always show loading states
{loading && <Spinner />}
{error && <ErrorMessage error={error} />}
{data && <Content data={data} />}
```

---

**Next**: Build your frontend and start investigating mysteries!

