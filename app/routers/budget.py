from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.service_managers.budget_manager import BudgetManager
from app.utils import require_auth, optional_auth
from app.schemas import CreateBudget, UpdateBudget

budget = APIRouter(prefix="/budget", tags=["budget-categories"])


@budget.post("/", status_code=status.HTTP_200_OK)
@require_auth
async def create_budget(
    request: Request,
    payload: CreateBudget,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    result = await BudgetManager.create_budget(db=db, payload=payload, user=user)
    return result


@budget.get("/", status_code=status.HTTP_200_OK)
@optional_auth(default_return=[])
async def get_budgets(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    result = await BudgetManager.get_budgets(db=db, user=user)
    return result


@budget.put("/{budget_id}", status_code=status.HTTP_200_OK)
@require_auth
async def update_budget_by_id(
    request: Request,
    budget_id: int,
    payload: UpdateBudget,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    result = await BudgetManager.update_budget_by_id(
        db=db, payload=payload, id=budget_id, user=user
    )
    return result


@budget.get("/{id}", status_code=status.HTTP_200_OK)
async def get_budget_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await BudgetManager.get_budget_by_id(db=db, id=id)
    return result


@budget.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_budget(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await BudgetManager.delete_budget(db=db, id=id)
    return result
