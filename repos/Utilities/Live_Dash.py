
## Created by Cillian, Fabio & ..........................................................................................................................................................................Ellen

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 15:51:57 2023

@author: Ellen.Hynes
"""

import pandas as pd
from datetime import datetime
import numpy as np 
import plotly
import plotly.express as px
import plotly.graph_objects as go
import win32com.client as win32
import datetime as dt
import snowflake.connector
import os
import sys
import pythoncom
import pyodbc
import glob
from datetime import date
from dash.dash_table.Format import Format
import plotly.io as pio
import time
from xbbg import blp
import os.path
import os
import dash
from dash import html
from dash import dcc
from dash import dash_table, ctx
#rom brinson_attribution import attribution
from datetime import timedelta 
import dash_mantine_components as dmc
import traceback
from dash.exceptions import PreventUpdate
import math
import json 
from pandas.tseries.offsets import BDay
import datetime
from UpcomingEarningsCheck import *
import pretty_html_table


###snowflake database connectors#####################

ctx = snowflake.connector.connect(user="QUANT_PYTHON_ADMIN", password='u8dcHBmHm5eJMaUv', account='mediolanum-snowflake.privatelink')
conn = pyodbc.connect('Driver={SQL Server};' 'Server=euncsqldb01.c.prv.mediolanum.ie;' 'Database=MED_EDW;' 'Trusted_Connection=yes;')
ctx_fabio = snowflake.connector.connect(user="TEST_QUANT_PYTHON_ADMIN",
                                  role='TEST_MED_BUSINESS_ANALYST',
                                  warehouse='TEST_EDW_LOAD',
                                  password='cRbBumWy9k5ZYJSr', 
                                  account='mediolanum-snowflake.privatelink')


#colours########
mediolanum_blue = "#002A56"
mediolanum_light_blue = "#00BFFF"
mediolanum_white = "#FFFFFF"
mediolanum_turquoise = "#85D0CD"


#####conditional formatting####################



conditional_formatting_port_vs_bmk = [
    {
        'if': {'column_id': 'Global vs MSCI World', 'filter_query': '{Global vs MSCI World} > 0'},
        'backgroundColor': mediolanum_turquoise,
        'color': 'black'
    },
    {
        'if': {'column_id': 'Global vs MSCI World', 'filter_query': '{Global vs MSCI World} < 0'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },

    {
        'if': {'column_id': 'Eur vs MSCI Europe', 'filter_query': '{Eur vs MSCI Europe} > 0'},
        'backgroundColor': mediolanum_turquoise,
        'color': 'black'
    },
    {
        'if': {'column_id': 'Eur vs MSCI Europe', 'filter_query': '{Eur vs MSCI Europe} < 0'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },

    {
        'if': {'column_id': 'US vs MSCI US', 'filter_query': '{US vs MSCI US} > 0'},
        'backgroundColor': mediolanum_turquoise,
        'color': 'black'
    },
    {
        'if': {'column_id': 'US vs MSCI US', 'filter_query': '{US vs MSCI US} < 0'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },


]


# define the conditional formatting rules
conditional_formatting_companies_reporting = [
    {
        'if': {'column_id': 'European', 'filter_query': '{European} > 0.3'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },
    {
        'if': {'column_id': 'Global', 'filter_query': '{Global} > 0.3'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },
    {
        'if': {'column_id': 'US', 'filter_query': '{US} > 0.3'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },
    {
        'if': {'column_id': 'Ind & Mat', 'filter_query': '{Ind & Mat} > 0.3'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },



    {
        'if': {'column_id': 'Quality', 'filter_query': '{Quality} > 66'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },
    
    {
        'if': {'column_id': 'Quality', 'filter_query': '{Quality} < 33'},
        'backgroundColor': '#85D0CD',
        'color': 'black'
    },

    {
        'if': {'column_id': 'Growth', 'filter_query': '{Growth} > 66'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },
    
    {
        'if': {'column_id': 'Growth', 'filter_query': '{Growth} < 33'},
        'backgroundColor': '#85D0CD',
        'color': 'black'
    },

    {
        'if': {'column_id': 'Value', 'filter_query': '{Value} > 66'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },
    
    {
        'if': {'column_id': 'Value', 'filter_query': '{Value} < 33'},
        'backgroundColor': '#85D0CD',
        'color': 'black'
    },

    {
        'if': {'column_id': 'Value Rel', 'filter_query': '{Value Rel} > 66'},
        'backgroundColor': '#FFB6C1',
        'color': 'black'
    },
    {
        'if': {'column_id': 'Value Rel', 'filter_query': '{Value Rel} < 33'},
        'backgroundColor': '#85D0CD',
        'color': 'black'
    },
    {
        'if': {'column_id': 'Global_Delta', 'filter_query': '{Global_Delta} > 0'},
        'backgroundColor': 'orange',
        'color': 'black'
    }

]

###templates
# Get the 'plotly_dark' template
light_template = pio.templates['seaborn']

# Convert the template to a dictionary
template_dict = light_template

# Modify the font settings of the template dictionary
template_dict['layout']['font']['family'] = 'Mediolanum Sans'
template_dict['layout']['font']['color'] = '#002A56'
# Modify the font color of headings
template_dict['layout']['title']['font']['color'] = '#85D0CD'

# Register the new template with a new name
pio.templates['my_light_template'] = template_dict

# Set the default template for all plots
pio.templates.default = 'my_light_template'

#####paths########################################################################################################

username = os.getlogin()
path = f'C:\\Users\\{username}\\Source\Repos\\Investments-Quant\\Utilities'
os.chdir(path)
sys.path.append(path)


folders = ['Utilities', 'Ecosystem', 'Backtester']
for folder in folders:
    path_to_folders = os.path.join('C:\\Users\\' + os.getlogin() +'\\Source\\Repos\\Investments-Quant\\' + folder)
    if path_to_folders not in sys.path:
        print(path_to_folders)
        sys.path.append(path_to_folders)
        
################################################################################################

def process_data(df, groupby_col):
    factor_df = df.groupby([groupby_col]).count()
    factor_total = factor_df.iloc[:,0]
    factor_df = factor_df.div(factor_total, axis=0).mul(100).round(2)
    factor_df = 100 - factor_df
    factor_df = factor_df.T.reset_index()
    return factor_df

###############load in the ecosystem#########################################

# set the path to the folder
folder_path = 'Q:/Investment/Securities/Quant/Data/1. Ecosystem/4. Excel Master/'
all_files = sorted(glob.glob(folder_path + '*[!_JH].xlsx'), key=os.path.getmtime, reverse=True)

# iterate through the list of files and attempt to read each one
for file_path in all_files:
    try:
        # attempt to read the file
        current_ecosystem = pd.read_excel(file_path)
        print(file_path)
        print(current_ecosystem)
        break
    except PermissionError:
        # if a PermissionError is raised, continue to the next file
        continue
    
current_ecosystem_fin = current_ecosystem
###########################################

current_bmks = current_ecosystem[['ISIN', 'PROPER_NAME' , 'GICS Sector' , 'MSCI World' , 'MSCI Europe' , 'MSCI US', 'MSCI IND & MAT']]
current_bmks.columns = ['ISIN', 'SECURITY_NAME','GICS Sector','Global_Benchmark','EUR_Benchmark', 'US_Benchmark','Ind_Mat_Benchmark']
#current_bmks = current_bmks[current_bmks[['Global_Benchmark', 'EUR_Benchmark', 'US_Benchmark']].notna().any(axis=1)]
#current_bmks.iloc[:,-3:] = current_bmks.iloc[:,-3:]*100
current_bmks_port_vs_bmk = current_bmks.groupby('GICS Sector').sum()
current_bmks_port_vs_bmk = current_bmks_port_vs_bmk*100


sleeveMap = pd.read_excel('Q:/Investment/Securities/Quant/Implementation/6 - Fusion/quantMap.xlsx')
delCode = tuple(sleeveMap['DelCode'].apply(str).to_list())
checkMap = pd.read_excel('Q:/Investment/Securities/Quant/Implementation/6 - Fusion/quantMap.xlsx', sheet_name='checkMap')
checkCode = tuple(checkMap['DelCode'].apply(str).to_list())

fullCode = delCode + checkCode

query = f"""Select POSITION_DATE, 
fund_accounting_code,
fund_accounting_name,
INSTRUMENT_NAME, 
TICKER_INSTRUMENT_REFERENCE, 
ISIN_INSTRUMENT_REFERENCE, 
NUMBER_OF_SECURITIES, 
WEIGHT_IN_MANAGED_ACCOUNT_PCNT AS STRATEGY_WEIGHTING,
THEORETICAL as LAST_PRICE,
ISO_CURRENCY_CODE as CURRENCY,
COUNTRY_NAME as COUNTRY_OF_RISK
from TEST_MED_DATAHUB.atomic_warehouse.instrument a
JOIN TEST_MED_DATAHUB.atomic_warehouse.instrument_position b on a.instrument_id = b.instrument_id 
JOIN TEST_MED_DATAHUB.mdm_mdh.currency c on payment_currency_id = c.currency_id
join TEST_MED_DATAHUB.mdm_mdh.country d on d.country_id = a.country_of_risk_id
join TEST_MED_DATAHUB.mdm_mdh.managed_account e on e.managed_account_id = b.managed_account_id
where fund_accounting_code in {fullCode} 
AND NUMBER_OF_SECURITIES IS NOT NULL
AND STRATEGY_WEIGHTING IS NOT NULL
AND POSITION_DATE >= '2023-03-09'
Order by POSITION_DATE asc;;"""

universe = pd.read_sql(query, ctx_fabio)

########################################################################

test=universe.loc[universe['ISIN_INSTRUMENT_REFERENCE']=='GB00BM8PJY71']
z=test.loc[test['FUND_ACCOUNTING_CODE']=='711979']

quant = sleeveMap['DelCode'].astype(str).to_list()
equity = checkMap['DelCode'].astype(str).to_list()

universe.loc[universe['FUND_ACCOUNTING_CODE'].astype(str).isin(quant), 'FUND_ACCOUNTING_NAME'] = 'Quant - ' + universe['FUND_ACCOUNTING_NAME'].astype(str)
universe.loc[universe['FUND_ACCOUNTING_CODE'].astype(str).isin(equity), 'FUND_ACCOUNTING_NAME'] = 'Equity - ' + universe['FUND_ACCOUNTING_NAME'].astype(str)

universe_sleeve = universe.FUND_ACCOUNTING_NAME.unique()
universe_stock = universe.INSTRUMENT_NAME.unique()

###############load in the ecosystem#########################################
most_recent_date = max(universe.POSITION_DATE)
universe = universe[universe.POSITION_DATE == most_recent_date]


snowflake_ecosystem_trim = universe.filter(items = ['FUND_ACCOUNTING_NAME','INSTRUMENT_NAME','ISIN_INSTRUMENT_REFERENCE','STRATEGY_WEIGHTING'])
prts = ['Quant - Challenge European Equity','Quant - Challenge International Equity','Quant - Challenge North American Equity', 'Quant - Challenge Industrial and Material EQ Evo']
snowflake_ecosystem_trim = snowflake_ecosystem_trim.loc[snowflake_ecosystem_trim['FUND_ACCOUNTING_NAME'].isin(prts)]
snowflake_ecosystem_trim_piv = snowflake_ecosystem_trim.pivot_table(index = ['INSTRUMENT_NAME','ISIN_INSTRUMENT_REFERENCE'] , columns = 'FUND_ACCOUNTING_NAME', values = 'STRATEGY_WEIGHTING')
snowflake_ecosystem_trim_piv = snowflake_ecosystem_trim_piv.fillna(0)
snowflake_ecosystem_trim_piv = snowflake_ecosystem_trim_piv.reset_index()
col_order = ['ISIN_INSTRUMENT_REFERENCE','INSTRUMENT_NAME', 'Quant - Challenge International Equity','Quant - Challenge European Equity', 'Quant - Challenge North American Equity', 'Quant - Challenge Industrial and Material EQ Evo']
snowflake_ecosystem_trim_piv = snowflake_ecosystem_trim_piv.reindex(columns = col_order)
snowflake_ecosystem_trim_piv.columns = ['ISIN', 'SECURITY_NAME', 'Global_port', 'EUR_port', 'US_port','Ind_and_Mat']

current_ecosystem_trim = pd.merge(snowflake_ecosystem_trim_piv, current_bmks, on = 'ISIN')
current_ecosystem_trim = current_ecosystem_trim.filter(items = ['ISIN','SECURITY_NAME_y','Global_port','Global_Benchmark', 'EUR_port','EUR_Benchmark', 'US_port','US_Benchmark','Ind_and_Mat','Ind_Mat_Benchmark'])
current_ecosystem_trim.columns = ['ISIN', 'SECURITY_NAME', 'Global_port', 'Global_Benchmark', 'EUR_port', 'EUR_Benchmark', 'US_port', 'US_Benchmark','Ind_and_Mat','Ind_Mat_Benchmark']


current_ecosystem_trim_isins = list(current_ecosystem_trim['ISIN'])

model_query = """
SELECT U.PROPER_NAME, RM.MODEL_NAME, MAX(DF.DATA_DATE) AS LATEST_DATE , MAX(DF.MODEL_VALUE) AS MODEL_VALUE
FROM QUANT.WORKING.DATA_MODELS AS DF
LEFT JOIN QUANT.WORKING.REF_MODELS AS RM ON DF.MODEL_ID = RM.MODEL_ID
JOIN QUANT.WORKING.UNIVERSE AS U ON U.FSYM_REGIONAL_ID = DF.FSYM_REGIONAL_ID
WHERE U.ISIN IN ({})
GROUP BY U.PROPER_NAME, RM.MODEL_NAME
""".format(','.join("'" + isin + "'" for isin in current_ecosystem_trim_isins))

model_ranks_ = pd.read_sql(model_query, con=ctx)


model_ranks_piv = pd.pivot_table(model_ranks_, index = 'PROPER_NAME', columns = 'MODEL_NAME' , values= 'MODEL_VALUE' )
model_ranks_piv = model_ranks_piv.reset_index()
model_ranks_piv = model_ranks_piv.rename(columns={col: 'Rank_'+ col for col in model_ranks_piv.columns[1:]})
model_ranks_piv = model_ranks_piv.rename(columns={'PROPER_NAME':'SECURITY_NAME'})


current_ecosystem_trim_done = pd.merge(current_ecosystem_trim , model_ranks_piv , how = 'inner' )

#current_ecosystem_trim_done.columns = ['ISIN', 'SECURITY_NAME', 'Global_port', 'Global_Benchmark', 'EUR_port',
       #'EUR_Benchmark', 'US_port', 'US_Benchmark', 'Rank_Growth',
       #'Rank_Momentum', 'Rank_QCap', 'Rank_QSafe', 'Rank_QSecurity',
       #'Rank_QStability', 'Rank_QStrength', 'Rank_Quality', 'Rank_Value',
       #'Rank_Value Rel']

current_ecosystem_trim_done_isins = current_ecosystem_trim_done['ISIN'].tolist()
rbics_sect_q = """select ISIN, RBICS_ECONOMY from QUANT.WORKING.UNIVERSE
                  WHERE ISIN IN {}""".format(current_ecosystem_trim_done_isins)
                  
#rbics_sect_q = pd.read__sql(rbics_sect_q, ctx)
                  
                  
###flag table##########################################
current_ecosystem_trim_done['GLB_Selected'] = ''
current_ecosystem_trim_done['EUR_Selected'] = ''
current_ecosystem_trim_done['US_Selected'] = ''
current_ecosystem_trim_done['IND_MAT_Selected'] = ''
current_ecosystem_trim_done['Flag_1'] = 'NO'
current_ecosystem_trim_done['Flag_2'] = 'NO'


current_ecosystem_trim_done['GLB_Selected'] = np.where(current_ecosystem_trim_done['Global_Benchmark'] > 0, 'NO', '')
current_ecosystem_trim_done['GLB_Selected'] = np.where((current_ecosystem_trim_done['GLB_Selected'] == 'NO') & (current_ecosystem_trim_done['Global_port'] > 0), 'YES', current_ecosystem_trim_done['GLB_Selected'])

current_ecosystem_trim_done['US_Selected'] = np.where(current_ecosystem_trim_done['US_Benchmark'] > 0, 'NO', '')
current_ecosystem_trim_done['US_Selected'] = np.where((current_ecosystem_trim_done['US_Selected'] == 'NO') & (current_ecosystem_trim_done['US_port'] > 0), 'YES', current_ecosystem_trim_done['US_Selected'])

current_ecosystem_trim_done['EUR_Selected'] = np.where(current_ecosystem_trim_done['EUR_Benchmark'] > 0, 'NO', '')
current_ecosystem_trim_done['EUR_Selected'] = np.where((current_ecosystem_trim_done['EUR_Selected'] == 'NO') & (current_ecosystem_trim_done['EUR_port'] > 0), 'YES', current_ecosystem_trim_done['EUR_Selected'])

current_ecosystem_trim_done['IND_MAT_Selected'] = np.where(current_ecosystem_trim_done['Ind_Mat_Benchmark'] > 0, 'NO', '')
current_ecosystem_trim_done['IND_MAT_Selected'] = np.where((current_ecosystem_trim_done['IND_MAT_Selected'] == 'NO') & (current_ecosystem_trim_done['Ind_and_Mat'] > 0), 'YES', current_ecosystem_trim_done['IND_MAT_Selected'])


current_ecosystem_trim_done['Flag_1'] = np.where((current_ecosystem_trim_done['EUR_Selected'] == 'NO') & (current_ecosystem_trim_done['GLB_Selected'] == 'YES'), 'YES', 'NO')
current_ecosystem_trim_done['Flag_1'] = np.where((current_ecosystem_trim_done['US_Selected'] == 'NO') & (current_ecosystem_trim_done['GLB_Selected'] == 'YES'), 'YES', current_ecosystem_trim_done['Flag_1'])

current_ecosystem_trim_done['Flag_2'] = np.where(
    (
        (current_ecosystem_trim_done['GLB_Selected'] == 'YES') |
        (current_ecosystem_trim_done['US_Selected'] == 'YES') |
        (current_ecosystem_trim_done['EUR_Selected'] == 'YES')
    ) &
    (current_ecosystem_trim_done['IND_MAT_Selected'] == 'NO'),
    'YES',
    current_ecosystem_trim_done['Flag_2']
)



current_ecosystem_trim_filtered = current_ecosystem_trim_done[(current_ecosystem_trim_done['Flag_1'] == 'YES') | (current_ecosystem_trim_done['Flag_2'] == 'YES')].reset_index(drop=True)



final_df = current_ecosystem_trim_filtered.drop(columns = ['GLB_Selected', 'US_Selected', 'EUR_Selected', 'Flag_1','Flag_2','IND_MAT_Selected'])

for c in ['Global_Benchmark',  'EUR_Benchmark', 'US_Benchmark']:
    final_df[c] = final_df[c] * 100
final_df.iloc[:,2:] = final_df.iloc[:,2:].round(decimals = 3)

final_df = final_df.replace(0, '')

###############most recent upcoming reporting table###################

excel_link = r'Q:\Investment\Securities\Quant\Data\3. Reporting\Upcoming Earnings\Portfolio_Data.xlsx'
template = r'Q:\Investment\Securities\Quant\Data\3. Reporting\Upcoming Earnings\Upcoming_Earnings_Template.xlsx'
output_folder = r'Q:\Investment\Securities\Quant\Data\3. Reporting\Upcoming Earnings\Earnings'
BQL_excel = r'Q:\Investment\Securities\Quant\Data\3. Reporting\Upcoming Earnings\BQL_Excel.xlsm'
number_of_days = 7
send_email = False

include_optimisation_cols = True
opt_folder = r'Q:\Investment\Securities\Quant\Implementation\5 - Optimisation\BBG Rest API\Optimisations'
opt_names = ['EUR_2Q_1V_1G', 'GLB_2Q_1V_1G', 'US_2Q_1V_1G', 'EUR_1VR', 'GLB_1VR', 'US_1VR']


import os
import pandas as pd
import glob

# set the path to the folder
folder_path = 'Q:/Investment/Securities/Quant/Data/3. Reporting/Upcoming Earnings/Earnings/'

# use glob to get a list of all files in the folder
all_files = sorted(glob.glob(folder_path + '*[!_JH].xlsx'), key=os.path.getmtime, reverse=True)
# sort the list of files by modification time
sorted_files = sorted(all_files, key=os.path.getmtime, reverse=True)

# loop through the sorted files to find the most recent file that has read permission
for file in sorted_files:
    try:
        upcoming_earnings = pd.read_excel(file)
        break
    except PermissionError:
        print(f"Permission denied for file {file}. Trying the next most recent file.")

upcoming_earnings = upcoming_earnings.iloc[:,0:15]
upcoming_earnings.columns = ['Date', 'Time', 'Type', 'Ticker', 'Name', 'Region', 'Country','Global',
       'European','US','Ind & Mat',
       'Quality', 'Growth', 'Value',
       'Value Rel']


#replace NaT with blank and nan with blank
upcoming_earnings  = upcoming_earnings .fillna("")
# define a function to multiply a value by 100
def multiply_by_100(x):
    return x * 100

# apply the function to every cell in the DataFrame
upcoming_earnings.iloc[:, -8:] = upcoming_earnings.iloc[:, -8:].applymap(multiply_by_100).round(decimals = 3)     
upcoming_earnings.iloc[:, 5:7] = upcoming_earnings.iloc[:, 5:7].round(decimals = 3)     
upcoming_earnings.iloc[:, -8:] = upcoming_earnings.iloc[:, -8:].round(decimals = 3)     


# For the first table
upcoming_earnings.loc[:,['European' ,'Global' ,'US' ,'Ind & Mat']]= upcoming_earnings.loc[:,['European' ,'Global' ,'US' ,'Ind & Mat']].apply(pd.to_numeric, errors='coerce')
upcoming_earnings['Ind & Mat'] = upcoming_earnings['Ind & Mat']/100
# create an array of zeros
import numpy as np
import pandas as pd


# create an array of zeros
x = np.zeros(len(upcoming_earnings))

# assign relative weights to non-zero European or US
for i in range(len(upcoming_earnings)):
    if not pd.isna(upcoming_earnings['European'][i]):
        x[i] = upcoming_earnings['Global'][i] - upcoming_earnings['European'][i]
    elif not pd.isna(upcoming_earnings['US'][i]):
        x[i] = upcoming_earnings['Global'][i] - upcoming_earnings['US'][i]

# assign the array as a new column 'rel_weight'
upcoming_earnings.insert(loc=11, column='Global_Delta', value=x)


############################


pio.renderers.default = "browser"

import datetime
currentDate = datetime.date.today()
yday = currentDate - timedelta(days= 1) 

#find most recent data date 
models_date_q = """select distinct(DATA_DATE)
from QUANT.WORKING.DATA_MODELS
order by DATA_DATE DESC"""


model_date = pd.read_sql(models_date_q, ctx)

model_date_new = model_date['DATA_DATE'][0]
#format
model_date_new = str(model_date_new)
model_date_new = "'{}'".format(model_date_new)

#find most recent data date 
factors_date_q = """select distinct(DATA_DATE)
from QUANT.WORKING.DATA_FACTORS_PIT
order by DATA_DATE DESC"""


factors_date = pd.read_sql(factors_date_q, ctx)

factors_date = factors_date['DATA_DATE'][0]
#format
factors_date = str(factors_date)
factors_date = "'{}'".format(factors_date)


currentDate = str(currentDate)
currentDate = "'{}'".format(currentDate)

#queries
#################################filters###################################
msci = current_ecosystem[current_ecosystem['MSCI World']>0]

isin_list = msci['ISIN'].tolist()


msci_universe = msci
msci_universe_cols = msci_universe.columns.tolist()
rem = ['DATA_DATE', 'PROPER_NAME_y', 'FSYM_REGIONAL_ID_y']
msci_universe_new_cols =  [cols_i for cols_i in msci_universe_cols if msci_universe_cols not in rem]
msci_universe_new = msci_universe.filter(items = msci_universe_new_cols)  ######use



msci_universe_region = process_data(msci_universe_new, 'REGION')
msci_universe_sector = process_data(msci_universe_new, 'RBICS_ECONOMY')
msci_universe_country = process_data(msci_universe_new, 'COUNTRY_HQ')

###############stale prelim data###################
 
query_get_fsyms = """
    SELECT DISTINCT FSYM_REGIONAL_ID 
    FROM QUANT.WORKING.UNIVERSE 
    WHERE ISIN IN {}""".format(current_ecosystem_trim_isins)

query_get_fsyms = query_get_fsyms.replace('[','(')
query_get_fsyms = query_get_fsyms.replace(']',')')
 

holding_fsym_id_list = pd.read_sql(query_get_fsyms, ctx)
holding_fsym_id_list = holding_fsym_id_list.FSYM_REGIONAL_ID.tolist()
 

query_last_updated = """
SELECT U.PROPER_NAME, DC.FSYM_REGIONAL_ID, MAX(DC.UPDATE_DATE) ,RC.CONSTITUENT_ID, RC.CONSTITUENT_TYPE, CONSTITUENT_STATUS
FROM QUANT.WORKING.DATA_CONSTITUENTS AS DC
INNER JOIN QUANT.WORKING.UNIVERSE AS U
ON DC.FSYM_REGIONAL_ID = U.FSYM_REGIONAL_ID
JOIN QUANT.WORKING.REF_CONSTITUENTS AS RC
ON DC.CONSTITUENT_ID = RC.CONSTITUENT_ID
WHERE DC.FSYM_REGIONAL_ID IN {}
AND RC.CONSTITUENT_ID = '40002'
GROUP BY DC.FSYM_REGIONAL_ID, U.PROPER_NAME,RC.CONSTITUENT_ID,RC.CONSTITUENT_TYPE, CONSTITUENT_STATUS""".format(tuple(holding_fsym_id_list))


query_get_default_date = """SELECT QF.FSYM_ID, MAX(QF.DATE) AS Q_DATE, MAX(AF.DATE) AS A_DATE, MAX(SAF.DATE) AS SAF_DATE 
                            FROM FACTSET.FF_V3.FF_BASIC_QF AS QF
                            JOIN FACTSET.FF_V3.FF_BASIC_AF AS AF
                            ON QF.FSYM_ID = AF.FSYM_ID
                            JOIN FACTSET.FF_V3.FF_BASIC_SAF AS SAF
                            ON SAF.FSYM_ID = AF.FSYM_ID
                            WHERE QF.FF_ASSETS IS NOT NULL
                            AND QF.FSYM_ID IN {}
                            GROUP BY QF.FSYM_ID""".format(tuple(holding_fsym_id_list))
                            
 
last_updated_table = pd.read_sql(query_last_updated, ctx)
default_date = pd.read_sql(query_get_default_date , ctx)

def get_rep(row):
    q_date = row['Q_DATE']
    a_date = row['A_DATE']
    saf_date = row['SAF_DATE']
    
    if q_date == a_date:
        return 'Q'
    elif a_date == saf_date:
        return 'S'
    elif max(q_date, a_date, saf_date) == q_date:
        return 'Q'
    elif max(q_date, a_date, saf_date) == a_date:
        return 'A'
    else:
        return 'S'

default_date['rep'] = default_date.apply(lambda row: get_rep(row), axis=1)
default_date = default_date.filter(items = ['FSYM_ID','rep'])
default_date = default_date.rename(columns={'rep': 'rep_freq'})


#last_updated_table = last_updated_table[~last_updated_table['CONSTITUENT_TYPE'].isin(['Estimates', 'Pricing'])]
#last_updated_table = last_updated_table[~last_updated_table['CONSTITUENT_STATUS'].isin(['Prod', 'Test'])]
last_updated_table = last_updated_table.filter(items = ['PROPER_NAME', 'FSYM_REGIONAL_ID', 'MAX(DC.UPDATE_DATE)'])
last_updated_table = last_updated_table.rename(columns={'MAX(DC.UPDATE_DATE)': 'UPDATE_DATE'})

#last_updated_table['UPDATE_DATE'] = pd.to_datetime(last_updated_table['UPDATE_DATE'])
#max_update_dates = last_updated_table.groupby('PROPER_NAME')['UPDATE_DATE'].max().reset_index()
#max_update_dates['UPDATE_DATE'] = max_update_dates['UPDATE_DATE'].dt.date


current_date = date.today()
 
last_updated_table['Days since update'] = current_date - last_updated_table['UPDATE_DATE']
last_updated_table['Days since update'] = last_updated_table['Days since update'].dt.days
 
last_updated_table = last_updated_table.sort_values(by = 'Days since update', ascending = False)
last_updated_table = last_updated_table.rename(columns={'FSYM_REGIONAL_ID': 'FSYM_ID'})
last_updated_table = pd.merge(last_updated_table,  default_date , on = 'FSYM_ID' )


dropdown_options_port = ['MSCI_World','MSCI_Europe','MSCI_US']
mapped_msci_world = ['Global_port', 'Global_Benchmark']
mapped_msci_eur = ['EUR_port', 'EUR_Benchmark']
mapped_msci_us = ['US_port', 'US_Benchmark']

map_dict = {}
map_dict['MSCI_World'] = mapped_msci_world
map_dict['MSCI_Europe'] = mapped_msci_eur
map_dict['MSCI_US'] = mapped_msci_us


###############################################################################################################
#Creating styles for the dataframe tables---------------------------------------------------------------------
mediolanum_dark_blue = "#002A56"
mediolanum_light_blue = "#00BFFF"
mediolanum_white = "#FFFFFF"


################################app layout################################################
#-----------------------------------------------------------------------------------------------------------


app = dash.Dash(__name__)

from dash.dependencies import Input, Output, State

# define table options
table_options = [
    {"label": "Table 1", "value": "table_1"},
    {"label": "Table 2", "value": "table_2"},
    {"label": "Table 3", "value": "table_3"},
]


#############################################################################

#####table styles####################
common_style = {
    'font-family': 'Mediolanum Sans',
    'background-color': 'white',
    'color': mediolanum_blue,
    #"padding": "10px",
    "format": ".3f", # Add this line to format values to 3 decimal places
    "table-layout": "fixed"  # Add this line to make all columns equal width
}

box_style = {
    
    
    
    
    }

# Update style_header and style_cell to use common_style for both tables
table_style = {
    **common_style,
    "width": "100px",
    #"fontWeight": "bold",
    "backgroundColor": "white",
    "textAlign": "left",
    'format': {'specifier': '.3f'},
    'overflow-x': 'auto',
    'overflow-y': 'auto',
    'min-height': '30vh'

}# Update tab styles to use common_style


table_style_header_c_r = {
    **common_style,
    "width": "100px",
    "fontWeight": "bold",
    "backgroundColor": mediolanum_blue,
    "textAlign": "left",
    'format': {'specifier': '.3f'},
    'color': 'white'

 }   



table_style_header = {
    **common_style,
    "width": "100px",
    "fontWeight": "bold",
    "backgroundColor": mediolanum_turquoise,
    "textAlign": "left",
    'format': {'specifier': '.3f'},
    'color': 'white'

 }   


table_style_factor_analysis = {
  "font-family": "Mediolanum Sans",
  "background-color": "white",
  "color": "mediolanum_blue",
  "width": "100px",
  "background-color": "white",
  "text-align": "left",
  'format': {'specifier': '.3f'},
}


table_style_factor_analysis_header = {
    "font-family": "Mediolanum Sans",
    "background-color": "mediolanum_turquoise",
    "color": "white",
    "font-weight": "bold",
    "width": "100px",
    "text-align": "left",
    "format": {'specifier': '.3f'}
}


tab_style = {
    **common_style,
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}
 
tab_selected_style = {
    **common_style,
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}


######################################factor breakdown#######################
FSYM_ID_names_q = """select distinct(PROPER_NAME), FSYM_REGIONAL_ID,  RBICS_ECONOMY from
QUANT.WORKING.UNIVERSE"""


factor_names_q = """select distinct(FACTOR_NAME) , FACTOR_GROUP
from QUANT.WORKING.REF_FACTORS
ORDER BY FACTOR_GROUP DESC """


company_names = pd.read_sql(FSYM_ID_names_q, ctx)
company_names = company_names.sort_values(by = 'PROPER_NAME')
factor_names = pd.read_sql(factor_names_q, ctx)


#app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])#, external_stylesheets=[dbc.themes.DARKLY])
server = app.server
app.title = "Live Dashboard"


#Creating styles for the datepickers and company filters
Center_pickers = {#'height': '200px',
        #'background': '#003b4a',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'center',
}


factor_list_query = """select distinct(FACTOR_NAME) from QUANT.WORKING.REF_FACTORS"""
factor_list = pd.read_sql(factor_list_query, ctx)
 

####### This is for the Confirmation Status table of the Data Quality tab

portfolios_df = current_ecosystem[['FSYM_REGIONAL_ID', 'ISIN', 'CH_Int Wgt', 'CH_NthAm Wgt', 'CH_Eur Wgt']]
portfolios_df.columns = ['FSYM_REGIONAL_ID', 'ISIN', 'CH_Int', 'CH_NthAm', 'CH_Eur'] 
portfolios_df = portfolios_df.fillna(0)
portfolios_df['holding'] = portfolios_df['CH_Int'] + portfolios_df['CH_NthAm'] + portfolios_df['CH_Eur']
portfolios_df = portfolios_df[portfolios_df['holding'] > 0]
fsym_id = portfolios_df['FSYM_REGIONAL_ID'].tolist()
portfolios_df = portfolios_df.drop(columns = ['FSYM_REGIONAL_ID', 'holding']).reset_index(drop = True)

###################queries###################################
#ff basic af 
query_ff_basic_af = """select FSYM_ID,DATE,FF_UPD_TYPE 
 from FACTSET.FF_V3.FF_BASIC_AF 
where DATE >=  '2022-09-20'
and FSYM_ID in {}""".format(fsym_id)

query_ff_basic_af = query_ff_basic_af.replace('[', '(')
query_ff_basic_af = query_ff_basic_af.replace(']', ')')

ff_basic_af = pd.read_sql(query_ff_basic_af, ctx)

#ff basic qf
query_ff_basic_qf = """select FSYM_ID,DATE,FF_UPD_TYPE 
 from FACTSET.FF_V3.FF_BASIC_QF 
where DATE >=  '2022-09-20'
and FSYM_ID in {}""".format(fsym_id)

query_ff_basic_qf = query_ff_basic_qf.replace('[', '(')
query_ff_basic_qf = query_ff_basic_qf.replace(']', ')')

ff_basic_qf = pd.read_sql(query_ff_basic_qf, ctx)
#get the dates:
#ff basic saf
query_ff_basic_saf = """select FSYM_ID,DATE,FF_UPD_TYPE 
 from FACTSET.FF_V3.FF_BASIC_SAF
where DATE >=  '2022-09-20'
and FSYM_ID in {}""".format(fsym_id)

query_ff_basic_saf = query_ff_basic_saf.replace('[', '(')
query_ff_basic_saf = query_ff_basic_saf.replace(']', ')')
ff_basic_saf = pd.read_sql(query_ff_basic_saf, ctx)

##count number of ff_upd_typpe = 3
number_dic = {}
number = pd.DataFrame()
l = {}
l['AF'] = ff_basic_af
l['QF'] = ff_basic_qf
l['SAF'] = ff_basic_saf

d  ={}

# l = [ff_basic_af,ff_basic_qf, ff_basic_saf]
# l_name = ['ff_basic_af','ff_basic_qf', 'ff_basic_saf']
for i in l.keys():
    number = pd.DataFrame()
    for j in l[i]['FSYM_ID']:
         fsym =  l[i][ l[i]['FSYM_ID'] == j]
         fsym_date = fsym['DATE']
         fsym_date = pd.DataFrame(fsym_date)
         fsym_date = fsym_date.sort_values(by='DATE', ascending=False)
         fsym_date = fsym_date.iloc[-1].values[0]
         fsym_date = str(fsym_date)   
         number_l = len(fsym[fsym[ 'FF_UPD_TYPE'] == '1'])
         number[j] = [number_l, fsym_date]
         number.index = ['number','date']
             
    number = number.T 
    number = number.reset_index()
    number = number.rename(columns = {'index':'FSYM_ID'})
    d[i] = number
         
         #number[j:'Value'] = number_l
    
##new df
ff_basic_af_df =  pd.DataFrame.from_dict(d['AF'])
ff_basic_af_df = ff_basic_af_df.rename(columns = {'number':'AF'})
ff_basic_af_df = ff_basic_af_df.rename(columns = {'date':'DATE_AF'})

ff_basic_saf_df =  pd.DataFrame.from_dict(d['SAF'])
ff_basic_saf_df = ff_basic_saf_df.rename(columns = {'number':'SAF'})
ff_basic_saf_df = ff_basic_saf_df.rename(columns = {'date':'DATE_SAF'})


ff_basic_qf_df =  pd.DataFrame.from_dict(d['QF'])
ff_basic_qf_df = ff_basic_qf_df.rename(columns = {'number':'QF'})
ff_basic_qf_df = ff_basic_qf_df.rename(columns = {'date':'DATE_QF'})


new_df =pd.merge(ff_basic_af_df,ff_basic_saf_df, on= 'FSYM_ID',how = 'outer')
new_df =pd.merge(new_df,ff_basic_qf_df, on= 'FSYM_ID',how = 'outer')

uni_data = current_ecosystem[['PROPER_NAME','ISIN','FSYM_REGIONAL_ID']]

new_df = pd.merge(new_df, uni_data, right_on = 'FSYM_REGIONAL_ID', left_on = 'FSYM_ID', how = 'inner')

new_df_reind = new_df
col_order = [ 'PROPER_NAME', 'ISIN','FSYM_ID', 'AF', 'SAF', 'QF','DATE_AF','DATE_SAF','DATE_QF']
new_df_reind = new_df_reind.reindex(columns = col_order)

new_df_reind_fin = pd.merge(new_df_reind, portfolios_df.filter(items = ['ISIN']), how = 'inner')

for i in col_order[-3:]:
    new_df_reind_fin[i] = pd.to_datetime(new_df_reind_fin[i])

new_df_reind_fin['DATE_AF'] = new_df_reind_fin['DATE_AF'].dt.date
new_df_reind_fin['DATE_SAF'] = new_df_reind_fin['DATE_SAF'].dt.date
new_df_reind_fin['DATE_QF'] = new_df_reind_fin['DATE_QF'].dt.date





####### This is for the Market Opportunities Page : 

model_ranks_query = """select MODEL_NAME from QUANT.WORKING.REF_MODELS where MODEL_STATUS = 'Prod' ORDER BY COL_ORDER"""
model_ranks =  pd.read_sql(model_ranks_query, ctx)
model_ranks['AIM'] = 'L'
model_ranks.columns = ['MODEL_OR_FACTOR', 'AIM']

factor_ranks_query = """select FACTOR_NAME, AIM from QUANT.WORKING.REF_FACTORS where FACTOR_STATUS = 'Prod'"""
factor_ranks =  pd.read_sql(factor_ranks_query, ctx)
factor_ranks.columns = ['MODEL_OR_FACTOR', 'AIM']

model_and_factor_df = pd.concat([model_ranks, factor_ranks])

facts = model_and_factor_df['MODEL_OR_FACTOR'].tolist()

model_fact_invert_dict = dict(zip(model_and_factor_df['MODEL_OR_FACTOR'], model_and_factor_df['AIM']))
winVec = [3,97]

for f in factor_ranks['MODEL_OR_FACTOR']:
    f_ = f.replace(" ", "_")
    if f_ in current_ecosystem.columns:
        HorL = model_fact_invert_dict.get(f)
        mean = current_ecosystem[f_].mean()
        std = current_ecosystem[f_].std()
        
        temp = (current_ecosystem[f_] - mean) / std
        limit_lower = np.nanpercentile(temp, winVec[0])
        limit_higher = np.nanpercentile(temp, winVec[1])  
        temp = np.clip(temp,a_min=limit_lower,a_max=limit_higher)  
        min_ = min(temp)
        max_ = max(temp)
        
        if HorL == 'H':
            temp = temp.fillna(min_)
            current_ecosystem['Rank - ' + f] = (temp - min_) / (max_ - min_)
        else:
            temp = temp.fillna(max_)
            current_ecosystem['Rank - ' + f] = (1 - (temp - min_) / (max_ - min_))        
    else:
        facts.remove(f)

portfolios = ['MSCI World', 'CH_Eur Wgt' ,'CH_Int Wgt', 'CH_NthAm Wgt' , 'MSCI Europe', 'MSCI US', 'MSCI IND & MAT', 'MSCI HC']
portfolio_labels = ['MSCI World', 'Challenge Europe', 'Challenge International', 'Challenge North America', 'MSCI Europe', 'MSCI USA', 'Industrials & Materials', 'Healthcare']


rank_facts = []
rank_facts.append('RBICS_ECONOMY')
rank_facts.append('REGION')

for p in portfolios:
    rank_facts.append(p)

for r in facts:
    rank_facts.append('Rank - ' + r)
    
ecosystem_ranks = current_ecosystem[rank_facts]

for i in range(0, len(portfolios)):
    ecosystem_ranks = ecosystem_ranks.rename({portfolios[i]: portfolio_labels[i]})

############################combo of model ranks and factor values################################


#################################################################################################
# Define the dropdown options
dropdown_options = [{'label': col, 'value': col} for col in facts]
portfolios = ['MSCI World', 'CH_Eur Wgt' ,'CH_Int Wgt', 'CH_NthAm Wgt' , 'MSCI Europe', 'MSCI US', 'MSCI IND & MAT', 'MSCI HC']
portfolio_options = [{'label': label, 'value': portfolio} for portfolio, label in zip(portfolios, portfolio_labels)]



######### DASH FUNCTIONS BELOW : 
    
FSYM_ID_names_q = """select distinct(PROPER_NAME), FSYM_REGIONAL_ID,  RBICS_ECONOMY from
QUANT.WORKING.UNIVERSE"""

company_names = pd.read_sql(FSYM_ID_names_q , ctx)
company_lists = list(company_names.PROPER_NAME.unique())

min_date_query = """select min(DATA_DATE)
from QUANT.WORKING.DATA_MODELS
"""

max_date_query = """select min(DATA_DATE)
from QUANT.WORKING.DATA_MODELS
"""

min_date = pd.read_sql(min_date_query , ctx)

max_date = pd.read_sql(max_date_query , ctx)

models_query = """
select MODEL_NAME from QUANT.WORKING.REF_MODELS 
where MODEL_STATUS = 'Prod'
order by col_order
"""

models = pd.read_sql(models_query , ctx).values.ravel().tolist()
######################################################################################################################
all_holdings = current_ecosystem_trim.filter(items = ['SECURITY_NAME', 'ISIN','Global_port','EUR_port','US_port'])

xoxo = current_ecosystem.filter(items = ['ISIN','GICS Sector'])
bmk_vs_port = all_holdings.merge(xoxo, on = 'ISIN')
bmk_vs_port = bmk_vs_port.groupby(by = 'GICS Sector').sum()
bmk_vs_port = current_bmks_port_vs_bmk.merge(bmk_vs_port, on = current_bmks_port_vs_bmk.index )

bmk_vs_port['Global vs MSCI World'] = bmk_vs_port['Global_port'] - bmk_vs_port['Global_Benchmark']
bmk_vs_port['Eur vs MSCI Europe'] = bmk_vs_port['EUR_port'] - bmk_vs_port['EUR_Benchmark']
bmk_vs_port['US vs MSCI US'] = bmk_vs_port['US_port'] - bmk_vs_port['US_Benchmark']
bmk_vs_port = bmk_vs_port.filter(items=['key_0', 'Global vs MSCI World', 'Eur vs MSCI Europe', 'US vs MSCI US'])
bmk_vs_port.set_index('key_0', inplace=True)
bmk_vs_port.index.name = 'GICS Sector'
bmk_vs_port.iloc[:,-3:] = bmk_vs_port.iloc[:,-3:].round(decimals = 3)
bmk_vs_port = bmk_vs_port.reset_index()

#####################################################

all_holdings = current_ecosystem_trim.filter(items = ['SECURITY_NAME', 'ISIN','Global_port','EUR_port','US_port'])
# filter the rows of current_ecosystem_trim
# that have at least one non-null value in Global_port, EUR_port, or US_port
all_holdings = all_holdings[
    (current_ecosystem_trim['Global_port'].notnull()) | 
    (current_ecosystem_trim['EUR_port'].notnull()) | 
    (current_ecosystem_trim['US_port'].notnull())
][['SECURITY_NAME','ISIN', 'Global_port', 'EUR_port', 'US_port']]

all_holdings = all_holdings.dropna(subset=['ISIN'])
#all_holdings['SECURITY_NAME'] = all_holdings['SECURITY_NAME'].apply(lambda x: f"'{x}'")
all_holdings_names = all_holdings.ISIN.tolist()

all_holdings_fsyms = """SELECT distinct(FSYM_REGIONAL_ID) , ISIN
FROM QUANT.WORKING.UNIVERSE
WHERE ISIN IN {}""".format(all_holdings_names)
all_holdings_fsyms = all_holdings_fsyms.replace('[','(')
all_holdings_fsyms = all_holdings_fsyms.replace(']',')')

all_holdings_fsyms = pd.read_sql(all_holdings_fsyms, ctx)
all_holdings = pd.merge(all_holdings,all_holdings_fsyms, on= 'ISIN' )

all_holdings_fsyms = all_holdings_fsyms.FSYM_REGIONAL_ID.tolist()

##########step 2######################

last_reporting_query = """
    SELECT FSYM_REGIONAL_ID, MAX(DATA_DATE) AS LAST_REPORTED_DATE
    FROM QUANT.WORKING.DATA_CONSTITUENTS
    WHERE CONSTITUENT_ID = 40002
    AND FSYM_REGIONAL_ID IN {}
    GROUP BY CONSTITUENT_ID, FSYM_REGIONAL_ID
    ORDER BY LAST_REPORTED_DATE
""".format(all_holdings_fsyms)

last_reporting_query = last_reporting_query.replace('[','(')
last_reporting_query = last_reporting_query.replace(']',')')

last_reporting_query = pd.read_sql(last_reporting_query, ctx)

last_reporting_df = pd.merge(last_reporting_query, all_holdings, on = 'FSYM_REGIONAL_ID')


last_reporting_df = last_reporting_df.filter(items = ['SECURITY_NAME','ISIN','FSYM_REGIONAL_ID','LAST_REPORTED_DATE'])
last_reporting_df = last_reporting_df.sort_values(by = 'LAST_REPORTED_DATE')
#last_reporting_df.to_excel(r'C:\Users\ellen.hynes\Downloads/last_reporting_df.xlsx')
last_reporting_df= last_reporting_df.drop_duplicates(subset = 'SECURITY_NAME')

default_date = dt.date.today() - dt.timedelta(days=6*30)


####fabio code###############################
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

import numpy as np
# import datetime as dt
# from pandas.tseries.offsets import BDay
import snowflake.connector


delCode = tuple(sleeveMap['DelCode'].apply(str).to_list())


query = f"""Select POSITION_DATE, 
fund_accounting_code,
fund_accounting_name,
INSTRUMENT_NAME, 
TICKER_INSTRUMENT_REFERENCE, 
ISIN_INSTRUMENT_REFERENCE, 
NUMBER_OF_SECURITIES, 
WEIGHT_IN_MANAGED_ACCOUNT_PCNT AS STRATEGY_WEIGHTING,
THEORETICAL as LAST_PRICE,
ISO_CURRENCY_CODE as CURRENCY,
COUNTRY_NAME as COUNTRY_OF_RISK
from TEST_MED_DATAHUB.atomic_warehouse.instrument a
JOIN TEST_MED_DATAHUB.atomic_warehouse.instrument_position b on a.instrument_id = b.instrument_id 
JOIN TEST_MED_DATAHUB.mdm_mdh.currency c on payment_currency_id = c.currency_id
join TEST_MED_DATAHUB.mdm_mdh.country d on d.country_id = a.country_of_risk_id
join TEST_MED_DATAHUB.mdm_mdh.managed_account e on e.managed_account_id = b.managed_account_id
where fund_accounting_code in {delCode} 
AND NUMBER_OF_SECURITIES IS NOT NULL
AND STRATEGY_WEIGHTING IS NOT NULL
AND POSITION_DATE >= '2023-03-09'
Order by POSITION_DATE asc;;"""

universe = pd.read_sql(query, ctx_fabio)

# universe['Delta'] =  universe.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=0)-universe.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=1)
# universe['Delta%'] =  (universe.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=0)/universe.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=1)-1)*100
# universe.loc[universe['Delta'] == 0,'Delta'] = np.nan
# universe['Delta%'] = universe['Delta%'].round(decimals=2)
# universe['Delta%'] = universe.agg('{0[Delta%]}%'.format, axis=1)
# universe.loc[universe['Delta%'] == 'nan%','Delta%'] = np.nan
# universe.loc[universe['Delta%'] == '0.0%','Delta%'] = np.nan

test=universe.loc[universe['ISIN_INSTRUMENT_REFERENCE']=='GB00BM8PJY71']
z=test.loc[test['FUND_ACCOUNTING_CODE']=='711979']

universe_sleeve = universe.FUND_ACCOUNTING_NAME.unique()
universe_stock = universe.INSTRUMENT_NAME.unique()

####
data = pd.read_excel(r'Q:\Investment\Securities\Quant\Implementation\6 - Fusion\quantMap.xlsx', sheet_name = 'Sheet1')

#get column 'Region' and drop duplicates
list_portfolio = data['Region'].drop_duplicates().to_list()

bhList = ['0','1','2','3','4','5','6']
portfolio_options_2 = ['MSCI World','MSCI US','MSCI Europe']



######################################################################################################################
#open up excel file using pandas
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

import numpy as np
# import datetime as dt
# from pandas.tseries.offsets import BDay
import snowflake.connector


sleeveMap = pd.read_excel('Q:/Investment/Securities/Quant/Implementation/6 - Fusion/quantMap.xlsx')
delCode = tuple(sleeveMap['DelCode'].apply(str).to_list())


query = f"""Select POSITION_DATE, 
fund_accounting_code,
fund_accounting_name,
INSTRUMENT_NAME, 
TICKER_INSTRUMENT_REFERENCE, 
ISIN_INSTRUMENT_REFERENCE, 
NUMBER_OF_SECURITIES, 
WEIGHT_IN_MANAGED_ACCOUNT_PCNT AS STRATEGY_WEIGHTING,
THEORETICAL as LAST_PRICE,
ISO_CURRENCY_CODE as CURRENCY,
COUNTRY_NAME as COUNTRY_OF_RISK
from TEST_MED_DATAHUB.atomic_warehouse.instrument a
JOIN TEST_MED_DATAHUB.atomic_warehouse.instrument_position b on a.instrument_id = b.instrument_id 
JOIN TEST_MED_DATAHUB.mdm_mdh.currency c on payment_currency_id = c.currency_id
join TEST_MED_DATAHUB.mdm_mdh.country d on d.country_id = a.country_of_risk_id
join TEST_MED_DATAHUB.mdm_mdh.managed_account e on e.managed_account_id = b.managed_account_id
where fund_accounting_code in {delCode} 
AND NUMBER_OF_SECURITIES IS NOT NULL
AND STRATEGY_WEIGHTING IS NOT NULL
AND POSITION_DATE >= '2023-03-09'
Order by POSITION_DATE asc;;"""

universe = pd.read_sql(query, ctx_fabio)

# universe['Delta'] =  universe.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=0)-universe.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=1)
# universe['Delta%'] =  (universe.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=0)/universe.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=1)-1)*100
# universe.loc[universe['Delta'] == 0,'Delta'] = np.nan
# universe['Delta%'] = universe['Delta%'].round(decimals=2)
# universe['Delta%'] = universe.agg('{0[Delta%]}%'.format, axis=1)
# universe.loc[universe['Delta%'] == 'nan%','Delta%'] = np.nan
# universe.loc[universe['Delta%'] == '0.0%','Delta%'] = np.nan

test=universe.loc[universe['ISIN_INSTRUMENT_REFERENCE']=='GB00BM8PJY71']
z=test.loc[test['FUND_ACCOUNTING_CODE']=='711979']

universe_sleeve = universe.FUND_ACCOUNTING_NAME.unique()
universe_stock = universe.INSTRUMENT_NAME.unique()


#####################################################################################################################


data = pd.read_excel(r'Q:\Investment\Securities\Quant\Implementation\6 - Fusion\quantMap.xlsx', sheet_name = 'Sheet1')

#get column 'Region' and drop duplicates
list_portfolio = data['Region'].drop_duplicates().to_list()

bhList = ['0','1','2','3','4','5','6']
########################################################################################################################

ref_factor_query = """select * from QUANT.WORKING.REF_FACTORS"""
ref_factor = pd.read_sql(ref_factor_query , ctx)


######################################app layout######################################################################

# Define the light and dark themes
light_theme = {"background-color": "white", "color": "black"}
dark_theme = {"background-color": "black", "color": "white"}
from datetime import datetime
# Define the layout of the app
app.layout = html.Div(
    [
    dcc.Store(id="theme", data="light"),  # Store the current theme preference
    dcc.Tabs(
        [
            dcc.Tab(
                label="Portfolio Analysis",
                children=[
                    html.Div(
                        children=[
                                html.Div([
                                    html.H3("Portfolio vs Benchmark",
                                    className="header-title",
                                    style={
                                        **common_style,
                                        "font-size": "20px",
                                    },
                                    ),
                                    html.Div(
                                        children=[
                                            dash_table.DataTable(
                                                bmk_vs_port.to_dict('records'),
                                                style_cell=table_style,
                                                style_header=table_style_header_c_r,
                                                style_data_conditional = conditional_formatting_port_vs_bmk,
                                                sort_action="native",
                                                sort_mode="multi",
                                            )
                                        ], 
                                        className="portfolio_table",
                                    ),
                                ],
                                className="div_style",
                                ),
                            html.Div(
                                [
                                    html.H2(
                                        children="Companies Reporting",
                                        className="header-title",
                                        style={
                                            **common_style,
                                            "font-size": "20px",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Button(
                                                "Create new Excel file",
                                                id="create-button",
                                            ),
                                            dash_table.DataTable(
                                                id="table",
                                                style_cell=table_style,
                                                style_header=table_style_header_c_r,
                                                style_data_conditional = conditional_formatting_companies_reporting,
                                                sort_action="native",
                                                sort_mode="multi",
                                            ),
                                        ],className="portfolio_table",
                                    ),
                                    html.Div(
                                        [
                                            html.H2(
                                                children="Portfolio Alignment",
                                                className="header-title",
                                                style={
                                                    **common_style,
                                                    "font-size": "20px",
                                                },
                                            ),
                                            html.Div(
                                                children=[
                                                    dash_table.DataTable(
                                                        id="styled-table",
                                                        columns=[
                                                            {
                                                                "name": i,
                                                                "id": i
                                                            } for i in final_df.columns
                                                        ],
                                                        data=final_df.to_dict(
                                                            "records"),
                                                        style_cell=table_style,
                                                        style_header=table_style_header_c_r,
                                                        sort_action="native",
                                                        sort_mode="multi",
                                                    ),
                                                ],className="portfolio_table",
                                            ),

                                            html.Div(
                                                children=[
                                                    html.H3(
                                                        children="Additional info:",
                                                        style={
                                                            **common_style,
                                                            "font-size": "16px",
                                                        },
                                                    ),
                                                    dcc.Textarea(
                                                        id="additional-info",
                                                        placeholder="The bmk data comes from this file:" + file_path,
                                                        value="",
                                                        style={
                                                            **common_style,
                                                            "font-size": "16px",
                                                            "width": "100%",
                                                            "height": "100px",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "margin-top": "20px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "margin-top": "20px",
                                        },
                                    ),
                                ],
                                className="div_style",
                            ),
                        ],
                        className="div_style",
                    ),
                ],
                style = tab_style,
                selected_style = tab_selected_style
            ),

    
    dcc.Tab(
        label="Model Analysis",
        children=[
            html.Div(
                children=[
                    #HTML DIV FOR INSERTING THE HEADER ------------------------------------------------------------------------------------------------
                    html.Div(children = [
                        html.Div(
                            children=[
                                html.P(
                                    children="Choose models and date range to analyse change in model values",
                                    className="header-description",
                                ),
                            ],
                            className="header"
                            ),              
                            
                            
                        #HTML DIV FOR INSERTING THE FILTERS AND DATE PICKER --------------------------------------------------------------------------------
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.Div(children="Pick Date Range: "), #className="menu-title-left"),
                                        dcc.DatePickerRange(
                                        id='my_date_picker_range_nath',
                                        #min_date_allowed = min_date,
                                        max_date_allowed = currentDate,
                                        #initial_visible_month= max_date,
                                        #end_date = max_date
                                    ),
                                    ] ,
    
                                className="div_style"),
                                    
                                html.Div(
                                    children=[
                                        html.Div(children="Pick Models: "), #className="menu-title-left"),
    
                                        dmc.MultiSelect(
                                        label=None,
                                        placeholder="Select all models you would like to plot",
                                        id="model_filter",
                                        data= models,
                                        clearable=True,
                                        searchable = True, 
                                        limit=10,
                                        style={"width": 300, "marginBottom": 10},
                                        ),
                                    ],
                                className="div_style"),
    
                                
                                html.Div(
                                    children=[
                                        dmc.Checkbox(id="checkbox_simple", label="Filter for portfolio holdings",
                                                    mb=10, checked=True)
                                    ],
                                className="div_style"),
                                    
                                    
                                html.Div(
                                    children=[
                                        dmc.NumberInput(
                                            id= 'number_input',
                                            label="Pick the minimum rank change for display",
                                            description="From 0 to infinity, in steps of 5",
                                            value=0.05,
                                            min=0,
                                            step=0.01,
                                            style={
                                                **common_style,
                                                "font-size": "16px",
                                            },
                                        )
                                    ],
                                className="div_style"),

                            ],
                            className="wrapper-50",
                        ),
                    ],className = 'wrapper-spaced'),
    
                    #HTML DIV FOR INSERTING THE RANK CHANGES SUBPLOTS -----------------------------------------------------------------------------------------
                    html.Div(
                        children=[
                            html.Div(
                                children=dcc.Graph(
                                    id="model_plots",
                                    config={"displayModeBar": False},
                                    style ={'height': 'inherit'},
                                ),
                                className="card-90",
                            ),
                        ],
                        className="div_style",
                    ),    
    
                                      
                #HTML DIV FOR INSERTING THE COMPANY  FILTER -------------------------------------------------------------------------------- 
                    
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Div(children="Company: ", className="menu-title"),
                                    
                                    dmc.MultiSelect(
                                        label=None,
                                        placeholder="Select all companies you would like to plot",
                                        id="Company_filter_nath",
                                        data= company_lists,
                                        clearable=True,
                                        searchable = True, 
                                        limit=10,
                                        style={"width": 500, "marginBottom": 10},
                                    ),
                                ],className="div_style"
                            ),
                            #className="menu-title-right"),
                        ],
                        #style = Center_pickers
                                
                    className="wrapper-65"),
    
                    #HTML DIV FOR INSERTING THE FACTOR SUBPLOTS -----------------------------------------------------------------------------------------
                    html.Div(
                        children=[
                            html.Div(
                                children=[ dcc.Graph(
                                    id="factor_plots_nath",
                                    config={"displayModeBar": False},
                                    style ={'height': '100%'},
                                ),
                            ],className="large_div_style",
                            ),
                        ],
                        
                    ),        
                ],
            ),
            
            html.Div(
                children=[
                    # Div for Company and Date Range
                    html.Div(
                        children=[
                            # Company Select
                            html.Div(
                                children=[
                                    html.Div(
                                        children="Company: ",
                                        className="menu-title",
                                        style={"font-family": "Mediolanum Sans"},
                                    ),
                                    dmc.Select(
                                        data=company_names.PROPER_NAME.tolist(),
                                        searchable=True,
                                        id="Company_filter_tables",
                                        limit=10,
                                        value="3M Company",
                                        clearable=True,
                                        style={
                                            "font-size": "16px",
                                            "font-family": "Mediolanum Sans",
                                        },
                                    ),
                                ],
                                className = "div_style",
                            ),
                            # Date Range Selector
                            html.Div(
                                children=[
                                    html.Div(
                                        children="Date range: ",
                                        className="menu-title",
                                        style={"font-family": "Mediolanum Sans"},
                                    ),
                                    dcc.DatePickerRange(
                                        id="date_picker_ellen",
                                        min_date_allowed=date(1995, 8, 5),
                                        max_date_allowed=date.today(),
                                        initial_visible_month=date.today(),
                                        style={
                                            "font-size": "16px",
                                            "font-family": "Mediolanum Sans",
                                        },
                                    ),
                                ],
                                className = "div_style"                  
                            ),
                        ],    
                    ),
    
                    # Divs for Tables
                    
                    html.Div(id="my-table-container"),
                        
                   
    
                    # Div for Select a Factor
                    html.Div(
                        children=[
                            html.Div(
                                children="Select a factor:",
                                className="menu-title",
                                style={"font-family": "Mediolanum Sans"},
                            ),
                            dcc.Dropdown(
                                id="Factor_filter_ellen",
                                options=[
                                    {"label": factor, "value": factor}
                                    for factor in factor_names.FACTOR_NAME.unique()
                                ],
                                placeholder="Select a factor",
                                style={
                                    "font-size": "16px",
                                    "font-family": "Mediolanum Sans",
                                },
                            ),
                        ],
                        className = "div_style",
                    ),
    
                    # Div for Plot
                    html.Div(
                        children=[dcc.Graph(id="graph", className = "div_style")],
                        className = "div_style",
                    ),
                ],
                className = "div_style",
            ),

            #div for last updated table
            html.Div(
                children=[
                    html.Div(
                        
                        children="Last updated FSYM:",
                        className="menu-title",
                        style={"font-family": "Mediolanum Sans"},

                    ),


            html.Div(
                
                    dash_table.DataTable(
                        
                        last_updated_table.to_dict("records"),
                        style_cell=table_style,
                        style_header=table_style_header,
                        sort_action="native",
                        sort_mode="multi",
                    )
            ),


        ],
                className= 'div_style'
            ),
      
        #),
            ],
        style = tab_style,
        selected_style = tab_selected_style
    ),

               dcc.Tab(
                    label="Data Quality",
                    children=[
                html.Div(
                        dcc.RadioItems(
                            id='category',
                            options=[
                                {'label': 'Country', 'value': 'country'},
                                {'label': 'Region', 'value': 'region'},
                                {'label': 'Sector', 'value': 'sector'}
                            ],
                            value='country',
                            
            
                            
                        ),
                        className = "div_style",

                        ),
                html.Div(

                        dcc.Graph(id='output_plot'),
                        className = "div_style",
                        ),
                    html.Div(
                        dcc.Dropdown(
                            id='dropdown'
                        ),
                        className="div_style",
                    ),

                html.Div(
                    children=[
                        html.Div(
                            id='output_table',
                            style={"margin-top": "20px"},
                            className="portfolio_table",
                        ),
                    ],className="div_style",
                ),

                                    
                html.Div(
                    children=[
                        html.H3("Confirmation Status"),

                        html.Div(
                            children=[
                                dash_table.DataTable(
                                    data=new_df_reind_fin.to_dict('records'),
                                    columns=[{"name": i, "id": i} for i in new_df_reind_fin.columns],
                                    style_cell=table_style,
                                    style_header=table_style_header,
                                    sort_action="native",
                                    sort_mode="multi",
                                )
                            ],className="portfolio_table",
                        ),
                    ],
                    style={"margin-top": "20px"},
                    className="div_style",
                ),
               
        html.Div([
            html.H3('Last Reported Data'),
            
            dcc.DatePickerSingle(
                id='my-date-picker-single',
                min_date_allowed=last_reporting_df['LAST_REPORTED_DATE'].min(),
                max_date_allowed=last_reporting_df['LAST_REPORTED_DATE'].max(),
                initial_visible_month=default_date,
                date=default_date
            ),
            html.Br(),
            html.Div(id='table_last_reported_date')
        ],
                    style={"margin-top": "20px"},
                    className="div_style",
   
            
            ),  
            ],
            style = tab_style,
            selected_style = tab_selected_style
        ),

                
    dcc.Tab(
        label='Factor Returns',
        children=[
            html.Div(
                children=[
                    html.Div(
                        className="div_style",
                        children=[
                            html.Div(
                                className="menu-title",
                                children="Date Range:",
                                style={"font-family": "Mediolanum Sans"}
                            ),
                            dcc.DatePickerRange(
                                id="my-date-picker-range_factor_returns",
                                min_date_allowed=date(1995, 8, 5),
                                max_date_allowed=date.today(),
                                initial_visible_month=date.today(),
                            ),
                        ],
                    ),
                    html.Div(
                        className="div_style",
                        children=[
                            html.Label("Percentage", style={"font-family": "Mediolanum Sans"}),
                            dcc.Input(
                                id="percentage_input",
                                type="number",
                                min=0,
                                max=1,
                                step=0.1,
                                value=0.2,
                                style={"border": "0px solid black", "font-size": "120%", "font-family": "Mediolanum Sans"}
                            ),
                        ],
                    ),
                    html.Div(
                        className="div_style",
                        children=[
                            html.Label('Select a portfolio'),
                            dcc.Dropdown(
                                id='dropdown-portfolio_2',
                                options=portfolio_options_2,
                                value=portfolio_options_2[0]
                            )
                        ]
                    ),
                    html.Div(
                        className="div_style",
                        children=[
                            html.Label('Rebalance Frequency'),
                            dcc.Dropdown(
                                id='rebalance_frequency',
                                options=[
                                    {'label': 'Daily', 'value': 'daily'},
                                    {'label': 'Weekly', 'value': 'weekly'},
                                    {'label': 'Quarterly', 'value': 'quarterly'},
                                    {'label': 'Never', 'value': 'never'},
                                ],
                                value='daily'
                            )
                        ]
                    ),
                    html.Div(
                        children=[
                            html.Div(
                                className="card-90",
                                children=[
                                    dcc.Graph(
                                        id="factor_return_graph",
                                        config={"displayModeBar": False},
                                        style={"height": "inherit"},
                                    )
                                ],
                            )
                        ],
                        className="div_style",
                    ),
                    html.Div(
                        className="div_style",
                        children=[
                            html.Label('Select a Factor'),
                            dcc.Dropdown(
                                id='factor_returns_table_dropdown',
                                options=[
                                    {'label': 'Value', 'value': 'Value'},
                                    {'label': 'Quality', 'value': 'Quality'},
                                    {'label': 'Growth', 'value': 'Growth'},
                                    {'label': 'Sentiment', 'value': 'Sentiment'},
                                    {'label': 'Momentum', 'value': 'Momentum'},

                                ],
                                value='Value'
                            )
                        ]
                    ),

                    html.Div(
                        className="div_style",
                        children=[
                            html.Label('Factor Returns Table'),
                            dash_table.DataTable(
                                id='factor_returns_table',
                                columns=[
                                    {'name': col, 'id': col, 'editable': col == 'FACTOR_NAME'}
                                    for col in ref_factor.columns
                                ],
                                data=ref_factor.to_dict('records'),
                                editable=True,
                                row_selectable='single',
                                style_cell={
                                    'cursor': 'pointer',
                                    'pointer-events': 'none'
                                },
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': 'FACTOR_NAME'},
                                        'pointer-events': 'all'
                                    }
                                ]
                            )
                        ]
                    ),
                    
                    html.Div(
                    html.Label('Factor Definition'),    
                    id='selected_factor_table',
                    className='div_style'
                    ),
                    ],
                ),
            ],
            style=tab_style,
            selected_style=tab_selected_style

            ),
    
dcc.Tab(
    label='Market Opportunities',
    children=[
        html.Div(
            [  
                html.Div(
                        dcc.RadioItems(
                            id='region_input',
                            options=[
                                {'label': 'region', 'value': 'region'},
                                {'label': 'region_sector', 'value': 'region_sector'},
                            ],
                            value='region',
                            
            
                            
                        ),
                        className = "div_style",

                        ),

                html.Div(
                    [
                        html.Label('Select a portfolio'),
                        dcc.Dropdown(
                            id='dropdown-portfolio',
                            options=portfolio_options,
                            value=portfolio_options[0]['value']
                        )
                    ],
                    className = "div_style"
                ),
                html.Div(
                    [
                        html.Label('Select a factor'),
                        dcc.Dropdown(
                            id='dropdown-factor',
                            options= current_ecosystem_fin.iloc[:,34:].columns,
                            value='Net_Revenue'
                        )
                    ],
                    className = "div_style"
                ),
                
                html.Div(
                        dcc.RadioItems(
                            id='mean_method',
                            options=[
                                {'label': 'mean', 'value': 'mean'},
                                {'label': 'median', 'value': 'median'}
                            ],
                            value='mean',
                            
            
                            
                        ),
                        className = "div_style",

                        ),

                
                html.Div(
                    [                        
                        dcc.Graph( id="heatmap", config={"displayModeBar": False})

                    ],
                    className = "div_style"
                ),
                
                html.Div(
                    [   
                        html.Div(
                            children=[
                                dash_table.DataTable(
                                    id="table_2",
                                    style_cell=table_style,
                                    style_header=table_style_header,
                                    sort_action="native",
                                    sort_mode="multi",
                                )
                            ],className="portfolio_table",
                        ),
                    ],
                    className = "div_style"
                ),
                

                
                
            ],
            className = "div_style"
        )
    ],
    style = tab_style,
    selected_style = tab_selected_style
    ),


dcc.Tab(
    label='Fusion',
    children=[
        html.Div(className='div_style', children=[
            html.H1(children='Fusion Holdings', style={'textAlign':'center'}),
            dcc.Dropdown(options=[{'label': name, 'value': name} for name in sorted(universe_sleeve)],
                         value='Quant - Challenge International Equity',
                         id='dropdown-selection_1'),
            dcc.Dropdown(id='dropdown-selection_2'),
            html.Div([
                dcc.Graph(id='graph1')
            ]),
            html.Div([
                dcc.Graph(id='graph2')
            ])
        ]),
        
        html.Div(className='div_style', children=[
            html.Div([
                html.H1(children='Fusion Checks'),
        
                #add a dropdown menu
                dmc.Select(
                    id='portfolio_filter',
                    data=list_portfolio,
                    searchable=True,
                    clearable=True,
                    nothingFound="No options found",
                    style={"width": 400},
                    value="Global",
                    label="Strategy:"
                ),
            ]),
                    
            html.Div([
                dcc.DatePickerSingle(
                    date=datetime.today() - BDay(1),
                    id='datepicker'
                ),
            ]),
        
            html.Div([
                #html.H1(children='Bank Holiday Adjustment'),
        
                #add a dropdown menu
                dmc.Select(
                    id='Bank_holiday',
                    data=bhList,
                    searchable=True,
                    clearable=True,
                    nothingFound="No options found",
                    style={"width": 120},
                    value='0',
                    label="Bank Holiday Adj:"
                ),
            ]),
        ]),
        
        html.Div([
                
            html.H2(children='QPS - GLB Portfolio Position Holdings | Fusion t-2 vs RBC Rec t-1'),
            dash_table.DataTable(virtualization=True, id='mergedDB_full', style_cell=table_style)
        
        ], className='div_style'),
        
        html.Div([
                
            html.H2(children='QPS - GLB Portfolio Position Changes | Fusion t-1 vs Fusion t-2'),
            dash_table.DataTable(id='fusionCheck_full', style_cell=table_style)
        
        ], className='div_style'),
        
        html.Div([
                
            html.H2(children='QPS - GLB Portfolio Position Deltas'),
            dash_table.DataTable(id='fusionPtf_Wgt', style_cell=table_style)
        
        ], className='div_style'),
        
        html.Div([
                
            html.H2(children='QPS - GLB Portfolio Cash %'),
            dash_table.DataTable(id='cashFull', style_cell=table_style)
        
        ], className='div_style')
    ],

    style=tab_style,
    selected_style=tab_selected_style
    ),
    ],
    ),
    ],
    )

 


############################## callbacks ##################################################################################

@app.callback(
    Output("mergedDB_full", "data"),
    Output("fusionCheck_full", "data"),
    Output("fusionPtf_Wgt", "data"),
    Output("cashFull", "data"),
    Input('datepicker', 'date'),
    Input("portfolio_filter", "value"),
    Input("Bank_holiday", "value")
)

def update_output(date_value, portfolio_filter, bankHoliday):
    # d = datetime.today() - timedelta(days=1)
    bankHoliday = int(bankHoliday)

    #NAVdate = d.strftime('%Y-%m-%d')
    # NAVdate = '2023-04-18'
    # bankHoliday = 0
    NAVdate = f"{date_value}"
    print(NAVdate)


    sleeveMap = pd.read_excel(r'Q:\Investment\Securities\Quant\Implementation\6 - Fusion\quantMap.xlsx')
    sleeveMap = sleeveMap.loc[sleeveMap['Region']== portfolio_filter]

    #using sleeve map and creating a list from a column
    folders = sleeveMap['FolderName'].tolist()
    ManagerCode = pd.Series(sleeveMap['DelCode'].tolist())
    ManagerCode = ManagerCode.astype(str)


    # create full tab to check portfolios' holings deltas
    idx=0
    irx=0
    for i in range(len(folders)):
        print(i)
        print(ManagerCode[i])
        print(folders[i])
        
        conn = pyodbc.connect('Driver={SQL Server};' 'Server=euncsqldb01.c.prv.mediolanum.ie;' 'Database=MED_EDW;' 'Trusted_Connection=yes;')
        
        myArray = pd.read_sql_query("""DECLARE @NAVdate as date
        DECLARE @PortCode as nvarchar(10)

        --SET @NAVdate = '_NAVdate_'
        --SET @PortCode = '_portCode4d_'
        SET @NAVdate = '""" + NAVdate + """'
        SET @PortCode = '""" + ManagerCode[i] + """'

        SELECT
        RIGHT(Ptfl.[Fund_Code],4) AS Ptfl_Code
        , Ptfl.[Fund Name] AS Ptfl_Name
        , Ptfl.[ISIN code] AS sub_ISIN
        , NULL AS sub_BBG_Code
        , Ptfl.[Manager Code] AS sub_Code
        , Ptfl.[Instrument Description] AS sub_Des
        , Ptfl.[Instrument Currency] AS sub_CCY
        , Ptfl.[Valuation Price in local currency] AS sub_MktP_l
        , Ptfl.[Quantity] AS sub_Size
        , Ptfl.[Exchange Rate] AS sub_FX
        , Ptfl.[Market Value in Fund Currency] AS sub_MktVal
        , Ptfl.[Accrued Interest in Instrument Currency] * Ptfl.[Exchange Rate] AS sub_Accrual
        , Ptfl.[% of Fund Assets] AS sub_Weight
        , Ptfl.SEDOL AS sub_SEDOL
        , Ptfl.CUSIP AS sub_CUSIP
        , Ptfl.[Sub Type MDF] AS sub_Type
        , Ptfl.[Complement Type MDF] sub_comp_Type
        , Ptfl.[Description for Complement Type] AS sub_Des_Comp_Type
        , Ptfl.[Bloomberg Sector Code] AS sub_BBG_Sec
        , Ptfl.[NAV_Date] AS NAV_date
        , 'Ptfl' AS Source
        , Ptfl.[LineNo]
        FROM MED_EDW.edw.rbc_xcp2p018portfo AS Ptfl 
        WHERE Ptfl.[NAV_Date] in (@NAVdate)
        AND [Manager Code] in (@PortCode)

        UNION 
        SELECT
        RIGHT(Cash.[Fund_Code],4) AS Ptfl_Code
        , Cash.[Fund Name] AS Ptfl_Name
        , NULL AS sub_ISIN
        , Cash.Currency + ' Curncy' AS sub_BBG_Code
        , Cash.[Manager Code] AS sub_Code
        , Cash.[Type] AS sub_Des
        , Cash.[Currency] AS sub_CCY
        , NULL as sub_MktP_l 
        , Cash.[Balance local currency] AS sub_Size
        , Cash.[Balance Fund currency]/Cash.[Balance local currency] AS sub_FX
        , Cash.[Balance Fund currency] AS sub_MktVal
        , NULL AS sub_Accrual
        , NULL AS sub_Weight
        , NULL AS sub_SEDOL
        , NULL AS sub_CUSIP
        , 'Cash' AS sub_Type
        , 'Cash' AS sub_comp_Type
        , 'Cash' AS sub_Des_Comp_Type
        , 'Cash' AS sub_BBG_Sec
        , Cash.[NAV_Date] AS NAV_date
        , 'Cash' AS Source
        , Cash.[LineNo]
        FROM MED_EDW.edw.rbc_xc20p018cashfd AS Cash 
        WHERE ABS(Cash.[Balance local currency]) > 0
        AND Cash.[NAV_Date] in (@NAVdate)
        AND  [Manager Code] in (@PortCode)
        AND [Type] IN ('Receivables/Payables','Settled cash position','Time Deposits/Loans', 'Accrued Interest on IRS', 'Int.Rec. on Swaps')""", conn)

        myArray.loc[myArray['sub_ISIN'].isna(), 'sub_ISIN'] = myArray['sub_BBG_Code']

        dbRBC = (myArray
                .assign(NAV_date = pd.to_datetime(myArray['NAV_date'], infer_datetime_format=True))
                .assign(NAV_date = pd.to_datetime(myArray['NAV_date']).dt.strftime('%m-%d-%Y'))
                .assign(SUB_MKTVAL = pd.to_numeric(myArray["sub_MktVal"]))
                .rename(columns={"sub_ISIN":"ISIN", "sub_Size":"Quantity"}))

        dbRBC_id = dbRBC.filter(items = ['ISIN','sub_Des'])
        dbRBC_id = dbRBC_id[~dbRBC_id['ISIN'].str.contains("Curncy")]
        
        if len(dbRBC_id) == 0:
            sys.exit("No RBC data for "+folders[i])  
        else:
            print('RBC data in DWH for '+folders[i])

        dbRBC_sum = (dbRBC
                #.assign(Quantity = pd.to_numeric(myArray["Quantity"]))
                .groupby(['NAV_date','ISIN'])
                .sum(['Quantity'])
                .reset_index()
                .filter(items = ['NAV_date','ISIN', 'Quantity', 'sub_Des'])
                .round({'Quantity': 0})
                .merge(dbRBC_id, on='ISIN', how='left'))

        #dbRBC["Wgt"] = (dbRBC["SUB_MKTVAL"]/dbRBC["SUB_MKTVAL"].sum()) 
        
        repDate = dbRBC["NAV_date"][0]


        # repDate = dbRBC["NAV_date"][0]
        #n[ManagerCode[i]] = dbRBC
        #globals()[f'{ManagerCode[i]}_rbc'] = dbRBC
        
        fusionPtf = (pd.read_excel("""Q://Investment//Securities//Quant//Implementation//6 - Fusion//"""+ folders[i] +"""//"""+ ManagerCode[i] +"""_"""+ repDate + """.xlsx"""))
        fusionPtf = fusionPtf[(fusionPtf.nSec != 0)]
        fusionPtf = (fusionPtf
                #.assign(Quantity = pd.to_numeric(myArray["Quantity"]))
                .groupby(['timeMachine','Ticker','ISIN','Name'])
                .sum(['nSec'])
                .reset_index())
        
        mergedDB = fusionPtf.merge(dbRBC_sum, on='ISIN', how='outer')
        mergedDB["Check"] = (mergedDB["nSec"]-mergedDB["Quantity"]) 
        mergedDB = (mergedDB
                    .rename(columns={"nSec":"Fusion", "Quantity":"RBC"})
                    .assign(timeMachine = pd.to_datetime(mergedDB['timeMachine']).dt.strftime('%m-%d-%Y')))
        mergedDB = mergedDB[mergedDB.Check != 0]
        mergedDB.loc[mergedDB['Name'].isna(), 'Name'] = mergedDB['sub_Des']
        mergedDB.Fusion = mergedDB.Fusion.round(1)
        mergedDB.Check = mergedDB.Check.round(1)
        mergedDB = mergedDB[['timeMachine', 'NAV_date', 'Name', 'Ticker', 'ISIN', 'Fusion', 'RBC', 'Check']]
        mergedDB = mergedDB.reset_index(drop=True)
        mergedDB = mergedDB.rename(columns={'timeMachine':'Date – Fusion','NAV_date':'Date – RBC', 'Fusion':str('Fusion '+folders[i]), 'RBC':str('RBC '+folders[i]), 'Check':str('Check '+folders[i])})
        mergedDB = mergedDB.sort_values(by=str('Check '+folders[i]), na_position='first', ascending = False)
        mergedDB = mergedDB.sort_values(by=str('Check '+folders[i]), na_position='first', ascending = False)
        

        if idx==0:
            mergedDB_full = mergedDB.copy()
            idx = idx+1
        else:
            # mergedDB = mergedDB.drop(columns = 'Name')
            mergedDB_full = mergedDB_full.merge(mergedDB, on = ['Name','Date – Fusion','Date – RBC','Ticker','ISIN'], how = 'outer')
        
        # add check fusion t-1 vs fusion t-2
        
        fusionR = fusionPtf.drop('Wgt', axis=1).rename(columns={'nSec':'nSecT2'})
        fusionR = fusionR[~fusionR['Ticker'].str.contains("Curncy")]
        
        dateD = pd.to_datetime(repDate).date()
        dateD = (dateD + BDay(1+bankHoliday)).strftime('%m-%d-%Y')
        
        fusionPtfD = (pd.read_excel("""Q://Investment//Securities//Quant//Implementation//6 - Fusion//"""+ folders[i] +"""//"""+ ManagerCode[i] +"""_"""+ dateD + """.xlsx"""))
        fusionPtfD = fusionPtfD[(fusionPtfD.nSec != 0)]
        fusionPtfD = (fusionPtfD
                #.assign(Quantity = pd.to_numeric(myArray["Quantity"]))
                .groupby(['timeMachine','Ticker','ISIN','Name'])
                .sum(['nSec'])
                .reset_index()
                .drop('Wgt', axis=1)
                .rename(columns={'nSec':'nSecT1'}))
        fusionPtfD = fusionPtfD[~fusionPtfD['Ticker'].str.contains("Curncy")]
        
        fusionCheck = fusionR.merge(fusionPtfD, on =  ['Ticker','ISIN','Name'], how = 'outer')
        fusionCheck[folders[i]] = fusionCheck['nSecT1'] - fusionCheck['nSecT2']
        fusionCheck = fusionCheck.filter(items=['Name','Ticker','ISIN',folders[i]])
        fusionCheck = fusionCheck.loc[fusionCheck[folders[i]]!= 0]
        
        if irx==0:
            fusionCheck_full = fusionCheck.copy()
            irx = irx+1
        else:
            # mergedDB = mergedDB.drop(columns = 'Name')
            fusionCheck_full = fusionCheck_full.merge(fusionCheck, on = ['Name','Ticker','ISIN'], how = 'outer')

    # mailDate = mergedDB["Date – Fusion"][0]
    repDate = dateD


    idx=0
    for i in range(len(folders)):
        print(i)
        print(ManagerCode[i])
        print(folders[i])
        

        fusionPtf = (pd.read_excel("Q://Investment//Securities//Quant//Implementation//6 - Fusion//"+ folders[i] +"//"+ ManagerCode[i] +"""_"""+ repDate +""".xlsx"""))
        fusionPtf = fusionPtf[(fusionPtf.nSec != 0)]
        
        fusionPtf = fusionPtf.rename(columns={"Wgt":folders[i]})
        fusionPtf = fusionPtf.filter(items = ['timeMachine','Name','Ticker',folders[i]]).rename(columns={"timeMachine":"Date - Fusion"})
        
        if idx==0:
            fusionPtf_full = fusionPtf.copy()
            idx = idx+1
        else:
            fusionPtf = fusionPtf.filter(items = ['Ticker',folders[i]])
            fusionPtf_full = fusionPtf_full.merge(fusionPtf, on = ['Ticker'], how = 'outer')
        
    delta_vars = folders.copy()
    del delta_vars[-0]
    fusionPtf_Wgt = fusionPtf_full.copy()
        
    for i in range(len(delta_vars)):
        print(i)
                
        fusionPtf_Wgt = fusionPtf_Wgt.assign(Delta = lambda x: (fusionPtf_Wgt[delta_vars[i]]-fusionPtf_Wgt[folders[0]])*100).round({'Delta': 2}).rename(columns={"Delta":str('Delta_'+delta_vars[i])})

    idx=0
    for i in range(len(delta_vars)):
        print(i)
        
        fusionPtf_Wgt = fusionPtf_Wgt.assign(absol = lambda x: abs(fusionPtf_Wgt[str('Delta_'+delta_vars[i])]))
            
        if idx==0:
            fusionPtf_Wgt_full = fusionPtf_Wgt.copy()
            idx = idx+1
        else:
            fusionPtf_Wgt_full = fusionPtf_Wgt_full.assign(absol = lambda x: fusionPtf_Wgt_full['absol'] + abs(fusionPtf_Wgt[str('Delta_'+delta_vars[i])]))

        fusionPtf_Wgt = fusionPtf_Wgt_full.copy()

    "add delta_vars[n] below if a new sleeve will be added in line 197 and 199"

    # Define the column range
    # start_col = 0
    # end_col = len(delta_vars)

    # Initialize the condition
    condition = False

    # Loop through the columns
    for i in range(len(delta_vars)):
        # Update the condition
        condition = condition | (abs(fusionPtf_Wgt[str('Delta_'+delta_vars[i])]) >= 0.75)

    fusionPtf_Wgt['Date - Fusion'] = pd.to_datetime(fusionPtf_Wgt['Date - Fusion']).dt.date
    # Filter the data
    fusionPtf_Wgt = fusionPtf_Wgt.loc[condition]


    fusionPtf_Wgt = fusionPtf_Wgt[~fusionPtf_Wgt['Ticker'].str.contains("Curncy")].sort_values(['absol'], ascending=[False])
    fusionPtf_Wgt = fusionPtf_Wgt.drop('absol', axis=1)
    fusionPtf_Wgt = fusionPtf_Wgt.rename(columns={"Ticker":"Reference"})
    
    fusionPtf_Wgt['Date - Fusion'] = pd.to_datetime(fusionPtf_Wgt['Date - Fusion']).dt.date

    num_cols = fusionPtf_Wgt.select_dtypes(include='number').columns
    fusionPtf_Wgt[num_cols] = fusionPtf_Wgt[num_cols].round(decimals=2)


    "get cash weight"

    cashWGT = fusionPtf_full[fusionPtf_full['Ticker'].str.contains("Curncy")]
    cashWGT = cashWGT.drop(['Ticker', 'Name'], axis=1)
    cashWGT = pd.melt(cashWGT, id_vars='Date - Fusion')
    cashWGT = cashWGT.groupby(['variable']).sum().sort_values(['value'], ascending=[False]).reset_index(drop=False)
    cashWGT.value = cashWGT.value.round(2)
    cashWGT = cashWGT.rename(columns={"variable":"Sleeve","value":"%Cash t-1"})

    yDate = datetime.strptime(dateD, '%m-%d-%Y') - BDay(1+bankHoliday)
    yDate = yDate.strftime('%m-%d-%Y')


    idx=0
    for i in range(len(folders)):
        print(i)
        print(ManagerCode[i])
        print(folders[i])
        
        cashY = (pd.read_excel("Q://Investment//Securities//Quant//Implementation//6 - Fusion//"+ folders[i] +"//"+ ManagerCode[i] +"""_"""+ yDate +""".xlsx"""))
        cashY['Sleeve'] = folders[i]
        cashY = cashY[cashY['Ticker'].str.contains("Curncy")]
        cashY = cashY.groupby(['Sleeve'])['Wgt'].sum().reset_index(drop=False)
        cashY.Wgt = cashY.Wgt.round(2)
        cashWGTY = cashY.rename(columns={"Wgt":"%Cash t-2"})
        
        if idx==0:
            cashWGTY_full = cashWGTY.copy()
            idx = idx+1
        else:
            cashWGTY_full = pd.concat([cashWGTY_full, cashWGTY])

    cashFull = cashWGT.merge(cashWGTY_full, on='Sleeve', how='left')
    cashFull['%Delta'] = cashFull['%Cash t-1'] - cashFull['%Cash t-2']
    
    num_cols = cashFull.select_dtypes(include='number').columns
    cashFull[num_cols] = cashFull[num_cols].round(decimals=3)


    mergedDB_full = mergedDB_full.to_dict('records')
    fusionCheck_full = fusionCheck_full.to_dict('records')
    fusionPtf_Wgt = fusionPtf_Wgt.to_dict('records')
    cashFull = cashFull.to_dict('records')

    return mergedDB_full, fusionCheck_full, fusionPtf_Wgt, cashFull 



##################################################################################################################
@app.callback(
    Output('factor_returns_table', 'data'),
    Input('factor_returns_table_dropdown', 'value')
)
def update_factor_returns_table(selected_factor):
    # Perform any data manipulation based on the selected factor here
    updated_data = ref_factor[ref_factor['FACTOR_GROUP'] == selected_factor] 
    return updated_data.to_dict('records')



@app.callback(
    Output('selected_factor_table', 'children'),
    [Input('factor_returns_table', 'active_cell'),
     Input('factor_returns_table', 'data')]
)
def show_selected_factor_table(active_cell, data):
    if active_cell and active_cell['column_id'] == 'FACTOR_NAME':
        factor_name = data[active_cell['row']][active_cell['column_id']]
        # Perform any necessary data processing based on the selected factor_name
        selected_factor_table = generate_selected_factor_table(factor_name)
        return html.Div([
            html.Label(f"Constituents of {factor_name}"),
            dash_table.DataTable(
                columns=[{'name': col, 'id': col} for col in selected_factor_table.columns],
                data=selected_factor_table.to_dict('records')
            )
        ])
    return None

def generate_selected_factor_table(factor_name):
    # Perform any necessary data retrieval or processing based on the factor_name
    # Return the corresponding table
    # This is just a placeholder example
    query = """select RC.CONSTITUENT_ID , RC.CONSTITUENT_NAME, RC.CONSTITUENT_SCHEMA, RC.CONSTITUENT_TABLE, RC.CONSTITUENT_METHODOLOGY , RC.CONSTITUENT_ITEM, RC.CONSTITUENT_TYPE, RC.HISTORICAL_LAG, RC.CONSTITUENT_STATUS
    FROM QUANT.WORKING.REF_FC_MAP AS MAP 
    JOIN QUANT.WORKING.REF_FACTORS AS RF
    ON RF.FACTOR_ID = MAP.FACTOR_ID
    JOIN QUANT.WORKING.REF_CONSTITUENTS AS RC
    ON RC.CONSTITUENT_ID = MAP.CONSTITUENT_ID
    WHERE FACTOR_NAME = '{}'""".format(factor_name)
    
    selected_table_data = pd.read_sql(query, ctx)
    return selected_table_data



@app.callback(
    dash.dependencies.Output('table_last_reported_date', 'children'),
    [dash.dependencies.Input('my-date-picker-single', 'date')]
)
def update_table(date):
    # Convert the date string to a datetime object
    date = dt.datetime.strptime(date, '%Y-%m-%d').date()
    
    # Filter the last_reporting_df table based on the selected date
    filtered_df = last_reporting_df[last_reporting_df['LAST_REPORTED_DATE'] < date]
    
    # Create the DataTable object with the filtered dataframe
    table = dash_table.DataTable(
        columns=[{'name': col, 'id': col} for col in filtered_df.columns],
        data=filtered_df.to_dict('records'),
        style_cell=table_style,
        style_header=table_style_header,

    )
    
    # Wrap the table in a div element for styling purposes
    table_container = html.Div([
        html.H4(f"Holdings with no Constituents since {date}"),
        table
    ])
    
    return table_container


#n_clicks = 0
@app.callback(Output('table', 'data'),
              Input('create-button', 'n_clicks'))
def update_table_elle(n_clicks):
    if n_clicks is not None:
        print('Starting upcoming earnings script----------------------------------------------------------------')
        
        try:
            check_Upcoming_Earnings(number_of_days, excel_link, send_email, template, output_folder, BQL_excel, include_optimisation_cols, opt_folder, opt_names)
        
        except BaseException as ex:
            # Get current system exception
            ex_type, ex_value, ex_traceback = sys.exc_info()
        
            # Format stacktrace
            stack_trace = traceback.format_exc()
            
            error_body = f"""
            The daily ecosystem run has failed, find below the error report to explain what caused the issue:<br><br>
            The exception type is: {ex_type.__name__}<br>
            The exception message is: {ex_value}<br>
            <br>
            {stack_trace}<br>
            Thank you
            """
            
            # Sending email confirmation to recipients
            test_date = datetime.today().strftime("%d %b %Y %H:%M")
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)
            mail.To = 'QuantReports@mediolanum.ie'
            mail.Subject = f'Master Ecosystem Update run has failed - {test_date}'
            mail.Body = 'Message body'
            mail.HTMLBody = error_body
            mail.Send()
        
            # Load the most recent file as new upcoming earnings
            folder_path = 'Q:/Investment/Securities/Quant/Data/3. Reporting/Upcoming Earnings/Earnings/'
            files = glob.glob(folder_path + '*')
            files.sort(key=os.path.getmtime, reverse=True)
            most_recent_file = files[0]
            new_upcoming_earnings = pd.read_excel(most_recent_file)
            new_upcoming_earnings = new_upcoming_earnings.fillna("")
            new_upcoming_earnings['Date'] = new_upcoming_earnings['Date'].dt.date
            return new_upcoming_earnings.to_dict('records')
        
    else:
        upcoming_earnings.iloc[:, -9:] = upcoming_earnings.iloc[:, -9:].round(decimals=3) 
        upcoming_earnings['Date'] = upcoming_earnings['Date'].dt.date
        return upcoming_earnings.to_dict('records')



import datetime
@app.callback(Output('factor_return_graph', 'figure'), 
              Input("my-date-picker-range_factor_returns", "start_date"),
              Input("my-date-picker-range_factor_returns", "end_date"),
              Input("percentage_input", "value"),
              Input("dropdown-portfolio_2", "value"),
              Input("rebalance_frequency", "value"),)
def update_factor_returns(start_date, end_date, percentage, portfolio, rebalance_frequency):
        
    a1 = dt.datetime.now()
    
    msci_query = """select VALUATION_DATE, BLOOMBERG_TICKER, ISIN, SECURITY_WEIGHT, INDEX_SYMBOL, SECTOR_LABEL_LEVEL1 as GICS FROM [MED_EDW].[rimes].[benchmark] where INDEX_SYMBOL = 'WRLD.R' and VALUATION_DATE >= '""" + str(start_date) + """' and VALUATION_DATE <= '""" + str(end_date) + """'"""
    msci_df = pd.read_sql(msci_query, conn)
    max_msci_dt = max(msci_df['VALUATION_DATE'])
    msci_date_list_sorted = msci_df['VALUATION_DATE'].sort_values().unique().tolist()
    
    dates_df = pd.DataFrame()
    dates_df['MSCI Dates'] = msci_date_list_sorted
    
    uni_dates_query = """select distinct(DATA_DATE) from QUANT.WORKING.UNIVERSE where DATA_DATE > '""" + str(dates_df['MSCI Dates'].iloc[0]) + """'"""
    uni_dates = pd.read_sql(uni_dates_query, ctx)
    
    uni_dates_list = []
    
    for d in msci_date_list_sorted:
        uni_date = find_minimum_greater_date(uni_dates['DATA_DATE'].tolist(), date(int(d[0:4]),int(d[5:7]),int(d[8:10])))
        uni_dates_list.append(uni_date)
    
    dates_df['Universe Dates'] = uni_dates_list
    
    first_msci_isins_list = msci_df[msci_df['VALUATION_DATE'] == max_msci_dt]['ISIN'].tolist()
    first_universe_date = dates_df['Universe Dates'].iloc[0]
    
    universe_query = """select ISIN, PROPER_NAME, FSYM_REGIONAL_ID from QUANT.WORKING.UNIVERSE where DATA_DATE = '""" +str(first_universe_date) + """'""" 
    universe_query = universe_query + "and ISIN in  {}".format(first_msci_isins_list)
    universe_query = universe_query.replace('[','(')
    universe_query = universe_query.replace(']',')')
    universe_df = pd.read_sql(universe_query, ctx)
    current_ecosystem_fin_filter = current_ecosystem_fin.filter(items = ['PROPER_NAME','MSCI World','MSCI US','MSCI Europe'])
    universe_df = pd.merge(universe_df, current_ecosystem_fin_filter, on = 'PROPER_NAME')
    universe_df = universe_df[universe_df[portfolio].notnull()]
    
    fsym_id_list = universe_df['FSYM_REGIONAL_ID'].unique().tolist()
    
    model_date_list = []
    model_date_list_str = []
    
    uni_d_query = "select distinct(DATA_DATE) from QUANT.WORKING.DATA_MODELS where DATA_DATE < '" + str(dates_df['Universe Dates'].iloc[-1]) + "'"
    model_dates = pd.read_sql(uni_d_query, ctx)
    
    for d in uni_dates_list:
        model_date = find_maximum_less_than_date(model_dates['DATA_DATE'].tolist(), d)
        model_date_list.append(model_date)
        model_date_list_str.append(str(model_date))
    
    dates_df['Model Dates']= model_date_list
    dates_df['Model Dates Str']= model_date_list_str
           
    
    model_query = "select M.DATA_DATE, M.FSYM_REGIONAL_ID, R.MODEL_NAME, M.MODEL_VALUE "
    model_query = model_query + "from QUANT.WORKING.DATA_MODELS as M "
    model_query = model_query + "inner join QUANT.WORKING.REF_MODELS as R "
    model_query = model_query + "on M.MODEL_ID = R.MODEL_ID "
    model_query = model_query + "where M.DATA_DATE in {}".format(model_date_list_str)
    model_query = model_query + "and FSYM_REGIONAL_ID in {}".format(fsym_id_list)
    model_query = model_query + "and R.MODEL_STATUS = 'Prod'"
    model_query = model_query.replace('[','(')
    model_query = model_query.replace(']',')')
    model_df = pd.read_sql(model_query, ctx)
    models = model_df['MODEL_NAME'].unique().tolist()
    
    model_count = []
    for m in models:
        count = model_df[model_df['MODEL_NAME'] == m].shape[0]
        model_count.append(count)
    max_ = max(model_count)
    for i in range(0,len(model_count)):
        if model_count[i] < max_:
            models.remove(models[i])
                
    returns_query = "select DATA_DATE, FSYM_REGIONAL_ID, D_RETURN_EUR "
    returns_query = returns_query + "from QUANT.WORKING.DATA_RETURNS "
    returns_query = returns_query + "where DATA_DATE in {}".format(msci_date_list_sorted)
    returns_query = returns_query + "and FSYM_REGIONAL_ID in {}".format(fsym_id_list)
    returns_query = returns_query.replace('[','(')
    returns_query = returns_query.replace(']',')')
    returns_df = pd.read_sql(returns_query, ctx)
            
    #full_data_sect_df = {}
    model_returns_sect_df = pd.DataFrame()
    #top_data_keep_sect_ = pd.DataFrame(columns = ['DATE', 'BLOOMBERG_TICKER', 'ISIN', 'SECURITY_WEIGHT', 'D_RETURN_EUR', 'GICS', 'MODEL'])
    sectors = msci_df['GICS'].unique().tolist()
    
    a2 = dt.datetime.now()
    
    for i in range(0, dates_df.shape[0]-1):
        msci_d = dates_df['MSCI Dates'].iloc[i]
        #uni_d = dates_df['Universe Dates'].iloc[i]
        model_d = dates_df['Model Dates'].iloc[i]
        msci_dt = date(int(msci_d[0:4]),int(msci_d[5:7]),int(msci_d[8:10]))
        next_msci_d = dates_df['MSCI Dates'].iloc[i+1]
        next_msci_dt = date(int(next_msci_d[0:4]),int(next_msci_d[5:7]),int(next_msci_d[8:10]))
        
        msci = msci_df[msci_df['VALUATION_DATE'] == msci_d]
        model = model_df[model_df['DATA_DATE'] == model_d]
        model_trim = model.drop(columns = 'DATA_DATE')
        model_trim_drop =  model_trim.drop_duplicates(subset=['FSYM_REGIONAL_ID','MODEL_NAME'])
        
        model_trim_p = pd.pivot(model_trim_drop, index = 'FSYM_REGIONAL_ID', columns = 'MODEL_NAME', values = 'MODEL_VALUE').reset_index(drop=False)
        returns = returns_df[returns_df['DATA_DATE'] == next_msci_dt]
        returns_trim = returns.drop(columns = 'DATA_DATE').reset_index(drop=True)
        
        msci_uni = msci.merge(universe_df, on = 'ISIN', how = 'left')
        msci_uni_model = msci_uni.merge(model_trim_p, on = 'FSYM_REGIONAL_ID', how = 'left')
        msci_uni_model_ret = msci_uni_model.merge(returns_trim, on = 'FSYM_REGIONAL_ID', how = 'left')
        msci_uni_model_ret['DATE'] = msci_dt
           
        sec_weight_dict = {}
        for sec in sectors: 
            sec_weight_dict[sec] = msci_uni_model_ret[msci_uni_model_ret['GICS'] == sec]['SECURITY_WEIGHT'].sum()
            
        model_returns_list=[]
        for m in models:
            msci_uni_model_ret[m] = msci_uni_model_ret[m].fillna(1)
            sec_ret = 0
            for sec in sectors: 
                count = msci_uni_model_ret['GICS'].value_counts()[sec]
                cut_off = msci_uni_model_ret[msci_uni_model_ret['GICS']==sec][m].nsmallest(int(count*percentage)).iloc[-1]
                df_ = msci_uni_model_ret[(msci_uni_model_ret['GICS'] == sec) & (msci_uni_model_ret[m] <= cut_off)]
                ret = (df_['SECURITY_WEIGHT'] * df_['D_RETURN_EUR']).sum() / df_['SECURITY_WEIGHT'].sum()
                sec_ret = sec_ret + (ret * sec_weight_dict[sec])                    
            model_returns_list.append(sec_ret)
        
        model_returns_sect_df[next_msci_dt] = model_returns_list
      
    a3 = dt.datetime.now()
    
    model_returns_sect_df.index = models
    model_returns_sect_df_t = model_returns_sect_df.T
    
    ###############################cumulative ret#########################
    
    for m in models:
        model_returns_sect_df_t[m] = model_returns_sect_df_t[m] + 1
        model_returns_sect_df_t[m] = model_returns_sect_df_t[m].cumprod()
        model_returns_sect_df_t[m] = model_returns_sect_df_t[m] - 1
       
    model_returns_sect_df_t = model_returns_sect_df_t.reset_index()
    
    date_init_minus_one = model_returns_sect_df_t['index'].iloc[0]- timedelta(days = 1)
    new_row = pd.DataFrame(np.zeros((1, model_returns_sect_df_t.shape[1])), columns=model_returns_sect_df_t.columns)
    new_row['index']= date_init_minus_one
    # concatenate the new row with the original DataFrame and reassign to df
    df = pd.concat([new_row, model_returns_sect_df_t]).reset_index(drop=True)
    
    max_row = df.iloc[df.shape[0]-1].reset_index()
    max_row = max_row[max_row['index'] != 'index']
    max_row.columns = ['model', 'return']
    max_row = max_row.sort_values(by = 'return', ascending = False).reset_index(drop=True)
    
    order_list = []
    order_list.append('index')
    for m in max_row['model'].tolist():
        order_list.append(m)
        
    df_reordered = df[order_list]
    df_cols = df_reordered.columns
    factor_return_fig = px.line(df_reordered, x = df['index'], y = df_cols[1:])
    a4 = dt.datetime.now()
    
    time_1 = divmod((a2-a1).total_seconds(), 60)
    time_2 = divmod((a3-a2).total_seconds(), 60)
    time_3 = divmod((a4-a3).total_seconds(), 60)
    
    print( " part 1 :" + str(time_1 [0]) + " mins and " + str(int(time_1 [1])) + " secs")
    print( " part 2 :" + str(time_2 [0]) + " mins and " + str(int(time_2 [1])) + " secs")
    print( " part 3 :" + str(time_3 [0]) + " mins and " + str(int(time_3 [1])) + " secs")
    
    return factor_return_fig

     
@app.callback(Output('graph', 'figure'),
              Input("date_picker_ellen", "start_date"),
              Input("date_picker_ellen", "end_date"),
              Input("Company_filter_tables", "value"),
              Input("Factor_filter_ellen", "value"))

def plot_factors_nath(start_date, end_date, Company, factor):
    
    print('HELLO')
    Company = "'{}'".format(Company)
    start_date = "'{}'".format(start_date)
    end_date = "'{}'".format(end_date)
    Factor = "'{}'".format(factor)
     
    #msci = pd.read_sql_query(msci_query, conn)
    name_query = """
    SELECT DISTINCT FSYM_REGIONAL_ID
    FROM QUANT.WORKING.UNIVERSE
    WHERE PROPER_NAME IN ({})
""".format(Company)
    
    #msci = pd.read_sql_query(msci_query, conn)
    
    fsym = pd.read_sql(name_query, ctx)
    fsym = fsym.to_string(index=False, header=False)
    fsym = "'{}'".format(fsym)

    ##GET FACTORS THROUGH TIME
    factor_through_time_q = """ 
     SELECT F.DATA_DATE, F.FACTOR_VALUE
     FROM QUANT.WORKING.REF_FACTORS AS H
     INNER JOIN 
     (SELECT * FROM QUANT.WORKING.DATA_FACTORS_PIT
     UNION ALL
     SELECT * FROM QUANT.WORKING.DATA_FACTORS_HIST) as F
     ON F.FACTOR_ID = H.FACTOR_ID
     WHERE F.DATA_DATE <=  """+end_date+"""
     and F.FSYM_REGIONAL_ID = """+fsym+"""
     and H.FACTOR_NAME = """+Factor+"""
     ORDER BY DATA_DATE DESC"""
     
    factors_through_time = pd.read_sql(factor_through_time_q, ctx )
    factors_through_time = factors_through_time.drop_duplicates(subset=["DATA_DATE"])
 
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Line(x=factors_through_time["DATA_DATE"], y=factors_through_time["FACTOR_VALUE"], name="Line"),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(x=factors_through_time["DATA_DATE"], y=factors_through_time["FACTOR_VALUE"], name="Bar"),
        secondary_y=False
    )
    
    fig.update_layout(title= factor, xaxis_title='Date', yaxis_title='Factor Value', yaxis2_title='Secondary Y Axis Title')

    return fig



@app.callback(Output("my-table-container", "children"),
              Input("Company_filter_tables", "value"),
              Input("date_picker_ellen", "end_date"),
              Input("date_picker_ellen", "start_date"))


#Company = '3i Group plc'
#start_date = '2023-04-04'
#end_date = '2023-04-08'

def update_charts(Company, end_date, start_date):
    print(Company)
    
    end_date_copy = end_date
    start_date_copy = start_date
    
    Company = "'{}'".format(Company)
    start_date = "'{}'".format(start_date)
    end_date = "'{}'".format(end_date)
    
    
    #find most recent data date 
    models_date_q = """
    SELECT distinct(DATA_DATE)
    FROM QUANT.WORKING.DATA_MODELS
    WHERE DATA_DATE < """+start_date+"""
    ORDER BY DATA_DATE DESC
    LIMIT 1
    """
    
    model_date = pd.read_sql(models_date_q, ctx)
    
    model_date_new = model_date.to_string(index=False, header=False)
    model_date_new = "'{}'".format(model_date_new)
    
    
    Model_names = """select distinct(M.MODEL_NAME) from QUANT.WORKING.REF_MODELS as M left join QUANT.WORKING.DATA_MODELS as D on D.MODEL_ID = M.MODEL_ID where D.DATA_DATE =  """+model_date_new+""" """
    
    model_names = pd.read_sql(Model_names, ctx)
    
    
    
    #msci = pd.read_sql_query(msci_query, conn)
    name_query = """select distinct(FSYM_REGIONAL_ID) from QUANT.WORKING.UNIVERSE
    WHERE PROPER_NAME in ({})""".format(Company) 
    
    #msci = pd.read_sql_query(msci_query, conn)
    
    fsym = pd.read_sql(name_query, ctx)
    fsym = fsym.to_string(index=False, header=False)
    fsym = "'{}'".format(fsym)
    
    
        
    ##############################chatgpt###################################################
    date_q = """SELECT MIN(DATA_DATE) FROM QUANT.WORKING.DATA_FACTORS_PIT WHERE DATA_DATE >= {} AND DATA_DATE <= {}
    UNION ALL
    SELECT MAX(DATA_DATE) FROM QUANT.WORKING.DATA_FACTORS_PIT WHERE DATA_DATE >= {} AND DATA_DATE <= {}""".format(start_date, end_date, start_date, end_date)
    
    
    #get max dates between start and end date
    dates = pd.read_sql(date_q, ctx)
    my_list_dates = dates['MIN(DATA_DATE)'].astype(str).tolist()
    my_list_dates = ["'{}'".format(i) for i in my_list_dates]
    
    date_1 = my_list_dates[0]
    date_2 = my_list_dates[1]
    
    factors_query = """SELECT F.FACTOR_NAME, F.FACTOR_GROUP, F.FACTOR_SUB_GROUP, D.FACTOR_VALUE, D.DATA_DATE
    FROM QUANT.WORKING.REF_FACTORS AS F 
    inner JOIN (
        SELECT *
        FROM QUANT.WORKING.DATA_FACTORS_PIT
        WHERE FSYM_REGIONAL_ID = {}
        AND DATA_DATE IN ({},{})) AS D
    ON F.FACTOR_ID = D.FACTOR_ID
    """.format(fsym, date_1 ,date_2)
    
    
    factors_df = pd.read_sql(factors_query,ctx) 
    factors_df_p = pd.pivot(factors_df, index = ['FACTOR_GROUP', 'FACTOR_SUB_GROUP','FACTOR_NAME'], columns = 'DATA_DATE', values = 'FACTOR_VALUE').reset_index(drop=False) 
    
    factor_cols = factors_df_p.columns.tolist()
    
    # Loop through the list and check if the item is a datetime object
    for i in range(len(factor_cols)):
        if isinstance(factor_cols[i], datetime.date):
            # Convert the datetime object to a string with the desired format
            factor_cols[i] = factor_cols[i].strftime('%Y-%m-%d')
            
    factors_df_p.columns = factor_cols
    
    #factors_df_p.columns = ['FACTOR_GROUP', 'FACTOR_SUB_GROUP','FACTOR_NAME', 'T', 'T-1']
    factors_df_p['FACTOR_SUB_GROUP'] = np.where(factors_df_p['FACTOR_GROUP'] == 'Quality', 'Quality_'+factors_df_p['FACTOR_SUB_GROUP'], factors_df_p['FACTOR_GROUP'])
    
    factors_df_p[start_date_copy] = pd.to_numeric(factors_df_p[start_date_copy])
    factors_df_p[end_date_copy] = pd.to_numeric(factors_df_p[end_date_copy])
    factors_df_p['delta'] = factors_df_p[end_date_copy] - factors_df_p[start_date_copy]

    #factors_df_p = factors_df_p.filter(items = ['FACTOR_SUB_GROUP', 'FACTOR_NAME', 'T', 'T-1', 'delta'])
    model_list = factors_df_p['FACTOR_SUB_GROUP'].unique().tolist()
    model_list_order = ['Growth', 'Momentum', 'Quality_Strength', 'Quality_Stability', 'Quality_Security', 'Sentiment', 'Value']
    sorted_model_list = sorted(model_list, key=lambda x: model_list_order.index(x))

    return_divs = []
    factor_dict = {}
    for i in sorted_model_list:
        try:
            factor = factors_df_p[factors_df_p['FACTOR_SUB_GROUP'] == i]
            
            #check if dataframe is empty
            if factor.empty:
                print('dataframe is empty for {}'.format(i))
                continue

            #round the values to 3 decimal places from column 3 to the end
            title = factor.iloc[1, 0] # get value at row 0, column 1
            title_as_str = str(title)
            factor = factor.iloc[:,1:]
            factor.iloc[:,-3:] = factor.iloc[:,-3:]*100
            factor.iloc[:,-3:] = factor.iloc[:,-3:].round(decimals = 3)

            #columns=[{"name": col, "id": col, "type": "numeric", "format": Format(precision=3)} for col in factor.columns]
            columns=[{"name": col, "id": col} for col in factor.columns]

            data_dict = factor.to_dict("records")
            datatable = dash_table.DataTable(
            columns=columns,
            data=data_dict,
            #style_table={"margin": "10px"},
            #style_cell={'width': '25%'},
            sort_action='native',
            style_cell=table_style_factor_analysis,
            style_header=table_style_header_c_r)

            div = html.Div([   html.H2(title_as_str),    datatable] ,className="div_style",)
            return_divs.append(div)
        
        except:
            div = html.Div([   html.H2(i),    html.H3('No data available for this factor')],className="div_style",)
            return_divs.append(div)
            continue

    return return_divs

@app.callback(
    [Output('dropdown', 'options'),
    Output('output_table', 'children')],
    Input('category', 'value')
)
def update_dropdown(category):
    # Load data based on the selected category
    if category == 'sector':
        df = msci_universe_sector
    elif category == 'region':
        df = msci_universe_region
    elif category == 'country':
        df = msci_universe_country
    
    # Generate dropdown options
    options = [{'label': i, 'value': i} for i in df.columns[1:]]
    table = generate_table(df)
    return options, table

from plotly.subplots import make_subplots
import plotly.graph_objs as go




@app.callback(
    Output('output_plot', 'figure'),
    [Input('dropdown', 'value'),
     Input('category', 'value')]
)
def update_output(selected, category):
    if category == 'sector':
        df = msci_universe_sector
    elif category == 'region':
        df = msci_universe_region
    elif category == 'country':
        df = msci_universe_country

    df_sorted = df.sort_values(by=[selected], ascending=False)
    fig = px.bar(df_sorted, x=df_sorted.iloc[:,0], y=selected)

    return fig


def generate_table(dataframe):
    dataframe = dataframe.round(3)
    table = dash_table.DataTable(
        dataframe.to_dict('records'), [{"name": i, "id": i} for i in dataframe.columns],     
        sort_mode="multi",
        style_cell=table_style,
        style_header=table_style_header,
        sort_action="native"
)
    
    return table



def generate_plot(dataframe, selected):
    fig = px.bar(dataframe, x= dataframe.iloc[:,0], y=selected)
    return fig


# Define the callback to update the table based on the selected factor
portfolio_factor = 'MSCI World' 
selected_factor = 'FCF_Margin'
region_input = 'region'
mean_method = 'mean'

@app.callback([Output('table_2', 'data'), Output('heatmap', 'figure')],
              Input('mean_method', 'value'),
              Input('dropdown-portfolio', 'value'),
              Input('dropdown-factor', 'value'),
              Input('region_input', 'value'))

def update_table_sec(mean_method,  portfolio_factor, selected_factor, region_input):
  
    ecosystem_sect_ = current_ecosystem_fin[current_ecosystem_fin[portfolio_factor].notnull()]
    ecosystem_sect_ = ecosystem_sect_.dropna(subset=[portfolio_factor])
    filter_items =  ['REGION','RBICS_ECONOMY',selected_factor,portfolio_factor ]
    ecosystem_sect_ = ecosystem_sect_.dropna(subset=[portfolio_factor])
    ecosystem_sect_ = current_ecosystem_fin[filter_items]
    ecosystem_sect_ = ecosystem_sect_.dropna(subset=[portfolio_factor])

    if region_input == 'region':
        if mean_method == 'mean':
            ecosystem_sect_ = ecosystem_sect_.groupby(['REGION']).mean().reset_index(drop=False)

        else:
            ecosystem_sect_ = ecosystem_sect_.groupby(['REGION']).median().reset_index(drop=False)#
            
        ecosystem_sect_piv = ecosystem_sect_
    elif region_input == 'region_sector':
        if mean_method == 'mean':
            ecosystem_sect_ = ecosystem_sect_.groupby(['RBICS_ECONOMY', 'REGION']).mean().reset_index(drop=False)

        else:
            ecosystem_sect_ = ecosystem_sect_.groupby(['RBICS_ECONOMY', 'REGION']).median().reset_index(drop=False)
            
        ecosystem_sect_piv = ecosystem_sect_.pivot_table(index = 'RBICS_ECONOMY', columns = 'REGION', values = selected_factor).reset_index(drop=False)

    ecosystem_sect_piv.iloc[:,1:] = ecosystem_sect_piv.iloc[:,1:].applymap(multiply_by_100).round(decimals = 3)

    #CREATING HEATMAP ============================================================
    name = selected_factor
    if region_input == 'region':
        fig3 = go.Figure(data=go.Bar(
            x=ecosystem_sect_['REGION'],
            y=ecosystem_sect_[selected_factor],
            marker=dict(
                color=ecosystem_sect_[selected_factor],
                colorscale='RdYlGn',
                reversescale=True
            )
        ))
        fig3.update_layout(
            title=f'Average {selected_factor} by region',
            xaxis_title='Region',
            yaxis_title='Average Factor Value',
            # paper_bgcolor='#011627',
            # plot_bgcolor='#011627'
        )
        fig3.update_traces(text=ecosystem_sect_[selected_factor].round(decimals=2), texttemplate="%{text}", hovertemplate=None)

    elif region_input == 'region_sector':
        fig3 = go.Figure(data=go.Heatmap(
            z=ecosystem_sect_[name],
            x=ecosystem_sect_['REGION'],
            y=ecosystem_sect_['RBICS_ECONOMY'],
            reversescale=True,
            colorscale='RdYlGn'
        ))
        fig3.update_layout(
            title=f'Heatmap of average {selected_factor} rank for {portfolio_factor}',
            #paper_bgcolor='#011627',
            #plot_bgcolor='#011627'
        )
        fig3.update_traces(zhoverformat=',.2', selector=dict(type='heatmap'))
        fig3.update_traces(colorbar_tickformat=',.2', selector=dict(type='heatmap'))
        fig3 = fig3.update_traces(text=ecosystem_sect_[name].round(decimals=2), texttemplate="%{text}", hovertemplate=None)

    return ecosystem_sect_piv.to_dict('records'), fig3



#nathan code:
@app.callback(
    Output('model_plots', 'figure'),
    Input('my_date_picker_range_nath', 'start_date'),
    Input('my_date_picker_range_nath', 'end_date'),
    Input("model_filter", "value"),
    Input("checkbox_simple", "checked"),
    Input("number_input", "value"))
def update_output_nath(start_date, end_date, models,filter_by_our_portfolios , number_input):
    if start_date is not None and end_date is not None and models is not None:
        email_threshold = number_input

        #setting up date objects and strings        
        cur = end_date

        if len(models)== 1:
            #removing the last comma in the tuple to stop snowflake breakdown
            models_tuple = f"('{models[0]}')"

        else:
            models_tuple = tuple(x for x in models)

        prev = start_date

        cur_d = date.fromisoformat(end_date)
        prev_d = date.fromisoformat(start_date)
                
        prev = "'{}'".format(prev)
        cur = "'{}'".format(cur)
        
        query_1 = f"""select D.DATA_DATE, S.PROPER_NAME, S.RBICS_ECONOMY, S.COUNTRY_HQ, D.FSYM_REGIONAL_ID, R.MODEL_NAME, D.MODEL_ID, D.MODEL_VALUE, S.ISIN, S.MKT_VAL_USD
        from QUANT.WORKING.DATA_MODELS as D LEFT JOIN QUANT.WORKING.REF_MODELS AS R ON D.MODEL_ID = R.MODEL_ID
        left JOIN
        (select * from QUANT.WORKING.UNIVERSE where DATA_DATE = {prev}) as S ON S.FSYM_REGIONAL_ID = D.FSYM_REGIONAL_ID
        where D.DATA_DATE in ({prev},{cur}) and R.MODEL_STATUS = 'Prod' and R.MODEL_NAME in {models_tuple}"""
        
        
        snowflake = pd.read_sql(query_1, ctx)
        snowflake = snowflake.filter(items = ['DATA_DATE', 'FSYM_REGIONAL_ID', 'MODEL_VALUE','MODEL_NAME', 'PROPER_NAME', 'RBICS_ECONOMY', 'COUNTRY_HQ', 'ISIN', 'MKT_VAL_USD'])
        
        
        if filter_by_our_portfolios:
            #Getting names of all excel files in file path
            ptfs = ['CH_Int', 'CH_NthAm', 'CH_Eur']
            files_list = []
            for ptf in ptfs:
                folder_path = f'Q:\\Investment\\Securities\\Quant\\Implementation\\6 - Fusion\\{ptf}/*.xlsx'
                files = glob.glob(folder_path, recursive=False)
                files_list += files
            
            #Filtering for given portfolio and getting the latest excel file for given portfolio
            fusionPtfGlb = pd.read_excel(max(list(filter(lambda k: '711979' in k,files_list)), key=os.path.getctime))
            fusionPtfUS = pd.read_excel(max(list(filter(lambda k: '713733' in k,files_list)), key=os.path.getctime))
            fusionPtfEUR = pd.read_excel(max(list(filter(lambda k: '714110' in k,files_list)), key=os.path.getctime))
            
            fusionPtf = fusionPtfGlb.append(fusionPtfUS)
            fusionPtf = fusionPtf.append(fusionPtfEUR)
            fusionPtf = fusionPtf[(fusionPtf.nSec != 0)]
            
            mask = fusionPtf['ISIN'].str.contains('Curncy')
            fusionPtf['mask'] = mask 
            fusionPtf = fusionPtf[fusionPtf['mask']== False]
            fusionPtf = fusionPtf.drop(columns = ['mask'])
            isin = tuple(fusionPtf["ISIN"].unique())
            snowflake = snowflake[snowflake['ISIN'].isin(isin)] # filter by vector
        
        df_old = snowflake[snowflake['DATA_DATE'] == prev_d]
        df_new = snowflake[snowflake['DATA_DATE'] == cur_d]
        
        
        df_old = df_old.rename(columns = {'MODEL_VALUE':'MODEL_VAL_OLD'})
        df_new = df_new.rename(columns = {'MODEL_VALUE':'MODEL_VAL_NEW'})
        df_new = df_new.drop(columns = ['DATA_DATE', 'ISIN', 'MKT_VAL_USD', 'PROPER_NAME', 'RBICS_ECONOMY', 'COUNTRY_HQ'])
        
        df_full = df_old.merge(df_new, on =['FSYM_REGIONAL_ID','MODEL_NAME'], how = 'left')
        df_full['Change'] = df_full['MODEL_VAL_NEW']-df_full['MODEL_VAL_OLD']
        df_full = df_full.sort_values(by = 'Change').reset_index(drop = True)
        
        
        
        df_trim = df_full[abs(df_full['Change']) > email_threshold]
        df_trim = df_trim.sort_values(by = ['Change'])
        df_trim['Absolute_change'] = abs(df_trim['Change'])
        
        # plotly setup
        plot_rows= math.ceil((len(models))/2)
        
    fig = go.Figure()
    
    if len(models) < 2:
        plot_cols = 1
    else:    
        plot_cols = 2
        
    fig = make_subplots(rows=plot_rows, cols=plot_cols, subplot_titles = tuple(models),
                         x_title=f'Model value - {prev}',
                         y_title=f'Model value - {cur}')


    # add traces
    x = 0
    for i in range(1, plot_rows + 1):
        for j in range(1, plot_cols + 1):    
            if x < len(models) :
                names = models[x]
                df = df_trim.loc[df_trim['MODEL_NAME'] == models[x]]
                old_name = f"{names} value - {prev}"
                new_name = f"{names} value - {cur}"
                df.rename(columns={"MODEL_VAL_OLD": old_name, "MODEL_VAL_NEW": new_name}, inplace=True)
                count = 0

                #creating graph element
                fig.add_trace(px.scatter(df, x = old_name, y = new_name, size = 'MKT_VAL_USD',
                                 color="Absolute_change", hover_name="PROPER_NAME",size_max=(50),
                                 range_x=[0,1],range_y=[0,1],
                                 color_continuous_scale='portland',  title = names).data[0],
                              row=i,
                              col=j)

                count += 1

                fig.update_yaxes(range=[0, 1], row=i, col=j)
                fig.update_xaxes(range=[0, 1], row=i, col=j)
                #fig.layout.annotations[x].update(text=FSYM_ID_list_names[x])
                x=x+1
    chart_name = f"Rank Changes of Models from {prev} to {cur}"
    # add a shared colorbar
    fig.update_layout(coloraxis=dict(colorbar=dict(title="% Rank Change", yanchor='middle')), showlegend=False)
    #Adding a title
    fig.update_layout(title_text="Rank changes of Models", title_x=0.5, title_font=dict(size=20), title_y=0.95, title_xanchor='center')  

    return fig

    
@app.callback(Output("factor_plots_nath", "figure"), [Input("Company_filter_nath", "value")])

def update_charts_nath(Company_filter):
    if Company_filter is None:
        raise PreventUpdate
    FSYM_ID_list_names =  Company_filter
    FSYM_ID_list = []
    for i in FSYM_ID_list_names:
        FSYM_ID_list.append(company_names.loc[company_names['PROPER_NAME'] == i  , 'FSYM_REGIONAL_ID'].values[0])

    DF_dict ={}
    for i in range(0,len(FSYM_ID_list)):
        FSYM_ID_list[i] = "'{}'".format(FSYM_ID_list[i])
        DF_query = """select R.DATA_DATE, R.FSYM_REGIONAL_ID	, R.MODEL_VALUE	, RM.MODEL_NAME
        from QUANT.WORKING.DATA_MODELS AS R 
        LEFT JOIN QUANT.WORKING.REF_MODELS AS RM
        ON RM.MODEL_ID = R.MODEL_ID
        WHERE R.FSYM_REGIONAL_ID= """+FSYM_ID_list[i]+""" ORDER BY DATA_DATE DESC"""

        DF = pd.read_sql(DF_query , ctx)
        DF = DF.pivot_table(index = ['DATA_DATE'], values ='MODEL_VALUE' , columns = 'MODEL_NAME')
        DF= DF.reset_index(drop = False)
        DF_dict[FSYM_ID_list_names[i]] = DF
        
    models = ['Growth','Quality', 'Value', 'Value Rel']    
    colours = px.colors.qualitative.Plotly
    # plotly setup
    plot_rows= math.ceil((len(FSYM_ID_list_names))/2)
    
    if len(FSYM_ID_list_names)<=1:
        plot_cols = 1
    
    else:
        plot_cols = 2
    
    fig = make_subplots(rows=plot_rows, cols=plot_cols, subplot_titles = FSYM_ID_list_names)
    
    # add traces
    x = 0
    for i in range(1, plot_rows + 1):
        for j in range(1, plot_cols + 1):    
            if x < len(FSYM_ID_list_names) :
                names = FSYM_ID_list_names[x]
                df = DF_dict[names]
                count = 0
                for model in models:
                    if i == 1 and x == 0:
                        fig.add_trace(go.Scatter( x=df['DATA_DATE'], y = df[model], mode = 'lines',
                                                 legendgroup =  model, showlegend=True,
                                                 name = model, line=dict(color=colours[count])),
                                      row=i,
                                      col=j)
                    else:
                        fig.add_trace(go.Scatter( x=df['DATA_DATE'], y = df[model], mode = 'lines',
                                                 legendgroup =  model,
                                                 name = model, line=dict(color=colours[count]),  showlegend=False),
                                      row=i,
                                      col=j)
                    count += 1
      
                fig.update_yaxes(range=[0, 1], row=i, col=j)
                #fig.layout.annotations[x].update(text=FSYM_ID_list_names[x])
                x=x+1
    return fig

#################################Fabio####################################################################################
@app.callback(
    Output('dropdown-selection_2', 'options'),
    Input('dropdown-selection_1', 'value')
)
def update_dropdown_2_options(selected_value):
    universe_filter = universe[universe.FUND_ACCOUNTING_NAME == selected_value]
    options = [{'label': name, 'value': name} for name in sorted(universe_filter.INSTRUMENT_NAME.unique())]
    return options

@app.callback(
    Output('dropdown-selection_2', 'value'),
    Input('dropdown-selection_2', 'options')
)
def set_dropdown_2_value(options):
    if len(options) > 0:
        return options[0]['value']
    else:
        return None

@app.callback(
    Output('graph1', 'figure'),
    Input('dropdown-selection_1', 'value'),
    Input('dropdown-selection_2', 'value')
)
def update_graph1(selected_value_1, selected_value_2):
    universe_filter = universe[universe.FUND_ACCOUNTING_NAME == selected_value_1]
    universe_filter_2 = universe_filter[universe_filter.INSTRUMENT_NAME == selected_value_2]
    
    universe_filter_2 = universe_filter_2.sort_values(by=['POSITION_DATE'], ascending=True)
    universe_filter_2 = universe_filter_2.set_index('POSITION_DATE')
    universe_filter_2 = universe_filter_2.apply(lambda x: x.asfreq('D', method='ffill')).reset_index()
    
    universe_filter_2['Delta'] =  universe_filter_2.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=0)-universe_filter_2.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=1)
    universe_filter_2['Delta%'] =  (universe_filter_2.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=0)/universe_filter_2.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=1)-1)*100
    universe_filter_2.loc[universe_filter_2['Delta'] == 0,'Delta'] = np.nan
    universe_filter_2['Delta%'] = universe_filter_2['Delta%'].round(decimals=2)
    universe_filter_2['Delta%'] = universe_filter_2.agg('{0[Delta%]}%'.format, axis=1)
    universe_filter_2.loc[universe_filter_2['Delta%'] == 'nan%','Delta%'] = np.nan
    universe_filter_2.loc[universe_filter_2['Delta%'] == '0.0%','Delta%'] = np.nan
    
    fig = px.line(universe_filter_2, x="POSITION_DATE", y="LAST_PRICE",width=1800, height=400)#, text="Delta")
    fig.update_layout(xaxis_title=None, yaxis_title='Price', legend_title=None, legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    fig.update_traces(textposition='top center')
    fig.update_xaxes(showticklabels=False)
    
    # add vertical lines for positive delta values
    positive_delta = universe_filter_2[universe_filter_2['Delta'] > 0]
    for date in positive_delta['POSITION_DATE']:
        fig.add_vline(x=date, line_color='green')
        
    # add vertical lines for positive delta values
    positive_delta = universe_filter_2[universe_filter_2['Delta'] < 0]
    for date in positive_delta['POSITION_DATE']:
        fig.add_vline(x=date, line_color='red')

    return fig

@app.callback(
    Output('graph2', 'figure'),
    Input('dropdown-selection_1', 'value'),
    Input('dropdown-selection_2', 'value')
)
def update_graph2(selected_value_1, selected_value_2):
    universe_filter = universe[universe.FUND_ACCOUNTING_NAME == selected_value_1]
    universe_filter_2 = universe_filter[universe_filter.INSTRUMENT_NAME == selected_value_2]
    
    universe_filter_2 = universe_filter_2.sort_values(by=['POSITION_DATE'], ascending=True)
    universe_filter_2 = universe_filter_2.set_index('POSITION_DATE')
    universe_filter_2 = universe_filter_2.apply(lambda x: x.asfreq('D', method='ffill')).reset_index()
    
    universe_filter_2['Delta'] =  universe_filter_2.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=0)-universe_filter_2.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=1)
    universe_filter_2['Delta%'] =  (universe_filter_2.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=0)/universe_filter_2.groupby(['FUND_ACCOUNTING_CODE','ISIN_INSTRUMENT_REFERENCE'])['NUMBER_OF_SECURITIES'].shift(periods=1)-1)*100
    universe_filter_2.loc[universe_filter_2['Delta'] == 0,'Delta'] = np.nan
    universe_filter_2['Delta%'] = universe_filter_2['Delta%'].round(decimals=2)
    universe_filter_2['Delta%'] = universe_filter_2.agg('{0[Delta%]}%'.format, axis=1)
    # universe_filter_2['STRATEGY_WEIGHTING'] = universe_filter_2.agg('{0[STRATEGY_WEIGHTING]}%'.format, axis=1)
    universe_filter_2.loc[universe_filter_2['Delta%'] == 'nan%','Delta%'] = np.nan
    universe_filter_2.loc[universe_filter_2['Delta%'] == '0.0%','Delta%'] = np.nan
    universe_filter_2['STRATEGY_WEIGHTING'] = universe_filter_2['STRATEGY_WEIGHTING'].round(2)
    universe_filter_2.loc[universe_filter_2['Delta%'].notnull(),'Delta%'] = universe_filter_2['STRATEGY_WEIGHTING'].astype(str) + ' (' +  universe_filter_2['Delta%'] + ')'
    

    fig = px.area(universe_filter_2, x="POSITION_DATE", y="NUMBER_OF_SECURITIES",width=1800, height=300, text="Delta%", hover_data={"Delta%":False})
    fig.update_layout(xaxis_title=None, yaxis_title='Wgt% (RelDelta)', legend_title=None, legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))#,showlegend=False)
    fig.update_yaxes(range=[min(universe_filter_2['NUMBER_OF_SECURITIES'])-min(universe_filter_2['NUMBER_OF_SECURITIES'])/20, max(universe_filter_2['NUMBER_OF_SECURITIES'])+max(universe_filter_2['NUMBER_OF_SECURITIES'])/20])
    fig.update_traces(textfont_size=12, textposition='bottom center')
    
    return fig

def find_minimum_greater_date(date_list, given_date):
    given_datetime = given_date

    filtered_list = []
    
    for date_ in date_list:
        if date_ > given_datetime:
            filtered_list.append(date_)
    min_date = min(filtered_list)
    
    return min_date

def find_maximum_less_than_date(date_list, given_date):
    given_datetime = given_date

    filtered_list = []
    
    for date_ in date_list:
        if date_ < given_datetime:
            filtered_list.append(date_)
    min_date = max(filtered_list)
    
    return min_date

################################run app####################################################################################
if __name__ == "__main__":
    app.run(port = 56191, debug= True, use_reloader=False)
#    app.run_server(host="0.0.0.0", port="8050")
    #app.run_server(host="0.0.0.0", port="56175")




























