#%%
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
import git
# def add_directories_to_sys_path():
#     """
#     Add a list of directories to the sys.path for importing modules.

#     This function figures out the list of folders in the git repo and appends each directory to the
#     sys.path, making it possible to import modules from those directories.

#     """
#     # Open the Git repository in the current directory or its parent directories
#     repo = git.Repo('.', search_parent_directories=True)

#     # Get the root directory of the working tree
#     working_tree_dir = repo.working_tree_dir

#     # Use os.listdir() to list all files and directories in the working tree
#     contents = os.listdir(working_tree_dir)

#     # Filter out only the directories that do not have a dot before the name
#     directories = [item for item in contents if os.path.isdir(os.path.join(working_tree_dir, item)) and not item.startswith('.')]

#     # Now 'directories' contains a list of all non-hidden directories in the Git repository
#     ###print(directories)

#     for directory in directories:
#         nth_dir = working_tree_dir + '\\' + directory
#         ##print(nth_dir)
#         sys.path.append(nth_dir)

# add_directories_to_sys_path()
from create_index_blends import CreateQpsBlends
# from Utility_functions import *
# new class to test out pulling benchmark data in different waterfall scenarios
class GetBenchmarks:

    def __init__(self, connection_dict):
        """
        Initialize the GetBenchmarks class.

        This class is responsible for retrieving benchmark data from the database.
        It connects to the database using the provided connection dictionary and sets up the necessary parameters.  
        """

        self.connection_dict = connection_dict
        self.ctx = connection_dict['default_snowflake_connection']
        self.conn = connection_dict['EDW_connection']
        self.today = datetime.today()
        self.today = self.today.strftime('%Y-%m-%d')
        self.portfolio_map = None
        self.rimes_to_msci_map = None

    # get quant strategy mapping
    def get_portfolio_map(self, representative_portfolios_only=True):

        """
        Retrieve the portfolio map from the database.
        This method queries the database to get the portfolio map, which includes information about
        representative portfolios and their associated RIMES blend IDs.

        Parameters:
            representative_portfolios_only (bool): If True, only retrieve representative portfolios.
                                                   Defaults to True.

        Returns:
            pd.DataFrame: DataFrame containing the portfolio map.
        """

        if representative_portfolios_only == True:
            rep_flag = True
        else:
            rep_flag = False

        # Query to get the portfolio map
        portfolio_map_query = f"""
        SELECT *
        FROM QUANT.WORKING.REF_PORTFOLIOS
        WHERE IS_REPRESENTATIVE = {rep_flag}
        """
        
        # Execute the query and get the result
        portfolio_map = pd.read_sql(portfolio_map_query, con=self.ctx)

        self.portfolio_map = portfolio_map
        
        return portfolio_map
    
    # get rimes to MSCI Code mapping
    def get_rimes_to_msci_map(self, filter_rimes_codes=None, keep_only_portfolio_bmks=False):
        """
        Retrieve the mapping between RIMES and MSCI from the database.

        Returns:
            pd.DataFrame: DataFrame containing the mapping between RIMES and MSCI.
        """
        
        # Query to get the mapping between RIMES and MSCI
        rimes_to_msci_query = """SELECT RIMES_BLEND_ID AS INDEX_ID, 
                                 WEIGHT AS INDEX_CONSTITUENT_WGT, 
                                 MSCI_INDEX_CODE AS MSCI_INDEX_CODE
                                 FROM QUANT.REFERENCES.RIMES_MSCI_INDEX"""
        
        # Execute the query and get the result
        rimes_to_msci_map = pd.read_sql(rimes_to_msci_query, con=self.ctx)

        # If filter_index_codes is provided, filter the DataFrame
        if filter_rimes_codes is not None:
            rimes_to_msci_map = rimes_to_msci_map.query("INDEX_ID == @filter_rimes_codes")

        # Filter the rimes_to_msci_map to keep only the blends that are in the portfolio map
        # this is useful in case the user wants to get only the blends that are mapped to the live portfolios
        if keep_only_portfolio_bmks:

            if self.portfolio_map is not None:
                portfolio_blends = self.portfolio_map['RIMES_BLEND_ID'].unique().tolist()
                rimes_to_msci_map = rimes_to_msci_map.query("INDEX_ID in @portfolio_blends")

        self.rimes_to_msci_map = rimes_to_msci_map
        
        return rimes_to_msci_map

    # define function to pull data from rimes
    def get_benchmark_data_rimes(self, input_date=None, rimes_bmk_codes=None, optimisation=False, historic_monthly=False, historic_daily=False, take_previous_available=False, end_date=None):
        """
        Retrieve benchmark holdings from the MED_EDW database for a given date.

        If the optimisation flag is set to True, the function will fetch data only for the provided date.
        Otherwise, it will attempt to fetch data for the given date and, if unavailable, will fall back 
        to the latest available date.

        Parameters:
            input_date (str): The date for which the benchmark holdings are to be fetched.
            params_dict_dict (dict): A dictionary containing 'BMKS', which is expected to have 
                                     benchmark codes as values.
            rimes_bmk_codes: list of rimes codes, in case the user wants to specify custom list.
            optimisation (bool, optional): A flag indicating whether the function should fetch 
                                           data strictly for the input date. Defaults to False.
            historic_monthly (bool, optional): Whether to fetch monthly historical data. Defaults to False.
            historic_daily (bool, optional): Whether to fetch daily historical data. Defaults to False.
            take_previous_available (bool, optional): Whether to take the previous available date if data is missing. Defaults to False.
            end_date (str, optional): The end date for fetching historical data. Defaults to None.

        Returns:
            pd.DataFrame: A dataframe with details on benchmark holdings including index symbol, ISIN, security weight, 
                          security name, Bloomberg ticker, GICS sector details, and valuation date. The security weight 
                          is presented in percentage terms.
        """

        bmk_df = self.portfolio_map.copy()
        bmk_df = bmk_df[['RIMES_BLEND_ID', 'BENCHMARK']]
        bmk_df = bmk_df.rename(columns={'RIMES_BLEND_ID': 'INDEX_SYMBOL', 'BENCHMARK': 'INDEX_NAME'})
        bmk_df = bmk_df.drop_duplicates()
        bmk_codes = self.rimes_to_msci_map['INDEX_ID'].unique().tolist()

        if len(bmk_codes) > 1:
            bmk_codes_tuple = tuple(bmk_codes)
        else:
            bmk_codes_tuple = f"('{bmk_codes[0]}')"

        if rimes_bmk_codes is not None:
            if len(rimes_bmk_codes) > 1:
                bmk_codes = rimes_bmk_codes
                bmk_codes_tuple = tuple(bmk_codes)
            else:
                bmk_codes = f"('{rimes_bmk_codes[0]}')"
                bmk_codes_tuple = bmk_codes

        if optimisation:
            # If optimisation flag is True, only get data for input_date
            query = f"""
            SELECT A.INDEX_SYMBOL, A.ISIN, A.security_weight, A.Security_name, A.BLOOMBERG_TICKER, A.SEDOL, A.ISSUER_CODE,
            A.CUSIP, A.SECURITY_COUNTRY_CODE as COUNTRY, A.SECTOR_LABEL_LEVEL1 as GICS_SECTOR, 
            A.SECTOR_LABEL_LEVEL2 as GICS_INDUSTRY_GROUP, A.SECTOR_LABEL_LEVEL3 as GICS_INDUSTRY, 
            A.SECTOR_LABEL_LEVEL4 as GICS_SUB_INDUSTRY, A.VALUATION_DATE, A.SECURITY_PRICE as SECURITY_PRICE, A.SECURITY_CCY_CODE as SECURITY_CCY_CODE
            FROM [MED_EDW].[rimes].[benchmark] as A
            WHERE A.INDEX_SYMBOL IN {bmk_codes_tuple} AND A.VALUATION_DATE = '{input_date}'
            """

        elif historic_monthly==False and historic_daily==False:
            # If optimisation flag is False, fall back to the original query that retrieves the latest date
            # Query modified to accept an input date and to fall back to the maximum available date if there's no data for the input date
            if take_previous_available==True:
                query = f"""
                    DECLARE @input_date DATE = '{input_date}';
                    
                    WITH latest_date AS (
                    SELECT INDEX_SYMBOL, 
                    CASE 
                        WHEN COUNT(DISTINCT CASE WHEN VALUATION_DATE = @input_date THEN VALUATION_DATE END) > 0 
                        THEN @input_date 
                        ELSE MAX(VALUATION_DATE) 
                    END AS max_valuation_date
                    FROM [MED_EDW].[rimes].[timeseries]
                    WHERE INDEX_SYMBOL IN {bmk_codes_tuple}
                    AND VALUATION_DATE < @input_date
                    GROUP BY INDEX_SYMBOL
                    )
                    SELECT A.INDEX_SYMBOL, A.ISIN, A.security_weight, A.Security_name, A.BLOOMBERG_TICKER, A.SEDOL, A.CUSIP, A.SECURITY_COUNTRY_CODE as COUNTRY,
                    A.SECTOR_LABEL_LEVEL1 as GICS_SECTOR, A.SECTOR_LABEL_LEVEL2 as GICS_INDUSTRY_GROUP, A.SECTOR_LABEL_LEVEL3 as GICS_INDUSTRY, A.SECTOR_LABEL_LEVEL4 as GICS_SUB_INDUSTRY, A.VALUATION_DATE, A.SECURITY_PRICE as SECURITY_PRICE, A.SECURITY_CCY_CODE as SECURITY_CCY_CODE
                    FROM [MED_EDW].[rimes].[benchmark] as A
                    JOIN latest_date LD on A.INDEX_SYMBOL = LD.INDEX_SYMBOL AND A.VALUATION_DATE = LD.max_valuation_date;
                    """
                
            else:
            # If optimisation flag is False, fall back to the original query that retrieves the latest date
            # Query modified to accept an input date and to fall back to the maximum available date if there's no data for the input date
                query = f"""
                    DECLARE @input_date DATE = '{input_date}';
                    
                    WITH latest_date AS (
                    SELECT INDEX_SYMBOL, 
                    CASE 
                        WHEN COUNT(DISTINCT CASE WHEN VALUATION_DATE = @input_date THEN VALUATION_DATE END) > 0 
                        THEN @input_date 
                        ELSE MAX(VALUATION_DATE) 
                    END AS max_valuation_date
                    FROM [MED_EDW].[rimes].[timeseries]
                    WHERE INDEX_SYMBOL IN {bmk_codes_tuple}
                    GROUP BY INDEX_SYMBOL
                    )
                    SELECT A.INDEX_SYMBOL, A.ISIN, A.security_weight, A.Security_name, A.BLOOMBERG_TICKER, A.SEDOL, A.CUSIP, A.SECURITY_COUNTRY_CODE as COUNTRY,
                    A.SECTOR_LABEL_LEVEL1 as GICS_SECTOR, A.SECTOR_LABEL_LEVEL2 as GICS_INDUSTRY_GROUP, A.SECTOR_LABEL_LEVEL3 as GICS_INDUSTRY, A.SECTOR_LABEL_LEVEL4 as GICS_SUB_INDUSTRY, A.VALUATION_DATE, A.SECURITY_PRICE as SECURITY_PRICE, A.SECURITY_CCY_CODE as SECURITY_CCY_CODE
                    FROM [MED_EDW].[rimes].[benchmark] as A
                    JOIN latest_date LD on A.INDEX_SYMBOL = LD.INDEX_SYMBOL AND A.VALUATION_DATE = LD.max_valuation_date;
                    """
                
            
        elif historic_monthly==True:
            # Get monthly historical data
            query = f"""WITH MaxDatePerSymbol AS (
                    SELECT
                    INDEX_SYMBOL,
                    MAX(VALUATION_DATE) AS max_date_month
                    FROM [MED_EDW].[rimes].[timeseries]
                    WHERE INDEX_SYMBOL IN {bmk_codes_tuple}
                    AND VALUATION_DATE > '{input_date}'
                    GROUP BY
                    INDEX_SYMBOL,
                    FORMAT(VALUATION_DATE, 'yyyy-MM')
                )
                SELECT
                    A.INDEX_SYMBOL,
                    A.ISIN,
                    A.security_weight,
                    A.Security_name,
                    A.BLOOMBERG_TICKER,
                    A.SEDOL,
                    A.CUSIP,
                    A.SECURITY_COUNTRY_CODE AS COUNTRY,
                    A.SECTOR_LABEL_LEVEL1 AS GICS_SECTOR,
                    A.SECTOR_LABEL_LEVEL2 AS GICS_INDUSTRY_GROUP,
                    A.SECTOR_LABEL_LEVEL3 AS GICS_INDUSTRY,
                    A.SECTOR_LABEL_LEVEL4 AS GICS_SUB_INDUSTRY,
                    A.VALUATION_DATE AS DATA_DATE
                FROM [MED_EDW].[rimes].[benchmark] AS A
                INNER JOIN MaxDatePerSymbol AS M ON A.INDEX_SYMBOL = M.INDEX_SYMBOL AND A.VALUATION_DATE=M.max_date_month
                WHERE A.INDEX_SYMBOL IN {bmk_codes_tuple}"""
        
        elif historic_daily==True and end_date is None:
            # Get daily historical up to most recent date
            query = f"""SELECT
                    A.INDEX_SYMBOL,
                    A.ISIN,
                    A.security_weight,
                    A.Security_name,
                    A.BLOOMBERG_TICKER,
                    A.SEDOL,
                    A.CUSIP,
                    A.SECURITY_COUNTRY_CODE AS COUNTRY,
                    A.SECTOR_LABEL_LEVEL1 AS GICS_SECTOR,
                    A.SECTOR_LABEL_LEVEL2 AS GICS_INDUSTRY_GROUP,
                    A.SECTOR_LABEL_LEVEL3 AS GICS_INDUSTRY,
                    A.SECTOR_LABEL_LEVEL4 AS GICS_SUB_INDUSTRY,
                    A.VALUATION_DATE AS DATA_DATE
                FROM [MED_EDW].[rimes].[benchmark] AS A
                WHERE A.INDEX_SYMBOL IN {bmk_codes_tuple}
                AND VALUATION_DATE >= '{input_date}'"""
                
        elif historic_daily==True and end_date is not None:
            # Get daily historical up until user specified date
            query = f"""SELECT
                    A.INDEX_SYMBOL,
                    A.ISIN,
                    A.security_weight,
                    A.Security_name,
                    A.BLOOMBERG_TICKER,
                    A.SEDOL,
                    A.CUSIP,
                    A.SECURITY_COUNTRY_CODE AS COUNTRY,
                    A.SECTOR_LABEL_LEVEL1 AS GICS_SECTOR,
                    A.SECTOR_LABEL_LEVEL2 AS GICS_INDUSTRY_GROUP,
                    A.SECTOR_LABEL_LEVEL3 AS GICS_INDUSTRY,
                    A.SECTOR_LABEL_LEVEL4 AS GICS_SUB_INDUSTRY,
                    A.VALUATION_DATE AS DATA_DATE
                FROM [MED_EDW].[rimes].[benchmark] AS A
                WHERE A.INDEX_SYMBOL IN {bmk_codes_tuple}
                AND VALUATION_DATE >= '{input_date}'
                AND VALUATION_DATE <= '{end_date}'
                """

        # Execute the query and fetch the data
        bmk_data = pd.read_sql(query, con=self.conn)

        # # Reverse the dictionary
        # index_name_dict = {v: k for k, v in bmks_dict.items()}

        # # Map the index name to the index symbol
        # bmk_data['INDEX_NAME'] = bmk_data['INDEX_SYMBOL'].map(index_name_dict)
        bmk_data = bmk_data.merge(bmk_df, on='INDEX_SYMBOL', how='left')

        # Multiply the security weight by 100 to get the weight in percentage terms
        bmk_data['security_weight'] = bmk_data['security_weight'] * 100

        bmk_data = bmk_data.query("security_weight > 0")

        return bmk_data
    
    # define function to rename columns to align with RIMES
    def rename_msci_columns(self, df):

        """
        Rename columns in the DataFrame to align with RIMES naming conventions.

        Parameters:
            df (pd.DataFrame): The DataFrame to rename columns for.

        Returns:
            pd.DataFrame: The DataFrame with renamed columns.
        """
        
        # Rename columns to align with RIMES
        df.rename(columns={'SECURITY_NAME':'Security_name', 'SECURITY_ISIN':'ISIN', 'BB_TICKER':'BLOOMBERG_TICKER', 
                           'SECURITY_SECTOR':'GICS_SECTOR', 'ISO_COUNTRY_SYMBOL':'COUNTRY', 'AS_OF_DATE':'VALUATION_DATE',
                           'INDEX_ID':'INDEX_SYMBOL', 'WGT':'security_weight', 'MSCI_ISSUER_CODE': 'ISSUER_CODE', 'PRICE':'SECURITY_PRICE',
                           'GICS_IND':'GICS_INDUSTRY', 'GICS_IND_GRP':'GICS_INDUSTRY_GROUP', 'GICS_SUB_IND':'GICS_SUB_INDUSTRY',
                           'PRICE_ISO_CURRENCY_SYMBOL':'SECURITY_CCY_CODE'}, inplace=True)
        
        return df

    # define function to pull data from MSCI
    def get_benchmark_data_msci(self, input_date=None, msci_index_codes=None, optimisation=False, historic_monthly=False, historic_daily=False, end_date=None, get_1day_proforma=True):
        """
        Retrieve benchmark holdings from the MSCI database for a given date.
        If the optimisation flag is set to True, the function will fetch data only for the provided date.
        Otherwise, it will attempt to fetch data for the given date and, if unavailable, will fall back
        to the latest available date.
        Parameters:
            input_date (str): The date for which the benchmark holdings are to be fetched.
            msci_index_codes (list, optional): List of MSCI index codes to filter the data.
            optimisation (bool, optional): A flag indicating whether the function should fetch
                                           data strictly for the input date. Defaults to False.
            historic_monthly (bool, optional): Whether to fetch monthly historical data. Defaults to False.
            historic_daily (bool, optional): Whether to fetch daily historical data. Defaults to False.
            take_previous_available (bool, optional): Whether to take the previous available date if data is missing. Defaults to False.
            end_date (str, optional): The end date for fetching historical data. Defaults to None
        Returns:
            pd.DataFrame: A dataframe with details on benchmark holdings including index symbol, ISIN,
                            security weight, security name, Bloomberg ticker, GICS sector details, and valuation date.
        """

        # get the rimes to msci mapping
        if msci_index_codes is not None:
            rimes_msci_map = self.rimes_to_msci_map.query("RIMES_BLEND_ID == @msci_index_codes")
        else:
            rimes_msci_map = self.rimes_to_msci_map
        
        # define instance of the CreateQpsBlends class, this is used to create blended indexes and get msci data
        cb = CreateQpsBlends(blend_scope_file=rimes_msci_map, connection_dict=self.connection_dict)
        self.cb_instance = cb

        # If end_date is not provided, set it to today's date
        if end_date is None:
            end_date = self.today

        # if input_date is None, set it to last available date in MSCI database
        if input_date is None:
            last_avail_date = pd.read_sql(f"SELECT MAX(CALC_DATE) AS LAST_DATE FROM MSCI.INDEX.SECURITY WHERE CALC_DATE < '{end_date}'", con=self.ctx)
            input_date = last_avail_date['LAST_DATE'].values[0]

        # If optimisation flag is True, only get data for input_date, if not available then it's an issue in the msci database
        if optimisation == True:
            const_data = cb.get_msci_index_constituents_data(min_date=input_date, max_date=input_date, get_month_end_dates=False, get_1day_proforma=get_1day_proforma)
            sec_map = cb.get_msci_security_map(get_month_end_dates=False, add_metadata=True)
            blended_index_df, wgt_check = cb.create_blended_index()

            # rename columns to align with rimes
            blended_index_df = self.rename_msci_columns(blended_index_df)

        elif historic_monthly==False and historic_daily==False:
            # If optimisation flag is False, fall back to the original query that retrieves the latest date before the input date
            last_date_df = cb.get_last_index_constituent_available_date(less_than_date=input_date, msci_index_codes=['990100'])
            last_date = last_date_df['AS_OF_DATE'].values[0]
            const_data = cb.get_msci_index_constituents_data(min_date=last_date, max_date=last_date, get_month_end_dates=False, get_1day_proforma=get_1day_proforma)
            sec_map = cb.get_msci_security_map(get_month_end_dates=False, add_metadata=True)
            blended_index_df, wgt_check = cb.create_blended_index()

            # rename columns to align with rimes
            blended_index_df = self.rename_msci_columns(blended_index_df)

        elif historic_monthly==True:
            # Get monthly historical data
            month_end_dates = cb.get_month_end_dates(min_date=input_date, max_date=end_date, include_last_bd=True)
            const_data = cb.get_msci_index_constituents_data(min_date=input_date, max_date=end_date, get_month_end_dates=True, get_1day_proforma=get_1day_proforma)
            sec_map = cb.get_msci_security_map(get_month_end_dates=True, add_metadata=True)
            blended_index_df, wgt_check = cb.create_blended_index()

            # rename columns to align with rimes
            blended_index_df = self.rename_msci_columns(blended_index_df)

        elif historic_daily==True:
            # Get daily historical up to most recent date
            const_data = cb.get_msci_index_constituents_data(min_date=input_date, max_date=end_date, get_month_end_dates=False, get_1day_proforma=get_1day_proforma)
            sec_map = cb.get_msci_security_map(get_month_end_dates=False, add_metadata=True)
            blended_index_df, wgt_check = cb.create_blended_index()

            # rename columns to align with rimes
            blended_index_df = self.rename_msci_columns(blended_index_df)


        return blended_index_df

    # define function to get benchmark data for optimisation purposes
    def get_benchmark_data(self, date=None, waterfall=None, optimisation=False, historic_monthly=False, historic_daily=False, end_date=None, get_1day_proforma=True, keep_only_portfolio_bmks=False):
        """
        Retrieves benchmark data for optimisation purposes for a given date.
        Allows the user to specify the order of data sources to try via the waterfall parameter.
        Args:
            date (datetime.date or str, optional): The date for which to retrieve benchmark data.
            waterfall (list of str, optional): List specifying the order of sources to try, e.g., ['rimes', 'msci'].
                Defaults to ['rimes', 'msci'].
            optimisation (bool, optional): If True, retrieves data strictly for the input date.
            historic_monthly (bool, optional): If True, retrieves monthly historical data.
            historic_daily (bool, optional): If True, retrieves daily historical data.
            end_date (str, optional): The end date for fetching historical data. Defaults to None.
            get_1day_proforma (bool, optional): If True, retrieves 1-day proforma data - applies only to MSCI. Defaults to True.
            keep_only_portfolio_bmks (bool, optional): If True, filters the benchmarks to keep only those that are in the portfolio map.
        Returns:
            DataFrame: The benchmark data retrieved from the first available source in the waterfall.
        """

        # waterfall is a list of sources to try in order, default is RIMES then MSCI
        if waterfall is None:
            waterfall = ['msci', 'rimes']

        # if date is None, use today's date
        if self.portfolio_map is None:
            self.get_portfolio_map()

        # if rimes_to_msci_map is None, get the mapping
        if self.rimes_to_msci_map is None:
            self.get_rimes_to_msci_map(keep_only_portfolio_bmks=keep_only_portfolio_bmks)

        # figure out the waterfall order and query the data sources in that order
        for source in waterfall:
            if source.lower() == 'rimes':
                print(f"Trying to get benchmark data from RIMES")
                # Get benchmark data from RIMES
                bmk_data = self.get_benchmark_data_rimes(input_date=date, 
                                                         optimisation=optimisation,
                                                          historic_monthly=historic_monthly,
                                                          historic_daily=historic_daily, 
                                                          end_date=end_date)
                if len(bmk_data) > 0:
                    print("Data found for RIMES, using that")
                    return bmk_data
                else:
                    print("No data found for RIMES, trying next source...")
            elif source.lower() == 'msci':
                print(f"Trying to get benchmark data from MSCI")
                # Get benchmark data from MSCI
                bmk_data = self.get_benchmark_data_msci(input_date=date, 
                                                        optimisation=optimisation,
                                                        historic_monthly=historic_monthly,
                                                        historic_daily=historic_daily, 
                                                        end_date=end_date,
                                                        get_1day_proforma=get_1day_proforma)
                if len(bmk_data) > 0:
                    print("Data found for MSCI, using that")
                    return bmk_data
                else:
                    print("No data found for MSCI, trying next source...")
            else:
                print(f"Unknown source '{source}' specified in waterfall, skipping...")

        print("No data found in any specified source.")
        return None
     
#%%
# example usage
# firt get the connection dictionary, get the portfolio and rimes to msci mapping
# then get the benchmark data for a specific date, you can use the rimes or msci function direcrly or
# use the get_optimisation_data method which will try to get data from rimes first and then fall back to msci if no data is found
# if __name__ == "__main__":

# connection_dict, params_dict_dict = initialize_env_and_db_connections()
# ctx = connection_dict['default_snowflake_connection']
# conn = connection_dict['EDW_connection']

# Create an instance of GetBenchmarks
# gb = GetBenchmarks(connection_dict)

# # Get portfolio map
# portfolio_map = gb.get_portfolio_map()
# print(portfolio_map)

# # Get RIMES to MSCI mapping
# rimes_to_msci_map = gb.get_rimes_to_msci_map()
# print(rimes_to_msci_map)

# Get benchmark data for a specific date
# benchmark_data = gb.get_benchmark_data(date='2025-07-01', waterfall=['msci', 'rimes'])
# print(benchmark_data)

# filt_fund_codes = ['WRLD.R', 'BLEND218', 'BLEND25', 'BLEND24']
# filter_funds = benchmark_data.query("INDEX_SYMBOL == @filt_fund_codes")
# print(filter_funds['INDEX_SYMBOL'].unique())

# count = filter_funds['INDEX_SYMBOL'].value_counts()
# sum_tot = filter_funds['security_weight'].sum()

# filter_funds.to_pickle('benchmark_data_2025_07_01.pkl')
# %%
