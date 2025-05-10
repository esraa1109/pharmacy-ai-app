# Load database with caching and validation
@st.cache_data
def load_database(file_path):
    try:
        data = pd.read_excel(file_path)
        required_columns = {"باركود", "اسم الدواء", "الشركة", "السعر", "تاريخ الانتهاء"}
        if not required_columns.issubset(data.columns):
            raise ValueError("Missing required columns")
        return data
    except Exception as e:
        st.error(f"❌ خطأ أثناء تحميل قاعدة البيانات: {e}")
        return pd.DataFrame()

df = load_database("pharmacy_database.xlsx")
if df.empty:
    st.stop()

# Initialize OCR reader once and cache it
@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['en', 'ar'])

reader = get_ocr_reader()

# Image processing
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image = ImageOps.exif_transpose(image)  # Handle orientation
    image.thumbnail((1024, 1024))  # Resize if needed
    st.image(image, caption="الصورة المرفوعة", use_column_width=True)

    # Decode barcode and OCR text
    barcode_data = None
    barcodes = decode(image)
    if barcodes:
        barcode_data = barcodes[0].data.decode("utf-8")
        st.success(f"تم قراءة الباركود: {barcode_data}")
    else:
        st.warning("لم يتم العثور على باركود في الصورة.")

    result = reader.readtext(np.array(image))
    extracted_name = " ".join([res[1] for res in result]).strip()
    st.info(f"الاسم المستخرج باستخدام OCR: {extracted_name}")

    # Match and validate
    if barcode_data or extracted_name:
        matched_row = df[
            (df["باركود"] == barcode_data) | 
            (df["اسم الدواء"].str.contains(extracted_name, case=False, na=False))
        ]
    else:
        matched_row = pd.DataFrame()

    if not matched_row.empty:
        row = matched_row.iloc[0]
        st.success("✅ الدواء موجود في قاعدة البيانات")
        st.write("**اسم الدواء:**", row["اسم الدواء"])
        st.write("**الشركة:**", row["الشركة"])
        st.write("**السعر:**", row["السعر"])
        try:
            expiry_date = pd.to_datetime(row["تاريخ الانتهاء"], errors='coerce')
            if pd.isnull(expiry_date):
                st.error("⚠️ تاريخ الانتهاء غير صالح.")
            elif expiry_date < datetime.today():
                st.error("⚠️ الدواء منتهي الصلاحية!")
            elif (expiry_date - datetime.today()).days < 60:
                st.warning("تنبيه: الدواء قارب على الانتهاء.")
            else:
                st.success("الدواء ساري الصلاحية.")
        except Exception:
            st.error("⚠️ حدث خطأ أثناء التحقق من تاريخ الانتهاء.")
    else:
        st.error("❌ الدواء غير موجود في قاعدة البيانات.")
