import streamlit as st
from datetime import datetime

# Import Backend Logic
from backend.api import add_member, add_deposit, give_loan, repay_loan, activate_member,deactivate_member, update_member
from backend.sms import send_sms, deposit_sms, loan_given_sms, loan_closed_sms
from backend.calculations import (
    calculate_monthly_interest, calculate_monthly_payable, 
    get_wallet_balance, is_loan_fully_paid
)
from backend.db import get_db_connection

# 1. PAGE CONFIGURATION & AUTH
st.set_page_config(layout="wide", page_title="SHG Management Portal")

if "logged_in" not in st.session_state or st.session_state.role != "president":
    st.switch_page("app.py")
    st.stop()

shg_id = st.session_state.shg_id

# 2. BILINGUAL DICTIONARY
if "lang" not in st.session_state:
    st.session_state.lang = "मराठी"

LANG = {
    "मराठी": {
        
        "title": "व्यवस्थापन पोर्टल", 
        "tab1": "👤 सभासद", "tab2": "💰 मासिक जमा", "tab3": "💸 कर्ज व्यवहार", 
        "tab4": "📜 इतिहास", "tab5": "📁 जुनी नोंदणी",
        "add": "सभासद जोडा", "submit": "जमा नोंदवा", "disburse": "कर्ज द्या",
        "repay": "परतफेड नोंदवा", "back": "⬅️ डॅशबोर्ड", "logout": "🔓 लॉगआउट",

       
        "tab6": "✏️ सभासद बदला",
        "edit_header": "✏️ सभासद माहिती बदला / निष्क्रिय करा",
        "select_member": "सभासद निवडा",
        "first_name": "पहिले नाव",
        "last_name": "आडनाव",
        "mobile": "मोबाईल नंबर",
        "monthly": "दरमहा जमा",
        "update": "💾 माहिती अपडेट करा",
        "deactivate": "🚫 सभासद निष्क्रिय करा",
        "success_update": "सभासद माहिती अपडेट झाली",
        "success_deactivate": "सभासद निष्क्रिय केला",
        "reactivate": "♻️ सभासद पुन्हा सुरू करा",
        "success_reactivate": "सभासद पुन्हा सक्रिय केला"

    },

    "English": {
        
        "title": "Management Portal", 
        "tab1": "👤 Members", "tab2": "💰 Deposits", "tab3": "💸 Loans", 
        "tab4": "📜 History", "tab5": "📁 Legacy Data",
        "add": "Add Member", "submit": "Record Deposit", "disburse": "Give Loan",
        "repay": "Record Repayment", "back": "⬅️ Dashboard", "logout": "🔓 Logout",

       
        "tab6": "✏️ Edit Member",
        "edit_header": "✏️ Edit / Deactivate Member",
        "select_member": "Select Member",
        "first_name": "First Name",
        "last_name": "Last Name",
        "mobile": "Mobile Number",
        "monthly": "Monthly Deposit",
        "update": "💾 Update Details",
        "deactivate": "🚫 Deactivate Member",
        "success_update": "Member details updated",
        "success_deactivate": "Member deactivated",
        "reactivate": "♻️ Reactivate Member",
        "success_reactivate": "Member reactivated"

    }
}

t = LANG[st.session_state.lang]

# 3. GLOBAL UI STYLING
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    
    /* Elegant Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: rgba(255,255,255,0.02);
        border-radius: 12px 12px 0 0; border: 1px solid rgba(255,255,255,0.05); padding: 10px 20px;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #6366f1 !important; color: white !important; 
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    /* Input Field Styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 10px;
    }
    
    /* Section Headers */
    .section-head {
        font-weight: 500; font-size: 1.2rem; color: #6366f1; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. DATA FETCHING HELPERS
def get_members():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, first_name, last_name, mobile, monthly_deposit FROM members WHERE shg_id=%s AND status='active' ORDER BY first_name", (shg_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

def get_active_loans():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT l.id, m.first_name, l.loan_amount, l.interest_rate FROM loans l JOIN members m ON m.id = l.member_id WHERE l.shg_id=%s AND l.status='active'", (shg_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

members = get_members()
member_map = {f"{m['first_name']} {m['last_name']}": m for m in members}

# 5. HEADER SECTION
head_l, head_r = st.columns([3, 1])
with head_l:
    st.markdown(f"<h1 style='font-weight:100; margin:0;'>{t['title']}</h1>", unsafe_allow_html=True)
with head_r:
    st.session_state.lang = st.selectbox("🌐", ["मराठी", "English"], index=0 if st.session_state.lang == "मराठी" else 1, label_visibility="collapsed")

st.divider()

# 6. MAIN INTERFACE TABS
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([t['tab1'], t['tab2'], t['tab3'], t['tab4'], t['tab5'], t['tab6']])

# --- TAB 1: MEMBER MANAGEMENT ---
with tab1:
    m_left, m_right = st.columns([1, 2])
    with m_left:
        st.markdown('<p class="section-head">➕ New Member / नवीन सभासद</p>', unsafe_allow_html=True)
        fn = st.text_input("First Name")
        ln = st.text_input("Last Name")
        mobile = st.text_input("Mobile")
        dep_amt = st.number_input("Monthly Deposit", value=500, step=100)
        if st.button(t["add"], use_container_width=True, type="primary"):
            if fn and mobile:
                add_member(shg_id, fn, ln, mobile, dep_amt)
                st.success(t["add"])
                st.rerun()
    with m_right:
        st.markdown('<p class="section-head">👥 Active List / सक्रिय यादी</p>', unsafe_allow_html=True)
        st.dataframe(members, use_container_width=True, hide_index=True)

# --- TAB 2: MONTHLY DEPOSIT ---
with tab2:
    st.markdown(f'<p class="section-head">{t["tab2"]}</p>', unsafe_allow_html=True)
    sel_members = st.multiselect("Select Members / सभासद निवडा", list(member_map.keys()))
    if st.button(t["submit"], use_container_width=True, type="primary"):
        month, year = datetime.now().month, datetime.now().year
        for name in sel_members:
            m = member_map[name]
            add_deposit(shg_id, m["id"], m["monthly_deposit"], month, year)
            send_sms(shg_id, m["id"], m["mobile"], deposit_sms(name, m["monthly_deposit"], get_wallet_balance(shg_id)))
        st.success(f"{len(sel_members)} deposits recorded!")

# --- TAB 3: LOAN SYSTEM ---
with tab3:
    give_col, repay_col = st.columns(2)
    with give_col:
        st.markdown(f'<p class="section-head">{t["disburse"]}</p>', unsafe_allow_html=True)
        l_member = st.selectbox("Member", list(member_map.keys()), key="l_mem")
        l_amt = st.number_input("Loan Amount", step=1000, key="l_amt")
        l_int = st.number_input("Interest %", value=2.0, key="l_int")
        if st.button(t["disburse"], use_container_width=True):
            m = member_map[l_member]
            give_loan(shg_id, m["id"], l_amt, l_int)
            send_sms(shg_id, m["id"], m["mobile"], loan_given_sms(l_member, l_amt, l_int, calculate_monthly_payable(l_amt, l_int)))
            st.rerun()

    with repay_col:
        st.markdown(f'<p class="section-head">{t["repay"]}</p>', unsafe_allow_html=True)
        act_loans = get_active_loans()
        if not act_loans: st.info("No active loans")
        else:
            l_lbls = {f"{l['first_name']} - ₹{l['loan_amount']}": l for l in act_loans}
            sel_l = st.selectbox("Choose Loan", list(l_lbls.keys()))
            p_type = st.radio("Type", ["interest", "principal"], horizontal=True)
            p_amt = st.number_input("Payment Amount", step=100)
            if st.button(t["repay"], use_container_width=True):
                repay_loan(l_lbls[sel_l]["id"], p_amt, p_type)
                st.rerun()

# --- TAB 4: HISTORY & AUDIT ---
with tab4:
    h_top, h_bot = st.columns(2)
    with h_top:
        st.markdown('<p class="section-head">📜 Recent Transactions / अलीकडील व्यवहार</p>', unsafe_allow_html=True)
        conn = get_db_connection(); cur = conn.cursor(dictionary=True)
        cur.execute("SELECT created_at, txn_type, amount FROM transactions WHERE shg_id=%s ORDER BY created_at DESC LIMIT 50", (shg_id,))
        st.dataframe(cur.fetchall(), use_container_width=True)
        cur.close(); conn.close()
    with h_bot:
        st.markdown('<p class="section-head">📁 Closed Loans / पूर्ण झालेले कर्ज</p>', unsafe_allow_html=True)
        st.info("Historical data of closed loans is visible here.")

# --- TAB 5: LEGACY / TIME MACHINE ---
with tab5:
    st.markdown('<p class="section-head">🕰️ Legacy Data Entry / मागील नोंदी</p>', unsafe_allow_html=True)
    st.info("Use this tab only for entries made before using this application.")

    # Time Selection Card
    with st.expander("📅 Select Legacy Date / तारीख निवडा", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            legacy_month = st.selectbox("Month", list(range(1, 13)), format_func=lambda x: datetime(1900, x, 1).strftime('%B'))
        with c2:
            legacy_year = st.selectbox("Year", list(range(2000, datetime.now().year + 1)), index=len(list(range(2000, datetime.now().year + 1)))-1)

    st.divider()

    leg_col1, leg_col2 = st.columns(2)

    with leg_col1:
        st.markdown("### 💰 Past Deposits")
        legacy_members = st.multiselect("Select Members", list(member_map.keys()), key="legacy_members")
        if st.button("Save Past Deposits", use_container_width=True):
            for name in legacy_members:
                m = member_map[name]
                add_deposit(shg_id, m["id"], m["monthly_deposit"], legacy_month, legacy_year)
                
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("UPDATE transactions SET is_legacy=1 WHERE shg_id=%s AND member_id=%s ORDER BY created_at DESC LIMIT 1", (shg_id, m["id"]))
                conn.commit()
                cur.close(); conn.close()
            st.success("Past deposits saved as Legacy")
            st.rerun()

    with leg_col2:
        st.markdown("### 💸 Past Loan")
        l_mem_name = st.selectbox("Member", list(member_map.keys()), key="legacy_loan_member")
        l_amt_val = st.number_input("Loan Amount", step=1000, key="legacy_loan_amt")
        l_int_val = st.number_input("Interest %", value=2.0, key="legacy_loan_int")
        
        if st.button("Save Past Loan", use_container_width=True):
            m = member_map[l_mem_name]
            loan_id = give_loan(shg_id, m["id"], l_amt_val, l_int_val)
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE loans SET loan_date=STR_TO_DATE(%s,'%%Y-%%m-%%d') WHERE id=%s", (f"{legacy_year}-{legacy_month}-01", loan_id))
            cur.execute("UPDATE transactions SET is_legacy=1 WHERE shg_id=%s AND member_id=%s ORDER BY created_at DESC LIMIT 1", (shg_id, m["id"]))
            conn.commit()
            cur.close(); conn.close()
            st.success("Past loan saved as Legacy")
            st.rerun()

    st.divider()
    st.markdown("### 🔁 Past Loan Repayment")
    active_loans_leg = get_active_loans()
    if active_loans_leg:
        loan_map_leg = {f"{l['first_name']} - ₹{l['loan_amount']}": l for l in active_loans_leg}
        leg_repay_sel = st.selectbox("Select Loan", list(loan_map_leg.keys()), key="leg_repay_box")
        leg_pay_type = st.radio("Type", ["interest", "principal"], horizontal=True, key="leg_repay_type")
        leg_pay_amt = st.number_input("Amount", step=100, key="leg_pay_amt")
        
        if st.button("Save Past Repayment", use_container_width=True):
            loan_obj = loan_map_leg[leg_repay_sel]
            repay_loan(loan_obj["id"], leg_pay_amt, leg_pay_type)
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE transactions SET is_legacy=1 WHERE shg_id=%s AND member_id=%s ORDER BY created_at DESC LIMIT 1", (shg_id, loan_obj["id"]))
            conn.commit()
            cur.close(); conn.close()
            st.success("Past repayment saved as Legacy")
            st.rerun()

            
with tab6:
    st.subheader(t["edit_header"])

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, first_name, last_name, mobile, monthly_deposit, status
        FROM members
        WHERE shg_id=%s
        ORDER BY first_name
    """, (shg_id,))
    all_members = cur.fetchall()
    cur.close()
    conn.close()

    if not all_members:
        st.info("No members found")
    else:
        member_labels = {
            f"{m['first_name']} {m['last_name']} ({m['status']})": m
            for m in all_members
        }

        selected = st.selectbox(
            t["select_member"],
            list(member_labels.keys()),
            key="edit_member_select"
        )

        m = member_labels[selected]

        col1, col2 = st.columns(2)
        with col1:
            new_fn = st.text_input(t["first_name"], value=m["first_name"], key="edit_fn")
            new_ln = st.text_input(t["last_name"], value=m["last_name"], key="edit_ln")

        with col2:
            new_mobile = st.text_input(t["mobile"], value=m["mobile"], key="edit_mobile")
            new_dep = st.number_input(
                t["monthly"],
                value=m["monthly_deposit"],
                step=100,
                key="edit_monthly"
            )

        st.write("")

        # -------- ACTION BUTTONS --------
        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button(t["update"], use_container_width=True):
                update_member(
                    m["id"],
                    new_fn,
                    new_ln,
                    new_mobile,
                    new_dep
                )
                st.success(t["success_update"])
                st.rerun()

        with c2:
            if m["status"] == "active":
                if st.button(t["deactivate"], use_container_width=True):
                    deactivate_member(m["id"])
                    st.warning(t["success_deactivate"])
                    st.rerun()

        with c3:
            if m["status"] == "left":
                if st.button(t["reactivate"], use_container_width=True):
                    activate_member(m["id"])
                    st.success(t["success_reactivate"])
                    st.rerun()

# 8. FOOTER NAVIGATION
st.write("")
st.divider()
f1, f2 = st.columns(2)
with f1:
    if st.button(t["back"], use_container_width=True): st.switch_page("pages/dashboard.py")
with f2:
    if st.button(t["logout"], use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")