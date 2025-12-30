import streamlit as st
import joblib
import pandas as pd

# ==================================================
# Page Configuration
# ==================================================
st.set_page_config(
    page_title="Loan Eligibility Checker",
    page_icon="💳",
    layout="centered"
)

# ==================================================
# Load Model (cached for performance)
# ==================================================
@st.cache_resource
def load_model():
    return joblib.load("best_risk_model_pipeline.joblib")

model = load_model()

# ==================================================
# App Title & Introduction
# ==================================================
st.title("💳 Loan Eligibility Pre-Screening App")

st.markdown(
    """
    This application provides an **early loan eligibility assessment** using
    machine learning.  
    It is designed to **support decision-making** and does **not constitute
    final loan approval**.
    """
)

st.divider()

# ==================================================
# Sidebar — Applicant Inputs
# ==================================================
st.sidebar.header("🧍 Applicant Profile")

age = st.sidebar.slider(
    "Age",
    min_value=18,
    max_value=60,
    value=25,
    help="Applicant's age in years"
)

education = st.sidebar.selectbox(
    "Highest Education Level",
    ["Associate", "Bachelor", "Master"],
    help="Associate ≈ Diploma level"
)

is_fresh_grad = st.sidebar.selectbox(
    "Fresh graduate / limited credit history?",
    ["No", "Yes"],
    help="Fresh graduates or applicants with limited credit history may have higher uncertainty"
)

home_ownership = st.sidebar.selectbox(
    "Home Ownership Status",
    ["Rent", "Own", "Mortgage"],
    help="Living with parents is typically treated as 'Rent' in credit scoring"
)

previous_default = st.sidebar.selectbox(
    "Any previous loan defaults?",
    ["No", "Yes"],
    help="A default refers to serious non-payment (e.g. 90+ days overdue)"
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
# Main Section — Application Summary
# ==================================================
st.subheader("📄 Application Summary")

st.info(
    f"""
    **Monthly Income:** RM {income:,.2f}  
    **Loan Amount Requested:** RM {loan_amount:,.2f}  
    **Fresh Graduate / Limited Credit:** {is_fresh_grad}
    """
)

# Derived financial insight
loan_to_income = loan_amount / max(income, 1)
st.write(f"📈 **Loan-to-Income Ratio:** {loan_to_income:.2f}")

st.divider()

# ==================================================
# Prediction Section
# ==================================================
st.subheader("📊 Eligibility Assessment")

if st.button("🔍 Check Eligibility"):

    # ----------------------------------------------
    # Adjust assumptions based on fresh graduate flag
    # ----------------------------------------------
    if is_fresh_grad == "Yes":
        emp_exp = 0
        cred_hist = 0
        credit_score = 600
    else:
        emp_exp = 5
        cred_hist = 5
        credit_score = 700

    # ----------------------------------------------
    # Build input dataframe (MUST match training data)
    # ----------------------------------------------
    input_df = pd.DataFrame({
        "person_age": [age],
        "person_gender": ["Male"],  # simplified for demo
        "person_education": [education],

        "person_emp_exp": [emp_exp],
        "person_income": [income],

        "loan_amnt": [loan_amount],
        "loan_intent": ["Personal"],
        "loan_int_rate": [10.0],
        "loan_percent_income": [loan_amount / max(income, 1)],

        "cb_person_cred_hist_length": [cred_hist],
        "credit_score": [credit_score],

        "person_home_ownership": [home_ownership],
        "previous_loan_defaults_on_file": [previous_default]
    })

    # ----------------------------------------------
    # Model Prediction
    # ----------------------------------------------
    prob = model.predict_proba(input_df)[0][1]

    # ----------------------------------------------
    # Display Results
    # ----------------------------------------------
    st.metric(
        label="Predicted Approval Probability",
        value=f"{prob:.2%}"
    )

    # Visual risk indicator
    st.progress(min(int(prob * 100), 100))
    st.caption("Approval likelihood indicator")

    # ----------------------------------------------
    # Risk-aware decision logic
    # ----------------------------------------------
    if is_fresh_grad == "Yes":
        st.warning(
            "⚠️ **Fresh graduate / limited credit profile detected.**\n\n"
            "Based on prior analysis, the model may be **overconfident** for "
            "under-represented applicants. Manual review is strongly recommended."
        )

        if prob >= 0.8:
            st.info("📝 **Recommendation:** Conditional approval subject to manual verification.")
        else:
            st.info("📝 **Recommendation:** Further assessment required.")

    else:
        if prob >= 0.75:
            st.success("✅ **Likely eligible for approval.**")
        elif prob >= 0.50:
            st.warning("⚠️ **Borderline case** — additional review advised.")
        else:
            st.error("❌ **Low likelihood of approval.**")

# ==================================================
# Footer / Disclaimer
# ==================================================
st.divider()
st.caption(
    "⚖️ Disclaimer: This application is a **decision-support tool only**. "
    "Predictions are based on historical patterns and do not guarantee loan approval. "
    "Final decisions should be made by qualified credit officers."
)