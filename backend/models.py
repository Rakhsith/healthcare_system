from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    department = Column(String)
    gender = Column(String)
    age = Column(Integer)
    treatment_cost = Column(Float)
    readmission = Column(String)
    outcome = Column(String)
