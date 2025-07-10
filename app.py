import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(page_title="نظام سناد - أمانة العاصمة المقدسة", layout="centered")

st.image("sanad_logo.png", width=160)
st.markdown("<h2 style='text-align: right; color: #135846;'>نظام سناد لتصنيف أولوية البلاغات</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: right;'>منصة ذكية داخلية مقدّمة من أمانة العاصمة المقدسة لتحليل وتصنيف أولوية البلاغات بناءً على نوع الخدمة وعدد السكان وموقع البلاغ.</p>", unsafe_allow_html=True)
st.markdown("---")

uploaded_file = st.file_uploader("تحميل ملف البلاغات (بصيغة Excel)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    model = joblib.load("rf_model_only.pkl")
    df = df.rename(columns={'عدد تكرار البلاغ': 'عدد البلاغات'})

    danger_map = {
        'تغليف المباني': 1,
        'تسوير المباني': 2,
        'الحواجز الخرسانية': 3,
        'سيارات تالفة': 4,
        'مخلفات البناء': 5,
        'أعمدة إنارة': 6
    }
    df['درجة الخطورة'] = df['نوع الخدمة'].map(danger_map)

    group1 = ['حي الريان','حي الشرائع','حي النوارية','حي العوالي','حي الكعكية','حي التنعيم','حي الهجلة','حي الهجرة']
    group2 = ['شارع العزيزية','شارع الحج','منطقة الحرم','شارع أجياد']
    group3 = ['بحرة المجاهدين','شارع ثبير','حي جبل النور','حي السلام','حي الغزالي',
              'حي الشوقية','حي حداء','شارع الليث','حي الخنساء','شارع عمر بن الخطاب',
              'شارع بحرة العام','شارع النورية']

    def classify_site(location):
        if location in group1:
            return 0
        elif location in group2:
            return 2
        elif location in group3:
            return 1
        else:
            return 3

    df['صفة الموقع'] = df['موقع البلاغ'].apply(classify_site)

    features = ['درجة الخطورة', 'عدد البلاغات', 'عدد السكان', 'صفة الموقع']
    X = df[features]

    df['توقع_مستوى_الأولوية'] = model.predict(X)

    st.markdown("### نتائج التوقع:")
    st.dataframe(df[['نوع الخدمة', 'موقع البلاغ', 'عدد السكان', 'عدد البلاغات', 'توقع_مستوى_الأولوية']])

    def convert_df_to_excel(df):
        return df.to_excel(index=False, engine='openpyxl')

    st.download_button("تحميل النتائج كملف Excel", convert_df_to_excel(df), file_name="توقعات_البلاغات.xlsx")