from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict
from app.core.database import get_session
from app.models.models import SystemSetting, AuditLog, User
from app.services.analytics_service import get_sensor_analytics

router = APIRouter()

@router.get("/settings/", response_model=List[SystemSetting])
def get_settings(session: Session = Depends(get_session)):
    return session.exec(select(SystemSetting)).all()

@router.patch("/settings/{key}", response_model=SystemSetting)
def update_setting(key: str, value: str, admin_id: int, session: Session = Depends(get_session)):
    setting = session.get(SystemSetting, key)
    if not setting:
        setting = SystemSetting(key=key, value=value)
    else:
        setting.value = value
    
    session.add(setting)
    
    log = AuditLog(
        user_id=admin_id,
        action="UPDATE_SETTING",
        target=key,
        details=f"Value changed to {value}"
    )
    session.add(log)
    
    session.commit()
    session.refresh(setting)
    return setting

@router.get("/audit-logs/", response_model=List[AuditLog])
def get_audit_logs(limit: int = 100, session: Session = Depends(get_session)):
    return session.exec(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)).all()

@router.get("/analytics/sensors/{sensor_id}")
def get_analytics(sensor_id: int, session: Session = Depends(get_session)):
    return get_sensor_analytics(sensor_id, session)
