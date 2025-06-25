import streamlit as st
import csv
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Amount", "Category", "Sub-Category", "Date", "Type"])
# Ensure CSV file exists
def initialize_csv():
    if 'expenses' not in not st.session_state:
        st.session_state.expenses = pd.DataFrame(columns=["Amount", "Category", "Sub-Category", "Date", "Type"])
        writer = csv.writer(file)
        writer.writerow(["Amount", "Category", "Sub-Category", "Date", "Type"])

def save_expense(amount, category, sub_category, date, type_):
    with open("expenses.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([amount, category, sub_category, date, type_])

def load_expenses():
    if not os.path.exists("expenses.csv"):
        return pd.DataFrame(columns=["Amount", "Category", "Sub-Category", "Date", "Type"])
    return pd.read_csv("expenses.csv")

initialize_csv()

# Streamlit App UI
st.title("💸 Expense & Income Tracker")

menu = st.sidebar.selectbox("Navigation", ["Add Record", "View Summary", "View Graph"])

if menu == "Add Record":
    st.header("➕ Add New Expense or Income")

    type_ = st.selectbox("Select Type", ["Expense", "Income"])

    amount = st.number_input("Amount", min_value=0.0, format="%.2f")

    if type_ == "Expense":
        category = st.selectbox("Category", ["Leisure", "Bills", "Other"])
        sub_category = "N/A"

        if category == "Bills":
            sub_category = st.selectbox("Sub-Category", ["Groceries", "Rent/Mortgage", "Transport", "Utilities", "Medical Bills"])
        else:
            sub_category = "N/A"
    else:
        category = "Income"
        sub_category = "N/A"

    if st.button("Add Record"):
        if amount > 0:
            date = datetime.now().strftime("%Y-%m-%d")
            new_row = pd.DataFrame([{
                "Amount": amount,
                "Category": category,
                "Sub-Category": sub_category,
                "Date": date,
                "Type": type_
            }])
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
            st.success(f"{type_} of ${amount:.2f} added successfully!")
        else:
            st.error("Please enter a valid amount.")

elif menu == "View Summary":
    st.header("📊 Monthly Summary")

    df = st.session_state.expenses

    if df.empty:
        st.warning("No records found.")
    else:
        df['Date'] = pd.to_datetime(df['Date'])
        current_month = datetime.now().strftime("%Y-%m")
        df_month = df[df['Date'].dt.strftime('%Y-%m') == current_month]

        income_total = df_month[df_month['Type'] == "Income"]['Amount'].sum()
        expense_total = df_month[df_month['Type'] == "Expense"]['Amount'].sum()
        net_total = income_total - expense_total

        st.write(f"**Income:** ${income_total:.2f}")
        st.write(f"**Expenses:** ${expense_total:.2f}")
        st.write(f"**Net Total:** ${net_total:.2f}")

        if not df_month.empty:
            st.subheader("Expenses by Category")
            expense_df = df_month[df_month['Type'] == "Expense"]
            if not expense_df.empty:
                grouped = expense_df.groupby(['Category', 'Sub-Category'])['Amount'].sum().reset_index()
                st.dataframe(grouped)

elif menu == "View Graph":
    st.header("📈 Expense Breakdown")

    df = st.session_state.expenses

    if df.empty or 'Amount' not in df:
        st.warning("No expense data to plot.")
    else:
        df['Date'] = pd.to_datetime(df['Date'])
        current_month = datetime.now().strftime("%Y-%m")
        df_month = df[df['Date'].dt.strftime('%Y-%m') == current_month]

        expense_df = df_month[df_month['Type'] == "Expense"]

        if not expense_df.empty:
            expense_df['Label'] = expense_df.apply(lambda x: f"{x['Category']} - {x['Sub-Category']}" if x['Sub-Category'] != "N/A" else x['Category'], axis=1)
            grouped = expense_df.groupby('Label')['Amount'].sum()

            fig, ax = plt.subplots()
            ax.pie(grouped.values, labels=grouped.index, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')
            st.pyplot(fig)
        else:
            st.info("No expenses for this month yet.")

st.sidebar.caption("Made with 💻 by Britney Forrester")
