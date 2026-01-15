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
    db: Session = Depends(get_db),
):

    result = await BudgetManager.get_budgets(db=db)
    return result


@budget.get("/<id>", status_code=status.HTTP_200_OK)
async def get_budget_by_id(
    id: int,
    db: Session = Depends(get_db),
):

    result = await BudgetManager.get_budget_by_id(db=db, id=id)
    return result


@budget.put("/<id>", status_code=status.HTTP_200_OK)
async def update_budget(
    id: int,
    payload: dict,
    db: Session = Depends(get_db),
):

    result = await BudgetManager.update_budget(db=db, id=id, payload=payload)
    return result


@budget.delete("/<id>", status_code=status.HTTP_200_OK)
async def delete_budget(
    id: int,
    db: Session = Depends(get_db),
):

    result = await BudgetManager.delete_budget(db=db, id=id)
    return result