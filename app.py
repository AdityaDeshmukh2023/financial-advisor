from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in .env file")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains


# Helper function to generate external links using AI
def generate_external_links(query: str):
    prompt = (
        f"Provide external resources such as articles or videos related to: {query}"
    )
    response = model.generate_content(prompt)
    links = response.text.strip().split("\n")
    return [
        {
            "title": link,
            "url": f"https://www.google.com/search?q={link.replace(' ', '+')}",
        }
        for link in links
    ]


# Financial Advisor
@app.route("/financial-advisor", methods=["POST"])
def financial_advisor():
    data = request.json
    prompt = f"""
    As a financial advisor for rural India, provide guidance in simple language for:

    Background:
    - Name: {data['name']}
    - Age: {data['age']}
    - Location: {data['location']}
    - Monthly Income: ₹{data['monthly_income']}
    - Expenditure: ₹{data['expenditure']}
    - Financial Goals: {data['financial_goals']}
    - Investments: {data['investments']}
    - Loans: {data['loans']}

    Ask the following questions:
    1. What is your target savings percentage?
    2. Are you interested in any specific investment plans?
    3. Do you want advice on budgeting, savings, or retirement plans?
    
    Provide detailed advice in a simplified manner, using examples and suggestions.
    """

    # Generate advice based on user input
    response = model.generate_content(prompt)

    # Generate external links for further learning
    external_links = generate_external_links(
        "saving money, investments, financial goals"
    )

    return jsonify(
        {
            "title": "Financial Advice",
            "information": response.text,
            "external_links": external_links,
        }
    )


# Business Advisor
@app.route("/business-advisor", methods=["POST"])
def business_advisor():
    data = request.json
    prompt = f"""
    As a business advisor for rural India, provide guidance on the following business idea:

    Background:
    - Business Idea: {data['business_idea']}
    - Current Finances: ₹{data['current_finances']}
    - Monthly Revenue: ₹{data['monthly_revenue']}
    - Expenses: ₹{data['expenses']}
    - Financial Goals: {data['financial_goals']}
    
    Ask the following questions:
    1. What is your expected growth rate for the business?
    2. Do you need advice on expanding, managing cash flow, or optimizing expenses?
    
    Provide practical advice in simple language on:
    1. Business setup steps
    2. Financial planning for the business
    3. Identifying potential funding or government schemes
    """

    # Generate advice based on user input
    response = model.generate_content(prompt)

    # Generate external links for business guidance
    external_links = generate_external_links(
        "starting a business, managing finances, business growth"
    )

    return jsonify(
        {
            "title": "Business Advice",
            "information": response.text,
            "external_links": external_links,
        }
    )


# Loan Advisor
@app.route("/loan-advisor", methods=["POST"])
def loan_advisor():
    data = request.json
    prompt = f"""
    As a loan advisor, provide guidance based on the following loan details:

    Background:
    - Loan Amount: ₹{data['loan_amount']}
    - Interest Rate: {data['interest_rate']}%
    - Loan Term: {data['loan_term']} years
    - Risk Management: {data['risk_management']}
    - Current Debts: ₹{data['current_debts']}
    
    Ask the following questions:
    1. What is the purpose of the loan (e.g., home, business, education)?
    2. Do you need advice on adjusting your loan amount, term, or interest rate?
    3. Would you like information on government schemes for loans or financial relief?
    
    Provide advice on:
    1. Choosing the right loan
    2. Risks involved and risk management
    3. Loan repayment strategies
    """

    # Generate advice based on user input
    response = model.generate_content(prompt)

    # Generate external links related to loans and finance
    external_links = generate_external_links(
        "loan types, loan comparison, financial planning"
    )

    return jsonify(
        {
            "title": "Loan Advice",
            "information": response.text,
            "external_links": external_links,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
