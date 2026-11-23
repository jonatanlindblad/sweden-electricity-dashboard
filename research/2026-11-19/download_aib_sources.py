"""Collect AIB reports and workbooks for 2015–2024 in a new archive folder.

This is a source-collection step, not part of a normal dashboard refresh.
Keep the reviewed archive: the extraction script uses its numbered filenames.
To collect another snapshot, deliberately choose a different archive folder
below and review its sources before using them in the analysis.
"""

from datetime import date
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, unquote, urljoin, urlparse
from urllib.request import urlopen


archive_folder = Path(__file__).resolve().parent / "aib"


class PageLinks(HTMLParser):
    """Collect the link addresses found in an annual webpage."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attributes):
        if tag == "a":
            for name, value in attributes:
                if name == "href" and value is not None:
                    self.links.append(value)


def download_year_sources(year):
    page_url = f"https://www.aib-net.org/facts/european-residual-mix/{year}"
    with urlopen(page_url, timeout=60) as response:
        page_content = response.read()
    (archive_folder / f"{year}.html").write_bytes(page_content)

    page_links = PageLinks()
    page_links.feed(page_content.decode())
    document_urls = []
    for link in page_links.links:
        if urlparse(link).path.lower().endswith((".pdf", ".xlsx")):
            document_urls.append(urljoin(page_url, link))

    # Remove duplicate links and sort them before assigning numbered filenames.
    document_urls = sorted(set(document_urls))
    download_records = []
    for index, document_url in enumerate(document_urls):
        if urlparse(document_url).hostname != "www.aib-net.org":
            raise ValueError(f"Review document link outside AIB: {document_url}")
        document_url = quote(unquote(document_url), safe=":/?=&%")
        file_extension = Path(urlparse(document_url).path).suffix.lower()
        filename = f"{year}_{index}{file_extension}"

        try:
            with urlopen(document_url, timeout=60) as response:
                document_content = response.read()
        except HTTPError as error:
            download_records.append({
                "year": year,
                "url": document_url,
                "error": str(error),
            })
            continue

        (archive_folder / filename).write_bytes(document_content)
        download_records.append({
            "year": year,
            "file": filename,
            "url": document_url,
            "landing_url": page_url,
            "sha256": sha256(document_content).hexdigest(),
            "retrieved": date.today().isoformat(),
        })

    return download_records


def main():
    # Stop before downloading if this archive already exists. Reusing numbered
    # files could attach an old document to a new URL when AIB's links change.
    if archive_folder.exists():
        raise FileExistsError(
            f"Archive already exists: {archive_folder}. "
            "Keep it intact; choose a new folder for a new source snapshot."
        )
    archive_folder.mkdir()

    download_records = []
    for year in range(2015, 2025):
        download_records.extend(download_year_sources(year))
        # Save after each completed year so earlier records survive a later error.
        manifest_file = archive_folder / "manifest.json"
        manifest_file.write_text(
            json.dumps(download_records, indent=2) + "\n", encoding="utf-8"
        )

    for record in download_records:
        print(record.get("file", record.get("error")), record["url"])


if __name__ == "__main__":
    main()
