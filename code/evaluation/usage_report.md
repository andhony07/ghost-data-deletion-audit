# Usage Report: Ghost Data Still Exists

HackerRank Orchestrate (October 2026)  
Challenge: **Ghost Data Still Exists**  
Component: **Runtime Resource and Token Usage Report**

---

## 1. Execution Summary

The final full-dataset run of the deletion-audit solution was executed using the primary entry point:

```bash
python code/main.py --input dataset/deletion_requests.csv --output output.csv
```

The system evaluated all 518 requests in `dataset/deletion_requests.csv` and produced root-level `output.csv`.

---

## 2. Model & Token Usage Summary

As specified by the challenge guidelines, the baseline solution was engineered to be completely deterministic, reproducible, and self-contained using Python's standard library. No external LLM or foundation model APIs were invoked during the prediction run.

| Metric | Measured Value | Notes |
|---|---|---|
| **Model Provider** | None (Deterministic Local Execution) | No external API calls made |
| **Model Name** | N/A | Deterministic rules & evidence graph |
| **Model Call Count** | 0 | 0 remote API calls |
| **Input Tokens** | N/A (0) | No prompt tokens consumed |
| **Output Tokens** | N/A (0) | No completion tokens generated |
| **Total Tokens** | 0 | Standard library implementation |
| **Average Tokens Per Request** | 0 | Local parsing & correlation |
| **Estimated Total Cost (USD)** | **$0.00** | Zero external infrastructure expense |
| **Estimated Cost Per Request (USD)** | **$0.00** | Zero marginal cost per case |

---

## 3. Computational Performance & Runtime Characteristics

The evaluation was performed locally on the challenge evaluation environment:

- **Total Requests Evaluated**: 518 cases
- **Execution Wall Clock Time**: ~2.1 seconds
- **Throughput**: ~245 cases / second
- **Peak Memory Consumption**: < 65 MB RAM
- **Storage Footprint**: Root `output.csv` (492 KB, 492,726 bytes)
- **External Dependencies**: 0 (Pure Python 3 standard library: `csv`, `json`, `sqlite3`, `re`, `zlib`, `base64`, `hashlib`)

---

## 4. Architectural Determinism & Cost Benefits

By designing a deterministic evidence-correlation engine with in-memory SQLite parsing and structured log tracing:
1. **Zero Marginal Inference Cost**: Scales across hundreds of thousands of privacy requests without token consumption or per-call API charges.
2. **Deterministic Reproducibility**: Repeated runs produce identical outputs, eliminating non-deterministic hallucinations in legal compliance auditing.
3. **Strict Data Privacy**: Personal identity snapshots, hashes, and evidence records remain entirely on local infrastructure, preventing PII transmission to third-party model providers.
