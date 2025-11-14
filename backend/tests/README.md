# Test Suite

Integration tests for InvestigationBackEnd components.

## Test Files

### Individual Component Tests

1. **`test_llm_clients.py`** - LLM API connectivity
   - Cerebras client
   - OpenAI client
   - Text and JSON generation

2. **`test_arkiv.py`** - Arkiv SDK integration
   - Connection to Mendoza testnet
   - Entity creation
   - Entity retrieval
   - Query functionality

3. **`test_web3.py`** - Kusama Web3 integration
   - Connection to Paseo testnet
   - Account balance check
   - AsyncWeb3 functionality

4. **`test_replicate.py`** - Image generation
   - Replicate API connectivity
   - Flux Schnell model
   - Image download and storage

### Master Test Runner

**`run_all_tests.py`** - Runs all tests in sequence with summary

## Running Tests

### Prerequisites

```bash
# Install dependencies
uv pip install -e .

# Set up environment variables
cp ../env.example ../.env
# Edit .env with your API keys
```

### Run Individual Tests

```bash
# Test LLM clients
python tests/test_llm_clients.py

# Test Arkiv SDK
python tests/test_arkiv.py

# Test Kusama Web3
python tests/test_web3.py

# Test Replicate (uses API credits!)
python tests/test_replicate.py
```

### Run All Tests

```bash
python tests/run_all_tests.py
```

## Required Environment Variables

### For LLM Tests
- `CEREBRAS_API_KEY` - Cerebras API key
- `OPENAI_API_KEY` - OpenAI API key

### For Arkiv Tests
- `ARKIV_RPC_URL` - Arkiv Mendoza RPC endpoint
- `ARKIV_PRIVATE_KEY` - Test account private key

### For Web3 Tests
- `KUSAMA_RPC_URL` - Kusama Paseo testnet RPC
- `ORACLE_PRIVATE_KEY` - Test account private key
- `CONTRACT_ADDRESS` - (optional) Deployed contract address

### For Replicate Tests
- `REPLICATE_API_TOKEN` - Replicate API token

## Getting Test Tokens

### Arkiv Mendoza Testnet
Visit Arkiv faucet and request test tokens for your `ARKIV_PRIVATE_KEY` address.

### Kusama Paseo Testnet
1. Visit: https://faucet.polkadot.io
2. Select "Paseo" network
3. Enter your address (derived from `ORACLE_PRIVATE_KEY`)
4. Request PAS tokens

## Expected Results

All tests should pass if:
- ✅ All API keys are valid
- ✅ Network connections are stable
- ✅ Test accounts have sufficient balance

## Troubleshooting

### "Connection refused"
- Check RPC URLs in `.env`
- Verify network is accessible

### "Insufficient funds"
- Request testnet tokens from faucets

### "Invalid API key"
- Verify keys in `.env` are correct
- Check key has not expired

### "Import errors"
- Ensure you're in the backend directory
- Check dependencies are installed: `uv pip install -e .`

## CI/CD Integration

To run tests in CI without interactive prompts:

```bash
# Skip Replicate test automatically
echo "y" | python tests/run_all_tests.py
```

## Notes

- Tests create temporary data in `outputs/test_*/`
- Arkiv entities have 120 block TTL (test only)
- Replicate tests consume API credits (skip if needed)
- All tests are independent and can run in any order

