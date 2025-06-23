"""
Ekspor data monitoring ke file CSV.
"""
import csv
from typing import List, Dict

def export_to_csv(data: List[Dict], path: str) -> None:
    """Ekspor list of dict ke file CSV."""
    if not data:
        return
    fieldnames = list(data[0].keys())
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data) 