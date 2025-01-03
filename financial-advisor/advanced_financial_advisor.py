from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import google.generativeai as genai
from enum import Enum
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in .env file")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

app = FastAPI()

class IncomeSource(str, Enum):
    AGRICULTURE = "agriculture"
    DAILY_WAGE = "daily_wage"
    SMALL_BUSINESS = "small_business"
    LIVESTOCK = "livestock"
    HANDICRAFTS = "handicrafts"
    OTHER = "other"

class QueryType(str, Enum):
    BUSINESS_ADVICE = "business_advice"
    SAVINGS = "savings"
    LOAN = "loan"
    GOVERNMENT_SCHEMES = "government_schemes"
    INVESTMENT = "investment"
    INSURANCE = "insurance"
    GENERAL = "general"

class FinancialQuery(BaseModel):
    query_type: QueryType
    question: str
    language: str = Field(default="English", description="Preferred language for response")
    
    # Context information
    monthly_income: Optional[float] = Field(None, description="Monthly income in INR")
    income_sources: Optional[List[IncomeSource]] = Field(None, description="Sources of income")
    location: Optional[str] = Field(None, description="State/District")
    age: Optional[int] = Field(None, description="Age of the person")
    family_size: Optional[int] = Field(None, description="Number of family members")
    has_bank_account: Optional[bool] = Field(None, description="Whether person has a bank account")
    education_level: Optional[str] = Field(None, description="Education level")
    existing_loans: Optional[float] = Field(None, description="Total existing loans in INR")

def load_scheme_database():
    """Load government scheme database from JSON file"""
    try:
        with open("scheme_database.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to basic schemes if file not found
        return {
            "agriculture": ["PM-KISAN", "Kisan Credit Card", "Soil Health Card Scheme"],
            "business": ["PMEGP", "MUDRA Loans", "Stand-Up India"],
            "social_security": ["PM Jeevan Jyoti Bima Yojana", "PM Suraksha Bima Yojana"],
            "women_specific": ["Mahila Samman Savings Certificate", "STEP Scheme"]
        }

def generate_context_based_prompt(query: FinancialQuery) -> str:
    schemes = load_scheme_database()
    
    # Build context section
    context = f"""As an expert financial advisor specialized in rural finance and financial inclusion:

Query Type: {query.query_type.value}
Question: {query.question}
Language: {query.language}

Available Context:"""

    if query.monthly_income:
        context += f"\n- Monthly Income: ₹{query.monthly_income}"
    if query.income_sources:
        context += f"\n- Income Sources: {', '.join(source.value for source in query.income_sources)}"
    if query.location:
        context += f"\n- Location: {query.location}"
    if query.age:
        context += f"\n- Age: {query.age}"
    if query.family_size:
        context += f"\n- Family Size: {query.family_size}"
    if query.has_bank_account is not None:
        context += f"\n- Has Bank Account: {'Yes' if query.has_bank_account else 'No'}"
    if query.education_level:
        context += f"\n- Education Level: {query.education_level}"
    if query.existing_loans:
        context += f"\n- Existing Loans: ₹{query.existing_loans}"

    # Add query-specific guidance
    prompt_additions = {
        QueryType.BUSINESS_ADVICE: """
Focus on:
- Local market opportunities and challenges
- Initial investment requirements and potential returns
- Risk assessment and mitigation strategies
- Required licenses and regulations
- Local success stories and common pitfalls
- Step-by-step implementation plan""",
        
        QueryType.SAVINGS: """
Focus on:
- Practical savings methods for irregular income
- Priority-based saving goals
- Local savings groups and self-help groups
- Digital banking and mobile money options
- Emergency fund planning
- Child education planning""",
        
        QueryType.LOAN: """
Focus on:
- Suitable loan products (priority sector, MUDRA, KCC)
- Documentation requirements
- Interest rates and EMI calculations
- Risk assessment
- Alternatives to formal loans
- Debt management strategies""",
        
        QueryType.GOVERNMENT_SCHEMES: """
Focus on:
- Eligibility criteria and benefits
- Application process and required documents
- Local success stories
- Common application mistakes to avoid
- Timeline and follow-up process
- Alternative schemes if not eligible""",
        
        QueryType.INVESTMENT: """
Focus on:
- Safe and suitable investment options
- Risk assessment
- Local investment opportunities
- Avoiding fraud and scams
- Long-term vs short-term planning
- Diversification strategies""",
        
        QueryType.INSURANCE: """
Focus on:
- Relevant insurance products (crop, health, life)
- Premium affordability
- Claim process
- Coverage understanding
- Family protection planning
- Government insurance schemes""",
        
        QueryType.GENERAL: """
Focus on:
- Practical and actionable advice
- Local context and cultural considerations
- Risk awareness and protection
- Long-term financial health
- Available support systems
- Step-by-step guidance"""
    }

    context += f"\n\n{prompt_additions[query.query_type]}"
    
    context += """

Additional Guidelines:
1. Provide advice in simple, clear language with local examples
2. Include specific numbers and calculations where relevant
3. Suggest both immediate actions and long-term planning
4. Address common risks and misconceptions
5. Include relevant government schemes and support programs
6. Provide alternative solutions for different scenarios
7. Include contact information for local resources when applicable

Please provide comprehensive advice that is practical, actionable, and sensitive to rural financial realities."""

    return context
# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add a route for the root path
@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

    
@app.post("/get-advice")
async def get_financial_advice(query: FinancialQuery):
    try:
        prompt = generate_context_based_prompt(query)
        response = model.generate_content(prompt)
        
        return {
            "status": "success",
            "query_type": query.query_type,
            "advice": response.text,
            "metadata": {
                "language": query.language,
                "location": query.location,
                "context_provided": bool(query.monthly_income or query.income_sources)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/supported-query-types")
async def get_query_types():
    return {
        "query_types": [
            {
                "type": query_type.value,
                "description": query_type.name.replace("_", " ").title()
            }
            for query_type in QueryType
        ]
    }

@app.get("/income-sources")
async def get_income_sources():
    return {
        "income_sources": [
            {
                "source": source.value,
                "description": source.name.replace("_", " ").title()
            }
            for source in IncomeSource
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)