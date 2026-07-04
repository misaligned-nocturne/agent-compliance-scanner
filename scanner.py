#!/usr/bin/env python3
"""
Agent Compliance Scanner - EU AI Act & AB 316 Readiness Check
=============================================================
MVP v0.1.0 - Scans an AI agent or MCP server manifest for compliance gaps
against EU AI Act (effective Aug 2, 2026) and California AB 316.

Usage:
    python scanner.py --manifest agent.json
    python scanner.py --manifest agent.json --format markdown
    python scanner.py --interactive

Output: JSON or Markdown compliance gap report.
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path

# ─── Check Definitions ───────────────────────────────────────────

CHECKS = [
    {
        "id": "high_risk_classification",
        "regulation": "EU AI Act Annex III",
        "article": "Annex III",
        "question": "Does the agent operate in a high-risk domain?",
        "domains": [
            "biometric identification/categorization",
            "critical infrastructure management",
            "education/vocational training",
            "employment/worker management",
            "essential public/private services",
            "law enforcement",
            "migration/asylum/border control",
            "administration of justice/democratic processes",
        ],
        "guidance": "If your agent touches ANY of these domains, it is likely classified as high-risk under the EU AI Act and must comply with Articles 8-15."
    },
    {
        "id": "risk_management_system",
        "regulation": "EU AI Act",
        "article": "Article 9",
        "question": "Is there a documented risk management system?",
        "required": [
            "Risk identification and analysis process",
            "Risk estimation and evaluation methodology",
            "Risk mitigation measures",
            "Residual risk acceptance criteria",
        ],
        "guidance": "High-risk AI systems must have a continuous, iterative risk management process throughout the system lifecycle."
    },
    {
        "id": "data_governance",
        "regulation": "EU AI Act",
        "article": "Article 10",
        "question": "Are data governance practices documented?",
        "required": [
            "Training data provenance and characteristics",
            "Data collection methodology",
            "Data preparation/cleaning procedures",
            "Bias examination and mitigation measures",
            "Data relevance and representativeness assessment",
        ],
        "guidance": "Training, validation and testing datasets must be relevant, representative, and subject to appropriate data governance."
    },
    {
        "id": "technical_documentation",
        "regulation": "EU AI Act",
        "article": "Article 11 + Annex IV",
        "question": "Is technical documentation complete per Annex IV?",
        "required": [
            "System architecture and design specifications",
            "Development methodology",
            "Validation and testing procedures + test logs",
            "Performance metrics (accuracy, robustness, bias)",
            "Intended purpose and foreseeable misuse",
        ],
        "guidance": "Annex IV specifies detailed technical documentation requirements. Test logs must be dated and signed."
    },
    {
        "id": "record_keeping",
        "regulation": "EU AI Act",
        "article": "Article 12",
        "question": "Does the agent maintain automatic logs?",
        "required": [
            "Event logging during operation",
            "Traceability of decisions/actions",
            "Log retention period defined",
            "Log integrity/immutability safeguards",
        ],
        "guidance": "High-risk AI systems must automatically record events (logs) over their lifetime. Logs must enable traceability and post-market monitoring."
    },
    {
        "id": "transparency_to_deployers",
        "regulation": "EU AI Act",
        "article": "Article 13",
        "question": "Is transparency information provided to deployers?",
        "required": [
            "Intended purpose and capabilities description",
            "Known limitations and failure modes",
            "Performance characteristics (accuracy levels per group)",
            "Human oversight measures",
            "Input data specifications",
        ],
        "guidance": "Deployers must receive clear, complete information about the system's capabilities, limitations, and expected performance."
    },
    {
        "id": "human_oversight",
        "regulation": "EU AI Act",
        "article": "Article 14",
        "question": "Are human oversight measures implemented?",
        "required": [
            "Human-in-the-loop or human-on-the-loop design",
            "Override/intervention capabilities",
            "Human operator training/competence documentation",
            "Situation awareness tools for operators",
        ],
        "guidance": "High-risk AI systems must be designed to allow effective human oversight to prevent or minimize risks."
    },
    {
        "id": "accuracy_robustness_cybersecurity",
        "regulation": "EU AI Act",
        "article": "Article 15",
        "question": "Have accuracy, robustness, and cybersecurity been tested?",
        "required": [
            "Accuracy metrics with relevant benchmarks",
            "Robustness against errors/faults/adversarial inputs",
            "Cybersecurity measures and penetration testing",
            "Fallback plans and safe-state behavior",
        ],
        "guidance": "Systems must achieve appropriate levels of accuracy, robustness, and cybersecurity throughout their lifecycle."
    },
    {
        "id": "ai_transparency_labeling",
        "regulation": "EU AI Act",
        "article": "Article 50",
        "question": "Does the agent meet transparency obligations?",
        "required": [
            "Humans informed they are interacting with AI (chatbot/interactive agent)",
            "AI-generated output marked in machine-readable format",
            "Emotion recognition or biometric categorization disclosed",
            "Deep fake / synthetic content clearly labeled",
        ],
        "guidance": "Applies regardless of risk classification. Any AI system interacting with humans must disclose its AI nature."
    },
    {
        "id": "ab316_audit_trail",
        "regulation": "California AB 316",
        "article": "Civil Code 1714.46",
        "question": "Is there an audit trail for AB 316 readiness?",
        "required": [
            "Records of agent configuration and intended scope",
            "Logs of agent actions and decisions",
            "Evidence of testing and validation before deployment",
            "Human oversight records for high-stakes decisions",
            "Post-deployment monitoring and incident tracking",
        ],
        "guidance": "AB 316 removes the 'AI did it autonomously' defense. Organizations must maintain verifiable records of what the agent was configured to do vs what it actually did."
    },
]


def run_scan(manifest: dict | None, interactive: bool = False) -> dict:
    """Run all compliance checks and return results."""
    results = {
        "scan_metadata": {
            "tool": "agent-compliance-scanner",
            "version": "0.1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "regulations_covered": ["EU AI Act (effective 2026-08-02)", "California AB 316 (effective 2026-01-01)"],
            "disclaimer": "This tool provides a compliance gap analysis, NOT legal advice. Consult qualified legal counsel for regulatory compliance.",
        },
        "summary": {"total_checks": len(CHECKS), "passed": 0, "missing": 0, "not_applicable": 0, "needs_review": 0},
        "checks": [],
    }

    if interactive:
        print("\n╔══════════════════════════════════════════════╗")
        print("║   Agent Compliance Scanner v0.1.0           ║")
        print("║   EU AI Act + AB 316 Readiness Check        ║")
        print("╚══════════════════════════════════════════════╝")
        print("\nAnswer each question with: y (yes/documented), n (no/missing), na (not applicable), ? (unsure)\n")

    for check in CHECKS:
        if interactive:
            print(f"\n── {check['id']} ──")
            print(f"   Regulation: {check['regulation']} | {check['article']}")
            print(f"   {check['question']}")
            if "domains" in check:
                print("   High-risk domains:")
                for d in check["domains"]:
                    print(f"     - {d}")
            else:
                print("   Required elements:")
                for r in check.get("required", []):
                    print(f"     - {r}")
            answer = input("\n   Status? [y/n/na/?]: ").strip().lower()
        else:
            # Non-interactive: check if manifest provides evidence
            answer = _check_manifest(manifest, check) if manifest else "?"

        status = _parse_answer(answer)
        results["checks"].append({
            "id": check["id"],
            "regulation": check["regulation"],
            "article": check["article"],
            "question": check["question"],
            "status": status["label"],
            "guidance": check["guidance"],
        })
        results["summary"][status["key"]] += 1

    return results


def _parse_answer(answer: str) -> dict:
    mapping = {
        "y": {"label": "PASS", "key": "passed"},
        "yes": {"label": "PASS", "key": "passed"},
        "n": {"label": "MISSING", "key": "missing"},
        "no": {"label": "MISSING", "key": "missing"},
        "na": {"label": "NOT_APPLICABLE", "key": "not_applicable"},
        "?": {"label": "NEEDS_REVIEW", "key": "needs_review"},
    }
    return mapping.get(answer, {"label": "NEEDS_REVIEW", "key": "needs_review"})


def _check_manifest(manifest: dict, check: dict) -> str:
    """Auto-check if manifest provides evidence for this requirement."""
    if not manifest:
        return "?"
    evidence_fields = manifest.get("compliance", {}).get(check["id"], None)
    if evidence_fields is True:
        return "y"
    if evidence_fields is False:
        return "n"
    if evidence_fields == "na":
        return "na"
    if isinstance(evidence_fields, (list, dict)) and len(evidence_fields) > 0:
        return "y"
    return "?"


def format_report(results: dict, fmt: str = "json") -> str:
    """Format scan results as JSON or Markdown."""
    if fmt == "json":
        return json.dumps(results, indent=2, ensure_ascii=False)

    # Markdown format
    md = []
    md.append("# Agent Compliance Scan Report")
    md.append("")
    md.append(f"**Scan Date**: {results['scan_metadata']['timestamp']}")
    md.append(f"**Regulations**: {', '.join(results['scan_metadata']['regulations_covered'])}")
    md.append("")
    md.append("> ⚠️ This is a compliance gap analysis, NOT legal advice.")
    md.append("")
    md.append("## Summary")
    md.append("")
    s = results["summary"]
    total = s["total_checks"]
    md.append(f"| Status | Count | Percentage |")
    md.append(f"|--------|-------|------------|")
    md.append(f"| ✅ PASS | {s['passed']} | {s['passed']/total*100:.0f}% |")
    md.append(f"| ❌ MISSING | {s['missing']} | {s['missing']/total*100:.0f}% |")
    md.append(f"| ⬜ NOT APPLICABLE | {s['not_applicable']} | {s['not_applicable']/total*100:.0f}% |")
    md.append(f"| ❓ NEEDS REVIEW | {s['needs_review']} | {s['needs_review']/total*100:.0f}% |")

    if s["missing"] > 0:
        md.append("")
        md.append("## ❌ Missing Requirements")
        md.append("")
        for c in results["checks"]:
            if c["status"] == "MISSING":
                md.append(f"### {c['id']}")
                md.append(f"- **Regulation**: {c['regulation']} | {c['article']}")
                md.append(f"- **Question**: {c['question']}")
                md.append(f"- **Guidance**: {c['guidance']}")
                md.append("")

    if s["needs_review"] > 0:
        md.append("## ❓ Needs Review")
        md.append("")
        for c in results["checks"]:
            if c["status"] == "NEEDS_REVIEW":
                md.append(f"- **{c['id']}**: {c['question']}")
        md.append("")

    md.append("## All Checks")
    md.append("")
    for c in results["checks"]:
        emoji = {"PASS": "✅", "MISSING": "❌", "NOT_APPLICABLE": "⬜", "NEEDS_REVIEW": "❓"}.get(c["status"], "❓")
        md.append(f"- {emoji} **{c['id']}** ({c['regulation']} {c['article']}): {c['question']}")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(
        description="Agent Compliance Scanner - EU AI Act & AB 316 Readiness Check"
    )
    parser.add_argument("--manifest", type=Path, help="Path to agent manifest JSON file")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive questionnaire mode")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="json", help="Output format")
    parser.add_argument("--output", "-o", type=Path, help="Output file path (default: stdout)")

    args = parser.parse_args()

    if not args.manifest and not args.interactive:
        parser.error("Either --manifest or --interactive is required")

    manifest = None
    if args.manifest:
        try:
            manifest = json.loads(args.manifest.read_text())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading manifest: {e}", file=sys.stderr)
            sys.exit(1)

    results = run_scan(manifest, interactive=args.interactive)
    output = format_report(results, args.format)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
