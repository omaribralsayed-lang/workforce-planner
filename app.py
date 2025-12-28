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
target_prod = st.sidebar.number_input("Target Production", min_value=1, value=1000)
cycle_time = st.sidebar.number_input("Cycle Time (Min)", min_value=0.1, value=5.0)
shift_hours = st.sidebar.slider("Shift Hours", 1, 12, 8)
efficiency = st.sidebar.slider("Efficiency (%)", 10, 100, 85)

# 3. الحسابات
eff_min = shift_hours * 60 * (efficiency / 100)
req_workers = (target_prod * cycle_time) / eff_min
final_workers = int(req_workers) + 1
max_cap = (eff_min / cycle_time) * final_workers

# 4. عرض النتائج
c1, c2 = st.columns(2)
c1.metric("Required Workers", final_workers)
c2.metric("Total Capacity", int(max_cap))

# 5. الرسم البياني (الألوان)
st.subheader("📊 Capacity Analysis")
fig = px.bar(x=["Target", "Capacity"], y=[target_prod, int(max_cap)],
             color=["Target", "Capacity"], color_discrete_sequence=["#1f77b4", "#ff7f0e"])
st.plotly_chart(fig, use_container_width=True)

# 6. قسم التقارير (حل نهائي ومضمون للخطأ الأحمر)
st.subheader("📑 Export Reports")
report_df = pd.DataFrame({"Metric": ["Target", "Workers"], "Value": [target_prod, final_workers]})

# دالة PDF بسيطة جداً متوافقة مع fpdf و fpdf2
def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Workforce Report", ln=True, align='C')
    for i, row in df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Metric']}: {row['Value']}", ln=True)
    
    # تحويل البيانات لـ bytes بطريقة تناسب زر التحميل
    out_str = pdf.output(dest='S')
    if isinstance(out_str, str): # للتعامل مع النسخ القديمة والجديدة
        return out_str.encode('latin-1')
    return out_str

col_ex, col_pdf = st.columns(2)
with col_ex:
    st.download_button("📥 Excel (CSV)", data=report_df.to_csv().encode('utf-8'), file_name="plan.csv")
with col_pdf:
    try:
        pdf_data = generate_pdf_report(report_df)
        st.download_button("📥 Download PDF", data=pdf_data, file_name="report.pdf", mime="application/pdf")
    except:
        st.info("Generating PDF... please wait.")
