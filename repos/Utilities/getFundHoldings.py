# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 15:37:54 2022

@author: fabio.peterlin
"""

import pandas as pd
import pyodbc
import Utilities.databaseConnectionSnowflake as db

# set variables 
NAVdate = '06-Apr-2022' 
FundCode = '4223'

# querying data from Snowflake
query = """SELECT "NAV Date" AS NAV_date
,RIGHT ("Fund Code",4) AS Ptfl_Code
, "Fund Name" AS Ptfl_Name
, "Manager Code" AS Del_Code
, "Instrument Description" AS sub_Des
, "ISIN code" AS sub_ISIN
, "Quantity" AS sub_Size
, "% of Fund Assets" AS sub_Weight
, "Market Value in Fund Currency" AS sub_MktVal
FROM DEV_MED_EDW.STAGE."s_rbc_xcp2p018portfo"
WHERE "NAV_DATE" in ('""" + NAVdate + """')
AND RIGHT ("Fund Code",4) in (""" + FundCode + """)
AND "Sub Type MDF" not in ('ETF', 'FCP', 'SIC');"""

myArray = db.getData(query)
myArray = myArray.assign(DEL_CODE = pd.to_numeric(myArray["DEL_CODE"]))

# querying data from DWH
conn = pyodbc.connect('Driver={SQL Server};' 'Server=MED-SQL01;' 'Database=MED_EDW;' 'Trusted_Connection=yes;')

delMap = pd.read_sql_query('SELECT * FROM MedDirectAccess.stage.delegate_map', conn)
delMap = (delMap
          .filter(items = ['DelCode','mgrName','DBCode','AssetClass','Style'])
          .assign(DBCode = delMap["DBCode"].astype(str))
          .rename(columns={"DelCode":"DEL_CODE"}))

FundCodeDB = 'DB'+FundCode
delMap = delMap[(delMap.DBCode == FundCodeDB)]
delMap = delMap.assign(DEL_CODE = pd.to_numeric(delMap["DEL_CODE"]))

# merging tables
fullPtf = (myArray
           .merge(delMap, on='DEL_CODE', how='left'))

fullPtf['ID'] = fullPtf['mgrName'] + ' ' + fullPtf['AssetClass'] + ' ' + fullPtf['Style']

delPtf = (fullPtf
         .assign(NAV_DATE = pd.to_datetime(fullPtf['NAV_DATE'], infer_datetime_format=True))
         .assign(NAV_DATE = pd.to_datetime(fullPtf['NAV_DATE']).dt.strftime('%m-%d-%Y'))
         .assign(SUB_MKTVAL = pd.to_numeric(fullPtf["SUB_MKTVAL"]))
         .assign(SUB_SIZE = pd.to_numeric(fullPtf["SUB_SIZE"]))
         .assign(SUB_WEIGHT = pd.to_numeric(fullPtf["SUB_WEIGHT"]))
         .rename(columns={"SUB_ISIN":"ISIN"}))

# recalculate weights
delPtf['Weights'] = (delPtf
          .groupby(['NAV_DATE','ID'])['SUB_MKTVAL']
          .transform(lambda x: x/x.sum()))

delPtf = (delPtf
          .filter(items = ['NAV_DATE','PTFL_NAME','ID','SUB_DES','ISIN','SUB_SIZE','Weights']))