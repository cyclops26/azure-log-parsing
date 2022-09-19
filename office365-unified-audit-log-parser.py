import argparse
import csv
import json
import sys


parser=argparse.ArgumentParser()

parser.add_argument("--input_file", help="CSV log file to read", required=True)
parser.add_argument("--output_file", help="CSV log file to write", required=True)
parser.add_argument("--search_term", help="an optional search term", required=False)

args=parser.parse_args()

input_file = args.input_file
output_file = args.output_file

search_term = args.search_term
search_results = dict()

overwrite_confirmation = input("Are you sure you wish to overwrite %s with the parsed output of %s? (y/n): " % (output_file, input_file))
if overwrite_confirmation != "y":
    sys.exit()

field_names = []

def add_key(key):
    if key not in field_names:
        field_names.append(key)

def handle_search_term(data, line_number, field_name):
    if search_term and data and isinstance(data, str) and search_term in data:
        key = 'Line %s' % line_number
        if line_number not in search_results.keys():
            search_results[key] = list()
        search_results[key].append(field_name)

# Read the CSV file
with open(input_file, 'r') as f:
    print("Parsing ...", end="")
    csv_data = csv.DictReader(f)

    new_structure = []

    for row in csv_data:
        line_number = csv_data.line_num
        print(".", end="")
        # Convert the CSV row into a dictionary
        row_dict = dict(row)
        for key in row_dict.keys():
            add_key(key)
            handle_search_term(row_dict[key], line_number, key)
        audit_data = json.loads(row_dict['AuditData'])
        for key, value in audit_data.items():
            key_name = 'AuditData_%s' % key
            add_key(key_name)
            row_dict[key_name] = value
            handle_search_term(value, line_number, key_name)
            if key in ['ExtendedProperties', 'ModifiedProperties', 'Actor', 'Target', 'DeviceProperties']:
                for index, property in enumerate(value):
                    property_name = '%s_%s' % (key_name, index)
                    for sub_key, sub_value in property.items():
                        sub_key_name = '%s_%s' % (property_name, sub_key)
                        add_key(sub_key_name)
                        row_dict[sub_key_name] = sub_value
                        handle_search_term(sub_value, line_number, sub_key_name)
            if key in ['AppAccessContext']:
                for sub_key in value.keys():
                    sub_key_name = '%s_%s' % (key_name, sub_key)
                    add_key(sub_key_name)
                    row_dict[sub_key_name] = value[sub_key]
                    handle_search_term(value[sub_key], line_number, sub_key_name)
        # Add the dictionary to the new structure
        new_structure.append(row_dict)

    # Write the new structure to a CSV file
    with open(output_file, 'w') as fw:
        csv_writer = csv.DictWriter(fw, fieldnames=field_names)
        csv_writer.writeheader()
        csv_writer.writerows(new_structure)

print ("")
print ("Done!")

if search_term:
    print ("")
    print ("Search results for '%s':" % search_term)
    for key, value in search_results.items():
        print ("%s contains the search term in the following fields: %s" % (key, ', '.join(value)))
