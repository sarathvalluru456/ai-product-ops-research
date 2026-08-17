# AI Product Ops Research — 100-App Agent Readiness Study

An agentic research pipeline that evaluates 100 applications for AI-agent/toolkit readiness.

The project researches authentication, credential access, API surface, MCP availability, buildability, blockers, and supporting evidence, then produces an interactive case study.

## What I Built

The pipeline takes a predefined list of 100 applications and:

1. Identifies the application's category and purpose.
2. Researches authentication methods.
3. Determines whether developer credentials are self-serve or gated.
4. Evaluates the documented API surface.
5. Checks for MCP availability.
6. Determines agent/toolkit readiness.
7. Captures supporting documentation URLs.
8. Assigns a confidence level.
9. Aggregates the research into cross-app patterns.
10. Runs automated quality checks and human verification.

## Research Pipeline

```text
100 App Research Set
        ↓
Research Agent
        ↓
Documentation / Evidence Collection
        ↓
Structured JSON Dataset
        ↓
Analysis
        ↓
Automated Quality Checks
        ↓
Human Verification
        ↓
Case Study