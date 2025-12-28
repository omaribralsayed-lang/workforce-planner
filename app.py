import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# 1. إعداد واجهة البرنامج
st.set_page_config(page_title="Workforce Planner Pro", layout="wide")
st.title("👷‍♂️ Workforce Planning Smart Tool")
st.markdown("---")

# 2. القائمة الجانبية للمدخلات
st.sidebar.header("📥 Production Inputs")
target_prod = st.sidebar.number_input("Target Production (Units)", min_value=1, value=1000)
cycle_time = st.sidebar.number_input("Standard Cycle Time (Minutes)", min_value=0.1, value=5.0)
shift_hours = st.sidebar.slider("Shift Working Hours", 1, 12, 8)
efficiency = st.sidebar.slider("Line Efficiency (%)", 10, 100, 85)

# 3. الحسابات الهندسية
available_minutes = shift_hours * 60
effective_minutes = available_minutes * (efficiency / 100)
req_workers = (target_prod * cycle_time) / effective_minutes
final_workers = int(req_workers) + 1
max_cap = (effective_minutes / cycle_time) * final_workers

# 4. عرض النتائج في بطاقات (Metrics)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Required Workers", f"{final_workers} Workers")
with col2:
    st.metric("Target Units", f"{target_prod} Units")
with col3:
    st.metric("Max Capacity", f"{int(max_cap)} Units")

st.markdown("---")

# 5. الرسم البياني الملون (الذي نجحت في تفعيله)
st.subheader("📊 Production Capacity Analysis")
chart_data = pd.DataFrame({
    "Category": ["Target Production", "Total Capacity"],
    "Units": [target_prod, int(max_cap)],
    "Status": ["Target", "Capacity"]
})
fig = px.bar(chart_data, x="Category", y="Units", color="Status",
             color_discrete_map={"Target": "#1f77b4", "Capacity": "#ff7f0e"},
             text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# 6. نظام التقارير (الحل النهائي للخطأ الأحمر)
st.subheader("📑 Export Official Reports")

report_df = pd.DataFrame({
    "Parameter": ["Target Production", "Cycle Time", "Shift Hours", "Efficiency", "Final Workers"],
    "Value": [target_prod, cycle_time, shift_hours, efficiency, final_workers]
})

# دالة الـ PDF المصححة لتتوافق مع السيرفر
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Workforce Planning Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    for i, row in df.iterrows():
        pdf.cell(200, 10, f"{row['Parameter']}: {row['Value']}", ln=1)
    
    # الحل التقني: إخراج الملف كـ bytes مباشرة
    return pdf.output(dest='S').encode('latin-1')

col_ex, col_pdf = st.columns(2)

with col_ex:
    # تصدير CSV (يعمل دائماً كبديل للأكسل)
    csv_data = report_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Excel (CSV)", data=csv_data, file_name="Plan_Report.csv", mime="text/csv")

with col_pdf:
    # تصدير PDF (حل مشكلة AttributeError)
    try:
        pdf_bytes = generate_pdf(report_df)
        st.download_button("📥 Download Official PDF", data=pdf_bytes, file_name="Workforce_Report.pdf", mime="application/pdf")
    except Exception as e:
        st.error("Preparing PDF... please wait or refresh.")
