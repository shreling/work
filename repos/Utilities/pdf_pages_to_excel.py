"""Extract selected PDF pages and save the actual table(s) to Excel.

Usage examples:
    python Utilities/pdf_pages_to_excel.py "C:/docs/report.pdf" --pages "1,3,5-8"
    python Utilities/pdf_pages_to_excel.py "C:/docs/report.pdf" --pages "8" --output "C:/docs/page8.xlsx" --headings "Composition,Statistics"
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable, List, Sequence

import pdfplumber
from openpyxl import Workbook
from openpyxl.styles import Alignment


def parse_pages(pages_arg: str, total_pages: int) -> List[int]:
    value = pages_arg.strip().lower()
    if value == "all":
        return list(range(total_pages))

    selected: set[int] = set()
    tokens = [token.strip() for token in pages_arg.split(",") if token.strip()]
    if not tokens:
        raise ValueError("No pages were provided.")

    for token in tokens:
        if re.fullmatch(r"\d+", token):
            page_num = int(token)
            if not 1 <= page_num <= total_pages:
                raise ValueError(f"Page {page_num} is out of range 1-{total_pages}.")
            selected.add(page_num - 1)
            continue

        if re.fullmatch(r"\d+-\d+", token):
            start_str, end_str = token.split("-", 1)
            start, end = int(start_str), int(end_str)
            if start > end:
                raise ValueError(f"Invalid range '{token}'. Start page must be <= end page.")
            if start < 1 or end > total_pages:
                raise ValueError(f"Range '{token}' is out of bounds 1-{total_pages}.")
            for page_num in range(start, end + 1):
                selected.add(page_num - 1)
            continue

        raise ValueError(
            f"Invalid token '{token}'. Use formats like 1,3,5-8 or 'all'."
        )

    return sorted(selected)


def normalize_table(table: Sequence[Sequence[object]]) -> list[list[str]]:
    cleaned = []
    for row in table:
        normalized = [str(cell).strip() if cell is not None else "" for cell in row]
        if any(cell for cell in normalized):
            cleaned.append(normalized)
    return cleaned


def page_has_any_heading(page_text: str, headings: Sequence[str] | None) -> bool:
    if not headings:
        return True
    lower_text = page_text.lower()
    return any(heading.lower() in lower_text for heading in headings)


def extract_page_tables(
    pdf_path: Path,
    page_indices: Iterable[int],
    headings: Sequence[str] | None = None,
) -> list[tuple[int, list[list[list[str]]]]]:
    tables_by_page: list[tuple[int, list[list[list[str]]]]] = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        for index in page_indices:
            page = pdf.pages[index]
            page_text = page.extract_text() or ""
            extracted_tables = page.extract_tables() or []
            cleaned_tables: list[list[list[str]]] = []

            for table in extracted_tables:
                normalized_table = normalize_table(table)
                if not normalized_table:
                    continue
                if headings and not page_has_any_heading(page_text, headings):
                    continue
                cleaned_tables.append(normalized_table)

            if not cleaned_tables and headings and not page_has_any_heading(page_text, headings):
                tables_by_page.append((index + 1, []))
                continue

            if not cleaned_tables and not headings:
                cleaned_tables = [normalize_table(table) for table in extracted_tables if normalize_table(table)]

            tables_by_page.append((index + 1, cleaned_tables))

    return tables_by_page


def write_excel(page_tables: list[tuple[int, list[list[list[str]]]]], output_path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Extracted Tables"

    has_data = False
    for page_number, tables in page_tables:
        if not tables:
            continue

        has_data = True
        ws.append([f"Page {page_number}"])

        for table in tables:
            for row in table:
                ws.append(row)
            ws.append([])

    if ws.max_row > 0 and all(cell is None or str(cell).strip() == "" for cell in ws[ws.max_row]):
        ws.delete_rows(ws.max_row, 1)

    for row in ws.iter_rows():
        for cell in row:
            if cell.value is None:
                continue
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    ws.freeze_panes = "A2"
    wb.save(output_path)

    if not has_data:
        raise ValueError("No tables were detected for the selected pages.")


def build_output_path(pdf_path: Path, output_arg: str | None) -> Path:
    if output_arg:
        return Path(output_arg).expanduser().resolve()
    return pdf_path.with_name(f"{pdf_path.stem}_pages.xlsx")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract selected PDF page tables to an Excel file."
    )
    parser.add_argument("pdf_path", help="Full path to the PDF file.")
    parser.add_argument(
        "--pages",
        required=True,
        help="Page selection: 'all' or values like '1,3,5-8'.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output .xlsx path. Defaults to same folder as PDF.",
    )
    parser.add_argument(
        "--headings",
        default=None,
        help="Optional filter to keep only tables containing one of these headings, e.g. 'Composition,Statistics'.",
    )

    args = parser.parse_args()

    pdf_path = Path(args.pdf_path).expanduser().resolve()
    if not pdf_path.exists() or not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file must be a .pdf: {pdf_path}")

    with pdfplumber.open(str(pdf_path)) as pdf:
        total_pages = len(pdf.pages)

    if total_pages == 0:
        raise ValueError("PDF has no pages.")

    headings = None
    if args.headings:
        headings = [heading.strip() for heading in args.headings.split(",") if heading.strip()]

    page_indices = parse_pages(args.pages, total_pages)
    page_tables = extract_page_tables(pdf_path, page_indices, headings=headings)

    output_path = build_output_path(pdf_path, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_excel(page_tables, output_path)

    print(f"Done. Extracted tables to: {output_path}")


if __name__ == "__main__":
    main()
