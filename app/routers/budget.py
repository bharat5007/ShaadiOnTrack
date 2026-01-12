from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_user_id
from app.service_managers.budget_manager import BudgetManager

budget = APIRouter(prefix="/budget", tags=["budget-categories"])

@budget.post("/", status_code=status.HTTP_201_CREATED)
async def create_budget(
    payload: dict,
    db: Session = Depends(get_db),
):

    result = await BudgetManager.create_budget(db=db, payload=payload)
    return result


@budget.get("/", status_code=status.HTTP_201_CREATED)
async def get_budgets(
    payload: dict,
    db: Session = Depends(get_db),
):

    result = await BudgetManager.get_budgets(db=db, payload=payload)
    return result