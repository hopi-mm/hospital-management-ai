from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
# Configure Gemini API key
genai.configure(api_key=API_KEY)

app = FastAPI(title="Hospital AI API")


# -------------------------------
# Models
# -------------------------------
class Doctor(BaseModel):
    id: int
    name: str
    specialization: List[str]


class RecommendDoctorRequest(BaseModel):
    doctors: List[Doctor]
    reason: str


class SuggestMedicineRequest(BaseModel):
    medical_records: List[Dict]
    symptoms: List[str]


# -------------------------------
# Doctor Recommendation Endpoint
# -------------------------------
@app.post("/recommend-doctor")
def recommend_doctor(data: RecommendDoctorRequest):
    doctors_list = [(d.id, d.name, d.specialization) for d in data.doctors]

    prompt = f"""
You are a hospital AI assistant. A patient has the following reason: "{data.reason}".
From the following doctors, recommend the most suitable doctor.
Doctors: {doctors_list}
Return only JSON: {{'id': , 'name': }}
"""

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(prompt)

    try:
        return json.loads(response.text)
    except:
        return {"id": None, "name": "No suitable doctor found"}


# -------------------------------
# Medicine Suggestion Endpoint
# -------------------------------
@app.post("/suggest-medicine")
def suggest_medicine(data: SuggestMedicineRequest):
    prompt = f"""
You are a hospital AI assistant. A patient has symptoms: {data.symptoms}.
Past medical records: {data.medical_records}
Suggest medicines in a JSON list format: {{'medicines': []}}
"""

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(prompt)

    try:
        return json.loads(response.text)
    except:
        return {"medicines": []}
