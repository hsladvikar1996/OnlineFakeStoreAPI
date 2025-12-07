import json
import csv
from openpyxl import load_workbook

#Json Data Provider
def read_json_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return [(item,) for item in data]
