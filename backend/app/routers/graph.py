"""Live Security Graph topology router generating React Flow nodes and edges."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.models import Api, Finding

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/topology")
def get_graph_topology(view: str = Query("architecture"), db: Session = Depends(get_db)):
    """
    Generate graph topology for React Flow.
    Supports 'architecture' and 'attack_path' views.
    """
    apis = db.query(Api).all()
    findings = db.query(Finding).all()

    nodes = [
        {"id": "app", "type": "input", "data": {"label": "Sentinel Travel Portal", "category": "Application"}, "position": {"x": 380, "y": 40}, "className": "graph-node-app"},
        {"id": "db", "type": "output", "data": {"label": "VoyageSim Database", "category": "Database"}, "position": {"x": 750, "y": 280}, "className": "graph-node-db"},
        {"id": "agency_a", "data": {"label": "Agency A (TravelCorp)", "category": "Agency"}, "position": {"x": 50, "y": 140}, "className": "graph-node-agency"},
        {"id": "agency_b", "data": {"label": "Agency B (GlobalTrips)", "category": "Agency"}, "position": {"x": 50, "y": 280}, "className": "graph-node-agency"},
        {"id": "workflow_booking", "data": {"label": "Booking Workflow", "category": "Workflow"}, "position": {"x": 400, "y": 420}, "className": "graph-node-workflow"},
    ]

    edges = [
        {"id": "e_agency_wf", "source": "agency_a", "target": "workflow_booking", "label": "executes", "animated": True},
        {"id": "e_wf_db", "source": "workflow_booking", "target": "db", "label": "persists"},
    ]

    # Add API nodes
    for i, api in enumerate(apis[:12]):
        node_id = f"api_{api.id}"
        x = 220 + (i % 3) * 220
        y = 120 + (i // 3) * 110
        is_risky = api.risk >= 70 or api.category in ("Zombie", "Shadow")
        nodes.append({
            "id": node_id,
            "data": {
                "label": f"{api.method} {api.endpoint}",
                "method": api.method,
                "endpoint": api.endpoint,
                "category": api.category,
                "risk": api.risk,
                "auth": api.auth_required
            },
            "position": {"x": x, "y": y},
            "className": f"graph-node-api {'graph-risk' if is_risky else ''}"
        })
        # Link from app to api
        edges.append({
            "id": f"e_app_{node_id}",
            "source": "app",
            "target": node_id,
            "animated": is_risky
        })
        # Link from api to db
        edges.append({
            "id": f"e_db_{node_id}",
            "source": node_id,
            "target": "db"
        })

    # Add Finding / Vulnerability nodes
    for j, f in enumerate(findings[:5]):
        f_id = f"finding_{f.id}"
        nodes.append({
            "id": f_id,
            "data": {
                "label": f"[{f.severity}] {f.title}",
                "code": f.code,
                "severity": f.severity,
                "status": f.status,
                "impact": f.impact
            },
            "position": {"x": 680, "y": 80 + j * 90},
            "className": f"graph-node-vuln vuln-{f.severity.lower()}"
        })
        # If finding has affected endpoint, link to that API node
        matching_api = next((a for a in apis if a.endpoint in (f.endpoint or "")), None)
        if matching_api:
            edges.append({
                "id": f"e_vuln_{f.id}",
                "source": f"api_{matching_api.id}",
                "target": f_id,
                "label": "affects",
                "style": {"stroke": "#ef4444", "strokeWidth": 2},
                "animated": True
            })

    # If attack_path view, add attack path chain link
    if view == "attack_path":
        edges.append({
            "id": "e_attack_chain_1",
            "source": "agency_a",
            "target": "agency_b",
            "label": "IDOR Pivot",
            "style": {"stroke": "#dc2626", "strokeWidth": 3},
            "animated": True
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "view": view,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }
