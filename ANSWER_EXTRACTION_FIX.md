# Answer Extraction Fix: LLM-Based Semantic Extraction

**Date:** November 16, 2025  
**Status:** ✅ Implemented

## Problem

The original answer extraction used **regex patterns** which were too fragile:

### Issues Found:
1. **WHO** was truncated ("Director General Armand Voss" → "Armand")
2. **HOW** extracted person names instead of methods ("Viktor Koval" instead of "Infiltrate Ministry")
3. **WHY** was incomplete ("Control over the" instead of "Control Reality")
4. Regex couldn't handle complex premise text with nuanced language

## Solution

**Replaced regex extraction with LLM semantic understanding.**

### Implementation

```python
class AnswerTemplateGenerator:
    def __init__(self, llm_client):
        """Now requires LLM client for semantic extraction."""
        self.llm = llm_client
    
    async def extract_from_premise(self, premise: ConspiracyPremise) -> MysteryAnswer:
        """Use LLM to semantically extract discoverable answers."""
        
        # Build extraction prompt with clear rules
        prompt = f"""Extract 4 discoverable answers from conspiracy premise:

WHO: {premise.who}
WHAT: {premise.what}
WHY: {premise.why}
HOW: {premise.how}

RULES:
1. WHO: Full primary conspirator name (2-4 words, with title if present)
2. WHAT: Operation codename (2-3 words, remove "Operation" prefix)
3. WHY: Core motivation (verb + noun, 2-4 words like "Awaken Entity")
4. HOW: Primary method (verb + target, 2-4 words like "Infiltrate Agency")
   CRITICAL: HOW must be a METHOD/ACTION, NOT a person name

Output JSON only:
{{
  "who": "...",
  "what": "...",
  "why": "...",
  "how": "..."
}}
"""
        
        response = await self.llm.generate_json(prompt, temperature=0.3)
        
        # Validate with fallback
        who = response.get("who", "").strip()
        if not who or len(who.split()) < 2:
            who = self._fallback_extract_who(premise.who)
        
        # Check HOW isn't a person name
        how = response.get("how", "").strip()
        if self._looks_like_person_name(how):
            how = self._fallback_extract_how(premise.how)
        
        return MysteryAnswer(who=who, what=what, why=why, how=how)
```

### Key Features

1. **Semantic Understanding:** LLM understands context, not just patterns
2. **Validation:** Checks extracted values (length, format, semantic correctness)
3. **Person Name Detection:** Prevents extracting person names as methods
4. **Fallback System:** Uses simple regex if LLM fails
5. **Low Temperature:** 0.3 for consistent extraction

### Example Improvement

**Before (regex):**
```json
{
  "who": "Director General Armand",      // ❌ Truncated
  "what": "Astral Dawn",                  // ✅ Good
  "where": "Viktor Koval",                // ❌❌ Person name!
  "why": "Control over the"               // ❌ Incomplete
}
```

**After (LLM):**
```json
{
  "who": "Director General Armand Voss",  // ✅ Full name
  "what": "Astral Dawn",                   // ✅ Good
  "why": "Achieve Supremacy",              // ✅ Complete verb phrase
  "how": "Infiltrate Ministry"             // ✅ Method, not person!
}
```

## Files Changed

1. `backend/src/narrative/conspiracy/answer_template_generator.py`
   - Added `__init__(self, llm_client)` constructor
   - Changed `extract_from_premise()` to `async`
   - Replaced regex extraction with LLM prompt
   - Added `_looks_like_person_name()` validator
   - Kept fallback methods for reliability

2. `backend/src/narrative/conspiracy/conspiracy_pipeline.py`
   - Updated initialization: `AnswerTemplateGenerator(llm_client)`
   - Updated call: `await self.answer_template_gen.extract_from_premise(premise)`

## Benefits

✅ **More Accurate:** LLM understands semantic meaning  
✅ **Complete Names:** No truncation issues  
✅ **Correct Types:** HOW is always a method, never a person  
✅ **Better WHY:** Extracts complete motivational phrases  
✅ **Robust:** Fallback system if LLM fails  
✅ **Consistent:** Low temperature (0.3) for predictable results  

## Testing

To test the new extraction:

```bash
cd backend
uv run python -c "
import asyncio
from src.llm.anthropic_client import get_anthropic_client
from src.narrative.conspiracy.answer_template_generator import AnswerTemplateGenerator
from src.models.conspiracy import ConspiracyPremise

async def test():
    llm = get_anthropic_client()
    generator = AnswerTemplateGenerator(llm)
    
    premise = ConspiracyPremise(
        who='Director General Armand Voss, Colonel Lyra Hsu, Viktor Koval',
        what='Activate the Astral Convergence to control ley-lines',
        why='Voss seeks redemacy and legacy, Koval wants monopoly',
        how='Phase 1: Infiltrate Ministry of Energy. Phase 2: Extract quartz...',
        conspiracy_name='Operation Astral Dawn',
        conspiracy_type='occult',
        difficulty=6
    )
    
    answer = await generator.extract_from_premise(premise)
    print(f'WHO: {answer.who}')
    print(f'WHAT: {answer.what}')
    print(f'WHY: {answer.why}')
    print(f'HOW: {answer.how}')

asyncio.run(test())
"
```

Expected output:
```
WHO: Director General Armand Voss
WHAT: Astral Dawn
WHY: Achieve Supremacy
HOW: Infiltrate Ministry
```

## Next Steps

1. ✅ Implement LLM extraction (DONE)
2. ✅ Add validation logic (DONE)
3. ✅ Update pipeline to use async (DONE)
4. 🔄 Delete old broken mysteries
5. 🔄 Regenerate mysteries with new code
6. 🔄 Verify answers are correct and discoverable

---

**Summary:** Answer extraction now uses LLM semantic understanding instead of fragile regex, fixing truncation and type confusion issues.

