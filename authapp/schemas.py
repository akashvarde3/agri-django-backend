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
    description: str | None = None
    user_provided_area: str | None = None
    calculated_area_sqm: float
    status: dict | None = None
    created_at: str | None = None

# Added schemas for cycles and harvest
class CycleCreateSchema(Schema):
    plot_id:int
    crop_name:str
    area_acres:float
    status:str | None = "Growing"
class HarvestCreateSchema(Schema):
    cycle_id:int
    harvested_area_acres:float
    harvested_qty:float
    is_final:bool | None = False

class HarvestEventOut(Schema):
    id:int
    harvested_on:str
    harvested_area_acres:float | None = None
    harvested_qty:float | None = None
    qr_url:str | None = None
    blockchain_tx:str | None = None

class CropCycleOutSchema(Schema):
    id:int
    plot_id:int
    crop_name:str
    area_acres:float
    status:str
    sowing_date:str | None = None
    harvested_qty_total:float | None = None
    harvested_area_total:float | None = None
    harvests:list[HarvestEventOut]

class PlotWithCyclesSchema(Schema):
    id:int
    plot_name:str
    description:str | None = None
    calculated_area_sqm:float
    user_provided_area:str | None = None
    status:dict | None = None
    created_at:str | None = None
    cycles:list[CropCycleOutSchema]
