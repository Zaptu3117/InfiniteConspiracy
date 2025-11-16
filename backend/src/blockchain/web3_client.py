"""AsyncWeb3 client for Kusama contract interaction."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware


logger = logging.getLogger(__name__)


class Web3Client:
    """
    Async wrapper for Web3.py to interact with InfiniteConspiracy contract.
    
    Uses AsyncWeb3 for proper async/await patterns.
    """
    
    def __init__(
        self,
        rpc_url: str,
        private_key: str,
        contract_address: str,
        contract_abi_path: Optional[str] = None
    ):
        """
        Initialize AsyncWeb3 client.
        
        Args:
            rpc_url: RPC endpoint (http)
            private_key: Private key for oracle account
            contract_address: Deployed contract address
            contract_abi_path: Path to contract ABI JSON
        """
        # Initialize AsyncWeb3 with HTTP provider
        self.w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        
        # Add PoA middleware for networks like Kusama/Polkadot EVM
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        # Set up account
        self.private_key = private_key if private_key.startswith('0x') else f'0x{private_key}'
        # Note: account signing is synchronous, only network calls are async
        self.account = self.w3.eth.account.from_key(self.private_key)
        self.address = self.account.address
        
        # Load contract
        self.contract_address = AsyncWeb3.to_checksum_address(contract_address)
        
        # Load ABI
        if contract_abi_path:
            abi_path = Path(contract_abi_path)
        else:
            # Default ABI path
            abi_path = Path(__file__).parent.parent.parent.parent / "contracts" / "artifacts" / "contracts" / "InfiniteConspiracy.sol" / "InfiniteConspiracy.json"
        
        if abi_path.exists():
            with open(abi_path, 'r') as f:
                contract_json = json.load(f)
                self.contract_abi = contract_json.get('abi', contract_json)
        else:
            # Minimal ABI for basic functions
            self.contract_abi = self._get_minimal_abi()
        
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
    
    def _get_minimal_abi(self):
        """Get minimal ABI if full ABI not available."""
        return [
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "mysteryId", "type": "bytes32"},
                    {"internalType": "bytes32", "name": "answerHash", "type": "bytes32"},
                    {"internalType": "bytes32", "name": "proofHash", "type": "bytes32"},
                    {"internalType": "uint256", "name": "duration", "type": "uint256"},
                    {"internalType": "uint8", "name": "difficulty", "type": "uint8"}
                ],
                "name": "createMystery",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "mysteryId", "type": "bytes32"},
                    {"internalType": "string", "name": "proof", "type": "string"}
                ],
                "name": "revealProof",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "mysteryId", "type": "bytes32"}
                ],
                "name": "getMystery",
                "outputs": [{
                    "components": [
                        {"internalType": "bytes32", "name": "mysteryId", "type": "bytes32"},
                        {"internalType": "bytes32", "name": "answerHash", "type": "bytes32"},
                        {"internalType": "bytes32", "name": "proofHash", "type": "bytes32"},
                        {"internalType": "uint256", "name": "bountyPool", "type": "uint256"},
                        {"internalType": "uint256", "name": "createdAt", "type": "uint256"},
                        {"internalType": "uint256", "name": "expiresAt", "type": "uint256"},
                        {"internalType": "uint8", "name": "difficulty", "type": "uint8"},
                        {"internalType": "bool", "name": "solved", "type": "bool"},
                        {"internalType": "address", "name": "solver", "type": "address"},
                        {"internalType": "bool", "name": "proofRevealed", "type": "bool"},
                        {"internalType": "string", "name": "proofData", "type": "string"}
                    ],
                    "internalType": "struct InfiniteConspiracy.Mystery",
                    "name": "",
                    "type": "tuple"
                }],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    async def is_connected(self) -> bool:
        """Check if connected to blockchain (async)."""
        return await self.w3.is_connected()
    
    async def get_balance(self, address: Optional[str] = None) -> int:
        """Get balance in wei (async)."""
        addr = address if address else self.address
        return await self.w3.eth.get_balance(AsyncWeb3.to_checksum_address(addr))
    
    def string_to_bytes32(self, text: str) -> bytes:
        """Convert string to bytes32 (via keccak256) - synchronous."""
        return AsyncWeb3.solidity_keccak(['string'], [text])
    
    async def send_transaction(
        self,
        function_call,
        value: int = 0,
        gas_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send a transaction to the contract (async).
        
        Args:
            function_call: Contract function call
            value: ETH/KSM value to send (in wei)
            gas_limit: Optional gas limit
        
        Returns:
            Transaction receipt
        """
        # Get nonce (async)
        nonce = await self.w3.eth.get_transaction_count(self.address, 'pending')
        
        # Get chain ID
        chain_id = await self.w3.eth.chain_id
        
        # Get gas price - check if EIP-1559 is supported
        latest_block = await self.w3.eth.get_block('latest')
        use_eip1559 = 'baseFeePerGas' in latest_block
        
        # Estimate gas if not provided
        if not gas_limit:
            try:
                estimated_gas = await function_call.estimate_gas({
                    'from': self.address,
                    'value': value
                })
                
                # Sanity check: if estimated gas is > 10M, it's likely garbage
                if estimated_gas > 10_000_000:
                    logger.warning(f"Unrealistic gas estimate: {estimated_gas}, using safe default")
                    gas_limit = 500_000  # Safe default for createMystery
                else:
                    gas_limit = int(estimated_gas * 1.5)  # Add 50% buffer
                    logger.info(f"Estimated gas: {estimated_gas}, using: {gas_limit}")
            except Exception as e:
                logger.warning(f"Gas estimation failed: {e}, using default")
                gas_limit = 500_000  # Safe default
        
        # Build transaction (EIP-1559 or legacy)
        tx_params = {
            'from': self.address,
            'nonce': nonce,
            'value': value,
            'gas': gas_limit,
            'chainId': chain_id
        }
        
        if use_eip1559:
            # EIP-1559 transaction
            base_fee = latest_block['baseFeePerGas']
            max_priority_fee = await self.w3.eth.max_priority_fee
            max_fee = base_fee * 2 + max_priority_fee  # 2x base fee + priority
            
            tx_params['maxFeePerGas'] = max_fee
            tx_params['maxPriorityFeePerGas'] = max_priority_fee
            logger.info(f"EIP-1559: maxFee={max_fee/10**9:.2f} Gwei, priority={max_priority_fee/10**9:.2f} Gwei")
        else:
            # Legacy transaction
            gas_price = await self.w3.eth.gas_price
            tx_params['gasPrice'] = max(gas_price, 1_000_000_000)  # At least 1 Gwei
            logger.info(f"Legacy: gasPrice={tx_params['gasPrice']/10**9:.2f} Gwei")
        
        tx = await function_call.build_transaction(tx_params)
        
        # Sign transaction (synchronous - cryptographic operation)
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        
        # Send transaction (async) - handle both old and new web3 versions
        raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx.rawTransaction
        tx_hash = await self.w3.eth.send_raw_transaction(raw_tx)
        
        logger.info(f"Transaction sent: {tx_hash.hex()}")
        
        # Wait for receipt (async)
        receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'tx_hash': tx_hash.hex(),
            'block_number': receipt['blockNumber'],
            'gas_used': receipt['gasUsed'],
            'status': receipt['status']
        }

