import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt

NORMAL_PHENOTYPES = ['NF', 'NM', 'non-expresser', 'negatief']

data = pd.read_excel(f'..\Miscellaneous\cardsdata20260116.xlsx')
data.columns = [
    c.replace('.1', '_phenotype') if c.endswith('.1') else f"{c}_genotype"
    for c in data.columns
]
data = data.drop(columns=data.filter(like='_genotype').columns)
data.columns = [c.replace('_phenotype','') for c in data.columns]
print(data)

# Hoeveelheid actionable genes per persoon
actionable_genes_dist = defaultdict(int)
for row in data.itertuples(index=False):
    amount_of_actionable_genes = sum(v not in NORMAL_PHENOTYPES for v in row)
    actionable_genes_dist[f"{amount_of_actionable_genes}_AG"] += 1

print(actionable_genes_dist)
print()

x = [int(k.split("_")[0]) for k in actionable_genes_dist.keys()]
y = list(actionable_genes_dist.values())
plt.figure()
bars = plt.bar(x, y)
plt.xlabel("Aantal relevante genen per persoon")
plt.ylabel("Aantal personen")
plt.title("Verdeling van relevante genen per persoon")
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        str(int(height)),
        ha="center",
        va="bottom"
    )
plt.xticks(x)
plt.show()

# Verdeling fenotypes per gen
phenotype_pct_per_gene = {gene: data[gene].value_counts(normalize=True, dropna=False) for gene in data.columns}
for i in range(data.shape[1]):
    gene = data.columns[i]
    print(phenotype_pct_per_gene[gene])
    print()

# Per individu hoeveel genen welke de combinatie PM/PM - PM/IM – UM hebben en voor welke genen
# Analyseer alleen de volgende genen en fenotype t.w. : Cyp2B6, cyp 2C9, Cyp2C19, Cyp2D6, Cyp3A4, NUDT 15, SCLO1B1, UGT1A1, VKORC1
import math
import pandas as pd

# If your phenotype values are not exactly PM/IM/UM, add mappings here.
def norm_pheno(x):
    if pd.isna(x):
        return None
    s = str(x).strip().upper()
    # optional aliases (edit to your real values)
    aliases = {
        "PF": "PM",
        "DF": "IM",
    }
    return aliases.get(s, s)

def nC2(n: int) -> int:
    return n * (n - 1) // 2

def sample_line(row: pd.Series, sample_label: str) -> str:
    # row has genes as index, phenotypes as values
    pm_genes = [g for g, v in row.items() if norm_pheno(v) == "PM"]
    im_genes = [g for g, v in row.items() if norm_pheno(v) == "IM"]
    um_genes = [g for g, v in row.items() if norm_pheno(v) == "UM"]

    # count combinations (unordered)
    combos = nC2(len(pm_genes)) + (len(pm_genes) * len(im_genes)) + len(um_genes)

    # build verbose text (each gene once)
    parts = (
        [f"{g} PM" for g in pm_genes] +
        [f"{g} IM" for g in im_genes] +
        [f"{g} UM" for g in um_genes]
    )

    if parts:
        return f"{sample_label}: " + " / ".join(parts) + f" ({combos} combinaties)"
    else:
        return f"{sample_label}: (0 combinaties)"

# Choose genes (or use all columns)
genes = ['CYP2B6','CYP2C9','CYP2C19','CYP2D6','CYP3A4','NUDT15','SLCO1B1','UGT1A1','VKORC1']
sub = data[genes].copy()

# Print lines
lines = []
for i, (_, row) in enumerate(sub.iterrows(), start=1):
    line = sample_line(row, f"Sample {i}")
    lines.append(line)
    print(line)

# If you want it stored in a dataframe column:
out = pd.DataFrame({"summary": lines})
# out.to_excel("sample_summaries.xlsx", index=False)