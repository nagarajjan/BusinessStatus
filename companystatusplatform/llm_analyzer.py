# llm_analyzer.py
from openai import OpenAI
from config import OPENAI_API_KEY
import pandas as pd

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_insights(financial_df: pd.DataFrame, scraped_text: str):
    """Generates comprehensive business insights using an LLM."""
    if OPENAI_API_KEY == 'YOUR_API_KEY_HERE' or not OPENAI_API_KEY:
        return "Insight generation requires a valid OpenAI API key in config.py or environment variables."

    # Use a descriptive summary to stay within token limits
    financial_summary = financial_df.describe().to_string() 
    prompt = f"""
    Analyze the following company data and provide a comprehensive business status report.

    Financial Data Summary (from Excel file):
    {financial_summary}

    External Scraped Data (SEC filings, market, customer feedback):
    {scraped_text}

    Provide insights on:
    1. Overall Company Health (Score 1-10)
    2. Key Financial Strengths and Weaknesses
    3. Competitive Landscape and Market Position
    4. Primary Risks and Opportunities
    5. Actionable Recommendations

    Format the response using markdown.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error with LLM insight generation: {e}"


def run_simulation(financial_df: pd.DataFrame, scenario: str):
    """Runs a 'what if' simulation using the LLM."""
    if OPENAI_API_KEY == 'YOUR_API_KEY_HERE' or not OPENAI_API_KEY:
        return "Simulation requires a valid OpenAI API key."
        
    financial_summary = financial_df.describe().to_string()
    prompt = f"""
    Based on the following financial data summary:
    {financial_summary}

    Analyze the potential impact of this scenario: "{scenario}".

    Provide a simulated report detailing the potential outcomes, changes in key metrics (e.g., sales, profit), and recommendations.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error with LLM simulation: {e}"

