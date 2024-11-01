# The ELT process

# Imports
import pandas as pd
import PySimpleGUI as sg
import math
import csv
import numpy as np

class Extract:
    """
    The data is extracted from the source files, and loaded into a pandas DataFrame.
    """

    def __init__(self):
        """
        Sets the field_size_limit to the maximum number the
        """
        csv.field_size_limit(1000000000)

    @staticmethod
    def extract_user_specified_file(filename):
        filepath = sg.popup_get_file(f"Please select the {filename} file",
                                     title="File selection", keep_on_top=True)
        df = pd.read_csv(filepath, sep="@", header=None, engine="python")
        return df

    @staticmethod
    def pharmacydata():
        return pd.read_excel("Input/Dataframes/apotheekinfosysteem.xlsx")

    @staticmethod
    def nutrimarkers():
        return pd.read_excel("Input/Dataframes/nutri_markers.xlsx")

    def phenotype_rpt(self):
        return self.extract_user_specified_file('phenotype.rpt')

    def genotype_txt(self):
        return self.extract_user_specified_file('genotype.txt')

    def customer_data(self):
        filepath = sg.popup_get_file(f'Please select the customer data file',
                                     title='File selection', keep_on_top=True)
        df = pd.read_excel(filepath, header=None)
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
        rowcount = dataframe[dataframe[0].str.contains("0001-0014")].index.min()
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
        First the headers are determined, then all the file's metadata is deleted from the dataframe, after which
        the dataframe is filtered on the specified genes, after which the data is split into columns and
        all columns get their names.
        :param dataframe: the genotype_txt dataframe
        :param needed_probeset_ids: the probeset_id's of the genes that need their phenotype determined by their
        rs designation.
        :return: The genotype.txt file but as a dataframe with headers and containing only the specified genes.
        """
        dataframe.columns = ['rest']
        headers_row = dataframe[dataframe['rest'].str.startswith("probeset_id")].index[0]
        headers = dataframe.iloc[headers_row]['rest'].split("\t")

        start_row = dataframe[dataframe['rest'].str.startswith("AX-")].index[0]
        dataframe = dataframe.iloc[start_row:]

        dataframe = dataframe[dataframe['rest'].str.startswith(tuple(needed_probeset_ids))]

        split_data = dataframe['rest'].str.split("\\t", expand=True)

        for idx, header in enumerate(headers):
            dataframe[header] = split_data[idx]

        dataframe.drop(['rest'], axis=1, inplace=True)
        dataframe.reset_index(drop=True, inplace=True)

        return dataframe


class Transform:
    """
    The data is transformed so that it is readable and compatible with each other.
    """
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
            """
            Drops all columns after the last sample. Samples are assumed to always start with D.
            :return: DataFrame with columns dropped
            """
            for column in self.dataframe.columns:
                if column[0] not in ['p','D','B','G']: #Being either probeset_id or something like D402000223.CEL_call_code.
                    drop_from_here_column = column
                    break
            index = self.dataframe.columns.get_loc(drop_from_here_column)
            self.dataframe = self.dataframe.iloc[:, :index + 1]

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
            pivot_columns = list(self.dataframe.columns)
            del pivot_columns[0]
            del pivot_columns[-1]
            self.dataframe = pd.melt(self.dataframe, id_vars='probeset_id', value_vars=pivot_columns)

        def reorder_and_rename_columns(self):
            """
            Reorders and renames the columns to match the structure of phenotypes.rpt.
            :return: DataFrame with reordered and renamed columns
            """
            self.dataframe = self.dataframe[['variable', 'probeset_id', 'value']]
            self.dataframe.rename(columns={'variable': 'sample_id', 'value': 'genotype'}, inplace=True)

        def add_gene_names(self):
            get_gene_name = lambda id: self.probeset_ids.get(id, 'NotPresent')
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
            "VKORC1": {"T/T": "PM", "T/C": "IM", "C/C": "NM"}
        }

        def change_gen(gene, gene_map):
            mask = self.complete_dataframe['gene'] == gene
            no_change = self.complete_dataframe.loc[mask, 'phenotype']
            self.complete_dataframe.loc[mask, 'phenotype'] = \
                np.where(self.complete_dataframe.loc[mask, 'genotype'].isin(gene_map.keys()),
                self.complete_dataframe.loc[mask, 'genotype'].map(gene_map), "ERROR")

        for gene in phenotype_map.keys():
            change_gen(gene, phenotype_map[gene])

    def keep_only_batch_relevant_data(self):
        relevant_samples = self.pheno_df['sample_id'].unique().tolist()
        self.complete_dataframe = self.complete_dataframe[self.complete_dataframe['sample_id'].isin(relevant_samples)]
