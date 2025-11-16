# Contract & Backend Answer Format Update

## Summary of Changes

Fixed the mismatch between conspiracy concept and smart contract answer format.

## Problems Found

### 1. Contract Used WHERE Instead of HOW
The smart contract used `WHERE` (location) but the conspiracy system uses `HOW` (method/tactics).

**Why HOW Makes More Sense for Conspiracies:**
- Conspiracies involve complex multi-step methods (infiltration, blackmail, etc.)
- "Where" is too limiting for multi-location conspiracies
- "How" captures the tactics and execution method

### 2. Answer Generator Was Not Creating Discoverable Answers
The old `answer_template_generator.py` just extracted from premise text instead of creating answers that are **findable through investigation**.

### 3. Answer Template Values Were Not Used in Evidence
The answer_template was created but NOT passed to evidence node generators, so the WHO name didn't appear in identity chains!

## Changes Made

### 1. Smart Contract (InfiniteConspiracy.sol)
```solidity
// BEFORE:
function submitAnswer(
    string calldata who,
    string calldata what,
    string calldata where,   ❌
    string calldata why
)

// AFTER:
function submitAnswer(
    string calldata who,
    string calldata what,
    string calldata why,     ✅ Reordered
    string calldata how      ✅ Changed
)
```

Hash generation updated:
```solidity
// BEFORE:
keccak256(abi.encodePacked(
    _toLower(who), "|",
    _toLower(what), "|",
    _toLower(where), "|",  ❌
    _toLower(why)
))

// AFTER:
keccak256(abi.encodePacked(
    _toLower(who), "|",
    _toLower(what), "|",
    _toLower(why), "|",    ✅
    _toLower(how)          ✅
))
```

### 2. Backend Models (conspiracy.py)
```python
# BEFORE:
@dataclass
class MysteryAnswer:
    who: str = ""
    what: str = ""
    where: str = ""   ❌
    why: str = ""
    
    def generate_hash(self) -> str:
        combined = f"{self.who.lower()}|{self.what.lower()}|{self.where.lower()}|{self.why.lower()}"

# AFTER:
@dataclass
class MysteryAnswer:
    who: str = ""
    what: str = ""
    why: str = ""     ✅
    how: str = ""     ✅
    
    def generate_hash(self) -> str:
        combined = f"{self.who.lower()}|{self.what.lower()}|{self.why.lower()}|{self.how.lower()}"
```

### 3. Answer Template Generator (answer_template_generator.py)
**Completely rewritten** to create **discoverable** answers:

```python
# BEFORE:
where = self._extract_primary_location(premise.how, premise.what)  ❌ Nonsensical

# AFTER:
# WHO: Extract PRIMARY conspirator name (appears in identity evidence)
who = self._extract_primary_conspirator(premise.who)  
# "Dr. Althea Voss (Chief Research Officer)..." → "Dr. Althea Voss"

# WHAT: Extract operation codename (appears in encrypted docs)
what = self._extract_operation_codename(premise.conspiracy_name)
# "Operation Abyssal Convergence" → "Abyssal Convergence"

# WHY: Extract core motivation (appears in psychological evidence)
why = self._extract_core_motivation(premise.why, premise.what)
# "They believe... awakening the Serpent..." → "Awaken Ancient Entity"

# HOW: Extract primary method (appears in evidence)
how = self._extract_primary_method(premise.how)
# "Phase 1: Infiltrate Obsidian Energy..." → "Infiltrate Obsidian Energy"
```

### 4. Conspiracy Pipeline (conspiracy_pipeline.py)
**Passed answer_template to evidence generation:**

```python
# BEFORE:
await self._populate_evidence_nodes(subgraphs, premise, political_context, difficulty)

# Inside _populate_evidence_nodes:
target_name = premise.who.split()[0]  ❌ Gets messy name

# AFTER:
await self._populate_evidence_nodes(subgraphs, premise, political_context, difficulty, answer_template)

# Inside _populate_evidence_nodes:
target_name = answer_template.who  ✅ Uses clean discoverable name
logger.info(f"   🔍 Identity chain will lead to: {target_name}")
```

Also fixed logging:
```python
# BEFORE:
logger.info(f"   WHERE: {answer_template.where}")  ❌

# AFTER:
logger.info(f"   WHY: {answer_template.why}")      ✅
logger.info(f"   HOW: {answer_template.how}")      ✅
```

## Result

Now the system:
1. ✅ Contract uses WHO/WHAT/WHY/HOW (matches conspiracy concept)
2. ✅ Answer generator creates SHORT, DISCOVERABLE answers
3. ✅ Answer template values are ACTUALLY USED in evidence generation
4. ✅ Identity chains lead to the correct WHO name
5. ✅ Hash generation is consistent between backend and contract

## Testing Required

1. **Compile Contract:**
   ```bash
   cd contracts
   npx hardhat compile
   npx hardhat test
   ```

2. **Generate New Mystery:**
   ```bash
   cd backend
   uv run python test_conspiracy_foundation.py
   ```

3. **Verify Answer Template:**
   Check that generated mystery has:
   - WHO: Clean name (e.g., "Dr. Althea Voss")
   - WHAT: Operation codename (e.g., "Abyssal Convergence")
   - WHY: Core motivation (e.g., "Awaken Ancient Entity")
   - HOW: Primary method (e.g., "Infiltrate Obsidian Energy")

4. **Verify Evidence Contains Answers:**
   - Identity chains mention the WHO name
   - Documents reference the WHAT operation
   - Psychological evidence suggests the WHY
   - Method descriptions include the HOW

## Files Changed

- `contracts/contracts/InfiniteConspiracy.sol`
- `backend/src/models/conspiracy.py`
- `backend/src/narrative/conspiracy/answer_template_generator.py` (rewritten)
- `backend/src/narrative/conspiracy/conspiracy_pipeline.py` (2 updates)

## Next Steps

1. Test contract compilation
2. Generate a new conspiracy mystery
3. Verify answers are discoverable in documents
4. Update frontend to use new answer format (WHO/WHAT/WHY/HOW)
5. Update documentation

---

**Date:** $(date)
**Status:** ✅ Complete - Ready for Testing
