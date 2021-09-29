#!/usr/bin/env python3

import sys
from components.data_processing import process_awhere_JSON

input = sys.argv[1]
output = sys.argv[2]

print("Starting data cleaning...")
process_awhere_JSON(input, output)
print("Completed data cleaning!")