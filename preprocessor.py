import requests
import csv
import time
import json
from pathlib import Path





def fetch_wikipedia_intro(name: str) -> str:
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '_')}"
    r = requests.get(url, headers={"User-Agent": "speciesnet-fetcher/1.0"})
    if r.status_code == 200:
        data = r.json()
        return data.get("extract", "")
    return ""

# Example: read taxonomy_release.txt and write out CSV with descriptions
with open("models/taxonomy_release.txt", "r", encoding="utf-8") as infile, \
     open("models/taxonomy_with_desc.csv", "w", newline="", encoding="utf-8") as outfile:

    writer = csv.writer(outfile)
    writer.writerow(["uuid", "class", "order", "family", "genus", "species", "common_name", "description"])

    for line in infile:
        parts = line.strip().split(";")
        if len(parts) < 7:
            continue
        uuid, clss, order, family, genus, species, common = parts

        # Use common name if available, else genus/species
        query_name = common if common else (species if species else genus)

        desc = fetch_wikipedia_intro(query_name)
        time.sleep(0.5)  # be gentle with requests

        writer.writerow([uuid, clss, order, family, genus, species, common, desc])
        print(common + " " +  desc)




def create_local_save():
    ANIMALS = []
    BASE_DIR = Path(__file__).parent
    csv_path = str(BASE_DIR / "models" / "taxonomy_with_desc.csv")
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("common_name") and row.get("description"):
                try:
                    ANIMALS.append({
                        "name": row["common_name"],
                        "description": row.get("description"),
                        "image": ""
                    })
                except ValueError:
                    pass
    with open(BASE_DIR / "models" / "animals.json", "w", encoding="utf-8") as f:
        json.dump(ANIMALS, f)

print("Done: taxonomy_with_desc.csv created")
print("Starting: Local DB Initialization")
create_local_save()
print("Done: Local DB Created")