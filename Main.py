# Where everything comes together

# imports
import ELT
import utilities as util
import pandas as pd
import Nifgo_proprietary_changes as changes

# Could be rewritten to be clearer.

# settings
pd.options.mode.chained_assignment = None  # default='warn'

#Global variables
ThermoFisher_determined_genes = [
    'CACNA1S',
    'CFTR',
    'CYP1A2',
    'CYP2A6',
    'CYP2B6',
    'CYP2C8',
    'CYP2C9',
    'CYP2C19',
    'CYP2D6',
    'CYP2E1',
    'CYP3A4',
    'CYP3A5',
    'CYP4F2',
    'DPYD',
    'G6PD',
    'GSTP1',
    'IFNL3',
    'MTRNR1',
    'NAT1',
    'NAT2',
    'RYR1',
    'TPMT',
    'UGT1A1',
]
probeset_id_dict = gene_probe_mapping = {
    "AX-11340068": "MC4R",
    "AX-11344567": "F2",
    "AX-11344570": "OPRM1",
    "AX-11515438": "NBPF3",
    "AX-11536589": "LOC105447645;FUT2",
    "AX-11561914": "BDNF-AS;BDNF",
    "AX-11579885": "ALDH2",
    "AX-11620565": "VDR",
    "AX-11626417": "BCO1",
    "AX-11652775": "TCF7L2",
    "AX-122940319": "Sult1A1",
    "AX-14792713": "ADRA2A",
    "AX-15693373": "GCK,YKT6",
    "AX-165872626": "MTHFRA1298C",
    "AX-165873266": "TMEM165;CLOCK",
    "AX-16761721": "MTNR1B",
    "AX-32261461": "ACE",
    "AX-39157579": "NADSYN1",
    "AX-40462051": "LOC105447645;FUT2",
    "AX-41185381": "ADIPOQ",
    "AX-41517991": "GC",
    "AX-41953347": "TNFa",
    "AX-51283185": "MTHFRC677T",
    "AX-51294184": "F5",
    "AX-82997505": "BCO1",
    "AX-83207592": "HLA-B*1502",
    "AX-83275492": "UCP2",
    "AX-83376893": "ANKK1",
    "AX-88902521": "Nudt15",
    "AX-112253889": "ABCB1",
    "AX-165872577": "DRD2",
    "AX-11151648": "FTO",
    "AX-11469525": "IGF1",
    "AX-11569288": "LDLR",
    "AX-112075557": "MAO-B",
    "AX-112067905": "Sult1E1",
    "AX-112185476": "COMT",
    "AX-165873829": "SLCO1B1",
    "AX-122936861": "VKORC1"
}

# body
phenotypes_df = ELT.Extract().phenotype_rpt()
phenotypes_df = ELT.Load().phenotype_rpt(phenotypes_df)
phenotype_transformation = ELT.Transform().phenotype_rpt(phenotypes_df)
print('phenotype import DONE')
phenotype_transformation.remove_cel_suffix()
phenotype_transformation.drop_gene_function()
phenotype_transformation.filter_thermofisher_genes(ThermoFisher_determined_genes)
phenotype_transformation.rename_known_call()

phenotypes_df = phenotype_transformation.dataframe
util.store_dataframe(phenotypes_df, 'phenotypes')
print('phenotype transformation DONE')

print('genotype import [...]',end='\r')
genotypes_df = ELT.Extract().genotype_txt()
genotypes_df = ELT.Load().genotype_txt(genotypes_df, probeset_id_dict.keys())
print('genotype import DONE')
genotypes_transformation = ELT.Transform().genotype_txt(genotypes_df, probeset_id_dict)
genotypes_transformation.drop_columns_after_dbsnp()
genotypes_transformation.drop_cel_call_code_suffix()
genotypes_transformation.unpivot_dataframe()
genotypes_transformation.reorder_and_rename_columns()
genotypes_transformation.add_gene_names()

genotypes_df = genotypes_transformation.dataframe
util.store_dataframe(genotypes_df, 'genotypes')
print('genotype transformation DONE')

data_preparation = ELT.DataPreparation(genotypes_df, phenotypes_df)
data_preparation.determine_phenotype()
data_preparation.merge_geno_and_phenotype_dataframes()

genotypes_df = data_preparation.geno_df
complete_dataframe = data_preparation.complete_dataframe
util.store_dataframe(complete_dataframe, 'complete')
print('complete dataframe creation DONE')

print('implementing NifGo changes [...]',end='\r')
general_changes = changes.GeneralChanges(complete_dataframe)
general_changes.pick_first_result()
complete_dataframe = general_changes.dataframe

phenotype_changes = changes.PhenotypeChanges(complete_dataframe)
phenotype_changes.change_EM_phenotypes_to_NM()
phenotype_changes.CACNA1S()
phenotype_changes.RYR1()
phenotype_changes.G6DP()
# phenotype_changes.CYP1A2() The following function seems to have never been carried out...
phenotype_changes.CYP2C19()
phenotype_changes.CYP3A4() # Should be checked with the next dataset.

complete_dataframe = phenotype_changes.dataframe
util.store_dataframe(complete_dataframe, 'complete')
print('implementing NifGo changes DONE')