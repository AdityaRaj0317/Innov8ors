import os
import json
import uuid
from datetime import datetime
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EscrowExecutionAgent:
    """
    The Real-Time Financial Execution Agent for SynapEscrow.
    Bridges AI verification with financial movement commands.
    """

    SYSTEM_PROMPT = """
Role: You are the Real-Time Financial Execution Agent for SynapEscrow. You operate as a secure state machine that bridges AI verification with financial movement.

Task: Monitor the incoming AQA_RESULT and the VAULT_LEDGER. If the verification signal is 1 (True), you must generate a high-precision execution command that our backend will use to trigger a live API call to the payment gateway.

Inputs (To be provided by current context):
- Current_Milestone_JSON: (Milestone details)
- AQA_Verification_Status: (PASS or FAIL)
- Vault_Balance: (Current balance in vault)
- Is_Final_Milestone: (Boolean)
- Success_Fee: (Amount of the success fee)

Execution Logic:
1. IF PASS: Calculate the exact payout, subtract from the vault, and set action to TRANSFER_AUTH. 
   - Note: If Is_Final_Milestone is True, add the Success_Fee to the payload amount.
2. IF FAIL: Maintain vault lock, set action to LOCK_FUNDS, and generate a rejection log.
3. IF REFUND (Special cases): Set action to REFUND_INITIATED.

Output (STRICT JSON for Backend Hook):
{
"execution_id": "AUTO-GEN-UUID",
"timestamp": "ISO-8601-FORMAT",
"action_code": "TRANSFER_AUTH | LOCK_FUNDS | REFUND_INITIATED",
"payload": {
"amount_numeric": 0.00,
"currency": "USD",
"target_status": "PAID",
"remaining_escrow_depth": 0.00
},
"audit_log": "String describing the verification and authorization."
}

Constraint: Zero subjectivity. You are a financial terminal. Any error in calculation or logic will result in a "Financial Integrity Failure."
Return ONLY the raw JSON object.
"""

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment.")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model_id = "google/gemini-2.0-flash-001"

    def execute_payout_logic(self, milestone: Dict, aqa_status: bool, vault_balance: float, is_final: bool, success_fee: float) -> Dict:
        """
        Processes the execution command based on AQA results and vault state.
        """
        # We pass the state to the LLM to generate the secure execution command string/JSON
        # as per the "Financial Execution Agent" prompt requirement.
        
        context = {
            "Current_Milestone_JSON": milestone,
            "AQA_Verification_Status": "PASS" if aqa_status else "FAIL",
            "Vault_Balance": vault_balance,
            "Is_Final_Milestone": is_final,
            "Success_Fee": success_fee
        }

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"PROCESS EXECUTION FOR CONTEXT: {json.dumps(context)}"}
                ]
            )
            
            text_result = response.choices[0].message.content.strip()
            
            # Robust JSON parsing
            if "```json" in text_result:
                text_result = text_result.split("```json")[1].split("```")[0].strip()
            elif "```" in text_result:
                text_result = text_result.split("```")[1].split("```")[0].strip()
            
            return json.loads(text_result)
        except Exception as e:
            # Fallback local logic if AI service fails (Safety Protocol)
            return {
                "execution_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "action_code": "LOCK_FUNDS",
                "payload": {
                    "amount_numeric": 0.0,
                    "currency": "USD",
                    "target_status": "LOCKED",
                    "remaining_escrow_depth": vault_balance
                },
                "audit_log": f"SAFETY LOCK TRIGGERED: Communication error with execution logic. {str(e)}"
            }

if __name__ == "__main__":
    # Test execution agent
    agent = EscrowExecutionAgent()
    milestone_data = {"title": "Design", "amount": "100.0 USD"}
    # Simulate a PASS/FINAL
    result = agent.execute_payout_logic(milestone_data, True, 500.0, False, 50.0)
    print(json.dumps(result, indent=2))
