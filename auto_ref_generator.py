"""
Module for automatically generating reference answers from question papers.
Uses AI models to generate reference answers based on questions extracted from PDFs.
Now enhanced with Google Gemini LLM support!
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from models import get_model_manager
from pdf_processor import get_pdf_processor, ExtractedQuestion
from config import get_settings
from gemini_service import get_gemini_service

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class GeneratedReference:
    """Represents a generated reference answer."""
    question_number: int
    generated_answer: str
    confidence: float


class ReferenceAnswerGenerator:
    """Generates reference answers from questions using AI models."""
    
    def __init__(self):
        self.model_manager = get_model_manager()
        self.pdf_processor = get_pdf_processor()
        self.gemini_service = get_gemini_service()  # NEW: Gemini LLM support
        
    def generate_reference_answer(self, question: str, max_length: int = 500) -> GeneratedReference:
        """
        Generate a reference answer for a given question using AI models.
        Now with Google Gemini LLM support for high-quality answers!
        
        Args:
            question: The question text
            max_length: Maximum length of the generated answer
            
        Returns:
            GeneratedReference with the answer and confidence score
        """
        try:
            # PRIORITY 1: Try to use Gemini LLM if available (real AI generation)
            if settings.USE_LLM_FOR_REFERENCE and self.gemini_service.is_available():
                logger.info(f"Using Gemini LLM to generate reference answer for: {question[:50]}...")
                
                gemini_answer = self.gemini_service.generate_reference_answer(question, max_length)
                
                if gemini_answer:
                    # Successfully generated with LLM
                    logger.info("✅ Gemini LLM generated reference answer successfully")
                    return GeneratedReference(
                        question_number=0,
                        generated_answer=gemini_answer,
                        confidence=0.9  # High confidence for LLM-generated answers
                    )
                else:
                    logger.warning("Gemini returned empty answer, falling back to heuristic method")
            
            # FALLBACK: Use heuristic-based generation (original method)
            logger.info("Using heuristic-based reference generation (fallback)")
            question_embedding = self.model_manager.get_sentence_transformer().encode(question)
            
            # Generate a simple reference answer based on the question
            # This is a simplified approach - in practice, you'd use a generative model
            words = question.split()
            if len(words) > 5:
                # Take key concepts from the question and expand them
                key_concepts = [word for word in words if len(word) > 3]
                if key_concepts:
                    # Create a basic answer structure
                    answer_parts = []
                    
                    # Introduction
                    intro = f"The answer to this question involves discussing {', '.join(key_concepts[:3])}."
                    answer_parts.append(intro)
                    
                    # Main body - explain key concepts
                    for concept in key_concepts:
                        explanation = f"{concept.capitalize()} is an important aspect of this topic. "
                        explanation += f"It relates to the fundamental principles mentioned in the question."
                        answer_parts.append(explanation)
                    
                    # Conclusion
                    conclusion = f"In summary, understanding {key_concepts[0] if key_concepts else 'the topic'} "
                    conclusion += f"is crucial for answering this question comprehensively."
                    answer_parts.append(conclusion)
                    
                    generated_answer = " ".join(answer_parts)
                else:
                    generated_answer = f"A comprehensive answer to '{question}' would include all relevant concepts and explanations."
            else:
                generated_answer = f"The answer to '{question}' should be detailed and cover all aspects mentioned in the question."
            
            # Truncate to max length if needed
            if len(generated_answer) > max_length:
                generated_answer = generated_answer[:max_length]
                # Find the last space to avoid cutting off words
                last_space = generated_answer.rfind(' ')
                if last_space > 0:
                    generated_answer = generated_answer[:last_space] + "..."
            
            # Calculate a confidence score based on question complexity
            # More complex questions (longer, with more keywords) might have higher confidence
            question_complexity = min(1.0, len(question.split()) / 20.0)
            answer_quality_score = min(1.0, len(generated_answer) / 100.0)
            confidence = (question_complexity + answer_quality_score) / 2
            
            return GeneratedReference(
                question_number=0,  # Will be set by caller
                generated_answer=generated_answer,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error generating reference answer: {e}")
            return GeneratedReference(
                question_number=0,
                generated_answer=f"Sample answer for: {question}",
                confidence=0.3
            )
    
    def generate_references_for_questions(self, questions: List[ExtractedQuestion]) -> Dict[int, str]:
        """
        Generate reference answers for a list of questions.
        
        Args:
            questions: List of ExtractedQuestion objects
            
        Returns:
            Dictionary mapping question numbers to generated reference answers
        """
        references = {}
        
        for question in questions:
            try:
                generated_ref = self.generate_reference_answer(question.text)
                references[question.number] = generated_ref.generated_answer
                logger.info(f"Generated reference for question {question.number} with confidence {generated_ref.confidence:.2f}")
            except Exception as e:
                logger.error(f"Failed to generate reference for question {question.number}: {e}")
                # Fallback to a basic reference answer
                references[question.number] = f"Sample answer for question: {question.text}"
        
        return references


# Singleton instance
_reference_generator: Optional[ReferenceAnswerGenerator] = None


def get_reference_generator() -> ReferenceAnswerGenerator:
    """Get or create the reference answer generator singleton."""
    global _reference_generator
    if _reference_generator is None:
        _reference_generator = ReferenceAnswerGenerator()
    return _reference_generator


# Example usage and testing
if __name__ == "__main__":
    # Test the reference generator
    generator = get_reference_generator()
    
    # Sample questions
    sample_questions = [
        ExtractedQuestion(number=1, text="What is machine learning and its applications?", marks=10),
        ExtractedQuestion(number=2, text="Explain the difference between supervised and unsupervised learning.", marks=8)
    ]
    
    print("Testing reference answer generation...")
    refs = generator.generate_references_for_questions(sample_questions)
    
    for q_num, ref in refs.items():
        print(f"\nQuestion {q_num}:")
        print(f"Reference: {ref}")