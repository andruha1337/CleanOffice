from sqlmodel import Session, select, func
from typing import Dict, Any
from app.models.models import Measurement
from datetime import datetime, timedelta

def get_sensor_analytics(sensor_id: int, session: Session) -> Dict[str, Any]:

    since = datetime.utcnow() - timedelta(hours=24)
    
    statement = select(
        func.avg(Measurement.temperature).label("avg_temp"),
        func.avg(Measurement.humidity).label("avg_hum"),
        func.avg(Measurement.co2_level).label("avg_co2"),
        func.avg(Measurement.aqi).label("avg_aqi"),
        func.count(Measurement.id).label("count")
    ).where(Measurement.sensor_id == sensor_id, Measurement.measured_at >= since)
    
    results = session.exec(statement).first()
    
    if not results or results.count == 0:
        return {"message": "No data for selected period"}
        
    return {
        "sensor_id": sensor_id,
        "period": "last_24h",
        "measurements_count": results.count,
        "averages": {
            "temperature": round(results.avg_temp, 2),
            "humidity": round(results.avg_hum, 2),
            "co2": round(results.avg_co2, 2),
            "aqi": round(results.avg_aqi, 2) if results.avg_aqi else None
        }
    }
