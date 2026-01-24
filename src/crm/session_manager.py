"""
Database Session Manager
Provides unified session management with automatic commit/rollback
"""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from .database import SessionLocal


class DatabaseSessionManager:
    """
    Unified database session manager
    
    Features:
    - Automatic session lifecycle management
    - Automatic commit on success
    - Automatic rollback on error
    - Context manager support
    - Thread-safe
    """
    
    @staticmethod
    @contextmanager
    def get_db() -> Generator[Session, None, None]:
        """
        Get database session with automatic management
        
        Usage:
            with DatabaseSessionManager.get_db() as db:
                customer = db.query(Customer).first()
                customer.name = "New Name"
                # Auto commit on exit
                
        On exception:
            - Automatically rollback
            - Re-raise exception
            
        Returns:
            Session: Database session
        """
        session: Session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    @staticmethod
    def refresh_and_detach(session: Session, obj):
        """
        Refresh object and detach from session
        
        Use this when you need to keep object after session closes
        
        Args:
            session: Database session
            obj: Object to refresh and detach
            
        Returns:
            Detached object
        """
        session.refresh(obj)
        session.expunge(obj)
        return obj
    
    @staticmethod
    @contextmanager
    def get_db_no_commit() -> Generator[Session, None, None]:
        """
        Get database session without auto-commit
        
        Use this when you want manual transaction control
        
        Usage:
            with DatabaseSessionManager.get_db_no_commit() as db:
                customer = db.query(Customer).first()
                customer.name = "New Name"
                db.commit()  # Manual commit
                
        Returns:
            Session: Database session
        """
        session: Session = SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()


# Convenience alias
get_managed_session = DatabaseSessionManager.get_db
