from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Farmer, Plot 
from .schemas import RegisterSchema, LoginSchema, FarmerOut ,  PlotCreateSchema, PlotOutSchema
from .jwt import create_jwt 
router = Router()

@router.post("/register", response=FarmerOut)
def register_farmer(request, payload: RegisterSchema):

    if Farmer.objects.filter(mobile=payload.mobile).exists():
        return {"error": "Mobile number already registered"}

    farmer = Farmer(
        name=payload.name,
        mobile=payload.mobile,
        role="farmer",
        agristack_id=payload.agristack_id
    )
    farmer.set_password(payload.password)
    farmer.save()

    return farmer


@router.post("/login")
def login_farmer(request, payload: LoginSchema):
    try:
        farmer = Farmer.objects.get(mobile=payload.mobile)
    except Farmer.DoesNotExist:
        return {"success": False, "message": "Mobile not registered"}

    if not farmer.check_password(payload.password):
        return {"success": False, "message": "Incorrect password"}

    # OTP optional
    # if payload.otp: handle OTP here later

    token = create_jwt(farmer.id)

    return {
        "success": True,
        "token": token,
        "farmer": {
            "id": farmer.id,
            "name": farmer.name,
            "mobile": farmer.mobile,
            "role": farmer.role
        }
    }


@router.post("/create", response={200: dict})
def create_plot(request, payload: PlotCreateSchema):
    farmer = get_object_or_404(Farmer, id=payload.farmer_id)

    plot = Plot.objects.create(
        farmer=farmer,
        plot_name=payload.plotName,
        description=payload.description,
        user_provided_area=payload.userProvidedArea,
        calculated_area_sqm=payload.calculatedAreaSqM,
        polygon_coordinates=payload.polygonCoordinates,
        markers=payload.markers,
        photo_geo=payload.photoGeo,
        photo_file=payload.photoFile,
        status=payload.status,
    )

    return {
        "success": True,
        "plot_id": plot.id,
        "message": "Plot registered successfully"
    }


@router.get("/list/{farmer_id}", response=list[PlotOutSchema])
def list_plots(request, farmer_id:int):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    return Plot.objects.filter(farmer=farmer)


@router.get("/detail/{plot_id}", response=PlotOutSchema)
def get_plot(request, plot_id:int):
    return get_object_or_404(Plot, id=plot_id)

# Added cycle and harvest APIs
from .models import CropCycle, HarvestEvent, ProductionHistory
from .schemas import CycleCreateSchema, HarvestCreateSchema, CropCycleOutSchema, HarvestEventOut, PlotWithCyclesSchema

def _harvest_totals(cycle: CropCycle):
    total_area = 0.0
    total_qty = 0.0
    for h in cycle.harvests.all():
        if h.harvested_area_acres:
            total_area += float(h.harvested_area_acres)
        if h.harvested_qty:
            total_qty += float(h.harvested_qty)
    return total_area or None, total_qty or None

def _serialize_harvest(h: HarvestEvent) -> HarvestEventOut:
    return HarvestEventOut(
        id=h.id,
        harvested_on=h.harvested_on.isoformat(),
        harvested_area_acres=h.harvested_area_acres,
        harvested_qty=h.harvested_qty,
        qr_url=h.qr_url,
        blockchain_tx=h.blockchain_tx,
    )

def _serialize_cycle(c: CropCycle) -> CropCycleOutSchema:
    total_area, total_qty = _harvest_totals(c)
    return CropCycleOutSchema(
        id=c.id,
        plot_id=c.plot.id,
        crop_name=c.crop_name,
        area_acres=c.area_acres,
        status=c.status,
        sowing_date=c.sowing_date.isoformat() if c.sowing_date else None,
        harvested_qty_total=total_qty,
        harvested_area_total=total_area,
        harvests=[_serialize_harvest(h) for h in c.harvests.all().order_by("-harvested_on", "-id")],
    )

def _serialize_plot_with_cycles(plot: Plot) -> PlotWithCyclesSchema:
    return PlotWithCyclesSchema(
        id=plot.id,
        plot_name=plot.plot_name,
        description=plot.description,
        calculated_area_sqm=plot.calculated_area_sqm,
        user_provided_area=plot.user_provided_area,
        status=plot.status,
        created_at=plot.created_at.isoformat() if plot.created_at else None,
        cycles=[_serialize_cycle(c) for c in plot.cycles.all().order_by("-id")],
    )
@router.post('/cycle/create')
def create_cycle(request,p:CycleCreateSchema):
    plot=get_object_or_404(Plot,id=p.plot_id)
    c=CropCycle.objects.create(plot=plot,crop_name=p.crop_name,area_acres=p.area_acres,status=p.status or "Growing")
    return {'success':True,'cycle_id':c.id}

@router.get('/cycles/{plot_id}', response=list[CropCycleOutSchema])
def list_cycles(request, plot_id:int):
    plot = get_object_or_404(Plot, id=plot_id)
    return [_serialize_cycle(c) for c in plot.cycles.all().order_by("-id")]

@router.post('/harvest/partial', response=dict)
def partial_harvest(request,p:HarvestCreateSchema):
    c=get_object_or_404(CropCycle,id=p.cycle_id)
    h=HarvestEvent.objects.create(crop_cycle=c,harvested_area_acres=p.harvested_area_acres,harvested_qty=p.harvested_qty,qr_url='qr',blockchain_tx='tx')
    total_area, _ = _harvest_totals(c)
    if total_area and total_area >= c.area_acres:
        c.status = "Harvested"
        c.save(update_fields=["status"])
    elif p.is_final:
        c.status = "Harvested"
        c.save(update_fields=["status"])
    else:
        c.status = "Partial harvest"
        c.save(update_fields=["status"])
    return {'success':True,'event_id':h.id,'cycle_status':c.status}

@router.post('/harvest/final', response=dict)
def final_harvest(request, payload: HarvestCreateSchema):
    c=get_object_or_404(CropCycle,id=payload.cycle_id)
    h=HarvestEvent.objects.create(crop_cycle=c,harvested_area_acres=payload.harvested_area_acres,harvested_qty=payload.harvested_qty,qr_url='qr_final',blockchain_tx='tx_final')
    c.status = "Harvested"
    c.save(update_fields=["status"])
    history=ProductionHistory.objects.create(plot=c.plot,crop_cycle=c,harvested_on=h.harvested_on,final_yield=payload.harvested_qty,qr_url=h.qr_url,blockchain_tx=h.blockchain_tx)
    return {'success':True,'history_id':history.id,'cycle_status':c.status}

@router.get("/with-cycles/{farmer_id}", response=list[PlotWithCyclesSchema])
def plots_with_cycles(request, farmer_id:int):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    plots = Plot.objects.filter(farmer=farmer).order_by("-id")
    return [_serialize_plot_with_cycles(p) for p in plots]
