import json
from typing import Dict, List

class LiquidityManager:
    """
    The Financial Liquidity Manager for SynapEscrow.
    Architects a fair budget proposal based on the technical roadmap.
    """

    def __init__(self, total_budget: float, currency: str = "USD"):
        self.total_budget = total_budget
        self.currency = currency
        # Success Fee is usually the last portion of the funds, e.g., 10%
        self.success_fee_percentage = 10.0

    def generate_budget_proposal(self, roadmap: Dict) -> Dict:
        """
        Takes a technical roadmap and generates a financial budget proposal.
        """
        milestones = roadmap.get("milestones", [])
        if not milestones:
            return {"error": "Invalid roadmap: No milestones found."}

        proposal_payouts = []
        
        # Calculate the base for milestone payouts (Total - Success Fee)
        available_for_milestones = self.total_budget * (1 - self.success_fee_percentage / 100)
        final_success_fee = self.total_budget * (self.success_fee_percentage / 100)

        running_total = 0.0

        for milestone in milestones:
            # Ensure percentage is treated as a number (AI might return it as a string)
            percentage = float(milestone.get("payout_percentage", 0))
            
            # percentage is of the technical completion, we map it to our available milestone budget
            amount = round((percentage / 100) * available_for_milestones, 2)
            
            proposal_payouts.append({
                "title": milestone.get("title", "Untitled Milestone"),
                "amount": f"{amount} {self.currency}",
                "type": "Micro-payout"
            })
            running_total += amount

        # Ensure the math is 100% accurate (adjustment for rounding errors if any)
        # However, for 100% sum, we check: payouts + success_fee = total_budget
        # Success fee is fixed at the end.
        
        # Format the final JSON output as requested
        output = {
            "budget_proposal": {
                "total_escrow_requirement": f"{self.total_budget} {self.currency}",
                "milestone_payouts": proposal_payouts,
                "final_success_fee": f"{round(final_success_fee, 2)} {self.currency}"
            },
            "employer_action_required": "Approve and Deposit Funds",
            "liquidity_status": "Awaiting Initial Deposit"
        }

        # Double check sum for internal validation
        total_payouts = sum([float(p["amount"].split()[0]) for p in proposal_payouts])
        calculated_total = round(total_payouts + round(final_success_fee, 2), 2)
        
        if calculated_total != self.total_budget:
            # Minor correction on the last milestone if rounding caused a mismatch
            diff = round(self.total_budget - calculated_total, 2)
            last_val = float(proposal_payouts[-1]["amount"].split()[0])
            proposal_payouts[-1]["amount"] = f"{round(last_val + diff, 2)} {self.currency}"

        return output

if __name__ == "__main__":
    # Test with a mock roadmap from Task 1
    mock_roadmap = {
        "project_summary": "A React portfolio with EmailJS integration.",
        "milestones": [
            {"title": "Project Setup", "payout_percentage": 20},
            {"title": "Core Features", "payout_percentage": 50},
            {"title": "Deployment", "payout_percentage": 30}
        ]
    }

    print("--- SynapEscrow Financial Liquidity Manager ---")
    budget_input = input("Enter Total Project Budget (e.g., 500): ")
    try:
        total = float(budget_input)
        manager = LiquidityManager(total_budget=total)
        proposal = manager.generate_budget_proposal(mock_roadmap)
        print(json.dumps(proposal, indent=2))
    except ValueError:
        print("Invalid budget amount.")
