import os
import json
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BlueprintingAgent:
    """
    The Blueprinting Agent acts as the Project Manager.
    It decomposes vague employer prompts into a technical, time-bound roadmap.
    """
    
    SYSTEM_PROMPT = """
Role: You are the core AI engine of an Autonomous Payment & Project Agent. Your purpose is to bridge the "Trust Gap" between employers and freelancers by removing manual oversight and subjective evaluations.

Objective: Perform "Intelligent Requirement Analysis" by decomposing vague employer prompts into a technical, time-bound roadmap.

Your Task: Generate a structured JSON object that will serve as the legal and technical "Definition of Done" for the project. This roadmap will be used to trigger automated micro-payouts.

Output Format (JSON Only):
{
"project_summary": "A 2-sentence technical overview of the goal.",
"milestones": [
{
"title": "Short name of the phase.",
"technical_checklist": [
"3-5 objective, AI-verifiable criteria (e.g., 'GitHub repo contains a Dockerfile', 'API endpoint /health returns 200')."
],
"estimated_days": "Number of days for this phase.",
"payout_percentage": "The % of total funds released upon AQA verification."
}
]
}

Constraints:
- No conversational filler.
- Checklist items must be binary (either met or unmet) to avoid payment disputes.
- Ensure the total payout_percentage across all milestones equals 100%.
- Return ONLY the raw JSON object without any backticks or formatting.
"""

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment. Please check your .env file.")
        
        # Initialize the OpenAI Client configured for OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        # Using Gemini 2.0 Flash via OpenRouter for high performance
        self.model_id = "google/gemini-2.0-flash-001"

    def generate_roadmap(self, project_description: str) -> Dict:
        """
        Calls the OpenRouter API to generate a structured roadmap with retries.
        """
        import time
        prompt = f"{self.SYSTEM_PROMPT}\n\nProject Description: {project_description}"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[
                        {"role": "user", "content": prompt}
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
                        print(f"Rate limited (OpenRouter). Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    return {"error": "Quota exceeded (429) via OpenRouter after multiple retries."}
                
                return {"error": f"Failed to generate roadmap: {error_str}"}
        
        return {"error": "Unexpected error in retry loop."}

if __name__ == "__main__":
    agent = BlueprintingAgent()
    print("--- SynapEscrow Blueprinting Agent: Test Interface ---")
    sample_desc = input("Describe your freelance project (Natural Language): ")
    
    if not sample_desc.strip():
        print("Error: Project description cannot be empty.")
    else:
        print("\nAnalyzing requirements and generating roadmap...\n")
        roadmap = agent.generate_roadmap(sample_desc)
        print(json.dumps(roadmap, indent=2))
        print("\n--- Roadmap Generated Successfully ---")
