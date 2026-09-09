"""
Fetches Managed Account Daily Metrics from Snowflake and exports to JSON
for the MS Manager Returns Dashboard.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Utilities'))

import snowflake.connector
import json
import pandas as pd
from datetime import datetime

PRE_APPOINTMENT_MAP_DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__),
    'Manager Returns Dashboard',
    'Historic Data SAA Map.xlsx'
)
POST_APPOINTMENT_MAP_DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__),
    'Manager Returns Dashboard',
    'SAA_map_final.xlsx'
)

SNOWFLAKE_QUERY_BASE = """
SELECT 
    MADM.MANAGED_ACCOUNT_KEY,
    MADM.DATE_KEY,
    DD.CALENDAR_DATE,
    MA.MANAGED_ACCOUNT_ID,
    MA.MANAGED_ACCOUNT_NAME,
    MADM.MANAGED_ACCOUNT_RETURN_INDEX,
    MADM.RELATIVE_SAA_RETURN_INDEX,
    MAD.CUSTODY_ACCOUNT_CODE,
    MAD.RBC_FA_CODE,
    MAD.CACEIS_MANAGER_CODE,
    MADM.FUND_ACCOUNTING_AUM
FROM PROD_MED_DATAHUB.DIMENSIONAL_WAREHOUSE.MANAGED_ACCOUNT_DAILY_METRICS MADM
JOIN PROD_MED_DATAHUB.DIMENSIONAL_WAREHOUSE.MANAGED_ACCOUNT_DIMENSION MAD
    ON MAD.MANAGED_ACCOUNT_KEY = MADM.MANAGED_ACCOUNT_KEY
JOIN PROD_MED_DATAHUB.MDM_MDH.MANAGED_ACCOUNT MA
    ON MA.RBC_FA_CODE = MAD.RBC_FA_CODE
JOIN PROD_MED_DATAHUB.DIMENSIONAL_WAREHOUSE.DATE_DIMENSION DD
    ON DD.DATE_KEY = MADM.DATE_KEY
"""

# Query used strictly for the Manager Pre-Appointment dashboard.
PRE_APPOINTMENT_QUERY_BASE = """
SELECT *
FROM IAR.MS.MS_RAG_HISTORY
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


def load_post_appointment_rbc_codes(map_path, sheet_name=None):
    """
    Load RBC_FA_CODE values from the post-appointment map workbook.
    If sheet_name is None, uses the first sheet.
    """
    if not os.path.exists(map_path):
        raise FileNotFoundError(f'SAA map file not found: {map_path}')

    sheet_to_use = sheet_name if sheet_name else 0
    map_df = pd.read_excel(map_path, sheet_name=sheet_to_use)
    map_df.columns = [str(c).strip().upper() for c in map_df.columns]

    candidate_cols = ['RBC_FA_CODE', 'RBC FA CODE', 'RBC_FA', 'RBC CODE']
    code_col = next((c for c in candidate_cols if c in map_df.columns), None)
    if code_col is None:
        raise ValueError(
            f'No RBC_FA_CODE column found in map file {map_path}. '
            f'Checked: {candidate_cols}'
        )

    rbc_codes = (
        map_df[code_col]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != '']
        .drop_duplicates()
        .tolist()
    )
    return rbc_codes


def build_manager_returns_query(rbc_codes):
    """Build manager-returns query filtered to map RBC_FA_CODE values."""
    if not rbc_codes:
        raise ValueError('No RBC_FA_CODE values found in SAA map; cannot build filtered query.')

    escaped = [code.replace("'", "''") for code in rbc_codes]
    in_list = ', '.join(f"'{code}'" for code in escaped)

    return (
        SNOWFLAKE_QUERY_BASE
        + f"\nWHERE TO_VARCHAR(MAD.RBC_FA_CODE) IN ({in_list})"
        + "\nORDER BY DD.CALENDAR_DATE, MADM.MANAGED_ACCOUNT_KEY"
    )


def fetch_data(map_path=POST_APPOINTMENT_MAP_DEFAULT_PATH, sheet_name=None):
    """Fetch map-filtered manager returns data from Snowflake."""
    rbc_codes = load_post_appointment_rbc_codes(map_path, sheet_name=sheet_name)
    query = build_manager_returns_query(rbc_codes)

    conn = get_snowflake_connection()
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    
    df.columns = [c.upper() for c in df.columns]
    df['CALENDAR_DATE'] = pd.to_datetime(df['CALENDAR_DATE'])
    return df


def fetch_pre_appointment_data():
    """Backward-compatible wrapper using default FinalMap path."""
    return fetch_pre_appointment_data_with_map(PRE_APPOINTMENT_MAP_DEFAULT_PATH)


def load_pre_appointment_id_codes(map_path, sheet_name='FinalMap'):
    """
    Load ID_CODE values from the FinalMap sheet.
    The fetched pre-appointment dataset is filtered to this strategy universe.
    """
    if not os.path.exists(map_path):
        raise FileNotFoundError(f'FinalMap file not found: {map_path}')

    map_df = pd.read_excel(map_path, sheet_name=sheet_name)
    map_df.columns = [str(c).strip().upper() for c in map_df.columns]

    if 'ID_CODE' not in map_df.columns:
        raise ValueError(
            f'Column ID_CODE not found in sheet {sheet_name!r} of {map_path}'
        )

    id_codes = (
        map_df['ID_CODE']
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != '']
        .drop_duplicates()
        .tolist()
    )
    return id_codes


def build_pre_appointment_query(id_codes):
    """Build Snowflake query filtered to FinalMap ID_CODE values."""
    if not id_codes:
        raise ValueError('No ID_CODE values found in FinalMap; cannot build filtered query.')

    # Escape single quotes for SQL string literals.
    escaped = [code.replace("'", "''") for code in id_codes]
    in_list = ', '.join(f"'{code}'" for code in escaped)

    return PRE_APPOINTMENT_QUERY_BASE + f"\nWHERE TO_VARCHAR(ID_CODE) IN ({in_list})"


def fetch_pre_appointment_data_with_map(map_path, sheet_name='FinalMap'):
    """Fetch MS_RAG_HISTORY filtered by FinalMap ID_CODEs."""
    id_codes = load_pre_appointment_id_codes(map_path, sheet_name=sheet_name)
    query = build_pre_appointment_query(id_codes)

    conn = get_snowflake_connection()
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()

    df.columns = [c.upper() for c in df.columns]
    return df


def export_pre_appointment_to_js(df, output_path=None):
    """
    Export the MS_RAG_HISTORY DataFrame to JS cache for the pre-appointment dashboard.
    Structure: { columns: [...], data: [ {col: value, ...}, ... ], last_updated: ... }
    This data is used strictly by the Manager Pre-Appointment dashboard.
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), 'pre_appointment_data.js')

    # Serialize records generically so any column set is supported.
    records = json.loads(df.to_json(orient='records', date_format='iso'))

    output = {
        'columns': df.columns.tolist(),
        'data': records,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    with open(output_path, 'w') as f:
        f.write('// Auto-generated cached data - do not edit manually\n')
        f.write('// Last updated: ' + output['last_updated'] + '\n')
        f.write('var CACHED_PRE_APPOINTMENT_DATA = ')
        json.dump(output, f)
        f.write(';\n')

    print(f"Pre-appointment JS cache exported to {output_path}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Total records: {len(df)}")
    return output_path


def export_to_js(df, output_path=None):
    """
    Export DataFrame to JS cache format consumable by the HTML dashboard.
    Structure: { managers: [...], data: { manager_name: [{date, return_index, relative_index, aum}, ...] } }
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), 'manager_returns_data.js')

    managers = sorted(df['MANAGED_ACCOUNT_NAME'].unique().tolist())
    
    data = {}
    for mgr in managers:
        mgr_df = df[df['MANAGED_ACCOUNT_NAME'] == mgr].sort_values('CALENDAR_DATE')
        records = []
        for _, row in mgr_df.iterrows():
            records.append({
                'date': row['CALENDAR_DATE'].strftime('%Y-%m-%d'),
                'return_index': float(row['MANAGED_ACCOUNT_RETURN_INDEX']) if pd.notna(row['MANAGED_ACCOUNT_RETURN_INDEX']) else None,
                'relative_saa_index': float(row['RELATIVE_SAA_RETURN_INDEX']) if pd.notna(row['RELATIVE_SAA_RETURN_INDEX']) else None,
                'aum': float(row['FUND_ACCOUNTING_AUM']) if pd.notna(row['FUND_ACCOUNTING_AUM']) else None,
                'managed_account_id': row.get('MANAGED_ACCOUNT_ID', ''),
                'managed_account_key': int(row['MANAGED_ACCOUNT_KEY']),
                'custody_account_code': row.get('CUSTODY_ACCOUNT_CODE', ''),
                'rbc_fa_code': row.get('RBC_FA_CODE', ''),
            })
        data[mgr] = records

    output = {
        'managers': managers,
        'data': data,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    with open(output_path, 'w') as f:
        f.write('// Auto-generated cached data - do not edit manually\n')
        f.write('// Last updated: ' + output['last_updated'] + '\n')
        f.write('var CACHED_MANAGER_DATA = ')
        json.dump(output, f)
        f.write(';\n')

    print(f"Manager returns JS cache exported to {output_path}")
    print(f"  Managers: {len(managers)}")
    print(f"  Total records: {len(df)}")
    return output_path


def run_manager_returns(map_path=None):
    if map_path is None:
        map_path = POST_APPOINTMENT_MAP_DEFAULT_PATH

    print("Fetching manager returns data from Snowflake...")
    print(f"Using SAA_map_final source: {map_path}")

    rbc_codes = load_post_appointment_rbc_codes(map_path)
    print(f"Loaded {len(rbc_codes)} RBC_FA_CODE values from map.")

    df = fetch_data(map_path)
    print(f"Fetched {len(df)} rows.")
    export_to_js(df)
    print("Done.")


def run_pre_appointment(map_path=None):
    if map_path is None:
        map_path = PRE_APPOINTMENT_MAP_DEFAULT_PATH

    print("Fetching pre-appointment (MS_RAG_HISTORY) data from Snowflake...")
    print(f"Using FinalMap source: {map_path}")

    id_codes = load_pre_appointment_id_codes(map_path)
    print(f"Loaded {len(id_codes)} ID_CODE values from FinalMap.")

    df = fetch_pre_appointment_data_with_map(map_path)
    print(f"Fetched {len(df)} rows.")
    export_pre_appointment_to_js(df)
    print("Done.")


if __name__ == '__main__':
    # Usage:
    #   python fetch_manager_returns_data.py                  -> manager returns only (default)
    #   python fetch_manager_returns_data.py "<path-to-SAA_map_final.xlsx>"
    #     -> manager returns only using explicit post-appointment map
    #   python fetch_manager_returns_data.py pre-appointment  -> pre-appointment data only
    #   python fetch_manager_returns_data.py pre-appointment "<path-to-Historic Data SAA Map.xlsx>"
    #   python fetch_manager_returns_data.py all "<path-to-SAA_map_final.xlsx>" "<path-to-Historic Data SAA Map.xlsx>"
    #     -> run both datasets with explicit map paths
    target = sys.argv[1].lower() if len(sys.argv) > 1 else 'manager-returns'
    map_path_arg = sys.argv[2] if len(sys.argv) > 2 else None
    pre_map_path_arg = sys.argv[3] if len(sys.argv) > 3 else None

    if target in ('pre-appointment', 'pre_appointment', 'preappointment'):
        run_pre_appointment(map_path_arg)
    elif target == 'all':
        run_manager_returns(map_path_arg)
        run_pre_appointment(pre_map_path_arg)
    else:
        run_manager_returns(map_path_arg)
