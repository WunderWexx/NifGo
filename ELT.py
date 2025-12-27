"""The Extract Load, and Transform process"""

# Imports
import pandas as pd
import math
import numpy as np

# Lists necessary for importing data
ThermoFisher_determined_genes = [
    "CACNA1S",
    "CFTR",
    "CYP1B1", #Wordt geleverd door Tahar
    "CYP2A6",
    "CYP2C8",
    "CYP2E1",
    "CYP2F1",
    "CYP4F2",
    "GSTM1",
    "GSTT1", #Wordt geleverd door Tahar
    "MTRNR1",
    "NAT1",
    "NAT2",
    "CYP1A2",
    "CYP2B6",
    "CYP2C9",
    "CYP2C19",
    "CYP2D6",
    "CYP3A4",
    "CYP3A5",
    "DPYD",
    "G6PD",
    "NUDT15",
    "TPMT",
    "UGT1A1",
    "GSTP1",
    "ABCG2"
]

# MULTIPLE_SNP represents that determining the genotype is dependent on multiple SNP's and will be handled via HandlingUnknowns.py
probeset_id_dict = {
    'ABCB1': ['AX-112253889'],
    'ACE': ['AX-40214457'],
    'ADIPOQ': ['AX-41185381'],
    'ADRA2A': ['AX-14792713'],
    'ALDH2': ['AX-11579885'],
    'AMDHD1': ['AX-17082373'],
    'BCO1': ['AX-82997505'],
    'BChE': ['MULTIPLE_SNP'],
    'BDNF': ['AX-11561914'],
    'COMT': ['AX-112185476'],
    'CYP1A1': ['AX-173402723'],
    'CYP17A1': ['AX-38703715'],
    'CYP24A1': ['AX-11314597'],
    'CYP2R1': ['AX-39007361'],
    'DHCR7 / NADSYN1': ['AX-39157579'],
    'DRD2': ['AX-165872577'],
    'F2': ['AX-11344567'],
    'F5': ['AX-51294184'],
    'FTO': ['AX-11151648'],
    'GC': ['AX-41517991'],
    'GCK, YKT6': ['AX-15693373'],
    'HLA-B*1502': ['UNKNOWN'], # HLA-B*5701, en HLA-B*1502 moeten nog ingevuld worden.
    'HLA-B*5701': ['UNKNOWN'], # HLA-B*5701, en HLA-B*1502 moeten nog ingevuld worden.
    'HLA-A*3101': ['MULTIPLE_SNP'],
    'IFNL3/IL28B': ['AX-112063628'],
    'IGF1': ['AX-11469525'],
    'LDLR': ['AX-11569288'],
    'LOC105447645; FUT2': ['AX-11536589'],
    'MAO-B': ['AX-112075557'],
    'MC4R': ['AX-11340068'],
    'MTHFR1298': ['AX-165872626'],
    'MTHFRC677T': ['AX-51283185'],
    'MTNR1B': ['AX-16761721'],
    'MnSOD': ['AX-41896949'],
    'NBPF3': ['AX-11515438'],
    'NQ01': ['AX-11344636'],
    'OPRM1': ['AX-11344570'],
    'PON1': ['AX-11575218'],
    'SLCO1B1': ['AX-165873829'],
    'Sult1A1': ['MULTIPLE_SNP'],
    'Sult1E1': ['AX-112067905'],
    'TCF7L2': ['AX-11652775'],
    'TMEM165; CLOCK': ['AX-165873266'],
    'TNFa': ['AX-41953347'],
    'UCP2': ['AX-83275492'],
    'VDR_1': ['AX-11620565'],
    'VDR_2': ['AX-96113594'],
    'VDR_3': ['AX-112158761'],
    'VDR_4': ['AX-165873135'],
    'VKORC1': ['AX-122936861']
}

class Extract:
    """
    The data is extracted from the source files, and loaded into a pandas DataFrame.
    """

    @staticmethod
    def extract_genotype_txt(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for rownumber, line in enumerate(f):
                if line.startswith("probeset_id"):
                    header_row = rownumber
                    break

        if header_row == None:
            raise ValueError("Couldn't find a header line starting with 'probeset_id'.")

        needed_columns  = lambda name: name.endswith(".CEL_call_code") or name in {"probeset_id", "dbSNP_RS_ID", "sex_metrics"}

        df = pd.read_csv(
            filepath,
            sep="\t",
            header=0,  # first row *after* skiprows is the header
            skiprows=header_row,  # skip metadata lines so header is the next line
            usecols=needed_columns,  # keep only needed columns
            low_memory=False
        )
        return df

class Load:
    """
    The data is "loaded" into a more efficient form. Still a local DataFrame though.
    """

    @staticmethod
    def phenotype_rpt(dataframe):
        """
        Removes the first lines of the phenotype.rpt file (which is metadata) and removes any control samples present
        at the end of the document. The single giant column is then split into five columns, and the rest of the data
        is lost.
        :param dataframe: phenotype.rpt dataframe
        :return: The cleaned phenotype.rpt dataframe
        """
        rowcount = dataframe[dataframe[0].str.match(r'^\d+')].index.min()
        dataframe = dataframe.iloc[rowcount:]
        dataframe.reset_index(drop=True, inplace=True)

        rowcount = dataframe[dataframe[0].str.contains("control")].index.min()
        if not math.isnan(rowcount):
            dataframe = dataframe.iloc[:rowcount]
            dataframe.reset_index(drop=True, inplace=True)

        dataframe.columns = ["rest"]
        headers = ["index", "sample_id", "gene", "phenotype", "gene_function", "known_call"]
        for name in headers:
            split = dataframe["rest"].str.split("\\t", n=1, expand=True)
            dataframe[name] = split[0]
            dataframe["rest"] = split[1]
        dataframe.drop(["rest", "index"], axis=1, inplace=True)

        return dataframe

    @staticmethod
    def genotype_txt(dataframe, needed_probeset_ids):
        """
        Filters the needed probeset id's from the dataframe, and drops the unneeded columns.
        """

        # Extract probeset_id list from nested list
        needed_ids = [id_list[0] for id_list in needed_probeset_ids]
        dataframe = dataframe[dataframe['probeset_id'].str.startswith(tuple(needed_ids))]
        dataframe.drop(columns = ["sex_metrics", 'dbSNP_RS_ID'], inplace=True)
        return dataframe


class Transform:
    """
    The data is transformed so that it is readable and compatible with each other.
    """
    class customer_data:
        def columns_and_dates(self, customerdata_df):
            customerdata_df = customerdata_df
            customerdata_df = customerdata_df.rename(
                columns={0: 'sample_id', 1: 'sex', 2: 'initials', 3: 'lastname', 4: 'birthdate'})
            customerdata_df = customerdata_df.fillna('')
            customerdata_df['sample_id'] = customerdata_df['sample_id'].astype(str)
            customerdata_df = customerdata_df.apply(
                lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))
            customerdata_df['birthdate'] = customerdata_df['birthdate'].dt.strftime('%Y-%m-%d')
            customerdata_df['birthdate'] = customerdata_df['birthdate'].fillna('20237-01-01')
            customerdata_df.sort_values(by='sample_id', ascending=True, inplace=True)
            customerdata_df.reset_index(inplace=True, drop=True)
            return customerdata_df

    class phenotype_rpt:
        """
        Transforms the phenotype_rpt dataframe.
        """
        def __init__(self, dataframe):
            self.dataframe = dataframe

        def remove_cel_suffix(self):
            """
            Removes the .CEL suffix from the sample_id column of the dataframe.
            :return: DataFrame with sample_id column modified
            """
            dataframe = self.dataframe
            remove_cel_suffix = lambda x: x.replace('.CEL', '')
            dataframe['sample_id'] = dataframe['sample_id'].apply(remove_cel_suffix)
            self.dataframe = dataframe

        def drop_gene_function(self):
            """
            Drops the gene_function column from the dataframe.
            :return: DataFrame with gene_function column dropped
            """
            dataframe = self.dataframe.drop(columns=['gene_function'])
            self.dataframe = dataframe

        def filter_thermofisher_genes(self, genes_with_thermofisher_phenotypes):
            """
            Filters the dataframe based on genes whose phenotypes are specified.
            :param genes_with_thermofisher_phenotypes: List of genes with phenotypes to be determined
            :return: Filtered DataFrame
            """
            boolean_mask = self.dataframe['gene'].isin(genes_with_thermofisher_phenotypes)
            dataframe = self.dataframe[boolean_mask]
            self.dataframe = dataframe

        def rename_known_call(self):
            self.dataframe.rename(columns={'known_call':'genotype'}, inplace=True)

    class genotype_txt:
        """
        Transforms the genotype_txt dataframe
        """
        def __init__(self, dataframe, probeset_ids):
            self.dataframe = dataframe
            self.probeset_ids = probeset_ids

        def drop_columns_after_last_sample(self):
            cols = self.dataframe.columns
            keep = ['probeset_id'] + [c for c in cols if c.endswith('.CEL_call_code')]
            self.dataframe = self.dataframe[keep]

        def drop_cel_call_code_suffix(self):
            """
            Removes the .CEL_call_code suffix from column names.
            :return: DataFrame with column names modified
            """
            self.dataframe.columns = [col.replace('.CEL_call_code', '') for col in self.dataframe.columns]

        def unpivot_dataframe(self):
            """
            Unpivots the DataFrame to match the structure of phenotypes.rpt.
            :return: Unpivoted DataFrame
            """
            pivot_columns = [c for c in self.dataframe.columns if c != 'probeset_id']
            self.dataframe = pd.melt(self.dataframe, id_vars='probeset_id', value_vars=pivot_columns)

        def reorder_and_rename_columns(self):
            """
            Reorders and renames the columns to match the structure of phenotypes.rpt.
            :return: DataFrame with reordered and renamed columns
            """
            self.dataframe = self.dataframe[['variable', 'probeset_id', 'value']]
            self.dataframe.rename(columns={'variable': 'sample_id', 'value': 'genotype'}, inplace=True)

        def add_gene_names(self):
            flattened_dict = {ids[0]: gene for gene, ids in self.probeset_ids.items()}
            get_gene_name = lambda id: flattened_dict.get(id, 'NotPresent')
            new_column = self.dataframe['probeset_id'].map(get_gene_name)
            self.dataframe['gene'] = new_column

class DataPreparation:
    def __init__(self, geno_df, pheno_df):
        self.geno_df = geno_df
        self.pheno_df = pheno_df

    def select_geno_columns_for_insertion_into_pheno(self):
        self.geno_df['phenotype'] = 'Not_Determined'
        insertion_geno_df = self.geno_df[['sample_id','gene','phenotype','genotype']]
        return insertion_geno_df

    def merge_geno_and_phenotype_dataframes(self):
        insertion_geno_df = self.select_geno_columns_for_insertion_into_pheno()
        complete_dataframe = pd.concat([self.pheno_df, insertion_geno_df])
        complete_dataframe.sort_values(by=['sample_id','gene'], inplace=True)
        complete_dataframe.reset_index(drop=True, inplace=True)
        self.complete_dataframe = complete_dataframe

    def move_MTHFR1298_and_CYP2C19(self):
        # Define the values and corresponding move down counts
        values_to_find = ['CYP2C19', 'MTHFRA1298C']
        move_down_counts = [2, 1]

        for value_to_find, move_down_by in zip(values_to_find, move_down_counts):
            df = self.complete_dataframe
            # Find the indices of the rows to move
            rows_to_move_indices = df[df['gene'] == value_to_find].index.tolist()

            # Extract the rows to be moved
            rows_to_move = df.loc[rows_to_move_indices]

            # Remove the rows from the DataFrame
            df = df.drop(rows_to_move_indices).reset_index(drop=True)

            # Calculate new indices for the rows to be inserted
            new_indices = [min(index + move_down_by, len(df)) for index in rows_to_move_indices]

            # Sort new indices and rows to insert in the order to avoid index shifting issues
            sorted_new_indices = sorted(new_indices)
            sorted_rows_to_move = rows_to_move.reset_index(drop=True)

            # Insert the rows back into the DataFrame at the new indices
            for i, new_index in enumerate(sorted_new_indices):
                df = pd.concat([df.iloc[:new_index], sorted_rows_to_move.iloc[[i]], df.iloc[new_index:]]).reset_index(
                    drop=True)
            self.complete_dataframe = df

    def determine_phenotype(self):
        """
        Makes a column of determined genotypes.
        :return: A list of phenotypes corresponding to the entered sample.
        """
        phenotype_map = {
            "F2": {"G/G": "PM", "A/A": "risico", "G/A": "risico", "A/G": "risico"},
            "F5": {"C/C": "PM", "T/T": "risico", "C/T": "risico", "T/C": "risico"},
            "OPRM1": {"A/A": "NM", "G/G": "PM", "A/G": "IM", "G/A": "IM"},
            "MTHFRA1298C": {"T/T": "NM", "G/G": "PM", "T/G": "IM", "G/T": "IM"},
            "MTHFRC677T": {"G/G": "NM", "A/A": "PM", "G/A": "IM", "A/G": "IM"},
            "HLA-B*1502": {"G/G": "negatief", "C/C": "risico", "G/C": "risico", "C/G": "risico"},
            "ABCB1": {"G/G": "NM", "A/A": "PM", "G/A": "IM", "A/G": "IM"},
            "COMT": {"A/A": "PM", "A/G": "IM", "G/G": "NM"},
            "SLCO1B1": {"T/T": "NF", "T/C": "DF", "C/C": "PF"},
            "VKORC1": {"T/T": "PM", "T/C": "IM", "C/C": "NM"},
            "ABCG2":{"rs2231142G/rs2231142G":"NF", "rs2231142G/rs2231142T":"DF","rs2231142T/rs2231142G":"DF", "rs2231142T/rs2231142T":"PF"},
            "CYP1A1":{"T/T":"NM", "T/C":"IM", "C/C":"PM"}
        }

        def change_gen(gene, gene_map):
            mask = self.complete_dataframe['gene'] == gene
            no_change = self.complete_dataframe.loc[mask, 'phenotype']
            self.complete_dataframe.loc[mask, 'phenotype'] = \
                np.where(self.complete_dataframe.loc[mask, 'genotype'].isin(gene_map.keys()),
                self.complete_dataframe.loc[mask, 'genotype'].map(gene_map), "ERROR")

        for gene in phenotype_map.keys():
            change_gen(gene, phenotype_map[gene])

    def merge_VDR(self):
        unique_samples = self.complete_dataframe['sample_id'].unique().tolist()
        missing_genes = set()

        for sample in unique_samples:
            divergent_count = 0
            has_invalid_part = False
            sample_id_mask = self.complete_dataframe['sample_id'] == sample

            # Check each VDR sub-gene and count divergences, track missing/invalid genes
            for gene, expected_base in [
                ('VDR_1', 'G'),
                ('VDR_2', 'A'),
                ('VDR_3', 'T'),
                ('VDR_4', 'C')
            ]:
                mask = sample_id_mask & (self.complete_dataframe['gene'] == gene)
                values = self.complete_dataframe.loc[mask, 'genotype'].values

                bad_values = {'ERROR', 'MISSING', 'Not_PM', 'Not_NM', 'Not_IM', 'Not_RM',
                              'Not_Determined', 'Not_UM', 'EM', 'unknown', '---', '', ','}

                genotype = values[0].strip().upper() if values.size > 0 else ''
                # invalid if empty/bad or not a diploid call (no '/')
                if (not genotype) or (genotype in bad_values) or ('/' not in genotype):
                    missing_genes.add(gene)
                    has_invalid_part = True
                    continue  # no divergence counting for invalid parts

                a1, a2, *_ = genotype.split('/')
                a1, a2 = a1.strip(), a2.strip()
                # Count ONE divergence if it's not exactly expected/expected
                if not (a1 == expected_base and a2 == expected_base):
                    divergent_count += 1

            # Determine phenotype and genotype
            if has_invalid_part:
                phenotype, combined_genotype = '---', '---'
            else:
                if divergent_count >= 2:
                    phenotype, combined_genotype = 'PF', 'MT/MT'
                elif divergent_count == 1:
                    phenotype, combined_genotype = 'IF', 'WT/MT'
                else:
                    phenotype, combined_genotype = 'NF', 'WT/WT'

            # Append combined VDR row
            VDR_row = {
                'sample_id': sample,
                'gene': 'VDR',
                'phenotype': phenotype,
                'genotype': combined_genotype
            }
            self.complete_dataframe = pd.concat(
                [self.complete_dataframe, pd.DataFrame([VDR_row])],
                ignore_index=True
            )

        # Remove individual VDR_* rows
        self.complete_dataframe = self.complete_dataframe[
            ~self.complete_dataframe['gene'].str.match(r'VDR_\d+', na=False)
        ]

    def keep_only_batch_relevant_data(self):
        relevant_samples = self.pheno_df['sample_id'].unique().tolist()
        self.complete_dataframe = self.complete_dataframe[self.complete_dataframe['sample_id'].isin(relevant_samples)]