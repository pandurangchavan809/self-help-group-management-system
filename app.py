import streamlit as st
import time
from backend.auth import (
    president_login,
    member_login,
    create_shg,
    get_shg_id
)

# -------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Bachat Gat Digital",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# 2. SESSION STATE INITIALIZATION (CRITICAL FIX)
# -------------------------------------------------
# This prevents the "AttributeError" crash
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "shg_id" not in st.session_state:
    st.session_state.shg_id = None
if "role" not in st.session_state:
    st.session_state.role = None
if "shg_no" not in st.session_state:
    st.session_state.shg_no = None
if "member_id" not in st.session_state:
    st.session_state.member_id = None

# -------------------------------------------------
# 3. DARK THEME CSS (WORLD CLASS UI)
# -------------------------------------------------
st.markdown("""
    <style>
    /* 1. Main Background - Deep Dark Blue/Black Gradient */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: white;
    }

    /* 2. Login Button (Blue Glow) */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background: linear-gradient(90deg, #4f46e5 0%, #6366f1 100%);
        color: white;
        font-weight: 600;
        border: none;
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.5); /* Neon Glow */
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background: linear-gradient(90deg, #4338ca 0%, #4f46e5 100%);
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(79, 70, 229, 0.8);
    }

    /* 3. Register Button (Red Neon) - Targets Secondary Button */
    button[kind="secondary"] {
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 0 10px rgba(220, 38, 38, 0.4) !important;
    }
    button[kind="secondary"]:hover {
        background: linear-gradient(90deg, #b91c1c 0%, #dc2626 100%) !important;
        box-shadow: 0 0 20px rgba(220, 38, 38, 0.7) !important;
    }

    /* 4. Fix the White Box Issue (Dark Expander) */
    div[data-testid="stExpander"] { 
        border: 1px solid #334155; 
        background-color: #1e293b; /* Dark Blue-Grey */
        border-radius: 12px; 
        color: white;
    }
    
    /* 5. Input Fields (Dark Mode Friendly) */
    div[data-baseweb="input"] {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        color: white;
    }
    div[data-baseweb="input"]:focus-within {
        border: 1px solid #6366f1;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
    }
    /* Input Text Color */
    input {
        color: white !important;
    }

    /* 6. Header Text */
    .header-text { 
        text-align: center; 
        color: #e2e8f0; 
        margin-bottom: 5px; 
        font-family: sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 4. LANGUAGE DICTIONARY
# -------------------------------------------------
LANG = {
    "मराठी": {
        "title": "डिजिटल बचत गट",
        "subtitle": "ग्रामीण महिलांच्या आर्थिक प्रगतीसाठी",
        "role": "प्रवेश प्रकार निवडा",
        "president": "अध्यक्ष (President)",
        "member": "सभासद (Member)",
        "login": "लॉगिन करा",
        "register": "नवीन बचत गट नोंदणी",
        "username": "युजरनेम",
        "password": "पासवर्ड",
        "fname": "पहिले नाव",
        "lname": "आडनाव",
        "mobile": "मोबाईल नंबर",
        "shg": "बचत गट क्रमांक",
        "success": "प्रवेश यशस्वी!",
        "invalid": "माहिती चुकीची आहे",
        "create": "लाल बटन दाबून नोंदणी करा",
        "info": "⚠️ हा क्रमांक पुन्हा बदलता येणार नाही"
    },
    "English": {
        "title": "Bachat Gat Digital",
        "subtitle": "Empowering Rural Women Digitally",
        "role": "Select Login Type",
        "president": "President",
        "member": "Member",
        "login": "Login Now",
        "register": "Register New Group",
        "username": "Username",
        "password": "Password",
        "fname": "First Name",
        "lname": "Last Name",
        "mobile": "Mobile Number",
        "shg": "SHG Group Number",
        "success": "Access Granted!",
        "invalid": "Invalid Credentials",
        "create": "Register Group (Red Button)",
        "info": "⚠️ SHG number is unique and permanent"
    }
}

# -------------------------------------------------
# 5. UI LAYOUT

col_l, col_r = st.columns([2, 1])
with col_r:
    # Custom styled selectbox is hard, standard one is okay
    lang = st.selectbox("🌐 Language", ["मराठी", "English"], label_visibility="collapsed")
t = LANG[lang]

st.markdown(f"<h1 class='header-text'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #818cf8; font-size: 0.9em;'>{t['subtitle']}</p>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    
    # Custom segmented control
    role_type = st.segmented_control(
        t["role"],
        [t["president"], t["member"]],
        default=t["president"],
        label_visibility="collapsed"
    )
    st.write("") # Spacer

    # Main Card Area
    with st.container(border=True):
        if role_type == t["president"]:
            shg_no = st.text_input(f"🆔 {t['shg']}")
            username = st.text_input(f"👤 {t['username']}")
            password = st.text_input(f"🔑 {t['password']}", type="password")

            # BLUE LOGIN BUTTON
            if st.button(t["login"]):
                if president_login(shg_no, username, password):
                    st.session_state.logged_in = True
                    st.session_state.role = "president"
                    st.session_state.shg_no = shg_no
                    st.session_state.shg_id = get_shg_id(shg_no)
                    st.toast(t["success"], icon="✅")
                    time.sleep(0.5)
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error(t["invalid"])

            st.markdown("---")
            
            # REGISTRATION EXPANDER (NOW DARK THEMED)
            with st.expander(f"✨ {t['register']}"):
                st.info(t["info"])
                r_shg = st.text_input(f"{t['shg']} (New)", key="r_shg")
                r_name = st.text_input("Group Name / गटाचे नाव")
                r_user = st.text_input(f"{t['username']} (New)", key="r_user")
                r_pass = st.text_input(f"{t['password']} (New)", type="password", key="r_pass")
                
                # RED REGISTER BUTTON (Triggered by type="secondary" and CSS)
                if st.button(t["create"], key="reg_btn", type="secondary"):
                    if create_shg(r_shg, r_name, "Village", r_user, r_pass):
                        st.success("Registration Successful! Please Login.")
                        st.balloons()
                    else:
                        st.error("SHG Number already exists.")

        else:
            # MEMBER VIEW
            m_shg = st.text_input(f"🆔 {t['shg']}", key="m_shg_input")
            col1, col2 = st.columns(2)
            with col1:
                fname = st.text_input(f"👤 {t['fname']}")
            with col2:
                lname = st.text_input(f"👤 {t['lname']}")
            
            mobile = st.text_input(f"📱 {t['mobile']}")

            if st.button(t["login"]):
                member_id = member_login(m_shg, fname, lname, mobile)
                if member_id:
                    st.session_state.logged_in = True
                    st.session_state.role = "member"
                    st.session_state.shg_no = m_shg
                    st.session_state.shg_id = get_shg_id(m_shg)
                    st.session_state.member_id = member_id
                    st.toast(t["success"], icon="✅")
                    time.sleep(0.5)
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error(t["invalid"])
else:
    st.switch_page("pages/dashboard.py")