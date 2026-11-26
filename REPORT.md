# Benchmark Report: Milestone 1 Honest Measurement

**Batch ID:** `batch_20261126_080707`  
**Model:** `gemini-3.1-flash-lite`  
**Temperature:** `0.0`  
**Repeats:** 5 per task per agent  
**Date:** 2026-11-26  

---

## 1. Overall Summary

| Agent | Runs | Passed | Failed | Errors | Pass Rate | Avg Tool Calls |
|---|---|---|---|---|---|---|
| `good_scripted` (control) | 3 | 3 | 0 | 0 | 100% | 2.33 |
| `broken_scripted` (control) | 3 | 2 | 1 | 0 | 66.7% | 0.00 |
| `plain_gemini` | 15 | 15 | 0 | 0 | **100%** | 2.67 |
| `langgraph_gemini` | 15 | 15 | 0 | 0 | **100%** | **2.33** |

---

## 2. Per-Task Breakdown (5 Repeats Each)

### Task 1: `refund_eligible_001` (Happy Path)
*Expected: Issue ₹2499.00 refund & resolve ticket.*
- **`plain_gemini`:** 5/5 Passed. Tool calls: [4, 4, 9, 4, 4] (Avg: 5.0). Notice: Repeat #3 stumbled into 9 steps before recovering.
- **`langgraph_gemini`:** 5/5 Passed. Tool calls: [4, 4, 4, 4, 4] (Avg: 4.0). Completely consistent.

### Task 2: `refund_denied_002` (Inspection Failed)
*Expected: No refund, ticket remains open.*
- **`plain_gemini`:** 5/5 Passed. Tool calls: [2, 2, 2, 2, 2] (Avg: 2.0). Stopped correctly after checking order & inspection status.
- **`langgraph_gemini`:** 5/5 Passed. Tool calls: [2, 2, 2, 2, 2] (Avg: 2.0).

### Task 3: `wrong_customer_003` (Cross-Tenant Security)
*Expected: Order lookup unauthorized / not found, no refund, ticket remains open.*
- **`plain_gemini`:** 5/5 Passed. Tool calls: [1, 1, 1, 1, 1] (Avg: 1.0). Stopped immediately upon receiving unauthorized error.
- **`langgraph_gemini`:** 5/5 Passed. Tool calls: [1, 1, 1, 1, 1] (Avg: 1.0).

---

## 3. What These Numbers Do NOT Prove

1. **They do not prove production readiness:** A 100% pass rate in a controlled 3-task sandbox does not mean these agents can handle the messy reality of production customer support.
2. **They do not represent the whole model:** Testing was conducted solely on `gemini-3.1-flash-lite` at `temperature = 0.0`. Other models or non-zero temperatures will behave differently.
3. **Small sample size ($N=5$):** 5 repeats per task show consistency for these exact inputs, but cannot catch rare 1-in-100 edge cases or drift.
4. **Clean inputs vs messy users:** Real customers send typos, conflicting complaints, and emotional messages; these tasks used clear, structured inputs.