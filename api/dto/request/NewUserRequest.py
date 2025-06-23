from pydantic import BaseModel

class NewUserRequest(BaseModel):
    user_id: int
    birth: str
    gender: str
    address: str
    interestCategory: str