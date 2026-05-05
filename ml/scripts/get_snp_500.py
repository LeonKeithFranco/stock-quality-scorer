import csv
from datetime import datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

_CSV_BASE_NAME = "snp_500_constituents_"


def main():
    today_date_str = datetime.now().date().strftime("%y%m%d")
    full_file_name = f"{_CSV_BASE_NAME}{today_date_str}.csv"
    file_path = Path(__file__).parent.parent / "data" / full_file_name

    if file_path.exists():
        return

    response = httpx.get(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="constituents")

    if table is None:
        raise ValueError("Table of S&P 500 constituents not found")

    rows = table.find_all("tr")

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        header_cells = [cell.get_text(strip=True) for cell in rows[0].find_all("th")]
        writer.writerow(header_cells)

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)

        for row in rows[1:]:
            data_cells = [cell.get_text(strip=True) for cell in row.find_all("td")]
            writer.writerow(data_cells)


if __name__ == "__main__":
    main()
