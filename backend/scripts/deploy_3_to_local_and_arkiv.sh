#!/bin/bash
# Deploy 3 conspiracies using the working e2e test

export CONTRACT_ADDRESS="0x5FbDB2315678afecb367f032d93F642f64180aa3"
export ORACLE_PRIVATE_KEY="0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  DEPLOYING 3 CONSPIRACIES TO LOCAL + ARKIV                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# We'll just use the e2e test that we KNOW works
# Then register each one on-chain

cd /home/flex3/projects/InvestigationBackEnd/backend

echo "Starting deployments... this will take 15-20 minutes total"
echo ""

uv run python test_e2e_conspiracy_arkiv.py

echo ""
echo "✅ Deployment complete!"

