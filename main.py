import json
from agents.blueprinting_agent import BlueprintingAgent
from agents.liquidity_manager import LiquidityManager
from agents.aqa_agent import AQAAgent
from agents.escrow_execution_agent import EscrowExecutionAgent

def run_project_flow():
    print("================================================")
    print("   SynapEscrow: Autonomous Project Lifecycle     ")
    print("================================================")

    # 1. Blueprinting Agent (Task 1)
    blueprint_agent = BlueprintingAgent()
    project_desc = input("\n[1] Blueprinting Agent: Describe the project requirements: ")
    
    print("\n[AI] Analyzing requirements and generating technical roadmap...")
    roadmap = blueprint_agent.generate_roadmap(project_desc)
    
    if "error" in roadmap:
        print(f"Error in Blueprinting: {roadmap['error']}")
        return

    print("\n--- Technical Roadmap (Definition of Done) ---")
    print(json.dumps(roadmap, indent=2))

    # 2. Liquidity Manager (Task 2)
    budget_val = input("\n[2] Liquidity Manager: Enter Total Project Budget (USD): ")
    try:
        total_budget = float(budget_val)
    except ValueError:
        print("Invalid budget. Defaulting to 1000.")
        total_budget = 1000.0

    liquidity_manager = LiquidityManager(total_budget=total_budget)
    print("\n[AI] Architecting budget proposal and escrow structure...")
    budget_proposal = liquidity_manager.generate_budget_proposal(roadmap)

    print("\n--- Financial Budget Proposal ---")
    print(json.dumps(budget_proposal, indent=2))
    
    print("\n[STATUS] Liquidity: " + budget_proposal["liquidity_status"])
    print("[ACTION] Employer: " + budget_proposal["employer_action_required"])

    # 3. AQA Agent (Task 3)
    print("\n--- Milestone Verification Phase ---")
    first_milestone = roadmap["milestones"][0]
    print(f"Current Milestone: {first_milestone['title']}")
    print(f"Checklist to satisfy: {first_milestone['technical_checklist']}")
    
    submission = input("\n[3] AQA Agent: Enter Freelancer Submission (e.g., code snippets, logs, or status): ")
    
    aqa_agent = AQAAgent()
    print("\n[AI] Reviewing submission against technical checklist...")
    eval_result = aqa_agent.evaluate_submission(first_milestone["technical_checklist"], submission)
    
    print("\n--- AQA Evaluation Report ---")
    print(json.dumps(eval_result, indent=2))
    
    is_passed = eval_result.get("payment_trigger_signal") is True

    # 4. Escrow Execution Agent (Task 4)
    print("\n[4] Escrow Agent: Processing financial state machine...")
    execution_agent = EscrowExecutionAgent()
    
    # Context for execution
    milestone_payout_info = budget_proposal["budget_proposal"]["milestone_payouts"][0]
    success_fee_str = budget_proposal["budget_proposal"]["final_success_fee"]
    success_fee_val = float(success_fee_str.split()[0])
    vault_balance = total_budget # Initially the full deposit
    
    # We check if it is the final milestone (for simulation, we'll assume it's NOT final if there are more)
    is_final = len(roadmap["milestones"]) == 1 

    execution_result = execution_agent.execute_payout_logic(
        milestone=milestone_payout_info,
        aqa_status=is_passed,
        vault_balance=vault_balance,
        is_final=is_final,
        success_fee=success_fee_val
    )

    print("\n--- Secure Financial Execution Command ---")
    print(json.dumps(execution_result, indent=2))

    # Real-Time Hook Simulation
    if execution_result.get("action_code") == "TRANSFER_AUTH":
        payout = execution_result["payload"]["amount_numeric"]
        print(f"\n[BACKEND HOOK] ACTION: TRANSFER_AUTH")
        print(f"[GATEWAY] Successfully sent {payout} USD to freelancer wallet.")
        print(f"[LEDGER] Remaining Vault Depth: {execution_result['payload']['remaining_escrow_depth']} USD")
    else:
        print(f"\n[BACKEND HOOK] ACTION: {execution_result.get('action_code')}")
        print("[GATEWAY] Payout blocked. Funds remaining in secure vault.")

    print("\n================================================")
    print("   SynapEscrow Process Complete (Simulation)     ")
    print("================================================")

if __name__ == "__main__":
    run_project_flow()
