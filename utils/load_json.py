import os
import json

def load_all_jobs(directory="preprocessed"):
    all_jobs = []

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    jobs = json.load(f)
                    if isinstance(jobs, list):
                        all_jobs.extend(jobs)
                    else:
                        print(f"⚠️ Skipped: {filename} did not contain a list.")
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")

    return all_jobs
