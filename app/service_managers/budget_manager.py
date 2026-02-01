from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Budget, BudgetCategory
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from app.utils import SharedContext
from app.schemas import CreateBudget, CreateBudgetCategories, UpdateBudgetCategory


class BudgetManager:
    @classmethod
    async def create_budget(
        cls, db: AsyncSession, payload: CreateBudget, user: SharedContext
    ):
        user_id = user.user_id
        total_budget = payload.total_budget
        name = payload.name
        budget_spend = 0

        new_budget = Budget(user_id=user_id, name=name, total_budget=total_budget)

        db.add(new_budget)
        await db.commit()
        await db.refresh(new_budget)

        budget_id = new_budget.id

        for categories in payload.categories:
            await cls.create_budget_categories(db, categories, budget_id)
            budget_spend += categories.actual_cost if categories.actual_cost else 0

        new_budget.spent_budget = budget_spend
        await db.commit()
        await db.refresh(Budget)

    @classmethod
    async def create_budget_categories(
        cls, db: AsyncSession, payload: CreateBudgetCategories, budget_id: int
    ):
        name = payload.name
        total_amt = payload.total_amt
        actual_cost = payload.actual_cost
        meta = payload.meta

        new_budget_cat = BudgetCategory(
            name=name,
            total_amt=total_amt,
            actual_cost=actual_cost,
            budget_id=budget_id,
            meta=meta,
        )

        db.add(new_budget_cat)
        await db.commit()
        await db.refresh(new_budget_cat)

    @classmethod
    async def update_budget_categories(
        cls, db: AsyncSession, payload: UpdateBudgetCategory
    ):
        budget_id = payload.budget_id
        category = BudgetCategory(budget_id=budget_id)

        category.total_amt = payload.total_amt
        category.actual_cost = payload.actual_cost
        category.meta = payload.meta

        await db.commit()
        return {"msg": "Budget updated"}

    @classmethod
    async def get_budgets(cls, db: AsyncSession, user: SharedContext):
        user_id = user.user_id

        query = (
            select(Budget)
            .options(selectinload(Budget.budget_categories))
            .filter(Budget.user_id == user_id)
            .order_by(Budget.created_at.desc())
        )

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
                "remaining_budget": budget.total_budget - budget.spent_budget,
                "budget_categories": [
                    {
                        "id": category.id,
                        "name": category.name,
                        "total_amt": category.total_amt,
                        "actual_cost": category.actual_cost,
                        "remaining": category.total_amt - category.actual_cost,
                        "meta": category.meta,
                    }
                    for category in budget.budget_categories
                ],
                "categories_count": len(budget.budget_categories),
            }
            budgets_with_categories.append(budget_dict)

        return budgets_with_categories

    @classmethod
    async def get_budget_by_id(cls, db: AsyncSession, id: int):
        if not id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Budget ID is required"
            )

        query = (
            select(Budget)
            .options(selectinload(Budget.budget_categories))
            .filter(Budget.id == id)
        )

        result = await db.execute(query)
        budget = result.scalar_one_or_none()

        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget with ID {id} not found",
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
                    "updated_at": category.updated_at,
                }
                for category in budget.budget_categories
            ],
            "categories_count": len(budget.budget_categories),
        }

        return budget_dict

    @classmethod
    async def delete_budget(cls, db: AsyncSession, id: int):
        if not id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Budget ID is required"
            )

        # Check if budget exists
        query = select(Budget).filter(Budget.id == id)
        result = await db.execute(query)
        budget = result.scalar_one_or_none()

        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget with ID {id} not found",
            )

        # Delete the budget (cascade will handle related categories)
        await db.delete(budget)
        await db.commit()

        return {"msg": f"Budget with ID {id} deleted successfully"}
