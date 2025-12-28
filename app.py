import streamlit as st
import math
import pandas as pd
from io import BytesIO
from fpdf import FPDF

# إعداد واجهة الأداة
st.set_page_config(page_title="Workforce Planner Pro", page_icon="👷‍♂️")
st.title("👷‍♂️ Workforce Planning Smart Tool")

# --- 1. القائمة الجانبية للمدخلات ---
st.sidebar.header("📋 Production Inputs")
target = st.sidebar.number_input("Target Production (Units)", value=1000)
hours = st.sidebar.slider("Shift Hours", 1, 12, 8)
efficiency = st.sidebar.slider("Expected Efficiency (%)", 50, 100, 85)
cycle_time = st.sidebar.number_input("Standard Cycle Time (Min)", value=5.0)

# --- 2. الحسابات الهندسية ---
available_time = hours * 60 * (efficiency / 100)
needed_workers = math.ceil((target * cycle_time) / available_time)

# --- 3. عرض النتائج الرئيسية ---
col1, col2 = st.columns(2)
col1.metric("Required Workers", f"{needed_workers} Workers")
col2.metric("Max Capacity", f"{target} Units")

# --- 4. الرسم البياني ---
st.write("### 📊 Capacity Utilization Analysis")
chart_data = pd.DataFrame({
    "Status": ["Utilized Efficiency", "Operational Loss"],
    "Percentage": [efficiency, 100 - efficiency]
})
st.bar_chart(chart_data.set_index("Status"))

# --- 5. تجهيز البيانات للتقارير (English Version) ---
# قمنا بتغيير الأسماء هنا لتكون بالإنجليزية وتتطابق مع الـ PDF
df_full_report = pd.DataFrame({
    "Indicator": ["Target Production", "Shift Hours", "Cycle Time (Min)", "Efficiency", "Required Workers"],
    "Value": [target, hours, cycle_time, f"{efficiency}%", needed_workers]
})

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Workforce_Report')
    return output.getvalue()

# --- 6. وظيفة الـ PDF الشامل (English) ---
def create_full_pdf(target, hours, cycle, eff, workers):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Detailed Workforce Planning Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    # إضافة جميع العوامل بالإنجليزية
    pdf.cell(200, 10, txt=f"- Target Production: {target} Units", ln=True)
    pdf.cell(200, 10, txt=f"- Shift Hours: {hours} Hours", ln=True)
    pdf.cell(200, 10, txt=f"- Standard Cycle Time: {cycle} Minutes", ln=True)
    pdf.cell(200, 10, txt=f"- Expected Efficiency: {eff}%", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Final Result: {workers} Workers Required", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 7. أزرار التحميل ---
st.write("---")
st.write("### 📥 Export Final Reports")
c1, c2 = st.columns(2)

with c1:
    st.download_button(
        label="Download Excel Report 📊",
        data=to_excel(df_full_report),
        file_name='Workforce_Detailed_Plan.xlsx'
    )

with c2:
    pdf_data = create_full_pdf(target, hours, cycle_time, efficiency, needed_workers)
    st.download_button(
        label="Download PDF Report 📄",
        data=pdf_data,
        file_name='Workforce_Detailed_Report.pdf'
    )
