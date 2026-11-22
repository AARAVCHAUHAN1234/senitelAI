"""Security assessment reports router."""

from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.models import Api, Finding, Agent

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("")
def generate_report(db: Session = Depends(get_db)):
    """Generate structured JSON security assessment report."""
    apis = db.query(Api).all()
    findings = db.query(Finding).all()

    crit = sum(1 for f in findings if f.severity == "Critical")
    high = sum(1 for f in findings if f.severity == "High")
    verified = sum(1 for f in findings if f.status == "Verified")

    return {
        "title": "SentinelAI DAST Security Assessment Report",
        "generated_at": datetime.utcnow().isoformat(),
        "mode": "DEMO / SIMULATED",
        "target_platform": "VoyageSim Multi-Tenant B2B Travel Platform",
        "executive_summary": (
            f"Autonomous DAST assessment discovered {len(apis)} endpoints across active, zombie, and shadow categories. "
            f"A total of {len(findings)} security findings were detected, of which {verified} have been independently "
            f"reproduced and verified in the safe sandbox environment."
        ),
        "metrics": {
            "total_apis": len(apis),
            "vulnerabilities": len(findings),
            "critical": crit,
            "high": high,
            "verified": verified,
            "risk_score": min(100, 25 + crit * 15 + high * 8)
        },
        "findings": [
            {
                "id": f.id,
                "code": f.code,
                "title": f.title,
                "severity": f.severity,
                "endpoint": f.endpoint,
                "tenant": f.tenant,
                "agent": f.agent_name,
                "status": f.status,
                "impact": f.impact,
                "evidence": f.evidence,
                "remediation": f.remediation,
                "demo_label": f.demo_label
            }
            for f in findings
        ]
    }


@router.get("/pdf", response_class=HTMLResponse)
def generate_printable_report(db: Session = Depends(get_db)):
    """Generate printable HTML report for export."""
    data = generate_report(db)
    rows_html = "".join([
        f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 10px; font-weight: bold;">{f['code']}</td>
            <td style="padding: 10px;">{f['title']}</td>
            <td style="padding: 10px; color: {'#ef4444' if f['severity']=='Critical' else '#f97316'}; font-weight: bold;">{f['severity']}</td>
            <td style="padding: 10px; font-family: monospace;">{f['endpoint']}</td>
            <td style="padding: 10px;">{f['status']}</td>
        </tr>
        """
        for f in data["findings"]
    ])

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SentinelAI Security Assessment Report</title>
        <style>
            body {{ font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }}
            .card {{ background: #1e293b; border-radius: 8px; padding: 24px; margin-bottom: 24px; border: 1px solid #334155; }}
            h1, h2, h3 {{ margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
            th {{ text-align: left; padding: 10px; border-bottom: 2px solid #475569; color: #94a3b8; font-size: 12px; }}
            .pill {{ display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 12px; background: #3b82f6; color: white; }}
        </style>
    </head>
    <body>
        <div class="card">
            <span class="pill">DEMO / SIMULATED</span>
            <h1>SentinelAI Security Assessment Report</h1>
            <p style="color: #94a3b8;">Generated: {data['generated_at']} | Target: {data['target_platform']}</p>
            <p>{data['executive_summary']}</p>
            <div style="display: flex; gap: 20px; margin-top: 20px;">
                <div style="background: #0f172a; padding: 16px; border-radius: 6px;"><b>Discovered APIs:</b> {data['metrics']['total_apis']}</div>
                <div style="background: #0f172a; padding: 16px; border-radius: 6px;"><b>Total Findings:</b> {data['metrics']['vulnerabilities']}</div>
                <div style="background: #0f172a; padding: 16px; border-radius: 6px; color: #ef4444;"><b>Critical Findings:</b> {data['metrics']['critical']}</div>
                <div style="background: #0f172a; padding: 16px; border-radius: 6px; color: #10b981;"><b>Verified Findings:</b> {data['metrics']['verified']}</div>
            </div>
        </div>

        <div class="card">
            <h2>Detailed Vulnerability Findings</h2>
            <table>
                <thead>
                    <tr>
                        <th>CODE</th>
                        <th>TITLE</th>
                        <th>SEVERITY</th>
                        <th>AFFECTED ENDPOINT</th>
                        <th>STATUS</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
