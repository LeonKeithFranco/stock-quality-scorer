import csv

import httpx
from bs4 import BeautifulSoup

from scripts.utils import CSV_FOLDER_PATH, FILE_BASE_NAME, get_today_date_as_str


def main():
    """Scrape the current S&P 500 constituents from Wikipedia and save to CSV.

    Fetches the constituents table from the Wikipedia S&P 500 page and writes it to a
    date-stamped CSV file. Skips the download if a file for today already exists.

    Raises:
        ValueError: If the constituents table is not found on the page.
    """
    today_date_str = get_today_date_as_str()
    full_file_name = f"{FILE_BASE_NAME}{today_date_str}.csv"
    file_path = CSV_FOLDER_PATH / full_file_name

    if file_path.exists():
        return

    response = httpx.get(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find("table", id="constituents")

    if table is None:
        raise ValueError("Table of S&P 500 constituents not found")

    rows = table.find_all("tr")

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        header_cells = [cell.get_text(strip=True) for cell in rows[0].find_all("th")]
        writer.writerow(header_cells)

        for row in rows[1:]:
            data_cells = [cell.get_text(strip=True) for cell in row.find_all("td")]
            writer.writerow(data_cells)


if __name__ == "__main__":
    main()
