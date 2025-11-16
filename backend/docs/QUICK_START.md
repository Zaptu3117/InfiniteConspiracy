# Quick Start Guide

Get started with Infinite Conspiracy backend in 5 minutes.

## Prerequisites

✅ Python 3.11+ installed  
✅ Dependencies installed (`uv pip install -e .`)  
✅ `.env` file configured with API keys

If you haven't completed these steps, see [INSTALLATION.md](./INSTALLATION.md).

## Quick Test

Verify your setup:

```bash
cd backend
python tests/run_all_tests.py
```

You should see: `✅ ALL TESTS PASSED!`

## Generate Your First Mystery

### Demo Mode (No API Keys Required)

Generate a simple mystery without calling any APIs:

```bash
cd backend
python scripts/generate_mystery.py --mode demo --difficulty 3 --docs 10
```

**Output**:
```
🎲 Starting mystery generation...
   Difficulty: 3
   Target documents: 10

📋 Mystery ID: 2f5a8b3c-...
   Question: Who leaked the classified documents to the press?

📄 Generating documents...
   ✅ Generated 10 documents

🖼️  Generating images...
   ✅ Planned 1 images (generation skipped for demo)

🔐 Generating hashes...
   Answer Hash: 0xabc123...
   Proof Hash: 0xdef456...

✅ Mystery generation complete!
Mystery ID: 2f5a8b3c-...
Question: Who leaked the classified documents to the press?
Answer: Sarah Martinez
Documents: 10
Output: outputs/mysteries/mystery_2f5a8b3c-.../

Next steps:
  1. python scripts/push_to_arkiv.py mystery_2f5a8b3c-...
  2. python scripts/register_on_chain.py mystery_2f5a8b3c-...
```

### Inspect the Mystery

```bash
cd outputs/mysteries/mystery_<id>/

# View mystery metadata
cat mystery.json | jq '.metadata'

# View documents
ls documents/
cat documents/doc_1_email.json | jq .

# View proof tree
cat mystery.json | jq '.proof_tree'
```

## Generate with LLM (Requires API Keys)

Generate a complete mystery using AI:

```bash
python scripts/generate_mystery.py --mode llm --difficulty 7 --docs 20
```

**This will**:
1. Generate premise with LLM (question + answer)
2. Create proof tree (reasoning steps)
3. Generate characters, timeline, locations
4. Plan 20 documents
5. Generate document content (parallel)
6. Apply cryptography (optional)
7. Add red herrings (optional)
8. Generate images (optional)
9. Validate mystery

**Time**: ~2-5 minutes  
**Cost**: ~$1-2 in API usage

## Deploy to Arkiv

Push your mystery to decentralized storage:

```bash
python scripts/push_to_arkiv.py <mystery_id>
```

**Example**:
```bash
python scripts/push_to_arkiv.py mystery_2f5a8b3c-4d9e-4a1b-8c7d-9e8f7a6b5c4d
```

**Output**:
```
📤 Pushing mystery to Arkiv...

Mystery ID: 2f5a8b3c-...
Documents: 10
Images: 1

Creating entities...
  Batch 1: 5 entities ✅
  Batch 2: 5 entities ✅
  Batch 3: 2 entities ✅

✅ Push complete!
Total entities: 12
  - 1 metadata
  - 10 documents
  - 1 image

Query on Arkiv:
  mystery_id = "2f5a8b3c-..."
```

## Register on Blockchain

Register your mystery on the smart contract:

```bash
python scripts/register_on_chain.py <mystery_id>
```

**Example**:
```bash
python scripts/register_on_chain.py mystery_2f5a8b3c-4d9e-4a1b-8c7d-9e8f7a6b5c4d
```

**Output**:
```
🔗 Registering mystery on Kusama...

Mystery ID: 2f5a8b3c-...
Answer Hash: 0xabc123...
Proof Hash: 0xdef456...
Difficulty: 7
Duration: 7 days

Calling createMystery()...
Transaction: 0x789abc...
Waiting for confirmation...

✅ Mystery registered!
Block: 1234567
Gas used: 150000

Contract address: 0xcontract...
Mystery on-chain ID: 0x2f5a8b3c...
```

## Verify Deployment

Check that your mystery is accessible:

```bash
# Test query on Arkiv
python scripts/test_query.py <mystery_id>

# Check on-chain status
python scripts/check_mystery.py <mystery_id>
```

## Common Tasks

### Generate Multiple Mysteries

```bash
# Generate 5 mysteries with different difficulties
for diff in 3 5 7 9 10; do
  python scripts/generate_mystery.py --mode demo --difficulty $diff
done
```

### Generate Conspiracy Mystery

```bash
# Generate a conspiracy-themed mystery
python scripts/generate_conspiracy.py --difficulty 8 --docs 25 --type occult
```

### Generate with Images

```bash
# Generate mystery with images (requires Replicate API)
python scripts/generate_mystery.py --mode llm --difficulty 7 --with-images
```

### Validate Existing Mystery

```bash
# Validate a previously generated mystery
python scripts/validate_mystery.py <mystery_id>
```

**Output**:
```
🔍 Validating mystery...

Mystery ID: 2f5a8b3c-...

Test 1: Single-LLM (should fail)
  ✅ Single LLM could not solve (as expected)

Test 2: Multi-hop (should succeed)
  Step 1: ✅ Extracted meeting time
  Step 2: ✅ Identified person at location
  Step 3: ✅ Connected timeline
  Step 4: ✅ Reached correct answer

✅ Mystery validated successfully!
```

## Quick Reference

### Generation Modes

| Mode | Description | API Keys Required |
|------|-------------|-------------------|
| `demo` | Simple hardcoded mystery | ❌ None |
| `llm` | Full AI-generated mystery | ✅ Cerebras, OpenAI |

### Common Flags

```bash
--mode {demo,llm}      # Generation mode
--difficulty {1-10}    # Mystery difficulty
--docs N               # Number of documents
--with-images          # Generate images (LLM mode only)
--no-crypto            # Skip cryptography
--no-herrings          # Skip red herrings
```

### File Locations

```
backend/
├── outputs/
│   ├── mysteries/           # Generated mysteries
│   │   └── mystery_<id>/
│   │       ├── mystery.json
│   │       ├── documents/
│   │       └── images/
│   └── logs/               # Generation logs
├── scripts/                # Helper scripts
└── config/                # Configuration files
```

## Next Steps

Now that you've generated your first mystery:

1. **Understand the generation process**: Read [MYSTERY_GENERATION.md](./MYSTERY_GENERATION.md)
2. **Learn about document types**: Read [DOCUMENT_GENERATION.md](./DOCUMENT_GENERATION.md)
3. **Explore cryptography**: Read [CRYPTOGRAPHY.md](./CRYPTOGRAPHY.md)
4. **Set up validation**: Read [VALIDATION.md](./VALIDATION.md)
5. **Deploy contracts**: See contracts documentation

## Troubleshooting

### Issue: `Config validation failed`

**Solution**: Check that `.env` file exists and has all required keys

```bash
cp env.example .env
# Edit .env with your keys
```

### Issue: `Mystery generation failed`

**Solution**: Check logs for details

```bash
tail -f outputs/logs/generation_*.log
```

### Issue: `Arkiv push failed`

**Solution**: Verify Arkiv private key and RPC URL

```bash
# Test connection
python -c "from arkiv_sdk import create_client; import asyncio; asyncio.run(create_client(...))"
```

### Issue: `Blockchain registration failed`

**Solution**: Check that contract is deployed and you have testnet tokens

```bash
# Check balance
python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('YOUR_RPC')); print(w3.eth.get_balance('YOUR_ADDRESS'))"
```

## Examples

### Example 1: Simple Demo Mystery

```bash
cd backend
python scripts/generate_mystery.py --mode demo --difficulty 3 --docs 5
```

**Use case**: Testing, development, demos without API calls

### Example 2: Full LLM Mystery

```bash
python scripts/generate_mystery.py --mode llm --difficulty 7 --docs 20
```

**Use case**: Production-quality mysteries for deployment

### Example 3: Conspiracy with Images

```bash
python scripts/generate_conspiracy.py \
  --difficulty 9 \
  --docs 30 \
  --type secret_society \
  --with-images
```

**Use case**: Advanced conspiracy mysteries with visual clues

### Example 4: Complete Deployment Pipeline

```bash
# 1. Generate
MYSTERY_ID=$(python scripts/generate_mystery.py --mode llm --difficulty 7 | grep "Mystery ID:" | cut -d' ' -f3)

# 2. Deploy to Arkiv
python scripts/push_to_arkiv.py $MYSTERY_ID

# 3. Register on blockchain
python scripts/register_on_chain.py $MYSTERY_ID

# 4. Verify
python scripts/validate_mystery.py $MYSTERY_ID

echo "✅ Mystery $MYSTERY_ID is live!"
```

## Getting Help

- **Documentation**: See other guides in `backend/docs/`
- **Examples**: Check `backend/tests/` for test scripts
- **Issues**: Open an issue on GitHub
- **Logs**: Check `outputs/logs/` for detailed error messages

