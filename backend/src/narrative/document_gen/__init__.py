"""Document generation system using narrative graph."""

from .parallel_generator import ParallelDocumentGenerator
from .document_prompts import get_document_prompt_template

__all__ = [
    'ParallelDocumentGenerator',
    'get_document_prompt_template'
]

