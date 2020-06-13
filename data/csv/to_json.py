#!/usr/bin/python3
# to_json.py
# Converts .csv documents to json

import pandas
from   pathlib  import Path

cur_dir = Path(__file__).resolve().parent
json_dir = Path(__file__).resolve().parents[1] / 'json'

def convert_to_json(f):
   df = pandas.read_csv(f)
   new_name = f.name.split('.')[0] + '.json'
   df.to_json(json_dir / new_name, orient='index')

def main():
   for f in cur_dir.iterdir():
      if '.csv' in f.name:
         convert_to_json(f)

if __name__ == '__main__':
   main()
