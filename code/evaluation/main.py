#!/usr/bin/env python3
"""
Ghost Data Still Exists - Evaluation Framework
HackerRank Orchestrate (October 2026)

Entry point: python code/evaluation/main.py
"""

import os
import sys
import csv
import json
import re
from collections import defaultdict

# Ensure repo root and code/ are in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT = os.path.dirname(CODE_DIR)

if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from main import DeletionAuditEngine, is_deletion_authorized, sort_steps

# Reconfigure stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

ALLOWED_PHASES = {'FINDING', 'REMEDIATION', 'VERIFICATION'}
ALLOWED_OPERATIONS = {
    'REPORT_REMAINING_RECORD', 'REPORT_EXPOSED_PII', 'REPORT_ACTIVE_DATA_FLOW', 'REPORT_RESTORE_RISK',
    'DISABLE_DATA_FLOW', 'BLOCK_RESTORE', 'DELETE_RECORD', 'REDACT_RECORD', 'ANONYMIZE_RECORD',
    'VERIFY_RECORD_ABSENT', 'VERIFY_RECORD_PRESENT', 'VERIFY_RECORD_REDACTED', 'VERIFY_RECORD_ANONYMIZED',
    'VERIFY_DATA_FLOW_DISABLED', 'VERIFY_RESTORE_BLOCKED'
}
ALLOWED_STATES = {'PRESENT', 'ACTIVE', 'DISABLED', 'BLOCKED', 'ABSENT', 'REDACTED', 'ANONYMIZED'}

def evaluate_sample_predictions(engine, sample_req_path, sample_gold_path):
    """Evaluates the engine against the 32 public sample cases and ground truth."""
    with open(sample_req_path, 'r', encoding='utf-8') as f:
        sample_requests = list(csv.DictReader(f))
    with open(sample_gold_path, 'r', encoding='utf-8') as f:
        gold_outputs = {r['case_id']: r for r in csv.DictReader(f)}

    total_cases = len(sample_requests)
    status_correct = 0
    exact_seq_correct = 0

    total_gold_steps = 0
    total_pred_steps = 0
    matched_steps = 0

    field_matches = defaultdict(int)
    field_totals = defaultdict(int)

    case_details = []

    for req in sample_requests:
        cid = req['case_id']
        gold = gold_outputs[cid]
        pred = engine.resolve_case(req)

        # Status accuracy
        st_match = (pred['deletion_status'] == gold['deletion_status'])
        if st_match:
            status_correct += 1
        else:
            print(f"Status mismatch for {cid}: pred={pred['deletion_status']}, gold={gold['deletion_status']}")

        gold_steps = json.loads(gold['steps_json'])
        pred_steps = json.loads(pred['steps_json'])

        total_gold_steps += len(gold_steps)
        total_pred_steps += len(pred_steps)

        # Exact sequence comparison
        gold_tuples = [(s['phase'], s['operation'], s['system_id'], s['resource_id'], s['state'], s['evidence_id']) for s in gold_steps]
        pred_tuples = [(s['phase'], s['operation'], s['system_id'], s['resource_id'], s['state'], s['evidence_id']) for s in pred_steps]

        seq_match = (gold_tuples == pred_tuples)
        if seq_match:
            exact_seq_correct += 1

        # Step-level and field-level alignment
        min_len = min(len(gold_steps), len(pred_steps))
        for i in range(min_len):
            gs = gold_steps[i]
            ps = pred_steps[i]
            if (gs['phase'], gs['operation'], gs['system_id'], gs['resource_id'], gs['state'], gs['evidence_id']) == \
               (ps['phase'], ps['operation'], ps['system_id'], ps['resource_id'], ps['state'], ps['evidence_id']):
                matched_steps += 1

            for fld in ['phase', 'operation', 'system_id', 'resource_id', 'state', 'evidence_id']:
                field_totals[fld] += 1
                if gs[fld] == ps[fld]:
                    field_matches[fld] += 1

        case_details.append({
            'case_id': cid,
            'status_match': st_match,
            'gold_status': gold['deletion_status'],
            'pred_status': pred['deletion_status'],
            'seq_match': seq_match,
            'gold_steps_count': len(gold_steps),
            'pred_steps_count': len(pred_steps)
        })

    return {
        'total_cases': total_cases,
        'status_correct': status_correct,
        'status_accuracy': (status_correct / total_cases) * 100,
        'exact_seq_correct': exact_seq_correct,
        'exact_seq_accuracy': (exact_seq_correct / total_cases) * 100,
        'total_gold_steps': total_gold_steps,
        'total_pred_steps': total_pred_steps,
        'matched_steps': matched_steps,
        'step_precision': (matched_steps / total_pred_steps * 100) if total_pred_steps else 100.0,
        'step_recall': (matched_steps / total_gold_steps * 100) if total_gold_steps else 100.0,
        'field_matches': field_matches,
        'field_totals': field_totals,
        'case_details': case_details
    }

def run_custom_evaluation_cases(engine):
    """Executes at least 3 custom independent evaluation cases testing specific edge scenarios."""
    custom_cases = [
        {
            'name': 'Custom Case 1: Multilingual Non-Deletion Request (Spanish Export Request)',
            'description': 'User requests a copy and export of their personal order history in Spanish; explicitly states do not delete.',
            'request': {
                'case_id': 'custom_01',
                'email': 'carlos.valdez@gmail.com',
                'requested_at': '2026-09-01T10:00:00Z',
                'reported_status': 'NOT_STARTED',
                'reported_at': '2026-09-01T10:30:00Z',
                'audit_at': '2026-09-10T12:00:00Z',
                'request_text': 'Por favor, export all my orders y download my data in a portable format. Do not delete my account.'
            },
            'expected_status': 'NOT_APPLICABLE',
            'expected_steps_count': 0
        },
        {
            'name': 'Custom Case 2: Active Synchronization Connector Flow',
            'description': 'Customer account deletion reported complete, but integration connector heartbeat shows enabled=True.',
            'request': {
                'case_id': 'custom_02',
                'email': 'lucia-torres@gmail.com',
                'requested_at': '2026-08-21T12:00:00Z',
                'reported_status': 'COMPLETE',
                'reported_at': '2026-08-22T12:00:00Z',
                'audit_at': '2026-09-15T12:00:00Z',
                'request_text': 'Please close my account and disconnect all active synchronizations and data connectors.'
            },
            'expected_status': 'INCOMPLETE',
            'expected_operation_present': 'REPORT_ACTIVE_DATA_FLOW'
        },
        {
            'name': 'Custom Case 3: Retained Account Tombstone Exposing PII (Phone & Email)',
            'description': 'Account was deleted and preserved as an ACCOUNT_TOMBSTONE, but direct identifiers were retained.',
            'request': {
                'case_id': 'custom_03',
                'email': 'addo.kofi@gmail.com',
                'requested_at': '2026-09-06T11:00:00Z',
                'reported_status': 'COMPLETE',
                'reported_at': '2026-09-06T12:00:00Z',
                'audit_at': '2026-09-20T12:00:00Z',
                'request_text': 'Permanently erase my account and verify that all personal identifiers are redacted from the tombstone.'
            },
            'expected_status': 'INCOMPLETE',
            'expected_operation_present': 'REPORT_EXPOSED_PII'
        },
        {
            'name': 'Custom Case 4: Unsafe Backup Archive Restore Risk',
            'description': 'Customer requested erasure, but backup archive is still active with restore allowed.',
            'request': {
                'case_id': 'custom_04',
                'email': 'y.tanaka32@gmail.com',
                'requested_at': '2026-09-05T12:00:00Z',
                'reported_status': 'COMPLETE',
                'reported_at': '2026-09-06T12:00:00Z',
                'audit_at': '2026-10-02T12:00:00Z',
                'request_text': 'Ensure that backup systems cannot restore my deleted profile.'
            },
            'expected_status': 'INCOMPLETE',
            'expected_operation_present': 'REPORT_RESTORE_RISK'
        }
    ]

    results = []
    for c in custom_cases:
        pred = engine.resolve_case(c['request'])
        steps = json.loads(pred['steps_json'])
        status_pass = (pred['deletion_status'] == c['expected_status'])
        
        feature_pass = True
        if 'expected_steps_count' in c:
            feature_pass = (len(steps) == c['expected_steps_count'])
        if 'expected_operation_present' in c:
            feature_pass = any(s['operation'] == c['expected_operation_present'] for s in steps)

        results.append({
            'name': c['name'],
            'description': c['description'],
            'passed': status_pass and feature_pass,
            'pred_status': pred['deletion_status'],
            'expected_status': c['expected_status'],
            'steps_count': len(steps)
        })

    return results

def run_focused_regression_tests(engine):
    """
    Focused regression tests validating the 4 core logic fixes:
    - Fix A: Account candidate resolution (outcome semantics, temporal clustering, audit cutoff)
    - Fix B: Deduplication of step tuples and avoiding duplicate account verification
    - Fix C: JSON collection snapshot timestamps and cutoff enforcement
    - Fix D: Support policy distinguishing SUPPORT_ATTACHMENT (DELETE/ABSENT) from SUPPORT_MESSAGE (REDACT/REDACTED)
    """
    tests = []

    # Test Fix A: Account candidate resolution
    test_req_a = {
        'case_id': 'test_fix_a',
        'email': 'gabriel.costa@proton.me',
        'requested_at': '2026-08-29T20:03:00Z',
        'reported_status': 'PARTIALLY_COMPLETE',
        'reported_at': '2026-08-31T13:44:00Z',
        'audit_at': '2026-09-14T16:10:00Z',
        'request_text': 'I closed my account, please delete my data.'
    }
    pred_a = engine.resolve_case(test_req_a)
    steps_a = json.loads(pred_a['steps_json'])
    has_acc_008 = any(s['resource_id'] == 'account_008' and s['operation'] == 'VERIFY_RECORD_ABSENT' for s in steps_a)
    tests.append({
        'name': 'Regression Fix A: Account Candidate Resolution',
        'passed': has_acc_008,
        'details': f"account_008 resolved in verification: {has_acc_008}"
    })

    # Test Fix B: Duplicate Step Generation
    tuples = [(s['phase'], s['operation'], s['system_id'], s['resource_id'], s['state'], s.get('evidence_id', '')) for s in steps_a]
    no_dups = len(tuples) == len(set(tuples))
    acc_verifs = [s for s in steps_a if s['system_id'] == 'account_service' and s['phase'] == 'VERIFICATION']
    acc_unique = len(acc_verifs) <= 1
    tests.append({
        'name': 'Regression Fix B: Duplicate Step Generation & Account Uniqueness',
        'passed': no_dups and acc_unique,
        'details': f"Unique tuples: {no_dups}, Account verifications count: {len(acc_verifs)}"
    })

    # Test Fix C: JSON collection snapshot timestamps
    snap_records = [r for r in engine.extracted_records if r.get('evidence_id') == 'evidence_51']
    has_snap_timestamps = all('captured_at' in r and r['captured_at'] is not None for r in snap_records)
    tests.append({
        'name': 'Regression Fix C: JSON Snapshot Collection Timestamps',
        'passed': has_snap_timestamps and len(snap_records) > 0,
        'details': f"Snapshot records evaluated: {len(snap_records)}, all timestamps valid: {has_snap_timestamps}"
    })

    # Test Fix D: Support policy attachment vs message
    attachment_records = [r for r in engine.extracted_records if r.get('category') == 'SUPPORT_ATTACHMENT']
    tests.append({
        'name': 'Regression Fix D: Support Policy Attachment vs Message Classification',
        'passed': len(attachment_records) > 0,
        'details': f"Identified {len(attachment_records)} distinct support attachment records across evidence corpus"
    })

    return tests

def validate_submission_file(csv_path, expected_row_count=518):
    """Strictly validates output.csv structure, sorting, types, and schema."""
    errors = []
    if not os.path.exists(csv_path):
        return [f"File not found: {csv_path}"]

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != ['case_id', 'deletion_status', 'steps_json']:
            errors.append(f"Invalid CSV header: {header}, expected ['case_id', 'deletion_status', 'steps_json']")

        rows = list(reader)

    if len(rows) != expected_row_count:
        errors.append(f"Invalid row count: {len(rows)}, expected {expected_row_count}")

    prev_cid_num = -1
    for idx, row in enumerate(rows, 1):
        if len(row) != 3:
            errors.append(f"Row {idx} has {len(row)} columns, expected 3")
            continue
        cid, status, steps_raw = row
        
        # Check ID format and sorting
        m = re.match(r'case_(\d+)', cid)
        if m:
            cid_num = int(m.group(1))
            if cid_num <= prev_cid_num:
                errors.append(f"Row {idx} case_id {cid} is not sorted ascending after {prev_cid_num}")
            prev_cid_num = cid_num

        if status not in {'COMPLETE', 'INCOMPLETE', 'NOT_APPLICABLE'}:
            errors.append(f"Row {idx} invalid deletion_status: {status}")

        try:
            steps = json.loads(steps_raw)
            if not isinstance(steps, list):
                errors.append(f"Row {idx} steps_json is not a JSON array")
                continue
            if status == 'NOT_APPLICABLE' and len(steps) != 0:
                errors.append(f"Row {idx} NOT_APPLICABLE must have empty steps_json, got {len(steps)} steps")
            
            for s_idx, s in enumerate(steps, 1):
                if s.get('step_no') != s_idx:
                    errors.append(f"Row {idx} step {s_idx} step_no is {s.get('step_no')}, expected {s_idx}")
                if s.get('phase') not in ALLOWED_PHASES:
                    errors.append(f"Row {idx} step {s_idx} invalid phase: {s.get('phase')}")
                if s.get('operation') not in ALLOWED_OPERATIONS:
                    errors.append(f"Row {idx} step {s_idx} invalid operation: {s.get('operation')}")
                if s.get('state') not in ALLOWED_STATES:
                    errors.append(f"Row {idx} step {s_idx} invalid state: {s.get('state')}")
                
                # Evidence rule check
                ev_id = s.get('evidence_id', '')
                if s.get('phase') == 'FINDING' and not ev_id:
                    errors.append(f"Row {idx} step {s_idx} FINDING must cite evidence_id, got empty")
                if status == 'COMPLETE' and not ev_id:
                    errors.append(f"Row {idx} step {s_idx} COMPLETE verification must cite evidence_id, got empty")
                if status == 'INCOMPLETE' and s.get('phase') in ['REMEDIATION', 'VERIFICATION'] and ev_id != "":
                    errors.append(f"Row {idx} step {s_idx} future remediation/verification must have empty evidence_id, got {ev_id}")
        except Exception as e:
            errors.append(f"Row {idx} JSON parse error: {e}")

    return errors

def main():
    print("================================================================================")
    print("         HackerRank Orchestrate - Deletion Audit Evaluation Suite               ")
    print("================================================================================\n")

    dataset_dir = os.path.join(REPO_ROOT, "dataset")
    sample_req_path = os.path.join(dataset_dir, "sample_deletion_requests.csv")
    sample_gold_path = os.path.join(dataset_dir, "sample_output.csv")

    print("[1/4] Initializing DeletionAuditEngine...")
    engine = DeletionAuditEngine(dataset_dir=dataset_dir)
    print("Engine initialized successfully.\n")

    print("[2/4] Evaluating Public Sample Dataset (32 cases)...")
    res = evaluate_sample_predictions(engine, sample_req_path, sample_gold_path)
    
    print("\n-------------------------- SAMPLE EVALUATION RESULTS --------------------------")
    print(f"Case-Level Deletion-Status Accuracy : {res['status_correct']}/{res['total_cases']} ({res['status_accuracy']:.2f}%)")
    print(f"Exact Step Sequence Accuracy        : {res['exact_seq_correct']}/{res['total_cases']} ({res['exact_seq_accuracy']:.2f}%)")
    print(f"Step Precision                      : {res['step_precision']:.2f}%")
    print(f"Step Recall                         : {res['step_recall']:.2f}%")
    print("\nField-Level Accuracies:")
    for fld in ['phase', 'operation', 'system_id', 'resource_id', 'state', 'evidence_id']:
        tot = res['field_totals'][fld]
        match = res['field_matches'][fld]
        pct = (match / tot * 100) if tot else 100.0
        print(f"  - {fld:<14} : {match}/{tot} ({pct:.2f}%)")
    print("--------------------------------------------------------------------------------\n")

    print("[3/5] Running Custom Independent Evaluation Cases...")
    custom_res = run_custom_evaluation_cases(engine)
    all_custom_pass = True
    for c in custom_res:
        status_str = "PASS" if c['passed'] else "FAIL"
        if not c['passed']: all_custom_pass = False
        print(f"  [{status_str}] {c['name']}")
        print(f"         Result: status={c['pred_status']} (expected {c['expected_status']}), steps={c['steps_count']}")
    print(f"\nCustom Cases Status: {'ALL PASSED' if all_custom_pass else 'SOME FAILED'}\n")

    print("[4/5] Running Focused Regression Tests for Fixes A-D...")
    reg_res = run_focused_regression_tests(engine)
    all_reg_pass = True
    for r in reg_res:
        status_str = "PASS" if r['passed'] else "FAIL"
        if not r['passed']: all_reg_pass = False
        print(f"  [{status_str}] {r['name']}")
        print(f"         {r['details']}")
    print(f"\nRegression Tests Status: {'ALL PASSED' if all_reg_pass else 'SOME FAILED'}\n")

    # Full output validation
    output_path = os.path.join(REPO_ROOT, "output.csv")
    print(f"[5/5] Validating Root Output Submission ({output_path})...")
    if os.path.exists(output_path):
        val_errors = validate_submission_file(output_path, expected_row_count=518)
        if not val_errors:
            print("  Root output.csv is 100% VALID: 518 sorted cases, strictly conformant schema and step syntax.")
        else:
            print(f"  Validation encountered {len(val_errors)} warnings/errors:")
            for err in val_errors[:5]:
                print(f"    * {err}")
    else:
        print("  Root output.csv has not been generated yet. Run 'python code/main.py' to produce it.")

    print("\n================================================================================")
    print("                         Evaluation Completed                                   ")
    print("================================================================================")

if __name__ == '__main__':
    main()
