# -*- coding: utf-8 -*-
"""
Created on Tue May 31 11:21:03 2022

@author: fabio.peterlin
"""

#import databaseConnectionSnowflake as db
import pandas as pd
import datetime as dt
dtime = dt.time()
now=dt.datetime.now()
now.isoformat()

date = str(now.strftime("%Y-%m-%d"))

universe = pd.read_pickle('Q:\\Investment\\Securities\\Quant\\Data\\Ecosystem Data\\Universe Files\\Universe_'+ date +'.pickle')
factors = pd.read_pickle('Q:\\Investment\\Securities\\Quant\\Data\\Ecosystem Data\\Constituents\\Factors_'+ date +'.pickle').rename(columns={'DATE':'FCTRS_DATE'})
prices = pd.read_pickle('Q:\\Investment\\Securities\\Quant\\Data\\Ecosystem Data\\Constituents\\AdjClosingPrice_'+ date +'_M.pickle').rename(columns={'Date':'PRICE_DATE','FSYM_ID':'FSYM_REGIONAL_ID'})

# get factors and prices by max date 
factors_last = factors.loc[factors.groupby('FSYM_REGIONAL_ID')['FCTRS_DATE'].idxmax()]

prices['PRICE_DATE'] = pd.to_datetime(prices['PRICE_DATE'])
prices_last = prices.loc[prices.groupby('FSYM_REGIONAL_ID')['PRICE_DATE'].idxmax()]

# merge universe with constituents
univ_const = universe.merge(factors_last, on = ['FSYM_REGIONAL_ID'], how = 'left')
univ_const = univ_const.merge(prices_last, on = ['FSYM_REGIONAL_ID'], how = 'left')

pd.to_pickle(univ_const, 'Q:\\Investment\\Securities\\Quant\\Data\\Ecosystem Data\\Universe Files\\Univ_Full_'+ date +'.pickle')
univ_const.to_excel('Q:\\Investment\\Securities\\Quant\\Data\\Ecosystem Data\\Universe Files\\Univ_Full_'+ date +'.xlsx')
