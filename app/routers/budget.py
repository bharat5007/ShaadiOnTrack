from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.service_managers.budget_manager import BudgetManager
from app.utils import require_auth
from app.schemas import CreateBudget, UpdateBudgetCategory

budget = APIRouter(prefix="/budget", tags=["budget-categories"])


@budget.post("/", status_code=status.HTTP_201_CREATED)
@require_auth
async def create_budget(
    request: Request,
    payload: CreateBudget,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    result = await BudgetManager.create_budget(db=db, payload=payload, user=user)
    return result


@budget.get("/", status_code=status.HTTP_201_CREATED)
@require_auth
async def get_budgets(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    result = await BudgetManager.get_budgets(db=db, user=user)
    return result


@budget.get("/{id}", status_code=status.HTTP_200_OK)
async def get_budget_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await BudgetManager.get_budget_by_id(db=db, id=id)
    return result


@budget.put("/", status_code=status.HTTP_200_OK)
async def update_budget(
    payload: UpdateBudgetCategory,
    db: AsyncSession = Depends(get_db),
):
    result = await BudgetManager.update_budget_categories(db=db, payload=payload)
    return result


@budget.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_budget(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await BudgetManager.delete_budget(db=db, id=id)
    return result
