# After the program has run, the output needs to be checked for mistakes both human and software. This process should be automated as much as possible.

# Voor de farmacogenetische rapporten:
# Zijn de fenotypes plausibel? [DONE]
# Zijn de genotypes plausibel?
# Zijn alle genen present?

# Voor de info sheets:
# Zijn de apothekercodes plausibel?
# Zijn de fenotypes plausibel? [DONE]
# Zijn de genotypes plausibel?
# Zijn alle genen present?

# Voor de nutrinomics:
# Kloppen de dbSNP nummers?
# Zijn de genotypes plausibel?
# Zijn alle genen present?

# Algemeen:
# Frequentie van allellen (moeilijk / tijdrovend)
# Afwijking van de norm
# Frequentie van fenotypes

# Metadata:
# Software versie
# rapporten gegenereerd in X seconden
# Aantal rapporten
# Aantal samples
# Zodoende aantal batches

import Utilities as util
from os import listdir
from os.path import isfile, join
from docx import Document

class Diagnostics:
    def __init__(self):
        self.path = 'Output\Reports'
        self.reports = [file for file in listdir(self.path) if isfile(join(self.path, file))]
        self.genes_by_phenotype_type = {
            'NM_phenotype_genes': [
                'CYP1A2', 'CYP2A6', 'CYP2B6', 'CYP2C19', 'CYP2C8', 'CYP2C9',
                'CYP2D6', 'CYP2E1', 'CYP3A4', 'CYP4F2', 'DPYD', 'F2', 'F5',
                'G6PD', 'GSTP1', 'IFNL3', 'MTHFR1298', 'MTHFR677', 'RYR1',
                'TPMT', 'UGT1A1', 'VKORC1'
            ],
            'NA_phenotype_genes': ['NAT1', 'NAT2'],
            'NF_phenotype_genes': ['CACNA1S', 'CFTR', 'SLCO1B1','MTRNR1'],
            'expressor_phenotype_genes': ['CYP3A5'],
            'pos_neg_phenotype_genes': ['HLA-B*1502']
        }
        self.possible_phenotypes_by_type = {
            'NM_phenotype_genes': ['UM','RM','NM','IM','PM'],
            'NA_phenotype_genes': ['RA','NA','IA','SA'],
            'NF_phenotype_genes': ['IF','NF','DF','PF'],
            'expressor_phenotype_genes': ['non-expressor','homozygoot','heterozygoot'],
            'pos_neg_phenotype_genes': ['positief','negatief','risico']
        }

    def get_doc_type(self, document_path):
        if util.is_substring_present_in_substring(document_path, 'FarmacogeneticReport'):
            return 'Farmacogenetics'
        elif util.is_substring_present_in_substring(document_path, 'InfoSheet'):
            return 'InfoSheet'
        elif util.is_substring_present_in_substring(document_path, 'NutrinomicsReport'):
            return 'Nutrinomics'
        else:
            return 'Medication'

    def check_phenotypes(self, document_path):
        document = Document(document_path)

        table_to_check = None
        if util.is_substring_present_in_substring(document_path, 'FarmacogeneticReport'):
            table_to_check = 1
        elif util.is_substring_present_in_substring(document_path, 'InfoSheet'):
            table_to_check = 0

        genes_to_check = []
        table = document.tables[table_to_check]
        for row in table.rows[1:]:
            gene = row.cells[0].text
            phenotype = row.cells[1].text
            phenotype_type = util.get_key_from_nested_value(self.genes_by_phenotype_type, gene)
            if phenotype_type in list(self.possible_phenotypes_by_type.keys()):
                if phenotype not in self.possible_phenotypes_by_type[phenotype_type]:
                    genes_to_check.append(gene)
                else:
                    pass
        return genes_to_check

    def check_gene_presence(self, document_path):
        pharmacogenetic_genes_list = [
            'CACNA1S', 'CFTR', 'CYP1A2', 'CYP2A6', 'CYP2B6', 'CYP2C19',
            'CYP2C8', 'CYP2C9', 'CYP2D6', 'CYP2E1', 'CYP3A4', 'CYP3A5',
            'CYP4F2', 'DPYD', 'F2', 'F5', 'G6PD', 'GSTP1', 'HLA-B*1502',
            'IFNL3', 'MTHFR1298', 'MTHFR677', 'MTRNR1', 'NAT1', 'NAT2',
            'RYR1', 'SLCO1B1', 'TPMT', 'UGT1A1', 'VKORC1'
        ]
        infosheet_genes_list = [
            'CYP1A2', 'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP2D6', 'CYP3A4',
            'CYP3A5', 'DPYD', 'HLA-B*1502', 'MTHFR677', 'SLCO1B1',
            'TPMT', 'UGT1A1', 'VKORC1'
        ]
        nutrinomics_genes_list = [
            'ABCB1', 'ACE', 'ADIPOQ', 'ADRA2A', 'ALDH2', 'BCO1', 'BDNF-AS', 'BDNF',
            'DRD2', 'FTO', 'GC', 'GCK', 'YKT6', 'IGF1', 'LDLR', 'LOC105447645',
            'FUT2', 'MAO-B', 'MC4R', 'MTNR1B', 'NADSYN1', 'NBPF3', 'Sult1A1',
            'Sult1E1', 'TCF7L2', 'TMEM165', 'CLOCK', 'TNFa', 'UCP2', 'VDR'
        ]
        document = Document(document_path)
        doc_type = self.get_doc_type(document_path)

        match doc_type:
            case 'Farmacogenetics':
                table_to_check = 1
                table = document.tables[table_to_check]
                present_genes = []
                for row in table.rows[1:]:
                    gene = row.cells[0].text
                    present_genes.append(gene)
                if not util.lists_contain_same_data(pharmacogenetic_genes_list, present_genes):
                    return False

            case 'InfoSheet':
                table_to_check = 0
                table = document.tables[table_to_check]
                present_genes = []
                for row in table.rows[1:]:
                    gene = row.cells[0].text
                    present_genes.append(gene)
                if not util.lists_contain_same_data(infosheet_genes_list, present_genes):
                    return False

            case 'Nutrinomics':
                table_to_check = 0
                table = document.tables[table_to_check]
                present_genes = []
                for row in table.rows[1:]:
                    gene = row.cells[0].text
                    present_genes.append(gene)
                if not util.lists_contain_same_data(nutrinomics_genes_list, present_genes):
                    return False

        return True


class PharmacoDiagnostics(Diagnostics):
    def pharmaco_reports_diagnostics(self):
        diag_file = open('Output/Diagnostics/pharmaco_reports_diagnostics.txt','w')
        diag_file.write('FarmacogeneticReport diagnostics\n')
        for report in self.reports:
            if util.is_substring_present_in_substring(report, 'FarmacogeneticReport'):
                document_path = self.path + '\\' + report
                sample_id = document_path.split('_')[1]

                # Checking if all genes are present
                if not self.check_gene_presence(document_path):
                    diag_file.write(f'Sample: {sample_id}\t Issue: Not all genes present\n')
                
                #Checking if all phenotypes are plausible
                list_of_genes_to_check = self.check_phenotypes(document_path)
                if len(list_of_genes_to_check) != 0:
                    for gene in list_of_genes_to_check:
                        diag_file.write(f'Sample: {sample_id}\tIssue: {gene}\n')
        diag_file.close()


class InfosheetDiagnostics(Diagnostics):
    def infosheet_diagnostics(self):
        diag_file = open('Output/Diagnostics/infosheet_diagnostics.txt', 'w')
        diag_file.write('Infosheet diagnostics\n')
        for report in self.reports:
            if util.is_substring_present_in_substring(report, 'InfoSheet'):
                document_path = self.path + '\\' + report
                sample_id = document_path.split('_')[1]

                # Checking if all genes are present
                if not self.check_gene_presence(document_path):
                    diag_file.write(f'Sample: {sample_id}\t Issue: Not all genes present\n')

                # Checking if all phenotypes are plausible
                list_of_genes_to_check = self.check_phenotypes(document_path)
                if len(list_of_genes_to_check) != 0:
                    for gene in list_of_genes_to_check:
                        diag_file.write(f'Sample: {sample_id}\tIssue: {gene}\n')
        diag_file.close()