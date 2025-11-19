from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

# -------------------------------
# Groq client configuration
# -------------------------------
client = Groq(api_key=API_KEY)  # replace with your Groq API key

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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    try:
        text = response.choices[0].message.content
        # Extract JSON from AI response
        json_text = text[text.find("{"): text.rfind("}") + 1]
        return json.loads(json_text)
    except Exception as e:
        return {"id": None, "name": "No suitable doctor found", "error": str(e)}


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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        text = response.choices[0].message.content
        json_text = text[text.find("{"): text.rfind("}") + 1]
        return json.loads(json_text)
    except Exception as e:
        return {"medicines": [], "error": str(e)}
