from timeit import default_timer as timer
import ELT
import Utilities as util
import pandas as pd
from os.path import join
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
from multiprocessing import Pool, cpu_count
from functools import partial
from docx2pdf import convert

# Multiprocessing functions
def generate_farmacogenetic_report(id, dataframe):
    farmaco = FarmacoGeneticReport(sample_id=id, dataframe=dataframe)
    farmaco.inleiding()
    farmaco.id_table()
    farmaco.inhoudsopgave()
    farmaco.table_heading()
    farmaco.uitslag_table()
    farmaco.verklaring_fenotype()
    farmaco.toelichting()
    farmaco.variaties_waarop_is_getest()
    farmaco.save()

def generate_infosheet(id, dataframe):
    infosheet = InfoSheet(sample_id=id, dataframe=dataframe)
    infosheet.standard_text()
    infosheet.table()
    infosheet.save()

def generate_nutrinomics_report(id, dataframe):
    nutrinomics = NutrinomicsReport(sample_id=id, dataframe=dataframe)
    nutrinomics.logo_titel_header()
    nutrinomics.table()
    nutrinomics.Toelichting()
    nutrinomics.save()

# Main functions
def phenotypes_import(phenotypes_rpt):
    pd.options.mode.chained_assignment = None  # default='warn'

    phenotypes_df = pd.read_csv(phenotypes_rpt, sep="@", header=None, engine="python")
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

    return phenotypes_df

def genotypes_import(genotypes_txt):
    print('genotype import [...]', end='\r')
    genotypes_df = pd.read_csv(genotypes_txt, sep="@", header=None, engine="python")
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

    return genotypes_df

def data_preparation(genotypes_df, phenotypes_df):
    data_preparation = ELT.DataPreparation(genotypes_df, phenotypes_df)
    data_preparation.merge_geno_and_phenotype_dataframes()
    data_preparation.determine_phenotype()
    data_preparation.move_MTHFR1298_and_CYP2C19()
    data_preparation.keep_only_batch_relevant_data()

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

    combined_changes = changes.CombinedChanges(complete_dataframe)
    util.execute_all_methods(combined_changes)
    complete_dataframe = combined_changes.dataframe
    util.store_dataframe(complete_dataframe, 'complete')
    print('Implementing NifGo changes DONE')

    return complete_dataframe

def handling_unknowns(complete_dataframe, corrected_unknowns_path):
    print('Handling unknowns [...]')
    handler = HandlingUnknowns(complete_dataframe, corrected_unknowns_path)
    handler.detect_unknowns()
    handler.correct_unknowns()
    complete_dataframe = handler.dataframe
    util.store_dataframe(complete_dataframe, 'complete')
    handler.detect_unknowns()
    print('Handling unknowns DONE')

    return complete_dataframe

def generating_pharmacogenetic(complete_dataframe):
    unique_sample_id_list = complete_dataframe['sample_id'].unique().tolist()
    print('Generating farmacogenetic reports [...]')
    timer_start = timer()
    partial_generate_farmacogenetic_report = partial(generate_farmacogenetic_report, dataframe=complete_dataframe)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_farmacogenetic_report, unique_sample_id_list)
    timer_end = timer()
    farmacogenetics_generation_time = timer_end - timer_start
    print('Generating farmacogenetic reports DONE')

    return farmacogenetics_generation_time

def generating_infosheet(complete_dataframe):
    unique_sample_id_list = complete_dataframe['sample_id'].unique().tolist()
    print('Generating info sheets [...]')
    timer_start = timer()
    partial_generate_infosheet = partial(generate_infosheet, dataframe=complete_dataframe)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_infosheet, unique_sample_id_list)
    timer_end = timer()
    infosheets_generation_time = timer_end - timer_start
    print('Generating info sheets [DONE]')

    return infosheets_generation_time

def generating_nutrinomics(complete_dataframe):
    unique_sample_id_list = complete_dataframe['sample_id'].unique().tolist()
    print('Generating nutrinomics reports [...]')
    timer_start = timer()
    partial_generate_nutrinomics_report = partial(generate_nutrinomics_report, dataframe=complete_dataframe)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_nutrinomics_report, unique_sample_id_list)
    timer_end = timer()
    nutrinomics_generation_time = timer_end - timer_start
    print('Generating nutrinomics reports [DONE]')

    return nutrinomics_generation_time

def enter_customer_data(filepath):
    print('Filling in customer data [...]')
    CustomerData(filepath).fill_customer_data()
    print('Filling in customer data [DONE]')

def export_to_pdf():
    print('Exporting to PDF [...]')
    reports = util.get_reports()
    try:
        convert('Output/Reports/', 'Output/Reports/PDF')
    except:
        pdf_reports = util.get_reports('Output\\Reports\\PDF')
        if len(pdf_reports) == len(reports):
            pass
        else:
            missed_conversions = []
            print('ERROR ENCOUNTERED\n{} out of {} reports converted.\nMissed conversions:')
            for pdf in pdf_reports:
                pdf_report = pdf.replace('pdf', 'docx')
                if pdf_report not in reports:
                    missed_conversions.append(pdf_report)
            for report in missed_conversions:
                print(report)
            return missed_conversions
    print('Exporting to PDF [DONE]')
    return None

def diagnostics(times, complete_dataframe):
    print('Generating diagnostic reports [...]')
    unique_sample_id_list = complete_dataframe['sample_id'].unique().tolist()
    (farmacogenetics_generation_time, infosheets_generation_time, nutrinomics_generation_time) = times
    generation_times = [farmacogenetics_generation_time, infosheets_generation_time, nutrinomics_generation_time]
    Diagnostics.GeneralDiagnostics().metadata(generation_times, unique_sample_id_list)
    Diagnostics.GeneralDiagnostics().sample_data(complete_dataframe)
    Diagnostics.PharmacoDiagnostics().pharmaco_reports_diagnostics()
    Diagnostics.InfosheetDiagnostics().infosheet_diagnostics()
    Diagnostics.NutrinomicsDiagnostics().nutrinomics_diagnostics()
    print('Generating diagnostic reports [DONE]')