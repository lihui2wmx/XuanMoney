# XuanMoney

XuanMoney is an AI finance agent project focused on trustworthy financial analysis rather than free-form financial chat.

## Design principles

- **LLM for intent, planning, analysis, and explanation.**
- **Deterministic code for financial calculations and validation.**
- **Structured tools for data access; no direct unrestricted database access from the model.**
- **Evidence-first outputs: material claims should be traceable to source data and calculations.**
- **Human approval for any future high-risk financial action.**

## v0.1 scope

The first milestone is a read-only Finance Analysis Agent that can:

1. accept normalized financial statement data;
2. compute core profitability metrics;
3. perform period-over-period variance analysis;
4. validate accounting identities and calculation consistency;
5. produce structured findings with evidence;
6. expose the analysis workflow through a small Python service boundary.

Out of scope for v0.1: payments, journal posting, tax filing, ERP write-back, autonomous execution, unrestricted SQL, and production authentication.

## Planned architecture

```text
User / API
   |
   v
Finance Agent State Machine
   |-- intent / planning
   |-- controlled tool routing
   |-- analysis
   |-- response synthesis
   |
   +--> Finance Kernel (deterministic metrics and variance)
   +--> Validator (accounting and consistency checks)
   +--> Evidence Model (claim -> metric -> source)
   +--> Data Adapter (read-only, normalized input)
```

Development starts on `feat/finance-agent-v0.1` after this bootstrap commit.
