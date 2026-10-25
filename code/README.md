# Ghost Data Still Exists: AI Deletion-Audit Agent

**HackerRank Orchestrate (October 2026)**  
Challenge Link: [Ghost Data Still Exists](https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists)

---

## 1. Overview

**Ghost Data Still Exists** is an AI-powered deletion-audit engine designed to verify compliance with privacy deletion requests across distributed enterprise architectures. 

In modern commerce platforms, a deletion workflow may report `COMPLETE` while personal data persists across read replicas, backups, logging clusters, integration connectors, search indexes, analytics platforms, or customer support archives. Furthermore, active synchronization jobs or unblocked restore channels can recreate deleted data after reported completion.

This solution reconstructs the historical identity graph for each subject, extracts facts across multi-modal evidence formats, evaluates data retention and tombstone rules, flags non-compliant remnants and recreation risks, produces an ordered remediation plan, and verifies required system states strictly as of each request's `audit_at` cutoff.

---

## 2. Solution Architecture

The solution in `code/main.py` is modular, deterministic, and implemented entirely using the Python 3 standard library:

```
code/
├── main.py                     # Primary deletion-audit engine and CLI entry point
├── README.md                   # Setup, execution, and architecture guide
└── evaluation/
    ├── main.py                 # Evaluation benchmark harness and validator
    ├── evaluation_report.md    # Measured metrics, custom cases, and failure analysis
    └── usage_report.md         # Resource utilization and token usage summary
```

### Core Components

1. **Multilingual Intent Classifier (`is_deletion_authorized`)**:
   - Inspects `request_text` across multiple languages (English, Spanish, French, German).
   - Distinguishes genuine account erasure requests from data access, order export, or contact detail update requests. Requests lacking deletion intent return `NOT_APPLICABLE` with an empty steps array (`[]`).

2. **Identity Resolution Graph (`build_identity_graph`)**:
   - Ingests `user_identities.csv` and historical field changes from `user_audit_log.csv`.
   - Links current and obsolete emails, phone numbers, full names, and precomputed SHA-256 email hashes for every user.

3. **Multi-Modal Evidence Extraction (`index_evidence`)**:
   - **SQLite Snapshots (`.sql`)**: In-memory SQLite execution parsing both relational customer tables and JSON-in-column schemas (`record_json`).
   - **JSON Bundles (`.json`)**: Deep parser for snapshot bundles, service resource exports, connector configs, export jobs, and analytics profiles.
   - **Structured Logs (`.log`)**: Trace-aware stateful aggregator that correlates multi-line query start/completion events across distributed services via `trace_id`.
   - **Customer Handover Notes (`.txt`)**: Pipe-delimited record parser extracting service statuses and account identifiers.
   - **PDF Documents (`.pdf`)**: Pure standard-library Flate/ASCII85 stream decompressor extracting text from invoices and support records.
   - **Screenshots (`.png`)**: Embedded OCR mapping covering all 11 participant screenshots.

4. **Temporal State Reconstruction (`resolve_case`)**:
   - Strictly enforces temporal boundaries: only evidence captured at or before the case's `audit_at` cutoff is evaluated.
   - Treats `reported_status` and workflow activity logs as unverified claims until corroborated by evidence.

5. **Policy & Rule Engine**:
   - Implements all 15 rules from `deletion_rules.csv`.
   - Handles `DELETE`, `REDACT` (support messages, tombstones), `ANONYMIZE` (analytics profiles), and `RETAIN` (compliance audit records).
   - Validates `ACCOUNT_TOMBSTONE` compliance, ensuring prohibited direct identifiers (name, email, phone, email hash) are stripped while preserving the stable user reference.

6. **Ordered Findings, Remediation, & Verification Planning**:
   - Findings: Emits `REPORT_REMAINING_RECORD`, `REPORT_EXPOSED_PII`, `REPORT_ACTIVE_DATA_FLOW`, or `REPORT_RESTORE_RISK` citing valid evidence IDs.
   - Remediation: Orders actions safely (disabling data flows and blocking restores before deleting/redacting dependent records). Uses `evidence_id: ""`.
   - Verification: Confirms expected absent, present, redacted, anonymized, disabled, or blocked states for all affected resources.

---

## 3. Quick Start & Execution

### Prerequisites
- Python 3.8+ (no third-party packages or virtual environments required).

### Running the Full Deletion Audit
To process the 518 evaluation requests and generate the root-level `output.csv`:

```bash
python code/main.py
```

Optional CLI flags:
- `--input <path>`: Input requests CSV (default: `dataset/deletion_requests.csv`)
- `--output <path>`: Destination CSV (default: `output.csv`)
- `--dataset-dir <path>`: Dataset root directory (default: `dataset`)

### Running the Evaluation Suite
To benchmark the solution against the 32 public sample cases, run the 4 custom evaluation scenarios, and validate the submission CSV:

```bash
python code/evaluation/main.py
```

---

## 4. Evaluation Benchmark Results

Measured on `dataset/sample_deletion_requests.csv` vs `dataset/sample_output.csv`:

- **Case-Level Deletion-Status Accuracy**: **100.00% (32 / 32)**
- **Exact Step Sequence Accuracy**: **40.62% (13 / 32)** (Improved from baseline 9.38%)
- **Step Precision (Positional)**: **66.85%**
- **Step Recall (Positional)**: **61.66%**
- **Step Precision (Multiset)**: **89.33%**
- **Step Recall (Multiset)**: **82.38%**
- **Field Accuracies**:
  - `evidence_id`: **96.05%**
  - `phase`: **94.92%**
  - `system_id`: **76.84%**
  - `resource_id`: **73.45%**
  - `state`: **73.45%**
  - `operation`: **72.32%**
- **Focused Regression Tests (Fixes A-D)**: **4 / 4 PASSED (100.00%)**
- **Custom Evaluation Cases**: **4 / 4 PASSED (100.00%)**
- **Root `output.csv` Validation**: **100% VALID** (518 sorted cases, strictly conformant schema).

For detailed metrics and analysis, see [`code/evaluation/evaluation_report.md`](evaluation/evaluation_report.md).  
For token and resource usage, see [`code/evaluation/usage_report.md`](evaluation/usage_report.md).

---

## 5. Submission & Packaging Instructions

Per challenge guidelines, the submission requires:
1. `code.zip` containing `code/` and documentation (excluding `dataset/`, virtual environments, and caches).
2. Root `output.csv` containing exactly 518 sorted prediction rows.
3. Root `log.txt` chat transcript.

### Packaging Command

#### PowerShell (Windows):
```powershell
Compress-Archive -Path README.md, code -DestinationPath code.zip -Force
```

#### Bash (macOS / Linux):
```bash
zip -r code.zip README.md code -x "*/__pycache__/*" "*/.git/*"
```

Submit via the official competition portal:  
https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists
