from fastapi import FastAPI, HTTPException, Depends, Request
from app.models import UserCreate, NoteIn, NoteOut
from app.database import SessionLocal, User
from app.auth import hash_password, verify_password
from app.crypto import encrypt_note, decrypt_note
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
@limiter.limit("5/minute")
def register(user: UserCreate, db=Depends(get_db)):
    if db.query(User).filter_by(username=user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/note", response_model=NoteOut)
@limiter.limit("10/minute")
def save_note(note_data: NoteIn, db=Depends(get_db)):
    user = db.query(User).filter_by(username=note_data.username).first()
    if not user or not verify_password(note_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.encrypted_note = encrypt_note(note_data.note)
    db.commit()
    return {"note": "Note saved securely"}

@app.post("/note/retrieve", response_model=NoteOut)
@limiter.limit("10/minute")
def get_note(note_data: UserCreate, db=Depends(get_db)):
    user = db.query(User).filter_by(username=note_data.username).first()
    if not user or not verify_password(note_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.encrypted_note:
        raise HTTPException(status_code=404, detail="No note found")
    decrypted = decrypt_note(user.encrypted_note)
    return {"note": decrypted}
