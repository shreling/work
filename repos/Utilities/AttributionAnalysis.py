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

sys.path.append(r'C:\Users\cillian.byrne\source\repos\Investments-Quant\Backtester')
sys.path.append(r'C:\Users\cillian.byrne\Source\Repos\Investments-Quant\Utilities')

from Backtester_engine import weighting_scheme

backtest_path = r'Q:\Investment\Securities\Quant\Data\2. Backtesting\Backtest Results\Pickle_Files\Full_backtest_MSCI World_Energy_Utilities_2023-10-23ALL.pickle'
attribution_folder = r'Q:\Investment\Securities\Quant\Data\2. Backtesting\Backtest Results\Pickle_Files\Attribution Output'


by = 'GICS_SECTOR'
model = 'D_50Qual_25Growth_25Val'
bins = ['1']
start_YM = 201001
end_YM = 202201
timer = True
weighting = 'Equal Overweight'


s_bins = ''
for b in bins:
    s_bins=s_bins+str(b)

last_backslash_index = backtest_path.rfind("\\")
#sub_string = input_string[last_backslash_index + 1:]
backtest_pickle = backtest_path[last_backslash_index + 1:]
backtest_name = backtest_pickle[:-7] 

attribution_name = backtest_name + "_" + model + "_" + by + "_" + s_bins + "_" + str(start_YM) + "_" + str(end_YM)
attribution_path = attribution_folder + '\\' + attribution_name + r'.pickle'

input_string = backtest_path[:-7]
last_backslash_index = input_string.rfind("\\")  # Find the index of the last "\"


# def create_bbg_test_file(backtest_df, model, by, bins, weighting, start_YM, end_YM, timer):

#     bin_col = model + '_bin'
    
#     weights, log_optimiser = weighting_scheme(backtest_df, bin_col, [weighting])
#     port_weights = weights[weighting].reset_index(drop=True)
#     backtest_df['Port_Wgt']=port_weights
    
#     cols_needed = ['DATA_DATE', by, bin_col, 'FSYM_REGIONAL_ID', 'WGT', 'ISIN', 'Port_Wgt', 'R_RETS_EUR_fwd']
#     dc_df_trim_2 = backtest_df[cols_needed]

#     dc_df_trim_2_bins = dc_df_trim_2[dc_df_trim_2[bin_col].isin(bins)].reset_index(drop=True)
#     #dc_df_trim_2_grouped = dc_df_trim_2_bins.groupby(['DATA_DATE', by, bin_col])['Port_Wgt'].sum().reset_index(drop=False).rename(columns = {'Port_Wgt': 'PORT_GROUP_WGT'})
#     #dc_df_trim_2_grouped = dc_df_trim_2_grouped[dc_df_trim_2_grouped[bin_col].isin(bins)].reset_index(drop=True)
#     dc_df_trim_2_bins['YM'] = dc_df_trim_2_bins['DATA_DATE'].dt.strftime('%Y%m').astype(int)
#     dc_df_trim_2_bins = dc_df_trim_2_bins[(dc_df_trim_2_bins['YM']>=start_YM) & (dc_df_trim_2_bins['YM']<=end_YM)]
#     dc_df_trim_2_bins = dc_df_trim_2_bins.drop(columns = 'YM')
    
#     return dc_df_trim_2_bins


def create_input_attribution_df(backtest_df, model, by, weighting, start_YM, end_YM):

    bin_col = model + '_bin'
    
    # calculate the weights for every stock based on the bins they are in
    weights, log_optimiser = weighting_scheme(backtest_df, bin_col, [weighting])
    port_weights = weights[weighting].reset_index(drop=True)
    backtest_df['Port_Wgt']=port_weights
    
    cols_needed = ['DATA_DATE', by, bin_col, 'WGT', 'Port_Wgt', 'R_RETS_EUR_fwd']
    dc_df_trim_2 = backtest_df[cols_needed]
    dc_df_trim_2.columns = ['DATA_DATE', by, 'Port_bins', 'Bmk_Wgt', 'Port_Wgt', 'Ret_Eur_Fwd']

    dc_df_trim_2['YM'] = dc_df_trim_2['DATA_DATE'].dt.strftime('%Y%m').astype(int)
    dc_df_trim_2 = dc_df_trim_2[(dc_df_trim_2['YM']>=start_YM) & (dc_df_trim_2['YM']<=end_YM)]
    dc_df_trim_2 = dc_df_trim_2.drop(columns = 'YM')
    
    return dc_df_trim_2



## This function will run attribution analysis on a dataframe
## dc_df_trim_2 should be the dataframe with the following columns : 'DATA_DATE', by, 'Port_bins', 'Bmk_Wgt', 'Port_Wgt', 'Ret_Eur_Fwd'
## by should be the grouping we're breaking up tyhe securities by (GICS_SECTOR, INDUSTRY, COUNTRY)....make sure this column is in the dataframe though
## bins is a list of what bins to run the analysis on (1,2,3 for example)
def run_attribution(dc_df_trim_2, by, bins):
        
    # Reduce the dataframe down to only include the bins and dates we want
    dc_df_trim_2_bins = dc_df_trim_2[dc_df_trim_2['Port_bins'].isin(bins)].reset_index(drop=True)
    dc_df_trim_2_grouped = dc_df_trim_2_bins.groupby(['DATA_DATE', by, 'Port_bins'])['Port_Wgt'].sum().reset_index(drop=False).rename(columns = {'Port_Wgt': 'PORT_GROUP_WGT'})
    dc_df_trim_2_grouped = dc_df_trim_2_grouped[dc_df_trim_2_grouped['Port_bins'].isin(bins)].reset_index(drop=True)
        
    # function to return the sum of weights for every date and bin combination
    def sum_prt_wgt(row):
        mask = ((dc_df_trim_2_grouped['DATA_DATE'] == row['DATA_DATE']) & (dc_df_trim_2_grouped['Port_bins'] == row['Port_bins']))
        matching_rows = dc_df_trim_2_grouped[mask]
        return matching_rows['PORT_GROUP_WGT'].sum()
    
    df_dates_bin = dc_df_trim_2_grouped[['DATA_DATE','Port_bins']].drop_duplicates().reset_index(drop=True)
    df_dates_bin['SUM_PRT_GROUP_WGT'] = df_dates_bin.apply(sum_prt_wgt,axis=1)
    dc_df_trim_2_grouped = dc_df_trim_2_grouped.merge(df_dates_bin, on = ['DATA_DATE','Port_bins'], how = 'left')
    
    # refactor the portfolio group weight to be a % of the sum of all portfolio group weights 
    dc_df_trim_2_grouped['PORT_GROUP_WGT'] = dc_df_trim_2_grouped['PORT_GROUP_WGT'] / dc_df_trim_2_grouped['SUM_PRT_GROUP_WGT']
    dc_df_trim_2_grouped = dc_df_trim_2_grouped.drop(columns = 'SUM_PRT_GROUP_WGT')
    
    dc_df_trim_2['wgt_ret'] = dc_df_trim_2['Port_Wgt'] * dc_df_trim_2['Ret_Eur_Fwd']
    dc_df_trim_2_group = dc_df_trim_2.groupby(['DATA_DATE', by, 'Port_bins'])['wgt_ret'].sum().reset_index()
    dc_df_trim_2_grouped = dc_df_trim_2_grouped.merge(dc_df_trim_2_group, on = ['DATA_DATE', by, 'Port_bins'], how = 'left')
    dc_df_trim_2_grouped['PORT_GROUP_WGT_RET'] = dc_df_trim_2_grouped['wgt_ret']/dc_df_trim_2_grouped['PORT_GROUP_WGT']
    dc_df_trim_2_grouped = dc_df_trim_2_grouped.drop(columns = ['wgt_ret'])
    
    dc_df_trim_2['wgt_ret_2'] = dc_df_trim_2['Bmk_Wgt'] * dc_df_trim_2['Ret_Eur_Fwd']
    
    # for every date and grouping (sector, etc) this will return the sum of the weights and the totral return
    def bmk_group_returns(row):
        mask = (dc_df_trim_2['DATA_DATE'] == row['DATA_DATE']) & (dc_df_trim_2[by] == row[by])
        matching_rows = dc_df_trim_2[mask]
        return matching_rows['Bmk_Wgt'].sum(), matching_rows['wgt_ret_2'].sum()
    
    df_date_group = dc_df_trim_2_grouped[['DATA_DATE', by]].drop_duplicates().reset_index(drop=True)
    
    a = df_date_group.apply(bmk_group_returns, axis=1)
    df = pd.DataFrame(a.tolist(), columns=['BMK_GROUP_WGT', 'TEMP'])
    df_date_group['BMK_GROUP_WGT'] = df['BMK_GROUP_WGT']
    df_date_group['TEMP'] = df['TEMP']
    
    # calculates the benchmark total return for a period
    def sum_bmk_group_wgt(row):
        mask = (df_date_group['DATA_DATE'] == row['DATA_DATE'])
        matching_rows = df_date_group[mask]
        return matching_rows['BMK_GROUP_WGT'].sum()
    
    df_dates = df_date_group['DATA_DATE'].drop_duplicates().reset_index(drop=True).to_frame()
    df_dates['SUM_BMK_GROUP_WGT'] = df_dates.apply(sum_bmk_group_wgt,axis=1)
    
    df_date_group_m = df_date_group.merge(df_dates, on = 'DATA_DATE', how = 'left')
    
    dc_df_trim_2_grouped = dc_df_trim_2_grouped.merge(df_date_group_m, on = ['DATA_DATE', by], how = 'left')
    
    # BMK_GROUP_WGT_100 will be the benchmark return for a group if that group was 100% of the benchmark
    dc_df_trim_2_grouped['BMK_GROUP_WGT_100'] = dc_df_trim_2_grouped['BMK_GROUP_WGT'] / dc_df_trim_2_grouped['SUM_BMK_GROUP_WGT']
    dc_df_trim_2_grouped['BMK_WGT_GROUP_RET'] = dc_df_trim_2_grouped['TEMP'] / dc_df_trim_2_grouped['BMK_GROUP_WGT']
    dc_df_trim_2_grouped= dc_df_trim_2_grouped.drop(columns = ['TEMP'])
    dc_df_trim_2_grouped['Active Wgt'] = dc_df_trim_2_grouped['PORT_GROUP_WGT'] - dc_df_trim_2_grouped['BMK_GROUP_WGT_100']
    
    # calcualtes the total return for every date/bin pairing
    def calculate_sumproduct(row):
        mask = (dc_df_trim_2_grouped['DATA_DATE'] == row['DATA_DATE']) & (dc_df_trim_2_grouped['Port_bins'] == row['Port_bins'])
        matching_rows = dc_df_trim_2_grouped[mask]
        return (matching_rows['PORT_GROUP_WGT_RET'] * matching_rows['PORT_GROUP_WGT']).sum()

    def calculate_bmk_returns(row):
        mask = (dc_df_trim_2['DATA_DATE'] == row['DATA_DATE'])
        matching_rows = dc_df_trim_2[mask]
        return (matching_rows['Bmk_Wgt'] * matching_rows['Ret_Eur_Fwd']).sum()
    
    
    df_date_bin = dc_df_trim_2_grouped[['DATA_DATE', 'Port_bins']].drop_duplicates().reset_index(drop=True)
    df_date_bin['PORT_RET_D'] = df_date_bin.apply(calculate_sumproduct, axis=1)
    dc_df_trim_2_grouped = dc_df_trim_2_grouped.merge(df_date_bin, on = ['DATA_DATE', 'Port_bins'], how = 'left')
    df_date_bin = df_date_bin.drop(columns = 'PORT_RET_D')
    
    df_bmk_date = dc_df_trim_2_grouped[['DATA_DATE']].drop_duplicates().reset_index(drop=True)
    df_bmk_date['BMK_WGT_RET_TOTAL'] = df_bmk_date.apply(calculate_bmk_returns, axis=1)
    dc_df_trim_2_grouped = dc_df_trim_2_grouped.merge(df_bmk_date, on = ['DATA_DATE'], how = 'left')
    dc_df_trim_2_grouped['PORT_GROUP_RET_1'] =dc_df_trim_2_grouped['PORT_GROUP_WGT_RET']+1
    
    first_group = dc_df_trim_2_grouped[by].iloc[0]
    first_bin = dc_df_trim_2_grouped['Port_bins'].iloc[0]
    
    dc_df_trim_2_grouped['BMK_GROUP_RET_1'] = np.where(dc_df_trim_2_grouped['Port_bins']==first_bin, dc_df_trim_2_grouped['BMK_WGT_GROUP_RET']+1, 1)
    dc_df_trim_2_grouped['PORT_RET_1'] = np.where(dc_df_trim_2_grouped[by]==first_group, dc_df_trim_2_grouped['PORT_RET_D']+1,1)
    dc_df_trim_2_grouped['BMK_RET_1'] = np.where(((dc_df_trim_2_grouped['Port_bins']==first_bin) & (dc_df_trim_2_grouped[by]==first_group)), dc_df_trim_2_grouped['BMK_WGT_RET_TOTAL']+1,1)
    
    # calculates the cumulative returns for the benchmark group returns (combination of bmk & grouping), the portfolio returns and the benchmark returns
    dc_df_trim_2_grouped['BMK_GROUP_RET_1_CUMM'] = dc_df_trim_2_grouped.groupby([by])['BMK_GROUP_RET_1'].transform(pd.Series.cumprod) - 1
    dc_df_trim_2_grouped['PORT_RET_1_CUMM'] = dc_df_trim_2_grouped.groupby(['Port_bins'])['PORT_RET_1'].transform(pd.Series.cumprod) - 1
    dc_df_trim_2_grouped['BMK_RET_1_CUMM'] = dc_df_trim_2_grouped['BMK_RET_1'].transform(pd.Series.cumprod) - 1
    
    # calculate the selectiona nd allocation per date and per group
    dc_df_trim_2_grouped['Selection_D_Group'] = dc_df_trim_2_grouped['PORT_GROUP_WGT'] * (dc_df_trim_2_grouped['PORT_GROUP_WGT_RET'] - dc_df_trim_2_grouped['BMK_WGT_GROUP_RET'])
    dc_df_trim_2_grouped['Allocation_D_Group'] = (dc_df_trim_2_grouped['PORT_GROUP_WGT'] -dc_df_trim_2_grouped['BMK_GROUP_WGT']) * (dc_df_trim_2_grouped['BMK_WGT_GROUP_RET'] - dc_df_trim_2_grouped['BMK_WGT_RET_TOTAL'])
    
    # get the sum of the selection and allocation per date and bin. the sums will be the portfolio's selection and allocation per date
    def selec_alloc_d_group(row):
        mask = (dc_df_trim_2_grouped['DATA_DATE'] == row['DATA_DATE']) & (dc_df_trim_2_grouped['Port_bins'] == row['Port_bins'])
        matching_rows = dc_df_trim_2_grouped[mask]
        return matching_rows['Selection_D_Group'].sum(), matching_rows['Allocation_D_Group'].sum()
    
    #df_date_bin = dc_df_trim_2_grouped[['DATA_DATE', bin_col]].drop_duplicates().reset_index(drop=True)
    a = df_date_bin.apply(selec_alloc_d_group, axis=1)
    df = pd.DataFrame(a.tolist(), columns=['Selection_D_Group', 'Allocation_D_Group'])
    df_date_bin['Selection_D_Port'] = df['Selection_D_Group']
    df_date_bin['Allocation_D_Port'] = df['Allocation_D_Group']
    
    dc_df_trim_2_grouped = dc_df_trim_2_grouped.merge(df_date_bin, on = ['DATA_DATE', 'Port_bins'], how = 'left')
    df_date_bin = df_date_bin.drop(columns = ['Selection_D_Port', 'Allocation_D_Port'])
    
    # get the sum of the selection and allocation per group and bin up till a date (the cumulative)
    
    dc_df_trim_2_grouped["Selection_Cumm_Group"] = dc_df_trim_2_grouped.groupby([by, 'Port_bins'])["Selection_D_Group"].transform(pd.Series.cumsum)
    dc_df_trim_2_grouped['Allocation_Cumm_Group'] = dc_df_trim_2_grouped.groupby([by, 'Port_bins'])["Allocation_D_Group"].transform(pd.Series.cumsum)
    
    # get the sum of the cumulative selections and allocations per date and bin
    def selec_alloc(row):
        mask = (dc_df_trim_2_grouped['DATA_DATE'] == row['DATA_DATE']) & (dc_df_trim_2_grouped['Port_bins'] == row['Port_bins'])
        matching_rows = dc_df_trim_2_grouped[mask]
        return matching_rows['Selection_Cumm_Group'].sum(), matching_rows['Allocation_Cumm_Group'].sum()
    
    
    #df_date_bin = dc_df_trim_2_grouped[['DATA_DATE', bin_col]].drop_duplicates().reset_index(drop=True)
    
    a = df_date_bin.apply(selec_alloc, axis=1)
    df = pd.DataFrame(a.tolist(), columns=['Selection_Cumm_Group', 'Allocation_Cumm_Group'])
    df_date_bin['Selection_Cumm'] = df['Selection_Cumm_Group']
    df_date_bin['Allocation_Cumm'] = df['Allocation_Cumm_Group']
    
    dc_df_trim_2_grouped = dc_df_trim_2_grouped.merge(df_date_bin, on = ['DATA_DATE', 'Port_bins'], how = 'left')
    
    dc_df_trim_2_g_cop = dc_df_trim_2_grouped.copy()
    dc_df_trim_2_g_cop = dc_df_trim_2_g_cop.rename(columns = {'PORT_RET_1_CUMM' : 'Port Return', 'BMK_RET_1_CUMM' : 'Bmk Return', 'Selection_Cumm' : 'Selection Effect', 'Allocation_Cumm' : 'Allocation Effect', 'PORT_GROUP_WGT': 'Portfolio Wgt', 'BMK_GROUP_WGT_100': 'Benchmark Wgt'})
    dc_df_trim_2_g_cop['Active Return'] = dc_df_trim_2_g_cop['Port Return'] - dc_df_trim_2_g_cop['Bmk Return']
    dc_df_trim_2_g_cop['Unexplained'] = dc_df_trim_2_g_cop['Active Return'] - dc_df_trim_2_g_cop['Selection Effect']- dc_df_trim_2_g_cop['Allocation Effect']
      
    ## This part makes the assumtion that the selection effect will extrapolate
    
    dc_df_trim_2_g_cop['selec'] = abs(dc_df_trim_2_g_cop['Selection Effect']) / (abs(dc_df_trim_2_g_cop['Selection Effect']) + abs(dc_df_trim_2_g_cop['Allocation Effect']))
    dc_df_trim_2_g_cop['alloc'] = abs(dc_df_trim_2_g_cop['Allocation Effect']) / (abs(dc_df_trim_2_g_cop['Selection Effect']) + abs(dc_df_trim_2_g_cop['Allocation Effect']))    
    dc_df_trim_2_g_cop['Selection'] = dc_df_trim_2_g_cop['Selection Effect'] + (dc_df_trim_2_g_cop['Unexplained'] * (dc_df_trim_2_g_cop['selec'] / (dc_df_trim_2_g_cop['selec'] + dc_df_trim_2_g_cop['alloc'])))
    dc_df_trim_2_g_cop['Allocation'] = dc_df_trim_2_g_cop['Allocation Effect'] + (dc_df_trim_2_g_cop['Unexplained'] * (dc_df_trim_2_g_cop['alloc'] / (dc_df_trim_2_g_cop['selec'] + dc_df_trim_2_g_cop['alloc'])))
   
    ## Removing these as the above two lines are smoother
    # dc_df_trim_2_g_cop['Selection'] = (dc_df_trim_2_g_cop['Selection Effect'] / (dc_df_trim_2_g_cop['Selection Effect'] + dc_df_trim_2_g_cop['Allocation Effect']))*dc_df_trim_2_g_cop['Active Return']
    # dc_df_trim_2_g_cop['Allocation'] = (dc_df_trim_2_g_cop['Allocation Effect'] / (dc_df_trim_2_g_cop['Selection Effect'] + dc_df_trim_2_g_cop['Allocation Effect']))*dc_df_trim_2_g_cop['Active Return']
    
    
    dc_df_trim_2_g_cop['Group Selection'] = dc_df_trim_2_g_cop['Selection_Cumm_Group'] * dc_df_trim_2_g_cop['Selection'] / dc_df_trim_2_g_cop['Selection Effect']
    dc_df_trim_2_g_cop['Group Allocation'] = dc_df_trim_2_g_cop['Allocation_Cumm_Group'] * dc_df_trim_2_g_cop['Allocation'] / dc_df_trim_2_g_cop['Allocation Effect']
    
    df_attributions = dc_df_trim_2_g_cop [['DATA_DATE', 'Port_bins', by, 'Portfolio Wgt', 'Benchmark Wgt', 'Active Wgt', 'Port Return', 'Bmk Return', 'Active Return', 'Selection', 'Allocation', 'Group Selection', 'Group Allocation']]
    
    return df_attributions



def create_dictionaries(df_attributions, by, model, bins):
    
    dict_attributions={}
    dict_selections={}
    dict_allocations={}
    dict_weights={}
    groups = df_attributions[by].unique().tolist()
    
    for b in bins:
        df_attributions_bin = df_attributions[df_attributions['Port_bins'] == b]
        
        df_weights = df_attributions_bin.groupby(by)['Active Wgt'].mean().reset_index()
        df_final_att_bin = df_attributions_bin[df_attributions_bin['DATA_DATE']==df_attributions_bin['DATA_DATE'].iloc[df_attributions_bin.shape[0]-1]]
        df_final_att_bin_trim = df_final_att_bin[[by, 'Group Selection', 'Group Allocation']]
        df_weights_s_all = df_weights.merge(df_final_att_bin_trim, on = by, how = 'left').fillna(0)
        df_weights_s_all.columns = [by, 'Avg Active Wgt', 'Selection Effect', 'Allocation Effect']
        
        new_row = {by:'Total', 'Avg Active Wgt':df_weights_s_all['Avg Active Wgt'].sum(), 'Selection Effect':df_weights_s_all['Selection Effect'].sum(), 'Allocation Effect':df_weights_s_all['Allocation Effect'].sum()}
        new_row_df = pd.DataFrame([new_row])
        df_weights_s_all = pd.concat([df_weights_s_all, new_row_df], ignore_index=True)
        dict_weights[b] = df_weights_s_all
        
        df_attributions_bin_d = df_attributions_bin.drop_duplicates('DATA_DATE')
        df_attributions_bin_trim = df_attributions_bin_d[['DATA_DATE', 'Active Return', 'Selection', 'Allocation']]
        dict_attributions[b] = df_attributions_bin_trim
        
        df_selections_bin_p = pd.pivot(df_attributions_bin, index = 'DATA_DATE', columns = by, values = 'Group Selection').reset_index(drop=False)
        df_selections_bin_p['Total'] = df_selections_bin_p[groups[0]].fillna(0)
        for s in groups[1:]:
            df_selections_bin_p['Total'] = df_selections_bin_p['Total'] + df_selections_bin_p[s].fillna(0)
        dict_selections[b] = df_selections_bin_p
            
        df_allocations_bin_p = pd.pivot(df_attributions_bin, index = 'DATA_DATE', columns = by, values = 'Group Allocation').reset_index(drop=False)
        df_allocations_bin_p['Total'] = df_allocations_bin_p[groups[0]].fillna(0)
        for s in groups[1:]:
            df_allocations_bin_p['Total'] = df_allocations_bin_p['Total'] + df_allocations_bin_p[s].fillna(0)
        dict_allocations[b] = df_allocations_bin_p
            
    return dict_attributions, dict_selections, dict_allocations, dict_weights


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


# if os.path.exists(attribution_path):
#     print('Attribution has already been run. Picking up the pickle files instead.')
#     dict_results = pd.read_pickle(attribution_path)
#     df_attributions = dict_results['df_attributions']
    
#     shift_col_list = df_attributions.columns.tolist()
#     for c in ['DATA_DATE', model+'_bin', by]:
#         shift_col_list.remove(c)
    
#     df_attributions_shift = df_attributions.copy()
#     for c in shift_col_list:
#         df_attributions_shift[c] = df_attributions_shift.groupby([model+'_bin', by])[c].shift(periods = 1)
#         df_attributions_shift[c] = df_attributions_shift[c].fillna(0)
    
#     dict_attributions = dict_results['dict_attributions']
#     dict_selections = dict_results['dict_selections']
#     dict_allocations = dict_results['dict_allocations']

# else:
#     print('Reading backtest pickle file.')
#     backtest_df = pd.read_pickle(backtest_path).reset_index(drop=True)
#     print('Running attribution.')
#     df_attributions = run_attribution(backtest_df, model, by, bins, start_YM, end_YM, timer)
    
#     dict_attributions, dict_selections, dict_allocations, dict_weights = create_dictionaries(df_attributions_shift, by, model, bins)
#     print('Saving attribution results.')
    
#     dict_results = {}
#     dict_results['df_attributions'] = df_attributions
#     dict_results['dict_attributions'] = dict_attributions
#     dict_results['dict_selections'] = dict_selections
#     dict_results['dict_allocations'] = dict_allocations

#     file_to_write = open(attribution_path, "wb")
#     pickle.dump(dict_results, file_to_write)
#     file_to_write.close()
#     pickle_Saved = True

if timer == True:
    a1 = dt.datetime.now()

print('Reading backtest pickle file.')
backtest_df = pd.read_pickle(backtest_path).reset_index(drop=True)

if timer == True:
    a2 = dt.datetime.now()

print("Orgainsing dataframe for attribution analysis.")
dc_df_trim_2 = create_input_attribution_df(backtest_df, model, by, weighting, start_YM, end_YM)

if timer == True:
    a3 = dt.datetime.now()

print('Running attribution.')
df_attributions = run_attribution(dc_df_trim_2, by, bins)

if timer == True:
    a4 = dt.datetime.now()
    
shift_col_list = df_attributions.columns.tolist()
for c in ['DATA_DATE', 'Port_bins', by]:
    shift_col_list.remove(c)

df_attributions_shift = df_attributions.copy()
for c in shift_col_list:
    df_attributions_shift[c] = df_attributions_shift.groupby(['Port_bins', by])[c].shift(periods = 1)
    df_attributions_shift[c] = df_attributions_shift[c].fillna(0)

dict_attributions, dict_selections, dict_allocations, dict_weights = create_dictionaries(df_attributions_shift, by, model, bins)
show_att_graphs(dict_attributions)
show_select_graphs(dict_selections)
show_selection_comparisons(dict_attributions)

if timer == True:
    a5 = dt.datetime.now()
    
if timer == True:
    time1 = divmod((a2-a1).total_seconds(), 60) 
    time2 = divmod((a3-a2).total_seconds(), 60) 
    time3 = divmod((a4-a3).total_seconds(), 60) 
    time4 = divmod((a5-a4).total_seconds(), 60) 
    
    st1 = "Reading pickle      :" + str(time1[0]) + " mins and " + str(int(time1[1])) + " secs"
    st2 = "Organising df       :" + str(time2[0]) + " mins and " + str(int(time2[1])) + " secs"
    st3 = "Running Attribution :" + str(time3[0]) + " mins and " + str(int(time3[1])) + " secs"
    st4 = "Arranging graphs    :" + str(time4[0]) + " mins and " + str(int(time4[1])) + " secs"
    
    print(st1)
    print(st2)
    print(st3)
    print(st4)
    