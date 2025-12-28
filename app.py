import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# 1. إعداد واجهة البرنامج
st.set_page_config(page_title="Workforce Planner Pro", layout="wide")
st.title("👷‍♂️ Workforce Planning Smart Tool")

# 2. المدخلات
st.sidebar.header("📥 Production Inputs")
target_prod = st.sidebar.number_input("Target Production (Units)", min_value=1, value=1000)
cycle_time = st.sidebar.number_input("Standard Cycle Time (Min)", min_value=0.1, value=5.0)
shift_hours = st.sidebar.slider("Shift Working Hours", 1, 12, 8)
efficiency = st.sidebar.slider("Line Efficiency (%)", 10, 100, 85)

# 3. الحسابات
eff_min = shift_hours * 60 * (efficiency / 100)
req_workers = (target_prod * cycle_time) / eff_min
final_workers = int(req_workers) + 1
max_cap = (eff_min / cycle_time) * final_workers

# 4. النتائج والرسم البياني
col1, col2 = st.columns(2)
col1.metric("Required Workers", final_workers)
col2.metric("Max Capacity", int(max_cap))

fig = px.bar(x=["Target", "Capacity"], y=[target_prod, int(max_cap)],
             color=["Target", "Capacity"], color_discrete_sequence=["#1f77b4", "#ff7f0e"], text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# 5. نظام التقارير المنظم (Excel & PDF)
st.subheader("📑 Export Professional Reports")

report_df = pd.DataFrame({
    "Description": ["Target Production", "Cycle Time", "Shift Hours", "Efficiency", "Required Workers", "Max Capacity"],
    "Value": [target_prod, cycle_time, shift_hours, f"{efficiency}%", final_workers, int(max_cap)]
})

# --- دالة إنشاء ملف Excel حقيقي بأعمدة منفصلة ---
def to_excel(df):
    output = BytesIO()
    # استخدام xlsxwriter لضمان الترتيب في أعمدة
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='WorkforcePlan')
    return output.getvalue()

# --- دالة إنشاء PDF ---
def to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Workforce Planning Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    for i, row in df.iterrows():
        pdf.cell(90, 10, txt=str(row['Description']), border=1)
        pdf.cell(60, 10, txt=str(row['Value']), border=1, ln=True)
    
    pdf_out = pdf.output(dest='S')
    return pdf_out.encode('latin-1') if isinstance(pdf_out, str) else bytes(pdf_out)

col_ex, col_pdf = st.columns(2)
with col_ex:
    # تحميل ملف Excel حقيقي وليس CSV لضمان التنسيق
    st.download_button(
        label="📥 Download Excel Report",
        data=to_excel(report_df),
        file_name="Workforce_Plan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col_pdf:
    st.download_button(
        label="📥 Download PDF Report",
        data=to_pdf(report_df),
        file_name="Workforce_Report.pdf",
        mime="application/pdf"
    )
