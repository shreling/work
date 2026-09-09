# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 17:08:01 2024

@author: cillian.byrne
"""


import pandas as pd
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo
import datetime as dt
import pickle
import os
import sys

# sys.path.append(r'C:\Users\cillian.byrne\source\repos\Investments-Quant\Backtester')
# sys.path.append(r'C:\Users\cillian.byrne\Source\Repos\Investments-Quant\Utilities')

# # from Backtester_engine import weighting_scheme

# backtest_path = r"Q:\Investment\Securities\Quant\Data\2. Backtesting\Backtest Results\Pickle_Files\Full_backtest_MSCI World2024-09-09_Financials.pickle"
# bt_data = pd.read_pickle(backtest_path)

# by = 'GICS_INDUSTRY'
# wgt_col = 'Optimised_wgt_50Qual_25Growth_25Val'
# start_YM = 200001
# end_YM = 202501


def create_input_attribution_df(bt_data, wgt_col, by, start_YM, end_YM):

    bt_data['YM'] = bt_data['DATA_DATE'].dt.strftime('%Y%m').astype(int)
    bt_data_trim = bt_data[(bt_data['YM']>=start_YM) & (bt_data['YM']<=end_YM)].reset_index(drop=True)
    cols_needed = ['DATA_DATE', by, 'FSYM_REGIONAL_ID', 'PROPER_NAME', wgt_col, 'WGT', 'R_RETS_EUR_fwd']
    bt_data_trim = bt_data_trim[cols_needed]
    bt_data_trim.columns = ['DATA_DATE', by, 'FSYM_REGIONAL_ID', 'PROPER_NAME', 'Port_Wgt', 'Bmk_Wgt', 'Ret_Eur_Fwd']
        
    # make sure the port and bmk weights add to 100
    port_df = bt_data_trim.groupby('DATA_DATE')['Port_Wgt'].sum().reset_index(drop=False)
    port_df.columns = ['DATA_DATE','Sum_Port_Wgt']
    
    bmk_df = bt_data_trim.groupby('DATA_DATE')['Bmk_Wgt'].sum().reset_index(drop=False)
    bmk_df.columns = ['DATA_DATE','Sum_Bmk_Wgt']
    
    bt_data_trim = bt_data_trim.merge(port_df, on = 'DATA_DATE', how = 'left').merge(bmk_df, on = 'DATA_DATE', how = 'left')
    bt_data_trim['Port_Wgt'] = bt_data_trim['Port_Wgt']/bt_data_trim['Sum_Port_Wgt']
    bt_data_trim['Bmk_Wgt'] = bt_data_trim['Bmk_Wgt']/bt_data_trim['Sum_Bmk_Wgt']
    
    bt_data_trim = bt_data_trim.drop(columns = ['Sum_Port_Wgt', 'Sum_Bmk_Wgt'])
    
    return bt_data_trim


## This function will run attribution analysis on a dataframe
## dc_df_trim_2 should be the dataframe with the following columns : 'DATA_DATE', by, 'Port_bins', 'Bmk_Wgt', 'Port_Wgt', 'Ret_Eur_Fwd'
## by should be the grouping we're breaking up tyhe securities by (GICS_SECTOR, INDUSTRY, COUNTRY)....make sure this column is in the dataframe though
## bins is a list of what bins to run the analysis on (1,2,3 for example)
def run_attribution(bt_data_trim, by):
            
    bt_data_trim['Ret_Eur_Fwd'] = bt_data_trim['Ret_Eur_Fwd'].fillna(0)
    
    bt_data_trim['Port_wgt_ret'] = bt_data_trim['Port_Wgt']*bt_data_trim['Ret_Eur_Fwd']
    bt_data_trim['Bmk_wgt_ret'] = bt_data_trim['Bmk_Wgt']*bt_data_trim['Ret_Eur_Fwd']
    
    port_return_df = bt_data_trim.groupby('DATA_DATE')['Port_wgt_ret'].sum().reset_index(drop=False).rename(columns = {'Port_wgt_ret': 'Port_Ret_Date'})
    port_return_df['Port_Ret_Date_1']=1+port_return_df['Port_Ret_Date']
    port_return_df['Port_Ret_Cumm'] = port_return_df['Port_Ret_Date_1'].transform(pd.Series.cumprod) - 1
    port_return_df = port_return_df.drop(columns = 'Port_Ret_Date_1')
    
    bmk_return_df = bt_data_trim.groupby('DATA_DATE')['Bmk_wgt_ret'].sum().reset_index(drop=False).rename(columns = {'Bmk_wgt_ret': 'Bmk_Ret_Date'})
    bmk_return_df['Bmk_Ret_Date_1']=1+bmk_return_df['Bmk_Ret_Date']
    bmk_return_df['Bmk_Ret_Cumm'] = bmk_return_df['Bmk_Ret_Date_1'].transform(pd.Series.cumprod) - 1
    bmk_return_df= bmk_return_df.drop(columns = 'Bmk_Ret_Date_1')
    
    port_return_group_df = bt_data_trim.groupby(['DATA_DATE',by])['Port_wgt_ret'].sum().reset_index(drop=False).rename(columns = {'Port_wgt_ret': 'Port_Ret_Group_Date'})
    bmk_return_group_df = bt_data_trim.groupby(['DATA_DATE',by])['Bmk_wgt_ret'].sum().reset_index(drop=False).rename(columns = {'Bmk_wgt_ret': 'Bmk_Ret_Group_Date'})
    
    
    
    port_wgt_df = bt_data_trim.groupby(['DATA_DATE',by])['Port_Wgt'].sum().reset_index(drop=False).rename(columns = {'Port_Wgt': 'Port_Wgt_Date'})
    bmk_wgt_df = bt_data_trim.groupby(['DATA_DATE',by])['Bmk_Wgt'].sum().reset_index(drop=False).rename(columns = {'Bmk_Wgt': 'Bmk_Wgt_Date'})
    
    df_combined = bt_data_trim[['DATA_DATE',by]].drop_duplicates()
    
    df_combined = df_combined.merge(port_wgt_df, on = ['DATA_DATE',by], how = 'left')
    df_combined = df_combined.merge(bmk_wgt_df, on = ['DATA_DATE',by], how = 'left')
    
    df_combined = df_combined.merge(port_return_group_df, on = ['DATA_DATE',by], how = 'left')
    df_combined = df_combined.merge(bmk_return_group_df, on = ['DATA_DATE',by], how = 'left')
    
    df_combined = df_combined.merge(port_return_df, on = 'DATA_DATE', how = 'left')
    df_combined = df_combined.merge(bmk_return_df, on = 'DATA_DATE', how = 'left')
    
    df_combined = df_combined.sort_values(by = ['DATA_DATE', by]).reset_index(drop=True)
    
    df_combined['Active_Wgt_Date'] = df_combined['Port_Wgt_Date']-df_combined['Bmk_Wgt_Date']
    
    df_combined['Port_Ret_Group_Date_Total'] = np.where(df_combined['Port_Wgt_Date']==0,0,df_combined['Port_Ret_Group_Date']/df_combined['Port_Wgt_Date'])
    df_combined['Bmk_Ret_Group_Date_Total'] = np.where(df_combined['Bmk_Wgt_Date']==0,0,df_combined['Bmk_Ret_Group_Date']/df_combined['Bmk_Wgt_Date'])
    
    df_combined['Selec_Group_Date'] = df_combined['Port_Wgt_Date']*(df_combined['Port_Ret_Group_Date_Total']-df_combined['Bmk_Ret_Group_Date_Total'])
    df_combined['Alloc_Group_Date'] = df_combined['Active_Wgt_Date']*(df_combined['Bmk_Ret_Group_Date_Total']-df_combined['Bmk_Ret_Date'])
    
    
    # The df_security dataframe will show the selection effects of the securities
    df_security = bt_data_trim[['DATA_DATE', by, 'FSYM_REGIONAL_ID', 'PROPER_NAME', 'Port_Wgt', 'Bmk_Wgt', 'Ret_Eur_Fwd']].merge(df_combined[['DATA_DATE', by, 'Bmk_Ret_Group_Date_Total']], on = ['DATA_DATE', by], how = 'left')
    df_security['Act_Wgt'] = df_security['Port_Wgt']-df_security['Bmk_Wgt']
    df_security['Selection']=df_security['Act_Wgt']*(df_security['Ret_Eur_Fwd']-df_security['Bmk_Ret_Group_Date_Total'])
    
    
    selec_alloc_per_group = df_combined[['DATA_DATE',by, 'Selec_Group_Date','Alloc_Group_Date']]
    selec_alloc_per_group.columns = ['DATA_DATE',by, 'Selection','Allocation']
    
    ## Now we want to combine all the cummulative data
    
    port_return_df = bt_data_trim.groupby('DATA_DATE')['Port_wgt_ret'].sum().reset_index(drop=False).rename(columns = {'Port_wgt_ret': 'Port_Ret_Date'})
    port_return_df['Port_Ret_Date_1']=1+port_return_df['Port_Ret_Date']
    port_return_df['Port_Ret_Cumm'] = port_return_df['Port_Ret_Date_1'].transform(pd.Series.cumprod) - 1
    port_return_df = port_return_df.drop(columns = 'Port_Ret_Date_1')
    
    bmk_return_df = bt_data_trim.groupby('DATA_DATE')['Bmk_wgt_ret'].sum().reset_index(drop=False).rename(columns = {'Bmk_wgt_ret': 'Bmk_Ret_Date'})
    bmk_return_df['Bmk_Ret_Date_1']=1+bmk_return_df['Bmk_Ret_Date']
    bmk_return_df['Bmk_Ret_Cumm'] = bmk_return_df['Bmk_Ret_Date_1'].transform(pd.Series.cumprod) - 1
    bmk_return_df= bmk_return_df.drop(columns = 'Bmk_Ret_Date_1')
    
    df_combined_selec = df_combined.groupby('DATA_DATE')['Selec_Group_Date'].sum().reset_index(drop=False)
    df_combined_selec['Selec_Group_Date_1']=1+df_combined_selec['Selec_Group_Date']
    df_combined_selec['Selec_Cumm'] = df_combined_selec['Selec_Group_Date_1'].transform(pd.Series.cumprod) - 1
    df_combined_selec = df_combined_selec.drop(columns = ['Selec_Group_Date_1','Selec_Group_Date'])
    
    df_combined_alloc = df_combined.groupby('DATA_DATE')['Alloc_Group_Date'].sum().reset_index(drop=False)
    df_combined_alloc['Alloc_Group_Date_1']=1+df_combined_alloc['Alloc_Group_Date']
    df_combined_alloc['Alloc_Cumm'] = df_combined_alloc['Alloc_Group_Date_1'].transform(pd.Series.cumprod) - 1
    df_combined_alloc = df_combined_alloc.drop(columns = ['Alloc_Group_Date_1','Alloc_Group_Date'])
    
   
    df_cumm_combined = bt_data_trim[['DATA_DATE']].drop_duplicates()
    df_cumm_combined = df_cumm_combined.merge(port_return_df[['DATA_DATE','Port_Ret_Cumm']], on = 'DATA_DATE', how = 'left')
    df_cumm_combined = df_cumm_combined.merge(bmk_return_df[['DATA_DATE','Bmk_Ret_Cumm']], on = 'DATA_DATE', how = 'left')
    df_cumm_combined = df_cumm_combined.merge(df_combined_selec, on = 'DATA_DATE', how = 'left')
    df_cumm_combined = df_cumm_combined.merge(df_combined_alloc, on = 'DATA_DATE', how = 'left')
    df_cumm_combined['Active_Ret_Cumm'] = df_cumm_combined['Port_Ret_Cumm']-df_cumm_combined['Bmk_Ret_Cumm']
    df_cumm_combined['Unexplained'] = df_cumm_combined['Active_Ret_Cumm']-df_cumm_combined['Alloc_Cumm']-df_cumm_combined['Selec_Cumm']
    
    df_cumm_combined['Selec_Cumm_Adj'] = df_cumm_combined['Selec_Cumm']+(abs(df_cumm_combined['Selec_Cumm'])/((abs(df_cumm_combined['Selec_Cumm'])+abs(df_cumm_combined['Alloc_Cumm'])))*(df_cumm_combined['Unexplained']))
    df_cumm_combined['Alloc_Cumm_Adj'] = df_cumm_combined['Alloc_Cumm']+(abs(df_cumm_combined['Alloc_Cumm'])/((abs(df_cumm_combined['Selec_Cumm'])+abs(df_cumm_combined['Alloc_Cumm'])))*(df_cumm_combined['Unexplained']))
    
    df_cumm_combined = df_cumm_combined.sort_values(by = 'DATA_DATE').reset_index(drop=True)
    
    
    df_selec_group = df_combined.groupby(by)['Selec_Group_Date'].sum().reset_index(drop=False).rename(columns = {'Selec_Group_Date':'Selec_Group_Total'})
    df_alloc_group = df_combined.groupby(by)['Alloc_Group_Date'].sum().reset_index(drop=False).rename(columns = {'Alloc_Group_Date':'Alloc_Group_Total'})
    
    selec = df_cumm_combined['Selec_Cumm_Adj'].iloc[df_cumm_combined['Selec_Cumm_Adj'].shape[0]-1]
    alloc = df_cumm_combined['Alloc_Cumm_Adj'].iloc[df_cumm_combined['Alloc_Cumm_Adj'].shape[0]-1]
    
    df_selec_alloc = df_selec_group.merge(df_alloc_group, on = by, how = 'outer')
    df_selec_alloc['Selec_Group_ABS']=abs(df_selec_alloc['Selec_Group_Total'])
    df_selec_alloc['Alloc_Group_ABS']=abs(df_selec_alloc['Alloc_Group_Total'])
    df_selec_alloc['Selec_Group_Total_Adj'] = selec*df_selec_alloc['Selec_Group_ABS']/sum(df_selec_alloc['Selec_Group_ABS'])
    df_selec_alloc['Alloc_Group_Total_Adj'] = alloc*df_selec_alloc['Alloc_Group_ABS']/sum(df_selec_alloc['Alloc_Group_ABS'])
    
    return df_cumm_combined, df_selec_alloc, selec_alloc_per_group, df_security
  
    
def show_att_graphs(df_cumm_combined, by):
    
    fig = go.Figure()
        
        # Add Active Return as a line plot
    fig.add_trace(go.Scatter(
        x=df_cumm_combined['DATA_DATE'],
        y=df_cumm_combined['Active_Ret_Cumm'],
        mode='lines',
        name='Active Return'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_cumm_combined['DATA_DATE'],
        y=df_cumm_combined['Selec_Cumm_Adj'],
        mode='lines',
        name='Selection Effect'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_cumm_combined['DATA_DATE'],
        y=df_cumm_combined['Alloc_Cumm_Adj'],
        mode='lines',
        name='Allocation Effect'
    ))
    
        
    fig.update_layout(
        title='Total Attribution per '+str(by),
        xaxis_title='Date',
        yaxis_title='Return',
    )
    
    fig.show()
        
    output_file = 'active_return_plot.html'
    pyo.plot(fig, filename=output_file)
        
    return True



# def show_brinson(df_selec_alloc, by):
    
#     df_selec_alloc = df_selec_alloc.sort_values(by = 'Selec_Group_Total_Adj').reset_index(drop=True)
#     fig = go.Figure(data=[
#         go.Bar(name='Selection', y=df_selec_alloc[by], x=df_selec_alloc['Selec_Group_Total_Adj'], orientation='h'),
#         go.Bar(name='Allocation', y=df_selec_alloc[by], x=df_selec_alloc['Alloc_Group_Total_Adj'], orientation='h')
#     ])
    
#     # Set the axis labels and title
#     fig.update_layout(yaxis_title='', xaxis_title='', title='Brinson Attribution per '+str(by))
    
#     fig.update_layout(legend=dict(
#     orientation="h",
#     yanchor="bottom",
#     y=1.02,
#     xanchor="center",
#     x=0.5
#     ))
    
#     fig.show()
        
#     output_file = 'brinson.html'
#     pyo.plot(fig, filename=output_file)
    
#     return True


# def show_selections(selec_alloc_per_group, by):
    
#     total_selec = selec_alloc_per_group.groupby('DATA_DATE')['Selection'].sum().reset_index(drop=False)
#     group_selec = selec_alloc_per_group.pivot(index = 'DATA_DATE', columns = by, values = 'Selection').reset_index(drop=False)
    
#     fig_total = go.Figure()
        
#         # Add Active Return as a line plot
#     fig_total.add_trace(go.Bar(
#         x=total_selec['DATA_DATE'],
#         y=total_selec['Selection'],
#         name='Total Selection'
#     ))
    
#     fig_total.update_layout(
#             title='Total Selection Effect',
#             xaxis_title='Date',
#             yaxis_title='Return',
#             barmode='group'  # Optional: to group bars together
#             )
    
#     fig_total.show()
    
#     groups = list(group_selec.columns)[1:]
    
#     fig_per_g = go.Figure()
        
#         # Add Active Return as a line plot
#     fig_per_g.add_trace(go.Bar(
#         x=group_selec['DATA_DATE'],
#         y=group_selec[groups[0]],
#         name=groups[0]
#     ))
    
#     for i in range(1,len(groups)):
#         fig_per_g.add_trace(go.Bar(
#             x=group_selec['DATA_DATE'],
#             y=group_selec[groups[i]],
#             name=groups[i]
#             ))
        
#     fig_per_g.update_layout(
#             title='Selection Effect per ' + str(by),
#             xaxis_title='Date',
#             yaxis_title='Return',
#             barmode='group'  # Optional: to group bars together
#             )
        
#     fig_per_g.show()
    
#     return True
    


# bt_data_trim = create_input_attribution_df(bt_data, wgt_col, by, start_YM, end_YM)
# df_cumm_combined, df_selec_alloc, selec_alloc_per_group, df_security = run_attribution(bt_data_trim, by)

# test = pd.read_pickle(r"C:\Users\cillian.byrne\OneDrive - Mediolanum International Funds\Documents\APEX_Helper\test.pickle")

# show_att_graphs(df_cumm_combined, by)
# show_brinson(df_selec_alloc, by)
# show_selections(selec_alloc_per_group, by)

# df_security_total = df_security.groupby([by, 'FSYM_REGIONAL_ID', 'PROPER_NAME'])['Selection'].sum().reset_index(drop=False)