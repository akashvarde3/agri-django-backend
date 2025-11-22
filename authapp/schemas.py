from ninja import Schema
from typing import List, Any
class RegisterSchema(Schema):
    name: str
    mobile: str
    password: str
    agristack_id: str | None = None

class LoginSchema(Schema):
    mobile: str
    password: str
    otp: str | None = None

class FarmerOut(Schema):
    id: int
    name: str
    mobile: str
    role: str
    agristack_id: str | None

class PlotCreateSchema(Schema):
    farmer_id: int
    plotName: str
    description: str | None = None
    userProvidedArea: str | None = None
    calculatedAreaSqM: float
    polygonCoordinates: List[List[float]]
    tempPoints: List[Any] | None = []
    markers: List[List[float]] = []
    photoGeo: List[float] | None = None
    photoFile: str | None = None
    status: dict | None = {}

class PlotOutSchema(Schema):
    id: int
    plot_name: str
