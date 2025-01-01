import streamlit as st
import requests
import json

# Set your backend Flask URL
API_URL = "http://127.0.0.1:5000"  # Replace with your Flask backend URL if different


# Helper function to send data to the Flask backend
def send_request(endpoint, data):
    try:
        response = requests.post(f"{API_URL}/{endpoint}", json=data)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the server: {e}")
        return None


# Financial Advisor Section
def financial_advisor():
    st.header("Financial Advisor")

    # Input fields for financial data
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=18)
    location = st.text_input("Location")
    monthly_income = st.number_input("Monthly Income (₹)", min_value=0.0)
    expenditure = st.number_input("Monthly Expenditure (₹)", min_value=0.0)
    financial_goals = st.text_input("Financial Goals")
    investments = st.text_area("Investments (e.g., stocks, mutual funds)")
    loans = st.text_area("Loans (e.g., home loan, personal loan)")

    if st.button("Get Financial Advice"):
        financial_data = {
            "name": name,
            "age": age,
            "location": location,
            "monthly_income": monthly_income,
            "expenditure": expenditure,
            "financial_goals": financial_goals,
            "investments": investments,
            "loans": loans,
        }

        # Send data to backend and get response
        result = send_request("financial-advisor", financial_data)
        if result:
            st.write(f"**{result['title']}**")
            st.write(result["information"])
            st.subheader("Helpful Resources:")
            for link in result["external_links"]:
                st.markdown(f"[{link['title']}]({link['url']})")


# Business Advisor Section
def business_advisor():
    st.header("Business Advisor")

    # Input fields for business data
    business_idea = st.text_input("Business Idea")
    current_finances = st.number_input("Current Finances (₹)", min_value=0.0)
    monthly_revenue = st.number_input("Monthly Revenue (₹)", min_value=0.0)
    expenses = st.number_input("Monthly Expenses (₹)", min_value=0.0)
    business_goals = st.text_input("Business Goals")

    if st.button("Get Business Advice"):
        business_data = {
            "business_idea": business_idea,
            "current_finances": current_finances,
            "monthly_revenue": monthly_revenue,
            "expenses": expenses,
            "financial_goals": business_goals,
        }

        # Send data to backend and get response
        result = send_request("business-advisor", business_data)
        if result:
            st.write(f"**{result['title']}**")
            st.write(result["information"])
            st.subheader("Helpful Resources:")
            for link in result["external_links"]:
                st.markdown(f"[{link['title']}]({link['url']})")


# Loan Advisor Section
def loan_advisor():
    st.header("Loan Advisor")

    # Input fields for loan data
    loan_amount = st.number_input("Loan Amount (₹)", min_value=0.0)
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0)
    loan_term = st.number_input("Loan Term (years)", min_value=1)
    risk_management = st.text_input("Risk Management (Low, Medium, High)")
    current_debts = st.number_input("Current Debts (₹)", min_value=0.0)

    if st.button("Get Loan Advice"):
        loan_data = {
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "loan_term": loan_term,
            "risk_management": risk_management,
            "current_debts": current_debts,
        }

        # Send data to backend and get response
        result = send_request("loan-advisor", loan_data)
        if result:
            st.write(f"**{result['title']}**")
            st.write(result["information"])
            st.subheader("Helpful Resources:")
            for link in result["external_links"]:
                st.markdown(f"[{link['title']}]({link['url']})")


# Main Streamlit App Layout
def main():
    st.title("Financial, Business, and Loan Advisor Chatbots")

    # Add buttons for each section
    menu = ["Financial Advisor", "Business Advisor", "Loan Advisor"]
    choice = st.sidebar.selectbox("Select an Advisor", menu)

    if choice == "Financial Advisor":
        financial_advisor()
    elif choice == "Business Advisor":
        business_advisor()
    elif choice == "Loan Advisor":
        loan_advisor()


if __name__ == "__main__":
    main()
