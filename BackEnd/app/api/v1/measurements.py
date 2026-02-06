from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List

from app.core.database import get_session
from app.models.models import Measurement

router = APIRouter()

@router.get("/measurements/", response_model=List[Measurement])
def read_measurements(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    measurements = session.exec(select(Measurement).offset(offset).limit(limit).order_by(Measurement.measured_at.desc())).all()
    return measurements
