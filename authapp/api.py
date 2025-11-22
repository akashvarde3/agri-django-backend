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
