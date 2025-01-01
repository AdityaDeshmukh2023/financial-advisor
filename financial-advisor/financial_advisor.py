from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in .env file")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FinancialProfile(BaseModel):
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
    return f"""As a financial advisor for rural India, provide guidance in {profile.preferred_language} for:

Background:
- Name: {profile.name}
- Age: {profile.age}
- Location: {profile.location}
- Monthly Income: ₹{profile.monthly_income}
- Family Size: {profile.family_size}
- Business Interest: {profile.business_type}
- Current Savings: ₹{profile.existing_savings}
- Financial Goal: {profile.financial_goal}
- Risk Tolerance: {profile.risk_tolerance}

Please provide detailed advice on:
1. Business Planning:
   - Initial investment needed for {profile.business_type}
   - Step-by-step setup process
   - Local regulations and requirements

2. Financial Planning:
   - Monthly budget breakdown
   - Savings targets
   - Emergency fund recommendations

3. Government Schemes and Support
4. Risk Management
5. Basic Financial Education

Please provide practical, actionable steps in simple language."""

@app.get("/", response_class=HTMLResponse)
async def get_html():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/get-financial-advice")
async def get_financial_advice(profile: FinancialProfile):
    try:
        # Generate the prompt
        prompt = generate_financial_advice_prompt(profile)
        
        # Get response from Gemini
        response = model.generate_content(prompt)
        
        return {
            "status": "success",
            "data": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/business-types")
async def get_business_types():
    return {
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
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)