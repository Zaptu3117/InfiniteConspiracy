"""Validation result models for anti-automation testing."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ValidationStep(BaseModel):
    """Result of validating a single step."""
    
    step_number: int
    sub_question: str
    llm_response: str
    expected_inference: str
    matches: bool
    confidence: float
    reasoning: Optional[str] = None


class ValidationResult(BaseModel):
    """Complete validation result for a mystery."""
    
    mystery_id: str
    
    # Single-LLM test (must FAIL)
    single_llm_test_passed: bool = False  # Should be False for valid mystery
    single_llm_response: Optional[str] = None
    single_llm_got_answer: bool = False  # Should be False
    
    # Multi-hop test (must SUCCEED)
    multi_hop_test_passed: bool = False  # Should be True for valid mystery
    multi_hop_steps: List[ValidationStep] = Field(default_factory=list)
    multi_hop_reached_answer: bool = False  # Should be True
    
    # Overall result
    is_valid: bool = False
    reason: str = ""
    
    def evaluate(self):
        """
        Evaluate if the mystery passes validation.
        
        A valid mystery must:
        1. Fail the single-LLM test (too hard for automation)
        2. Pass the multi-hop test (solvable with guidance)
        """
        # Check single-LLM test
        if self.single_llm_got_answer:
            self.is_valid = False
            self.reason = "Mystery is too easy - single LLM can solve it"
            return
        
        # Check multi-hop test
        if not self.multi_hop_reached_answer:
            self.is_valid = False
            self.reason = "Mystery is unsolvable - multi-hop test failed"
            return
        
        # Check all steps passed
        failed_steps = [s for s in self.multi_hop_steps if not s.matches]
        if failed_steps:
            self.is_valid = False
            self.reason = f"Multi-hop test failed at step(s): {[s.step_number for s in failed_steps]}"
            return
        
        # All checks passed
        self.is_valid = True
        self.reason = "Mystery is valid - automation-resistant and solvable"
        self.single_llm_test_passed = True  # Passed by failing
        self.multi_hop_test_passed = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.dict()
    
    def summary(self) -> str:
        """Get a summary string of the validation."""
        lines = [
            f"Mystery ID: {self.mystery_id}",
            f"Valid: {self.is_valid}",
            f"Reason: {self.reason}",
            "",
            f"Single-LLM Test (should fail): {'❌ FAILED (good!)' if not self.single_llm_got_answer else '✅ PASSED (bad!)'}",
            f"Multi-Hop Test (should pass): {'✅ PASSED' if self.multi_hop_reached_answer else '❌ FAILED'}",
            "",
            f"Multi-hop steps: {len(self.multi_hop_steps)}"
        ]
        
        for step in self.multi_hop_steps:
            status = "✅" if step.matches else "❌"
            lines.append(f"  Step {step.step_number}: {status} (confidence: {step.confidence:.2f})")
        
        return "\n".join(lines)

