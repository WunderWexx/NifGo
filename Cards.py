"""
Maakt Excel bestand aan voor aanlevering aan Card Vision BV
"""
"""import Utilities as util
import pandas as pd
from datetime import datetime

#Filter complete op genen
genes = [
    "ABCG2", "COMT", "CYP1A2", "CYP2B6", "CYP2C9", "CYP2C19", "CYP2D6", "CYP3A4", "CYP3A5",
    "DPYD", "G6PD", "HLA-B*1502", "MTHFR677", "NUDT15", "SLCO1B1", "TPMT", "UGT1A1", "VKORC1"
]
genes_left = ["ABCG2", "COMT", "CYP1A2", "CYP2B6", "CYP2C9", "CYP2C19", "CYP2D6", "CYP3A4", "CYP3A5"]
genes_right = ["DPYD", "G6PD", "HLA-B*1502", "MTHFR677", "NUDT15", "SLCO1B1", "TPMT", "UGT1A1", "VKORC1"]

complete_filtered = pd.read_excel('Output/Dataframes/complete.xlsx')
complete_filtered = complete_filtered[complete_filtered['gene'].isin(genes)]
print('complete_filtered')
util.printEntire(complete_filtered)

# Eerste kolom vullen met codes uit complete.xlsx
card = pd.DataFrame()
customer_codes = list(set(complete_filtered['sample_id']))
print(customer_codes)
print(len(customer_codes))
card['NAAM'] = customer_codes

# Derde kolom vullen met huidige datum
card['DATUM AFGIFTE'] = [datetime.today().strftime('%d-%m-%Y')] * len(card['NAAM'])
util.printEntire(card)

# Kolom 4 tm 12 vullen met uitslagen van genen links
# Kolom 13 tm 21 vullen met fenotypes van genen links
column_counter = 1
for gen in genes_left:
    gene_filtered = complete_filtered[complete_filtered['gene'] == gen]
    print('gene_filtered')
    util.printEntire(gene_filtered)
    print('\n\n')
    result_column = []
    for customer_code in customer_codes:
        print(gene_filtered.loc[gene_filtered['sample_id'] == customer_code, 'genotype'])
        result_column.append(gene_filtered.loc[gene_filtered['sample_id'] == customer_code, 'genotype'])
    card[f"ACHTERZIJDE UITSLAG {column_counter} LINKS"] = result_column
    column_counter += 1

util.printEntire(card)"""


import pandas as pd
from datetime import datetime
import Utilities as util

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

for idx, gen in enumerate(genes_left, start=1):
    gene_filtered = complete_filtered[complete_filtered['gene'] == gen]
    result_column = [
        gene_filtered.loc[gene_filtered['sample_id'] == customer_code, 'genotype'].values[0]
        if not gene_filtered.loc[gene_filtered['sample_id'] == customer_code, 'genotype'].empty
        else None
        for customer_code in customer_codes
    ]
    card[f"ACHTERZIJDE UITSLAG {idx} LINKS"] = result_column


def add_filled_column(geno_or_pheno, left_or_right):
    if left_or_right == 'left':
        columns_side = genes_left
        side_denom = 'LINKS'
    else:
        columns_side = genes_right
        side_denom = 'RECHTS'

    for idx, gen in enumerate(columns_side, start=1):
        gene_filtered = complete_filtered[complete_filtered['gene'] == gen]
        result_column = [
            gene_filtered.loc[gene_filtered['sample_id'] == customer_code, geno_or_pheno].values[0]
            if not gene_filtered.loc[gene_filtered['sample_id'] == customer_code, geno_or_pheno].empty
            else None
            for customer_code in customer_codes
        ]
        card[f"ACHTERZIJDE UITSLAG {idx} {side_denom}"] = result_column

add_filled_column('genotype','left')
add_filled_column('phenotype','left')
add_filled_column('genotype', 'right')
add_filled_column('phenotype', 'right')

util.printEntire(card)

card.to_excel(f'Output/Dataframes/cards-{date}.xlsx')

# Eerste kolom mappen naar klantnamen
# PENDING CUSTOMER DATA

# Tweede kolom vullen met geboortedata uit het klantbestand. Als die niet beschikbaar is lege string toevoegen.
# PENDING CUSTOMER DATA