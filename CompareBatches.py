from pathlib import Path
import pandas as pd
from docx import Document

# ==== CONFIGURATION ====
# Customer-data files:
CD_FILES = {
    'batch1': Path(r"C:/Users/Jarno/PycharmProjects/NifGo/Input/NifgoFiles/2025-05-24-B6/klantgegevens.xlsx"),
    'batch2': Path(r"C:/Users/Jarno/PycharmProjects/NifGo/Input/NifgoFiles/2025-05-07-B5/klantgegevens.xlsx"),
}

# Report folders:
REPORT_FOLDERS = {
    'batch1': Path(r"C:/Users/Jarno/PycharmProjects/NifGo/TEMP/Reports_B6"),
    'batch2': Path(r"C:/Users/Jarno/PycharmProjects/NifGo/TEMP/Reports_B5"),
}

# Report filename templates:
REPORT_TEMPLATES = {
    'farma': 'FarmacogeneticReport_{sample_id}.docx',
    'nutri': 'NutrigenomicsReport_{sample_id}.docx',
}

# For each report type, which tables to read, and column indices:
REPORT_TABLES = {
    'farma': {
        'tables': [1],
        'phenotype_col': 1,
        'uitslag_col': 2,
        'label': '[FARMA]'
    },
    'nutri': {
        'tables': [1, 2],
        'uitslag_col': -1,
        'label': '[NUTRI]'
    },
}

# ==== HELPERS ====
def read_customerdata(path: Path) -> pd.DataFrame:
    cd = pd.read_excel(path, header=None, engine='openpyxl')
    cd = cd.rename(columns={0: 'sample_id', 1: 'initials', 2: 'lastname', 3: 'birthdate'})
    cd['lastname'] = cd['lastname'].astype(str).str.strip().str.lower()
    return cd

def merge_customers(cd1: pd.DataFrame, cd2: pd.DataFrame) -> pd.DataFrame:
    merged = cd1.merge(
        cd2[['lastname', 'sample_id']],
        on='lastname', how='inner',
        suffixes=('_file1', '_file2')
    )
    merged['name'] = merged['initials'] + ' ' + merged['lastname'].str.title()
    return merged[['name', 'sample_id_file1', 'sample_id_file2']]

def parse_report(path: Path, spec: dict) -> dict:
    """Extract per-gene data per spec: returns gene-> tuple or string."""
    doc = Document(path)
    data = {}
    for idx in spec['tables']:
        table = doc.tables[idx]
        for row in table.rows[1:]:  # skip header
            gene = row.cells[0].text.strip()
            if 'phenotype_col' in spec:
                phen = row.cells[spec['phenotype_col']].text.strip()
            else:
                phen = None
            uitslag = row.cells[spec['uitslag_col']].text.strip()
            data[gene] = (phen, uitslag) if phen is not None else uitslag
    return data

def compare_reports(d1: dict, d2: dict, spec: dict) -> list[str]:
    """Compare two report dicts according to spec, return formatted diffs."""
    diffs = []
    label = spec['label']
    for gene in sorted(set(d1) | set(d2)):
        v1 = d1.get(gene, (None, '<missing>'))
        v2 = d2.get(gene, (None, '<missing>'))
        if isinstance(v1, tuple):  # farmacogenetic: (phen, uitslag)
            phen1, uit1 = v1
            phen2, uit2 = v2
            if phen1 != phen2:
                diffs.append(f"    {label} {gene} phenotype: {phen1}  !=  {phen2}")
            if uit1 != uit2:
                diffs.append(f"    {label} {gene} uitslag:    {uit1}  !=  {uit2}")
        else:  # nutrigenomics: just uitslag
            if v1 != v2:
                diffs.append(f"    {label} {gene}: {v1}  !=  {v2}")
    return diffs

# ==== MAIN SCRIPT ====
def main():
    # Load & merge customer data
    cd1 = read_customerdata(CD_FILES['batch1'])
    cd2 = read_customerdata(CD_FILES['batch2'])
    customers = merge_customers(cd1, cd2)
    print("=== In both files ===")
    print(customers.to_string(index=False))

    # Detect single/missing samples
    all_cd = cd1.merge(cd2[['lastname','sample_id']], on='lastname', how='outer',
                       suffixes=('_file1','_file2'))
    all_cd['name'] = all_cd['initials'].fillna('') + ' ' + all_cd['lastname'].str.title()
    only_one = all_cd[all_cd['sample_id_file1'].isna() ^ all_cd['sample_id_file2'].isna()]
    none_at_all = all_cd[all_cd['sample_id_file1'].isna() & all_cd['sample_id_file2'].isna()]
    print("\n=== Only in one file ===")
    print(only_one[['name','sample_id_file1','sample_id_file2']].to_string(index=False))
    print("\n=== In neither file ===")
    print(none_at_all['name'].to_string(index=False))

    # Compare reports
    out_path = Path('Output/Diagnostics/differences.txt')
    with open(out_path, 'w', encoding='utf-8') as fout:
        for _, row in customers.iterrows():
            name = row['name']
            id1 = row['sample_id_file1']
            id2 = row['sample_id_file2']

            person_diffs = []
            for rpt_type, spec in REPORT_TABLES.items():
                tpl = REPORT_TEMPLATES[rpt_type]
                p1 = REPORT_FOLDERS['batch1'] / tpl.format(sample_id=id1)
                p2 = REPORT_FOLDERS['batch2'] / tpl.format(sample_id=id2)
                if not p1.exists() or not p2.exists():
                    continue

                d1 = parse_report(p1, spec)
                d2 = parse_report(p2, spec)
                person_diffs += compare_reports(d1, d2, spec)

            if person_diffs:
                fout.write(f"{name} ({id1} vs {id2}):\n")
                fout.write("\n".join(person_diffs) + "\n\n")

    print(f"Differences written to {out_path.resolve()}")

if __name__ == '__main__':
    main()
