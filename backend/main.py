from fastapi import FastAPI
from .database import engine, SessionLocal
from .models import Base, Patient
import random

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MedIntel X API")

def seed_data():
    db = SessionLocal()
    if db.query(Patient).count() == 0:
        departments = ["Cardiology","Neurology","Orthopedics","Oncology"]
        genders = ["Male","Female"]
        outcomes = ["Recovered","Deceased"]
        for i in range(500):
            patient = Patient(
                department=random.choice(departments),
                gender=random.choice(genders),
                age=random.randint(20,80),
                treatment_cost=random.randint(10000,100000),
                readmission=random.choice(["Yes","No"]),
                outcome=random.choice(outcomes)
            )
            db.add(patient)
        db.commit()
    db.close()

seed_data()

@app.get("/patients")
def get_patients():
    db = SessionLocal()
    data = db.query(Patient).all()
    return data

@app.get("/kpis")
def get_kpis():
    db = SessionLocal()
    data = db.query(Patient).all()
    total = len(data)
    revenue = sum(p.treatment_cost for p in data)
    readmission_rate = sum(1 for p in data if p.readmission=="Yes") / total * 100
    return {
        "total_patients": total,
        "total_revenue": revenue,
        "readmission_rate": readmission_rate
    }
