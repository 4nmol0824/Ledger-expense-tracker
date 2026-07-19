import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime
from google import genai
from google.genai import types

# ----------------------------- CONFIG -----------------------------

st.set_page_config(page_title="LEDGER — AI Expense Tracker", page_icon="🧾", layout="wide")

DATA_FILE = "expenses.csv"

CATEGORY_COLORS = {
    "Food & Dining": "#A6402F",
    "Groceries": "#2F6F4E",
    "Transport": "#3F5B66",
    "Shopping": "#6B4A6B",
    "Bills & Utilities": "#C08A2E",
    "Entertainment": "#8C7A4E",
    "Health": "#2F6F4E",
    "Travel": "#3F5B66",
    "Other": "#5B5F51",
}
CATEGORIES = list(CATEGORY_COLORS.keys())

# ----------------------------- STYLE -----------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

.stApp { background-color: #F0EEE4; }
h1, h2, h3 { font-family: 'Roboto Slab', serif !important; }
.stCaption, .stMarkdown p, div[data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
}
.tag {
    display:inline-block; padding:3px 10px; border-radius:10px;
    font-family:'IBM Plex Mono', monospace; font-size:12px; white-space:nowrap;
}
div[data-testid="stMetricValue"] { font-family: 'Roboto Slab', serif !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- DATA -----------------------------

def load_expenses():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype={"id": str})
        return df
    return pd.DataFrame(columns=["id", "date", "merchant", "category", "amount"])

def save_expenses(df):
    df.to_csv(DATA_FILE, index=False)

if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

# ----------------------------- GEMINI CLIENT (free tier) -----------------------------

def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
    if not api_key:
        st.error("No GEMINI_API_KEY found. Add it in Streamlit Cloud → App settings → Secrets.")
        st.stop()
    return genai.Client(api_key=api_key)

EXTRACTION_PROMPT = f"""Extract the following fields from this receipt image and respond with ONLY a raw JSON object, no markdown fences, no other text:
{{"merchant": string, "date": "YYYY-MM-DD" or null if not visible, "amount": number (total paid, no currency symbol), "category": one of {json.dumps(CATEGORIES)}, "confidence": "high"|"medium"|"low"}}
If a field cannot be determined, use your best reasonable guess. Amount must be a plain number."""

def extract_receipt(image_bytes, media_type):
    client = get_client()
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=media_type),
            EXTRACTION_PROMPT,
        ],
    )
    text = resp.text or ""
    clean = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(clean)
    if not isinstance(data.get("amount"), (int, float)):
        try:
            data["amount"] = float(data.get("amount", 0))
        except (TypeError, ValueError):
            data["amount"] = 0.0
    if not data.get("date"):
        data["date"] = date.today().isoformat()
    if data.get("category") not in CATEGORY_COLORS:
        data["category"] = "Other"
    return data

# ----------------------------- HEADER -----------------------------

st.markdown("### LEDGER.")
st.caption("point your camera at paper. get numbers on a page.")
st.divider()

# ----------------------------- UPLOAD -----------------------------

uploaded = st.file_uploader(
    "Drop a receipt, or click to upload — JPG or PNG. The AI reads the merchant, date, total, and category.",
    type=["jpg", "jpeg", "png"],
)

if uploaded is not None and st.session_state.get("last_uploaded") != uploaded.file_id:
    with st.spinner("reading receipt…"):
        try:
            extracted = extract_receipt(uploaded.getvalue(), uploaded.type)
            st.session_state.pending = extracted
            st.session_state.last_uploaded = uploaded.file_id
        except json.JSONDecodeError:
            st.error("The AI couldn't find receipt data in that image. Make sure it's a photo of an actual receipt, not a screenshot or unrelated image, then try again.")
            st.session_state.pending = None
        except Exception as e:
            st.error("Could not read that receipt. See details below.")
            with st.expander("Error details"):
                st.exception(e)
            st.session_state.pending = None

if st.session_state.get("pending"):
    data = st.session_state.pending
    if data.get("confidence") == "low":
        st.warning("⚠️ Low confidence read — please double check these fields before saving")
    else:
        st.success("✓ Scanned — check the details before saving")

    with st.form("confirm_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        merchant = c1.text_input("Merchant", data.get("merchant", ""))
        try:
            parsed_date = pd.to_datetime(data.get("date")).date()
        except Exception:
            parsed_date = date.today()
        d = c2.date_input("Date", parsed_date)
        c3, c4 = st.columns(2)
        amount = c3.number_input("Amount", value=float(data.get("amount", 0)), step=0.01, min_value=0.0)
        cat_index = CATEGORIES.index(data.get("category")) if data.get("category") in CATEGORIES else len(CATEGORIES) - 1
        category = c4.selectbox("Category", CATEGORIES, index=cat_index)

        save_col, cancel_col = st.columns(2)
        submitted = save_col.form_submit_button("Save expense", type="primary", use_container_width=True)
        cancelled = cancel_col.form_submit_button("Cancel", use_container_width=True)

        if submitted:
            new_row = {
                "id": f"exp_{int(datetime.now().timestamp() * 1000)}",
                "date": str(d),
                "merchant": merchant.strip() or "Unknown",
                "category": category,
                "amount": round(float(amount), 2),
            }
            st.session_state.expenses = pd.concat(
                [pd.DataFrame([new_row]), st.session_state.expenses], ignore_index=True
            )
            save_expenses(st.session_state.expenses)
            st.session_state.pending = None
            st.rerun()
        if cancelled:
            st.session_state.pending = None
            st.rerun()

st.divider()

# ----------------------------- DASHBOARD -----------------------------

left, right = st.columns([2, 1])

with left:
    st.subheader("Ledger")
    df = st.session_state.expenses
    if df.empty:
        st.info("No expenses yet — upload a receipt to get started")
    else:
        df = df.sort_values("date", ascending=False).reset_index(drop=True)
        header = st.columns([1.2, 2, 1.6, 1, 0.5])
        for h, label in zip(header, ["Date", "Merchant", "Category", "Amount", ""]):
            h.markdown(f"**{label}**")
        for _, row in df.iterrows():
            c1, c2, c3, c4, c5 = st.columns([1.2, 2, 1.6, 1, 0.5])
            c1.write(row["date"])
            c2.write(row["merchant"])
            color = CATEGORY_COLORS.get(row["category"], "#5B5F51")
            c3.markdown(
                f"<span class='tag' style='background:{color}22;color:{color}'>{row['category']}</span>",
                unsafe_allow_html=True,
            )
            c4.write(f"${row['amount']:.2f}")
            if c5.button("✕", key=f"del_{row['id']}"):
                st.session_state.expenses = st.session_state.expenses[st.session_state.expenses["id"] != row["id"]]
                save_expenses(st.session_state.expenses)
                st.rerun()

with right:
    st.subheader("This Month")
    total = df["amount"].sum() if not df.empty else 0.0
    st.metric(label=f"{len(df)} expense(s) logged", value=f"${total:,.2f}")
    if not df.empty:
        by_cat = df.groupby("category")["amount"].sum().sort_values(ascending=False)
        st.bar_chart(by_cat, color="#2F6F4E")
    else:
        st.caption("No data yet")

st.divider()
st.caption("Built with Streamlit + the Gemini API. Receipts are sent to Google's API for extraction only.")