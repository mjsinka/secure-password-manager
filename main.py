from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import models
from database import engine, get_db

# 1. Initialize Database Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2. Static & Template Config
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 3. Encryption Setup (Using your generated key)
KEY = b'8n4KPEpMzuKwMKXusRQTb4byeXERYs6vae2mYZuKbcY=' 
cipher = Fernet(KEY)

# 4. View Passwords
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    db_passwords = db.query(models.PasswordEntry).all()
    
    display_list = []
    for entry in db_passwords:
        try:
            decrypted_pw = cipher.decrypt(entry.encrypted_password.encode()).decode()
            display_list.append({
                "id": entry.id,
                "service": entry.service_name,
                "pw": decrypted_pw
            })
        except:
            continue
            
    return templates.TemplateResponse("index.html", {"request": request, "passwords": display_list})

# 5. Save Password
@app.post("/save")
async def save(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    encrypted_pw = cipher.encrypt(password.encode()).decode()
    new_entry = models.PasswordEntry(service_name=username, encrypted_password=encrypted_pw)
    db.add(new_entry)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# 6. Delete Password
@app.post("/delete/{entry_id}")
async def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(models.PasswordEntry).filter(models.PasswordEntry.id == entry_id).first()
    if entry:
        db.delete(entry)
        db.commit()
    return RedirectResponse(url="/", status_code=303)