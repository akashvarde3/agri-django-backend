from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Farmer
from .schemas import RegisterSchema, LoginSchema, FarmerOut
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
