from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str

    class Config:
        from_attributes = True

class SignupIn(BaseModel):
    email: EmailStr
    name: str
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str
