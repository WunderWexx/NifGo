import pandas as pd
import PySimpleGUI as sg
import Utilities as util

# Importing genotypes file to read
filepath = sg.popup_get_file(f"Please select the genotypes file",
                                     title="File selection", keep_on_top=True)

file = open(filepath, 'r')
lines = file.readlines()

# Importing probeset_ids to check
probeset_ids = pd.read_excel("Input/Dataframes/nutri_markers.xlsx")
probeset_ids = probeset_ids['probeset_id']
probeset_ids = list(probeset_ids)
for i in probeset_ids:
    print(i)
print('\n\n\n\n\n\n\n')

idsfound = []
for line in lines:
    for id in probeset_ids:
        if util.is_substring_present_in_string(line, id):
            idsfound.append(id)
            print(id)

missing_genes = util.find_missing_items_in_list(idsfound, probeset_ids)
print(missing_genes)