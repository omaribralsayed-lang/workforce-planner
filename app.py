import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# إعدادات الصفحة
st.set_page_config(page_title="Workforce Planner Pro", layout="wide")

st.title("👷‍♂️ Workforce Planning Smart Tool")
st.markdown("---")

# القائمة الجانبية للمدخلات
st.sidebar.header("📥 Production Inputs")
target_prod = st.sidebar.number_input("Target Production (Units)", min_value=1, value=1000)
cycle_time = st.sidebar.number_input("Standard Cycle Time (Minutes)", min_value=0.1, value=5.0)
shift_hours = st.sidebar.slider("Shift Working Hours", 1, 12, 8)
efficiency = st.sidebar.slider("Line Efficiency (%)", 10, 100, 85)

# الحسابات الهندسية
available_minutes = shift_hours * 60
effective_minutes = available_minutes * (efficiency / 100)
required_workers = (target_prod * cycle_time) / effective_minutes

# عرض النتائج الأساسية
col1, col2 = st.columns(2)
with col1:
    st.metric("Required Workers", f"{int(required_workers) + 1} Workers")
with col2:
    max_cap = effective_minutes / cycle_time
    st.metric("Max Capacity/Worker", f"{int(max_cap)} Units")

st.markdown("---")

# الرسم البياني الملون
st.subheader("📊 Production Capacity Analysis")
chart_data = pd.DataFrame({
    "Category": ["Target Production", "Max Capacity (Current Workers)"],
    "Units": [target_prod, int(max_cap * (int(required_workers) + 1))],
    "Status": ["Target", "Capacity"]
})
fig = px.bar(chart_data, x="Category", y="Units", color="Status",
             color_discrete_map={"Target": "#1f77b4", "Capacity": "#ff7f0e"},
             text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# نظام التقارير
st.subheader("📑 Export Official Reports")

# تصدير Excel
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Plan')
    writer.close()
    return output.getvalue()

report_df = pd.DataFrame({
    "Parameter": ["Target Production", "Cycle Time", "Shift Hours", "Efficiency", "Required Workers"],
    "Value": [target_prod, cycle_time, shift_hours, efficiency, int(required_workers) + 1]
})

# تصدير PDF (نسخة مصححة)
def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Workforce Planning Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    for i, row in df.iterrows():
        pdf.cell(200, 10, f"{row['Parameter']}: {row['Value']}", ln=1)
    # تعديل طريقة الإخراج لحل الخطأ الأحمر
    return pdf.output(dest='S')

col_ex, col_pdf = st.columns(2)
with col_ex:
    st.download_button("📥 Download Excel Report", data=to_excel(report_df), file_name="Workforce_Plan.xlsx")
with col_pdf:
    st.download_button("📥 Download PDF Report", data=create_pdf(report_df), file_name="Workforce_Report.pdf")
