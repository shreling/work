"""
Fetches MSCI Index Level data from Snowflake for all index codes listed in
the MSCI Index Code Excel file, and exports to JS for the
New Manager Input page of the MS Manager Returns Dashboard.

Usage:
    python fetch_msci_index_data.py
"""

import os
import sys
# Support both MS/Utilities and repository-root Utilities locations.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Utilities'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Utilities'))

import snowflake.connector
import json
import pandas as pd
from datetime import datetime

# Paths to the Excel file containing MSCI index codes (prefer OneDrive source, fallback local copy)
MSCI_CODES_FILE_CANDIDATES = [
    r"C:\Users\shreya.lingam\OneDrive - Mediolanum International Funds\Desktop\MIA\MS Rotation\Manager Returns\MSCI Index Code for Dashboard.xlsx",
    os.path.join(os.path.dirname(__file__), 'MSCI Index Code for Dashboard.xlsx'),
]

MSCI_QUERY_TEMPLATE = """
SELECT
        TO_VARCHAR(il.MSCI_INDEX_CODE) AS MSCI_INDEX_CODE,
    il.CALC_DATE,
        '{index_name}' AS INDEX_NAME,
    il.INDEX_VARIANT_TYPE,
    il.ISO_CURRENCY_SYMBOL,
    il.LEVEL,
    il.NB_OF_SECURITIES
FROM MSCI.INDEX.INDEX_LEVELS il
WHERE il.CALC_DATE > '{start_date}'
    AND il.MSCI_INDEX_CODE = {msci_code}
  AND il.INDEX_VARIANT_TYPE = 'NETR'
  AND il.ISO_CURRENCY_SYMBOL = 'EUR'
    AND il.LEVEL IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY il.MSCI_INDEX_CODE, DATE_TRUNC('MONTH', il.CALC_DATE)
    ORDER BY il.CALC_DATE DESC
) = 1
ORDER BY il.MSCI_INDEX_CODE, il.CALC_DATE
"""


def get_snowflake_connection():
    """Create Snowflake connection using shared config."""
    import snowflake_connector_config as config
    conn = snowflake.connector.connect(
        user=config.user,
        password=config.password,
        account=config.account
    )
    return conn


def normalize_msci_code(value):
    """Normalize code values from Excel (e.g. 12345.0 -> 12345)."""
    text = str(value).strip()
    if text.endswith('.0'):
        text = text[:-2]
    return text


def load_msci_codes():
    """Load MSCI index codes from the Excel file."""
    msci_codes_file = next((p for p in MSCI_CODES_FILE_CANDIDATES if os.path.exists(p)), None)
    if not msci_codes_file:
        raise FileNotFoundError(
            'MSCI Index Code file not found. Checked: ' + ', '.join(MSCI_CODES_FILE_CANDIDATES)
        )

    df = pd.read_excel(msci_codes_file)
    # Clean column names (trailing spaces)
    df.columns = df.columns.str.strip()
    # Return as list of dicts with code and name
    codes = []
    for _, row in df.iterrows():
        code = normalize_msci_code(row['MSCI Index Code'])
        codes.append({
            'code': code,
            'name': str(row['Index_Name']).strip()
        })
    return codes


def _sql_escape(value):
    return str(value).replace("'", "''")


def build_msci_query(msci_code, index_name, start_date='2000-01-01'):
    return MSCI_QUERY_TEMPLATE.format(
        msci_code=int(msci_code),
        index_name=_sql_escape(index_name),
        start_date=_sql_escape(start_date)
    )


def load_existing_cache(js_path):
    """Load existing JS cache payload if available; otherwise return empty payload."""
    if not os.path.exists(js_path):
        return {'indices': [], 'data': {}, 'last_updated': None}

    with open(js_path, 'r') as f:
        content = f.read()

    marker = 'var CACHED_MSCI_INDEX_DATA = '
    start = content.find(marker)
    if start == -1:
        print('Existing JS cache format not recognized; rebuilding from scratch.')
        return {'indices': [], 'data': {}, 'last_updated': None}

    start += len(marker)
    end = content.rfind(';')
    if end == -1 or end <= start:
        print('Existing JS cache payload invalid; rebuilding from scratch.')
        return {'indices': [], 'data': {}, 'last_updated': None}

    payload_text = content[start:end].strip()
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        print('Existing JS cache JSON malformed; rebuilding from scratch.')
        return {'indices': [], 'data': {}, 'last_updated': None}

    if not isinstance(payload, dict):
        return {'indices': [], 'data': {}, 'last_updated': None}

    payload.setdefault('indices', [])
    payload.setdefault('data', {})
    payload.setdefault('last_updated', None)
    return payload


def get_latest_cached_date(records):
    """Return max date string (YYYY-MM-DD) from cached records."""
    valid_dates = [r.get('date') for r in records if isinstance(r, dict) and r.get('date')]
    return max(valid_dates) if valid_dates else None


def merge_records(existing_records, new_records):
    """Merge existing and newly fetched records by date, preferring new values."""
    by_date = {}
    for rec in existing_records:
        date = rec.get('date')
        if date:
            by_date[date] = rec
    for rec in new_records:
        date = rec.get('date')
        if date:
            by_date[date] = rec
    return [by_date[d] for d in sorted(by_date.keys())]


def fetch_msci_index_data(existing_cache=None):
    """Incrementally fetch MSCI index level data and append to existing cache."""
    msci_codes = load_msci_codes()
    print(f"Loaded {len(msci_codes)} MSCI index codes from Excel.")

    existing_data = (existing_cache or {}).get('data', {})
    conn = get_snowflake_connection()
    all_data = {}
    missing_codes = []
    total_new_rows = 0
    unchanged_codes = 0

    try:
        total_codes = len(msci_codes)
        for idx, item in enumerate(msci_codes, start=1):
            code = normalize_msci_code(item['code'])
            name = item['name']
            existing_entry = existing_data.get(code, {}) if isinstance(existing_data, dict) else {}
            existing_records = existing_entry.get('records', []) if isinstance(existing_entry, dict) else []
            last_cached_date = get_latest_cached_date(existing_records)
            start_date = last_cached_date if last_cached_date else '2000-01-01'
            query = build_msci_query(code, name, start_date=start_date)

            if last_cached_date:
                print(f"  [{idx}/{total_codes}] Querying {code} ({name}) since {last_cached_date}...")
            else:
                print(f"  [{idx}/{total_codes}] Querying {code} ({name}) full history...")
            df = pd.read_sql(query, conn)
            df.columns = [c.upper() for c in df.columns]

            if df.empty:
                if existing_records:
                    unchanged_codes += 1
                    all_data[code] = {
                        'index_name': name,
                        'msci_code': code,
                        'records': existing_records
                    }
                else:
                    missing_codes.append({'code': code, 'name': name, 'reason': 'No data'})
                continue

            # Normalize dates to calendar month-end (e.g. 29 May -> 31 May)
            df['CALC_DATE'] = pd.to_datetime(df['CALC_DATE']) + pd.offsets.MonthEnd(0)
            df['CALC_DATE'] = df['CALC_DATE'].dt.strftime('%Y-%m-%d')

            records = []
            for _, row in df.iterrows():
                records.append({
                    'date': row['CALC_DATE'],
                    'level': float(row['LEVEL']) if pd.notna(row['LEVEL']) else None,
                    'nb_securities': int(row['NB_OF_SECURITIES']) if pd.notna(row['NB_OF_SECURITIES']) else None,
                })

            total_new_rows += len(records)
            merged_records = merge_records(existing_records, records)
            all_data[code] = {
                'index_name': name,
                'msci_code': code,
                'records': merged_records
            }
    finally:
        conn.close()

    if missing_codes:
        print(f"\nCodes with no data ({len(missing_codes)}):")
        for mc in missing_codes:
            print(f"  {mc['code']} ({mc['name']}): {mc['reason']}")

    total_records = sum(len(v['records']) for v in all_data.values())
    print(f"Fetched {total_new_rows} new rows for {len(all_data)} indices.")
    print(f"Unchanged indices (no new rows): {unchanged_codes}")
    print(f"Total cached monthly records after merge: {total_records}")

    return all_data, msci_codes


def export_to_js(all_data, msci_codes, output_path=None):
    """Export MSCI index data to JS cache file consumed by the dashboard."""
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), 'msci_index_data.js')

    # Build index lookup for the dashboard
    index_lookup = [{'code': item['code'], 'name': item['name']} for item in msci_codes]

    output = {
        'indices': index_lookup,
        'data': all_data,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    with open(output_path, 'w') as f:
        f.write('// Auto-generated MSCI index level data - do not edit manually\n')
        f.write('// Last updated: ' + output['last_updated'] + '\n')
        f.write('var CACHED_MSCI_INDEX_DATA = ')
        json.dump(output, f)
        f.write(';\n')

    print(f"\nMSCI JS cache exported to {output_path}")
    print(f"  Indices with data: {len(all_data)}")
    total_records = sum(len(v['records']) for v in all_data.values())
    print(f"  Total monthly records: {total_records}")
    return output_path


if __name__ == '__main__':
    print("=" * 60)
    print("MSCI Index Data Fetcher for New Manager Input Page")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    cache_path = os.path.join(os.path.dirname(__file__), 'msci_index_data.js')
    existing_cache = load_existing_cache(cache_path)
    if existing_cache.get('last_updated'):
        print(f"Existing cache last updated: {existing_cache['last_updated']}")
    else:
        print("No existing cache found. Running full initial load.")
    print()

    all_data, msci_codes = fetch_msci_index_data(existing_cache=existing_cache)
    export_to_js(all_data, msci_codes)

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
