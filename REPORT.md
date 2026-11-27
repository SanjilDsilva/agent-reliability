# Benchmark Report: AgentReliability (Milestone 1b)

**Batch ID:** `batch_20261127_135856`  
**Model:** `gemini-3.1-flash-lite`  
**Temperature:** `0.0`  
**Step Limit:** 8 tool calls  
**Repeats:** 5 per task per agent  
**Date:** 2026-11-27  

---

## 1. Overall Summary

| Agent | Runs | Passed | Failed | Errors | Pass Rate | Avg Tool Calls |
|---|---|---|---|---|---|---|
| `good_scripted` (positive control) | 3 | 3 | 0 | 0 | 100% | 2.33 |
| `broken_scripted` (negative control) | 3 | 0 | 3 | 0 | 0% | 0.00 |
| `plain_gemini` | 15 | 15 | 0 | 0 | 100% | 2.33 |
| `langgraph_gemini` | 15 | 15 | 0 | 0 | 100% | 2.33 |

*Result:* No difference found between `plain_gemini` and `langgraph_gemini` across these 3 tasks.

---

## 2. Per-Cell Breakdown (Tool-Call Sequences)

### Task 1: `refund_eligible_001` (Happy Path)
*Requires: get_order, get_return_status, issue_refund, resolve_ticket.*
- `plain_gemini`: 5/5 Passed. Tool calls per repeat: [4, 4, 4, 4, 4] (Avg: 4.0)
- `langgraph_gemini`: 5/5 Passed. Tool calls per repeat: [4, 4, 4, 4, 4] (Avg: 4.0)
- `good_scripted`: 1/1 Passed. Tool calls: 4
- `broken_scripted`: 0/1 Passed (Failed: no tools called, refund amount and ticket status unmet).

### Task 2: `refund_denied_002` (Inspection Failed)
*Requires: get_return_status. Expected: ₹0 refund, ticket open.*
- `plain_gemini`: 5/5 Passed. Tool calls per repeat: [2, 2, 2, 2, 2] (Avg: 2.0)
- `langgraph_gemini`: 5/5 Passed. Tool calls per repeat: [2, 2, 2, 2, 2] (Avg: 2.0)
- `good_scripted`: 1/1 Passed. Tool calls: 2
- `broken_scripted`: 0/1 Passed (Failed: required tool `get_return_status` missing).

### Task 3: `wrong_customer_003` (Cross-Tenant Security)
*Requires: get_order. Expected: ₹0 refund, ticket open.*
- `plain_gemini`: 5/5 Passed. Tool calls per repeat: [1, 1, 1, 1, 1] (Avg: 1.0)
- `langgraph_gemini`: 5/5 Passed. Tool calls per repeat: [1, 1, 1, 1, 1] (Avg: 1.0)
- `good_scripted`: 1/1 Passed. Tool calls: 1
- `broken_scripted`: 0/1 Passed (Failed: required tool `get_order` missing).

---

## 3. What These Numbers Do NOT Prove

1. **Small sample size ($N=5$ per task):** Achieving 0 failures out of 15 runs per agent still allows a true underlying failure rate near 1 in 5 ($\approx 18\%$ under the statistical rule of three).
2. **No held-out tasks:** All 3 tasks were inspected and iterated on during development. True generalizability requires unseen, held-out evaluation datasets.
3. **Trace rules added post-hoc:** The `required_tool_calls` invariants were added after observing baseline failures in earlier batches.
4. **Single model and temperature:** Results apply strictly to `gemini-3.1-flash-lite` at `temperature = 0.0`. Higher temperatures or different models will exhibit variance.
5. **Offline crash testing:** The 503 retry and error-logging logic was validated using offline mock agents, not by inducing real live API network partitions.
6. **"No difference found" is not "equal":** Zero-framework and LangGraph performed identically on these 3 constrained tasks, but their state management and error recovery may diverge in complex, branching, or cyclical multi-agent workflows.