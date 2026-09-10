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
    scheme_type: str = "pm_mudra"

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
    master_pool = [
        # --- Agriculture & Allied ---
        {
            "category": "Agriculture & Allied",
            "business_type": "Smart Dairy & Automated Milk Collection Center",
            "risk_to_profit_ratio": "Low Risk / High Daily Demand",
            "best_scheme": "National Livestock Mission (NLM)",
            "nodal_agency": "Ministry of Fisheries, Animal Husbandry & Dairying",
            "scheme_subsidy": "Up to 50% capital subsidy",
            "estimated_setup_cost": 220000,
            "skill_requirement": "Unskilled / Beginner",
            "active_units": f"140+ active hubs in {req.district}, {req.state}",
            "regional_growth": "+14.2% YoY local consumption",
            "competitor_health": "Stable cooperative demand",
            "pros": ["Daily cash flow", "High local demand", "Government feed support"],
            "cons": ["Requires continuous cold chain", "Perishable goods management"]
        },
        {
            "category": "Agriculture & Allied",
            "business_type": "Organic Vermicomposting & Bio-Fertilizer Production",
            "risk_to_profit_ratio": "Low Risk / Steady Margin",
            "best_scheme": "Paramparagat Krishi Vikas Yojana (PKVY)",
            "nodal_agency": "Ministry of Agriculture & Farmers Welfare",
            "scheme_subsidy": "₹50,000 per hectare cluster support",
            "estimated_setup_cost": 110000,
            "skill_requirement": "Unskilled / Beginner",
            "active_units": f"65+ local organic farms in {req.district}",
            "regional_growth": "+18.5% shift towards chemical-free farming",
            "competitor_health": "Low corporate competition",
            "pros": ["Low initial investment", "High availability of raw farm waste"],
            "cons": ["Seasonal preparation cycles", "Bulk storage required"]
        },
        {
            "category": "Agriculture & Allied",
            "business_type": "Solar-Powered Cold Storage & Horticulture Aggregation",
            "risk_to_profit_ratio": "Moderate Risk / High Value",
            "best_scheme": "Agriculture Infrastructure Fund (AIF)",
            "nodal_agency": "Ministry of Agriculture",
            "scheme_subsidy": "Interest subvention of 3% up to ₹2 Crore",
            "estimated_setup_cost": 290000,
            "skill_requirement": "Intermediate / Skilled",
            "active_units": f"25+ storage units across {req.state}",
            "regional_growth": "+22.0% horticultural output",
            "competitor_health": "High demand during peak harvest",
            "pros": ["Prevents crop wastage", "Strong institutional credit backing"],
            "cons": ["Higher upfront capital requirement", "Power backup reliance"]
        },

        # --- Manufacturing & Handloom ---
        {
            "category": "Manufacturing & Handloom",
            "business_type": "Handloom Weaving & Traditional Handicrafts Studio",
            "risk_to_profit_ratio": "Moderate Risk / High Art Value",
            "best_scheme": "National Handloom Development Programme",
            "nodal_agency": "Ministry of Textiles",
            "scheme_subsidy": "Mudra Loan support with 3% interest subvention",
            "estimated_setup_cost": 175000,
            "skill_requirement": "Intermediate / Skilled",
            "active_units": f"90+ artisan clusters in {req.district}",
            "regional_growth": "+9.8% e-commerce export demand",
            "competitor_health": "Strong cultural heritage demand",
            "pros": ["GI tag branding leverage", "High export margin potential"],
            "cons": ["High manual labor dependency", "Changing design trends"]
        },
        {
            "category": "Manufacturing & Handloom",
            "business_type": "Eco-Friendly Bamboo & Jute Craft Manufacturing Unit",
            "risk_to_profit_ratio": "Low Risk / Sustainable Sector",
            "best_scheme": "National Bamboo Mission (NBM)",
            "nodal_agency": "Ministry of Agriculture & Farmers Welfare",
            "scheme_subsidy": "Up to 50% assistance for plantation & processing",
            "estimated_setup_cost": 140000,
            "skill_requirement": "Unskilled / Beginner",
            "active_units": f"40+ workshops in {req.district}",
            "regional_growth": "+27.5% plastic ban substitution",
            "competitor_health": "Growing eco-conscious consumer base",
            "pros": ["Abundant local raw materials", "Strong government push against plastics"],
            "cons": ["Requires specialized shaping tools", "Skill training needed"]
        },

        # --- Retail & Services ---
        {
            "category": "Retail & Services",
            "business_type": "Digital Common Service & Rural E-Commerce Hub",
            "risk_to_profit_ratio": "Low Risk / Service Oriented",
            "best_scheme": "PM Vishwakarma Scheme / CSC Scheme",
            "nodal_agency": "Ministry of Electronics and IT",
            "scheme_subsidy": "Toolkit incentive up to ₹15,000 + Low interest credit",
            "estimated_setup_cost": 90000,
            "skill_requirement": "Unskilled / Beginner",
            "active_units": f"210+ digital kiosks in {req.district}",
            "regional_growth": f"+25.4% digital service adoption in {req.state}",
            "competitor_health": "Essential utility requirement",
            "pros": ["Multiple transaction revenue streams", "Constant daily footfall"],
            "cons": ["Internet connectivity dependency", "Local kiosk competition"]
        },
        {
            "category": "Retail & Services",
            "business_type": "Solar Panel Maintenance & Rural Energy Service Station",
            "risk_to_profit_ratio": "Low Risk / High Future Demand",
            "best_scheme": "PM-KUSUM Scheme",
            "nodal_agency": "Ministry of New and Renewable Energy (MNRE)",
            "scheme_subsidy": "Up to 30% central financial assistance",
            "estimated_setup_cost": 150000,
            "skill_requirement": "Intermediate / Skilled",
            "active_units": f"35+ green energy providers in {req.state}",
            "regional_growth": "+40.0% solar pump installations",
            "competitor_health": "Very low local technical competition",
            "pros": ["Rapidly expanding clean energy market", "High maintenance service margins"],
            "cons": ["Requires technical training for staff", "Initial tool investment"]
        },

        # --- Food Processing & Dairy ---
        {
            "category": "Food Processing & Dairy",
            "business_type": "Millet Processing & Value-Added Packaging Unit",
            "risk_to_profit_ratio": "Low Risk / Trending Health Sector",
            "best_scheme": "PM Formalization of Micro Food Processing Enterprises (PMFME)",
            "nodal_agency": "Ministry of Food Processing Industries",
            "scheme_subsidy": "35% credit-linked subsidy up to ₹10 Lakh",
            "estimated_setup_cost": 260000,
            "skill_requirement": "Unskilled / Beginner",
            "active_units": f"45+ modern mills in {req.district}",
            "regional_growth": "+31.0% superfood & millet boom",
            "competitor_health": "Strong backing from national nutrition drives",
            "pros": ["High government backing", "Long shelf-life packaged goods"],
            "cons": ["FSSAI compliance licensing required", "Machinery maintenance cost"]
        },
        {
            "category": "Food Processing & Dairy",
            "business_type": "Rural Fruit Pulp Extraction & Pickle Micro-Enterprise",
            "risk_to_profit_ratio": "Low Risk / High Seasonal Margin",
            "best_scheme": "Mission Organic Value Chain Development (MOVCDNER)",
            "nodal_agency": "Ministry of Food Processing Industries",
            "scheme_subsidy": "Up to 50% assistance for value addition units",
            "estimated_setup_cost": 130000,
            "skill_requirement": "Unskilled / Beginner",
            "active_units": f"55+ local units in {req.district}",
            "regional_growth": "+16.8% processed food demand",
            "competitor_health": "Steady traditional market demand",
            "pros": ["Utilizes abundant regional seasonal fruits", "Low waste output"],
            "cons": ["Seasonal crop availability variations", "Glass jar packaging care"]
        }
    ]

    # 1. Filter by category
    filtered = [b for b in master_pool if req.category == "All Categories" or b["category"] == req.category]
    
    # 2. Filter by maximum capital investment limit
    filtered = [b for b in filtered if b["estimated_setup_cost"] <= req.max_capital]

    # 3. Adaptively filter/prioritize by skill level if user selected beginner/unskilled
    if req.skill_level == "Unskilled / Beginner":
        beginner_filtered = [b for b in filtered if b.get("skill_requirement") == "Unskilled / Beginner"]
        if beginner_filtered:
            filtered = beginner_filtered

    if not filtered:
        filtered = master_pool[:2]

    return {
        "region_context": f"📍 Intelligence Report for {req.district}, {req.state} | Skill: {req.skill_level} | Capital Limit: ₹{req.max_capital:,.0f}",
        "sectors": filtered
    }

@app.post("/api/analyze-financials")
def analyze_financials(req: FinancialRequest):
    loan_required = max(0.0, req.project_cost - req.own_contribution)
    
    scheme_rates = {
        "pm_mudra": 8.5,
        "stand_up_india": 7.5,
        "pmegp": 8.0,
        "pmfme": 8.25,
        "swarnima": 6.0,
        "general_loan": 10.5
    }
    
    interest_rate = scheme_rates.get(req.scheme_type, 8.5)
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
        "annual_expenses": req.annual_expenses,
        "scheme_type": req.scheme_type
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
    if "loan" in msg or "mudra" in msg or "money" in msg or "credit" in msg:
        reply = "For micro-enterprises, government schemes like PM Mudra Yojana or NBCFDC concessional loans offer low-interest financing ranging from ₹50,000 to ₹10 Lakhs with easy repayment tenures."
    elif "subsidy" in msg or "scheme" in msg or "fund" in msg:
        reply = "Central and state schemes provide capital subsidies between 25% to 50% depending on the sector (such as food processing, dairy, or handlooms) and your district category."
    elif "document" in msg or "apply" in msg or "process" in msg:
        reply = "Standard documentation required includes your Aadhaar Card, PAN Card, passport-size photos, bank statement for the last 6 months, project report, and proof of business address."
    elif "business" in msg or "idea" in msg or "suggest" in msg or "start" in msg or "open" in msg:
        reply = f"Great initiative, {req.username}! To find the best options, head over to **Tab 1 (AI Sector & Scheme Intelligence)** where you can enter your state, district, and capital limit to get tailored local business recommendations instantly."
    elif "hello" in msg or "hi" in msg or "hey" in msg or "namaste" in msg:
        reply = f"Namaste {req.username}! I am your GraminSarthi AI guide. How can I assist you with your business plans or government schemes today?"
    else:
        reply = f"That's a great question regarding '{req.message}'. You can explore custom regional business ideas in Tab 1, check your loan cash-flow viability in Tab 2, or ask me about loans, subsidies, and application paperwork!"
    return {"reply": reply}