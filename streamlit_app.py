# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
from pyzbar.pyzbar import decode
from datetime import datetime
import numpy as np

st.set_page_config(page_title="نظام التحقق من الأدوية", layout="centered")

st.title("نظام ذكي للتحقق من الأدوية")
st.write("ارفع صورة للدواء تحتوي على الباركود أو الاسم، وسيتم التحقق من صلاحية وتسجيل الدواء.")

# تحميل قاعدة بيانات الأدوية
df = pd.read_excel("pharmacy_database.xlsx")

# رفع الصورة
uploaded_file = st.file_uploader("ارفع صورة الدواء", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الصورة المرفوعة", use_column_width=True)

    # محاولة قراءة الباركود
    barcode_data = None
    barcodes = decode(image)
    if barcodes:
        barcode_data = barcodes[0].data.decode("utf-8")
        st.success(f"تم قراءة الباركود: {barcode_data}")
    else:
        st.warning("لم يتم العثور على باركود في الصورة.")

    # محاولة قراءة الاسم باستخدام OCR
    reader = easyocr.Reader(['en', 'ar'])
    result = reader.readtext(np.array(image))
    extracted_name = " ".join([res[1] for res in result]).strip()
    st.info(f"الاسم المستخرج باستخدام OCR: {extracted_name}")

    # البحث في قاعدة البيانات
    matched_row = None
    if barcode_data:
        matched_row = df[df["باركود"] == barcode_data]
    if matched_row is None or matched_row.empty:
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
