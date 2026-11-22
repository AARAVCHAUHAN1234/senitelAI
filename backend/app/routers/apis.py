"""APIs inventory router with search, filter, and OpenAPI export/import."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from datetime import datetime

from ..core.database import get_db
from ..core.models import Api
from ..core.schemas import ApiOut

router = APIRouter(prefix="/api/apis", tags=["apis"])


@router.get("", response_model=List[ApiOut])
def list_apis(
    q: Optional[str] = Query(None),
    category: str = Query("All"),
    sort_by: str = Query("risk"),
    db: Session = Depends(get_db)
):
    """Retrieve cataloged APIs with filtering and risk sorting."""
    query = db.query(Api)
    if q:
        query = query.filter(
            (Api.endpoint.ilike(f"%{q}%")) | (Api.method.ilike(f"%{q}%"))
        )
    if category != "All":
        query = query.filter(Api.category == category)

    if sort_by == "risk":
        query = query.order_by(Api.risk.desc())
    elif sort_by == "frequency":
        query = query.order_by(Api.frequency.desc())
    else:
        query = query.order_by(Api.id.desc())

    return query.all()


@router.get("/openapi")
def export_openapi(db: Session = Depends(get_db)):
    """Export cataloged APIs as OpenAPI 3.1.0 document."""
    apis = db.query(Api).all()
    paths = {}
    for api in apis:
        if api.endpoint not in paths:
            paths[api.endpoint] = {}
        paths[api.endpoint][api.method.lower()] = {
            "summary": f"Observed via {api.source}",
            "description": f"Classification: {api.category}, Risk Score: {api.risk}",
            "security": [{"BearerAuth": []}] if api.auth_required else [],
            "responses": {
                str(api.status_code or 200): {"description": "Observed status"}
            }
        }
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "SentinelAI Discovered API Surface",
            "version": "1.0.0",
            "description": "Exported API catalog including active, zombie, and shadow routes"
        },
        "paths": paths
    }


@router.post("/import-openapi")
def import_openapi(spec: dict = Body(...), db: Session = Depends(get_db)):
    """Import and catalog routes from an uploaded OpenAPI specification."""
    paths = spec.get("paths", {})
    imported = 0
    now = datetime.utcnow()
    for path, methods in paths.items():
        for method, meta in methods.items():
            if method.upper() in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                existing = db.query(Api).filter(Api.endpoint == path, Api.method == method.upper()).first()
                if not existing:
                    new_api = Api(
                        method=method.upper(),
                        endpoint=path,
                        category="New",
                        status_code=200,
                        auth_required=bool(meta.get("security")),
                        owner=meta.get("x-owner", "Imported Spec"),
                        frequency=10,
                        risk=40,
                        source="Uploaded OpenAPI",
                        last_observed=now
                    )
                    db.add(new_api)
                    imported += 1
    db.commit()
    return {"status": "success", "imported_routes": imported}
