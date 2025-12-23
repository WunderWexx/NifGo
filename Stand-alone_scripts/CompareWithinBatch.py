import pandas as pd

# 1. Load the data
df = pd.read_excel("C:/Users/Jarno/PycharmProjects/NifGo/Output/Dataframes/complete.xlsx", sheet_name='Sheet1')

# 2. Identify base sample IDs (those without the "_2" suffix)
all_ids = df['sample_id'].unique()
base_ids = [sid for sid in all_ids if not sid.endswith('_2')]

# 3. Open the output file
with open('differences.txt', 'w') as out_file:
    # 4. Iterate over each base sample
    for base in base_ids:
        partner = f"{base}_2"
        df_base = df[df['sample_id'] == base]
        df_p2 = df[df['sample_id'] == partner]

        # Skip if no counterpart exists
        if df_p2.empty:
            continue

        # 5. Merge on gene to line up records
        merged = pd.merge(
            df_base[['gene', 'phenotype', 'genotype']],
            df_p2[['gene', 'phenotype', 'genotype']],
            on='gene',
            suffixes=('', '_2')
        )

        # 6. Collect any differences (ignoring NaN vs NaN)
        diffs = []
        for _, row in merged.iterrows():
            details = []

            # Compare phenotype
            p1, p2 = row['phenotype'], row['phenotype_2']
            if not (pd.isna(p1) and pd.isna(p2)) and p1 != p2:
                details.append(f"phenotype: {p1} vs {p2}")

            # Compare genotype
            g1, g2 = row['genotype'], row['genotype_2']
            if not (pd.isna(g1) and pd.isna(g2)) and g1 != g2:
                details.append(f"genotype: {g1} vs {g2}")

            if details:
                diffs.append(f"{row['gene']}: " + "; ".join(details))

        # 7. Write out if any were found
        if diffs:
            out_file.write(f"{base} vs {partner}\n")
            for line in diffs:
                out_file.write(line + "\n")
            out_file.write("\n")

print("Comparison complete. Differences written to 'differences.txt'.")
