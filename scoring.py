"""
Scoring module for Answer Evaluation System.
Centralized scoring logic with configurable weights.
"""

import re
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher


from fuzzywuzzy import fuzz

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def generate_visual_highlights(reference_answer, matched, missing):
    """
    Generate HTML-ready visual highlights for gap visualization.
    Returns color-coded segments of the reference answer.
    """
    if not reference_answer:
        return []
    
    # Create list of concepts to highlight
    highlights = []
    
    # Add matched concepts (green)
    for match in matched:
        highlights.append({
            'text': match['concept'],
            'status': 'matched',
            'color': 'green',
            'type': match['status']  # 'correct' or 'partial'
        })
    
    # Add missing concepts (red)
    for miss in missing:
        highlights.append({
            'text': miss['concept'],
            'status': 'missing',
            'color': 'red',
            'importance': miss['importance'],
            'marks_worth': miss['marks_worth']
        })
    
    # Sort by position in text (simple approach)
    result = []
    remaining_text = reference_answer
    
    for highlight in sorted(highlights, key=lambda x: len(x['text']), reverse=True):
        concept = highlight['text']
        if concept in remaining_text:
            result.append(highlight)
    
    return result


def extract_key_concepts(text):
    """
    Extract key concepts from text using NLP techniques.
    Returns set of important terms and phrases.
    """
    if not text:
        return set()
    
    # Remove common stop words and get meaningful terms
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
        'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
        'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above',
        'below', 'between', 'under', 'again', 'further', 'then', 'once', 'and',
        'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither', 'not',
        'only', 'own', 'same', 'than', 'too', 'very', 'just', 'also', 'now'
    }
    
    # Extract multi-word technical terms (capitalized or hyphenated)
    tech_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|\b[a-z]+-[a-z]+|\b[A-Z]{2,}\b', text)
    
    # Extract noun phrases (simple approach)
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    meaningful_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Combine all concepts
    concepts = set(tech_terms)
    concepts.update(meaningful_words)
    
    return concepts


def perform_gap_analysis(reference_answer, student_answer):
    """
    Perform detailed gap analysis between reference and student answers.
    Returns visualizable gaps with color-coding suggestions.
    """
    if not reference_answer or not student_answer:
        return None
    
    ref_concepts = extract_key_concepts(reference_answer)
    stu_concepts = extract_key_concepts(student_answer)
    
    # Find matches, missing, and vague concepts
    matched = []
    missing = []
    vague = []
    
    ref_lower = {c.lower(): c for c in ref_concepts}
    stu_lower = {c.lower(): c for c in stu_concepts}
    
    for ref_concept in ref_concepts:
        ref_lower_concept = ref_concept.lower()
        
        # Check for exact or fuzzy match
        found = False
        for stu_concept in stu_concepts:
            stu_lower_concept = stu_concept.lower()
            
            # Exact match
            if ref_lower_concept == stu_lower_concept:
                matched.append({
                    'concept': ref_concept,
                    'status': 'correct',
                    'student_version': stu_concept
                })
                found = True
                break
            
            # Fuzzy match (>80% similarity)
            elif SequenceMatcher(None, ref_lower_concept, stu_lower_concept).ratio() > 0.8:
                matched.append({
                    'concept': ref_concept,
                    'status': 'partial',
                    'student_version': stu_concept
                })
                found = True
                break
        
        if not found:
            missing.append({
                'concept': ref_concept,
                'importance': 'high' if len(ref_concept.split()) > 1 else 'medium',
                'marks_worth': len(ref_concept.split()) * 2
            })
    
    # Find vague terms in student answer
    vague_indicators = ['thing', 'stuff', 'something', 'somehow', 'basically', 'generally']
    student_words = student_answer.lower().split()
    for word in student_words:
        if word in vague_indicators:
            vague.append({'term': word, 'suggestion': 'Be more specific'})
    
    # Calculate coverage percentage
    total_ref_concepts = len(ref_concepts)
    matched_concepts = len(matched)
    coverage_percentage = (matched_concepts / total_ref_concepts * 100) if total_ref_concepts > 0 else 0
    
    return {
        'matched': matched,
        'missing': missing,
        'vague': vague,
        'coverage_percentage': round(coverage_percentage, 2),
        'total_reference_concepts': total_ref_concepts,
        'matched_concepts': matched_concepts,
        'missing_concepts': len(missing),
        'visual_highlights': generate_visual_highlights(reference_answer, matched, missing)
    }


@dataclass
class ScoreResult:
    """Result of scoring an answer."""
    similarity: float
    coverage: float
    grammar: float
    relevance: float
    final_score: float
    grade: str
    feedback: str
    detailed_metrics: Dict
    cnn_score: Optional[float] = None  # Added for CNN scoring (optional with default)
    gap_analysis: Optional[Dict] = None  # Gap visualization data


class GradeCalculator:
    """Calculate letter grades from scores."""
    
    GRADE_SCALE = [
        (90, "A+"),
        (85, "A"),
        (80, "A-"),
        (75, "B+"),
        (70, "B"),
        (65, "B-"),
        (60, "C+"),
        (55, "C"),
        (50, "C-"),
        (40, "D"),
        (0, "F")
    ]
    
    @classmethod
    def from_percentage(cls, percentage: float) -> str:
        """Get grade from percentage (0-100)."""
        for threshold, grade in cls.GRADE_SCALE:
            if percentage >= threshold:
                return grade
        return "F"
    
    @classmethod
    def from_score(cls, score: float, max_score: float = 10.0) -> str:
        """Get grade from score (0-max_score)."""
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        return cls.from_percentage(percentage)


class GrammarScorer:
    """Score grammar quality of text."""
    
    @staticmethod
    def score(text: str) -> float:
        """Calculate grammar score (0-1)."""
        try:
            if not text or not isinstance(text, str):
                return 0.5
            
            text = text.strip()
            if not text:
                return 0.5
            
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return 0.5
            
            score = 1.0
            
            # Check capitalization
            capitalized = sum(1 for s in sentences if s and s[0].isupper())
            cap_ratio = capitalized / len(sentences)
            
            # Check ending punctuation
            has_ending_punct = text[-1] in '.!?' if text else False
            
            # Check sentence length
            words_per_sentence = [len(s.split()) for s in sentences]
            avg_words = sum(words_per_sentence) / len(words_per_sentence)
            
            # Penalty for very short or very long sentences
            length_penalty = 0
            if avg_words < 3:
                length_penalty = 0.3
            elif avg_words > 30:
                length_penalty = 0.2
            
            # Calculate final score
            score = (cap_ratio * 0.4) + (0.3 if has_ending_punct else 0) + max(0, 0.3 - length_penalty)
            
            # Additional checks for common issues
            # Check for repeated punctuation
            if re.search(r'[.]{2,}|[!]{2,}|[?]{2,}', text):
                score -= 0.1
            
            # Check for all caps words (shouting)
            words = text.split()
            caps_words = sum(1 for w in words if w.isupper() and len(w) > 1)
            if caps_words > len(words) * 0.3:
                score -= 0.1
            
            return round(max(0.0, min(1.0, score)), 3)
            
        except Exception as e:
            logger.error(f"Grammar scoring error: {e}")
            return 0.5


class CoverageScorer:
    """Score keyword coverage between reference and student answer."""
    
    @staticmethod
    def score(reference: str, student: str, threshold: int = 70) -> float:
        """Calculate fuzzy keyword coverage (0-1)."""
        try:
            if not reference or not student:
                return 0.0
            
            # Extract meaningful words (length > 2)
            ref_words = set(
                word.lower() for word in reference.split()
                if len(word) > 2 and word.isalnum()
            )
            student_words = set(
                word.lower() for word in student.split()
                if len(word) > 2 and word.isalnum()
            )
            
            if not ref_words:
                return 0.0
            
            matched = 0
            for ref_word in ref_words:
                # Check for exact match or fuzzy match
                for student_word in student_words:
                    if (
                        ref_word == student_word or
                        ref_word in student_word or
                        student_word in ref_word or
                        fuzz.ratio(ref_word, student_word) > threshold
                    ):
                        matched += 1
                        break
            
            score = matched / len(ref_words)
            if score == 0 and student_words:
                return 0.05
            return round(score, 3)
            
        except Exception as e:
            logger.error(f"Coverage scoring error: {e}")
            return 0.0


class FeedbackGenerator:
    """Generate feedback based on scores."""
    
    @staticmethod
    def generate(
        score: float,
        similarity: float,
        coverage: float,
        grammar: float,
        relevance: float,
        max_score: float = 10.0
    ) -> str:
        """Generate comprehensive feedback."""
        feedback_parts = []
        
        # Overall assessment
        percentage = (score / max_score) * 100
        if percentage >= 90:
            feedback_parts.append("Excellent answer! Outstanding comprehension and expression.")
        elif percentage >= 75:
            feedback_parts.append("Good answer with room for minor improvements.")
        elif percentage >= 60:
            feedback_parts.append("Satisfactory answer but needs improvement in key areas.")
        elif percentage >= 40:
            feedback_parts.append("Answer needs significant improvement.")
        else:
            feedback_parts.append("Answer requires substantial revision. Please review the topic.")
        
        # Specific suggestions
        suggestions = []
        
        if similarity < 0.6:
            suggestions.append("Include more concepts from the reference material.")
        
        if coverage < 0.5:
            suggestions.append("Cover more key terms and important points.")
        
        if grammar < 0.6:
            suggestions.append("Work on sentence structure, capitalization, and punctuation.")
        
        if relevance < 0.5:
            suggestions.append("Ensure your answer directly addresses the question asked.")
        
        if suggestions:
            feedback_parts.append("Suggestions: " + " ".join(suggestions))
        
        return " ".join(feedback_parts)


class ScoreCalculator:
    """Main scoring calculator."""
    
    def __init__(self, use_cnn: bool = False, cnn_weight: Optional[float] = None):
        self.weights = {
            'similarity': settings.WEIGHT_SIMILARITY,
            'coverage': settings.WEIGHT_COVERAGE,
            'grammar': settings.WEIGHT_GRAMMAR,
            'relevance': settings.WEIGHT_RELEVANCE
        }
        self.use_cnn = use_cnn
        self.cnn_weight = cnn_weight if cnn_weight is not None else settings.CNN_WEIGHT
        # Adjust weights if using CNN
        if use_cnn:
            # Reduce other weights proportionally to accommodate CNN
            scale_factor = 1.0 - self.cnn_weight
            self.weights['similarity'] *= scale_factor
            self.weights['coverage'] *= scale_factor
            self.weights['grammar'] *= scale_factor
            self.weights['relevance'] *= scale_factor
            self.weights['cnn'] = self.cnn_weight
    
    def calculate_final_score(
        self,
        similarity: float,
        coverage: float,
        grammar: float,
        relevance: float,
        cnn_score: Optional[float] = None
    ) -> float:
        """Calculate weighted final score (0-10)."""
        weighted_sum = (
            self.weights['similarity'] * similarity +
            self.weights['coverage'] * coverage +
            self.weights['grammar'] * grammar +
            self.weights['relevance'] * relevance
        )
        
        # Add CNN score if available and enabled
        if self.use_cnn and cnn_score is not None:
            weighted_sum += self.weights.get('cnn', 0) * cnn_score
        
        return round(weighted_sum * 10, 2)
    
    def calculate_with_bonus(
        self,
        similarity: float,
        coverage: float,
        grammar: float,
        relevance: float,
        cnn_score: Optional[float] = None,
        has_diagram: bool = False,
        diagram_bonus: float = 0.5,
        max_score: float = 10.0
    ) -> Tuple[float, float]:
        """Calculate score with optional diagram bonus."""
        base_score = self.calculate_final_score(similarity, coverage, grammar, relevance, cnn_score)
        
        if has_diagram:
            # Apply bonus as percentage increase, not fixed points
            bonus_amount = base_score * (diagram_bonus / 100)
            final_score = min(max_score, round(base_score + bonus_amount, 2))
        else:
            final_score = base_score
        
        return base_score, final_score


# Convenience functions
def determine_grade(score: float, max_score: float = 10.0) -> str:
    """Determine letter grade from score."""
    return GradeCalculator.from_score(score, max_score)


def determine_grade_from_percentage(percentage: float) -> str:
    """Determine letter grade from percentage."""
    return GradeCalculator.from_percentage(percentage)


def grammar_score(text: str) -> float:
    """Calculate grammar score."""
    return GrammarScorer.score(text)


def coverage_score(reference: str, student: str, threshold: int = 70) -> float:
    """Calculate coverage score."""
    return CoverageScorer.score(reference, student, threshold)


def generate_feedback(
    score: float,
    similarity: float,
    coverage: float,
    grammar: float,
    relevance: float,
    max_score: float = 10.0
) -> str:
    """Generate feedback."""
    return FeedbackGenerator.generate(score, similarity, coverage, grammar, relevance, max_score)

class GeminiEnhancedScorer:
    """Enhanced scoring using Gemini LLM."""
    
    def __init__(self):
        self.gemini_service = None
        try:
            from gemini_service import get_gemini_service
            self.gemini_service = get_gemini_service()
            if self.gemini_service and self.gemini_service.is_available():
                logger.info("✅ GeminiEnhancedScorer initialized successfully")
            else:
                logger.warning("⚠️  Gemini service not available for enhanced scoring")
        except Exception as e:
            logger.warning(f"Gemini service initialization failed: {e}")
    
    def score_with_gemini(self, question: str, reference: str, student: str):
        """
        Get Gemini-enhanced evaluation scores.
        Returns dictionary with scores or None if Gemini unavailable.
        """
        if not self.gemini_service or not self.gemini_service.is_available():
            return None
        
        try:
            result = self.gemini_service.evaluate_answer_quality(question, reference, student)
            
            if result:
                # Convert 0-100 scores to 0-1 scale
                return {
                    'coverage': result.get('coverage_score', 0) / 100,
                    'relevance': result.get('completeness_score', 0) / 100,
                    'accuracy': result.get('accuracy_score', 0) / 100,
                    'clarity': result.get('clarity_score', 0) / 100,
                    'overall': result.get('overall_score', 0) / 100,
                    'feedback': result.get('feedback', ''),
                    'matched_concepts': result.get('matched_concepts', []),
                    'missing_concepts': result.get('missing_concepts', []),
                    'strengths': result.get('strengths', []),
                    'areas_for_improvement': result.get('areas_for_improvement', []),
                    'vague_terms': result.get('vague_terms', []),
                    'coverage_score': result.get('coverage_score', 0),
                    'accuracy_score': result.get('accuracy_score', 0),
                    'clarity_score': result.get('clarity_score', 0),
                    'completeness_score': result.get('completeness_score', 0)
                }
            else:
                logger.warning("Gemini returned empty evaluation result")
                return None
                
        except Exception as e:
            logger.error(f"Gemini scoring error: {e}")
            return None