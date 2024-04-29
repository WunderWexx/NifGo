# The ELT process

# The genes that have their phenotype determined the hard way should have their phenotype appended in the transform
# phase. Maybe even combine them after pivoting the genotype dataframe.
# A list needs to be made of all these genes.

# Imports
import pandas as pd
import PySimpleGUI as sg
import math


class Extract:
    """
    The data is extracted from the source files, and loaded into a pandas DataFrame.
    """

    @staticmethod
    def extract_user_specified_file(filename):
        filepath = sg.popup_get_file(f"Please select the {filename} file",
                                     title="File selection", keep_on_top=True)
        df = pd.read_csv(filepath, sep="@", header=None, engine="python")
        return df

    @staticmethod
    def pharmacydata():
        return pd.read_excel("Input/global_files/apotheekinfosysteem.xlsx")

    @staticmethod
    def nutrimarkers():
        return pd.read_excel("Input/global_files/nutri_markers.xlsx")

    def phenotype_rpt(self):
        return self.extract_user_specified_file('phenotype.rpt')

    def genotype_txt(self):
        return self.extract_user_specified_file('genotype.txt')


class Load:
    """
    The data is "loaded" into a more efficient from. Still a local DataFrame though.
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
        rowcount = dataframe[dataframe[0].str.contains("0001")].index.min()
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

    @staticmethod
    def phenotype_rpt(dataframe, genes_with_thermofisher_phenotypes):
        """
        The dataframe is in order, cleansed of:
        - The .CEL suffix in the sample_id column
        - The gene_function column
        - All genes whose phenotype is not to be determined from this file
        :param dataframe:
        :return:
        """
        remove_cel_suffix = lambda x: x.replace('.CEL','')
        dataframe['sample_id'] = dataframe['sample_id'].apply(remove_cel_suffix)

        dataframe = dataframe.drop(columns = ['gene_function'])

        boolean_mask = dataframe['gene'].isin(genes_with_thermofisher_phenotypes)
        dataframe = dataframe[boolean_mask]
        return dataframe

    @staticmethod
    def genotype_txt(dataframe):
        """
        - All columns after dbSNP_RS_ID are dropped.
        - The .CEL_call_code suffix is dropped from column names.
        :param dataframe:
        :return:
        """
        dbSNP_index = dataframe.columns.get_loc('dbSNP_RS_ID')
        dataframe = dataframe.iloc[:, :dbSNP_index + 1]

        dataframe.columns = [col.replace('.CEL_call_code', '') for col in dataframe.columns]

        return dataframe

class Ingest:
    def phenotype_rpt(self,  ThermoFisher_determined_genes):
        phenotypes_df = Extract().phenotype_rpt()
        phenotypes_df = Load().phenotype_rpt(phenotypes_df)
        phenotypes_df = Transform().phenotype_rpt(phenotypes_df, ThermoFisher_determined_genes)
        return phenotypes_df

    def genotype_txt(self, probeset_ids):
        genotypes_df = Extract().genotype_txt()
        genotypes_df = Load().genotype_txt(genotypes_df, probeset_ids)
        genotypes_df = Transform().genotype_txt(genotypes_df)
        return genotypes_df