# Where everything comes together

# Could be rewritten to be clearer.

# imports
from timeit import default_timer as timer
import ELT
import Utilities as util
import pandas as pd
from docx2pdf import convert
from os import listdir
from os.path import isfile, join
import PySimpleGUI as sg
import NifgoProprietaryChanges as changes
import Diagnostics
from FarmacogeneticReport import FarmacoGeneticReport
from info_sheet import InfoSheet
from NutrinomicsReport import NutrinomicsReport
from MedicationReport import MedicationReport
from Globals import ThermoFisher_determined_genes, probeset_id_dict
from HandlingUnknowns import HandlingUnknowns
from AddCustomerData import CustomerData

# settings
pd.options.mode.chained_assignment = None  # default='warn'

# Data preparation
phenotypes_df = ELT.Extract().phenotype_rpt()
phenotypes_df = ELT.Load().phenotype_rpt(phenotypes_df)
print('phenotype import DONE')
phenotype_transformation = ELT.Transform().phenotype_rpt(phenotypes_df)
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
genotypes_transformation.drop_columns_after_last_sample()
genotypes_transformation.drop_cel_call_code_suffix()
genotypes_transformation.unpivot_dataframe()
genotypes_transformation.reorder_and_rename_columns()
genotypes_transformation.add_gene_names()

genotypes_df = genotypes_transformation.dataframe
util.store_dataframe(genotypes_df, 'genotypes')
print('genotype transformation DONE')

data_preparation = ELT.DataPreparation(genotypes_df, phenotypes_df)
data_preparation.merge_geno_and_phenotype_dataframes()
data_preparation.determine_phenotype()

complete_dataframe = data_preparation.complete_dataframe
util.store_dataframe(complete_dataframe, 'complete')
print('complete dataframe creation DONE')

general_changes = changes.GeneralChanges(complete_dataframe)
util.execute_all_methods(general_changes)
complete_dataframe = general_changes.dataframe

gene_name_changes = changes.GeneNameChanges(complete_dataframe)
util.execute_all_methods(gene_name_changes)
complete_dataframe = gene_name_changes.dataframe

phenotype_changes = changes.PhenotypeChanges(complete_dataframe)
util.execute_all_methods(phenotype_changes)
complete_dataframe = phenotype_changes.dataframe

genotype_changes = changes.GenotypeChanges(complete_dataframe)
util.execute_all_methods(genotype_changes)

complete_dataframe = genotype_changes.dataframe
util.store_dataframe(complete_dataframe, 'complete')
print('implementing NifGo changes DONE')

#Handling unknowns
print('Handling unknowns [...]')
handler = HandlingUnknowns(complete_dataframe)
handler.detect_unkowns()
handler.correct_unknowns()
complete_dataframe = handler.dataframe
util.store_dataframe(complete_dataframe, 'complete')
handler.detect_unkowns()
print('Handling unknowns DONE')

unique_sample_id_list = complete_dataframe['sample_id'].unique().tolist()

# Farmacogenetic Reports generation
print('Generating farmacogenetic reports [...]')
timer_start = timer()
for id in unique_sample_id_list:
    farmaco = FarmacoGeneticReport(sample_id= id,
                                   dataframe= complete_dataframe)
    farmaco.inleiding()
    farmaco.id_table()
    farmaco.inhoudsopgave()
    farmaco.table_heading()
    farmaco.uitslag_table()
    farmaco.verklaring_fenotype()
    farmaco.toelichting()
    farmaco.variaties_waarop_is_getest()
    farmaco.save()
timer_end = timer()
farmacogenetics_generation_time = timer_end - timer_start
print('Generating farmacogenetic reports DONE')

# Infosheet generation
print('Generating info sheets [...]')
timer_start = timer()
for id in unique_sample_id_list:
    infosheet = InfoSheet(sample_id= id,
                          dataframe= complete_dataframe)
    infosheet.standard_text()
    infosheet.table()
    infosheet.save()
timer_end = timer()
infosheets_generation_time = timer_end - timer_start
print('Generating info sheets [DONE]')

# Nutrinomics Reports generation
print('Generating nutrinomics reports [...]')
timer_start = timer()
for id in unique_sample_id_list:
    nutrinomics = NutrinomicsReport(sample_id= id,
                                    dataframe= complete_dataframe)
    nutrinomics.logo_titel_header()
    nutrinomics.table()
    nutrinomics.Toelichting()
    nutrinomics.save()
timer_end = timer()
nutrinomics_generation_time = timer_end - timer_start
print('Generating nutrinomics reports [DONE]')

# Medication report generation
print('Generating medication reports [...]')
timer_start = timer()
for id in unique_sample_id_list:
    medrep = MedicationReport(sample_id= id,
                              dataframe= complete_dataframe)
    medrep.medrep_intro_text()
    medrep.medrep_core_exec()
    medrep.save()
timer_end = timer()
medication_generation_time = timer_end - timer_start
print('Generating medication reports [DONE]')

# Filling in customer data
CustomerData().execute()

# Export to PDF
ask_pdf_generation = sg.popup_yes_no("Wilt u de PDF bestanden aanmaken?\nLET OP! Dit kan enkele minuten duren.")
print('Exporting to PDF [...]')
basepath = 'Output\Reports'
reports = [file for file in listdir(basepath) if isfile(join(basepath, file))]
for report in reports:
    if report.split('_')[0] != 'MedicationReport':
        filepath = basepath + '\\' + report
        pdf_name = report.replace('docx','pdf')
        convert(filepath, output_path='Output\Reports\PDF')
print('Exporting to PDF [DONE]')

# Diagnostics
print('Generating diagnostic reports [...]')
generation_times = [farmacogenetics_generation_time, infosheets_generation_time,
                        nutrinomics_generation_time, medication_generation_time]
Diagnostics.GeneralDiagnostics().metadata(generation_times, unique_sample_id_list)
# Diagnostics.GeneralDiagnostics().sample_data() DOES NOT WORK YET
Diagnostics.PharmacoDiagnostics().pharmaco_reports_diagnostics()
Diagnostics.InfosheetDiagnostics().infosheet_diagnostics()
Diagnostics.NutrinomicsDiagnostics().nutrinomics_diagnostics()
print('Generating diagnostic reports [DONE]')