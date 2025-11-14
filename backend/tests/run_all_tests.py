#!/usr/bin/env python3
"""Master test runner for all integration tests."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, setup_logger


async def run_test(test_name: str, test_func):
    """Run a single test and return result."""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print('='*60)
    try:
        result = await test_func()
        return result
    except Exception as e:
        print(f"❌ Test crashed: {e}")
        return False


async def main():
    """Run all tests."""
    config = load_config()
    logger = setup_logger("test_runner", "INFO", config.log_dir)
    
    print("🧪 InvestigationBackEnd - Full Test Suite")
    print("="*60)
    print("This will test all major components:")
    print("  1. LLM Clients (Cerebras, OpenAI)")
    print("  2. Arkiv SDK Integration")
    print("  3. Kusama Web3 Integration")
    print("  4. Replicate Image Generation")
    print("="*60)
    
    results = {}
    
    # Test 1: LLM Clients
    print("\n📍 Test Suite 1/4: LLM Clients")
    try:
        from test_llm_clients import test_cerebras, test_openai
        results['cerebras'] = await test_cerebras()
        results['openai'] = await test_openai()
    except Exception as e:
        print(f"❌ LLM tests failed to import: {e}")
        results['cerebras'] = False
        results['openai'] = False
    
    # Test 2: Arkiv
    print("\n📍 Test Suite 2/4: Arkiv SDK")
    try:
        from test_arkiv import test_arkiv_connection
        results['arkiv'] = test_arkiv_connection()
    except Exception as e:
        print(f"❌ Arkiv test failed to import: {e}")
        results['arkiv'] = False
    
    # Test 3: Web3
    print("\n📍 Test Suite 3/4: Kusama Web3")
    try:
        from test_web3 import test_kusama_connection
        results['web3'] = await test_kusama_connection()
    except Exception as e:
        print(f"❌ Web3 test failed to import: {e}")
        results['web3'] = False
    
    # Test 4: Replicate (optional - uses API credits)
    print("\n📍 Test Suite 4/4: Replicate Image Generation")
    print("⚠️  This test uses API credits. Skip? (y/N): ", end='')
    try:
        # In CI or non-interactive, skip
        skip = input().strip().lower() == 'y'
    except:
        skip = True
    
    if skip:
        print("⏭️  Skipped Replicate test")
        results['replicate'] = None
    else:
        try:
            from test_replicate import test_image_generation
            results['replicate'] = await test_image_generation()
        except Exception as e:
            print(f"❌ Replicate test failed to import: {e}")
            results['replicate'] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 FINAL TEST SUMMARY")
    print("="*60)
    
    def status(result):
        if result is None:
            return "⏭️  SKIPPED"
        return "✅ PASS" if result else "❌ FAIL"
    
    print(f"Cerebras LLM:     {status(results.get('cerebras'))}")
    print(f"OpenAI LLM:       {status(results.get('openai'))}")
    print(f"Arkiv SDK:        {status(results.get('arkiv'))}")
    print(f"Kusama Web3:      {status(results.get('web3'))}")
    print(f"Replicate Images: {status(results.get('replicate'))}")
    
    # Calculate pass rate
    total = len([r for r in results.values() if r is not None])
    passed = len([r for r in results.values() if r is True])
    
    print("="*60)
    if total > 0:
        print(f"✅ Passed: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total and total > 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

