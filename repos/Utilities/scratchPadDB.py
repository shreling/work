# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 15:29:29 2021

@author: Jeremy.Humphries
"""

import matplotlib.pyplot as plty
import pandas as pd
import numpy as np
import databaseConnectionSnowflake as db
import databaseConnection


# =============================================================================

workingDirParam = "Q:\\Investment\\Securities\\Quant\\Data\\Benchmarks\\"
df_data_main = pd.read_excel(workingDirParam+"MSCI_FSYMID.xlsx")

companies = tuple(df_data_main["FSYM_PRIMARY_LISTING_ID"])

query = "select LTM_DER.DATE,LTM_DER.FSYM_ID, LTM_DER.FF_OPER_MGN from FACTSET.FF_V3.FF_BASIC_DER_LTM LTM_DER  where  LTM_DER.FSYM_ID in {}".format(companies)
query = query+" order by FSYM_ID, Date desc"

myArray = db.getData(query)

#Pivot the data - NOE WE NEED TO CHECK THAT ALL MONTHS ARE PRESENT
df2 = myArray.pivot(index='DATE', columns='FSYM_ID', values='FF_OPER_MGN')





unqStk = myArray["FSYM_ID"].unique()
myDateRange = pd.date_range(start=myArray["DATE"].min(), end=myArray["DATE"].max(), freq = 'M')

for tmpStk in unqStk:
    tmpIdx = np.array(myArray["FSYM_ID"]) == tmpStk
    tmpData = np.array(myArray)[tmpIdx,:]

    g = pd.to_datetime(tmpData[:,0])

same_rows = [a == b for a,b in zip(myDateRange, g)]
max_row = next(i for i, row in enumerate(reversed(same_rows)) if row == True)



fig = plty.figure()
plty.plot(myArray["DATE"], myArray["FF_OPER_MGN"])


# =============================================================================
"""Pull some data back from snowflake"""

query = """select 
                   DATE, FSYM_ID, FF_OPER_MGN
           from 
                   FACTSET.FF_V3.FF_BASIC_DER_LTM 
           where FSYM_ID in ('MH33D6-R', 'P8R3C2-R','HQ4DBK-R')    
           order by Date desc"""

myArray = db.getData(query)
myArray.set_index('DATE', inplace=True)
myArray.groupby('FSYM_ID')["FF_OPER_MGN"].plot(legend=False,title='Operating Margin')
# myArray.groupby('DATE')["FF_OPER_MGN"].median().plot(legend=False)


"""All of MSCI World"""           
query = "select DATE, FSYM_ID, FF_OPER_MGN from FACTSET.FF_V3.FF_BASIC_DER_LTM where FSYM_ID in {}".format(companies)          
myArray = db.getData(query)
myArray.set_index('DATE', inplace=True)
myArray.groupby('FSYM_ID')["FF_OPER_MGN"].median().plot(legend=False)
# myArray.groupby('DATE')["FF_OPER_MGN"].median().plot(legend=False)


# fig = plty.figure()
# plty.plot(myArray["DATE"], myArray["FF_OPER_MGN"])






import pandas as pd
import databaseConnection

serverName = 'MED-SQL01'
dbName = 'MED_EDW'


# =============================================================================
# Sample Query RIMES data from EDW

query = 'SELECT top 10 * FROM [rimes].[timeseries]'
myData = databaseConnection.getData(serverName, dbName, query)


# =============================================================================
# Pull back count of an index through time from EDW

query = '''SELECT Valuation_Date, count(security_weight) as count
FROM [MED_EDW].[rimes].[benchmark]
Where INDEX_SYMBOL = 'ACWI.R' and security_weight>0.0
group by Valuation_date
ORDER BY 1 desc'''

myData = databaseConnection.getData(serverName, dbName, query)

#Plot Data
#myData.info()
myData['Valuation_Date'] = pd.to_datetime(myData['Valuation_Date'], format= '%Y %m %d')
myData.plot(y='count', x='Valuation_Date', title='Count of MSCI ACWI Stocks through time')


# =============================================================================
# Pull back sum of an index through time from EDW

query = '''SELECT Valuation_Date, sum(security_weight) as sec_sum
FROM [MED_EDW].[rimes].[benchmark]
Where INDEX_SYMBOL = 'ACWI.R' and security_weight>0.0
group by Valuation_date
ORDER BY 1 desc'''

myData = databaseConnection.getData(serverName, dbName, query)

#Plot Data
#myData.info()
myData['Valuation_Date'] = pd.to_datetime(myData['Valuation_Date'], format= '%Y %m %d')
plt = myData.plot(y='sec_sum', x='Valuation_Date', title='Sum of MSCI ACWI through time')
plt.set_ylim([0,1.1])


# =============================================================================
# Pull back Latest ESG Data from EDW

query = '''select * from [MedDirectAccess].[stage].[MSCI_ESG_Characterstics] where ReportDate 
in (select max(ReportDate) from [MedDirectAccess].[stage].[MSCI_ESG_Characterstics])'''

myData = databaseConnection.getData(serverName, dbName, query)
#plt = myData.hist(column = 'ESG_Rating')

unqCompanies = myData['ISSUER_NAME'].unique()
unqRatings = myData['ESG_RATING'].unique()
valCount = myData['ESG_RATING'].value_counts()

myIdx = myData["ESG_RATING"]=="AAA"
test = myData[myIdx]
unqCompaniesAAA = test['ISSUER_NAME'].unique()



query = '''select * from [MedDirectAccess].[stage].[MSCI_ESG_Characterstics] where ReportDate 
in (select max(ReportDate) from [MedDirectAccess].[stage].[MSCI_ESG_Characterstics])'''

myData = databaseConnection.getData(serverName, dbName, query)
