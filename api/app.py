from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from system.system import System
from system.database.database import DataBase

app = FastAPI(
    title='Personal Budget Tracker API',
    description="Some API for managing money",
    version="0.0.1"
)

database = DataBase(file_path="/Users/eduard.balamatiuc/projects/python-template-project/memory/database_v1.json")


class BudgetCreate(BaseModel):
    name: str
    description: str

class Budget(BaseModel):
    name: str
    description: str
    current_amount: int
    action_history: List[str]
    goal: Optional[int] = None

class MoneyOperatoin(BaseModel):
    budget_name: str
    amount: int

class ExpenseCreate(BaseModel):
    budget_name: str
    amount: int
    category: str

class BudgetGoal(BaseModel):
    budget_name: str
    amount: int

class StatsResponse(BaseModel):
    budget_name: str
    current_amount: int
    goal: Optional[int] = None
    goal_percentage: Optional[float] = None
    action_history: List[str]

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Hello from the Budget API"}


@app.get("/budgets", response_model=List[Budget], tags=["Budgets"])
def get_all_budgets():
    """Get all budgets"""
    return database.database["budgets"]


@app.post("/budgets", response_model=Budget, tags=["Budgets"])
def create_budget(budget: BudgetCreate):
    """Create a new budget"""
    for existing_budget in database.database["budgets"]:
        if existing_budget["name"] == budget.name:
            raise HTTPException(
                status_code=400,
                detail="Budget with this name already exists"
            )
        
    new_budget = {
        "name": budget.name,
        "description": budget.description,
        "current_amount": 0,
        "action_history": [],
        "goal": None,
    }

    database.database["budgets"].append(new_budget)
    database.save_database_state()

    return new_budget


@app.get("/budgets/{budget_name}", response_model=Budget, tags=["Budgets"])
def get_budget(
    budget_name: str
):
    """Get a budget by name"""
    for budget in database.database["budgets"]:
        if budget["name"] == budget_name:
            return budget
    raise HTTPException(status_code=404, detail="Budget Not Found")


@app.post("/budgets/{budget_name}/add-money", response_model=Budget, tags=["Transactions"])
def add_money(budget_name: str, operation: MoneyOperatoin):
    """Create a new budget"""
    if operation.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    

    for existing_budget in database.database["budgets"]:
        if existing_budget["name"] == budget_name:
            existing_budget["current_amount"] += operation.amount
            existing_budget["action_history"].append(f"+{operation.amount}")
            database.save_database_state()
            return existing_budget
        

    raise HTTPException(status_code=404, detail="Budget not found")

@app.post("/budgets/{budget_name}/add-expense", response_model=Budget, tags=["Transactions"])
def add_expense(budget_name: str, expense: ExpenseCreate):
    """Create a new expense"""
    if expense.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    

    for existing_budget in database.database["budgets"]:
        if existing_budget["name"] == budget_name:
            existing_budget["current_amount"] -= expense.amount
            existing_budget["action_history"].append(f"-{expense.amount} for {expense.category}")
            database.save_database_state()
            return existing_budget
        

    raise HTTPException(status_code=404, detail="Budget not found")


@app.post("/budgets/{budget_name}/set-goal", response_model=Budget, tags=["Goals"])
def set_goal(budget_name: str, goal: BudgetGoal):
    """Create a new goal"""
    if goal.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    
    for existing_budget in database.database["budgets"]:
        if existing_budget["name"] == budget_name:
            existing_budget["goal"] = goal.amount
            database.save_database_state()
            return existing_budget

    raise HTTPException(status_code=404, detail="Budget not found")

@app.get("/budgets/{budget_name}/stats", response_model=StatsResponse, tags=["Stats"])
def get_stats(budget_name: str):
    """Get statistics on the budget"""    

    for existing_budget in database.database["budgets"]:
        if existing_budget["name"] == budget_name:
            goal_percentage = None
            if existing_budget["goal"] is not None and existing_budget["goal"] > 0:
                goal_percentage = (existing_budget["current_amount"] * 100) / existing_budget["goal"]
            
            return {
                "budget_name": existing_budget["name"],
                "current_amount": existing_budget["current_amount"],
                "goal": existing_budget["goal"],
                "goal_percentage": goal_percentage,
                "action_history": existing_budget["action_history"],
            }
        

    raise HTTPException(status_code=404, detail="Budget not found")
