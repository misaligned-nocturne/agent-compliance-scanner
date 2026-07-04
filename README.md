# Agent Compliance Scanner

**EU AI Act & AB 316 Readiness Check for AI Agents**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

A lightweight CLI tool that scans your AI agent or MCP server for compliance gaps against:

- **EU AI Act** (effective August 2, 2026) — Articles 8–15 (High-Risk Requirements) + Article 50 (Transparency)
- **California AB 316** (effective January 1, 2026) — Audit trail readiness

> ⚠️ This tool provides a compliance **gap analysis**, NOT legal advice. Consult qualified legal counsel.

## Why This Exists

In one month (August 2, 2026), the EU AI Act enters full enforcement. Organizations deploying AI agents in the EU must comply with risk management, transparency, documentation, and human oversight requirements. California's AB 316 already removes the "the AI did it autonomously" defense — requiring audit trails.

Most agent developers haven't mapped their compliance exposure. This scanner gives you a first-pass gap analysis in under 60 seconds.

## Quick Start

```bash
# Interactive mode (questionnaire)
python scanner.py --interactive

# Scan a manifest file
python scanner.py --manifest example-manifest.json

# Output as Markdown report
python scanner.py --manifest example-manifest.json --format markdown -o report.md
```

## What It Checks

| # | Check | Regulation |
|---|-------|-----------|
| 1 | High-risk domain classification | EU AI Act Annex III |
| 2 | Risk management system | EU AI Act Article 9 |
| 3 | Data governance practices | EU AI Act Article 10 |
| 4 | Technical documentation (Annex IV) | EU AI Act Article 11 |
| 5 | Automatic record-keeping / logs | EU AI Act Article 12 |
| 6 | Transparency to deployers | EU AI Act Article 13 |
| 7 | Human oversight measures | EU AI Act Article 14 |
| 8 | Accuracy, robustness, cybersecurity | EU AI Act Article 15 |
| 9 | AI transparency labeling | EU AI Act Article 50 |
| 10 | Audit trail (AB 316 readiness) | California AB 316 |

## Example Output

```
# Agent Compliance Scan Report

## Summary
| Status | Count | Percentage |
|--------|-------|------------|
| ✅ PASS | 2 | 20% |
| ❌ MISSING | 6 | 60% |
| ⬜ NOT APPLICABLE | 2 | 20% |
| ❓ NEEDS REVIEW | 0 | 0% |

## ❌ Missing Requirements
### risk_management_system
- Regulation: EU AI Act | Article 9
- Guidance: High-risk AI systems must have a continuous, iterative risk management process...
```

## Manifest Format

Create a JSON manifest describing your agent and its current compliance posture:

```json
{
  "agent": {
    "name": "my-agent",
    "description": "What your agent does",
    "capabilities": ["text_generation"],
    "deployment": "cloud",
    "interacts_with_humans": true,
    "generates_content": true
  },
  "compliance": {
    "high_risk_classification": "na",
    "risk_management_system": false,
    "data_governance": false,
    "...": "..."
  }
}
```

Each `compliance` field accepts: `true` (documented), `false` (missing), `"na"` (not applicable).

## License

MIT — see [LICENSE](LICENSE)

---

*Built by [Nocturne](https://github.com/misaligned-nocturne). Part of the Misaligned Codex research on AI agent sovereignty and the emerging agent economy.*
