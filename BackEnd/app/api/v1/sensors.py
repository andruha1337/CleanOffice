from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.core.database import get_session
from app.services.aqi_service import calculate_aqi
from app.models.models import Sensor, Measurement, Alert, AlertSeverity, SystemSetting

router = APIRouter()

@router.post("/sensors/", response_model=Sensor)
def create_sensor(sensor: Sensor, session: Session = Depends(get_session)):
    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    return sensor

@router.get("/sensors/", response_model=List[Sensor])
def read_sensors(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    sensors = session.exec(select(Sensor).offset(offset).limit(limit)).all()
    return sensors

@router.get("/sensors/{sensor_id}", response_model=Sensor)
def read_sensor(sensor_id: int, session: Session = Depends(get_session)):
    sensor = session.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor

@router.post("/sensors/{sensor_id}/measurements", response_model=Measurement)
def create_measurement(sensor_id: int, measurement: Measurement, session: Session = Depends(get_session)):
    sensor = session.get(Sensor, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    measurement.aqi = calculate_aqi(measurement.co2_level, measurement.temperature, measurement.humidity)
    
    measurement.sensor_id = sensor_id 
    session.add(measurement)
    
    co2_limit_setting = session.get(SystemSetting, "CO2_CRITICAL_LIMIT")
    co2_limit = float(co2_limit_setting.value) if co2_limit_setting else 1500.0
    
    co2_warn_setting = session.get(SystemSetting, "CO2_WARNING_LIMIT")
    co2_warn = float(co2_warn_setting.value) if co2_warn_setting else 1000.0
    
    alerts = []
    if measurement.co2_level > co2_limit:
        alert = Alert(measurement_id=0, message=f"CRITICAL: CO2 at {measurement.co2_level} ppm (limit: {co2_limit})", severity=AlertSeverity.CRITICAL)
        alerts.append(alert)
    elif measurement.co2_level > co2_warn:
        alert = Alert(measurement_id=0, message=f"WARNING: CO2 at {measurement.co2_level} ppm (limit: {co2_warn})", severity=AlertSeverity.WARNING)
        alerts.append(alert)
        
    if measurement.aqi > 60: # High AQI score is bad in our model
        alert = Alert(measurement_id=0, message=f"Poor Air Quality Index: {measurement.aqi}", severity=AlertSeverity.WARNING)
        alerts.append(alert)
        
    session.commit()
    session.refresh(measurement)
    
    for alert in alerts:
        alert.measurement_id = measurement.id
        session.add(alert)
    
    if alerts:
        session.commit()

    return measurement
