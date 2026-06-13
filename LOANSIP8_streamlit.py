"""
LOANSIP8_streamlit.py — SIP Loan Calculator (Streamlit)
Added: Password protection via Streamlit Secrets.
To set/change password:
  Streamlit Cloud → Your App → Settings → Secrets → add:
  PASSWORD = "your_chosen_password"
"""

import math
import streamlit as st

st.set_page_config(
    page_title="SIP Loan Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────── PASSWORD GATE ───────────────────────

def check_password():
    """Returns True if the user has entered the correct password."""

    # If already authenticated this session, let through
    if st.session_state.get("authenticated"):
        return True

    # Password form
    st.markdown("""
    <div style="max-width:400px;margin:4rem auto;background:white;
         border:1px solid #CBD5E1;border-radius:10px;padding:2rem;">
        <h2 style="color:#1A56DB;text-align:center;margin-bottom:0.3rem">💰 SIP Loan Calculator</h2>
        <p style="color:#64748B;text-align:center;font-size:0.85rem;margin-bottom:1.5rem">
            Enter password to continue</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Password", type="password", key="pwd_input",
                            placeholder="Enter password")
        login = st.button("Login", use_container_width=True)

        if login:
            try:
                correct = st.secrets["PASSWORD"]
            except Exception:
                st.error("Password not configured. Please set PASSWORD in Streamlit Secrets.")
                return False

            if pwd == correct:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

        if st.session_state.get("show_wrong"):
            st.error("Incorrect password.")

    return False

if not check_password():
    st.stop()  # Stop here — do not render the app

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1A56DB, #1741B0);
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1.2rem;
    }
    .main-header h1 { color: white; font-size: 1.8rem; font-weight: 700; margin: 0; }
    .main-header p  { color: #BFD4FF; font-size: 0.85rem; margin: 0.3rem 0 0; }

    .tile-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 6px;
        margin: 0.5rem 0;
    }
    .tile {
        background: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 6px 10px;
    }
    .tile-label { font-size: 0.7rem; color: #64748B; margin: 0; }
    .tile-value { font-size: 1rem; font-weight: 700; margin: 0; }
    .val-text  { color: #1E293B; }
    .val-red   { color: #DC2626; }
    .val-green { color: #059669; }
    .val-amber { color: #D97706; }
    .val-blue  { color: #1A56DB; }
    .val-muted { color: #64748B; }

    .solved-box {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin: 0.5rem 0 0.8rem;
        font-size: 0.95rem;
        color: #1E40AF;
        font-weight: 600;
    }
    .tip-blue {
        background: #EFF6FF; border: 1px solid #DBEAFE;
        border-radius: 6px; padding: 0.5rem 0.8rem;
        font-size: 0.8rem; color: #1E40AF; margin-bottom: 0.5rem;
    }
    .tip-green {
        background: #F0FDF4; border: 1px solid #BBF7D0;
        border-radius: 6px; padding: 0.5rem 0.8rem;
        font-size: 0.8rem; color: #166534; margin-bottom: 0.5rem;
    }
    .section-title-blue  { color: #1A56DB; font-weight: 700; font-size: 1rem; margin-bottom: 0.3rem; }
    .section-title-green { color: #059669; font-weight: 700; font-size: 1rem; margin-bottom: 0.3rem; }
    #MainMenu { visibility: hidden; } footer { visibility: hidden; } header { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    div.stButton > button {
        background-color: #1A56DB; color: white; border: none;
        border-radius: 6px; padding: 0.4rem 1.5rem;
        font-weight: 600; font-size: 0.9rem;
    }
    div.stButton > button:hover { background-color: #1741B0; color: white; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────── MATH ───────────────────────

def calc_emi(P, roi, months):
    r = roi / 100 / 12
    if r == 0: return P / months
    return P * r * (1+r)**months / ((1+r)**months - 1)

def calc_principal(emi, roi, months):
    r = roi / 100 / 12
    if r == 0: return emi * months
    return emi * ((1+r)**months - 1) / (r * (1+r)**months)

def calc_tenure(P, emi, roi):
    r = roi / 100 / 12
    if r == 0: return P / emi
    if emi <= P * r: return None
    return math.log(emi / (emi - P*r)) / math.log(1+r)

def calc_roi_bisection(P, emi, months, tol=1e-9):
    lo, hi = 0.0001, 100.0
    for _ in range(400):
        mid = (lo+hi)/2
        e = calc_emi(P, mid, months)
        if abs(e-emi) < tol: return mid
        if e < emi: lo = mid
        else: hi = mid
    return (lo+hi)/2

def calc_breakeven_month(P, roi, months):
    r = roi/100/12
    emi = calc_emi(P, roi, months)
    bal = P
    for m in range(1, months+1):
        interest = bal*r
        principal = emi - interest
        if principal >= interest: return m
        bal -= principal
    return months

def calc_sip_corpus(P, roi, months, sip_pct, sip_return):
    emi = calc_emi(P, roi, months)
    sip = emi * sip_pct / 100
    r = sip_return/100/12
    if r == 0: return sip * months
    return sip * ((1+r)**months - 1) / r * (1+r)

def find_early_closure(P, roi, months, sip_pct, sip_return):
    r_loan = roi/100/12
    r_sip  = sip_return/100/12
    emi    = calc_emi(P, roi, months)
    sip    = emi * sip_pct/100
    bal    = P; corpus = 0.0
    for m in range(1, months+1):
        interest  = bal*r_loan
        principal = emi - interest
        bal       = max(bal - principal, 0)
        corpus    = corpus*(1+r_sip) + sip
        if corpus >= bal:
            return m, m/12, (months-m)/12, emi, sip
    return None, None, 0.0, emi, emi*sip_pct/100

def fmt(n):
    n = round(n,2)
    if n >= 10_000_000: return f"₹{n/10_000_000:.2f} Cr"
    if n >= 100_000:    return f"₹{n/100_000:.2f} L"
    return f"₹{n:,.2f}"

def tile(label, value, css):
    return f'<div class="tile"><p class="tile-label">{label}</p><p class="tile-value {css}">{value}</p></div>'

def grid(tiles):
    return f'<div class="tile-grid">{"".join(tiles)}</div>'


# ─────────────────────── HEADER ───────────────────────

st.markdown("""
<div class="main-header">
  <h1>💰 SIP Loan Calculator</h1>
  <p>Fill any 3 fields, leave 1 blank — click Calculate to solve &nbsp;·&nbsp; SIP updates automatically</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1,1], gap="medium")

# ═══════════════════════════════════════════
#  LEFT
# ═══════════════════════════════════════════
with left:
    st.markdown('<p class="section-title-blue">Loan Details</p>', unsafe_allow_html=True)
    st.markdown('<div class="tip-blue">Fill any 3 fields and leave 1 blank. Click <b>Calculate</b> to solve it.</div>', unsafe_allow_html=True)

    amt_str = st.text_input("Loan Amount (₹)",  placeholder="e.g. 10000000", key="amt")
    roi_str = st.text_input("Annual ROI (%)",    placeholder="e.g. 8.5",      key="roi")
    ten_str = st.text_input("Tenure (years)",    placeholder="e.g. 15",       key="ten")
    emi_str = st.text_input("Monthly EMI (₹)",   placeholder="leave blank to solve", key="emi")

    calc_clicked = st.button("Calculate")

# ═══════════════════════════════════════════
#  PROCESS
# ═══════════════════════════════════════════
result_data = None
error_msg   = None
solved_key  = None

if calc_clicked:
    def p(s):
        s = s.strip().replace(",","")
        return None if s=="" else (float(s) if s else None)

    try:
        iv = {"amt": p(amt_str), "roi": p(roi_str), "ten": p(ten_str), "emi": p(emi_str)}
        blanks = [k for k,v in iv.items() if v is None]
        known  = {k:v for k,v in iv.items() if v is not None}

        if len(blanks) > 1:
            error_msg = f"Please fill in {len(blanks)-1} more field(s). Exactly 1 should be blank."
        else:
            if len(blanks) == 1:
                blank = blanks[0]
                solved_key = blank
                if blank == "emi":
                    n = int(round(known["ten"]*12))
                    iv["emi"] = calc_emi(known["amt"], known["roi"], n)
                elif blank == "amt":
                    n = int(round(known["ten"]*12))
                    iv["amt"] = calc_principal(known["emi"], known["roi"], n)
                elif blank == "roi":
                    n = int(round(known["ten"]*12))
                    iv["roi"] = calc_roi_bisection(known["amt"], known["emi"], n)
                elif blank == "ten":
                    res = calc_tenure(known["amt"], known["emi"], known["roi"])
                    if res is None:
                        error_msg = "EMI is too small to repay this loan. Please increase EMI."
                    else:
                        n = int(math.ceil(res))
                        iv["ten"] = n/12

            if not error_msg:
                P   = iv["amt"]
                roi = iv["roi"]
                n   = int(round(iv["ten"]*12))
                emi = calc_emi(P, roi, n)
                result_data = (P, roi, n, emi, solved_key)
                st.session_state["loan_result"] = result_data

    except Exception as e:
        error_msg = str(e)

    if error_msg:
        st.session_state.pop("loan_result", None)

elif "loan_result" in st.session_state:
    result_data = st.session_state["loan_result"]

# ═══════════════════════════════════════════
#  LEFT — RESULT
# ═══════════════════════════════════════════
with left:
    if error_msg:
        st.error(error_msg)
    elif result_data:
        P, roi, n, emi, sk = result_data

        # Show solved value prominently
        labels = {"amt":"Loan Amount","roi":"Annual ROI","ten":"Tenure (years)","emi":"Monthly EMI"}
        values = {
            "amt": fmt(P),
            "roi": f"{roi:.2f}%",
            "ten": f"{n/12:.2f} years",
            "emi": fmt(emi)
        }
        if sk:
            st.markdown(
                f'<div class="solved-box">✅ Solved: <b>{labels[sk]}</b> = <b>{values[sk]}</b></div>',
                unsafe_allow_html=True)

        total_pay = emi*n
        total_int = total_pay - P
        int_ratio = total_int/P*100
        flat_rate = (total_int/P)/(n/12)*100
        be_month  = calc_breakeven_month(P, roi, n)
        cost_mult = total_pay/P

        def tc(key, default):
            return "val-red" if key==sk else default

        st.markdown('<p class="section-title-blue" style="margin-top:0.8rem">Result</p>', unsafe_allow_html=True)
        st.markdown(grid([
            tile("Loan Amount",         fmt(P),                       tc("amt","val-text")),
            tile("Annual ROI",           f"{roi:.2f}%",                tc("roi","val-text")),
            tile("Tenure",              f"{n/12:.1f} yrs ({n} mths)", tc("ten","val-text")),
            tile("Monthly EMI",          fmt(emi),                     tc("emi","val-text")),
            tile("Total Payment",        fmt(total_pay),               "val-text"),
            tile("Total Interest",       fmt(total_int),               "val-red"),
            tile("Interest / Principal", f"{int_ratio:.1f}%",          "val-red"),
            tile("Flat Interest Rate",   f"{flat_rate:.2f}% p.a.",     "val-amber"),
            tile("Break-even Month",     f"Month {be_month} (Yr {be_month/12:.1f})", "val-amber"),
            tile("Loan Cost Multiple",   f"{cost_mult:.2f}× principal","val-amber"),
        ]), unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  RIGHT — SIP
# ═══════════════════════════════════════════
with right:
    st.markdown('<p class="section-title-green">SIP Acceleration</p>', unsafe_allow_html=True)
    st.markdown('<div class="tip-green">Invest a % of your EMI as SIP — watch your corpus close the loan early.</div>', unsafe_allow_html=True)

    sip_pct = st.number_input("SIP as % of EMI",              min_value=1.0, max_value=200.0, value=10.0, step=1.0)
    sip_ret = st.number_input("Expected SIP return (% p.a.)", min_value=1.0, max_value=50.0,  value=10.0, step=0.5)

    st.markdown('<p class="section-title-green" style="margin-top:0.8rem">SIP Result</p>', unsafe_allow_html=True)

    loan_data = st.session_state.get("loan_result", None)

    if not loan_data:
        st.info("Complete loan details on the left and click Calculate to see SIP projection.")
    else:
        P, roi, n, emi, _ = loan_data
        monthly_sip = emi * sip_pct / 100

        closure_month, closure_year, years_saved, _, _ = find_early_closure(P, roi, n, sip_pct, sip_ret)
        corpus_at_end = calc_sip_corpus(P, roi, n, sip_pct, sip_ret)

        st.markdown(grid([
            tile("Monthly EMI",  fmt(emi),         "val-text"),
            tile("Monthly SIP",  fmt(monthly_sip),  "val-blue"),
            tile("SIP % of EMI", f"{sip_pct:.1f}%", "val-muted"),
        ]), unsafe_allow_html=True)

        if closure_month:
            interest_saved = emi * (n - closure_month)
            st.success(f"✅ Loan closure possible at Year **{closure_year:.1f}** — **{years_saved:.1f} years saved!**")
            st.caption(
                f"By investing {fmt(monthly_sip)}/month ({sip_pct:.1f}% of EMI) in a SIP at {sip_ret:.1f}% p.a., "
                f"your corpus will match the outstanding loan balance at Month {closure_month} (Year {closure_year:.1f}), "
                f"allowing early pre-closure and saving {years_saved:.1f} years of EMI payments."
            )
            st.markdown(grid([
                tile("Original tenure",      f"{n/12:.1f} years",        "val-text"),
                tile("Effective closure",     f"{closure_year:.1f} years", "val-green"),
                tile("Years saved",           f"{years_saved:.1f} years",  "val-green"),
                tile("Approx interest saved", fmt(interest_saved),         "val-green"),
                tile("SIP corpus at tenure end", fmt(corpus_at_end),       "val-blue"),
            ]), unsafe_allow_html=True)
        else:
            st.error("SIP corpus does not surpass loan balance within tenure.")
            st.caption(
                f"At {sip_pct:.1f}% of EMI invested at {sip_ret:.1f}% p.a., the corpus does not match "
                f"the outstanding balance within {n//12} years. Try increasing the SIP % or the return rate."
            )
            st.markdown(grid([
                tile("SIP corpus at tenure end", fmt(corpus_at_end), "val-blue"),
            ]), unsafe_allow_html=True)
