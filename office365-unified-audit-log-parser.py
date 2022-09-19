import argparse
import csv
import json
import sys


parser=argparse.ArgumentParser()

parser.add_argument("--input_file", help="CSV log file to read", required=True)
parser.add_argument("--output_file", help="CSV log file to write", required=True)

args=parser.parse_args()

input_file = args.input_file
output_file = args.output_file

overwrite_confirmation = input("Are you sure you wish to overwrite %s with the parsed output of %s? (y/n): " % (output_file, input_file))
if overwrite_confirmation != "y":
    sys.exit()

field_names = []

def add_key(key):
    if key not in field_names:
        field_names.append(key)

# Read the CSV file
with open(input_file, 'r') as f:
    csv_data = csv.DictReader(f)

    new_structure = []

    for row in csv_data:
        # Convert the CSV row into a dictionary
        row_dict = dict(row)
        for key in row_dict.keys():
            add_key(key)
        audit_data = json.loads(row_dict['AuditData'])
        for key, value in audit_data.items():
            key_name = 'AuditData_%s' % key
            add_key(key_name)
            row_dict[key_name] = value
        # Add the dictionary to the new structure
        new_structure.append(row_dict)

    # Write the new structure to a CSV file
    with open(output_file, 'w') as fw:
        csv_writer = csv.DictWriter(fw, fieldnames=field_names)
        csv_writer.writeheader()
        csv_writer.writerows(new_structure)
