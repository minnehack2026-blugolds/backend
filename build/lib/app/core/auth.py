from dataclasses import dataclass
from fastapi import Depends

@dataclass
class CurrentUser:
    id: int
    email: str

# TODO: replace with real auth later
async def get_current_user() -> CurrentUser:
    return CurrentUser(id=1, email="demo@school.edu")

def require_user(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user
