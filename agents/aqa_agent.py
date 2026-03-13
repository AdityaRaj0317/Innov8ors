import os
import json
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AQAAgent:
    """
    The Automated Quality Assurance (AQA) Agent for SynapEscrow.
    Evaluates freelancer submissions against the technical roadmap checklist.
    """

    SYSTEM_PROMPT = """
Role: You are the Automated Quality Assurance (AQA) Agent for SynapEscrow. Your goal is to provide a neutral, intelligent evaluation of submitted work to ensure capital is only exchanged for verified value.

Input Data:
- Roadmap Context: The technical checklist for the current milestone (generated in Task 1).
- Freelancer Submission: The actual files, code snippets, or execution logs provided by the contractor.

Evaluation Criteria:
Compare the submission against every single item in the checklist. You must categorize the milestone into one of three states:
- Fully Completed: Every checklist item is 100% verified.
- Partially Completed: Some items are met, but others are missing or buggy. Provide specific technical feedback.
- Unmet: The submission does not address the core requirements or fails significantly.

Output Format (STRICT JSON):
{
"evaluation_status": "Fully Completed | Partially Completed | Unmet",
"checklist_results": [{ "criterion": "item string", "status": "Pass | Fail", "evidence": "Technical reason for status" }],
"payment_trigger_signal": "Boolean (True only if Fully Completed)",
"payout_recommendation": "Percentage (100% for Full, 0-50% for Partial, 0% for Unmet)",
"feedback_report": "Detailed technical guidance for the freelancer to reach 'Fully Completed'."
}

Constraint:
- Do not use subjective judgment. 
- If a checklist item requires a specific asset (e.g., 'Docker container') and none is found in the submission, that item is a 'Fail'.
- Return ONLY the raw JSON object without any backticks or formatting.
"""

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment. Please check your .env file.")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model_id = "google/gemini-2.0-flash-001"

    def evaluate_submission(self, checklist: List[str], submission: str) -> Dict:
        """
        Evaluates the freelancer's submission against the provided technical checklist.
        """
        import time
        prompt_content = f"""
ROADMAP CHECKLIST:
{json.dumps(checklist, indent=2)}

FREELANCER SUBMISSION:
{submission}
"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt_content}
                    ]
                )
                
                text_response = response.choices[0].message.content.strip()
                
                # Defensive parsing for JSON
                if "```json" in text_response:
                    text_response = text_response.split("```json")[1].split("```")[0].strip()
                elif "```" in text_response:
                    text_response = text_response.split("```")[1].split("```")[0].strip()
                
                return json.loads(text_response)
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5
                        print(f"AQA Agent Rate Limited. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                return {"error": f"AQA Evaluation Failed: {error_str}"}

        return {"error": "AQA logic timed out after retries."}

if __name__ == "__main__":
    # Quick standalone test
    aqa = AQAAgent()
    test_checklist = ["API endpoint /health returns 200", "Repository contains Dockerfile"]
    test_submission = "I have created the API but I forgot the Dockerfile. The health check is live."
    
    print("--- SynapEscrow AQA Agent Test ---")
    result = aqa.evaluate_submission(test_checklist, test_submission)
    print(json.dumps(result, indent=2))
