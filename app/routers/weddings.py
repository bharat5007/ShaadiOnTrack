from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_user_id
from app.schemas import (
    WeddingCoreCreate,
    WeddingCoreUpdate,
    WeddingCoreResponse,
    PaginatedResponse
)
from app.crud import wedding_core_crud
from app.models import Budget

router = APIRouter(prefix="/weddings", tags=["weddings"])


@router.post("/", response_model=WeddingCoreResponse, status_code=status.HTTP_201_CREATED)
def create_wedding(
    wedding: WeddingCoreCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    """
    Create a new wedding for the authenticated user.
    
    Args:
        wedding: Wedding creation data
        db: Database session
        user_id: Authenticated user ID
        
    Returns:
        Created wedding
    """
    wedding_data = wedding.model_dump()
    db_wedding = wedding_core_crud.create_for_user(db, user_id, wedding_data)
    return db_wedding


@router.get("/", response_model=List[WeddingCoreResponse])
def list_weddings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    """
    Get all weddings for the authenticated user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        user_id: Authenticated user ID
        
    Returns:
        List of weddings
    """
    weddings = wedding_core_crud.get_by_user(db, user_id, skip, limit)
    return weddings


@router.get("/{wedding_id}", response_model=WeddingCoreResponse)
def get_wedding(
    wedding_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    """
    Get a specific wedding by ID.
    
    Args:
        wedding_id: Wedding ID
        db: Database session
        user_id: Authenticated user ID
        
    Returns:
        Wedding details
        
    Raises:
        HTTPException: If wedding not found or user doesn't have access
    """
    wedding = wedding_core_crud.get(db, wedding_id)
    
    if not wedding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wedding not found"
        )
    
    if wedding.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this wedding"
        )
    
    return wedding


@router.put("/{wedding_id}", response_model=WeddingCoreResponse)
def update_wedding(
    wedding_id: int,
    wedding: WeddingCoreUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    """
    Update a specific wedding.
    
    Args:
        wedding_id: Wedding ID
        wedding: Wedding update data
        db: Database session
        user_id: Authenticated user ID
        
    Returns:
        Updated wedding
        
    Raises:
        HTTPException: If wedding not found or user doesn't have access
    """
    db_wedding = wedding_core_crud.get(db, wedding_id)
    
    if not db_wedding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wedding not found"
        )
    
    if db_wedding.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this wedding"
        )
    
    update_data = wedding.model_dump(exclude_unset=True)
    updated_wedding = wedding_core_crud.update(db, db_wedding, update_data)
    return updated_wedding


@router.delete("/{wedding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wedding(
    wedding_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    """
    Delete a specific wedding.
    
    Args:
        wedding_id: Wedding ID
        db: Database session
        user_id: Authenticated user ID
        
    Raises:
        HTTPException: If wedding not found or user doesn't have access
    """
    db_wedding = wedding_core_crud.get(db, wedding_id)
    
    if not db_wedding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wedding not found"
        )
    
    if db_wedding.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this wedding"
        )
    
    wedding_core_crud.delete(db, wedding_id)
    return None