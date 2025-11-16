## MILESTONE 2 PLAN: Infinity Conspiracy Network

**Team:** Felix Zapata & Clémence Plenet

**Track:** [X] SHIP-A-TON [ ] IDEA-TON  

**Date:** November 16, 2025

---

## 📍 WHERE WE ARE NOW

**What we built/validated this weekend:**

- Core gameplay loop: investigation generation pipeline with LLM-powered narrative engine that creates coherent mysteries with causal evidence chains

- Blockchain integration: Smart contracts deployed on Kusama handling registration, answer submissions with quadratic pricing, and prize pool distribution

- Archive storage integration: Time-locked document storage on Layer 3, enabling public data that disappears post-investigation

- First fully playable investigation: Multiple document types (emails, bank statements, server logs) with solvable clue chains

- Frontend prototype: Document viewer with conspiracy board aesthetics and wallet connection

**What's working:**

- Narrative engine generates coherent investigations with hidden clues in plain text documents

- Smart contract successfully handles registration fees and answer validation

- Archive storage properly stores and retrieves investigation documents

- Quadratic pricing mechanism discourages brute-force attempts

- Causal evidence chain logic creates engaging detective gameplay

**What still needs work:**

- Answer validation currently requires manual verification - needs automation

- Frontend is desktop-only, not mobile-responsive

- No player annotation/note-taking system for evidence tracking

- Smart contracts need security audit before production

- Leaderboard system is basic, needs enhancement for competitive dynamics

- No analytics to understand player behavior and drop-off points

**Blockers or hurdles we hit:**

- Archive time-locking constraints required complete redesign of data availability strategy (turned into feature: "finding needles in public haystacks")

- Answer validation complexity - balancing automated checking with narrative flexibility

- Document generation costs (~$3 per investigation) need optimization for scale

- Gas cost optimization for frequent answer submissions

---

## 🚀 WHAT WE'LL SHIP IN 30 DAYS

**Our MVP will do this:**

A production-ready investigation game where players register for weekly mysteries, analyze procedurally generated evidence documents, submit answers through blockchain transactions, and compete for prize pools - with a polished mobile-friendly interface, automated answer validation, and community infrastructure to onboard our first 100 beta testers.

### Features We'll Build (5 max)

**Week 1-2:**

- **Feature:** Smart contract security audit & answer validation automation
- **Why it matters:** Cannot launch with real money without audited contracts. Automated validation eliminates manual work and enables instant winner determination, creating the competitive rush that drives engagement.
- **Who builds it:** Felix (smart contracts) + External auditor consultation

- **Feature:** Mobile-responsive frontend with local board saving
- **Why it matters:** 70% of gaming traffic is mobile. Players need to save annotations/connections between evidence pieces to solve complex mysteries. This is core to the investigation experience.
- **Who builds it:** Clémence (frontend) 

**Week 2-3:**

- **Feature:** Enhanced leaderboard & rewards system
- **Why it matters:** Competitive dynamics drive retention. Need real-time leaderboard updates, player statistics, historical performance tracking to create status incentives beyond monetary rewards.
- **Who builds it:** Felix (smart contracts + backend)

- **Feature:** PostHog analytics integration & player behavior tracking
- **Why it matters:** Need data on where players drop off, which documents they read, average solve times to iterate on difficulty and narrative generation. Essential for product-market fit.
- **Who builds it:** Clémence (frontend integration)

**Week 3-4:**

- **Feature:** Discord community launch + beta tester onboarding program
- **Why it matters:** Community is our moat. Early adopters provide feedback, create viral loops, and validate our "investigation as social experience" thesis. Discord becomes the place where players discuss strategies (without spoiling answers).
- **Who builds it:** Both (Felix: bot integration & wallet verification, Clémence: community management & content)

### Team Breakdown

**Felix Zapata - Technical Lead & Smart Contracts** | 30 hrs/week

- Owns: Smart contract audit coordination, answer validation automation, backend optimizations, leaderboard system, Discord wallet verification bot

**Clémence Plenet - Frontend & Product** | 30 hrs/week

- Owns: Mobile-responsive UI, local board saving system, PostHog integration, UX testing, Discord community management, beta tester onboarding

### Mentoring & Expertise We Need

**Areas where we need support:**

- Smart contract security best practices & audit recommendations (Kusama-specific considerations)

- Archive Layer 3 optimization strategies (data retrieval performance, cost optimization for scaling)

- Go-to-market strategy within Polkadot/Kusama ecosystem (community channels, partnership opportunities)

- Token economics design for future expansion (potential $CLUE token for governance/rewards)

**Specific expertise we're looking for:**

- Substrate/Kusama smart contract auditor for security review

- Archive technical architect for advanced features (batch document uploads, efficient querying)

- Growth/community expert familiar with crypto-native gaming launches

- Game economy designer with experience in competitive/prize pool mechanics

---

## 🎯 WHAT HAPPENS AFTER

**When M2 is done, we plan to...** 

- Launch first public investigation with 100-200 beta testers from Kusama community

- Run 2-3 investigations in month 2 to validate difficulty calibration and prize pool economics

- Implement creator economy foundation: allow anyone to generate custom investigations for ~$100

- Add multiple document types (phone transcripts, video evidence metadata) for narrative depth

- Build investigation template system so we can scale to weekly releases

- Integrate with additional Polkadot parachains for cross-chain player authentication

**And 6 months out we see our project achieving:**

- 1,000+ active investigators completing weekly missions across multiple difficulty tiers

- Proven unit economics: $7-10 registration fees with 70%+ margins after generation costs

- Thriving Discord community with player-created investigation theories and strategies

- First influencer partnerships (escape room YouTubers, true crime creators) driving viral growth

- Multiple simultaneous investigations running (beginner/intermediate/expert tracks)

- Investigation-as-a-Service beta: 10+ content creators paying to generate custom mysteries

- Case study demonstrating Archive's viability for novel blockchain-native game designs

- Foundation for physical/hybrid expansion: printable investigations, QR-code event mysteries

---

## 🔥 WHY THIS MATTERS

**Infinity Conspiracy Network proves blockchain can reward intelligence, not just luck.** We're building the first skill-based detective game where narrative depth meets competitive gameplay - addressing an intersection that doesn't exist in gaming today.

Our constraint-turned-feature (Archive's public data) creates a unique challenge: the truth is hidden in plain sight, rewarding deduction over guessing. This is the game conspiracy enthusiasts across the internet have been waiting for.

**"Everyone wants to be the first to solve a conspiracy. We're building the game that lets them."**

