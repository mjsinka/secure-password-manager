from sqlalchemy import Column, Integer, String
from database import Base

class PasswordEntry(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String)
    encrypted_password = Column(String)