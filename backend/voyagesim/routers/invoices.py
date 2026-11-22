"""Invoices router with IDOR vulnerability."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Invoice, User
from ..schemas import InvoiceOut
from ..auth import get_current_user
from ..vulnerabilities import VulnFlags

router = APIRouter(prefix="/api/v1/invoices", tags=["invoices"])
vulns = VulnFlags()


@router.get("/{id}", response_model=InvoiceOut)
def get_invoice(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve invoice details by ID.
    VULNERABILITY: idor_invoice.
    When enabled, invoices for other agencies can be read without authorization.
    When fixed, returns 404 if invoice does not belong to the user's agency.
    """
    invoice = db.query(Invoice).filter(Invoice.id == id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if not vulns.is_enabled("idor_invoice"):
        if invoice.agency_id != user.agency_id:
            raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice
