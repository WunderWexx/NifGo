import Utilities as util
import pandas as pd

# Load geslacht.xlsx (first sheet)
geslacht_xlsx = util.popup_get_file("Geslachten")
geslacht_dict = pd.read_excel(geslacht_xlsx, sheet_name=None, header=0)
geslacht_df = list(geslacht_dict.values())[0]  # take the first sheet

# Load klantdata.xlsx (first sheet)
klantdata_xlsx = util.popup_get_file("Klantdata")
klant_dict = pd.read_excel(klantdata_xlsx, sheet_name=None)
klant_df = list(klant_dict.values())[0]  # take the first sheet
klant_df.columns = ["sample_id", "sex", "initials", "last_name", "birthdate"]

# Map klant_df.sex to male/female
sex_map = {"Hr.": "male", "Mw.": "female"}
klant_df["sex_mapped"] = klant_df["sex"].map(sex_map)

# Merge on sample_id vs Sample Filename
merged = pd.merge(
    geslacht_df,
    klant_df,
    left_on="Sample Filename",
    right_on="sample_id",
    how="inner"
)

# Compare sexes
merged["sex_match"] = merged["QC computed_sex"] == merged["sex_mapped"]

# Show mismatches
mismatches = merged[~merged["sex_match"]]

print("\nMismatches found:")
print(mismatches[["sample_id", "QC computed_sex", "sex", "sex_mapped"]])
