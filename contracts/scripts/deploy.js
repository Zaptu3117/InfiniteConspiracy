const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Deploying InfiniteConspiracy contract...\n");

  const [deployer, oracle] = await hre.ethers.getSigners();

  console.log("📋 Deployment Details:");
  console.log("  Network:", hre.network.name);
  console.log("  Deployer:", deployer.address);
  console.log("  Oracle:", oracle?.address || deployer.address);
  console.log("");

  // Get deployer balance
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("  Deployer Balance:", hre.ethers.formatEther(balance), "KSM\n");

  // Deploy contract
  console.log("⏳ Deploying contract...");
  const InfiniteConspiracy = await hre.ethers.getContractFactory("InfiniteConspiracy");
  
  const oracleAddress = oracle?.address || deployer.address;
  const contract = await InfiniteConspiracy.deploy(oracleAddress);
  
  await contract.waitForDeployment();
  const contractAddress = await contract.getAddress();

  console.log("✅ Contract deployed to:", contractAddress);
  console.log("");

  // Save deployment info
  const deploymentInfo = {
    network: hre.network.name,
    contract: contractAddress,
    deployer: deployer.address,
    oracle: oracleAddress,
    deployedAt: new Date().toISOString(),
    blockNumber: await hre.ethers.provider.getBlockNumber()
  };

  const deploymentPath = path.join(__dirname, "..", "deployment.json");
  fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));

  console.log("💾 Deployment info saved to deployment.json");
  console.log("");
  console.log("📝 Contract Details:");
  console.log("  INSCRIPTION_FEE:", hre.ethers.formatEther(await contract.INSCRIPTION_FEE()), "KSM");
  console.log("  BASE_SUBMISSION_FEE:", hre.ethers.formatEther(await contract.BASE_SUBMISSION_FEE()), "KSM");
  console.log("");

  // Grant oracle role if different from deployer
  if (oracle && oracle.address !== deployer.address) {
    console.log("🔑 Granting ORACLE_ROLE to", oracle.address);
    const ORACLE_ROLE = await contract.ORACLE_ROLE();
    await contract.grantRole(ORACLE_ROLE, oracle.address);
    console.log("✅ Oracle role granted");
    console.log("");
  }

  console.log("🎉 Deployment complete!");
  console.log("");
  console.log("Next steps:");
  console.log("  1. Update backend/.env with CONTRACT_ADDRESS=" + contractAddress);
  console.log("  2. Generate mystery: cd backend && python scripts/generate_mystery.py");
  console.log("  3. Push to Arkiv: python scripts/push_to_arkiv.py <mystery_id>");
  console.log("  4. Register on-chain: python scripts/register_on_chain.py <mystery_id>");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

