from flask import Flask, request, jsonify
import google.generativeai as genai
from functools import wraps
from dotenv import load_dotenv
import os
from typing import Dict, Any
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in .env file")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

def validate_input(required_fields: list) -> callable:
    """Decorator to validate request input"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400
            
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_scheme_prompt(user_data: Dict[str, Any]) -> str:
    """Generate prompt for scheme recommendation"""
    return f"""You are a government scheme recommendation system. Based on the following user details, recommend ONE most relevant Indian government scheme.

User Details:
- Age: {user_data.get('age')}
- Income: ₹{user_data.get('income')} per annum
- State: {user_data.get('state')}
- Occupation: {user_data.get('occupation')}
- Category: {user_data.get('category', 'General')}

Provide your response strictly in the following JSON format, with no additional text:
{{
    "scheme_name": "Name of the scheme",
    "description": "Brief description of the scheme"
}}"""

def get_scheme_details_prompt(scheme_name: str) -> str:
    """Generate prompt for scheme details"""
    return f"""Provide detailed information about the Indian government scheme: {scheme_name}

Return your response strictly in the following JSON format, with no additional text:
{{
    "scheme_name": "Name of the scheme",
    "description": "Detailed description",
    "eligibility": "Eligibility criteria",
    "benefits": "Key benefits",
    "how_to_apply": "Application process"
}}"""

def extract_json_from_response(response_text: str) -> dict:
    """Extract JSON from Gemini response text"""
    try:
        # Try to find JSON content between curly braces
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
        raise ValueError("No JSON content found in response")
    except Exception as e:
        raise ValueError(f"Failed to extract JSON: {str(e)}")

@app.route('/api/recommend-scheme', methods=['POST'])
@validate_input(['age', 'income', 'state', 'occupation'])
def recommend_scheme():
    """Endpoint to recommend government schemes based on user details"""
    try:
        user_data = request.get_json()
        prompt = get_scheme_prompt(user_data)
        
        # Generate response from Gemini AI
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract and parse JSON from response
        scheme_data = extract_json_from_response(response_text)
        
        return jsonify(scheme_data), 200
        
    except ValueError as e:
        return jsonify({
            "error": f"Failed to process AI response: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/scheme-details', methods=['POST'])
@validate_input(['scheme_name'])
def get_scheme_details():
    """Endpoint to get detailed information about a specific scheme"""
    try:
        scheme_name = request.get_json()['scheme_name']
        prompt = get_scheme_details_prompt(scheme_name)
        
        # Generate response from Gemini AI
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract and parse JSON from response
        scheme_details = extract_json_from_response(response_text)
        
        return jsonify(scheme_details), 200
        
    except ValueError as e:
        return jsonify({
            "error": f"Failed to process AI response: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)