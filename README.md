# SynapEscrow: Autonomous Payment & Project Agent

SynapEscrow is an AI-driven platform designed to bridge the "Trust Gap" between employers and freelancers using automated project roadmaps and quality assurance triggers.

## Project Structure

- `agents/`: Core AI agents (Blueprinting, AQA, etc.)
- `schemas/`: JSON schemas for the "Definition of Done" and Milestone structures.
- `evaluators/`: Logic for the AQA agent to verify technical checklists.
- `contracts/`: (Future) Smart contract integration for automated payouts.

## Phase 1: The Blueprinting Agent
The Blueprinting Agent acts as the Project Manager. It ingests natural language project descriptions and outputs a technical roadmap in JSON format. This roadmap serves as the legal and technical "Definition of Done."
