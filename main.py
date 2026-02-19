import os
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet

# Import your local files
import models, schemas, database
from database import engine, get_db

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- ENCRYPTION SETUP ---
# It looks for the key in Render's settings. 
# If it can't find it, it uses a default (for your local laptop testing).
SECRET_KEY = os.getenv("ENCRYPTION_KEY", "b'7_X9_Zp8V_X88R5_m_Jk1cK5_Stores_Example='")
fernet = Fernet(SECRET_KEY.encode() if isinstance(SECRET_KEY, str) else SECRET_KEY)

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    passwords = db.query(models.Password).all()
    # Decrypt passwords for display
    for p in passwords:
        try:
            p.password_text = fernet.decrypt(p.password_text.encode()).decode()
        except:
            p.password_text = "Encryption Error"
    return templates.TemplateResponse("index.html", {"request": request, "passwords": passwords})

@app.post("/add")
def add_password(service: str = Form(...), password_text: str = Form(...), db: Session = Depends(get_db)):
    # Encrypt the password before saving to PostgreSQL
    encrypted_password = fernet.encrypt(password_text.encode()).decode()
    new_password = models.Password(service=service, password_text=encrypted_password)
    db.add(new_password)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# Add a delete route for your friends/clients to use
@app.post("/delete/{password_id}")
def delete_password(password_id: int, db: Session = Depends(get_db)):
    db_password = db.query(models.Password).filter(models.Password.id == password_id).first()
    if db_password:
        db.delete(db_password)
        db.commit()
    return RedirectResponse(url="/", status_code=303)