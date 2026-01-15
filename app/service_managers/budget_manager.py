from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Budget, BudgetCategory
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from app.auth import get_user_id


class BudgetManager:
    
    @classmethod
    async def create_budget(cls, db: AsyncSession, payload: dict, user_id: str):
        total_budget = payload.get("budget")
        name = payload.get("name")
        
        new_budget = Budget(
            user_id=user_id,
            name=name,
            total_budget=total_budget   
        )
        
        db.add(new_budget)
        await db.commit()
        await db.refresh(new_budget)
        
        budget_id = new_budget.id
        await cls.update_budget_categories(db, payload, budget_id)
        
        
    @classmethod
    async def update_budget_categories(cls, db: AsyncSession, payload: dict, budget_id: int=None):
        budget_id = budget_id or payload.get("budget_id")
        if not budget_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget ID not passed",
            )
            
        budget_categories = payload.get("budget_categories")
        
        for categories in budget_categories:
            name = categories.get("name")
            stmt = select(BudgetCategory).filter(BudgetCategory.name == name, BudgetCategory.budget_id == budget_id)
            category = await db.execute(stmt)
            
            if not category:
                category = BudgetCategory(
                    budget_id=budget_id,
                    name=name
                )
            
            category.total_cost = categories.get("total_cost")
            category.actual_cost = categories.get("actual_cost",0)
            category.remarks = categories.get("remarks")
            
        await db.commit()
        return {"msg": "Budget updated"}
    
    @classmethod
    async def get_budgets(cls, db: AsyncSession):
        user_id = get_user_id()
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID is required"
            )
        
        query = select(Budget).options(
            selectinload(Budget.budget_categories)
        ).filter(Budget.user_id == user_id).order_by(Budget.created_at.desc())
        
        result = await db.execute(query)
        budgets = result.scalars().all()
        
        budgets_with_categories = []
        for budget in budgets:
            budget_dict = {
                "id": budget.id,
                "user_id": budget.user_id,
                "name": budget.name,
                "total_budget": budget.total_budget,
                "spent_budget": budget.spent_budget,
                "remaining_budget": (budget.total_budget or 0) - (budget.spent_budget or 0),
                "created_at": budget.created_at,
                "updated_at": budget.updated_at,
                "budget_categories": [
                    {
                        "id": category.id,
                        "budget_cat": category.budget_cat,
                        "budget_amt": category.budget_amt,
                        "actual_cost": category.actual_cost,
                        "remaining": category.remaining,
                        "created_at": category.created_at,
                        "updated_at": category.updated_at
                    }
                    for category in budget.budget_categories
                ],
                "categories_count": len(budget.budget_categories)
            }
            budgets_with_categories.append(budget_dict)
        
        return budgets_with_categories
    
    @classmethod
    async def get_budget_by_id(cls, db: AsyncSession, id: int):
        if not id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget ID is required"
            )
        
        query = select(Budget).options(
            selectinload(Budget.budget_categories)
        ).filter(Budget.id == id)
        
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget with ID {id} not found"
            )
        
        budget_dict = {
            "id": budget.id,
            "user_id": budget.user_id,
            "name": budget.name,
            "total_budget": budget.total_budget,
            "spent_budget": budget.spent_budget,
            "remaining_budget": (budget.total_budget or 0) - (budget.spent_budget or 0),
            "created_at": budget.created_at,
            "updated_at": budget.updated_at,
            "budget_categories": [
                {
                    "id": category.id,
                    "budget_cat": category.budget_cat,
                    "budget_amt": category.budget_amt,
                    "actual_cost": category.actual_cost,
                    "remaining": category.remaining,
                    "created_at": category.created_at,
                    "updated_at": category.updated_at
                }
                for category in budget.budget_categories
            ],
            "categories_count": len(budget.budget_categories)
        }
        
        return budget_dict
    
    @classmethod
    async def update_budget(cls, db: AsyncSession, id: int, payload: dict):
        if not id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget ID is required"
            )
        
        # Check if budget exists
        query = select(Budget).filter(Budget.id == id)
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget with ID {id} not found"
            )
        
        # Update budget fields
        if "name" in payload:
            budget.name = payload["name"]
        if "total_budget" in payload:
            budget.total_budget = payload["total_budget"]
        if "spent_budget" in payload:
            budget.spent_budget = payload["spent_budget"]
        
        await db.commit()
        await db.refresh(budget)
        
        # Update budget categories if provided
        if "budget_categories" in payload:
            await cls.update_budget_categories(db, payload, budget_id=id)
        
        return {"msg": "Budget updated successfully", "budget_id": id}
    
    @classmethod
    async def delete_budget(cls, db: AsyncSession, id: int):
        if not id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Budget ID is required"
            )
        
        # Check if budget exists
        query = select(Budget).filter(Budget.id == id)
        result = await db.execute(query)
        budget = result.scalar_one_or_none()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget with ID {id} not found"
            )
        
        # Delete the budget (cascade will handle related categories)
        await db.delete(budget)
        await db.commit()
        
        return {"msg": f"Budget with ID {id} deleted successfully"}