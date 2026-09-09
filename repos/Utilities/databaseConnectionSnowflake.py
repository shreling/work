# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 08:36:10 2021

@author: Jeremy.Humphries
"""

#!/usr/bin/env python
import snowflake.connector
import snowflake_connector_config as config
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas
from snowflake.connector.pandas_tools import pd_writer
import datetime as dt

def getData(query):
    
    ctx = snowflake.connector.connect(
        user= config.user,
        password= config.password,
        account= config.account
    )
    cs = ctx.cursor()
    
    try:   
        cs.execute(query)    
        data = cs.fetch_pandas_all()
            
    finally:
        cs.close()
        ctx.close()                
    
    return data

def check_Update_Date(database, schema, table):
    ctx = snowflake.connector.connect(
        user= config.user,
        password= config.password,
        account= config.account
    )
    cs = ctx.cursor()
    
    #Inserting database and schema names due to package limitations: https://github.com/snowflakedb/snowflake-connector-python/issues/1034
    cs.execute(f'USE DATABASE {database}')
    cs.execute(f'USE SCHEMA {schema}')
    
    col_query = f"""select COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}'"""
    
    try:   
        cs.execute(col_query)  
        data = cs.fetch_pandas_all()
    finally:
        cs.close()
        ctx.close()   
    
    if "UPDATE_DATE" in data['COLUMN_NAME'].tolist():
        return True
    else:
        return False
    
    
def setDataDF(df, table,database, schema):
    
    ctx = snowflake.connector.connect(
        user= config.user,
        password= config.password,
        account= config.account
    )
    cs = ctx.cursor()
    
    #Inserting database and schema names due to package limitations: https://github.com/snowflakedb/snowflake-connector-python/issues/1034
    cs.execute(f'USE DATABASE {database}')
    cs.execute(f'USE SCHEMA {schema}')
    
    update_date_check = check_Update_Date(database, schema, table)
    
    if update_date_check == True:
        now=dt.datetime.now()
        now.isoformat()
        df['UPDATE_DATE'] = now.date()
    
    success, nchunks, nrows, _ = write_pandas(ctx, df, table_name=table)
    # success, nchunks, nrows, _ = write_pandas(ctx, df, table_name=table, database='QUANT', schema='WORKING')
    return success


def getDataOld(query):
    
    ctx = snowflake.connector.connect(
        user= config.user,
        password= config.password,
        account= config.account
    )
    cs = ctx.cursor()
    
    try:
        #cs.execute("SELECT current_version()")
        #one_row = cs.fetchone()
   
        cs.execute(query)    
        data = cs.fetchall()    
        colnames = [desc[0] for desc in cs.description]
            
    finally:
        cs.close()
        ctx.close()
        
        
    #Convert to DataFrame    
    myArray = pd.DataFrame(data, columns=colnames)  
    
    return myArray


def setData(query):
    
    ctx = snowflake.connector.connect(
        user= config.user,
        password= config.password,
        account= config.account
    )
    cs = ctx.cursor()
    
    try:   
        cs.execute(query)    
            
    finally:
        cs.close()
        ctx.close()        
      
def deleteData(query):
    
    ctx = snowflake.connector.connect(
        user= config.user,
        password= config.password,
        account= config.account
    )
    cs = ctx.cursor()
    
    try:   
        cs.execute(query)
                
    finally:
        cs.close()
        ctx.close()    
        
    return True

    
def writeDF(df, tableName, schemaName):
    
    #We need to miggrate over to updated version of python snowflake connecter which deals with pandas data frames natively
    ctx = snowflake.connector.connect(
        user= config.user,
        password= config.password,
        account= config.account
    )
    cs = ctx.cursor()
    
    try:   
        df.to_sql(tableName, ctx,schema = schemaName, if_exists='fail', index=False, method=pd_writer)
        # df.to_sql(tableName, engine,schema = schemaName, if_exists='fail', index=False, method=pd_writer)
        # success, nchunks, nrows, _ = write_pandas(ctx, df, tableName, schema = schemaName)  
            
    finally:
        cs.close()
        ctx.close()    
        
    
def getTableStructure(database, schema):
    
    ctx = snowflake.connector.connect(
        user= config.user,
        password= config.password,
        account= config.account
    )
    cs = ctx.cursor()
    data = pd.DataFrame()
    
    
    try:   
        cs.execute(f'USE DATABASE {database}')
        cs.execute(f"""SELECT TABLE_NAME, ORDINAL_POSITION, COLUMN_NAME, DATA_TYPE
                    FROM 
                    INFORMATION_SCHEMA.COLUMNS
                    WHERE 
                    TABLE_CATALOG = '{database}'
                    AND TABLE_SCHEMA = '{schema}'
                    ORDER BY TABLE_NAME, ORDINAL_POSITION""")
        data = cs.fetch_pandas_all()
        
    finally:
        cs.close()
        ctx.close()    
        
    return data
    

""" BELOW IS AN EXAMPLE OF HOW TO UPLOAD DATAFRAME USING PANDAS DIRECTLY
import pandas
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
import snowflake_connector_config as config
import pandas as pd


# Create the connection to the Snowflake database.
cnx = snowflake.connector.connect(
    user= config.user,
    password= config.password,
    account= config.account,
    database='QUANT',
    schema = 'WORKING',
)

# Create a random dataframe
df = pandas.DataFrame([('Mark', 10), ('Luke', 20)], columns=['HELLO', 'HELLO2'])

# Write the data from the DataFrame to the table named "TEST_NATHAN".
success, nchunks, nrows, _ = write_pandas(cnx, df, 'TEST_NATHAN')

"""