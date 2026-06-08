"""
Model management module for Answer Evaluation System.
Handles loading and caching of ML models.
"""

import os
import pickle
import logging
from typing import Dict, Optional, Any, Tuple
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer, util

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class ModelManager:
    """Manages ML models for answer evaluation."""
    
    def __init__(self):
        self.sentence_transformers: Dict[str, SentenceTransformer] = {}
        self.cnn_model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.default_model: str = settings.DEFAULT_MODEL
        self._load_models()
    
    def _load_models(self):
        """Load all configured models."""
        # Load sentence transformers
        for model_name in settings.sentence_transformer_models_list:
            try:
                # Create a friendly name from the model path
                friendly_name = model_name.split('/')[-1].replace('all-', '').replace('-v2', '').replace('-base', '')
                self.sentence_transformers[friendly_name] = SentenceTransformer(model_name)
                logger.info(f"Loaded sentence transformer: {friendly_name}")
            except Exception as e:
                logger.error(f"Failed to load sentence transformer {model_name}: {e}")
        
        # Load CNN model if available
        try:
            if os.path.exists(settings.CNN_MODEL_PATH):
                from tensorflow.keras.models import load_model
                self.cnn_model = load_model(settings.CNN_MODEL_PATH)
                logger.info("Loaded CNN model")
            else:
                logger.warning(f"CNN model not found at {settings.CNN_MODEL_PATH}")
        except Exception as e:
            logger.warning(f"Failed to load CNN model: {e}")
            self.cnn_model = None
        
        # Load tokenizer if available
        try:
            if os.path.exists(settings.TOKENIZER_PATH):
                # Warning: pickle files can execute arbitrary code if tampered with.
                # Ensure tokenizer.pkl comes from a trusted source and has not been modified.
                hash_file = settings.TOKENIZER_PATH + ".sha256"
                if os.path.exists(hash_file):
                    import hashlib
                    with open(settings.TOKENIZER_PATH, "rb") as f:
                        file_bytes = f.read()
                    actual_hash = hashlib.sha256(file_bytes).hexdigest()
                    with open(hash_file, "r") as hf:
                        expected_hash = hf.read().strip()
                    if actual_hash != expected_hash:
                        logger.error("Tokenizer file hash mismatch — refusing to load potentially tampered file.")
                        self.tokenizer = None
                        return
                    self.tokenizer = pickle.loads(file_bytes)
                else:
                    logger.warning(
                        f"No .sha256 hash file found for tokenizer at {settings.TOKENIZER_PATH}. "
                        "Loading anyway, but consider generating a hash file for integrity verification."
                    )
                    with open(settings.TOKENIZER_PATH, "rb") as f:
                        self.tokenizer = pickle.load(f)
                logger.info("Loaded tokenizer")
            else:
                logger.warning(f"Tokenizer not found at {settings.TOKENIZER_PATH}")
        except Exception as e:
            logger.warning(f"Failed to load tokenizer: {e}")
            self.tokenizer = None
    
    def get_sentence_transformer(self, model_name: Optional[str] = None) -> Optional[SentenceTransformer]:
        """Get a sentence transformer model by name."""
        model_name = model_name or self.default_model
        
        # Try exact match first
        if model_name in self.sentence_transformers:
            return self.sentence_transformers[model_name]
        
        # Try case-insensitive match
        for name, model in self.sentence_transformers.items():
            if name.lower() == model_name.lower():
                return model
        
        # Return first available if default not found
        if self.sentence_transformers:
            return next(iter(self.sentence_transformers.values()))
        
        return None
    
    def compute_similarity(
        self,
        reference: str,
        student: str,
        model_name: Optional[str] = None
    ) -> float:
        """Compute semantic similarity between two texts."""
        model = self.get_sentence_transformer(model_name)
        
        if not model:
            logger.error("No sentence transformer model available")
            return 0.0
        
        try:
            ref_emb = model.encode(reference, convert_to_tensor=True)
            student_emb = model.encode(student, convert_to_tensor=True)
            similarity = util.cos_sim(ref_emb, student_emb).item()
            # Normalize to 0-1 range
            normalized = round((similarity + 1) / 2, 3)
            if reference.strip() and student.strip():
                return max(0.05, normalized)
            return normalized
        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            return 0.0
    
    def compute_relevance(
        self,
        question: str,
        answer: str,
        model_name: Optional[str] = None
    ) -> float:
        """Compute relevance of answer to question."""
        model = self.get_sentence_transformer(model_name)
        
        if not model:
            logger.error("No sentence transformer model available")
            return 0.5
        
        try:
            q_emb = model.encode(question, convert_to_tensor=True)
            a_emb = model.encode(answer, convert_to_tensor=True)
            relevance = util.cos_sim(q_emb, a_emb).item()
            # Normalize to 0-1 range
            normalized = round((relevance + 1) / 2, 3)
            if question.strip() and answer.strip():
                return max(0.05, normalized)
            return normalized
        except Exception as e:
            logger.error(f"Relevance calculation error: {e}")
            return 0.5
    
    def _preprocess_for_cnn(self, text1: str, text2: str, max_length: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess two texts for CNN model input.
        
        Args:
            text1: First text (e.g., reference answer)
            text2: Second text (e.g., student answer)
            max_length: Maximum sequence length for padding/truncation
            
        Returns:
            Tuple of (sequence1, sequence2) as numpy arrays
        """
        if not self.tokenizer:
            raise ValueError("Tokenizer not loaded")
        
        # Tokenize both texts
        seq1 = self.tokenizer.texts_to_sequences([text1])[0]
        seq2 = self.tokenizer.texts_to_sequences([text2])[0]
        
        # Pad or truncate to max_length
        def pad_sequence(seq, maxlen):
            if len(seq) > maxlen:
                return seq[:maxlen]
            elif len(seq) < maxlen:
                return seq + [0] * (maxlen - len(seq))
            return seq
        
        seq1_padded = pad_sequence(seq1, max_length)
        seq2_padded = pad_sequence(seq2, max_length)
        
        return np.array([seq1_padded]), np.array([seq2_padded])
    
    def compute_cnn_score(
        self,
        reference: str,
        student: str,
        max_length: int = 100
    ) -> float:
        """Compute similarity score using CNN model.
        
        Args:
            reference: Reference answer text
            student: Student answer text
            max_length: Maximum sequence length for tokenization
            
        Returns:
            Score between 0 and 1
        """
        if not self.cnn_model:
            logger.warning("CNN model not available")
            return 0.0
        
        if not self.tokenizer:
            logger.warning("Tokenizer not available for CNN")
            return 0.0
        
        try:
            # Preprocess texts
            ref_seq, student_seq = self._preprocess_for_cnn(reference, student, max_length)
            
            # Predict using CNN
            prediction = self.cnn_model.predict([ref_seq, student_seq], verbose=0)
            
            # Assuming model outputs probability/score in [0, 1]
            score = float(prediction[0][0])
            
            # Ensure score is in valid range
            score = max(0.0, min(1.0, score))
            
            logger.debug(f"CNN score: {score:.3f} for reference='{reference[:50]}...' student='{student[:50]}...'")
            
            return round(score, 3)
            
        except Exception as e:
            logger.error(f"CNN scoring error: {e}")
            return 0.0
    
    def compute_hybrid_score(
        self,
        reference: str,
        student: str,
        question: Optional[str] = None,
        cnn_weight: float = 0.4,
        transformer_weight: float = 0.6,
        model_name: Optional[str] = None
    ) -> float:
        """Compute hybrid score combining CNN and Sentence Transformers.
        
        Args:
            reference: Reference answer text
            student: Student answer text
            question: Optional question text for relevance
            cnn_weight: Weight for CNN score (0-1)
            transformer_weight: Weight for transformer similarity (0-1)
            model_name: Optional model name for transformer
            
        Returns:
            Combined score between 0 and 1
        """
        # Get individual scores
        cnn_score = self.compute_cnn_score(reference, student)
        transformer_score = self.compute_similarity(reference, student, model_name)
        
        # Combine scores
        hybrid = (cnn_weight * cnn_score) + (transformer_weight * transformer_score)
        
        logger.debug(f"Hybrid score: {hybrid:.3f} (CNN: {cnn_score:.3f}, Transformer: {transformer_score:.3f})")
        
        return round(hybrid, 3)
    
    def get_available_models(self) -> Dict[str, bool]:
        """Get list of available models."""
        return {
            "sentence_transformers": list(self.sentence_transformers.keys()),
            "default_model": self.default_model,
            "cnn_available": self.cnn_model is not None,
            "tokenizer_available": self.tokenizer is not None
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check model health status."""
        return {
            "sentence_transformers_loaded": len(self.sentence_transformers),
            "sentence_transformer_models": list(self.sentence_transformers.keys()),
            "cnn_model_loaded": self.cnn_model is not None,
            "tokenizer_loaded": self.tokenizer is not None,
            "status": "healthy" if self.sentence_transformers else "unhealthy"
        }


# Global model manager instance
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get or create the global model manager."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
