const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("InfiniteConspiracy", function () {
  let contract;
  let owner, oracle, player1, player2;
  
  const INSCRIPTION_FEE = ethers.parseEther("10");
  const BASE_SUBMISSION_FEE = ethers.parseEther("1");

  beforeEach(async function () {
    [owner, oracle, player1, player2] = await ethers.getSigners();
    
    const InfiniteConspiracy = await ethers.getContractFactory("InfiniteConspiracy");
    contract = await InfiniteConspiracy.deploy(oracle.address);
    await contract.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set the correct oracle role", async function () {
      const ORACLE_ROLE = await contract.ORACLE_ROLE();
      expect(await contract.hasRole(ORACLE_ROLE, oracle.address)).to.be.true;
    });

    it("Should set correct fees", async function () {
      expect(await contract.INSCRIPTION_FEE()).to.equal(INSCRIPTION_FEE);
      expect(await contract.BASE_SUBMISSION_FEE()).to.equal(BASE_SUBMISSION_FEE);
    });
  });

  describe("Player Inscription", function () {
    it("Should allow player inscription with correct fee", async function () {
      await expect(
        contract.connect(player1).inscribePlayer({ value: INSCRIPTION_FEE })
      ).to.emit(contract, "PlayerInscribed");

      const stats = await contract.getPlayerStats(player1.address);
      expect(stats.inscribed).to.be.true;
      expect(stats.mysteriesSolved).to.equal(0);
    });

    it("Should reject inscription with insufficient fee", async function () {
      await expect(
        contract.connect(player1).inscribePlayer({ value: ethers.parseEther("5") })
      ).to.be.revertedWith("Insufficient fee");
    });

    it("Should reject double inscription", async function () {
      await contract.connect(player1).inscribePlayer({ value: INSCRIPTION_FEE });
      
      await expect(
        contract.connect(player1).inscribePlayer({ value: INSCRIPTION_FEE })
      ).to.be.revertedWith("Already inscribed");
    });

    it("Should split inscription fee correctly", async function () {
      const initialBalance = await ethers.provider.getBalance(contract.target);
      
      await contract.connect(player1).inscribePlayer({ value: INSCRIPTION_FEE });
      
      const treasuryBalance = await contract.treasuryBalance();
      expect(treasuryBalance).to.equal(INSCRIPTION_FEE / 2n);
    });
  });

  describe("Mystery Creation", function () {
    const mysteryId = ethers.keccak256(ethers.toUtf8Bytes("mystery_001"));
    const answerHash = ethers.keccak256(ethers.toUtf8Bytes("sarah martinez"));
    const proofHash = ethers.keccak256(ethers.toUtf8Bytes("{}"));
    const duration = 604800; // 7 days
    const difficulty = 7;
    const initialBounty = ethers.parseEther("10");

    it("Should allow oracle to create mystery", async function () {
      await expect(
        contract.connect(oracle).createMystery(
          mysteryId,
          answerHash,
          proofHash,
          duration,
          difficulty,
          { value: initialBounty }
        )
      ).to.emit(contract, "MysteryCreated")
        .withArgs(mysteryId, initialBounty);

      const mystery = await contract.getMystery(mysteryId);
      expect(mystery.mysteryId).to.equal(mysteryId);
      expect(mystery.answerHash).to.equal(answerHash);
      expect(mystery.bountyPool).to.equal(initialBounty);
      expect(mystery.difficulty).to.equal(difficulty);
      expect(mystery.solved).to.be.false;
    });

    it("Should reject non-oracle mystery creation", async function () {
      await expect(
        contract.connect(player1).createMystery(
          mysteryId,
          answerHash,
          proofHash,
          duration,
          difficulty,
          { value: initialBounty }
        )
      ).to.be.reverted;
    });

    it("Should reject duplicate mystery ID", async function () {
      await contract.connect(oracle).createMystery(
        mysteryId,
        answerHash,
        proofHash,
        duration,
        difficulty,
        { value: initialBounty }
      );

      await expect(
        contract.connect(oracle).createMystery(
          mysteryId,
          answerHash,
          proofHash,
          duration,
          difficulty,
          { value: initialBounty }
        )
      ).to.be.revertedWith("Exists");
    });
  });

  describe("Answer Submission", function () {
    const mysteryId = ethers.keccak256(ethers.toUtf8Bytes("mystery_001"));
    const answer = "Sarah Martinez";
    const answerHash = ethers.keccak256(ethers.toUtf8Bytes(answer.toLowerCase()));
    const proofHash = ethers.keccak256(ethers.toUtf8Bytes("{}"));
    const duration = 604800;
    const difficulty = 7;
    const initialBounty = ethers.parseEther("10");

    beforeEach(async function () {
      // Create mystery
      await contract.connect(oracle).createMystery(
        mysteryId,
        answerHash,
        proofHash,
        duration,
        difficulty,
        { value: initialBounty }
      );

      // Inscribe players
      await contract.connect(player1).inscribePlayer({ value: INSCRIPTION_FEE });
      await contract.connect(player2).inscribePlayer({ value: INSCRIPTION_FEE });
    });

    it("Should allow inscribed player to submit answer", async function () {
      const cost = await contract.getSubmissionCost(player1.address, mysteryId);
      
      await expect(
        contract.connect(player1).submitAnswer(mysteryId, "Wrong Answer", { value: cost })
      ).to.emit(contract, "AnswerSubmitted");
    });

    it("Should solve mystery with correct answer", async function () {
      const cost = await contract.getSubmissionCost(player1.address, mysteryId);
      
      await expect(
        contract.connect(player1).submitAnswer(mysteryId, answer, { value: cost })
      ).to.emit(contract, "MysterySolved")
        .withArgs(mysteryId, player1.address, await contract.getMystery(mysteryId).then(m => m.bountyPool));

      const mystery = await contract.getMystery(mysteryId);
      expect(mystery.solved).to.be.true;
      expect(mystery.solver).to.equal(player1.address);
    });

    it("Should increase cost quadratically", async function () {
      const cost1 = await contract.getSubmissionCost(player1.address, mysteryId);
      expect(cost1).to.equal(BASE_SUBMISSION_FEE); // 1 KSM

      // First submission
      await contract.connect(player1).submitAnswer(mysteryId, "Wrong 1", { value: cost1 });

      const cost2 = await contract.getSubmissionCost(player1.address, mysteryId);
      expect(cost2).to.equal(BASE_SUBMISSION_FEE + ethers.parseEther("1")); // 1 + 1² = 2 KSM

      // Second submission
      await contract.connect(player1).submitAnswer(mysteryId, "Wrong 2", { value: cost2 });

      const cost3 = await contract.getSubmissionCost(player1.address, mysteryId);
      expect(cost3).to.equal(BASE_SUBMISSION_FEE + ethers.parseEther("4")); // 1 + 2² = 5 KSM
    });

    it("Should add submission fees to bounty pool", async function () {
      const initialPool = (await contract.getMystery(mysteryId)).bountyPool;
      const cost = await contract.getSubmissionCost(player1.address, mysteryId);
      
      await contract.connect(player1).submitAnswer(mysteryId, "Wrong", { value: cost });
      
      const newPool = (await contract.getMystery(mysteryId)).bountyPool;
      expect(newPool).to.equal(initialPool + cost);
    });

    it("Should reject submission from non-inscribed player", async function () {
      const [, , , nonInscribed] = await ethers.getSigners();
      
      await expect(
        contract.connect(nonInscribed).submitAnswer(
          mysteryId,
          answer,
          { value: BASE_SUBMISSION_FEE }
        )
      ).to.be.revertedWith("Not inscribed");
    });

    it("Should update player stats on solve", async function () {
      const cost = await contract.getSubmissionCost(player1.address, mysteryId);
      const bountyPool = (await contract.getMystery(mysteryId)).bountyPool;
      
      await contract.connect(player1).submitAnswer(mysteryId, answer, { value: cost });
      
      const stats = await contract.getPlayerStats(player1.address);
      expect(stats.mysteriesSolved).to.equal(1);
      expect(stats.totalBountyWon).to.equal(bountyPool + cost);
      expect(stats.reputation).to.equal(100 * difficulty);
    });
  });

  describe("Leaderboard", function () {
    it("Should return top players", async function () {
      await contract.connect(player1).inscribePlayer({ value: INSCRIPTION_FEE });
      await contract.connect(player2).inscribePlayer({ value: INSCRIPTION_FEE });
      
      const [players, reps, solves] = await contract.getLeaderboard(10);
      expect(players.length).to.equal(2);
    });
  });

  describe("Active Mysteries", function () {
    it("Should track active mysteries", async function () {
      const mysteryId1 = ethers.keccak256(ethers.toUtf8Bytes("mystery_001"));
      const mysteryId2 = ethers.keccak256(ethers.toUtf8Bytes("mystery_002"));
      const answerHash = ethers.keccak256(ethers.toUtf8Bytes("answer"));
      const proofHash = ethers.keccak256(ethers.toUtf8Bytes("{}"));
      
      await contract.connect(oracle).createMystery(
        mysteryId1, answerHash, proofHash, 604800, 5, { value: ethers.parseEther("10") }
      );
      await contract.connect(oracle).createMystery(
        mysteryId2, answerHash, proofHash, 604800, 6, { value: ethers.parseEther("10") }
      );
      
      const active = await contract.getActiveMysteries();
      expect(active.length).to.equal(2);
    });
  });
});

