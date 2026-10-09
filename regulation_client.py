import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

RAILWAY_BASE_URL = os.getenv("RAILWAY_BASE_URL")

# Matches "GRZ 0.6", "GRZ of 0.6", "GRZ: 0.6", "GRZ is 0.6" etc.
GRZ_PATTERN = re.compile(r"grz[^0-9]{0,20}(0\.\d{1,3}|1\.0)", re.IGNORECASE)


def extract_grz_from_text(analysis_text):
    """Pulls a GRZ figure out of the system's free-text answer. Returns None
    if no value was stated — which is itself meaningful, matching your
    benchmark's N/A category rather than a failure."""
    match = GRZ_PATTERN.search(analysis_text)
    return float(match.group(1)) if match else None

FABRICATION_MARKERS = ["CONSULTATION REPORT", "REALISTIC DEVELOPMENT SCENARIO", "Prepared by: Architecture Consultant"]


def is_fabricated_report(analysis_text):
    """Checks whether the system's response matches the known fabricated
    Consultation Report pattern found on plot 18A."""
    return any(marker in analysis_text for marker in FABRICATION_MARKERS)
    

def get_regulatory_grz(plot_number, location="Stuttgart", district="general", query=None):
    """Calls your production multi-agent endpoint and extracts the GRZ value
    the system stated, if any."""
    if query is None:
        query = f"What is the GRZ for plot {plot_number}?"

    payload = {
        "query": query,
        "project_type": "mixed-use",
        "location": location,
        "district": district,
        "urgency": "normal",
        "use_multi_agent": True,
        "plot_number": plot_number,
    }

    response = requests.post(f"{RAILWAY_BASE_URL}/api/multi-agent/analyze", json=payload, timeout=90)
    response.raise_for_status()
    data = response.json()

    analysis_text = data.get("analysis", "")
    extracted_grz = extract_grz_from_text(analysis_text)

    return {
        "extracted_grz": extracted_grz,
        "analysis_text": analysis_text,
        "is_plot_query": data.get("is_plot_query"),
        "vision_used": data.get("vision_used"),
        "query_type": data.get("query_type"),
    }