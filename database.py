"""
Database module for Answer Evaluation System.
Provides persistence for evaluation history.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

import json
import sqlalchemy
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from config import get_settings

settings = get_settings()
Base = declarative_base()


class EvaluationRecord(Base):
    """Database model for storing evaluation results."""
    __tablename__ = "evaluations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow)
    student_name = Column(String(255), nullable=True)
    exam_name = Column(String(255), nullable=True)
    question = Column(Text, nullable=True)
    student_answer = Column(Text, nullable=True)
    reference_answer = Column(Text, nullable=True)
    similarity_score = Column(Float, nullable=True)
    coverage_score = Column(Float, nullable=True)
    grammar_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    grade = Column(String(10), nullable=True)
    feedback = Column(Text, nullable=True)
    metrics = Column(Text, nullable=True)
    evaluation_type = Column(String(50), default="single")  # single, batch, pdf, image
    processing_time_ms = Column(Integer, nullable=True)


class DatabaseManager:
    """Manages database operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False} if self.database_url.startswith("sqlite") else {}
        )

        # Ensure schema is up-to-date (add metrics column for existing DBs)
        if self.database_url.startswith("sqlite"):
            with self.engine.connect() as conn:
                res = conn.execute(text("PRAGMA table_info(evaluations)"))
                columns = [row[1] for row in res.fetchall()]
                if "metrics" not in columns:
                    conn.execute(text("ALTER TABLE evaluations ADD COLUMN metrics TEXT"))

        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def save_evaluation(self, 
                       evaluation_type: str = "single",
                       student_name: Optional[str] = None,
                       exam_name: Optional[str] = None,
                       question: Optional[str] = None,
                       student_answer: Optional[str] = None,
                       reference_answer: Optional[str] = None,
                       similarity_score: Optional[float] = None,
                       coverage_score: Optional[float] = None,
                       grammar_score: Optional[float] = None,
                       relevance_score: Optional[float] = None,
                       final_score: Optional[float] = None,
                       grade: Optional[str] = None,
                       feedback: Optional[str] = None,
                       metrics: Optional[Dict[str, Any]] = None,
                       processing_time_ms: Optional[int] = None) -> str:
        """Save an evaluation record to the database."""
        with self.get_session() as session:
            record = EvaluationRecord(
                evaluation_type=evaluation_type,
                student_name=student_name,
                exam_name=exam_name,
                question=question,
                student_answer=student_answer,
                reference_answer=reference_answer,
                similarity_score=similarity_score,
                coverage_score=coverage_score,
                grammar_score=grammar_score,
                relevance_score=relevance_score,
                final_score=final_score,
                grade=grade,
                feedback=feedback,
                metrics=json.dumps(metrics) if metrics is not None else None,
                processing_time_ms=processing_time_ms
            )
            session.add(record)
            try:
                session.flush()
                return record.id
            except OperationalError as err:
                if "no column named metrics" in str(err):
                    # backward compat: add missing column and retry once
                    with self.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE evaluations ADD COLUMN metrics TEXT"))
                        conn.commit()
                    session.rollback()
                    with self.get_session() as retry_session:
                        retry_record = EvaluationRecord(
                            evaluation_type=evaluation_type,
                            student_name=student_name,
                            exam_name=exam_name,
                            question=question,
                            student_answer=student_answer,
                            reference_answer=reference_answer,
                            similarity_score=similarity_score,
                            coverage_score=coverage_score,
                            grammar_score=grammar_score,
                            relevance_score=relevance_score,
                            final_score=final_score,
                            grade=grade,
                            feedback=feedback,
                            metrics=json.dumps(metrics) if metrics is not None else None,
                            processing_time_ms=processing_time_ms
                        )
                        retry_session.add(retry_record)
                        retry_session.flush()
                        return retry_record.id
                raise
    
    def get_evaluation(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        """Get a single evaluation by ID."""
        with self.get_session() as session:
            record = session.query(EvaluationRecord).filter(EvaluationRecord.id == evaluation_id).first()
            if record:
                return self._record_to_dict(record)
            return None
    
    def get_evaluations(self, 
                       student_name: Optional[str] = None,
                       exam_name: Optional[str] = None,
                       evaluation_type: Optional[str] = None,
                       limit: int = 100,
                       offset: int = 0) -> List[Dict[str, Any]]:
        """Get evaluations with optional filtering."""
        with self.get_session() as session:
            query = session.query(EvaluationRecord)
            
            if student_name:
                query = query.filter(EvaluationRecord.student_name == student_name)
            if exam_name:
                query = query.filter(EvaluationRecord.exam_name == exam_name)
            if evaluation_type:
                query = query.filter(EvaluationRecord.evaluation_type == evaluation_type)
            
            records = query.order_by(EvaluationRecord.timestamp.desc()).offset(offset).limit(limit).all()
            return [self._record_to_dict(record) for record in records]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get evaluation statistics."""
        with self.get_session() as session:
            total = session.query(EvaluationRecord).count()
            
            avg_score = session.query(EvaluationRecord).filter(
                EvaluationRecord.final_score.isnot(None)
            ).with_entities(
                sqlalchemy.func.avg(EvaluationRecord.final_score)
            ).scalar() or 0.0
            
            return {
                "total_evaluations": total,
                "average_score": round(avg_score, 2)
            }
    
    def delete_evaluation(self, evaluation_id: str) -> bool:
        """Delete an evaluation by ID."""
        with self.get_session() as session:
            result = session.query(EvaluationRecord).filter(EvaluationRecord.id == evaluation_id).delete()
            return result > 0
    
    def _record_to_dict(self, record: EvaluationRecord) -> Dict[str, Any]:
        """Convert a database record to a dictionary."""
        return {
            "id": record.id,
            "timestamp": record.timestamp.isoformat() if record.timestamp else None,
            "student_name": record.student_name,
            "exam_name": record.exam_name,
            "question": record.question,
            "student_answer": record.student_answer,
            "reference_answer": record.reference_answer,
            "similarity_score": record.similarity_score,
            "coverage_score": record.coverage_score,
            "grammar_score": record.grammar_score,
            "relevance_score": record.relevance_score,
            "final_score": record.final_score,
            "grade": record.grade,
            "feedback": record.feedback,
            "evaluation_type": record.evaluation_type,
            "processing_time_ms": record.processing_time_ms,
            "metrics": json.loads(record.metrics) if record.metrics else None
        }


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get or create the global database manager."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
