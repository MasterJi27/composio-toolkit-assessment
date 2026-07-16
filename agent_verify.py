import os
import json
import time
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def build_reviewer_agent():
    """Builds the AI Agent that verifies research output."""
    api_key = os.environ.get("OPENAI_API_KEY")
    kimchi_key = os.environ.get("KIMCHI_API_KEY")
    
    if kimchi_key and not api_key:
        llm = ChatOpenAI(
            api_key=kimchi_key,
            base_url="https://llm.kimchi.dev/openai/v1",
            model="kimi-k2.7",
            temperature=0.0
        )
    elif api_key:
        llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0.0)
    else:
        raise ValueError("No LLM API Key found in .env")

    prompt = PromptTemplate.from_template(
        """You are a QA Reviewer Agent.
Your job is to independently verify the following research conclusion for the app: {app_name}.

Original Conclusion:
Auth Type: {auth_type}
Access Status: {access_status}
Evidence URL: {evidence_url}

Read the documentation at {evidence_url} using your web scrape tool, and verify if the Auth Type and Access Status are correct.
Output EXACTLY as a JSON object:
{{
  "name": "{app_name}",
  "is_correct": true/false,
  "corrected_auth_type": "...",
  "corrected_access_status": "...",
  "reviewer_note": "Reason for correction or confirmation"
}}
"""
    )
    return prompt | llm | StrOutputParser()

def verify_app(chain, app_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        response = chain.invoke({
            "app_name": app_data['name'],
            "auth_type": app_data['auth_type'],
            "access_status": app_data['access_status'],
            "evidence_url": app_data['evidence_url']
        })
        
        if response.startswith("```json"):
            response = response[7:-3]
        elif response.startswith("```"):
            response = response[3:-3]
            
        return json.loads(response.strip())
    except Exception as e:
        print(f"Error verifying {app_data['name']}: {e}")
        return {
            "name": app_data['name'],
            "is_correct": False,
            "corrected_auth_type": "Unknown",
            "corrected_access_status": "Unknown",
            "reviewer_note": f"Verification failed: {e}"
        }

if __name__ == "__main__":
    print("Initializing Reviewer Agent...")
    try:
        reviewer_chain = build_reviewer_agent()
    except Exception as e:
        print(f"Initialization Failed: {e}")
        exit(1)

    # Sample batch to verify
    test_batch = [
        {
            "name": "Salesforce",
            "auth_type": "OAuth2",
            "access_status": "Gated",
            "evidence_url": "salesforce.com"
        }
    ]
    
    print("Starting verification loop...")
    for app in test_batch:
        res = verify_app(reviewer_chain, app)
        print(json.dumps(res, indent=2))
