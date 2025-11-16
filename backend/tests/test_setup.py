#!/usr/bin/env python3
"""
Quick setup verification test.
Checks if all modules can be imported without errors.
"""

import sys
from pathlib import Path

# Add src to path (go up to backend, then into src)
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir / "src"))

print("🔍 Testing Infinite Conspiracy Backend Setup")
print("=" * 60)
print()

# Test imports
tests = []

try:
    from utils import load_config
    tests.append(("utils.config", True, ""))
except Exception as e:
    tests.append(("utils.config", False, str(e)))

try:
    from utils import setup_logger
    tests.append(("utils.logger", True, ""))
except Exception as e:
    tests.append(("utils.logger", False, str(e)))

try:
    from utils import CerebrasClient, OpenAIClient
    tests.append(("utils.llm_clients", True, ""))
except Exception as e:
    tests.append(("utils.llm_clients", False, str(e)))

try:
    from models import Mystery, MysteryMetadata, Document, ProofTree, ValidationResult
    tests.append(("models", True, ""))
except Exception as e:
    tests.append(("models", False, str(e)))

try:
    from arkiv_integration import ArkivClient, EntityBuilder, ArkivPusher
    tests.append(("arkiv_integration", True, ""))
except Exception as e:
    tests.append(("arkiv_integration", False, str(e)))

try:
    from blockchain import Web3Client, MysteryRegistrar, ProofManager
    tests.append(("blockchain", True, ""))
except Exception as e:
    tests.append(("blockchain", False, str(e)))

# Print results
print("Import Tests:")
print("-" * 60)

all_passed = True
for module, passed, error in tests:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}  {module}")
    if not passed:
        print(f"       Error: {error}")
        all_passed = False

print()
print("=" * 60)

# Test config loading
print("\nConfiguration Test:")
print("-" * 60)

try:
    config = load_config()
    print("✅ Config loaded successfully")
    print(f"   Project root: {config.project_root}")
    print(f"   Outputs dir: {config.outputs_dir}")
    print(f"   Log dir: {config.log_dir}")
    
    # Check directories exist
    if config.outputs_dir.exists():
        print(f"✅ Outputs directory exists")
    else:
        print(f"⚠️  Outputs directory created")
    
    if config.log_dir.exists():
        print(f"✅ Log directory exists")
    else:
        print(f"⚠️  Log directory created")
    
except Exception as e:
    print(f"❌ Config load failed: {e}")
    all_passed = False

print()
print("=" * 60)

# Final summary
print("\n📊 Summary:")
if all_passed:
    print("✅ All tests passed! Setup is correct.")
    print("\nNext steps:")
    print("  1. Copy backend/env.example to backend/.env")
    print("  2. Fill in API keys in .env file")
    print("  3. Run: python backend/scripts/generate_mystery.py")
    sys.exit(0)
else:
    print("❌ Some tests failed. Please check the errors above.")
    sys.exit(1)

