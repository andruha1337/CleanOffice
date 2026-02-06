from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from typing import List, Optional

from app.core.database import get_session
from app.models.models import Alert, User

router = APIRouter()

@router.get("/alerts/", response_model=List[Alert])
def read_alerts(offset: int = 0, limit: int = 50, session: Session = Depends(get_session)):
    alerts = session.exec(select(Alert).offset(offset).limit(limit).order_by(Alert.created_at.desc())).all()
    return alerts

@router.get("/alerts/{alert_id}", response_model=Alert)
def read_alert(alert_id: int, session: Session = Depends(get_session)):
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/alerts/{alert_id}/resolve", response_model=Alert)
def resolve_alert(alert_id: int, session: Session = Depends(get_session)):
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_resolved = True
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert

@router.patch("/alerts/{alert_id}/assign", response_model=Alert)
def assign_alert(alert_id: int, user_id: int = Body(..., embed=True), session: Session = Depends(get_session)):

    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    alert.assigned_to_id = user.id
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert
