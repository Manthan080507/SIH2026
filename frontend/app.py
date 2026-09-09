import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="GraminSarthi-AI | Digital Business Advisor", 
    page_icon="🇮🇳", 
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    .top-accent-bar { height: 4px; background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%); margin-bottom: 1.5rem; }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .brand-header {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-top: 4px solid #003366;
        padding: 1.75rem 2rem; border-radius: 8px; margin-bottom: 2rem;
        display: flex; justify-content: space-between; align-items: center;
        animation: fadeIn 0.5s ease-out;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .brand-title-area h1 { color: #0F172A; font-size: 1.9rem; font-weight: 800; margin: 0; }
    .brand-title-area h1 span { color: #0056B3; }
    .brand-title-area p { color: #64748B; font-size: 0.95rem; margin-top: 0.4rem; }
    .gov-badge { background: #F1F5F9; border: 1px solid #CBD5E1; color: #334155; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    
    .stButton>button { 
        background-color: #003366; color: white; font-weight: 500; border-radius: 6px; border: none; 
        padding: 0.5rem 1rem; width: 100%; transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #002244; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,51,102,0.2); }
    
    section[data-testid="stSidebar"] { background-color: #0F172A; color: #F8FAFC; }
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] .stMarkdown { color: #F8FAFC !important; }
    
    div[data-testid="stExpander"] {
        animation: fadeIn 0.4s ease-out;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        margin-bottom: 0.75rem;
    }
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

state_district_map = {
    "Karnataka": ["Mandya", "Mysuru", "Bengaluru Urban", "Hubballi-Dharwad", "Mangaluru"],
    "Maharashtra": ["Mumbai City", "Pune", "Nagpur", "Nashik", "Thane"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur"]
}

# ==================== MANDATORY LOGIN / REGISTER GATEWAY ====================
if not st.session_state["logged_in"]:
    st.markdown('<div class="top-accent-bar"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 2.5rem; margin-bottom: 0.2rem;">🇮🇳</div>
                <h2 style="color: #0F172A; font-weight: 800; margin-bottom: 0.1rem;">GraminSarthi<span style="color: #0056B3;">-AI</span></h2>
                <p style="color: #64748B; font-size: 0.85rem; font-weight: 500; text-transform: uppercase;">Ministry of Social Justice & Empowerment Portal</p>
            </div>
        """, unsafe_allow_html=True)
        
        auth_mode = st.radio("Select Action", ["Sign In", "Register New Account"], horizontal=True, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if auth_mode == "Sign In":
            st.markdown("### Secure Citizen Login")
            login_user = st.text_input("Username", value="", placeholder="Enter your username")
            login_pass = st.text_input("Password", type="password", placeholder="Enter your password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Access Portal 🚀"):
                if login_user.strip() and login_pass.strip():
                    try:
                        res = requests.post("http://localhost:8000/api/login", json={"username": login_user, "password": login_pass})
                        if res.status_code == 200:
                            st.session_state["logged_in"] = True
                            st.session_state["username"] = login_user
                            st.success("Authentication successful! Loading portal...")
                            st.rerun()
                        else:
                            st.error("Invalid Login. Please check your credentials or register first.")
                    except Exception:
                        st.error("Invalid username, password, or account does not exist. Please register first.")
                else:
                    st.warning("Please enter both username and password.")
        else:
            st.markdown("### New Entrepreneur Registration")
            reg_user = st.text_input("Choose Username", placeholder="e.g. Manthan08")
            reg_email = st.text_input("Email Address", placeholder="name@example.com")
            reg_pass = st.text_input("Choose Password", type="password", placeholder="Create secure password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register Account 📝"):
                if reg_user.strip() and reg_pass.strip():
                    try:
                        res = requests.post("http://localhost:8000/api/register", json={"username": reg_user, "email": reg_email, "password": reg_pass})
                        if res.status_code == 200:
                            st.success("Registration successful! Please switch to 'Sign In' above.")
                        else:
                            st.error("Registration failed. Username might already exist.")
                    except Exception:
                        st.error("Could not connect to the backend server.")
                else:
                    st.warning("Please fill in all required fields.")

# ==================== MAIN APP (LOCKED UNTIL LOGGED IN) ====================
else:
    with st.sidebar:
        st.header("🌐 Portal Settings")
        lang = st.selectbox("Language / भाषा", ["English", "हिंदी (Hindi)", "ಕನ್ನಡ (Kannada)", "తెలుగు (Telugu)", "தமிழ் (Tamil)"])
        
        st.divider()
        st.header("👤 User Account")
        st.success(f"Active: **{st.session_state['username']}**")
        
        if st.button("Logout Session"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun()

    t = {
        "English": {
            "sub": "Digital Business Advisor & Government Scheme Matcher for Micro-Entrepreneurs",
            "tab1": "🤖 Sector & Scheme Intelligence",
            "tab2": "📊 Financial Simulator",
            "tab3": "📂 Saved Records",
            "tab4": "📈 Business Ledger",
            "tab5": "💬 AI Sarthi Chat",
            "h_market": "Regional Market Intelligence & Scheme Discovery",
            "lbl_state": "State Region",
            "lbl_dist": "District Selection",
            "lbl_cap": "Maximum Capital Investment (₹)",
            "lbl_skill": "Entrepreneur Skill Level",
            "chk_all": "🔍 Explore ALL Business Sectors Simultaneously",
            "lbl_biz": "Filter Specific Sector",
            "btn_rep": "Generate Advisory Report",
            "h_fin": "Financial Feasibility & DSCR Calculator",
            "lbl_cost": "Total Project Cost (₹)",
            "lbl_contrib": "Own Contribution (₹)",
            "lbl_sch_type": "Scheme Category",
            "lbl_rev": "Projected Annual Revenue (₹)",
            "lbl_exp": "Projected Annual Expenses (₹)",
            "btn_fin": "Run Financial Analysis",
            "btn_save": "Save Record",
            "h_rec": "Saved Profile Records",
            "h_ledger": "Business Operations Ledger",
            "lbl_mrev": "Monthly Revenue (₹)",
            "lbl_mrent": "Monthly Rent (₹)",
            "lbl_mutil": "Utilities (₹)",
            "lbl_msal": "Salaries (₹)",
            "lbl_mmat": "Raw Materials (₹)",
            "lbl_memi": "Loan EMI (₹)",
            "h_chat": "💬 GraminSarthi-AI Conversational Advisor",
            "chat_desc": "Chat with your virtual government scheme expert to get instant business recommendations and application guidance.",
            "chat_ph": "Ask about businesses, loans, documents..."
        },
        "हिंदी (Hindi)": {
            "sub": "सूक्ष्म उद्यमियों के लिए डिजिटल बिजनेस सलाहकार और सरकारी योजना मैचर",
            "tab1": "🤖 क्षेत्र और योजना इंटेलिजेंस",
            "tab2": "📊 वित्तीय सिम्युलेटर",
            "tab3": "📂 सहेजे गए रिकॉर्ड",
            "tab4": "📈 बिजनेस बहीखाता",
            "tab5": "💬 एआई सारथी चैट",
            "h_market": "क्षेत्रीय बाज़ार इंटेलिजेंस और योजना खोज",
            "lbl_state": "राज्य क्षेत्र",
            "lbl_dist": "जिला चयन",
            "lbl_cap": "अधिकतम पूंजी निवेश (₹)",
            "lbl_skill": "उद्यमी कौशल स्तर",
            "chk_all": "🔍 एकसाथ सभी व्यवसाय क्षेत्रों का अन्वेषण करें",
            "lbl_biz": "विशिष्ट क्षेत्र फ़िल्टर करें",
            "btn_rep": "सलाहकार रिपोर्ट तैयार करें",
            "h_fin": "वित्तीय व्यवहार्यता और DSCR कैलकुलेटर",
            "lbl_cost": "कुल परियोजना लागत (₹)",
            "lbl_contrib": "स्वयं का योगदान (₹)",
            "lbl_sch_type": "योजना श्रेणी",
            "lbl_rev": "अनुमानित वार्षिक राजस्व (₹)",
            "lbl_exp": "अनुमानित वार्षिक खर्च (₹)",
            "btn_fin": "वित्तीय विश्लेषण चलाएं",
            "btn_save": "रिकॉर्ड सहेजें",
            "h_rec": "सहेजे गए प्रोफाइल रिकॉर्ड",
            "h_ledger": "व्यापार संचालन बहीखाता",
            "lbl_mrev": "मासिक राजस्व (₹)",
            "lbl_mrent": "मासिक किराया (₹)",
            "lbl_mutil": "यूटिलिटी खर्च (₹)",
            "lbl_msal": "वेतन (₹)",
            "lbl_mmat": "कच्चा माल (₹)",
            "lbl_memi": "ऋण ईएमआई (₹)",
            "h_chat": "💬 ग्रामिनसारथी-एआई संवादात्मक सलाहकार",
            "chat_desc": "तत्काल व्यावसायिक सिफारिशें और आवेदन मार्गदर्शन प्राप्त करने के लिए अपने वर्चुअल गवर्नमेंट स्कीम एक्सपर्ट से बात करें।",
            "chat_ph": "व्यवसायों, ऋणों, दस्तावेजों के बारे में पूछें..."
        },
        "ಕನ್ನಡ (Kannada)": {
            "sub": "ಸೂಕ್ಷ್ಮ ಉದ್ಯಮಿಗಳಿಗಾಗಿ ಡಿಜಿಟಲ್ ವ್ಯಾಪಾರ ಸಲಹೆಗಾರ ಮತ್ತು ಸರ್ಕಾರಿ ಯೋಜನೆ ಹೊಂದಾಣಿಕೆದಾರ",
            "tab1": "🤖 ವಲಯ ಮತ್ತು ಯೋಜನೆ ಗುಪ್ತಚರ",
            "tab2": "📊 ಹಣಕಾಸು ಸಿಮ್ಯುಲೇಟರ್",
            "tab3": "📂 ಉಳಿಸಿದ ದಾಖಲೆಗಳು",
            "tab4": "📈 ವ್ಯಾಪಾರ ಲೆಡ್ಜರ್",
            "tab5": "💬 AI ಸಾರಥಿ ಚಾಟ್",
            "h_market": "ಪ್ರಾದೇಶಿಕ ಮಾರುಕಟ್ಟೆ ಗುಪ್ತಚರ ಮತ್ತು ಯೋಜನೆ ಅನ್ವೇಷಣೆ",
            "lbl_state": "ರಾಜ್ಯ ಪ್ರದೇಶ",
            "lbl_dist": "ಜಿಲ್ಲೆ ಆಯ್ಕೆ",
            "lbl_cap": "ಗರಿಷ್ಠ ಬಂಡವಾಳ ಹೂಡಿಕೆ (₹)",
            "lbl_skill": "ಉದ್ಯಮಿ ಕೌಶಲ್ಯ ಮಟ್ಟ",
            "chk_all": "🔍 ಎಲ್ಲಾ ವ್ಯಾಪಾರ ವಲಯಗಳನ್ನು ಏಕಕಾಲದಲ್ಲಿ ಅನ್ವೇಷಿಸಿ",
            "lbl_biz": "ನಿರ್ದಿಷ್ಟ ವಲಯವನ್ನು ಫಿಲ್ಟರ್ ಮಾಡಿ",
            "btn_rep": "ಸಲಹಾ ವರದಿಯನ್ನು ರಚಿಸಿ",
            "h_fin": "ಹಣಕಾಸಿನ ಕಾರ್ಯಸಾಧ್ಯತೆ ಮತ್ತು DSCR ಕ್ಯಾಲ್ಕುಲೇಟರ್",
            "lbl_cost": "ಒಟ್ಟು ಯೋಜನಾ ವೆಚ್ಚ (₹)",
            "lbl_contrib": "ಸ್ವಂತ ಕೊಡುಗೆ (₹)",
            "lbl_sch_type": "ಯೋಜನೆ ವರ್ಗ",
            "lbl_rev": "ಅಂದಾಜು ವಾರ್ಷಿಕ ಆದಾಯ (₹)",
            "lbl_exp": "ಅಂದಾಜು ವಾರ್ಷಿಕ ವೆಚ್ಚಗಳು (₹)",
            "btn_fin": "ಹಣಕಾಸು ವಿಶ್ಲೇಷಣೆ ನಡೆಸಿ",
            "btn_save": "ದಾಖಲೆಯನ್ನು ಉಳಿಸಿ",
            "h_rec": "ಉಳಿಸಿದ ಪ್ರೊಫೈಲ್ ದಾಖಲೆಗಳು",
            "h_ledger": "ವ್ಯಾಪಾರ ಕಾರ್ಯಾಚರಣೆಗಳ ಲೆಡ್ಜರ್",
            "lbl_mrev": "ಮಾಸಿಕ ಆದಾಯ (₹)",
            "lbl_mrent": "ಮಾಸಿಕ ಬಾಡಿಗೆ (₹)",
            "lbl_mutil": "ಸೌಲಭ್ಯಗಳು (₹)",
            "lbl_msal": "ಸಂಬಳಗಳು (₹)",
            "lbl_mmat": "ಕಚ್ಚಾ ವಸ್ತುಗಳು (₹)",
            "lbl_memi": "ಸಾಲದ EMI (₹)",
            "h_chat": "💬 ಗ್ರಾಮಿನಸಾರಥಿ-AI ಸಂಭಾಷಣಾ ಸಲಹೆಗಾರ",
            "chat_desc": "ತ್ವರಿತ ವ್ಯಾಪಾರ ಶಿಫಾರಸುಗಳು ಮತ್ತು ಅರ್ಜಿ ಮಾರ್ಗದರ್ಶನ ಪಡೆಯಲು ನಿಮ್ಮ ವರ್ಚುವಲ್ ಸರ್ಕಾರಿ ಯೋಜನೆ ತಜ್ಞರೊಂದಿಗೆ ಚಾಟ್ ಮಾಡಿ.",
            "chat_ph": "ವ್ಯವಹಾರಗಳು, ಸಾಲಗಳು, ದಾಖಲೆಗಳ ಬಗ್ಗೆ ಕೇಳಿ..."
        },
        "తెలుగు (Telugu)": {
            "sub": "సూక్ష్మ పారిశ్రామికవేత్తల కోసం డిజిటల్ బిజినెస్ అడ్వైజర్ & ప్రభుత్వ పథకాల మ్యాచ్ఛర్",
            "tab1": "🤖 రంగం & పథకం ఇంటెలిజెన్స్",
            "tab2": "📊 ఫైనాన్షియల్ సిమ్యులేటర్",
            "tab3": "📂 సేవ్ చేసిన రికార్డ్స్",
            "tab4": "📈 వ్యాపార లెడ్జర్",
            "tab5": "💬 AIసారథి చాట్",
            "h_market": "ప్రాంతీయ మార్కెట్ ఇంటెలిజెన్స్ & పథకాల అన్వేషణ",
            "lbl_state": "రాష్ట్ర ప్రాంతం",
            "lbl_dist": "జిల్లా ఎంపిక",
            "lbl_cap": "గరిష్ట మూలధన పెట్టుబడి (₹)",
            "lbl_skill": "పారిశ్రామికవేత్త నైపుణ్య స్థాయి",
            "chk_all": "🔍 అన్ని వ్యాపార రంగాలను ఒకేసారి అన్వేషించండి",
            "lbl_biz": "నిర్దిష్ట రంగాన్ని ఫిల్టర్ చేయండి",
            "btn_rep": "సలహా నివేదికను రూపొందించండి",
            "h_fin": "ఆర్థిక సాధ్యత & DSCR కాలిక్యులేటర్",
            "lbl_cost": "మొత్తం ప్రాజెక్ట్ ఖర్చు (₹)",
            "lbl_contrib": "స్వంత పెట్టుబడి (₹)",
            "lbl_sch_type": "పథకం వర్గం",
            "lbl_rev": "అంచనా వేసిన వార్షిక రాబడి (₹)",
            "lbl_exp": "అంచనా వేసిన వార్షిక ఖర్చులు (₹)",
            "btn_fin": "ఆర్థిక విశ్లేషణను అమలు చేయండి",
            "btn_save": "రికార్డ్‌ను సేవ్ చేయండి",
            "h_rec": "సేవ్ చేయబడిన ప్రొఫైల్ రికార్డులు",
            "h_ledger": "వ్యాపార కార్యకలాపాల లెడ్జర్",
            "lbl_mrev": "నెలవారీ ఆదాయం (₹)",
            "lbl_mrent": "నెలవారీ అద్దె (₹)",
            "lbl_mutil": "యుటిలిటీస్ (₹)",
            "lbl_msal": "జీతాలు (₹)",
            "lbl_mmat": "ముడి పదార్థాలు (₹)",
            "lbl_memi": "లోన్ EMI (₹)",
            "h_chat": "💬 గ్రామిన్‌సారథి-AI సంభాషణ సలహాదారు",
            "chat_desc": "తక్షణ వ్యాపార సిఫార్సులు మరియు దరఖాస్తు మార్గదర్శకత్వం పొందడానికి మీ వర్చువల్ ప్రభుత్వ పథకాల నిపుణుడితో మాట్లాడండి.",
            "chat_ph": "వ్యాపారాలు, రుణాలు, పత్రాల గురించి అడగండి..."
        },
        "தமிழ் (Tamil)": {
            "sub": "நுண் தொழில் முனைவோருக்கான டிஜிட்டல் வணிக ஆலோசகர் மற்றும் அரசு திட்டப் பொருத்துபவர்",
            "tab1": "🤖 துறை & திட்டம் நுண்ணறிவு",
            "tab2": "📊 நிதி சிமுலேட்டர்",
            "tab3": "📂 சேமிக்கப்பட்ட பதிவுகள்",
            "tab4": "📈 வணிக ஏடு",
            "tab5": "💬 AI சாரதி அரட்டை",
            "h_market": "பிராந்திய சந்தை நுண்ணறிவு & திட்ட கண்டுபிடிப்பு",
            "lbl_state": "மாநிலப் பகுதி",
            "lbl_dist": "மாவட்டம் தேர்வு",
            "lbl_cap": "அதிகபட்ச மூலதன முதலீடு (₹)",
            "lbl_skill": "தொழில்முனைவோர் திறன் நிலை",
            "chk_all": "🔍 அனைத்து வணிகத் துறைகளையும் ஒரே நேரத்தில் ஆராயுங்கள்",
            "lbl_biz": "குறிப்பிட்ட துறையை வடிகட்டவும்",
            "btn_rep": "ஆலோசனை அறிக்கையை உருவாக்கவும்",
            "h_fin": "நிதி சாத்தியக்கூறு & DSCR கால்குலேட்டர்",
            "lbl_cost": "மொத்த திட்டச் செலவு (₹)",
            "lbl_contrib": "சொந்த முதலீடு (₹)",
            "lbl_sch_type": "திட்ட வகை",
            "lbl_rev": "மதிப்பிடப்பட்ட ஆண்டு வருவாய் (₹)",
            "lbl_exp": "மதிப்பிடப்பட்ட ஆண்டு செலவுகள் (₹)",
            "btn_fin": "நிதி பகுப்பாய்வை இயக்கவும்",
            "btn_save": "பதிவை சேமிக்கவும்",
            "h_rec": "சேமிக்கப்பட்ட சுயவிவரப் பதிவுகள்",
            "h_ledger": "வணிக செயல்பாட்டு ஏடு",
            "lbl_mrev": "மாதாந்திர வருவாய் (₹)",
            "lbl_mrent": "மாதாந்திர வாடகை (₹)",
            "lbl_mutil": "பயன்பாடுகள் (₹)",
            "lbl_msal": "சம்பளங்கள் (₹)",
            "lbl_mmat": "மூலப்பொருட்கள் (₹)",
            "lbl_memi": "கடன் EMI (₹)",
            "h_chat": "💬 கிராமின்சாரதி-AI உரையாடல் ஆலோசகர்",
            "chat_desc": "உடனடி வணிக பரிந்துரைகள் மற்றும் விண்ணப்ப வழிகாட்டுதலைப் பெற உங்கள் மெய்நிகர் அரசு திட்ட நிபுணரிடம் பேசுங்கள்.",
            "chat_ph": "வணிகங்கள், கடன்கள், ஆவணங்கள் பற்றி கேட்கவும்..."
        }
    }[lang]

    st.markdown('<div class="top-accent-bar"></div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="brand-header">
            <div class="brand-title-area">
                <h1>GraminSarthi<span>-AI</span></h1>
                <p>{t['sub']}</p>
            </div>
            <div>
                <span class="gov-badge">🇮🇳 NBCFDC Initiative</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        t["tab1"], 
        t["tab2"], 
        t["tab3"], 
        t["tab4"],
        t["tab5"]
    ])

    with tab1:
        st.markdown(f"### {t['h_market']}")
        col1, col2 = st.columns(2)
        with col1:
            state = st.selectbox(t["lbl_state"], list(state_district_map.keys()))
            district = st.selectbox(t["lbl_dist"], state_district_map.get(state, ["Default"]))
        with col2:
            max_capital = st.number_input(t["lbl_cap"], value=300000, step=10000)
            skill_level = st.selectbox(t["lbl_skill"], ["Unskilled / Beginner", "Semi-Skilled", "Skilled"])

        # Fully interactive checkbox to toggle between all sectors or filtering
        explore_all = st.checkbox(t["chk_all"], value=True)
        business_type = None
        if not explore_all:
            business_type = st.selectbox(t["lbl_biz"], ["Dairy & Animal Husbandry", "Retail & Grocery Micro-Store", "Handloom & Traditional Handicrafts"])

        if st.button(t["btn_rep"]):
            try:
                res = requests.post("http://localhost:8000/api/recommend-all-businesses", json={"state": state, "district": district, "max_capital": max_capital, "skill_level": skill_level})
                if res.status_code == 200:
                    data = res.json()
                    st.success(data["region_context"])
                    
                    sectors_to_show = data["sectors"]
                    if not explore_all and business_type:
                        sectors_to_show = [s for s in data["sectors"] if business_type.lower() in s["business_type"].lower()]
                        if not sectors_to_show:
                            sectors_to_show = data["sectors"][:1]

                    for sector in sectors_to_show:
                        with st.expander(f"📌 {sector['business_type']} — Risk: {sector['risk_to_profit_ratio']}"):
                            col_x, col_y = st.columns(2)
                            with col_x:
                                st.markdown(f"**Best Scheme:** {sector['best_scheme']}")
                                st.markdown(f"**Nodal Agency:** {sector['nodal_agency']}")
                                st.markdown(f"**Subsidy Benefit:** {sector['scheme_subsidy']}")
                                st.markdown(f"**Estimated Setup Cost:** {sector['estimated_setup_cost']}")
                            with col_y:
                                st.markdown(f"**Active Regional Units:** {sector['active_units']}")
                                st.markdown(f"**Regional Growth:** {sector['regional_growth']}")
                                st.markdown(f"**Competitor Health:** {sector['competitor_health']}")
                            st.divider()
                            sc1, sc2 = st.columns(2)
                            with sc1:
                                st.markdown("✅ **Pros:**")
                                for pro in sector['pros']:
                                    st.markdown(f"- {pro}")
                            with sc2:
                                st.markdown("❌ **Cons / Risks:**")
                                for con in sector['cons']:
                                    st.markdown(f"- {con}")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab2:
        st.markdown(f"### {t['h_fin']}")
        col_a, col_b = st.columns(2)
        with col_a:
            project_cost = st.number_input(t["lbl_cost"], value=300000, step=10000)
            own_contribution = st.number_input(t["lbl_contrib"], value=30000, step=5000)
            scheme_type = st.selectbox(t["lbl_sch_type"], options=["general", "swarnima"])
        with col_b:
            annual_revenue = st.number_input(t["lbl_rev"], value=400000, step=10000)
            annual_expenses = st.number_input(t["lbl_exp"], value=130000, step=5000)

        if st.button(t["btn_fin"]):
            payload = {"project_cost": project_cost, "own_contribution": own_contribution, "annual_revenue": annual_revenue, "annual_expenses": annual_expenses, "scheme_type": scheme_type}
            try:
                response = requests.post("http://localhost:8000/api/analyze-financials", json=payload)
                if response.status_code == 200:
                    st.session_state["latest_analysis"] = {**payload, **response.json()}
            except Exception:
                st.error("Error running analysis.")

        if "latest_analysis" in st.session_state:
            res = st.session_state["latest_analysis"]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Loan Required", f"₹{res['loan_required']:,.2f}")
            m2.metric("Interest Rate", f"{res['interest_rate']}% p.a.")
            m3.metric("Monthly EMI", f"₹{res['monthly_emi']:,.2f}")
            m4.metric("DSCR Score", f"{res['dscr']}")
            st.info(f"**Verdict:** {res['status']}")

            st.markdown("#### 📊 Project Financial Distribution Chart")
            chart_data = pd.DataFrame({
                "Category": ["Own Contribution", "Loan Required", "Annual Revenue", "Annual Expenses"],
                "Amount (₹)": [res['own_contribution'], res['loan_required'], res['annual_revenue'], res['annual_expenses']]
            }).set_index("Category")
            st.bar_chart(chart_data)

            if st.button(t["btn_save"]):
                try:
                    requests.post("http://localhost:8000/api/save-record", json={"username": st.session_state["username"], **res})
                    st.success("Saved successfully!")
                except Exception:
                    st.error("Error saving record.")

    with tab3:
        st.markdown(f"### {t['h_rec']}")
        try:
            rec_res = requests.get(f"http://localhost:8000/api/records/{st.session_state['username']}")
            if rec_res.status_code == 200 and rec_res.json():
                st.dataframe(pd.DataFrame(rec_res.json()), use_container_width=True)
            else:
                st.info("No saved records found.")
        except Exception:
            st.error("Could not fetch records.")

    with tab4:
        st.markdown(f"### {t['h_ledger']}")
        t1, t2 = st.columns(2)
        with t1:
            m_rev = st.number_input(t["lbl_mrev"], value=35000, step=1000)
            m_rent = st.number_input(t["lbl_mrent"], value=5000, step=500)
            m_util = st.number_input(t["lbl_mutil"], value=2000, step=200)
        with t2:
            m_sal = st.number_input(t["lbl_msal"], value=8000, step=1000)
            m_mat = st.number_input(t["lbl_mmat"], value=10000, step=1000)
            m_emi = st.number_input(t["lbl_memi"], value=5000, step=500)

        total_exp = m_rent + m_util + m_sal + m_mat + m_emi
        net_prof = m_rev - total_exp
        st.divider()
        tm1, tm2, tm3 = st.columns(3)
        tm1.metric("Total Expenses", f"₹{total_exp:,.2f}")
        tm2.metric("Net Monthly Profit", f"₹{net_prof:,.2f}")
        tm3.metric("Margin", f"{(net_prof / m_rev * 100) if m_rev > 0 else 0:.1f}%")

    with tab5:
        st.markdown(f"### {t['h_chat']}")
        st.markdown(t["chat_desc"])
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": f"Namaste {st.session_state['username']}! I am your GraminSarthi AI guide."}
            ]

        for chat in st.session_state["chat_messages"]:
            with st.chat_message(chat["role"]):
                st.markdown(chat["content"])

        if user_input := st.chat_input(t["chat_ph"]):
            st.session_state["chat_messages"].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            try:
                res = requests.post("http://localhost:8000/api/ai-chat", json={"message": user_input, "username": st.session_state["username"]})
                ai_reply = res.json()["reply"] if res.status_code == 200 else "Server connection error."
            except Exception:
                ai_reply = "Could not reach backend service."

            st.session_state["chat_messages"].append({"role": "assistant", "content": ai_reply})
            with st.chat_message("assistant"):
                st.markdown(ai_reply)