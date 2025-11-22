from ninja import Schema

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
