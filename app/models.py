from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class NoteIn(BaseModel):
    username: str
    password: str
    note: str

class NoteOut(BaseModel):
    note: str
