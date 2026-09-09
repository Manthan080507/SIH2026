from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

class AnalysisRequest(BaseModel):
    business_type: str
    district: str
    block: str
    category: str
    education: str
    experience_years: int
    total_cost: float
    equity: float
    loan_tenure_years: int
    annual_interest_rate: float
    estimated_monthly_revenue: float
    estimated_monthly_expenses: float

class PDFRequest(BaseModel):
    business_type: str
    district: str
    feasibility_status: str
    executive_summary: str
    financials: Dict[str, Any]
    recommended_actions: List[str]

@app.post("/analyze")
def analyze_business(data: AnalysisRequest):
    principal = data.total_cost - data.equity
    monthly_rate = (data.annual_interest_rate / 100) / 12
    num_payments = data.loan_tenure_years * 12
    
    if monthly_rate > 0:
        emi = (principal * monthly_rate * ((1 + monthly_rate) ** num_payments)) / (((1 + monthly_rate) ** num_payments) - 1)
    else:
        emi = principal / num_payments

    net_monthly_profit = data.estimated_monthly_revenue - data.estimated_monthly_expenses - emi

    if net_monthly_profit > 10000:
        status = "HIGH FEASIBILITY"
        summary = f"The proposed {data.business_type} project in {data.district} demonstrates strong financial viability with healthy monthly margins."
    elif net_monthly_profit > 0:
        status = "MODERATE FEASIBILITY"
        summary = f"The {data.business_type} project is viable, but operational costs should be closely monitored to maintain profitability."
    else:
        status = "LOW FEASIBILITY"
        summary = f"Projected monthly cash flows are tight. Consider reducing initial loan capital or reducing operating costs."

    return {
        "feasibility_status": status,
        "executive_summary": summary,
        "financials": {
            "emi": round(emi, 2),
            "net_monthly_profit": round(net_monthly_profit, 2),
            "loan_amount": round(principal, 2)
        },
        "recommended_actions": [
            f"Apply for regional sector subsidies in {data.district} under {data.category} entrepreneur quotas.",
            "Maintain a digital ledger for operational revenue and expenditure.",
            "Establish working capital reserves prior to scaling operations."
        ]
    }

@app.post("/generate-pdf")
def generate_pdf(data: PDFRequest):
    pdf_content = f"Official Advisory Report\nBusiness: {data.business_type}\nDistrict: {data.district}\nStatus: {data.feasibility_status}\nSummary: {data.executive_summary}".encode('utf-8')
    return Response(content=pdf_content, media_type="application/pdf")