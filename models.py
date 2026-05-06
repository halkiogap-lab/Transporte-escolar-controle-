from pydantic import BaseModel
from typing import Optional, List

class Child(BaseModel):
    id: int
    name: str
    defaultAddress: Optional[str] = None
    notes: Optional[str] = None
    shift: Optional[str] = None
    createdAt: str

class CreateChild(BaseModel):
    name: str
    defaultAddress: Optional[str] = None
    notes: Optional[str] = None
    shift: Optional[str] = None

class UpdateChild(BaseModel):
    name: Optional[str] = None
    defaultAddress: Optional[str] = None
    notes: Optional[str] = None
    shift: Optional[str] = None

class AttendanceRow(BaseModel):
    childId: int
    name: str
    defaultAddress: Optional[str] = None
    shift: Optional[str] = None
    date: str
    status: str
    address: Optional[str] = None

class UpsertAttendance(BaseModel):
    childId: int
    date: str
    status: str
    address: Optional[str] = None

class RouteStop(BaseModel):
    childId: int
    name: str
    address: str

class Route(BaseModel):
    date: str
    stops: List[RouteStop]

class Stats(BaseModel):
    date: str
    totalChildren: int
    presentCount: int
    absentCount: int
    unmarkedCount: int
    addressesOnFile: int

class HealthStatus(BaseModel):
    status: str
  
