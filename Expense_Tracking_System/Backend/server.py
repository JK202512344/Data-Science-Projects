from fastapi import FastAPI,HTTPException
from datetime import date
import db_helper
from typing import List
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime

class Expense(BaseModel):
    #expense_date: date
    amount: float
    category: str
    notes: str
class DateRange(BaseModel):
    start_date: date
    end_date: date

app = FastAPI()

@app.get("/expenses/{expense_date}",response_model=List[Expense])

def expenses(expense_date: date):
    exp=db_helper.fetch_day_data(expense_date)
    
    return exp 

@app.post("/expenses/{expense_date}")

def insert_or_uppdate_expense(expense_date:date,expenses:List[Expense]):
    db_helper.delete_expense(expense_date)
    for expense in expenses:
        db_helper.insert_expense(expense_date,expense.amount,expense.category,expense.notes)

    return {"message":"Expense updated succesfully"}

@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expense(date_range.start_date, date_range.end_date)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database.")

    total = sum([row['total'] for row in data])

    breakdown = {}
    for row in data:
        percentage = (row['total']/total)*100 if total != 0 else 0
        breakdown[row['category']] = {
            "total": row['total'],
            "percentage": percentage
        }

    return breakdown

@app.get("/analyticsbymonth/")
def get_analytics():
    monthly_summary = db_helper.fetch_monthly_expense_summary()
    if monthly_summary is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve monthly expense summary from the database.")

    return monthly_summary
