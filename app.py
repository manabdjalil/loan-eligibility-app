import streamlit as st

# ==================================================
# Page configuration
# ==================================================
st.set_page_config(
    page_title="Loan Eligibility Pre-Screening",
    page_icon="💳",
    layout="centered"
)

# ==================================================
# Title & introduction
# ==================================================
st.title("💳 Loan Eligibility Pre-Screening App")

st.markdown(
    """
    This application demonstrates an **early loan eligibility screening system**.
    
    The logic is inspired by a trained machine learning model and is designed to
    **support decision-making**, not replace bank approval.
    """
)

st.divider()

# ==================================================
# Sidebar — Applicant Inputs
# ==================================================
st.sidebar.header("🧍 Applicant Profile")

age = st.sidebar.slider("Age", 18, 60, 25)

education = st.sidebar.selectbox(
    "Highest Education Level",
    ["Associate", "Bachelor", "Master"]
)

is_fresh_grad = st.sidebar.selectbox(
    "Fresh graduate / limited credit history?",
    ["No", "Yes"],
    help="Fresh graduates or applicants with limited credit history require additional review."
)

home_ownership = st.sidebar.selectbox(
    "Home Ownership Status",
    ["Rent", "Own", "Mortgage"]
)

previous_default = st.sidebar.selectbox(
    "Any previous loan defaults?",
    ["No", "Yes"]
)

st.sidebar.header("💰 Financial Information")

income = st.sidebar.number_input(
    "Monthly Income (RM)",
    min_value=0.0,
    step=500.0
)

loan_amount = st.sidebar.number_input(
    "Loan Amount Requested (RM)",
    min_value=0.0,
    step=1000.0
)

# ==================================================
# Proxy approval probability estimator
# (Deployment-safe, transparent logic)
# ==================================================
def estimate_approval_probability(
    income, loan_amount, emp_exp, credit_score, prev_default
):
    score = 0.0

    if income >= 4000:
        score += 0.25
    if loan_amount / max(income, 1) <= 0.30:
        score += 0.25
    if credit_score >= 650:
        score += 0.20
    if emp_exp >= 2:
        score += 0.20
    if prev_default == "No":
        score += 0.10

    return min(score, 0.95)

# ==================================================
# Main section — Summary
# ==================================================
st.subheader("📄 Application Summary")

st.info(
    f"""
    **Monthly Income:** RM {income:,.2f}  
    **Loan Amount Requested:** RM {loan_amount:,.2f}  
    **Fresh Graduate / Limited Credit:** {is_fresh_grad}
    """
)

loan_to_income = loan_amount / max(income, 1)
st.write(f"📈 **Loan-to-Income Ratio:** {loan_to_income:.2f}")

st.divider()

# ==================================================
# Eligibility Assessment
# ==================================================
st.subheader("📊 Eligibility Assessment")

if st.button("🔍 Check Eligibility"):

    # Assumptions based on profile
    if is_fresh_grad == "Yes":
        emp_exp = 0
        credit_score = 600
    else:
        emp_exp = 5
        credit_score = 700

    prob = estimate_approval_probability(
        income,
        loan_amount,
        emp_exp,
        credit_score,
        previous_default
    )

    st.metric(
        label="Estimated Approval Probability",
        value=f"{prob:.2%}"
    )

    st.progress(int(prob * 100))
    st.caption("Approval likelihood indicator")

    if is_fresh_grad == "Yes":
        st.warning(
            "⚠️ **Fresh graduate / limited credit profile detected.**\n\n"
            "Based on prior analysis, automated decisions for this group are less reliable. "
            "Manual review is recommended."
        )

        if prob >= 0.80:
            st.info("📝 **Recommendation:** Conditional approval subject to verification.")
        else:
            st.info("📝 **Recommendation:** Further assessment required.")

    else:
        if prob >= 0.75:
            st.success("✅ **Likely eligible for approval.**")
        elif prob >= 0.50:
            st.warning("⚠️ **Borderline case — additional review advised.**")
        else:
            st.error("❌ **Low likelihood of approval.**")

# ==================================================
# Disclaimer
# ==================================================
st.divider()
st.caption(
    "⚖️ Disclaimer: This application is a **decision-support demonstration**. "
    "It reflects model-inspired logic and does not guarantee loan approval."
)
