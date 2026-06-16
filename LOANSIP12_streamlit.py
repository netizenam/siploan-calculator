"""
LOANSIP12_streamlit.py — SIP Loan Calculator (Streamlit)
Coli 25: "Already repaying?" mode — field labels change, substitution logic
         with clear disclaimers in result when estimates are used.
Coli 27: Auto-reset on uncheck
Coli 26: "Should I prepay or SIP?" Advisor — compares current ROI vs SIP
         return with plain-language recommendation and math shown.
All Coli 1-24 retained.
"""

import math
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="SIP Loan Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────── PASSWORD GATE ───────────────────────

def check_password():
    if st.session_state.get("authenticated"):
        return True
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
        pwd   = st.text_input("Password", type="password", key="pwd_input", placeholder="Enter password")
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
    return False

if not check_password():
    st.stop()

# ─────────────────────── CSS ───────────────────────

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1A56DB, #1741B0);
        padding: 0.5rem 1rem; border-radius: 8px;
        text-align: center; margin-bottom: 0.8rem;
    }
    .main-header h1  { color: white; font-size: 1.2rem; font-weight: 700; margin: 0; display: inline; }
    .main-header span{ color: #BFD4FF; font-size: 0.8rem; margin-left: 1rem; }

    .tile-grid   { display: grid; grid-template-columns: repeat(3,1fr); gap:6px; margin:0.4rem 0; }
    .tile-grid-6 { display: grid; grid-template-columns: repeat(6,1fr); gap:6px; margin:0.4rem 0; }
    .tile-grid-2 { display: grid; grid-template-columns: repeat(2,1fr); gap:6px; margin:0.4rem 0; }

    .tile     { background:#F8FAFC; border:1px solid #CBD5E1; border-radius:6px; padding:6px 10px; }
    .tile-opt { background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:6px 10px; }
    .tile-mid { background:#FFF7ED; border:1px solid #FED7AA; border-radius:6px; padding:6px 10px; }

    .tile-label { font-size:0.7rem; color:#64748B; margin:0; }
    .tile-value { font-size:1rem;   font-weight:700; margin:0; }

    .val-text  { color:#1E293B; }
    .val-red   { color:#DC2626; }
    .val-green { color:#059669; }
    .val-amber { color:#D97706; }
    .val-blue  { color:#1A56DB; }
    .val-muted { color:#64748B; }

    .solved-box {
        background:#EFF6FF; border:1px solid #BFDBFE;
        border-radius:8px; padding:0.5rem 1rem;
        margin:0.4rem 0 0.6rem; font-size:0.9rem;
        color:#1E40AF; font-weight:600;
    }
    .tip-blue  { background:#EFF6FF; border:1px solid #DBEAFE; border-radius:6px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#1E40AF; margin-bottom:0.4rem; }
    .tip-green { background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#166534; margin-bottom:0.4rem; }
    .tip-amber { background:#FFFBEB; border:1px solid #FDE68A; border-radius:6px; padding:0.4rem 0.8rem; font-size:0.8rem; color:#92400E; margin-bottom:0.4rem; }

    .mid-mode-box { background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:0.6rem 1rem; margin:0.4rem 0; }
    .mid-mode-box p { margin:0; color:#92400E; font-size:0.82rem; }

    .advisor-green { background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:0.7rem 1rem; margin:0.4rem 0; }
    .advisor-green h4 { color:#166534; margin:0 0 0.2rem; font-size:0.95rem; }
    .advisor-green p  { color:#166534; margin:0; font-size:0.82rem; }

    .advisor-amber { background:#FFFBEB; border:1px solid #FDE68A; border-radius:8px; padding:0.7rem 1rem; margin:0.4rem 0; }
    .advisor-amber h4 { color:#92400E; margin:0 0 0.2rem; font-size:0.95rem; }
    .advisor-amber p  { color:#92400E; margin:0; font-size:0.82rem; }

    .advisor-neutral { background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:0.7rem 1rem; margin:0.4rem 0; }
    .advisor-neutral h4 { color:#1E293B; margin:0 0 0.2rem; font-size:0.95rem; }
    .advisor-neutral p  { color:#64748B; margin:0; font-size:0.82rem; }

    .opt-section       { background:white; border:1px solid #BBF7D0; border-radius:10px; padding:1rem 1.2rem; margin-top:0.5rem; }
    .opt-section-title { color:#059669; font-weight:700; font-size:1rem; margin-bottom:0.2rem; }
    .opt-section-sub   { color:#166534; font-size:0.8rem; margin-bottom:0.6rem; }
    .full-divider      { border:none; border-top:2px solid #E2E8F0; margin:1.2rem 0 0.8rem; }

    .section-title-blue  { color:#1A56DB; font-weight:700; font-size:1rem; margin-bottom:0.2rem; }
    .section-title-green { color:#059669; font-weight:700; font-size:1rem; margin-bottom:0.2rem; }
    .section-title-amber { color:#D97706; font-weight:700; font-size:1rem; margin-bottom:0.2rem; }

    #MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}
    .block-container{padding-top:0.5rem;padding-bottom:1rem;}
    div.stButton > button {
        background-color:#1A56DB; color:white; border:none;
        border-radius:6px; padding:0.4rem 1.5rem;
        font-weight:600; font-size:0.9rem;
    }
    div.stButton > button:hover{background-color:#1741B0;color:white;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────── MATH ───────────────────────

def calc_emi(P, roi, months):
    r = roi/100/12
    if r == 0: return P/months
    return P*r*(1+r)**months/((1+r)**months-1)

def calc_principal(emi, roi, months):
    r = roi/100/12
    if r == 0: return emi*months
    return emi*((1+r)**months-1)/(r*(1+r)**months)

def calc_tenure(P, emi, roi):
    r = roi/100/12
    if r == 0: return P/emi
    if emi <= P*r: return None
    return math.log(emi/(emi-P*r))/math.log(1+r)

def calc_roi_bisection(P, emi, months, tol=1e-9):
    lo, hi = 0.0001, 100.0
    for _ in range(400):
        mid = (lo+hi)/2
        e   = calc_emi(P, mid, months)
        if abs(e-emi) < tol: return mid
        if e < emi: lo = mid
        else: hi = mid
    return (lo+hi)/2

def calc_outstanding_balance(P, roi, months_paid, emi):
    """Amortise for months_paid months and return outstanding balance."""
    r   = roi/100/12
    bal = P
    for _ in range(int(months_paid)):
        interest  = bal*r
        principal = emi - interest
        bal       = max(bal - principal, 0)
    return bal

def calc_breakeven_month(P, roi, months):
    r   = roi/100/12
    emi = calc_emi(P, roi, months)
    bal = P
    for m in range(1, months+1):
        interest  = bal*r
        principal = emi - interest
        if principal >= interest: return m
        bal -= principal
    return months

def calc_sip_corpus(monthly_sip, sip_return, months):
    r = sip_return/100/12
    if r == 0: return monthly_sip*months
    return monthly_sip*((1+r)**months-1)/r*(1+r)

def find_early_closure(P, roi, months, monthly_sip, sip_return):
    r_loan = roi/100/12
    r_sip  = sip_return/100/12
    emi    = calc_emi(P, roi, months)
    bal    = P; corpus = 0.0
    for m in range(1, months+1):
        interest  = bal*r_loan
        principal = emi - interest
        bal       = max(bal-principal, 0)
        corpus    = corpus*(1+r_sip)+monthly_sip
        if corpus >= bal:
            return m, m/12, (months-m)/12, bal
    return None, None, 0.0, 0.0

def fmt(n):
    n = round(n,2)
    if n >= 10_000_000: return f"₹{n/10_000_000:.2f} Cr"
    if n >= 100_000:    return f"₹{n/100_000:.2f} L"
    return f"₹{n:,.2f}"

def tile(label, value, css, style="tile"):
    return f'<div class="{style}"><p class="tile-label">{label}</p><p class="tile-value {css}">{value}</p></div>'

def grid(tiles):  return f'<div class="tile-grid">{"".join(tiles)}</div>'
def grid6(tiles): return f'<div class="tile-grid-6">{"".join(tiles)}</div>'
def grid2(tiles): return f'<div class="tile-grid-2">{"".join(tiles)}</div>'


# ─────────────────────── HEADER ───────────────────────

st.markdown("""
<div class="main-header">
  <h1>💰 SIP Loan Calculator</h1>
  <span>Fill any 3 fields, leave 1 blank — click Calculate to solve &nbsp;·&nbsp; SIP updates automatically</span>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1,1], gap="medium")

# ═══════════════════════════════════════════
#  LEFT — LOAN INPUTS
# ═══════════════════════════════════════════
with left:
    st.markdown('<p class="section-title-blue">Loan Details</p>', unsafe_allow_html=True)

    # Coli 25 / Coli 27: Already repaying toggle with auto-reset on uncheck
    prev_mid = st.session_state.get("prev_mid_loan", False)
    mid_loan = st.checkbox("Already repaying this loan?", key="mid_loan")
    if prev_mid and not mid_loan:
        for key in ["loan_result", "budget"]:
            st.session_state.pop(key, None)
        st.session_state["prev_mid_loan"] = False
        st.rerun()
    st.session_state["prev_mid_loan"] = mid_loan

    if not mid_loan:
        st.markdown('<div class="tip-blue">Fill any 3 fields and leave 1 blank. Click <b>Calculate</b> to solve it.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            amt_str = st.text_input("Loan Amount (₹)",  placeholder="e.g. 10000000", key="amt")
            ten_str = st.text_input("Tenure (years)",    placeholder="e.g. 15",       key="ten")
        with c2:
            roi_str = st.text_input("Annual ROI (%)",    placeholder="e.g. 8.5",      key="roi")
            emi_str = st.text_input("Monthly EMI (₹)",   placeholder="leave blank",    key="emi")
    else:
        st.markdown('<div class="tip-amber">Enter your loan details below. Fields marked * are required. Others improve accuracy if available.</div>', unsafe_allow_html=True)
        st.markdown('<div class="mid-mode-box"><p>ℹ️ Results will clearly indicate where estimates have been used instead of actual figures.</p></div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            amt_str  = st.text_input("Original Loan Amount (₹) *",   placeholder="e.g. 10000000", key="amt")
            roi_str  = st.text_input("Current ROI (%) *",             placeholder="e.g. 9.5",      key="roi")
            paid_str = st.text_input("EMIs already paid *",           placeholder="e.g. 24",       key="paid")
        with c2:
            emi_str  = st.text_input("EMI currently paying (₹) *",   placeholder="e.g. 95000",    key="emi")
            orig_roi_str = st.text_input("Original ROI (%) — if different", placeholder="optional", key="orig_roi")
            bal_str  = st.text_input("Outstanding Balance (₹) — from bank statement", placeholder="optional", key="bal")
            rem_ten_str  = st.text_input("Remaining Tenure (years) — from bank statement", placeholder="optional", key="rem_ten")
        ten_str = ""  # not used in mid-loan mode

    calc_clicked = st.button("Calculate")

# ─── PROCESS ────────────────────────────────
result_data = None
error_msg   = None
solved_key  = None
disclaimers = []

def p(s):
    s = s.strip().replace(",","")
    return None if s=="" else float(s)

if calc_clicked:
    try:
        if not mid_loan:
            # ── FRESH LOAN MODE ──
            iv     = {"amt": p(amt_str), "roi": p(roi_str), "ten": p(ten_str), "emi": p(emi_str)}
            blanks = [k for k,v in iv.items() if v is None]
            known  = {k:v for k,v in iv.items() if v is not None}

            if len(blanks) > 1:
                error_msg = f"Please fill in {len(blanks)-1} more field(s). Exactly 1 should be blank."
            else:
                if len(blanks) == 1:
                    blank = blanks[0]; solved_key = blank
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
                            error_msg = "EMI is too small to repay this loan."
                        else:
                            n = int(math.ceil(res)); iv["ten"] = n/12
                if not error_msg:
                    P   = iv["amt"]; roi = iv["roi"]
                    n   = int(round(iv["ten"]*12))
                    emi = calc_emi(P, roi, n)
                    result_data = (P, roi, n, emi, solved_key, False, [], None, None)
                    st.session_state["loan_result"] = result_data

        else:
            # ── MID-LOAN MODE (Coli 25) ──
            orig_amt  = p(amt_str)
            curr_roi  = p(roi_str)
            paid_emis = p(paid_str)
            curr_emi  = p(emi_str)
            orig_roi  = p(orig_roi_str) if orig_roi_str.strip() else None
            bal_known = p(bal_str) if bal_str.strip() else None
            rem_ten_known = p(rem_ten_str) if rem_ten_str.strip() else None

            # Validate mandatory fields
            missing = []
            if orig_amt  is None: missing.append("Original Loan Amount")
            if curr_roi  is None: missing.append("Current ROI")
            if paid_emis is None: missing.append("EMIs already paid")
            if curr_emi  is None: missing.append("EMI currently paying")
            if missing:
                error_msg = f"Please enter: {', '.join(missing)}"
            else:
                paid_emis = int(paid_emis)
                roi_used  = curr_roi

                # Derive original tenure from original amt + original roi + curr emi (approx)
                # Use original ROI if provided for this derivation
                roi_for_orig = orig_roi if orig_roi else curr_roi
                orig_ten_months_approx = None
                try:
                    res = calc_tenure(orig_amt, curr_emi, roi_for_orig)
                    if res:
                        orig_ten_months_approx = int(math.ceil(res))
                except:
                    pass

                # Remaining tenure
                if rem_ten_known:
                    rem_months = int(round(rem_ten_known * 12))
                elif orig_ten_months_approx:
                    rem_months = max(orig_ten_months_approx - paid_emis, 1)
                    disclaimers.append("⚠️ Remaining tenure estimated as original tenure minus EMIs paid. May differ if bank has extended your tenure due to rate changes.")
                else:
                    error_msg = "Could not determine remaining tenure. Please enter it directly."

                if not error_msg:
                    # Outstanding balance
                    if bal_known:
                        outstanding = bal_known
                    else:
                        # Amortise using original ROI for paid months, current ROI conceptually
                        roi_for_amort = orig_roi if orig_roi else curr_roi
                        outstanding = calc_outstanding_balance(orig_amt, roi_for_amort, paid_emis, curr_emi)
                        if orig_roi and orig_roi != curr_roi:
                            disclaimers.append("⚠️ Outstanding balance estimated using original ROI for months already paid, then current ROI. Figures are approximate — use your bank statement for accuracy.")
                        else:
                            disclaimers.append("⚠️ Outstanding balance estimated from amortisation schedule. For accuracy, use the figure from your latest bank statement.")

                    result_data = (outstanding, roi_used, rem_months, curr_emi, None, True, disclaimers, orig_amt, paid_emis)
                    st.session_state["loan_result"] = result_data

    except Exception as e:
        error_msg = str(e)

    if error_msg:
        st.session_state.pop("loan_result", None)

elif "loan_result" in st.session_state:
    result_data = st.session_state["loan_result"]

# ─── LEFT RESULT ────────────────────────────
with left:
    if error_msg:
        st.error(error_msg)
    elif result_data:
        P, roi, n, emi, sk, is_mid, discs, orig_amt, paid_emis = result_data

        if sk:
            labels = {"amt":"Loan Amount","roi":"Annual ROI","ten":"Tenure (years)","emi":"Monthly EMI"}
            values = {"amt":fmt(P),"roi":f"{roi:.2f}%","ten":f"{n/12:.2f} years","emi":fmt(emi)}
            st.markdown(f'<div class="solved-box">✅ Solved: <b>{labels[sk]}</b> = <b>{values[sk]}</b></div>',
                        unsafe_allow_html=True)

        # Show disclaimers (Coli 25)
        for d in discs:
            st.warning(d)

        total_pay = emi*n; total_int = total_pay-P
        int_ratio = total_int/P*100
        flat_rate = (total_int/P)/(n/12)*100
        be_month  = calc_breakeven_month(P, roi, n)
        cost_mult = total_pay/P

        def tc(key, default): return "val-red" if key==sk else default

        if is_mid:
            st.markdown('<p class="section-title-amber" style="margin-top:0.6rem">Your Loan Position</p>',
                        unsafe_allow_html=True)
            st.markdown(grid([
                tile("Outstanding Balance", fmt(P),                              "val-amber"),
                tile("Current ROI",          f"{roi:.2f}%",                      "val-text"),
                tile("Remaining Tenure",    f"{n/12:.1f} yrs ({n} mths)",        "val-text"),
                tile("Current EMI",          fmt(emi),                           "val-text"),
                tile("Interest yet to pay",  fmt(total_int),                     "val-red"),
                tile("Total yet to pay",     fmt(total_pay),                     "val-text"),
            ]), unsafe_allow_html=True)
        else:
            st.markdown('<p class="section-title-blue" style="margin-top:0.6rem">Result</p>',
                        unsafe_allow_html=True)
            st.markdown(grid([
                tile("Loan Amount",         fmt(P),                              tc("amt","val-text")),
                tile("Annual ROI",           f"{roi:.2f}%",                      tc("roi","val-text")),
                tile("Tenure",              f"{n/12:.1f} yrs ({n} mths)",        tc("ten","val-text")),
                tile("Monthly EMI",          fmt(emi),                           tc("emi","val-text")),
                tile("Total Payment",        fmt(total_pay),                     "val-text"),
                tile("Total Interest",       fmt(total_int),                     "val-red"),
                tile("Interest / Principal", f"{int_ratio:.1f}%",                "val-red"),
                tile("Flat Interest Rate",   f"{flat_rate:.2f}% p.a.",           "val-amber"),
                tile("Break-even Month",     f"Month {be_month} (Yr {be_month/12:.1f})", "val-amber"),
                tile("Loan Cost Multiple",   f"{cost_mult:.2f}× principal",      "val-amber"),
            ]), unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  RIGHT — SIP
# ═══════════════════════════════════════════
with right:
    st.markdown('<p class="section-title-green">SIP Acceleration</p>', unsafe_allow_html=True)
    st.markdown('<div class="tip-green">Invest a % of your EMI as SIP — watch your corpus close the loan early.</div>',
                unsafe_allow_html=True)
    sip_pct = st.number_input("SIP as % of EMI",              min_value=1.0, max_value=200.0, value=10.0, step=1.0)
    sip_ret = st.number_input("Expected SIP return (% p.a.)", min_value=1.0, max_value=50.0,  value=10.0, step=0.5)
    st.markdown('<p class="section-title-green" style="margin-top:0.6rem">SIP Result</p>', unsafe_allow_html=True)

    loan_data = st.session_state.get("loan_result", None)
    if not loan_data:
        st.info("Complete loan details on the left and click Calculate to see SIP projection.")
    else:
        P, roi, n, emi, _, is_mid, discs, _, _ = loan_data
        monthly_sip = emi * sip_pct / 100

        closure_month, closure_year, years_saved, bal_at_closure = \
            find_early_closure(P, roi, n, monthly_sip, sip_ret)
        corpus_full = calc_sip_corpus(monthly_sip, sip_ret, n)

        st.markdown(grid([
            tile("Monthly EMI",  fmt(emi),          "val-text"),
            tile("Monthly SIP",  fmt(monthly_sip),   "val-blue"),
            tile("SIP % of EMI", f"{sip_pct:.1f}%",  "val-muted"),
        ]), unsafe_allow_html=True)

        # Coli 26: Should I prepay or SIP? Advisor
        diff = sip_ret - roi
        if diff > 0.5:
            adv_class = "advisor-green"
            adv_icon  = "✅"
            adv_head  = f"Invest in SIP — mathematically better than prepaying"
            adv_body  = (f"Your expected SIP return ({sip_ret:.1f}%) exceeds your loan ROI ({roi:.2f}%) "
                         f"by {diff:.1f}% p.a. Every rupee invested in SIP works harder than prepaying the loan.")
        elif diff < -0.5:
            adv_class = "advisor-amber"
            adv_icon  = "⚠️"
            adv_head  = f"Prepaying the loan is mathematically better"
            adv_body  = (f"Your loan ROI ({roi:.2f}%) exceeds your expected SIP return ({sip_ret:.1f}%) "
                         f"by {abs(diff):.1f}% p.a. Every rupee prepaid saves more than SIP returns. "
                         f"Consider increasing SIP return assumption or prepaying instead.")
        else:
            adv_class = "advisor-neutral"
            adv_icon  = "⚖️"
            adv_head  = f"Break-even — SIP and prepayment give equivalent results"
            adv_body  = (f"SIP return ({sip_ret:.1f}%) and loan ROI ({roi:.2f}%) are nearly equal "
                         f"(difference: {abs(diff):.1f}% p.a.). Either approach gives similar financial benefit. "
                         f"SIP builds a liquid corpus; prepayment reduces debt directly.")

        st.markdown(f"""
        <div class="{adv_class}">
            <h4>{adv_icon} {adv_head}</h4>
            <p>{adv_body}</p>
        </div>
        """, unsafe_allow_html=True)

        if closure_month:
            interest_saved = emi*(n-closure_month)
            st.success(f"✅ Loan closure possible at Year **{closure_year:.1f}** — **{years_saved:.1f} years saved!**")
            st.caption(
                f"By investing {fmt(monthly_sip)}/month ({sip_pct:.1f}% of EMI) in a SIP at {sip_ret:.1f}% p.a., "
                f"your corpus matches the {'outstanding' if is_mid else 'loan'} balance at Month {closure_month} "
                f"(Year {closure_year:.1f}), saving {years_saved:.1f} years of EMI payments."
            )
            st.markdown(grid([
                tile("Original tenure" if not is_mid else "Remaining tenure", f"{n/12:.1f} years", "val-text"),
                tile("Effective closure",              f"{closure_year:.1f} years", "val-green"),
                tile("Years saved",                   f"{years_saved:.1f} years",  "val-green"),
                tile("SIP corpus if held full term",   fmt(corpus_full),            "val-blue"),
                tile("Outstanding balance at closure", fmt(bal_at_closure),         "val-green"),
                tile("Approx interest saved",          fmt(interest_saved),         "val-green"),
            ]), unsafe_allow_html=True)
            st.caption("'SIP corpus if held full term' = SIP value if continued for the full tenure without early closure.")
        else:
            st.error("SIP corpus does not surpass loan balance within tenure.")
            st.caption(
                f"At {sip_pct:.1f}% of EMI invested at {sip_ret:.1f}% p.a., the corpus does not match "
                f"the outstanding balance within {n//12} years. Try increasing the SIP % or the return rate."
            )
            st.markdown(grid([
                tile("SIP corpus if held full term", fmt(corpus_full), "val-blue"),
            ]), unsafe_allow_html=True)
            st.caption("'SIP corpus if held full term' = SIP value if continued for the full tenure.")

# ═══════════════════════════════════════════
#  FULL WIDTH — BUDGET-NEUTRAL PLANNER
# ═══════════════════════════════════════════
loan_data   = st.session_state.get("loan_result", None)
sip_pct_val = sip_pct if 'sip_pct' in dir() else 10.0
sip_ret_val = sip_ret if 'sip_ret' in dir() else 10.0

if loan_data:
    P, roi, n, emi, _, is_mid, _, _, _ = loan_data

    st.markdown('<hr class="full-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="opt-section">
      <p class="opt-section-title">💡 Want to optimise your borrowing?</p>
      <p class="opt-section-sub">Enter your total monthly budget — we'll find the ideal reduced loan + SIP combination at zero extra cost.</p>
    </div>
    """, unsafe_allow_html=True)

    bc1, bc2, bc3 = st.columns([2,1,3])
    with bc1:
        budget_str = st.text_input("My total monthly budget (₹) for EMI & SIP",
                                   placeholder="e.g. 120000", key="budget")

    if budget_str.strip():
        try:
            budget   = float(budget_str.replace(",",""))
            opt_sip  = budget * sip_pct_val / 100
            opt_emi  = budget - opt_sip
            opt_loan = calc_principal(opt_emi, roi, n)

            if opt_loan <= 0 or opt_emi <= 0:
                st.warning("Budget too low for this ROI and tenure. Please try a higher amount.")
            else:
                loan_diff = P - opt_loan
                opt_closure_month, opt_closure_year, opt_years_saved, _ = \
                    find_early_closure(opt_loan, roi, n, opt_sip, sip_ret_val)

                st.markdown(
                    f'<div class="solved-box" style="background:#F0FDF4;border-color:#BBF7D0;color:#166534;">'
                    f'✅ Optimal combo found for a total budget of <b>{fmt(budget)}/month</b>'
                    f'</div>', unsafe_allow_html=True)

                lbl1 = "Reduced loan" if not is_mid else "Reduced outstanding"
                st.markdown(grid6([
                    tile(lbl1,               fmt(opt_loan),                                        "val-green", "tile-opt"),
                    tile("Reduction",         fmt(loan_diff),                                       "val-green", "tile-opt"),
                    tile("New EMI",           fmt(opt_emi),                                         "val-text",  "tile-opt"),
                    tile("Monthly SIP",       fmt(opt_sip),                                         "val-blue",  "tile-opt"),
                    tile("Total/month",       fmt(opt_emi+opt_sip),                                "val-text",  "tile-opt"),
                    tile("Loan closes at",
                         f"Year {opt_closure_year:.1f}" if opt_closure_month else "No early closure",
                         "val-green", "tile-opt"),
                ]), unsafe_allow_html=True)

                if opt_closure_month:
                    st.caption(
                        f"By borrowing {fmt(loan_diff)} less, your EMI drops to {fmt(opt_emi)}. "
                        f"Invest the freed-up {fmt(opt_sip)}/month as SIP and close the loan at "
                        f"Year {opt_closure_year:.1f} — saving {opt_years_saved:.1f} years. "
                        f"Total monthly outflow stays at {fmt(budget)}."
                    )
        except ValueError:
            st.warning("Please enter a valid number for your budget.")
