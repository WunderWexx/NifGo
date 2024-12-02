"""
Maakt Excel bestand aan voor aanlevering aan Card Vision BV
"""

import pandas as pd
from datetime import datetime
import Utilities as util
from ELT import Extract

# Define the genes
genes = [
    "ABCG2", "COMT", "CYP1A2", "CYP2B6", "CYP2C9", "CYP2C19", "CYP2D6", "CYP3A4", "CYP3A5",
    "DPYD", "G6PD", "HLA-B*1502", "MTHFR677", "NUDT15", "SLCO1B1", "TPMT", "UGT1A1", "VKORC1"
]
genes_left = ["ABCG2", "COMT", "CYP1A2", "CYP2B6", "CYP2C9", "CYP2C19", "CYP2D6", "CYP3A4", "CYP3A5"]
genes_right = ["DPYD", "G6PD", "HLA-B*1502", "MTHFR677", "NUDT15", "SLCO1B1", "TPMT", "UGT1A1", "VKORC1"]

# Load the complete data
complete_filtered = pd.read_excel('Output/Dataframes/complete.xlsx')

# Filter rows for the relevant genes
complete_filtered = complete_filtered[complete_filtered['gene'].isin(genes)]
util.printEntire(complete_filtered)

# Extract unique customer codes
customer_codes = list(complete_filtered['sample_id'].unique())

# Create the card DataFrame
card = pd.DataFrame()
card['NAAM'] = customer_codes  # Column 1: Customer Codes
date = datetime.today().strftime('%d-%m-%Y')
card['DATUM AFGIFTE'] = [date] * len(customer_codes)  # Column 3: Current Date

# Populate columns
def add_filled_column(geno_or_pheno, left_or_right):
    if left_or_right == 'left':
        columns_side = genes_left
        side_denom = 'LINKS'
    else:
        columns_side = genes_right
        side_denom = 'RECHTS'

    if geno_or_pheno == 'genotype':
        trait_denom = 'UITSLAG'
    else:
        trait_denom = 'FENOTYPE'

    for idx, gen in enumerate(columns_side, start=1):
        gene_filtered = complete_filtered[complete_filtered['gene'] == gen]
        result_column = [
            gene_filtered.loc[gene_filtered['sample_id'] == customer_code, geno_or_pheno].values[0]
            if not gene_filtered.loc[gene_filtered['sample_id'] == customer_code, geno_or_pheno].empty
            else None
            for customer_code in customer_codes
        ]
        card[f"ACHTERZIJDE {trait_denom} {idx} {side_denom}"] = result_column

add_filled_column('genotype','left')
add_filled_column('phenotype','left')
add_filled_column('phenotype', 'right')
add_filled_column('genotype', 'right')

util.printEntire(card)

# Eerste kolom mappen naar klantnamen
def customer_data_IA():
    customerdata_df = Extract().customer_data()
    customerdata_df = customerdata_df.rename(
        columns={0: 'sample_id', 1: 'initials', 2: 'lastname', 3: 'birthdate', 4: 'status'})
    customerdata_df = customerdata_df.fillna('')
    customerdata_df = customerdata_df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))
    customerdata_df['birthdate'] = customerdata_df['birthdate'].dt.strftime('%d-%m-%Y')
    customerdata_df['birthdate'] = customerdata_df['birthdate'].fillna('20237-01-01')
    customerdata_df.sort_values(by='sample_id', ascending=True, inplace=True)
    customerdata_df.reset_index(inplace=True, drop=True)
    return customerdata_df

customer_data = customer_data_IA()
util.printEntire(customer_data)

# Tweede kolom vullen met geboortedata uit het klantbestand. Als die niet beschikbaar is lege string toevoegen.
birthdates = []
for sample_id in card['NAAM']:
    birthdate = customer_data.loc[customer_data['sample_id'] == sample_id, 'birthdate'].values[0]
    if birthdate == '20237-01-01':
        birthdate = ''
    birthdates.append(birthdate)
card.insert(1, 'GEBOORTEDATUM', birthdates)

for sample_id in card['NAAM']:
    initials = customer_data.loc[customer_data['sample_id'] == sample_id, 'initials'].values[0]
    last_name = customer_data.loc[customer_data['sample_id'] == sample_id, 'lastname'].values[0]
    customer_name = f"{initials} {last_name}"
    card.loc[card['NAAM'] == sample_id, 'NAAM'] = customer_name

util.printEntire(card)

card.to_excel(f'Output/Dataframes/cards-{date}.xlsx')