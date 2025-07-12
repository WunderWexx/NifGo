"""
Maakt Excel bestand aan voor aanlevering aan Card Vision BV.
Kan pas gedraaid worden nadat alle unknowns en klantdata kloppen.
"""

import pandas as pd
from datetime import datetime

def cards(complete_df, customer_df):
    # Define the genes
    genes = [
        "ABCG2", "COMT", "CYP1A2", "CYP2B6", "CYP2C9", "CYP2C19", "CYP2D6",
        "CYP3A4", "CYP3A5", "DPYD", "G6PD", "HLA-B*1502", "HLA-B*5701",
        "HLA-A*3101", "MTHFR677", "NUDT15", "SLCO1B1", "TPMT", "UGT1A1", "VKORC1"]
    genes_left = [
        "ABCG2", "COMT", "CYP1A2", "CYP2B6", "CYP2C9", "CYP2C19", "CYP2D6",
        "CYP3A4", "CYP3A5", "DPYD"]
    genes_right = [
        "G6PD", "HLA-B*1502", "HLA-B*5701", "HLA-A*3101", "MTHFR677", "NUDT15",
        "SLCO1B1", "TPMT", "UGT1A1", "VKORC1"]

    # Load the complete data
    complete_filtered = complete_df

    # Filter rows for the relevant genes
    complete_filtered = complete_filtered[complete_filtered['gene'].isin(genes)]

    # Extract unique customer codes
    customer_codes = list(customer_df['sample_id'].unique())

    # Create the card DataFrame
    card = pd.DataFrame()
    card['NAAM'] = customer_codes  # Column 1: Customer Codes
    date = datetime.today().strftime('%d-%m-%Y')
    card['DATUM AFGIFTE'] = [date] * len(customer_codes)  # Column 3: Current Date

    # Populate columns
    def add_filled_column(geno_or_pheno, left_or_right):
        # Determine the columns and the side label
        columns_side = genes_left if left_or_right == 'left' else genes_right
        side_denom = 'LINKS' if left_or_right == 'left' else 'RECHTS'

        # Determine the trait label
        trait_denom = 'UITSLAG' if geno_or_pheno == 'genotype' else 'FENOTYPE'

        # Iterate over the genes and add the corresponding results to the card
        for idx, gene in enumerate(columns_side, start=1):
            gene_filtered = complete_filtered[complete_filtered['gene'] == gene]

            # Prepare the result column
            result_column = [
                gene_filtered.loc[gene_filtered['sample_id'] == customer_code, geno_or_pheno].values[0]
                if not gene_filtered.loc[gene_filtered['sample_id'] == customer_code, geno_or_pheno].empty
                else None
                for customer_code in customer_codes
            ]

            # Add the result column to the card with an appropriate label
            card[f"ACHTERZIJDE {trait_denom} {idx} {side_denom}"] = result_column

    # Call the function for different combinations of geno_or_pheno and left_or_right
    add_filled_column('genotype', 'left')
    add_filled_column('phenotype', 'left')
    add_filled_column('genotype', 'right')
    add_filled_column('phenotype', 'right')

    # Tweede kolom vullen met geboortedata uit het klantbestand. Als die niet beschikbaar is lege string toevoegen.
    birthdates = []
    for sample_id in card['NAAM']:
        birthdate = customer_df.loc[customer_df['sample_id'] == sample_id, 'birthdate'].values[0]
        if birthdate == '20237-01-01':
            birthdate = ''
        birthdates.append(birthdate)
    card.insert(1, 'GEBOORTEDATUM', birthdates)

    # Eerste kolom mappen naar klantnamen
    for sample_id in card['NAAM']:
        initials = customer_df.loc[customer_df['sample_id'] == sample_id, 'initials'].values[0]
        last_name = customer_df.loc[customer_df['sample_id'] == sample_id, 'lastname'].values[0]
        customer_name = f"{initials} {last_name}".strip()
        card.loc[card['NAAM'] == sample_id, 'NAAM'] = customer_name

    # Rijen verwijderen waar data mist
    card = card.dropna(subset=['ACHTERZIJDE UITSLAG 1 LINKS'])

    card.to_excel(f'Output/Dataframes/cards.xlsx', index=False)