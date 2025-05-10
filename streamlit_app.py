# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="نظام التحقق من الأدوية", layout="centered")

st.title("نظام ذكي للتحقق من الأدوية")
st.write("ارفع صورة للدواء تحتوي على الاسم، وسيتم التحقق من صلاحية وتسجيل الدواء.")

# تحميل قاعدة بيانات الأدوية
df = pd.read_excel("pharmacy_database.xlsx")

# رفع الصورة
uploaded_file = st.file_uploader("ارفع صورة الدواء", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الصورة المرفوعة", use_column_width=True)

    # قراءة الاسم باستخدام OCR فقط
    reader = easyocr.Reader(['en', 'ar'])
    result = reader.readtext(image)
    extracted_name = " ".join([res[1] for res in result]).strip()

    # البحث في قاعدة البيانات
    matched_row = df[df["اسم الدواء"].str.contains(extracted_name, case=False, na=False)]

    # عرض النتائج
    if matched_row is not None and not matched_row.empty:
        row = matched_row.iloc[0]
        st.success("✅ الدواء موجود في قاعدة البيانات")
        st.write("**اسم الدواء:**", row["اسم الدواء"])
        st.write("**الشركة:**", row["الشركة"])
        st.write("**السعر:**", row["السعر"])
        st.write("**تاريخ الانتهاء:**", row["تاريخ الانتهاء"])

        # التحقق من الصلاحية
        expiry_date = pd.to_datetime(row["تاريخ الانتهاء"])
        today = datetime.today()
        if expiry_date < today:
            st.error("⚠️ الدواء منتهي الصلاحية!")
        elif (expiry_date - today).days < 60:
            st.warning("تنبيه: الدواء قارب على الانتهاء.")
        else:
            st.success("الدواء ساري الصلاحية.")
    else:
        st.error("❌ الدواء غير موجود في قاعدة البيانات.")
