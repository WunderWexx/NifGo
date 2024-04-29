# Where everything comes together

# imports
import ELT
import utilities as util
import pandas as pd

# settings
pd.options.mode.chained_assignment = None  # default='warn'

#Global variables
ThermoFisher_determined_genes = [
    'CACNA1S',
    'CFTR',
    'COMT',
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
    'F2',
    'F5',
    'G6PD',
    'GSTP1',
    'IFNL3',
    'MTHFR1298',
    'MTHFR677',
    'MTRNR1',
    'NAT1',
    'NAT2',
    'RYR1',
    'SLCO1B1',
    'TPMT',
    'UGT1A1',
    'VKORC1'
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
phenotypes_df = ELT.Ingest().phenotype_rpt(ThermoFisher_determined_genes)
util.store_dataframe(phenotypes_df, 'phenotypes')
util.printEntire(phenotypes_df)

genotypes_df = ELT.Ingest().genotype_txt(probeset_id_dict.keys())
util.store_dataframe(genotypes_df, 'genotypes')
util.printEntire(genotypes_df)