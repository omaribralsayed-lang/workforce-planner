import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# إعدادات الصفحة
st.set_page_config(page_title="Workforce Planner Pro", layout="wide")

st.title("👷‍♂️ Workforce Planning Smart Tool")

# المدخلات في القائمة الجانبية
st.sidebar.header("📥 Production Inputs")
target_prod = st.sidebar.number_input("Target Production", min_value=1, value=1000)
cycle_time = st.sidebar.number_input("Cycle Time (Min)", min_value=0.1, value=5.0)
shift_hours = st.sidebar.slider("Shift Hours", 1, 12, 8)
efficiency = st.sidebar.slider("Efficiency (%)", 10, 100, 85)

# الحسابات الهندسية
effective_min = shift_hours * 60 * (efficiency / 100)
req_workers = (target_prod * cycle_time) / effective_min
max_cap_worker = effective_min / cycle_time

# عرض النتائج
col1, col2 = st.columns(2)
with col1:
    st.metric("Required Workers", f"{int(req_workers) + 1}")
with col2:
    st.metric("Capacity per Worker", f"{int(max_cap_worker)}")

# الرسم البياني الملون
st.subheader("📊 Production Capacity Analysis")
fig = px.bar(
    x=["Target Production", "Max Capacity"], 
    y=[target_prod, int(max_cap_worker * (int(req_workers) + 1))],
    color=["Target", "Capacity"],
    color_discrete_map={"Target": "#1f77b4", "Capacity": "#ff7f0e"}
)
st.plotly_chart(fig, use_container_width=True)

# نظام التقارير - الحل النهائي للخطأ الأحمر
st.subheader("📑 Export Official Reports")

report_df = pd.DataFrame({
    "Metric": ["Target Production", "Cycle Time", "Required Workers"],
    "Value": [target_prod, cycle_time, int(req_workers) + 1]
})

# دالة PDF بسيطة ومضمونة لتجنب AttributeError
def create_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Workforce Planning Report", ln=True, align='C')
    pdf.ln(10)
    for i, row in df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Metric']}: {row['Value']}", ln=True)
    
    # تحويل الـ PDF إلى Bytes بطريقة تتوافق مع Streamlit 1.52
    return pdf.output(dest='S').encode('latin-1')

col_ex, col_pdf = st.columns(2)
with col_ex:
    st.download_button("📥 Download Excel (CSV)", data=report_df.to_csv().encode('utf-8'), file_name="plan.csv")
with col_pdf:
    # توليد البيانات وتنزيلها مباشرة
    pdf_bytes = create_pdf_report(report_df)
    st.download_button("📥 Download PDF Report", data=pdf_bytes, file_name="Workforce_Report.pdf", mime="application/pdf")
