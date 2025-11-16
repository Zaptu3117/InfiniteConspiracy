/**
 * Register a mystery on InfiniteConspiracy contract
 * Works around Paseo testnet "Invalid Transaction" issue
 */
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  // Get mystery data from environment variable or command line
  let mysteryData;
  
  if (process.env.MYSTERY_DATA_FILE) {
    // Load from JSON file specified in env
    const filePath = process.env.MYSTERY_DATA_FILE;
    console.log(`📄 Loading mystery data from: ${filePath}\n`);
    const fileContent = fs.readFileSync(filePath, 'utf8');
    mysteryData = JSON.parse(fileContent);
  } else {
    // Parse from command line
    const args = process.argv.slice(2);
    
    if (args.length < 5) {
      console.log("Usage: npx hardhat run scripts/register_mystery.js --network paseo <mysteryId> <answerHash> <proofHash> <duration> <difficulty> [bountyKSM]");
      console.log("\nOr set MYSTERY_DATA_FILE environment variable to JSON file path");
      process.exit(1);
    }
    
    mysteryData = {
      mysteryId: args[0],
      answerHash: args[1],
      proofHash: args[2],
      duration: parseInt(args[3]),
      difficulty: parseInt(args[4]),
      bountyKSM: args[5] ? parseFloat(args[5]) : 10.0
    };
  }
  
  console.log("\n🔍 Registering Mystery on Blockchain...\n");
  
  // Get contract address from env or deployment.json
  let contractAddress;
  let networkName;
  
  if (process.env.CONTRACT_ADDRESS && process.env.NETWORK_NAME) {
    // Use env variables (from Python backend)
    contractAddress = process.env.CONTRACT_ADDRESS;
    networkName = process.env.NETWORK_NAME;
    console.log(`📋 Contract: ${contractAddress}`);
    console.log(`   Network: ${networkName}\n`);
  } else {
    // Fallback to deployment.json
    const deploymentPath = path.join(__dirname, "../deployment.json");
    if (!fs.existsSync(deploymentPath)) {
      console.error("❌ deployment.json not found and CONTRACT_ADDRESS not set!");
      process.exit(1);
    }
    
    const deployment = JSON.parse(fs.readFileSync(deploymentPath, 'utf8'));
    contractAddress = deployment.contract;
    networkName = deployment.network;
    console.log(`📋 Contract: ${contractAddress}`);
    console.log(`   Network: ${networkName}\n`);
  }
  
  // Get contract
  const InfiniteConspiracy = await hre.ethers.getContractFactory("InfiniteConspiracy");
  const contract = InfiniteConspiracy.attach(contractAddress);
  
  // Get signer info
  const [signer] = await hre.ethers.getSigners();
  const balance = await hre.ethers.provider.getBalance(signer.address);
  console.log(`🔑 Oracle: ${signer.address}`);
  console.log(`   Balance: ${hre.ethers.formatEther(balance)} KSM\n`);
  
  // Prepare parameters
  const mysteryIdBytes = hre.ethers.id(mysteryData.mysteryId); // keccak256 hash
  const answerHashBytes = mysteryData.answerHash.startsWith('0x') ? mysteryData.answerHash : '0x' + mysteryData.answerHash;
  const proofHashBytes = mysteryData.proofHash.startsWith('0x') ? mysteryData.proofHash : '0x' + mysteryData.proofHash;
  const bountyWei = hre.ethers.parseEther(mysteryData.bountyKSM.toString());
  
  console.log("📝 Mystery Parameters:");
  console.log(`   Mystery ID: ${mysteryData.mysteryId}`);
  console.log(`   ID (bytes32): ${mysteryIdBytes}`);
  console.log(`   Answer Hash: ${answerHashBytes}`);
  console.log(`   Proof Hash: ${proofHashBytes}`);
  console.log(`   Duration: ${mysteryData.duration} seconds`);
  console.log(`   Difficulty: ${mysteryData.difficulty}/10`);
  console.log(`   Bounty: ${mysteryData.bountyKSM} KSM\n`);
  
  // Check if mystery already exists
  try {
    const existing = await contract.getMystery(mysteryIdBytes);
    if (existing.mysteryId !== "0x0000000000000000000000000000000000000000000000000000000000000000") {
      console.log("⚠️  Mystery already exists on-chain!");
      console.log(`   Bounty: ${hre.ethers.formatEther(existing.bountyPool)} KSM`);
      console.log(`   Solved: ${existing.solved}`);
      process.exit(0);
    }
  } catch (e) {
    // Mystery doesn't exist, continue
  }
  
  console.log("⏳ Sending transaction...\n");
  
  // Send transaction
  try {
    const tx = await contract.createMystery(
      mysteryIdBytes,
      answerHashBytes,
      proofHashBytes,
      mysteryData.duration,
      mysteryData.difficulty,
      { 
        value: bountyWei,
        gasLimit: 300000,  // Conservative gas limit
        type: 0  // Force legacy transaction (Type 0)
      }
    );
    
    console.log(`📤 Transaction sent: ${tx.hash}`);
    console.log("⏳ Waiting for confirmation...\n");
    
    const receipt = await tx.wait();
    
    console.log("✅ Mystery Registered Successfully!\n");
    console.log(`   Tx Hash: ${receipt.hash}`);
    console.log(`   Block: ${receipt.blockNumber}`);
    console.log(`   Gas Used: ${receipt.gasUsed.toString()}`);
    console.log(`   Status: ${receipt.status === 1 ? 'Success' : 'Failed'}\n`);
    
    // Save registration info
    const registrationInfo = {
      mysteryId: mysteryData.mysteryId,
      mysteryIdBytes32: mysteryIdBytes,
      answerHash: answerHashBytes,
      proofHash: proofHashBytes,
      difficulty: mysteryData.difficulty,
      bountyKSM: mysteryData.bountyKSM,
      network: networkName,
      contract: contractAddress,
      txHash: receipt.hash,
      blockNumber: receipt.blockNumber,
      gasUsed: receipt.gasUsed.toString(),
      timestamp: new Date().toISOString()
    };
    
    const registrationsPath = path.join(__dirname, "../registrations.json");
    let registrations = [];
    if (fs.existsSync(registrationsPath)) {
      registrations = JSON.parse(fs.readFileSync(registrationsPath, 'utf8'));
    }
    registrations.push(registrationInfo);
    fs.writeFileSync(registrationsPath, JSON.stringify(registrations, null, 2));
    
    console.log("💾 Registration saved to registrations.json\n");
    
  } catch (error) {
    console.error("❌ Registration failed:");
    console.error(error.message);
    if (error.data) {
      console.error("Error data:", error.data);
    }
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

