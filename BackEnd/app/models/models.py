from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    password_hash: str
    full_name: Optional[str] = Field(default=None, max_length=100)
    role: UserRole = Field(default=UserRole.USER)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    alerts: List["Alert"] = Relationship(back_populates="assigned_to")

class Sensor(SQLModel, table=True):
    __tablename__ = "sensors"
    id: Optional[int] = Field(default=None, primary_key=True)
    serial_number: str = Field(unique=True, index=True, max_length=50)
    location: Optional[str] = Field(default=None, max_length=100)
    type: str = Field(default="generic", max_length=50)
    is_active: bool = Field(default=True)
    last_seen: Optional[datetime] = Field(default=None)
    
    measurements: List["Measurement"] = Relationship(back_populates="sensor")

class Measurement(SQLModel, table=True):
    __tablename__ = "measurements"
    id: Optional[int] = Field(default=None, primary_key=True)
    sensor_id: int = Field(foreign_key="sensors.id")
    temperature: float
    humidity: float
    co2_level: float
    aqi: Optional[float] = Field(default=None) 
    measured_at: datetime = Field(default_factory=datetime.utcnow)
    
    sensor: Optional[Sensor] = Relationship(back_populates="measurements")
    alerts: List["Alert"] = Relationship(back_populates="measurement")

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class Alert(SQLModel, table=True):
    __tablename__ = "alerts"
    id: Optional[int] = Field(default=None, primary_key=True)
    measurement_id: int = Field(foreign_key="measurements.id")
    assigned_to_id: Optional[int] = Field(default=None, foreign_key="users.id")
    
    message: str = Field(max_length=255)
    severity: AlertSeverity = Field(default=AlertSeverity.INFO)
    is_resolved: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    measurement: Optional[Measurement] = Relationship(back_populates="alerts")
    assigned_to: Optional[User] = Relationship(back_populates="alerts")

class SystemSetting(SQLModel, table=True): 
    __tablename__ = "system_settings"
    key: str = Field(primary_key=True, max_length=50)
    value: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(SQLModel, table=True): 
    __tablename__ = "audit_logs"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    action: str = Field(max_length=100)
    target: str = Field(max_length=100)
    details: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
