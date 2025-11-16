const hre = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("🚀 Deploying SimpleTest to Paseo...\n");
  
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer:", deployer.address);
  
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Balance:", hre.ethers.formatEther(balance), "KSM\n");
  
  const SimpleTest = await hre.ethers.getContractFactory("SimpleTest");
  const simple = await SimpleTest.deploy();
  await simple.waitForDeployment();
  
  const address = await simple.getAddress();
  console.log("✅ SimpleTest deployed to:", address);
  
  // Save address
  fs.writeFileSync("/tmp/simple_test_address.txt", address);
  
  // Test reading
  const counter = await simple.getCounter();
  console.log("✅ Initial counter:", counter.toString());
  console.log("\n📝 Address saved to /tmp/simple_test_address.txt");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

