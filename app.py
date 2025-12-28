import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# إعدادات الصفحة
st.set_page_config(page_title="Workforce Planner Pro", layout="wide")

st.title("👷‍♂️ Workforce Planning Smart Tool")

# المدخلات
st.sidebar.header("📥 Production Inputs")
target_prod = st.sidebar.number_input("Target Production", min_value=1, value=1000)
cycle_time = st.sidebar.number_input("Cycle Time (Min)", min_value=0.1, value=5.0)
shift_hours = st.sidebar.slider("Shift Hours", 1, 12, 8)
efficiency = st.sidebar.slider("Efficiency (%)", 10, 100, 85)

# الحسابات
req_workers = (target_prod * cycle_time) / (shift_hours * 60 * (efficiency/100))
max_cap_worker = (shift_hours * 60 * (efficiency/100)) / cycle_time

# الرسم البياني
st.subheader("📊 Production Capacity Analysis")
fig = px.bar(x=["Target", "Capacity"], y=[target_prod, int(max_cap_worker * (int(req_workers)+1))],
             color=["Target", "Capacity"], color_discrete_sequence=["#1f77b4", "#ff7f0e"])
st.plotly_chart(fig, use_container_width=True)

# الأزرار والتقارير
st.subheader("📑 Export Reports")

report_df = pd.DataFrame({"Metric": ["Target", "Workers"], "Value": [target_prod, int(req_workers)+1]})

# وظيفة PDF المصححة 100%
def generate_pdf_bytes(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Workforce Report", ln=True, align='C')
    for i, row in df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Metric']}: {row['Value']}", ln=True)
    return pdf.output(dest='S').encode('latin-1') # هذه هي الطريقة الصحيحة

col_ex, col_pdf = st.columns(2)
with col_ex:
    st.download_button("📥 Excel", data=report_df.to_csv().encode('utf-8'), file_name="plan.csv")
with col_pdf:
    # استخدام BytesIO لضمان عدم حدوث خطأ StreamlitAPIException
    pdf_data = generate_pdf_bytes(report_df)
    st.download_button("📥 PDF", data=pdf_data, file_name="report.pdf", mime="application/pdf")
