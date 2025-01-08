from flask import Flask, request, jsonify
from flask_cors import CORS
from dataclasses import dataclass
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
model = genai.GenerativeModel('gemini-1.5-pro')

app = Flask(__name__)
CORS(app)

@dataclass
class FinancialProfile:
    name: str
    age: int
    location: str
    preferred_language: str
    monthly_income: float
    family_size: int
    business_type: str
    existing_savings: float
    financial_goal: str
    risk_tolerance: str

def generate_financial_advice_prompt(profile: FinancialProfile) -> str:
    return f"""Generate a detailed financial advice JSON response for a rural entrepreneur with the following format:
{{
  "clientDetails": {{
    "name": "{profile.name}",
    "age": {profile.age},
    "location": "{profile.location}",
    "monthlyIncome": {profile.monthly_income},
    "familySize": {profile.family_size},
    "businessInterest": "{profile.business_type}",
    "currentSavings": {profile.existing_savings},
    "financialGoal": "{profile.financial_goal}",
    "riskTolerance": "{profile.risk_tolerance}"
  }},
  "financialAdvice": {{
    "businessPlanning": {{
      "initialInvestment": {{
        "text": "<overview of investment needed>",
        "details": [
          {{"item": "<item1>", "cost": "<cost1>"}},
          {{"item": "<item2>", "cost": "<cost2>"}}
        ]
      }},
      "setupProcess": [
        "<step1>",
        "<step2>"
      ],
      "localRegulations": "<regulations text>"
    }},
    "financialPlanning": {{
      "monthlyBudget": {{
        "text": "<budget overview>",
        "details": [
          {{"item": "<expense1>", "amount": "<amount1>"}},
          {{"item": "<expense2>", "amount": "<amount2>"}}
        ]
      }},
      "savingsTargets": "<savings advice>",
      "emergencyFund": "<emergency fund advice>"
    }},
    "governmentSchemes": {{
      "text": "<schemes overview>",
      "schemes": [
        {{"name": "<scheme1>", "details": "<details1>"}},
        {{"name": "<scheme2>", "details": "<details2>"}}
      ]
    }},
    "riskManagement": {{
      "text": "<risk overview>",
      "strategies": [
        {{"point": "<strategy1>", "details": "<details1>"}},
        {{"point": "<strategy2>", "details": "<details2>"}}
      ]
    }},
    "financialEducation": {{
      "text": "<education overview>",
      "resources": [
        {{"name": "<resource1>", "link": "<link1>"}},
        {{"name": "<resource2>", "link": "<link2>"}}
      ]
    }}
  }}
}}

Please provide specific, practical advice for {profile.business_type} in {profile.location} considering their monthly income of ₹{profile.monthly_income} and savings of ₹{profile.existing_savings}."""

@app.route('/api/financial-advice', methods=['POST'])
def get_financial_advice():
    try:
        data = request.get_json()
        profile = FinancialProfile(**data)
        
        # Generate the prompt
        prompt = generate_financial_advice_prompt(profile)
        
        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Parse the response text as JSON and return directly
        return response.text, 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/business-types', methods=['GET'])
def get_business_types():
    return jsonify({
        "business_types": [
            "Dairy Farming",
            "Poultry Farming",
            "Small Retail Shop",
            "Handicrafts",
            "Agricultural Products",
            "Food Processing",
            "Tailoring",
            "Beauty Parlor",
            "General Store",
            "Vegetable Vending"
        ]
    })

@app.route('/add', methods=['GET'])
def add_numbers():
    try:
        # Get query parameters
        a = int(request.args.get('a', 0))
        b = int(request.args.get('b', 0))
        return jsonify({'result': a + b}), 200
    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
