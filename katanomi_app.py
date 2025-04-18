import streamlit as st
import pandas as pd
import math
from io import BytesIO

st.set_page_config(page_title="Κατανομή Μαθητών", layout="wide")
st.title("📚 Εργαλείο Κατανομής Μαθητών")

uploaded_file = st.file_uploader("📂 Ανέβασε αρχείο Excel (.xlsx) με μαθητές", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("Το αρχείο φορτώθηκε με επιτυχία!")

    required_columns = [
        "Ονοματεπώνυμο", "Φύλο", "Παιδί Εκπαιδευτικού", "Ζωηρός",
        "ΙΔΙΑΙΤΕΡΟΤΗΤΑ(ΔΕΠΥ ,ΣΥΝΟΔΟ)", "Καλή γνώση Ελληνικών", "Φίλος/Φίλη", "Συγκρούσεις"
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"❌ Το αρχείο δεν περιέχει τις απαραίτητες στήλες: {', '.join(missing_columns)}")
        st.stop()

    st.write("📌 Στήλες που βρέθηκαν στο αρχείο:", list(df.columns))

    def parse_boolean(value):
        return str(value).strip().lower() in ["ναι", "x", "yes", "true"]

    def parse_list(value):
        if pd.isna(value):
            return []
        return [name.strip() for name in str(value).split(";") if name.strip()]

    students_raw = []
    for _, row in df.iterrows():
        students_raw.append({
            "name": row["Ονοματεπώνυμο"].strip(),
            "gender": row["Φύλο"].strip().upper(),
            "is_teacher_child": parse_boolean(row["Παιδί Εκπαιδευτικού"]),
            "is_lively": parse_boolean(row["Ζωηρός"]),
            "has_special_needs": parse_boolean(row["ΙΔΙΑΙΤΕΡΟΤΗΤΑ(ΔΕΠΥ ,ΣΥΝΟΔΟ)"]),
            "language_level": "Καλή" if parse_boolean(row["Καλή γνώση Ελληνικών"]) else "Χαμηλή",
            "friends": parse_list(row["Φίλος/Φίλη"]),
            "conflicts": parse_list(row["Συγκρούσεις"])
        })

    # Φιλτράρουμε ώστε να κρατήσουμε μόνο αμοιβαίες φιλίες
    name_to_friends = {s["name"]: set(s["friends"]) for s in students_raw}
    for student in students_raw:
        student["friends"] = [f for f in student["friends"] if student["name"] in name_to_friends.get(f, set())]

        # Ειδοποιήσεις για μη αμοιβαίες φιλίες
    unreciprocated = []
    for s in students_raw:
        original = set(name_to_friends.get(s["name"], []))
        confirmed = set(s["friends"])
        diff = original - confirmed
        for d in diff:
            unreciprocated.append((s["name"], d))

    students = students_raw
