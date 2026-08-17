\# AI Product Ops Research — 100-App Agent Readiness Study



An agentic research pipeline for evaluating 100 applications for AI-agent/toolkit readiness.



\## What It Researches



For each application, the pipeline evaluates:



\- Category and product description

\- Authentication methods

\- Self-serve vs gated credential access

\- API surface and breadth

\- MCP availability

\- Agent/toolkit buildability

\- Main blockers

\- Supporting documentation

\- Confidence level



\## Pipeline



100 Apps

→ Research Agent

→ Evidence Collection

→ Structured Dataset

→ Analysis

→ Automated QA

→ Human Verification

→ Interactive Case Study



\## Final Dataset



\- 100 applications

\- 10 categories

\- Evidence for all 100 records

\- 71 self-serve

\- 41 with MCP identified

\- 72 agent-ready

\- 15 agent-ready with setup

\- 75 broad API surfaces

\- 89 high-confidence records



\## Verification



A 20-app sample was manually checked against documentation.



Results:



\- 20 apps reviewed

\- 14 exact matches

\- 5 partial matches

\- 1 miss

\- 70% strict-match accuracy

\- 95% directionally correct



The verification process intentionally exposed errors instead of treating the agent output as ground truth.



\## Automated QA



The QA process identified:



\- 4 potential cross-app references

\- 9 missing authentication fields

\- 8 missing API-type fields

\- 11 low/medium-confidence records



These findings were used to improve and qualify the final research.



\## Running Locally



Create a virtual environment:



```bash

python -m venv .venv

