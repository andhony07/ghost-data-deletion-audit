\# Ghost Data Deletion Audit



An evidence-driven Python solution for auditing whether personal-data deletion requests have actually been completed.



\## Overview



A deletion workflow can report success while copies of personal data remain in databases, replicas, logs, support attachments, exports, search indexes, archives, or backups. Synchronization and restoration processes may also recreate deleted records.



This project was developed for the \*\*HackerRank Orchestrate — October 2026: Ghost Data Still Exists\*\* challenge.



The solution analyzes available audit evidence, evaluates deletion status, identifies remaining-data and recreation risks, and produces ordered remediation and verification steps.



\## Key Features



\- \*\*Deletion-status assessment:\*\* Classifies requests as `COMPLETE`, `INCOMPLETE`, or `NOT\_APPLICABLE`.

\- \*\*Evidence-based auditing:\*\* Uses available activity records, identity history, and supporting evidence.

\- \*\*Identity resolution:\*\* Considers current and historical identity mappings.

\- \*\*Remediation planning:\*\* Produces ordered findings, corrective actions, and verification steps.

\- \*\*Structured output:\*\* Generates CSV predictions with JSON-encoded steps.

\- \*\*Evaluation tooling:\*\* Includes an evaluation script and reports documenting measured results, custom test cases, and improvements.



\## Technology



\- Python

\- CSV and JSON data processing

\- Rule-based evidence analysis

\- Automated evaluation and testing



\## Repository Structure



```text

ghost-data-deletion-audit/

├── README.md

└── code/

&#x20;   ├── main.py

&#x20;   ├── README.md

&#x20;   └── evaluation/

&#x20;       ├── main.py

&#x20;       ├── evaluation\_report.md

&#x20;       └── usage\_report.md

```



\## How It Works



1\. Read deletion requests and the available evidence.

2\. Determine whether each request actually requires deletion.

3\. Resolve the relevant identity and resources.

4\. Assess the state of the evidence at the audit timestamp.

5\. Identify remaining data and potential recreation risks.

6\. Generate the deletion status and ordered remediation or verification steps.

7\. Evaluate predictions against the available reference answers.



\## Running the Project



The original challenge expects its input files under a `dataset/` directory and writes `output.csv` to the repository root.



This portfolio repository intentionally excludes the challenge datasets and evidence files. Therefore, execution requires access to the authorized input files and any dependencies documented in `code/README.md`.



From a compatible project environment, the original entry point is:



```bash

python code/main.py

```



Check `code/README.md` for implementation-specific setup details before running it.



\## Evaluation



The submitted challenge result was \*\*46.6/100\*\* on the HackerRank leaderboard.



The local evaluation reported:



\- Deletion-status accuracy: \*\*32/32 (100%)\*\* on the supplied 32-case sample.

\- Exact step-sequence accuracy: \*\*13/32 (40.62%)\*\* on that sample.

\- Positional step precision: \*\*66.85%\*\*.

\- Positional step recall: \*\*61.66%\*\*.



These sample metrics do not represent overall hidden-test performance. The leaderboard score reflects the broader challenge evaluation.



See `code/evaluation/evaluation\_report.md` and `code/evaluation/usage\_report.md` for further details.



\## Limitations



\- Results depend on the completeness and reliability of the available evidence.

\- A reported deletion status alone is not proof that data has been removed.

\- The solution's output is an audit assessment, not a guarantee that every copy of personal data has been deleted.

\- Production deployment would require additional security controls, authorization checks, and integration-specific verification.



\## Responsible Data Handling



Challenge datasets, evidence files, credentials, private transcripts, and agent traces are not included in this portfolio repository. Use only data you are authorized to process.



\## Context



Built as a programming and evidence-analysis challenge project for HackerRank Orchestrate, October 2026.



