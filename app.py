import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# 1. إعداد واجهة البرنامج
st.set_page_config(page_title="Workforce Planner Pro", layout="wide")
st.title("👷‍♂️ Workforce Planning Smart Tool")

# 2. القائمة الجانبية للمدخلات
st.sidebar.header("📥 Production Inputs")
target_prod = st.sidebar.number_input("Target Production (Units)", min_value=1, value=1000)
cycle_time = st.sidebar.number_input("Standard Cycle Time (Min)", min_value=0.1, value=5.0)
shift_hours = st.sidebar.slider("Shift Working Hours", 1, 12, 8)
efficiency = st.sidebar.slider("Line Efficiency (%)", 10, 100, 85)

# 3. الحسابات الهندسية الدقيقة
available_min = shift_hours * 60
effective_min = available_min * (efficiency / 100)
req_workers = (target_prod * cycle_time) / effective_min
final_workers = int(req_workers) + 1
max_cap_total = (effective_min / cycle_time) * final_workers

# 4. عرض النتائج الأساسية
col1, col2, col3 = st.columns(3)
col1.metric("Required Workers", f"{final_workers} Workers")
col2.metric("Target Units", f"{target_prod} Units")
col3.metric("Max System Capacity", f"{int(max_cap_total)} Units")

# 5. الرسم البياني (الألوان)
st.subheader("📊 Production Capacity Analysis")
fig = px.bar(x=["Target Production", "System Capacity"], y=[target_prod, int(max_cap_total)],
             color=["Target", "Capacity"], color_discrete_sequence=["#1f77b4", "#ff7f0e"],
             text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# 6. تجميع "كافة" البيانات للتقرير (Excel & PDF)
st.subheader("📑 Export Comprehensive Reports")

# إنشاء جدول بيانات كامل للتقرير
full_report_data = {
    "Description": [
        "Target Production (Units)", 
        "Standard Cycle Time (Min)", 
        "Shift Duration (Hours)", 
        "Line Efficiency (%)", 
        "Effective Working Minutes",
        "Calculated Required Workers",
        "Final Assigned Workers",
        "Max Possible Capacity (with Assigned Workers)"
    ],
    "Value": [
        target_prod, 
        cycle_time, 
        shift_hours, 
        f"{efficiency}%", 
        effective_min,
        round(req_workers, 2),
        final_workers,
        int(max_cap_total)
    ]
}
report_df = pd.DataFrame(full_report_data)

# دالة PDF المحدثة لتشمل كل الأسطر
def generate_full_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Workforce Planning Full Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    # رسم جدول بسيط في PDF
    for i, row in df.iterrows():
        pdf.cell(100, 10, txt=str(row['Description']), border=1)
        pdf.cell(80, 10, txt=str(row['Value']), border=1, ln=True)
    
    pdf_out = pdf.output(dest='S')
    return pdf_out.encode('latin-1') if isinstance(pdf_out, str) else bytes(pdf_out)

col_ex, col_pdf = st.columns(2)
with col_ex:
    # تصدير Excel (CSV) بكامل البيانات
    csv = report_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Full Excel", data=csv, file_name="Full_Workforce_Plan.csv", mime="text/csv")

with col_pdf:
    # تصدير PDF بكامل البيانات
    pdf_bytes = generate_full_pdf(report_df)
    st.download_button("📥 Download Full PDF", data=pdf_bytes, file_name="Full_Workforce_Report.pdf", mime="application/pdf")
