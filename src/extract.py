import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# Imitialize local variable configuration mapping
load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def fetch_api_page(country_code, target_term, page_number):
    # Executes an isolated API call to extract an atomic data block from Adzuna
    url = f"{BASE_URL}/{country_code}/search/{page_number}"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": target_term,
        "results_per_page": 50,
        "content-type": "application/json"
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def fetch_all_jobs(country_code="gb", keyword="Data Analyst", max_pages=None):
    all_jobs = []
    page = 1

    # First request (to find total pages)
    first_response = fetch_api_page(country_code, keyword, page)

    if not first_response:
        print("Failed to fetch data")
        return []

    total_pages = first_response.get("pages", 1)

    print(f"Total pages available: {total_pages}")

    # Decide how many pages to fetch
    if max_pages:
        total_pages = min(total_pages, max_pages)

    # Add first page results
    all_jobs.extend(first_response.get("results", []))

    print(
        f"Fetched page {page} with {len(first_response.get('results', []))} jobs")

    # Loop through remaining pages
    for page in range(2, total_pages + 1):
        try:
            data = fetch_api_page(country_code, keyword, page)
            jobs = data.get("results", [])
            all_jobs.extend(jobs)
            print(f"Fetched page {page} with {len(jobs)} jobs")
        except requests.RequestException as e:
            print(f"Error on page {page}: {e}")

            continue

    print(f"\nTotal jobs collected: {len(all_jobs)}")

    return all_jobs


def save_raw_data(jobs, keyword):
    # Save extracted jobs to JSON file.

    os.makedirs("data/raw", exist_ok=True)

    today = datetime.today().strftime("%Y-%m-%d")
    file_path = f"data/raw/jobs_{keyword}_{today}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=4)

    print(f"Data saved to {file_path}")


if __name__ == "__main__":

    country = "gb"
    keyword = "Data Analyst"

    jobs = fetch_all_jobs(country_code=country, keyword=keyword, max_pages=5)

    save_raw_data(jobs, keyword)
