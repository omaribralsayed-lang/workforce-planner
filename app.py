import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# 1. إعدادات الواجهة (لضمان ظهور الألوان والأعمدة بشكل صحيح)
st.set_page_config(page_title="Workforce Planner Pro", layout="wide")
st.title("👷‍♂️ Workforce Planning Smart Tool")

# 2. المدخلات الجانبية
st.sidebar.header("📥 Production Inputs")
target_prod = st.sidebar.number_input("Target Production", min_value=1, value=1000)
cycle_time = st.sidebar.number_input("Cycle Time (Min)", min_value=0.1, value=5.0)
shift_hours = st.sidebar.slider("Shift Hours", 1, 12, 8)
efficiency = st.sidebar.slider("Efficiency (%)", 10, 100, 85)

# 3. الحسابات الهندسية الدقيقة
effective_min = shift_hours * 60 * (efficiency / 100)
req_workers = (target_prod * cycle_time) / effective_min
final_workers = int(req_workers) + 1
max_cap = (effective_min / cycle_time) * final_workers

# 4. عرض النتائج (Metrics)
col1, col2 = st.columns(2)
col1.metric("Required Workers", f"{final_workers}")
col2.metric("Total Capacity", f"{int(max_cap)}")

# 5. الرسم البياني بالألوان الثابتة (حل مشكلة الألوان)
st.subheader("📊 Capacity Analysis")
# إنشاء جدول بيانات للرسم البياني لضمان ثبات اللون
chart_df = pd.DataFrame({
    "Metric": ["Target Production", "Maximum Capacity"],
    "Value": [target_prod, int(max_cap)],
    "Type": ["Target", "Capacity"]
})
fig = px.bar(chart_df, x="Metric", y="Value", color="Type",
             color_discrete_map={"Target": "#1f77b4", "Capacity": "#ff7f0e"}, 
             text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# 6. نظام التقارير المحترف (حل مشكلة الإكسيل والـ PDF نهائياً)
st.subheader("📑 Export Official Reports")

report_df = pd.DataFrame({
    "Description": ["Target Production", "Cycle Time (Min)", "Shift Hours", "Efficiency (%)", "Required Workers", "Max Capacity"],
    "Value": [target_prod, cycle_time, shift_hours, f"{efficiency}%", final_workers, int(max_cap)]
})

# --- وظيفة الإكسيل المنسق (حل مشكلة الأعمدة المتداخلة في الصورة 19) ---
def get_excel_data(df):
    output = BytesIO()
    # المحرك xlsxwriter يضمن فصل الأعمدة تماماً
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plan')
    return output.getvalue()

# --- وظيفة الـ PDF المستقرة (حل الخطأ الأحمر في الصورة 17) ---
def get_pdf_data(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Workforce Planning Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    # رسم جدول منظم بالـ PDF
    for i, row in df.iterrows():
        pdf.cell(100, 10, txt=str(row['Description']), border=1)
        pdf.cell(80, 10, txt=str(row['Value']), border=1, ln=True)
    
    # تحويل المخرجات بطريقة تناسب السيرفر وتمنع الانهيار
    out = pdf.output(dest='S')
    return out.encode('latin-1') if isinstance(out, str) else bytes(out)

btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    # تحميل الإكسيل الحقيقي (XLSX)
    st.download_button(
        label="📥 Download Excel (Fixed Columns)",
        data=get_excel_data(report_df),
        file_name="Workforce_Plan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with btn_col2:
    # تحميل الـ PDF بدون أخطاء حمراء
    st.download_button(
        label="📥 Download PDF (Fixed Error)",
        data=get_pdf_data(report_df),
        file_name="Workforce_Report.pdf",
        mime="application/pdf"
    )
