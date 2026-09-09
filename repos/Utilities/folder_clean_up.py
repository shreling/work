# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 12:43:47 2023

@author: cillian.byrne
"""

import os
from datetime import datetime
from collections import defaultdict

folders = {}
folders['Constituents'] = r"Q:\Investment\Securities\Quant\Data\1. Ecosystem\2. Constituents"
folders['Estimates'] = r"Q:\Investment\Securities\Quant\Data\1. Ecosystem\5. Estimates"
folders['Factors'] = r"Q:\Investment\Securities\Quant\Data\1. Ecosystem\3. Factors"

for t in folders:
    print(t)
    print(folders[t])

def extract_date(filename):
    # Extract the date part from the filename and convert it to a datetime object
    date_str = filename.split("_")[1].split(".")[0]
    return datetime.strptime(date_str, "%Y-%m-%d")

def delete_files_except_last_in_month(folder_path, type_):
    files_by_month = defaultdict(list)

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.startswith(type_) and filename.endswith(".pickle"):
            full_path = os.path.join(folder_path, filename)
            date = extract_date(filename)
            files_by_month[(date.year, date.month)].append((full_path, date))

    for month_files in files_by_month.values():
        if len(month_files) > 1:
            # Sort files in each month by date
            month_files.sort(key=lambda x: x[1])

            # Delete all files in the month except the last one
            for file_path, _ in month_files[:-1]:
                os.remove(file_path)
                print(f"Deleted: {file_path}")

for t in folders:
    folder_path = folders[t]
    type_ = t

    delete_files_except_last_in_month(folder_path, type_)