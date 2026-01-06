import streamlit as st
import matplotlib.pyplot as plt

# 1. SESSION SHIELD

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.switch_page("app.py")
    st.stop()

shg_id = st.session_state.get("shg_id")
role = st.session_state.get("role")

if not shg_id:
    st.switch_page("app.py")
    st.stop()

# 2. DATA IMPORTS

from backend.calculations import (
    get_total_savings,
    get_total_loan_given,
    get_wallet_balance
)
from backend.db import get_db_connection

@st.cache_data(ttl=60)
def fetch_dashboard_stats(shg_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM members WHERE shg_id=%s AND status='active'", (shg_id,))
    members = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM loans WHERE shg_id=%s AND status='active'", (shg_id,))
    loans = cur.fetchone()[0]
    cur.execute("SELECT shg_name, shg_number FROM shg_groups WHERE id=%s", (shg_id,))
    details = cur.fetchone()
    cur.close()
    conn.close()
    return members, loans, details

active_members, active_loans, shg_details = fetch_dashboard_stats(shg_id)

total_savings = get_total_savings(shg_id)
total_loan_given = get_total_loan_given(shg_id)
wallet_balance = get_wallet_balance(shg_id)

shg_name = shg_details[0] if shg_details else "SHG"
shg_number = shg_details[1] if shg_details else "N/A"

# 3. LANGUAGE

if "lang" not in st.session_state:
    st.session_state.lang = "मराठी"

LANG = {
    "मराठी": {
        "sav": "एकूण बचत", "loan": "एकूण कर्ज", "avail": "शिल्लक",
        "members": "सभासद", "loans": "सक्रिय कर्ज",
        "manage": "👥 सभासद", "report": "📄 अहवाल", "logout": "🔓 लॉगआउट", "next_p":"पुढील हप्ता"
    },
    "English": {
        "sav": "Savings", "loan": "Loans", "avail": "Balance",
        "members": "Members", "loans": "Active Loans",
        "manage": "👥 Members", "report": "📄 Reports", "logout": "🔓 Logout", "next_p":"Next Payable"
    }
}
t = LANG[st.session_state.lang]

# 4. COMPACT CSS

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Compact metrics */
div[data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 500 !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    color: #64748b !important;
}

/* Balance strip */
.balance-strip {
    border: 1px solid #e5e7eb;
    padding: 6px 12px;
    border-radius: 6px;
    text-align: right;
}

/* Buttons */
.stButton>button {
    padding: 6px 10px !important;
    border-radius: 8px;
    font-weight: 400;
}
</style>
""", unsafe_allow_html=True)

# 5. HEADER + LANGUAGE

h1, h2 = st.columns([4, 1])
with h2:
    st.session_state.lang = st.selectbox(
        "🌐", ["मराठी", "English"],
        index=0 if st.session_state.lang == "मराठी" else 1,
        label_visibility="collapsed"
    )

title_l, title_r = st.columns([3, 1])
with title_l:
    st.markdown(f"### {shg_name.upper()}")
    st.caption(f"गट क्रमांक : {shg_number}")

with title_r:
    st.markdown(f"""
        <div class="balance-strip">
            <span style="font-size:0.65rem;color:#64748b;">₹ उपलब्ध रक्कम</span><br>
            <b style="font-size:1.2rem;">₹ {wallet_balance:,}</b>
        </div>
    """, unsafe_allow_html=True)

# 6. METRICS (ONE ROW)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric(t["sav"], f"₹{total_savings:,}")
m2.metric(t["loan"], f"₹{total_loan_given:,}")
m3.metric(t["avail"], f"₹{wallet_balance:,}")
m4.metric(t["members"], active_members)
m5.metric(t["loans"], active_loans)

st.divider()

# 7. SAME DONUT GRAPH (UNCHANGED STYLE)

chart_l, chart_r = st.columns([1.2, 1])

with chart_l:
    fig, ax = plt.subplots(figsize=(4, 4))
    fig.patch.set_facecolor("none")

    ax.pie(
        [total_savings, total_loan_given],
        colors=["#6366f1", "#f43f5e"],
        autopct="%1.0f%%",
        startangle=100,
        pctdistance=0.75,
        wedgeprops={"width": 0.35, "edgecolor": "none"}
    )
    ax.axis("equal")
    st.pyplot(fig)

with chart_r:
    st.markdown(f"### 📅 {t['next_p']}")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            m.first_name,
            m.last_name,
            m.monthly_deposit,
            IFNULL(l.loan_amount, 0) AS loan_amount,
            IFNULL(l.interest_rate, 0) AS interest_rate
        FROM members m
        LEFT JOIN loans l 
            ON l.member_id = m.id AND l.status='active'
        WHERE m.shg_id=%s AND m.status='active'
    """, (shg_id,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    table_data = []

    for r in rows:
        interest = int(r["loan_amount"] * r["interest_rate"] / 100)
        payable = r["monthly_deposit"] + interest

        table_data.append({
            f"{t['members']}": f"{r['first_name']} {r['last_name']}",
            f"₹ {t['next_p']}": payable
        })

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
        height=400
    )

st.divider()

# 8. NAVIGATION

n1, n2, n3 = st.columns(3)
with n1:
    if role == "president":
        if st.button(t["manage"], use_container_width=True):
            st.switch_page("pages/members.py")
with n2:
    if st.button(t["report"], use_container_width=True):
        st.switch_page("pages/reports.py")
with n3:
    if st.button(t["logout"], use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")
