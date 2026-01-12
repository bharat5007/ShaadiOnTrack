from sqlalchemy.orm import Session
from typing import List, Optional, Type, TypeVar, Generic
from fastapi import HTTPException, status
from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """Base class for CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with a SQLAlchemy model.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Model instance or None
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: dict = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of filter conditions
            
        Returns:
            List of model instances
        """
        query = db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, db: Session, filters: dict = None) -> int:
        """
        Count records with optional filters.
        
        Args:
            db: Database session
            filters: Dictionary of filter conditions
            
        Returns:
            Count of records
        """
        query = db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.count()
    
    def create(self, db: Session, obj_in: dict) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Dictionary of object attributes
            
        Returns:
            Created model instance
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: dict
    ) -> ModelType:
        """
        Update an existing record.
        
        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Dictionary of updated attributes
            
        Returns:
            Updated model instance
        """
        for field, value in obj_in.items():
            if value is not None and hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False