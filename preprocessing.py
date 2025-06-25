import os
import json
import re
from datetime import datetime, timedelta

# === FOLDER SETUP ===
RAW_FOLDER = r"C:\Users\Jhotika Raja\OneDrive\Documents\GitHub\ai-freelance-copilot\raw_data"
PROCESSED_FOLDER = r"C:\Users\Jhotika Raja\OneDrive\Documents\GitHub\ai-freelance-copilot\processed"
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# === HELPERS ===
def clean_description(text):
    if not isinstance(text, str): return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

def extract_skills(job):
    return [
        v.lower().strip()
        for k, v in job.items()
        if k.startswith("skill") and not k.endswith("_url") and isinstance(v, str)
    ]

def extract_budget_in_inr(budget_text):
    if not isinstance(budget_text, str): return None, None, None
    usd_to_inr = 83
    clean = budget_text.replace("$", "").replace(",", "")
    match = re.findall(r"(\d+)", clean)
    budget_type = "hourly" if "hour" in clean.lower() else "fixed"
    if len(match) == 1:
        amt = int(match[0]) * usd_to_inr
        return amt, amt, budget_type
    elif len(match) >= 2:
        return int(match[0]) * usd_to_inr, int(match[1]) * usd_to_inr, budget_type
    return None, None, budget_type

def parse_days_left(text):
    if not isinstance(text, str): return None, None
    match = re.search(r"(\d+)\s+day", text.lower())
    if match:
        days = int(match.group(1))
        expiry = datetime.utcnow() + timedelta(days=days)
        return expiry.strftime("%Y-%m-%dT%H:%M:%SZ"), days
    return None, None

def extract_bids(bids_text):
    if not isinstance(bids_text, str): return 0
    match = re.search(r"\d+", bids_text)
    return int(match.group()) if match else 0

# === MAIN PROCESSING LOOP ===
for filename in os.listdir(RAW_FOLDER):
    if filename.endswith(".json"):
        file_path = os.path.join(RAW_FOLDER, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                jobs = json.load(f)  # ✅ Assumes each file contains a LIST of job dicts
            except Exception as e:
                print(f"⚠️ Failed to load {filename}: {e}")
                continue

        cleaned_jobs = []
        category = filename.replace(".json", "").lower().replace(" ", "_")

        for job in jobs['job_title']:
            title = job.get("name", "").strip()
            description = clean_description(job.get("description", ""))
            description_length = len(description.split())
            skills = extract_skills(job)
            budget_min, budget_max, budget_type = extract_budget_in_inr(job.get("budget", ""))
            timestamp, days_remaining = parse_days_left(job.get("timestamp", ""))
            bids = extract_bids(job.get("bids", "0"))

            cleaned_jobs.append({
                "title": title,
                "description": description,
                "description_length": description_length,
                "skills": skills,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "budget_type": budget_type,
                "bids": bids,
                "category": category,
                "source": "freelancer",
                "deadline": timestamp,
                "days_remaining": days_remaining,
                "url": job.get("url", "")
            })

        output_name = f"{category}_cleaned.json"
        output_path = os.path.join(PROCESSED_FOLDER, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_jobs, f, indent=2)

        print(f"✅ Cleaned and saved: {output_name}")
