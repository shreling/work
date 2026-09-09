# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 16:09:30 2021

@author: Jeremy.Humphries
"""

import pyodbc
import pandas as pd

def getData(serverName, dbName, query):

    # =============================================================================
    # Example settings    
    # =============================================================================
    #   serverName = 'MED-SQL01'
    #   dbName = 'MED_EDW'
    #   query = 'SELECT top 10 * FROM [rimes].[timeseries]'
    
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=' +serverName+ ';'
                      'Database='+dbName+';'
                      'Trusted_Connection=yes;'
                      )
    data = pd.read_sql(query,conn)
    return data