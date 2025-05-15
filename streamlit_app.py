# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
from pyzbar.pyzbar import decode
from datetime import datetime
import numpy as np

# إعداد الصفحة
st.set_page_config(page_title="نظام التحقق من الأدوية", layout="centered")

# إضافة CSS لتحسين الواجهة
st.markdown("""
    <style>
    body {
        background-color: #F7FAFF;
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        background-color: #F7FAFF;
    }
    .title {
        color: #2C5F9E;
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle {
        color: #6B7280;
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }
    .stFileUploader label {
        color: #2C5F9E;
        font-weight: bold;
    }
    .stSuccess, .stWarning, .stError {
        background-color: #E6F0FA;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .stSuccess {
        color: #2C5F9E;
        border: 2px solid #2C5F9E;
    }
    .stWarning {
        color: #D97706;
        border: 2px solid #D97706;
    }
    .stError {
        color: #B91C1C;
        border: 2px solid #B91C1C;
    }
    .stButton>button {
        background-color: #2C5F9E;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1E4A7B;
    }
    .info-box {
        background-color: #E6F0FA;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #2C5F9E;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# العنوان والوصف
st.markdown('<div class="title">نظام ذكي للتحقق من الأدوية</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">ارفع صورة الدواء للتحقق من الاسم أو الباركود ومعرفة الصلاحية</div>', unsafe_allow_html=True)

# تحميل قاعدة بيانات الأدوية
df = pd.read_excel("pharmacy_database.xlsx")

# رفع الصورة
uploaded_file = st.file_uploader("📷 ارفع صورة الدواء", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الصورة المرفوعة", use_column_width=True)

    # محاولة قراءة الباركود
    barcode_data = None
    barcodes = decode(image)
    if barcodes:
        barcode_data = barcodes[0].data.decode("utf-8")
        st.success(f"✅ تم قراءة الباركود: {barcode_data}")
    else:
        st.warning("⚠️ لم يتم العثور على باركود في الصورة")

    # محاولة قراءة الاسم باستخدام OCR
    reader = easyocr.Reader(['en', 'ar'])
    result = reader.readtext(np.array(image))
    extracted_name = " ".join([res[1] for res in result]).strip()
    st.markdown(f'<div class="info-box">📝 الاسم المستخرج: {extracted_name}</div>', unsafe_allow_html=True)

    # البحث في قاعدة البيانات
    matched_row = None
    if barcode_data:
        matched_row = df[df["باركود"] == barcode_data]
    if matched_row is None or matched_row.empty:
        matched_row = df[df["اسم الدواء"].str.contains(extracted_name, case=False, na=False)]

    # عرض النتائج
    if matched_row is not None and not matched_row.empty:
        row = matched_row.iloc[0]
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown(f"✅ <b>اسم الدواء:</b> {row['اسم الدواء']}", unsafe_allow_html=True)
        st.markdown(f"🏭 <b>الشركة:</b> {row['الشركة المصنعة']}", unsafe_allow_html=True)
        st.markdown(f"📅 <b>تاريخ الانتهاء:</b> {row['تاريخ الانتهاء']}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # التحقق من الصلاحية
        expiry_date = pd.to_datetime(row["تاريخ الانتهاء"])
        today = datetime.today()
        if expiry_date < today:
            st.error("🚫 الدواء منتهي الصلاحية!")
        elif (expiry_date - today).days < 60:
            st.warning("⚠️ الدواء قريب من الانتهاء")
        else:
            st.success("✔️ الدواء ساري الصلاحية")
    else:
        st.error("❌ الدواء غير موجود في قاعدة البيانات")
