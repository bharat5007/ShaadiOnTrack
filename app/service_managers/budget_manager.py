from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Budget, BudgetCategory
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload


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
    async def get_budgets(cls, db: AsyncSession, user_id: str):
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
                        "remaining": category.reaming,
                        "created_at": category.created_at,
                        "updated_at": category.updated_at
                    }
                    for category in budget.budget_categories
                ],
                "categories_count": len(budget.budget_categories)
            }
            budgets_with_categories.append(budget_dict)
        
        return budgets_with_categories