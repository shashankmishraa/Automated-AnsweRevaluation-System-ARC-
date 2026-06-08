"""
Google Gemini LLM Integration for Answer Evaluation System.
Provides AI-powered reference answer generation and intelligent scoring.
Includes detailed logging and API usage tracking.
"""

import json
import re
import time
import logging
from typing import Optional, Dict, Any
from config import get_settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service class for interacting with Gemini API."""

    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self._initialized = False
        self._usage_count = 0  # Track API calls in this session

        # Only initialize if API key is provided
        if self.settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(self.settings.GEMINI_MODEL)
                self._initialized = True
                logger.info(f"✨ Gemini LLM initialized with model: {self.settings.GEMINI_MODEL}")
                logger.info(f"📊 Free tier limits: 60 requests/min, 1500 requests/day")
            except ImportError:
                logger.warning("google-generativeai package not installed. Install with: pip install google-generativeai")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini LLM: {e}. Falling back to heuristic-based generation.")
        else:
            logger.warning("⚠️  GEMINI_API_KEY not set. LLM features will be disabled.")

    def is_available(self) -> bool:
        """Check if Gemini LLM is available."""
        return self._initialized and self.model is not None

    def _call_with_retry(self, prompt: str, generation_config: dict, max_retries: int = 3) -> Optional[str]:
        """Call Gemini API with exponential backoff on rate limit (429) errors."""
        for attempt in range(max_retries):
            try:
                self._usage_count += 1
                response = self.model.generate_content(prompt, generation_config=generation_config)
                return response.text.strip() if response and response.text else None
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                    # Try multiple regex patterns to parse retry delay from error
                    wait = 15 * (2 ** attempt)  # default exponential backoff
                    for pattern in [
                        r'retry_delay\s*\{\s*seconds:\s*(\d+)',
                        r'retryDelay["\s:]+([\d]+)',
                        r'retry in ([\d.]+)s',
                        r'Please retry in ([\d.]+)',
                    ]:
                        delay_match = re.search(pattern, err_str, re.IGNORECASE)
                        if delay_match:
                            wait = int(float(delay_match.group(1))) + 1
                            break
                    logger.warning(
                        f"Rate limit hit. Waiting {wait}s before retry "
                        f"(attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(wait)
                else:
                    logger.error(f"❌ Gemini API error: {e}")
                    return None
        logger.error("❌ Max retries exceeded for Gemini API call.")
        return None

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Robustly extract a JSON object from a Gemini response."""
        logger.debug(f"Attempting JSON extraction from: {text[:300]}")

        # Strip markdown code fences
        cleaned = re.sub(r'```(?:json)?\s*', '', text).strip().rstrip('`').strip()

        # Try direct parse first
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Find the outermost {...} block (greedy to get full object)
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError as e:
                logger.debug(f"JSON parse failed on extracted block: {e}")

        logger.warning(f"❌ No JSON found in Gemini response. Full response: {text[:500]}")
        return None

    def generate_reference_answer(self, question: str, max_length: int = 500) -> Optional[str]:
        """
        Generate a comprehensive reference answer using Gemini LLM.

        Args:
            question: The question text
            max_length: Maximum length of the generated answer

        Returns:
            Generated reference answer or None if LLM is unavailable
        """
        if not self.is_available():
            return None

        prompt = f"""You are an expert educational assistant. Your task is to generate a comprehensive, well-structured reference answer for the following question.

Question: {question}

Guidelines:
1. Provide a clear, accurate, and educationally appropriate answer
2. Include key concepts and important details that should be mentioned
3. Structure your answer logically (introduction, main points, conclusion)
4. Use academic language appropriate for student assessment
5. Keep the answer concise but comprehensive (around {max_length} characters)

Reference Answer:"""

        logger.info(f"🚀 [Gemini API Call #{self._usage_count + 1}] Generating reference answer...")
        result = self._call_with_retry(
            prompt,
            generation_config={
                'temperature': self.settings.LLM_TEMPERATURE,
                'max_output_tokens': self.settings.LLM_MAX_TOKENS,
            }
        )

        if result:
            logger.info(f"✅ Gemini generated reference answer ({len(result)} chars) - Session usage: {self._usage_count} calls")
        else:
            logger.warning("❌ Gemini returned empty response")
        return result

    def evaluate_answer_quality(
        self,
        question: str,
        reference_answer: str,
        student_answer: str
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate a student's answer using Gemini LLM for intelligent assessment.

        Args:
            question: The original question
            reference_answer: The ideal reference answer
            student_answer: The student's answer to evaluate

        Returns:
            Dictionary with evaluation metrics or None if LLM is unavailable
        """
        if not self.is_available():
            return None

        prompt = f"""You are an expert educational evaluator. Analyze and compare the following question, reference answer, and student answer.

Question: {question}

Reference Answer (Ideal):
{reference_answer}

Student Answer:
{student_answer}

Task: Evaluate the student's answer based on:
1. Content Coverage - What percentage of key concepts from the reference answer are present?
2. Accuracy - How factually correct is the information?
3. Completeness - Does the answer address all parts of the question?
4. Clarity - Is the answer well-organized and easy to understand?

Respond with ONLY a valid JSON object in this exact format (no markdown, no extra text):
{{
    "coverage_score": 0-100,
    "accuracy_score": 0-100,
    "completeness_score": 0-100,
    "clarity_score": 0-100,
    "overall_score": 0-100,
    "matched_concepts": ["list", "of", "concepts", "present"],
    "missing_concepts": ["list", "of", "concepts", "absent"],
    "feedback": "Detailed feedback for the student",
    "strengths": ["list", "of", "strengths"],
    "areas_for_improvement": ["list", "of", "improvements"]
}}"""

        logger.info(f"🚀 [Gemini API Call #{self._usage_count + 1}] Evaluating answer quality...")
        raw = self._call_with_retry(
            prompt,
            generation_config={
                'temperature': 0.2,
                'max_output_tokens': 800,
            }
        )

        if not raw:
            logger.warning("❌ Gemini returned empty evaluation")
            return None

        evaluation = self._extract_json(raw)
        if evaluation:
            logger.info(f"✅ Gemini successfully evaluated answer - Session usage: {self._usage_count} calls")
            return evaluation

        logger.error(f"❌ Failed to parse Gemini JSON response. Raw response: {raw[:200]}")
        return None

    def enhance_feedback(
        self,
        question: str,
        student_answer: str,
        base_feedback: str
    ) -> Optional[str]:
        """
        Use Gemini to enhance and elaborate on automated feedback.

        Args:
            question: The question being answered
            student_answer: The student's answer
            base_feedback: Basic feedback from traditional scoring

        Returns:
            Enhanced feedback or None if LLM is unavailable
        """
        if not self.is_available():
            return None

        prompt = f"""You are a helpful educational tutor. Enhance the following feedback for a student's answer.

Question: {question}

Student Answer: {student_answer}

Basic Feedback: {base_feedback}

Task: Make the feedback more constructive, encouraging, and specific. Include:
1. Specific examples from the student's answer
2. Clear explanations of what was done well
3. Actionable suggestions for improvement
4. Encouraging tone

Enhanced Feedback:"""

        logger.info(f"🚀 [Gemini API Call #{self._usage_count + 1}] Enhancing feedback...")
        result = self._call_with_retry(
            prompt,
            generation_config={
                'temperature': 0.4,
                'max_output_tokens': 400,
            }
        )

        if result:
            logger.info(f"✅ Gemini enhanced feedback ({len(result)} chars) - Session usage: {self._usage_count} calls")
        else:
            logger.warning("❌ Gemini returned empty feedback")
        return result


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create the Gemini service singleton."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
