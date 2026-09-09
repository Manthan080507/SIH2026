from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="GraminSarthi-AI Backend")

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            project_cost REAL,
            own_contribution REAL,
            loan_required REAL,
            interest_rate REAL,
            monthly_emi REAL,
            dscr REAL,
            status TEXT,
            annual_revenue REAL,
            annual_expenses REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

class AuthModel(BaseModel):
    username: str
    password: str
    email: str = None

class RecommendationRequest(BaseModel):
    state: str
    district: str
    max_capital: float
    skill_level: str

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
    dscr: float
    status: str
    annual_revenue: float
    annual_expenses: float

class ChatRequest(BaseModel):
    message: str
    username: str

@app.post("/api/register")
def register(data: AuthModel):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (data.username, data.email, data.password))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists.")
    finally:
        conn.close()
    return {"message": "Registered successfully"}

@app.post("/api/login")
def login(data: AuthModel):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (data.username, data.password))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "username": data.username}

@app.post("/api/recommend-all-businesses")
def recommend_all_businesses(data: RecommendationRequest):
    sectors = [
        {
            "business_type": "Dairy & Animal Husbandry",
            "risk_to_profit_ratio": "1:2.8 (Low Risk)",
            "best_scheme": "National Livestock Mission (NLM) / Dairy Entrepreneurship Development Scheme",
            "nodal_agency": "Ministry of Fisheries, Animal Husbandry & Dairying",
            "scheme_subsidy": "Up to 25% to 35% capital subsidy through NABARD",
            "estimated_setup_cost": f"₹{min(data.max_capital, 250000):,.0f}",
            "active_units": f"1,420 units active in {data.district}",
            "regional_growth": "+14.2% YoY Demand Surge",
            "competitor_health": "Stable, high local daily consumer demand",
            "pros": ["High daily recurring cash flow", "Constant local demand for milk & dairy products", "Strong central backing & fodder support"],
            "cons": ["Daily perishable handling required", "Veterinary healthcare dependency", "Fodder price fluctuations"]
        },
        {
            "business_type": "Retail & Grocery Micro-Store",
            "risk_to_profit_ratio": "1:2.2 (Low Risk)",
            "best_scheme": "PMEGP (Prime Minister's Employment Generation Programme)",
            "nodal_agency": "KVIC (Khadi and Village Industries Commission)",
            "scheme_subsidy": "15% to 35% margin money subsidy",
            "estimated_setup_cost": f"₹{min(data.max_capital, 200000):,.0f}",
            "active_units": f"3,850 retail hubs in {data.district}",
            "regional_growth": "+9.8% Annual Retail Expansion",
            "competitor_health": "High competition; neighborhood loyalty is key",
            "pros": ["Essential consumer goods ensure steady footfall", "Easy supplier chains through local distributors", "Scalable into wholesale or delivery services"],
            "cons": ["Working capital locked in inventory", "Low profit margins on branded FMCG goods", "Local credit management risk (Udhar)"]
        },
        {
            "business_type": "Handloom & Traditional Handicrafts",
            "risk_to_profit_ratio": "1:3.1 (Medium Risk)",
            "best_scheme": "National Handloom Development Programme (NHDP) & Mudra Loan",
            "nodal_agency": "Ministry of Textiles",
            "scheme_subsidy": "Margin money assistance up to ₹10,000 & subsidized tool kits",
            "estimated_setup_cost": f"₹{min(data.max_capital, 150000):,.0f}",
            "active_units": f"620 artisan units in {data.district}",
            "regional_growth": "+18.5% Growth via e-Commerce & GI Tagging",
            "competitor_health": "Niche market with high export potential",
            "pros": ["High profit margins on authentic hand-crafted goods", "Government e-Marketplace (GeM) & export linkages", "Preserves traditional artisan heritage"],
            "cons": ["Seasonal sales cycles", "Long production cycles per unit", "Requires active digital marketing exposure"]
        }
    ]
    return {
        "region_context": f"Multi-sector macroeconomic assessment for {data.district}, {data.state} (Skill Level: {data.skill_level}).",
        "sectors": [s for s in sectors if float(s["estimated_setup_cost"].replace("₹","").replace(",","")) <= data.max_capital + 100000]
    }

@app.post("/api/analyze-financials")
def analyze_financials(data: FinancialRequest):
    loan_required = max(0, data.project_cost - data.own_contribution)
    interest_rate = 6.0 if data.scheme_type == "swarnima" else 8.5
    monthly_interest = (interest_rate / 100) / 12
    tenure_months = 60
    
    if monthly_interest > 0:
        monthly_emi = (loan_required * monthly_interest * (1 + monthly_interest)**tenure_months) / ((1 + monthly_interest)**tenure_months - 1)
    else:
        monthly_emi = loan_required / tenure_months if tenure_months > 0 else 0

    annual_net_income = data.annual_revenue - data.annual_expenses
    annual_debt_service = monthly_emi * 12
    dscr = round(annual_net_income / annual_debt_service, 2) if annual_debt_service > 0 else 9.99

    status = "Approved — Financially Viable & Healthy DSCR" if dscr >= 1.5 else ("Conditional Approval — Moderate Coverage" if dscr >= 1.1 else "Needs Capital Restructuring — Low DSCR")

    return {
        "loan_required": loan_required,
        "interest_rate": interest_rate,
        "monthly_emi": round(monthly_emi, 2),
        "dscr": dscr,
        "status": status
    }

@app.post("/api/save-record")
def save_record(data: RecordSaveRequest):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO saved_records (username, project_cost, own_contribution, loan_required, interest_rate, monthly_emi, dscr, status, annual_revenue, annual_expenses)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data.username, data.project_cost, data.own_contribution, data.loan_required, data.interest_rate, data.monthly_emi, data.dscr, data.status, data.annual_revenue, data.annual_expenses))
    conn.commit()
    conn.close()
    return {"message": "Record saved successfully"}

@app.get("/api/records/{username}")
def get_records(username: str):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_records WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/ai-chat")
def ai_chat(data: ChatRequest):
    msg = data.message.lower()
    if "loan" in msg or "mudra" in msg:
        reply = "For micro-enterprises under NBCFDC schemes, you can avail loans up to ₹10 Lakhs under PMEGP or Mudra Shishu/Kishore categories with interest subvention up to 5%."
    elif "document" in msg or "paper" in msg:
        reply = "Standard documentation required includes: 1. Aadhaar Card, 2. Income/Caste Certificate, 3. Project Report / Business Plan, 4. Bank Account Passbook, 5. Passport size photographs."
    else:
        reply = f"I am your GraminSarthi AI assistant. Based on your profile query '{data.message}', I recommend checking the Regional Market Intelligence tab to discover district-level schemes and setup costs."
    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)