import streamlit as st
import requests

st.set_page_config(
    page_title="Rural Business Advisor",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 AI-Driven Hyper-Local Business Advisor")
st.caption("Smart India Hackathon 2026 | Problem ID: SIH26091")

st.markdown("---")

# Section 1: Profile
st.header("📋 Entrepreneur Profile & Business Goal")
col1, col2 = st.columns(2)

with col1:
    state = st.selectbox("State", ["Karnataka", "Maharashtra", "Tamil Nadu", "Uttar Pradesh"])
    district = st.text_input("District", value="Mandya")
    block_village = st.text_input("Block / Village", value="Maddur")
    
with col2:
    business_type = st.selectbox("Proposed Business", ["Dairy Farming", "Poultry Farming", "Food Processing", "Solar Water Pump Services"])
    capital_available = st.number_input("Available Capital (₹)", min_value=5000, value=50000, step=5000)
    experience_years = st.slider("Prior Experience (Years)", 0, 10, 1)

st.markdown("---")

# Section 2: Financials
st.header("💰 Financial Parameters")
col_fin1, col_fin2 = st.columns(2)

with col_fin1:
    project_cost = st.number_input("Total Project Cost (₹)", min_value=10000, value=200000, step=10000)
    own_contribution = st.number_input("Own Contribution / Equity (₹)", min_value=0, value=50000, step=5000)
    interest_rate = st.number_input("Annual Interest Rate (%)", min_value=1.0, max_value=25.0, value=9.5, step=0.5)

with col_fin2:
    tenure_years = st.number_input("Loan Tenure (Years)", min_value=1, max_value=20, value=5, step=1)
    monthly_revenue = st.number_input("Estimated Monthly Revenue (₹)", min_value=0, value=35000, step=2000)
    monthly_expenses = st.number_input("Estimated Monthly Expenses (₹)", min_value=0, value=15000, step=1000)

st.markdown("---")

if st.button("Run Full Advisory Analysis"):
    fin_url = "http://127.0.0.1:8000/calculate-financials"
    scheme_url = "http://127.0.0.1:8000/recommend-schemes"
    advisory_url = "http://127.0.0.1:8000/generate-advisory"

    fin_payload = {
        "project_cost": float(project_cost),
        "own_contribution": float(own_contribution),
        "annual_interest_rate": float(interest_rate),
        "tenure_years": int(tenure_years),
        "monthly_revenue": float(monthly_revenue),
        "monthly_expenses": float(monthly_expenses)
    }

    scheme_payload = {
        "project_cost": float(project_cost),
        "business_type": business_type,
        "category": "General"
    }

    try:
        fin_resp = requests.post(fin_url, json=fin_payload)
        scheme_resp = requests.post(scheme_url, json=scheme_payload)

        if fin_resp.status_code == 200 and scheme_resp.status_code == 200:
            fin_data = fin_resp.json()
            scheme_data = scheme_resp.json()

            location_str = f"{block_village}, {district}, {state}"
            advisory_payload = {
                "location": location_str,
                "business_type": business_type,
                "experience_years": int(experience_years),
                "financial_summary": fin_data,
                "matched_schemes": scheme_data["schemes"]
            }
            advisory_resp = requests.post(advisory_url, json=advisory_payload)
            advisory_data = advisory_resp.json() if advisory_resp.status_code == 200 else {}

            st.success("Analysis Complete!")

            # Advisory Summary
            st.subheader("💡 Strategic Feasibility Executive Summary")
            status = advisory_data.get("feasibility_status", "ANALYSIS COMPLETE")
            if status == "HIGH FEASIBILITY":
                st.success(f"Status: {status}")
            else:
                st.warning(f"Status: {status}")

            st.markdown(advisory_data.get("executive_summary", ""))

            st.subheader("🎯 Recommended Action Plan")
            for idx, action in enumerate(advisory_data.get("recommended_actions", []), 1):
                st.write(f"**{idx}.** {action}")

            st.markdown("---")

            # Financial Breakdown
            st.subheader("📊 Financial Breakdown")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Required Loan", f"₹{fin_data['loan_amount']:,.2f}")
            m2.metric("Monthly EMI", f"₹{fin_data['monthly_emi']:,.2f}")
            m3.metric("Total Interest", f"₹{fin_data['total_interest']:,.2f}")
            m4.metric("Net Monthly Profit", f"₹{fin_data['net_monthly_profit']:,.2f}")

            st.markdown("---")

            # Schemes
            st.subheader("🏛️ Recommended Government Schemes")
            if scheme_data["total_matches"] > 0:
                for scheme in scheme_data["schemes"]:
                    with st.expander(f"📌 {scheme['scheme_name']}", expanded=True):
                        st.write(f"**Subsidy / Subvention:** {scheme['subsidy']}")
                        st.write(f"**Maximum Limit:** {scheme['max_limit']}")
                        st.write(f"**Why Eligible:** {scheme['eligibility_reason']}")
            else:
                st.info("No specific scheme matched your exact criteria.")

            st.markdown("---")

            # PDF Download Endpoint Integration
            pdf_url = "http://127.0.0.1:8000/generate-pdf"
            pdf_payload = {
                "location": location_str,
                "business_type": business_type,
                "feasibility_status": advisory_data.get("feasibility_status", "N/A"),
                "executive_summary": advisory_data.get("executive_summary", ""),
                "recommended_actions": advisory_data.get("recommended_actions", []),
                "financial_summary": fin_data
            }

            pdf_resp = requests.post(pdf_url, json=pdf_payload)
            if pdf_resp.status_code == 200:
                st.download_button(
                    label="📄 Download Official Advisory Report (PDF)",
                    data=pdf_resp.content,
                    file_name="Business_Advisory_Report.pdf",
                    mime="application/pdf"
                )

        else:
            st.error("Error communicating with backend API.")

    except Exception as e:
        st.error(f"Could not connect to backend server: {e}")