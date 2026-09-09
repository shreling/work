from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List

import pandas as pd


DEFAULT_INPUT_FOLDER = Path(
    "C:/Users/shreya.lingam/OneDrive - Mediolanum International Funds/Desktop/EMD/2025"
)


def _require_pdfplumber() -> None:
    try:
        import pdfplumber  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "Missing dependency: pdfplumber. Install with: pip install pdfplumber"
        ) from exc


def _safe_sheet_name(name: str, existing: set[str]) -> str:
    clean = re.sub(r"[:\\/?*\[\]]", "_", name).strip()
    if not clean:
        clean = "Sheet"
    clean = clean[:31]

    candidate = clean
    i = 1
    while candidate in existing:
        suffix = f"_{i}"
        candidate = f"{clean[:31 - len(suffix)]}{suffix}"
        i += 1
    return candidate


def _extract_country_weight_table_from_lines(lines: List[str]) -> pd.DataFrame:
    rows: List[Dict[str, str | float]] = []
    header_terms = {
        "emb",
        "global",
        "diversified",
        "index",
        "country",
        "weights",
    }

    for raw_line in lines:
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue

        lower = line.lower()
        if sum(1 for term in header_terms if term in lower) >= 2:
            continue

        numeric_tokens = re.findall(r"[-+]?\d+(?:[\.,]\d+)?", line)
        if len(numeric_tokens) != 1:
            continue

        match = re.match(r"^(?P<country>[A-Za-z][A-Za-z .&'/-]*?)\s+(?P<value>[-+]?\d+(?:[\.,]\d+)?)$", line)
        if not match:
            parts = line.rsplit(" ", 1)
            if len(parts) != 2:
                continue
            country_candidate, value_candidate = parts[0].strip(), parts[1].strip()
            if not country_candidate:
                continue
            if not re.fullmatch(r"[-+]?\d+(?:[\.,]\d+)?", value_candidate):
                continue
            country = country_candidate
            value_text = value_candidate
        else:
            country = match.group("country").strip()
            value_text = match.group("value").strip()

        try:
            weight = float(value_text.replace(",", "."))
        except ValueError:
            continue

        rows.append({"Country": country, "Weight": weight})

    if len(rows) < 3:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    return df.drop_duplicates(subset=["Country"], keep="first")


def _extract_country_returns_table_from_lines(lines: List[str]) -> pd.DataFrame:
    rows: List[List[str]] = []
    number_pattern = r"[-+]?\d+(?:[\.,]\d+)?"

    for raw_line in lines:
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue

        numbers = re.findall(number_pattern, line)
        if len(numbers) < 3:
            continue

        first_number_match = re.search(number_pattern, line)
        if not first_number_match:
            continue

        country = line[: first_number_match.start()].strip(" -:\t")
        if not country:
            continue
        if not re.search(r"[A-Za-z]", country):
            continue

        row = [country] + [num.replace(",", ".") for num in numbers]
        rows.append(row)

    if len(rows) < 3:
        return pd.DataFrame()

    max_cols = max(len(r) for r in rows)
    normalized = [r + [""] * (max_cols - len(r)) for r in rows]
    headers = ["Country"] + [f"Return_{i}" for i in range(1, max_cols)]
    df = pd.DataFrame(normalized, columns=headers)

    for col in headers[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["Country"]).drop_duplicates(subset=["Country"], keep="first")


def _extract_lines_from_pdf(pdf_path: Path) -> List[str]:
    import pdfplumber

    lines: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
            for line in text.splitlines():
                clean = line.strip()
                if clean:
                    lines.append(clean)
    return lines


def _lines_to_dataframe(lines: List[str]) -> pd.DataFrame:
    if not lines:
        return pd.DataFrame()

    returns_df = _extract_country_returns_table_from_lines(lines)
    if not returns_df.empty:
        return returns_df

    weight_df = _extract_country_weight_table_from_lines(lines)
    if not weight_df.empty:
        return weight_df

    rows: List[List[str]] = []
    for line in lines:
        parts = [p.strip() for p in re.split(r"\s{2,}", line) if p.strip()]
        if len(parts) >= 2:
            rows.append(parts)

    if not rows:
        return pd.DataFrame({"Text": lines})

    max_cols = max(len(r) for r in rows)
    normalized = [r + [""] * (max_cols - len(r)) for r in rows]
    headers = [f"Column_{i + 1}" for i in range(max_cols)]
    return pd.DataFrame(normalized, columns=headers)


def pdf_table_to_dataframe(pdf_path: Path) -> pd.DataFrame:
    lines = _extract_lines_from_pdf(pdf_path)
    return _lines_to_dataframe(lines)


def convert_pdf_folder_to_excel(input_folder: Path, output_excel: Path | None = None) -> Path:
    _require_pdfplumber()

    if not input_folder.exists() or not input_folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {input_folder}")

    pdf_files = sorted(input_folder.glob("*.pdf"))
    if not pdf_files:
        raise ValueError(f"No PDF files found in {input_folder}")

    if output_excel is None:
        output_excel = input_folder / "pdf_tables.xlsx"

    existing_sheets: set[str] = set()
    sheet_payloads: List[tuple[str, pd.DataFrame]] = []

    for pdf_path in pdf_files:
        sheet_name = _safe_sheet_name(pdf_path.stem, existing_sheets)
        existing_sheets.add(sheet_name)

        try:
            df = pdf_table_to_dataframe(pdf_path)
            if df.empty:
                df = pd.DataFrame({"Message": ["No table text detected from PDF"]})
        except Exception as exc:
            df = pd.DataFrame(
                {
                    "Message": ["Failed to extract table from PDF"],
                    "File": [str(pdf_path.name)],
                    "Error": [str(exc)],
                }
            )

        sheet_payloads.append((sheet_name, df))

    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        for sheet_name, df in sheet_payloads:
            df.to_excel(writer, index=False, sheet_name=sheet_name)

    return output_excel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read all PDF files from a folder and write each file to a separate "
            "sheet in one Excel workbook."
        )
    )
    parser.add_argument(
        "input_folder",
        nargs="?",
        type=Path,
        default=None,
        help=(
            "Folder containing PDF files. "
            f"If omitted, defaults to: {DEFAULT_INPUT_FOLDER}"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output Excel path (default: <input_folder>/pdf_tables.xlsx)",
    )
    args, _unknown = parser.parse_known_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    input_folder = args.input_folder or DEFAULT_INPUT_FOLDER
    output_path = convert_pdf_folder_to_excel(input_folder, args.output)
    print(f"Excel workbook created: {output_path}")
