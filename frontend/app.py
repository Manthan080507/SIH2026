import streamlit as st
import requests
import plotly.express as px

st.set_page_config(page_title="Rural Business Advisory", layout="wide")

st.title("🌾 Rural Business Advisory Engine")
st.markdown("Enter entrepreneur and financial metrics below to generate feasibility analysis.")

# Input Form
col1, col2 = st.columns(2)

with col1:
    business_type = st.selectbox("Business Type", ["Dairy Farming", "Poultry Farming", "Textile Unit", "Agri-Retail", "Food Processing"])
    district = st.text_input("District", value="Mandya")
    block = st.text_input("Block / Village", value="Maddur")
    category = st.selectbox("Category / Demographic", ["General", "OBC", "SC", "ST", "Woman Entrepreneur"])
    education = st.selectbox("Education Level", ["8th Pass", "10th Pass", "12th Pass", "Graduate", "Post Graduate"])
    experience = st.slider("Prior Experience (Years)", 0, 20, 1)

with col2:
    st.subheader("💰 Financial Parameters")
    total_cost = st.number_input("Total Project Cost (₹)", value=200000)
    equity = st.number_input("Own Contribution / Equity (₹)", value=50000)
    interest_rate = st.number_input("Annual Interest Rate (%)", value=9.5)
    tenure = st.number_input("Loan Tenure (Years)", value=5)
    revenue = st.number_input("Estimated Monthly Revenue (₹)", value=35000)
    expenses = st.number_input("Estimated Monthly Expenses (₹)", value=15000)

if st.button("Run Full Advisory Analysis"):
    payload = {
        "business_type": business_type,
        "district": district,
        "block": block,
        "category": category,
        "education": education,
        "experience_years": int(experience),
        "total_cost": float(total_cost),
        "equity": float(equity),
        "loan_tenure_years": int(tenure),
        "annual_interest_rate": float(interest_rate),
        "estimated_monthly_revenue": float(revenue),
        "estimated_monthly_expenses": float(expenses)
    }

    # API Endpoint URL pointing to backend /analyze endpoint
    backend_url = "http://127.0.0.1:8000/analyze"
    pdf_url = "http://127.0.0.1:8000/generate-pdf"

    try:
        response = requests.post(backend_url, json=payload)
        if response.status_code == 200:
            st.success("Analysis Complete!")
            data = response.json()

            st.header("📊 Strategic Feasibility Executive Summary")
            st.info(f"Status: {data.get('feasibility_status', 'HIGH FEASIBILITY')}")
            st.write(data.get("executive_summary", ""))

            # Financial Metrics & Plotly Charts
            st.subheader("Financial Breakdown")
            financials = data.get("financials", {})
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Loan Amount", f"₹{financials.get('loan_amount', 0)}")
            c2.metric("Monthly EMI", f"₹{financials.get('emi', 0)}")
            c3.metric("Net Monthly Profit", f"₹{financials.get('net_monthly_profit', 0)}")

            # Plotly Visualization
            chart_data = {
                "Category": ["Monthly Revenue", "Monthly Expenses", "Monthly EMI", "Net Profit"],
                "Amount (₹)": [
                    revenue,
                    expenses,
                    financials.get("emi", 0),
                    financials.get("net_monthly_profit", 0)
                ]
            }
            fig = px.bar(chart_data, x="Category", y="Amount (₹)", color="Category", title="Monthly Cashflow Breakdown")
            st.plotly_chart(fig, use_container_width=True)

            # Recommended Actions
            st.subheader("Recommended Action Plan")
            actions = data.get("recommended_actions", [])
            for action in actions:
                st.write(f"- {action}")

            # PDF Generation Handler
            json_pdf_payload = {
                "business_type": business_type,
                "district": district,
                "feasibility_status": data.get("feasibility_status", ""),
                "executive_summary": data.get("executive_summary", ""),
                "financials": financials,
                "recommended_actions": actions
            }

            pdf_resp = requests.post(pdf_url, json=json_pdf_payload)
            if pdf_resp.status_code == 200:
                st.download_button(
                    label="📄 Download Official Advisory Report (PDF)",
                    data=pdf_resp.content,
                    file_name="Business_Advisory_Report.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Error generating PDF from backend.")
        else:
            st.error("Error communicating with backend API.")
    except Exception as e:
        st.error(f"Could not connect to backend server: {e}")