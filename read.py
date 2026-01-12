import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. SETUP & CONFIG
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
CSV_FILE = "bankstatementconverter.com.csv"

st.set_page_config(page_title="Smart.Expense.Tracker", layout="wide")

# 2. CORE FUNCTIONS
def predict_category(description):
    """Predicts category using keywords first, then AI fallback."""
    if not description: return "Others"
    
    # Keyword Scout (Free)
    keywords = {
        'Food': ['restaurant', 'cafe', 'uber eats', 'mcdonalds', 'pizza', 'grocery', 'kfc', 'food'],
        'Transportation': ['uber', 'bolt', 'train', 'fuel', 'shell', 'parking', 'taxi'],
        'Entertainment': ['netflix', 'cinema', 'spotify', 'pub', 'bar', 'gaming', 'steam'],
        'Utilities': ['recharge', 'airtime', 'mascom', 'orange', 'water', 'electricity'],
        'Bank Fees': ['fee', 'charge', 'commission', 'tax']
    }
    
    desc_lower = description.lower()
    for cat, terms in keywords.items():
        if any(term in desc_lower for term in terms):
            return cat

    # AI Fallback (Paid)
    try:
        prompt = f"Categorize this expense: '{description}' into: Food, Transportation, Entertainment, Utilities, Shopping, Bank Fees, Others. Just return the category name."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Others"

def load_and_clean_data():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])
    # Load and strip spaces from headers
    df = pd.read_csv(CSV_FILE)
    df.columns = df.columns.str.strip()
    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]

    # UNIFY THE DATA: Convert Debit/Credit to a single 'Amount' if they exist
    if 'Amount' not in df.columns:
        if 'Credit' in df.columns and 'Debit' in df.columns:
            # Credit is money in, Debit is money out. We want the absolute value for 'Amount'
            df['Amount'] = df['Credit'].fillna(df['Debit'])
        else:
            # If neither exists, create an empty Amount column
            df['Amount'] = 0

    # Clean the 'Description' column
    if 'Description' not in df.columns and 'Note' in df.columns:
        df['Description'] = df['Note']

    # SANITIZE: Remove rows without a Date or Amount (like "Opening Balance" rows)
    df = df.dropna(subset=['Date'])
    
    # FORCE NUMERIC: Ensure Amount is a float, not text
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    
    # Standardize Categories (No "Utilities " vs "Utilities")
    if 'Category' in df.columns:
        df['Category'] = df['Category'].fillna('Others').astype(str).str.strip()

    # Return only the columns the App actually cares about
    return df[["Date", "Description", "Amount", "Category"]]

# 3. STREAMLIT UI
st.title("S.E.T")

data = load_and_clean_data()

# Sidebar: Quick Stats
with st.sidebar:
    st.header("Overview")
    total_spent = data[data['Amount'] > 0]['Amount'].sum()
    st.metric("Total Recorded", f"${total_spent:,.2f}")

# Main Layout: Form
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Add New Entry")
    # Step 1: Trigger Prediction
    desc_input = st.text_input("Transaction Description (e.g., 'Netflix Subscription')")
    
    # We only predict if user typed something
    suggested = predict_category(desc_input) if desc_input else ""
    
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("Date")
        # Step 2: Form captures everything
        final_desc = st.text_input("Confirmed Description", value=desc_input)
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        category = st.text_input("Category", value=suggested)
        
        submitted = st.form_submit_button("Log Transaction")
        
        if submitted:
            if final_desc and amount > 0:
                new_row = pd.DataFrame([{"Date": date, "Description": final_desc, "Amount": amount, "Category": category}])
                data = pd.concat([data, new_row], ignore_index=True)
                data.to_csv(CSV_FILE, index=False)
                st.success(f"Logged: {final_desc}")
                st.rerun()
            else:
                st.warning("Please provide a description and amount.")

# 4. VISUALIZATION
with col2:
    st.subheader("Spending Analysis")
    # Filter for valid expenses only
    plot_data = data[data['Amount'] > 0].copy()
    
    if not plot_data.empty:
        category_totals = plot_data.groupby("Category")["Amount"].sum()
        
        tab1, tab2 = st.tabs(["Bar Chart", "Pie Chart"])
        
        with tab1:
            fig, ax = plt.subplots()
            category_totals.sort_values().plot(kind="barh", ax=ax, color="#1E88E5")
            ax.set_xlabel("Amount")
            st.pyplot(fig)
            
        with tab2:
            fig2, ax2 = plt.subplots()
            category_totals.plot(kind="pie", autopct="%1.1f%%", ax=ax2, startangle=140)
            ax2.set_ylabel("") # Remove default label
            st.pyplot(fig2)
    else:
        st.info("No data yet. Log an expense to see the breakdown.")

st.divider()
st.subheader("Recent Transactions")
st.dataframe(data.tail(10), use_container_width=True)
