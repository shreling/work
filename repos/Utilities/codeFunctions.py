import pandas as pd
import snowflake_connector_config as config
import databaseConnectionSnowflake as db
import snowflake.connector
import math
import numpy as np
import datetime
from datetime import datetime, timedelta

def GetCorporateActionSecurities(MinDate, MaxDate):

    QDriveLocation = 'Q:/Investment/Securities/Quant/Data/Ecosystem Data/Universe Files/'
    FileRead = QDriveLocation + 'Universe_' + MaxDate + '.pickle'
    FileRead
    
    UniverseDT = pd.read_pickle(FileRead)
    
    FSYMIDsInScope = UniverseDT.FSYM_REGIONAL_ID.unique()
    FSYMIDsInScope = FSYMIDsInScope.tolist()
    
    params = {
      'MaxDate': MaxDate,
      'MinDate': MinDate,
      'FilterFSYMIDs': FSYMIDsInScope
    }
    
    ctx = snowflake.connector.connect(user=config.user, password=config.password, account=config.account)
    
    SplitFactorRaw = pd.read_sql("""SELECT FSYM_ID, P_SPLIT_DATE AS DATE, P_SPLIT_FACTOR FROM FACTSET.FP_V2.FP_BASIC_SPLITS
                                 WHERE DATE <= %(MaxDate)s
                                 AND DATE >= %(MinDate)s
                                 AND FSYM_ID IN (%(FilterFSYMIDs)s)""", params=params, con=ctx)
    
    Div_SpinFactorRaw = pd.read_sql("""SELECT FSYM_ID, P_DIVS_EXDATE AS DATE, P_DIVS_PD FROM FACTSET.FP_V2.FP_BASIC_DIVIDENDS
                                    WHERE P_DIVS_EXDATE <= %(MaxDate)s
                                    AND P_DIVS_EXDATE >= %(MinDate)s
                                    AND FSYM_ID IN (%(FilterFSYMIDs)s)""",params=params, con=ctx)  
                                 
                                 
    SplitScope = SplitFactorRaw.FSYM_ID.unique().tolist()
    DivScope = Div_SpinFactorRaw.FSYM_ID.unique().tolist()
    
    CombinedScope = SplitScope + DivScope
    print(len(CombinedScope))

    return CombinedScope

def GetUniverseData(MinDate, MaxDate):

    params = {'FilterMinDate': MinDate, 'FilterMaxDate':MaxDate}

    ctx = snowflake.connector.connect(user=config.user, password=config.password, account=config.account)


    UniverseData = pd.read_sql("""SELECT * FROM QUANT.WORKING.UNIVERSE 
                               WHERE DATA_DATE <= %(FilterMaxDate)s
                               AND DATA_DATE >= %(FilterMinDate)s""",
                               params=params, con=ctx)

    return(UniverseData)

def GetDistinctUniverseSecurities():
    
    ctx = snowflake.connector.connect(user=config.user, password=config.password, account=config.account)

    UniverseSecurities = pd.read_sql("""SELECT distinct(FSYM_REGIONAL_ID) FROM QUANT.WORKING.UNIVERSE""", con=ctx)
    UniverseSecurities = UniverseSecurities['FSYM_REGIONAL_ID'].unique().tolist()

    return(UniverseSecurities)

def GetPrevRunFSYMInScope(ChooseTableType):
    """
    This function retrieves the last run FSYM (Financial Symmetric) in scope based on the chosen table type.
    
    Parameters:
    ChooseTableType (str): The type of table to choose. It can be either 'Prices' or 'Estimates'.
    
    Returns:
    DataFrame: A pandas DataFrame containing the last price FSYMs with the date.
    """
    
    # Establish a connection to the Snowflake database
    ctx = snowflake.connector.connect(user=config.user, password=config.password, account=config.account)
    
    # If the chosen table type is 'Prices'
    if  ChooseTableType=='Prices':
        # Define the table name
        TableName='QUANT.WORKING.DATA_RETURNS'
        
        # Query the database to get the last price date
        LastPriceDate = pd.read_sql("""SELECT max(data_date) as DATA_DATE from QUANT.WORKING.DATA_RETURNS""", con=ctx)
        LastPriceDate = str(LastPriceDate['DATA_DATE'].item())
        
        # Query the database to get the last price FSYMs
        LastPriceFSYMs = pd.read_sql(f"""SELECT distinct(FSYM_REGIONAL_ID) FROM {TableName} where DATA_DATE = '{LastPriceDate}'""",con=ctx)
        
        # Add the date to the DataFrame
        LastPriceFSYMs = LastPriceFSYMs.assign(DATE = LastPriceDate)
        
    # If the chosen table type is 'Estimates'
    if  ChooseTableType=='Estimates':
        # Define the table name
        TableName='QUANT.WORKING.DATA_CONSTITUENTS'
        
        # Query the database to get the estimate constituents
        EstConsts = pd.read_sql("""SELECT distinct(CONSTITUENT_ID) FROM QUANT.WORKING.REF_CONSTITUENTS WHERE CONSTITUENT_TYPE = 'Estimates'""", con=ctx)
        EstConsts = EstConsts['CONSTITUENT_ID'].unique().tolist()

        # Query the database to get the last estimate date
        LastEstDate = pd.read_sql(f"""SELECT max(data_date) as DATA_DATE FROM QUANT.WORKING.DATA_CONSTITUENTS 
                                      WHERE CONSTITUENT_ID IN {tuple(EstConsts)}""", con=ctx)
        LastEstDate = str(LastEstDate['DATA_DATE'].item())

        # Query the database to get the last price FSYMs for the estimate date
        LastPriceFSYMs = pd.read_sql(f"""SELECT distinct(FSYM_REGIONAL_ID) AS FSYM_REGIONAL_ID FROM QUANT.WORKING.DATA_CONSTITUENTS 
                                        WHERE CONSTITUENT_ID IN {tuple(EstConsts)} AND DATA_DATE = '{LastEstDate}' """, con=ctx)    
        
        # Add the date to the DataFrame
        LastPriceFSYMs = LastPriceFSYMs.assign(DATE = LastEstDate)

    # Return the DataFrame
    return LastPriceFSYMs


def df_clean_up(constBasic, constID):
    
    historical = 'CURRENCY' in constBasic.columns
    #constBasic = CURR_LTM_df
    
    basicFinal = constBasic.copy()
    #basicFinal = constBasic.loc[constBasic['UPDATE_TYPE_QF'] == '3']
    
    "Prevent bad padding of stale data"
    basicFinal = basicFinal.fillna(-99999999999)       

    # expand and pad fw
    if historical == True:
        
        fctrs = constID[~constID['CONSTITUENT_ITEM'].isin(['P_PRICE', 'CURRENCY'])]
        fctrs = fctrs['CONSTITUENT_ITEM'].dropna().drop_duplicates().reset_index(drop= True)
    
    else:
        fctrs = constID.loc[constID['CONSTITUENT_ITEM'] != 'P_PRICE']
        fctrs = fctrs['CONSTITUENT_ITEM'].dropna()
        fctr_list = fctrs.tolist()
        fctr_list.append('P_DIVS_PS')
        fctrs = pd.Series(fctr_list)
    
    
    constBasicExp = basicFinal.copy()
    constBasicExp['DATETIME'] = pd.to_datetime(constBasicExp['DATE'])
    
    # check which factors are actually present in the dataframe
    fctrs = [col for col in fctrs if col in constBasicExp.columns]

    constBasicExp = constBasicExp.groupby(['FSYM_REGIONAL_ID',pd.Grouper(key='DATETIME', freq='M')])[fctrs].mean()
    constBasicExp = (constBasicExp.reset_index(level=0)
            .groupby('FSYM_REGIONAL_ID')[fctrs]
            .apply(lambda x: x.asfreq('M'))
            .reset_index())
    
    constBasicExp = column_Timestamp_To_Date(constBasicExp, "DATETIME", "DATE", True)
    constBasicExp_pad = constBasicExp.copy()
    
    for f in fctrs: 
        
        if f == 'P_DIVS_PS':
            unpadded = False
            LTM = False
        else:
            con_method = constID.loc[constID['CONSTITUENT_ITEM'] == f].reset_index(drop=True)
            LTM = (con_method['CONSTITUENT_METHODOLOGY'].iloc[0] == 'LTM')
            unpadded = (con_method['CONSTITUENT_TYPE'].iloc[0] == 'Unpadded')
        
        if unpadded == True:
            constBasicExp_pad[f] = constBasicExp_pad[f].replace(-99999999999, np.nan)
        
        else:
        
            if LTM == False:
                constBasicExp_pad[f] = (constBasicExp_pad
                                              .groupby('FSYM_REGIONAL_ID')[f]
                                              .ffill(limit=12))
            else:
                constBasicExp_pad[f] = (constBasicExp_pad
                                              .groupby('FSYM_REGIONAL_ID')[f]
                                              .ffill(limit=18))
            
    if historical == True:
        rep_frq = basicFinal.filter(items = ['FSYM_REGIONAL_ID', 'DATE', 'REPORTING_FREQ', 'CURRENCY']).drop_duplicates()
    else:
        rep_frq = basicFinal.filter(items = ['FSYM_REGIONAL_ID', 'DATE', 'REPORTING_FREQ']).drop_duplicates()
        
        
    constBasicExp_pad_1 = constBasicExp_pad.merge(rep_frq, on = ['FSYM_REGIONAL_ID', 'DATE'], how = 'left')
    
    if 'REPORTING_FREQ' in constBasicExp_pad_1.columns:
        constBasicExp_pad_1['REPORTING_FREQ'] = (constBasicExp_pad_1
                                          .groupby('FSYM_REGIONAL_ID')['REPORTING_FREQ']
                                          .ffill(limit=12))
    
    if historical == True:
        constBasicExp_pad_1['CURRENCY'] = (constBasicExp_pad_1
                                          .groupby('FSYM_REGIONAL_ID')['CURRENCY']
                                          .ffill(limit=12))
    
    first_column = constBasicExp_pad_1.pop('DATE')
    constBasicExp_pad_1.insert(0, 'DATE', first_column)

    first_column = constBasicExp_pad_1.pop('FSYM_REGIONAL_ID')
    constBasicExp_pad_1.insert(0, 'FSYM_REGIONAL_ID', first_column)

    return constBasicExp_pad_1

def column_Timestamp_To_Date(df, oldColumnName, newColumnName, deleteOldColumn = False):
    dates = []
    for i in range(0, df.shape[0]):
        dates.append(pd.to_datetime(df[oldColumnName].iloc[i]).date())
    df[newColumnName] = dates
    if deleteOldColumn == True:
        df = df.drop(columns = [oldColumnName])
    return df

def column_Date_To_Timestamp(df, oldColumnName, newColumnName, deleteOldColumn = False):
    df[newColumnName] = pd.to_datetime(df[oldColumnName], infer_datetime_format=True)
    if deleteOldColumn == True:
        df = df.drop(columns = [oldColumnName])
    return df

def timestamps_to_ME(df, oldColumnName, newColumnName, deleteOldColumn = False):
    Today = datetime.today()
    month_end_dates = []
    uni_dates = df[oldColumnName].unique()
    df_dates = pd.DataFrame(uni_dates, columns = ['TimeStamps'])
    for d in df_dates['TimeStamps']:
        if d.month == Today.month and d.year == Today.year:
            month_end_dates.append(d.date())
        else:
            d_ = d.date()
            next_month = d_.replace(day=28) + timedelta(days=4) 
            last_day_month = next_month - timedelta(days=next_month.day)
            month_end_dates.append(last_day_month)
    df_dates[newColumnName] = month_end_dates
    
    df_merge = df.merge(df_dates, left_on = 'Date', right_on = 'TimeStamps', how = 'left')
    if deleteOldColumn == True:
        df_merge = df_merge.drop(columns = [oldColumnName, 'TimeStamps'])
    else:
        df_merge = df_merge.drop(columns = 'TimeStamps')

    return df_merge

def get_Snowflake_Data(table, columns, f_syms_list, fromDate):
    if columns == "ALL": 
        query = """select * """
    else:
        query = """select {} """.format(columns)
    query = query.replace("""'""",'')
    query = query.replace('(','')
    query = query.replace(')','')
    query = query + """ from QUANT.WORKING.""" + table
    query = query + " where FSYM_REGIONAL_ID IN {}".format(f_syms_list)
    query = query + f" AND DATA_DATE >= '{fromDate}'"
     
    query = query + """;"""
    query = query.replace('[','(')
    query = query.replace(']',')')
    query_results = db.getData(query)
    
    return query_results
  
def add_YearMonth_Column(df, date_column_name):
    df = df.assign(YearMonth = lambda x: pd.to_datetime(df[date_column_name]).dt.strftime("%Y%m"))
    return df

def check_For_Duplicates(df_to_check, df_name):
        
    c = df_to_check
    if 'DATE' in c.columns:
        col='DATE'
    else:
        col='DATA_DATE'
    check = c.copy().filter(items = [col, 'FSYM_REGIONAL_ID'])
    check[col] = pd.to_datetime(check[col])
    check = check.assign(YearMonth = lambda x: check[col].dt.strftime("%Y%m")).astype(str)
    check['dist'] = (check['FSYM_REGIONAL_ID']+" "+check['YearMonth'])
    check = check.drop(columns = [col])
    check['duplicated'] = check.filter(items = ['dist']).duplicated()
    check = check.loc[check["duplicated"] == True]
    
    number_of_duplicates = check['duplicated'].shape[0]
    duplicates_list = check['dist'].unique().tolist()
    
    print("There are " + str(number_of_duplicates) + " Security / YearMonth duplicates in the " + df_name + " dataframe.")
    
    if number_of_duplicates > 10:
        print ("10 examples are:")
        for i in range(0,10):
            print(duplicates_list[i])
    else:
        if number_of_duplicates > 0:
            print ("Here they are:")
            for i in range(0,number_of_duplicates):
                print(duplicates_list[i])
        
    return True
  
def organise_returns_df(returns_, percentage_required):
    
    returns_['Return'] = returns_['Return']-1
    returns_p = returns_.pivot(index = 'DATA_DATE', columns = 'FSYM_REGIONAL_ID', values = 'Return')
    returns_p = returns_p.sort_values(by = 'DATA_DATE')
    
    drop_list = []
    max_na = int(returns_p.shape[0] * (1-percentage_required))
    
    for c in returns_p.columns:
        if returns_p[c].isna().sum() > max_na:
            drop_list.append(c)
    
    returns_p_trim = returns_p.drop(columns = drop_list)
    
    return returns_p_trim

def fill_recent_months(prices_con_est_df):
    cols = prices_con_est_df.columns
        
    for i in range(0, prices_con_est_df.shape[0]):
        print(type(prices_con_est_df['REPORTING_FREQ'].iloc[i]))
        if isinstance(prices_con_est_df['REPORTING_FREQ'].iloc[i], float) == True:
            print("true")
            if prices_con_est_df['FSYM_REGIONAL_ID'].iloc[i] == prices_con_est_df['FSYM_REGIONAL_ID'].iloc[i-1]:
                for c in range(prices_con_est_df.shape[1]):
                    if math.isnan(prices_con_est_df.iloc[i, c]) == True:
                        prices_con_est_df.at[i,c] = prices_con_est_df.iloc[i-1,c]

def get_index_return_data(index_ids_scope, base_date):
    """
    Retrieves and processes index return data from a Snowflake database.

    Args:
    index_ids_scope (list): A list of index IDs to filter the data.
    base_date (str): The base date from which to fetch data, in the format 'YYYY-MM-DD'.

    Returns:
    pandas.DataFrame: A DataFrame containing processed index return data, including columns:
        - 'DATA_DATE': Date of the data point.
        - 'INDEX_ID': ID of the index.
        - 'D_RETURN_LOCAL': Local currency return for the index.
        - 'D_RETURN_INDEX_LOCAL': Cumulative local currency return for the index.
        - 'D_RETURN_INDEX_USD': Cumulative USD currency return for the index.
        - 'D_RETURN_INDEX_EUR': Cumulative EUR currency return for the index.

    This function connects to a Snowflake database, retrieves index return data, performs currency conversion,
    and calculates cumulative return index. The resulting DataFrame is filtered and returned.

    Note:
    - Requires a Snowflake connection and relevant configurations.
    - Ensure that the required Snowflake connector and pandas libraries are installed.
    """

    #### Convert list to tuple for fstring
    index_ids_scope = tuple(list(index_ids_scope))
    #### Create snowflake connection
    ctx = snowflake.connector.connect(user=config.user, password=config.password, account=config.account)
    #### Get Index returns and index ref table from snowflake
    Index_Rets=pd.read_sql(f"""SELECT * FROM QUANT.WORKING.DATA_INDICES WHERE DATA_DATE >= '{base_date}' 
                           AND INDEX_ID IN {index_ids_scope}""", ctx)
    Index_Ref=pd.read_sql(f"""SELECT * FROM QUANT.WORKING.REF_INDICES WHERE INDEX_ID IN {index_ids_scope}""", ctx)

    #### unique local currencies of the indices
    ccy_to_filter = tuple(Index_Ref['CURRENCY'].unique().tolist())
    #### FX rate to convert to EUR
    FX = pd.read_sql(f"""SELECT ISO_CURRENCY AS CURRENCY, EXCH_DATE AS DATA_DATE, EXCH_RATE_USD, EXCH_RATE_PER_USD FROM QUANT.DATA.ECON_FX_RATES_USD
                    WHERE EXCH_DATE >= '{base_date}' 
                    AND ISO_CURRENCY IN {ccy_to_filter}
                    ORDER BY CURRENCY, DATA_DATE""", ctx)
    

    FX_EUR = FX.query("CURRENCY == 'EUR'")

    #### Join everything together
    Index_Full = (Index_Rets
                .merge(Index_Ref[['INDEX_ID', 'CURRENCY']], on='INDEX_ID', how='left')
                .merge(FX[['CURRENCY', 'DATA_DATE', 'EXCH_RATE_USD']], on=['CURRENCY', 'DATA_DATE'], how='left')
                .merge(FX_EUR[['DATA_DATE', 'EXCH_RATE_PER_USD']], on=['DATA_DATE'], how='left')
                )

    #### Sort values and calculate cumulative returns
    Index_Full = Index_Full.sort_values(by=['INDEX_ID', 'DATA_DATE'], ascending=True)
    Index_Full['D_RETURN_INDEX_LOCAL'] = Index_Full.groupby('INDEX_ID')['D_RETURN_LOCAL'].transform(lambda x: 100 * np.cumprod(1 + x))

    #### Convert to EUR and remove extra columns
    Index_Full['EXCH_RATE_USD']=np.where(Index_Full.CURRENCY == 'USD', 1, Index_Full.EXCH_RATE_USD)
    Index_Full['EXCH_RATE_USD']=np.where(Index_Full.CURRENCY == 'EUR', 1, Index_Full.EXCH_RATE_USD)
    Index_Full['EXCH_RATE_PER_USD']=np.where(Index_Full.CURRENCY == 'EUR', 1, Index_Full.EXCH_RATE_PER_USD)
    Index_Full['D_RETURN_INDEX_USD'] = Index_Full['D_RETURN_INDEX_LOCAL']*Index_Full['EXCH_RATE_USD']
    Index_Full['D_RETURN_INDEX_EUR'] = Index_Full['D_RETURN_INDEX_USD']*Index_Full['EXCH_RATE_PER_USD']
    Index_Full = Index_Full.filter(['DATA_DATE', 'INDEX_ID', 'CURRENCY', 'D_RETURN_LOCAL', 'D_RETURN_INDEX_LOCAL', 'D_RETURN_INDEX_USD', 'D_RETURN_INDEX_EUR'])


    return Index_Full