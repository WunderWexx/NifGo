# This is where unknown handling is done, including both unknown detection and replacement.

import pandas as pd
import PySimpleGUI as sg

class HandlingUnknowns:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.unknown_signs_list = ['ERROR', 'Not_PM', 'Not_NM', 'Not_IM', 'Not_RM', 'Not_UM', 'unknown', '---', '']

    def detect_unknowns(self):
        unknowns_df = self.dataframe[
            self.dataframe['phenotype'].isin(self.unknown_signs_list) |
            self.dataframe['genotype'].isin(self.unknown_signs_list)
            ]
        unknowns_df.to_excel('Output/Diagnostics/unknowns.xlsx')

    def ask_for_unknowns_df(self):
        file_is_present = sg.popup_yes_no("Heeft u het bestand met de gecorrigeerde unknowns?")
        if file_is_present == 'Yes':
            correcties_path = sg.popup_get_file(
                "Selecteer alstublieft het .xlsx (Excel) bestand met de unknown correcties",
                title="Invoer unknown correctie")
            correcties_df = pd.read_excel(correcties_path)
            return correcties_df
        else:
            return None

    def correct_unknowns(self):
        # correct_unknowns_df is the hand corrected version of unknowns_df
        # df is the copy of complete.xlsx that is being edited
        correct_unknowns_df = self.ask_for_unknowns_df()
        if isinstance(correct_unknowns_df, pd.DataFrame):
            df = self.dataframe
            for index, row in correct_unknowns_df.iterrows():
                sample_id = row['sample_id']
                gene = row['gene']
                filter = (df['gene'] == gene) & (df['sample_id'] == sample_id)
                df.loc[filter, 'phenotype'] = row['phenotype']
                df.loc[filter, 'genotype'] = row['genotype']
            self.dataframe = df
        else:
            pass
