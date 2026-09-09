# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 12:52:58 2023

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


from Backtester_engine import weighting_scheme


def create_input_attribution_df(backtest_df, quantile, model, by, weighting, start_YM, end_YM, port_weights = None):

    bin_col = model + '_bin'
    
    # Check if port_weights is None or if a series has been passed
    if port_weights is None:
        weights, log_optimiser = weighting_scheme(backtest_df, bin_col, weighting)
        port_weights = weights[weighting].reset_index(drop=True)

    backtest_df['Port_Wgt']=port_weights
    
    backtest_df['R_RETS_LOCAL_fwd'] = backtest_df.groupby('FSYM_REGIONAL_ID')['M_Return_Local'].shift(periods = -1)
    
    if weighting != 'Optimiser':
        backtest_df['Port_Wgt'] = np.where(backtest_df[bin_col]==quantile,backtest_df['Port_Wgt'],0)
    
    cols_needed = ['DATA_DATE', by, 'Port_Wgt', 'WGT', 'R_RETS_EUR_fwd', 'R_RETS_LOCAL_fwd']
    
    # Remove the columns we don't need
    portfolio_df = backtest_df[cols_needed]
    portfolio_df.columns = ['DATA_DATE', by, 'Port_Wgt', 'BMK_Wgt', 'Ret_Eur_Fwd', 'Ret_Local_Fwd']

    if type(portfolio_df['DATA_DATE'].iloc[0])==str:
        portfolio_df['YM'] = portfolio_df['DATA_DATE'].apply(lambda x: int(x[:4]+x[5:7]))
    else:
        portfolio_df['YM'] = portfolio_df['DATA_DATE'].dt.strftime('%Y%m').astype(int)
    
    portfolio_df = portfolio_df[(portfolio_df['YM']>=start_YM) & (portfolio_df['YM']<=end_YM)].reset_index(drop=True)
    portfolio_df = portfolio_df.drop(columns = 'YM')
    
    return portfolio_df
    
## This function will run attribution analysis on a dataframe
## portfolio_df should be the dataframe with the following columns : 'DATA_DATE', by, 'Bmk_Wgt', 'Port_Wgt', 'Ret_Eur_Fwd', 'Ret_Local_Fwd'
## by should be the grouping we're breaking up tyhe securities by (GICS_SECTOR, INDUSTRY, COUNTRY)....make sure this column is in the dataframe though

def run_attribution(portfolio_df, by):
    
    from itertools import product 
    combo_df = pd.DataFrame(product(portfolio_df['DATA_DATE'].unique(), portfolio_df[by].unique())).drop_duplicates()
    combo_df.columns = ['DATA_DATE', by]
    portfolio_df_date_group = combo_df.sort_values(by = ['DATA_DATE', by]).reset_index(drop=True)
    
    portfolio_df['Ret_Eur_Fwd'] = portfolio_df['Ret_Eur_Fwd'].fillna(0)
    portfolio_df['Ret_Local_Fwd'] = portfolio_df['Ret_Local_Fwd'].fillna(0)
    
    # Calculate the weight x return for port & bmk in eur and local currencies
    portfolio_df['prt_wgt_ret_eur']= portfolio_df['Port_Wgt'] * portfolio_df['Ret_Eur_Fwd']
    portfolio_df['bmk_wgt_ret_eur']= portfolio_df['BMK_Wgt'] * portfolio_df['Ret_Eur_Fwd']
    portfolio_df['prt_wgt_ret_local']= portfolio_df['Port_Wgt'] * portfolio_df['Ret_Local_Fwd']
    portfolio_df['bmk_wgt_ret_local']= portfolio_df['BMK_Wgt'] * portfolio_df['Ret_Local_Fwd']

    portfolio_df_held = portfolio_df[portfolio_df['Port_Wgt']>0].reset_index(drop=True)
        
    # Calculates the weight x return for the sum of all securities in each group for port & bmk in eur and local currencies
    def sum_prt_bmk_wgts_rets(row):
        mask = ((portfolio_df['DATA_DATE'] == row['DATA_DATE']) & (portfolio_df[by] == row[by]))
        matching_rows = portfolio_df[mask]
        return matching_rows['Port_Wgt'].sum(), matching_rows['BMK_Wgt'].sum(), matching_rows['prt_wgt_ret_eur'].sum(), matching_rows['bmk_wgt_ret_eur'].sum(), matching_rows['prt_wgt_ret_local'].sum(), matching_rows['bmk_wgt_ret_local'].sum()
    
    a = portfolio_df_date_group.apply(sum_prt_bmk_wgts_rets, axis=1)
    df = pd.DataFrame(a.tolist(), columns=['Port_Group_Wgt', 'BMK_Group_Wgt', 'Port_Group_Wgt_Ret_Eur', 'BMK_Group_Wgt_Ret_Eur', 'Port_Group_Wgt_Ret_Local', 'BMK_Group_Wgt_Ret_Local'])
    
    for c in ['Port_Group_Wgt', 'BMK_Group_Wgt']:
        portfolio_df_date_group[c] = df[c]
    for c in ['Port_Group_Wgt_Ret_Eur', 'Port_Group_Wgt_Ret_Local']:
        portfolio_df_date_group[c] = (df[c] / portfolio_df_date_group['Port_Group_Wgt']).fillna(0)
        portfolio_df_date_group[c + "_Real"] = (df[c]).fillna(0)
    for c in ['BMK_Group_Wgt_Ret_Eur', 'BMK_Group_Wgt_Ret_Local']:
        portfolio_df_date_group[c] = (df[c] / portfolio_df_date_group['BMK_Group_Wgt']).fillna(0)
        portfolio_df_date_group[c + "_Real"] = (df[c]).fillna(0)        
    
    df_dates = portfolio_df['DATA_DATE'].drop_duplicates().reset_index(drop=True).to_frame()
    
    def sum_bmk_wgts_held(row):
        mask = (portfolio_df_held['DATA_DATE'] == row['DATA_DATE'])
        matching_rows = portfolio_df_held[mask]
        return matching_rows['BMK_Wgt'].sum()
    
    df_dates['BMK_Wgt_Held'] = df_dates.apply(sum_bmk_wgts_held, axis=1)
    
    portfolio_df_date_group = portfolio_df_date_group.merge(df_dates, on = 'DATA_DATE', how = 'left')
    
    def cumulate_group_returns(df, by, column):
        first_group = df[by].iloc[0]
        df['returns_1'] = np.where(df[by]==first_group, df[column]+1,1)
        df[column+"_Cumm"] = df['returns_1'].transform(pd.Series.cumprod)-1
        df = df.drop(columns = 'returns_1')
        return df
    
    def cummulate_returns_per_group(df, by, return_col, cumm_returns_col):
        df['temp1'] = 1 + df[return_col]
        df[cumm_returns_col] = df.groupby(by)["temp1"].transform(pd.Series.cumprod)-1
        df = df.drop(columns = ['temp1'])
        return df
    
    portfolio_df_date_group = cummulate_returns_per_group(portfolio_df_date_group, by, "Port_Group_Wgt_Ret_Eur", "Port_Group_Wgt_Ret_Eur_Cumm")
    portfolio_df_date_group = cummulate_returns_per_group(portfolio_df_date_group, by, "BMK_Group_Wgt_Ret_Eur", "BMK_Group_Wgt_Ret_Eur_Cumm")
    portfolio_df_date_group = cummulate_returns_per_group(portfolio_df_date_group, by, "Port_Group_Wgt_Ret_Local", "Port_Group_Wgt_Ret_Local_Cumm")
    portfolio_df_date_group = cummulate_returns_per_group(portfolio_df_date_group, by, "BMK_Group_Wgt_Ret_Local", "BMK_Group_Wgt_Ret_Local_Cumm")
    
    portfolio_df_date_group = cummulate_returns_per_group(portfolio_df_date_group, by, "Port_Group_Wgt_Ret_Eur_Real", "Port_Group_Wgt_Ret_Eur_Cumm_Real")
    portfolio_df_date_group = cummulate_returns_per_group(portfolio_df_date_group, by, "BMK_Group_Wgt_Ret_Eur_Real", "BMK_Group_Wgt_Ret_Eur_Cumm_Real")
    portfolio_df_date_group = cummulate_returns_per_group(portfolio_df_date_group, by, "Port_Group_Wgt_Ret_Local_Real", "Port_Group_Wgt_Ret_Local_Cumm_Real")
    portfolio_df_date_group = cummulate_returns_per_group(portfolio_df_date_group, by, "BMK_Group_Wgt_Ret_Local_Real", "BMK_Group_Wgt_Ret_Local_Cumm_Real")
        
    # calculates the benchmark total return for a period
    def port_bmk_date_returns(row):
        mask = (portfolio_df['DATA_DATE'] == row['DATA_DATE'])
        matching_rows = portfolio_df[mask]
        return matching_rows['prt_wgt_ret_eur'].sum(), matching_rows['bmk_wgt_ret_eur'].sum(), matching_rows['prt_wgt_ret_local'].sum(), matching_rows['bmk_wgt_ret_local'].sum()
    
    df_dates = portfolio_df['DATA_DATE'].drop_duplicates().reset_index(drop=True).to_frame()
    
    a = df_dates.apply(port_bmk_date_returns, axis=1)
    df = pd.DataFrame(a.tolist(), columns=['Port_Date_Ret_Eur', 'BMK_Date_Ret_Eur', 'Port_Date_Ret_Local', 'BMK_Date_Ret_Local'])
    for c in ['Port_Date_Ret_Eur', 'BMK_Date_Ret_Eur', 'Port_Date_Ret_Local', 'BMK_Date_Ret_Local']:
        df_dates[c] = df[c]
    
    portfolio_df_date_group = portfolio_df_date_group.merge(df_dates, on = 'DATA_DATE', how = 'left')
    portfolio_df_date_group = portfolio_df_date_group.fillna(0)
    portfolio_df_date_group['Active Wgt'] = portfolio_df_date_group['Port_Group_Wgt'] - portfolio_df_date_group['BMK_Group_Wgt']
    
    first_group = portfolio_df_date_group[by].iloc[0]
    portfolio_df_date_group = cumulate_group_returns(portfolio_df_date_group, by, 'Port_Date_Ret_Eur')
    portfolio_df_date_group = cumulate_group_returns(portfolio_df_date_group, by, 'BMK_Date_Ret_Eur')
    portfolio_df_date_group = cumulate_group_returns(portfolio_df_date_group, by, 'Port_Date_Ret_Local')
    portfolio_df_date_group = cumulate_group_returns(portfolio_df_date_group, by, 'BMK_Date_Ret_Local')
    
    # calculate the selectiona nd allocation per date and per group
    portfolio_df_date_group['Selection_D_Group'] = portfolio_df_date_group['Port_Group_Wgt'] * (portfolio_df_date_group['Port_Group_Wgt_Ret_Local'] - portfolio_df_date_group['BMK_Group_Wgt_Ret_Local'])
    portfolio_df_date_group['Allocation_D_Group'] = (portfolio_df_date_group['Port_Group_Wgt'] -portfolio_df_date_group['BMK_Group_Wgt']) * (portfolio_df_date_group['BMK_Group_Wgt_Ret_Local'] - portfolio_df_date_group['BMK_Date_Ret_Local'])
    
    def cummulate_returns_per_group(df, by, return_col, cumm_returns_col):
        df['temp1'] = 1 + df[return_col]
        df[cumm_returns_col] = df.groupby(by)["temp1"].transform(pd.Series.cumprod)-1
        df = df.drop(columns = ['temp1'])
        return df
    
    portfolio_df_date_group = cummulate_returns_per_group(portfolio_df_date_group, by, "Selection_D_Group", "Selection_Group_Cumm")
    portfolio_df_date_group = cummulate_returns_per_group(portfolio_df_date_group, by, "Allocation_D_Group", "Allocation_Group_Cumm")
    portfolio_df_date_group['Currency_D_Group'] = (portfolio_df_date_group['Port_Group_Wgt_Ret_Eur_Real'] - portfolio_df_date_group['BMK_Group_Wgt_Ret_Eur_Real'])-(portfolio_df_date_group['Port_Group_Wgt_Ret_Local_Real'] - portfolio_df_date_group['BMK_Group_Wgt_Ret_Local_Real'])
    portfolio_df_date_group['Currency_Group_Cumm'] = (portfolio_df_date_group['Port_Group_Wgt_Ret_Eur_Cumm_Real'] - portfolio_df_date_group['BMK_Group_Wgt_Ret_Eur_Cumm_Real'])-(portfolio_df_date_group['Port_Group_Wgt_Ret_Local_Cumm_Real'] - portfolio_df_date_group['BMK_Group_Wgt_Ret_Local_Cumm_Real'])
    
       
    # portfolio_df_date_group['Currency_Group_Cumm'] = (portfolio_df_date_group['Port_Group_Wgt_Ret_Eur_Cumm'] - portfolio_df_date_group['BMK_Group_Wgt_Ret_Eur_Cumm'])-(portfolio_df_date_group['Port_Group_Wgt_Ret_Local_Cumm'] - portfolio_df_date_group['BMK_Group_Wgt_Ret_Local_Cumm'])
    
    # get the sum of the selection and allocation per date and bin. the sums will be the portfolio's selection and allocation per date
    def selec_alloc_d_group(row):
        mask = (portfolio_df_date_group['DATA_DATE'] == row['DATA_DATE'])
        matching_rows = portfolio_df_date_group[mask]
        return matching_rows['Selection_D_Group'].sum(), matching_rows['Allocation_D_Group'].sum()
    
    df_dates = portfolio_df['DATA_DATE'].drop_duplicates().reset_index(drop=True).to_frame()
    
    a = df_dates.apply(selec_alloc_d_group, axis=1)
    df = pd.DataFrame(a.tolist(), columns=['Selection_D_Group', 'Allocation_D_Group'])
    df_dates['Selection_D'] = df['Selection_D_Group']
    df_dates['Allocation_D'] = df['Allocation_D_Group']
    
    portfolio_df_date_group = portfolio_df_date_group.merge(df_dates, on = ['DATA_DATE'], how = 'left')
    
    portfolio_df_date_group = cumulate_group_returns(portfolio_df_date_group, by, 'Selection_D')
    portfolio_df_date_group = cumulate_group_returns(portfolio_df_date_group, by, 'Allocation_D')
    portfolio_df_date_group['Currency_D_Cumm'] = (portfolio_df_date_group['Port_Date_Ret_Eur_Cumm'] - portfolio_df_date_group['BMK_Date_Ret_Eur_Cumm'])-(portfolio_df_date_group['Port_Date_Ret_Local_Cumm'] - portfolio_df_date_group['BMK_Date_Ret_Local_Cumm'])
    
    port_att_df = portfolio_df_date_group.copy()
    port_att_df = port_att_df.rename(columns = {'Port_Date_Ret_Eur_Cumm' : 'Port Return Eur', 'BMK_Date_Ret_Eur_Cumm' : 'Bmk Return Eur', 'Selection_D_Cumm' : 'Selection Effect', 'Allocation_D_Cumm' : 'Allocation Effect', 'Currency_D_Cumm' : 'Currency', 'Port_Group_Wgt': 'Portfolio Wgt', 'BMK_Group_Wgt': 'Benchmark Wgt'})
    port_att_df['Active Return Eur'] = port_att_df['Port Return Eur'] - port_att_df['Bmk Return Eur']
    port_att_df['Unexplained'] = port_att_df['Active Return Eur'] - port_att_df['Selection Effect']- port_att_df['Allocation Effect']- port_att_df['Currency']
      
    ## This part makes the assumtion that the selection effect will extrapolate
    port_att_df['selec'] = abs(port_att_df['Selection Effect']) / (abs(port_att_df['Selection Effect']) + abs(port_att_df['Allocation Effect']))
    port_att_df['alloc'] = abs(port_att_df['Allocation Effect']) / (abs(port_att_df['Selection Effect']) + abs(port_att_df['Allocation Effect']))    
    port_att_df['Selection'] = port_att_df['Selection Effect'] + (port_att_df['Unexplained'] * (port_att_df['selec'] / (port_att_df['selec'] + port_att_df['alloc'])))
    port_att_df['Allocation'] = port_att_df['Allocation Effect'] + (port_att_df['Unexplained'] * (port_att_df['alloc'] / (port_att_df['selec'] + port_att_df['alloc'])))
    
    
    def sum_group_cumms(row):
        mask = (port_att_df['DATA_DATE'] == row['DATA_DATE'])
        matching_rows = port_att_df[mask]
        return matching_rows['Selection_Group_Cumm'].sum(), matching_rows['Allocation_Group_Cumm'].sum(), matching_rows['Currency_Group_Cumm'].sum()
    
    df_dates = pd.DataFrame(port_att_df['DATA_DATE'].drop_duplicates().reset_index(drop=True))
        
    a = df_dates.apply(sum_group_cumms, axis=1)
    df = pd.DataFrame(a.tolist(), columns=['Sum_Selection_Cumm', 'Sum_Allocation_Cumm', 'Sum_Currency_Cumm'])
    for c in ['Sum_Selection_Cumm', 'Sum_Allocation_Cumm', 'Sum_Currency_Cumm']:
        df_dates[c] = df[c]
        
    port_att_df_m = port_att_df.merge(df_dates, on = 'DATA_DATE', how = 'left')
    
    port_att_df_m['Group Selection'] = port_att_df_m['Selection_Group_Cumm'] / port_att_df_m['Sum_Selection_Cumm'] * port_att_df_m['Selection']
    port_att_df_m['Group Allocation'] = port_att_df_m['Allocation_Group_Cumm'] / port_att_df_m['Sum_Allocation_Cumm'] * port_att_df_m['Allocation']
    port_att_df_m['Group Currency'] = port_att_df_m['Currency_Group_Cumm'] / port_att_df_m['Sum_Currency_Cumm'] * port_att_df_m['Currency']
    
    df_attributions = port_att_df_m [['DATA_DATE', by, 'Portfolio Wgt', 'Benchmark Wgt', 'Active Wgt', 'Port Return Eur', 'Bmk Return Eur', 'Active Return Eur', 'Selection', 'Allocation', 'Currency', 'Group Selection', 'Group Allocation', 'Group Currency']]
    
    return df_attributions

def re_order_df(df_selections_bin_p):
    df_final_vals = df_selections_bin_p.iloc[-1:, 1:].T
    df_final_vals.columns = ['final_val']
    df_final_vals = df_final_vals.sort_values(by = 'final_val', ascending = False)
    order_list = []
    order_list.append(df_selections_bin_p.columns[0])
    order_list = order_list + df_final_vals.index.tolist()
    df_ordered = df_selections_bin_p[order_list]
    return df_ordered

def create_dataframes(df_attributions, by, model):
    
    groups = df_attributions[by].unique().tolist()
    
    # df_weights = df_attributions_bin.groupby(by)['Active Wgt'].mean().reset_index()
    df_weights = df_attributions.groupby(by)[['Portfolio Wgt', 'Benchmark Wgt', 'Active Wgt']].mean().reset_index()
    df_final_att_bin = df_attributions[df_attributions['DATA_DATE']==df_attributions['DATA_DATE'].iloc[df_attributions.shape[0]-1]]
    df_final_att_bin_trim = df_final_att_bin[[by, 'Group Selection', 'Group Allocation', 'Group Currency']]
    df_weights_s_all = df_weights.merge(df_final_att_bin_trim, on = by, how = 'left').fillna(0)
    df_weights_s_all.columns = [by, 'Avg Port Wgt', 'Avg Bmk Wgt', 'Avg Active Wgt', 'Selection Effect', 'Allocation Effect',  'Currency Effect']
    
    new_row = {by:'Total', 'Avg Port Wgt':df_weights_s_all['Avg Port Wgt'].sum(), 'Avg Bmk Wgt':df_weights_s_all['Avg Bmk Wgt'].sum(), 'Avg Active Wgt':df_weights_s_all['Avg Active Wgt'].sum(), 'Selection Effect':df_weights_s_all['Selection Effect'].sum(), 'Allocation Effect':df_weights_s_all['Allocation Effect'].sum(), 'Currency Effect':df_weights_s_all['Currency Effect'].sum()}
    new_row_df = pd.DataFrame([new_row])
    df_weights_s_all = pd.concat([df_weights_s_all, new_row_df], ignore_index=True)
    
    df_attributions_bin_d = df_attributions.drop_duplicates('DATA_DATE')
    df_attributions_bin_trim = df_attributions_bin_d[['DATA_DATE', 'Active Return Eur', 'Selection', 'Allocation', 'Currency']]
    
    df_selections_bin_p = pd.pivot(df_attributions, index = 'DATA_DATE', columns = by, values = 'Group Selection').reset_index(drop=False)
    df_selections_bin_p_sorted = re_order_df(df_selections_bin_p)
    df_selections_bin_p_sorted['Total'] = df_selections_bin_p_sorted[groups[0]].fillna(0)
    for s in groups[1:]:
        df_selections_bin_p_sorted['Total'] = df_selections_bin_p_sorted['Total'] + df_selections_bin_p_sorted[s].fillna(0)
    
    df_allocations_bin_p = pd.pivot(df_attributions, index = 'DATA_DATE', columns = by, values = 'Group Allocation').reset_index(drop=False)
    df_allocations_bin_p_sorted = re_order_df(df_allocations_bin_p)
    df_allocations_bin_p_sorted['Total'] = df_allocations_bin_p[groups[0]].fillna(0)
    for s in groups[1:]:
        df_allocations_bin_p_sorted['Total'] = df_allocations_bin_p_sorted['Total'] + df_allocations_bin_p_sorted[s].fillna(0)
        
    df_currencies_bin_p = pd.pivot(df_attributions, index = 'DATA_DATE', columns = by, values = 'Group Currency').reset_index(drop=False)
    df_currencies_bin_p_sorted = re_order_df(df_currencies_bin_p)
    df_currencies_bin_p_sorted['Total'] = df_currencies_bin_p[groups[0]].fillna(0)
    for s in groups[1:]:
        df_currencies_bin_p_sorted['Total'] = df_currencies_bin_p_sorted['Total'] + df_currencies_bin_p_sorted[s].fillna(0)    
    
    return df_attributions_bin_trim, df_selections_bin_p_sorted, df_allocations_bin_p_sorted, df_currencies_bin_p_sorted, df_weights_s_all


def show_att_graphs(dict_attributions):
    
    for b in dict_attributions:
        df = dict_attributions[b]
        
        fig = go.Figure()
        
        # Add Active Return as a line plot
        fig.add_trace(go.Scatter(
            x=df['DATA_DATE'],
            y=df['Active Return'],
            mode='lines',
            name='Active Return'
        ))
        
        
        fig.add_trace(go.Scatter(
            x=df['DATA_DATE'],
            y=df['Selection'],
            mode='lines',
            fill='tozeroy',  # fill to the x-axis
            name='Selection'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['DATA_DATE'],
            y=df['Allocation'],
            mode='lines',
            fill='tozeroy',  # fill to the x-axis
            name='Allocation'
        ))
        # Update layout and add labels
        fig.update_layout(
            title='Attribution for Bin ' + str(b),
            xaxis_title='Date',
            yaxis_title='Amount',
        )
        
        output_file = 'active_return_plot' + str(b) + '.html'
        pyo.plot(fig, filename=output_file)
        
    return True


def show_select_graphs(dict_selections):
    
    for b in dict_selections:
        df_select = dict_selections[b]
        
        df_select_copy = df_select.copy()
        df_select_copy = df_select_copy.ffill()[-1:]
        df_select_copy_p = df_select_copy.transpose().reset_index(drop=False)[1:]
        df_select_copy_p.columns = ['group','ret']
        df_select_copy_p_sort = df_select_copy_p.sort_values(by = 'ret', ascending = False)
        df_select_copy_p_sort = df_select_copy_p_sort[df_select_copy_p_sort ['group'] != 'Total'].reset_index(drop=True)
        fig = go.Figure()

        # Loop through each column (except 'DATA_DATE' and 'Total') and add it as a line plot
        for column in df_select_copy_p_sort['group']:
            fig.add_trace(go.Scatter(
                x=df_select['DATA_DATE'],
                y=df_select[column],
                mode='lines',
                name=column
            ))

        # Update layout and add labels
        fig.update_layout(
            title='Selections for bin ' + str(b),
            xaxis_title='Date',
            yaxis_title='Value',
        )

        # Save the plot as an HTML file
        output_file = 'time_series_graphs_' + str(b) + '.html'
        pyo.plot(fig, filename=output_file)
        
    return True
        
    
def show_selection_comparisons(dict_attributions):
    
    fig = go.Figure()
    
    for b in dict_attributions:
        df_select = dict_attributions[b]
        
        fig.add_trace(go.Scatter(
            x=df_select['DATA_DATE'],
            y=df_select['Selection'],
            mode='lines',
            name='Bin: ' + str(b)
        ))

        # Update layout and add labels
        fig.update_layout(
            title='Selection Effects for the bins',
            xaxis_title='Date',
            yaxis_title='Value',
        )

    # # Save the plot as an HTML file
    output_file = 'selection_effect_comparisons.html'
    pyo.plot(fig, filename=output_file)
        
    return True

