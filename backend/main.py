from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI(title="GraminSarthi-AI Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            project_cost REAL,
            own_contribution REAL,
            loan_required REAL,
            interest_rate REAL,
            monthly_emi REAL,
            annual_revenue REAL,
            annual_expenses REAL,
            dscr REAL,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class UserAuth(BaseModel):
    username: str
    password: str
    email: str = None

class RecommendationRequest(BaseModel):
    state: str
    district: str
    max_capital: float
    skill_level: str
    category: str = "All Categories"

class FinancialRequest(BaseModel):
    project_cost: float
    own_contribution: float
    annual_revenue: float
    annual_expenses: float
    scheme_type: str = "general"

class RecordSaveRequest(BaseModel):
    username: str
    project_cost: float
    own_contribution: float
    loan_required: float
    interest_rate: float
    monthly_emi: float
    annual_revenue: float
    annual_expenses: float
    dscr: float
    status: str

class ChatRequest(BaseModel):
    message: str
    username: str

@app.post("/api/register")
def register(user: UserAuth):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                       (user.username, user.email, user.password))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()
    return {"message": "User registered successfully"}

@app.post("/api/login")
def login(user: UserAuth):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user.username, user.password))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful", "username": user.username}

@app.post("/api/recommend-all-businesses")
def recommend_businesses(req: RecommendationRequest):
    # Expanded AI generation database based on category & capital limits
    master_pool = [
        {
            "category": "Agriculture & Allied",
            "business_type": "Smart Dairy & Milk Collection Center",
            "risk_to_profit_ratio": "Low Risk / High Demand",
            "best_scheme": "National Livestock Mission (NLM)",
            "nodal_agency": "Ministry of Fisheries, Animal Husbandry & Dairying",
            "scheme_subsidy": "Up to 50% capital subsidy",
            "estimated_setup_cost": 250000,
            "active_units": f"140+ active hubs in {req.district}",
            "regional_growth": "+14.2% YoY growth",
            "competitor_health": "Stable cooperative demand",
            "pros": ["Daily cash flow", "High local consumption", "Government feed support"],
            "cons": ["Requires cold chain maintenance", "Perishable commodity"]
        },
        {
            "category": "Agriculture & Allied",
            "business_type": "Organic Vermicomposting & Bio-Fertilizer Unit",
            "risk_to_profit_ratio": "Low Risk / Steady Margin",
            "best_scheme": "Paramparagat Krishi Vikas Yojana (PKVY)",
            "nodal_agency": "Ministry of Agriculture & Farmers Welfare",
            "scheme_subsidy": "₹50,000 per hectare cluster support",
            "estimated_setup_cost": 120000,
            "active_units": f"65+ local organic farms in {req.district}",
            "regional_growth": "+18.5% organic shift",
            "competitor_health": "Low corporate competition",
            "pros": ["Low initial investment", "Eco-friendly raw material supply"],
            "cons": ["Seasonal preparation cycle", "Bulk storage needed"]
        },
        {
            "category": "Manufacturing & Handloom",
            "business_type": "Handloom Weaving & Traditional Handicrafts Studio",
            "risk_to_profit_ratio": "Moderate Risk / High Art Value",
            "best_scheme": "National Handloom Development Programme",
            "nodal_agency": "Ministry of Textiles",
            "scheme_subsidy": "Mudra Loan support with 3% interest subvention",
            "estimated_setup_cost": 180000,
            "active_units": f"90+ artisan clusters in {req.district}",
            "regional_growth": "+9.8% e-commerce export demand",
            "competitor_health": "Strong cultural heritage demand",
            "pros": ["GI tag branding leverage", "High export margin potential"],
            "cons": ["High manual labor dependency", "Design trend shifts"]
        },
        {
            "category": "Retail & Services",
            "business_type": "Digital Common Service & Rural E-Commerce Hub",
            "risk_to_profit_ratio": "Low Risk / Service Oriented",
            "best_scheme": "PM Vishwakarma Scheme / CSC Scheme",
            "nodal_agency": "Ministry of Electronics and IT",
            "scheme_subsidy": "Toolkit incentive up to ₹15,000 + Low interest credit",
            "estimated_setup_cost": 95000,
            "active_units": f"210+ digital kiosks in {req.district}",
            "regional_growth": "+25.4% digital adoption",
            "competitor_health": "Essential utility requirement",
            "pros": ["Multiple revenue streams", "Constant footfall"],
            "cons": ["Internet dependency", "Local service competition"]
        },
        {
            "category": "Food Processing & Dairy",
            "business_type": "Millet Processing & Packaging Micro-Enterprise",
            "risk_to_profit_ratio": "Low Risk / Trending Sector",
            "best_scheme": "PM Formalization of Micro Food Processing Enterprises (PMFME)",
            "nodal_agency": "Ministry of Food Processing Industries",
            "scheme_subsidy": "35% credit-linked subsidy up to ₹10 Lakh",
            "estimated_setup_cost": 270000,
            "active_units": f"45+ modern mills in {req.district}",
            "regional_growth": "+31.0% health food boom",
            "competitor_health": "Rising consumer health preference",
            "pros": ["High government backing for millets", "Long shelf life products"],
            "cons": ["Machinery upkeep costs", "FSSAI compliance compliance required"]
        }
    ]

    # Filter by category if selected
    filtered = [b for b in master_pool if req.category == "All Categories" or b["category"] == req.category]
    
    # Filter by capital constraint
    filtered = [b for b in filtered if b["estimated_setup_cost"] <= req.max_capital]

    if not filtered:
        # Fallback if strict capital filter yields 0
        filtered = master_pool[:2]

    return {
        "region_context": f"📍 AI Market Intelligence Report for {req.district}, {req.state} | Skill Target: {req.skill_level}",
        "sectors": filtered
    }

@app.post("/api/analyze-financials")
def analyze_financials(req: FinancialRequest):
    loan_required = max(0.0, req.project_cost - req.own_contribution)
    interest_rate = 6.0 if req.scheme_type == "swarnima" else 9.0
    monthly_interest = (interest_rate / 100) / 12
    tenure_months = 60
    
    if loan_required > 0:
        monthly_emi = (loan_required * monthly_interest * (1 + monthly_interest)**tenure_months) / \
                      ((1 + monthly_interest)**tenure_months - 1)
    else:
        monthly_emi = 0.0

    annual_debt_service = monthly_emi * 12
    net_operating_income = req.annual_revenue - req.annual_expenses
    dscr = round(net_operating_income / annual_debt_service, 2) if annual_debt_service > 0 else 9.99
    
    status = "Highly Feasible & Bankable" if dscr >= 1.5 else ("Moderately Feasible" if dscr >= 1.1 else "High Financial Risk")

    return {
        "loan_required": loan_required,
        "interest_rate": interest_rate,
        "monthly_emi": round(monthly_emi, 2),
        "dscr": dscr,
        "status": status,
        "own_contribution": req.own_contribution,
        "annual_revenue": req.annual_revenue,
        "annual_expenses": req.annual_expenses
    }

@app.post("/api/save-record")
def save_record(rec: RecordSaveRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO records (username, project_cost, own_contribution, loan_required, interest_rate, monthly_emi, annual_revenue, annual_expenses, dscr, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (rec.username, rec.project_cost, rec.own_contribution, rec.loan_required, rec.interest_rate, rec.monthly_emi, rec.annual_revenue, rec.annual_expenses, rec.dscr, rec.status))
    conn.commit()
    conn.close()
    return {"message": "Record saved successfully"}

@app.get("/api/records/{username}")
def get_records(username: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT project_cost, own_contribution, loan_required, interest_rate, monthly_emi, annual_revenue, annual_expenses, dscr, status FROM records WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    
    records = []
    for r in rows:
        records.append({
            "Project Cost": r[0],
            "Own Contribution": r[1],
            "Loan Required": r[2],
            "Interest Rate (%)": r[3],
            "Monthly EMI": r[4],
            "Annual Revenue": r[5],
            "Annual Expenses": r[6],
            "DSCR": r[7],
            "Status": r[8]
        })
    return records

@app.post("/api/ai-chat")
def ai_chat(req: ChatRequest):
    msg = req.message.lower()
    if "loan" in msg or "mudra" in msg or "money" in msg:
        reply = "For micro-enterprises, government schemes like PM Mudra Yojana or NBCFDC concessional loans offer low-interest financing ranging from ₹50,000 to ₹10 Lakhs with easy repayment tenures."
    elif "subsidy" in msg or "scheme" in msg:
        reply = "Central and state schemes provide capital subsidies between 25% to 50% depending on the sector (such as food processing or handlooms) and your district category."
    elif "document" in msg or "apply" in msg:
        reply = "Standard documentation required includes your Aadhaar Card, PAN Card, passport-size photos, bank statement for the last 6 months, project report, and proof of business address."
    else:
        reply = f"Hello {req.username}! As your GraminSarthi AI Advisor, I recommend exploring high-growth sectors in Tab 1 and verifying your cash flow using Tab 2's DSCR financial calculator."
    return {"reply": reply}