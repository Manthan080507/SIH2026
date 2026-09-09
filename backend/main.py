from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

app = FastAPI(
    title="Rural Business Advisor API",
    description="Backend service for SIH26091 - AI-Driven Hyper-Local Business Advisory",
    version="0.1.0"
)

# Input models
class FinancialRequest(BaseModel):
    project_cost: float
    own_contribution: float
    annual_interest_rate: float
    tenure_years: int
    monthly_revenue: float
    monthly_expenses: float

class SchemeRequest(BaseModel):
    project_cost: float
    business_type: str
    category: str = "General"

class SynthesisRequest(BaseModel):
    location: str
    business_type: str
    experience_years: int
    financial_summary: dict
    matched_schemes: List[dict]

class PDFReportRequest(BaseModel):
    location: str
    business_type: str
    feasibility_status: str
    executive_summary: str
    recommended_actions: List[str]
    financial_summary: dict

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Rural Business Advisor backend is running!",
        "project_id": "SIH26091"
    }

@app.post("/calculate-financials")
def calculate_financials(data: FinancialRequest):
    loan_amount = max(0.0, data.project_cost - data.own_contribution)
    
    if loan_amount > 0 and data.annual_interest_rate > 0:
        monthly_rate = (data.annual_interest_rate / 100) / 12
        num_months = data.tenure_years * 12
        emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** num_months) / (((1 + monthly_rate) ** num_months) - 1)
        total_repayment = emi * num_months
        total_interest = total_repayment - loan_amount
    else:
        emi = 0.0
        total_repayment = 0.0
        total_interest = 0.0

    net_monthly_profit = data.monthly_revenue - data.monthly_expenses - emi

    return {
        "project_cost": data.project_cost,
        "own_contribution": data.own_contribution,
        "loan_amount": loan_amount,
        "monthly_emi": round(emi, 2),
        "total_interest": round(total_interest, 2),
        "total_repayment": round(total_repayment, 2),
        "monthly_revenue": data.monthly_revenue,
        "monthly_expenses": data.monthly_expenses,
        "net_monthly_profit": round(net_monthly_profit, 2)
    }

@app.post("/recommend-schemes")
def recommend_schemes(data: SchemeRequest):
    recommended = []

    if data.project_cost <= 5000000:
        recommended.append({
            "scheme_name": "PMEGP (Prime Minister's Employment Generation Programme)",
            "subsidy": "25% (Rural General) / 35% (Rural Special)",
            "max_limit": "₹50 Lakhs (Manufacturing) / ₹20 Lakhs (Service)",
            "eligibility_reason": "Project cost is within the allowable PMEGP setup threshold."
        })

    if data.project_cost <= 1000000:
        category_name = "Shishu" if data.project_cost <= 50000 else ("Kishore" if data.project_cost <= 500000 else "Tarun")
        recommended.append({
            "scheme_name": f"PM MUDRA Yojana ({category_name} Category)",
            "subsidy": "Collateral-free loan with interest subvention options",
            "max_limit": "Up to ₹10 Lakhs",
            "eligibility_reason": f"Project cost fits within MUDRA {category_name} collateral-free financing."
        })

    if "Dairy" in data.business_type or "Food" in data.business_type or "Processing" in data.business_type:
        recommended.append({
            "scheme_name": "Agriculture Infrastructure Fund (AIF)",
            "subsidy": "3% Interest Subvention per annum up to ₹2 Crore",
            "max_limit": "₹2 Crores",
            "eligibility_reason": "Post-harvest / agri-processing activity qualifies for AIF interest subvention."
        })

    return {
        "total_matches": len(recommended),
        "schemes": recommended
    }

@app.post("/generate-advisory")
def generate_advisory(data: SynthesisRequest):
    is_profitable = data.financial_summary.get("net_monthly_profit", 0) > 0
    profit_margin = data.financial_summary.get("net_monthly_profit", 0)
    scheme_names = [s["scheme_name"] for s in data.matched_schemes]

    status_label = "HIGH FEASIBILITY" if is_profitable else "NEEDS RESTRUCTURING"

    executive_summary = (
        f"Based on local market conditions in {data.location}, establishing a {data.business_type} "
        f"project shows {status_label}. The projected net monthly profit is Rs. {profit_margin:,.2f} "
        f"after accounting for operational expenses and loan EMI repayments."
    )

    recommended_actions = [
        f"Leverage {scheme_names[0]} for primary capital backing and subsidy benefits." if scheme_names else "Explore local cooperative credit societies for low-interest financing.",
        "Establish local supply links within a 15–20 km radius to keep logistics costs low.",
        f"Utilize your {data.experience_years} year(s) of practical experience to streamline early operational risks."
    ]

    return {
        "feasibility_status": status_label,
        "executive_summary": executive_summary,
        "recommended_actions": recommended_actions
    }

@app.post("/generate-pdf")
def generate_pdf(data: PDFReportRequest):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, spaceAfter=12)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=14, spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=6)

    elements = []
    elements.append(Paragraph("Rural Business Advisory Report", title_style))
    elements.append(Paragraph(f"<b>SIH Project ID:</b> SIH26091 | <b>Location:</b> {data.location}", body_style))
    elements.append(Paragraph(f"<b>Proposed Business:</b> {data.business_type}", body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("1. Executive Feasibility Summary", heading_style))
    elements.append(Paragraph(f"<b>Status:</b> {data.feasibility_status}", body_style))
    elements.append(Paragraph(data.executive_summary, body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. Financial Breakdown", heading_style))
    fin = data.financial_summary
    elements.append(Paragraph(f"• Total Project Cost: Rs. {fin.get('project_cost', 0):,.2f}", body_style))
    elements.append(Paragraph(f"• Required Loan Amount: Rs. {fin.get('loan_amount', 0):,.2f}", body_style))
    elements.append(Paragraph(f"• Monthly EMI: Rs. {fin.get('monthly_emi', 0):,.2f}", body_style))
    elements.append(Paragraph(f"• Estimated Monthly Profit: Rs. {fin.get('net_monthly_profit', 0):,.2f}", body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("3. Recommended Action Plan", heading_style))
    for idx, act in enumerate(data.recommended_actions, 1):
        elements.append(Paragraph(f"{idx}. {act}", body_style))

    doc.build(elements)
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=business_advisory_report.pdf"}
    )