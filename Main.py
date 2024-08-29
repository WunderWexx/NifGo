# Where everything comes together

# Could be rewritten to be clearer.

# imports
from timeit import default_timer as timer
import ELT
import Utilities as util
import pandas as pd
from os.path import join, abspath
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

def generate_medication_report(id, dataframe):
    medrep = MedicationReport(sample_id=id, dataframe=dataframe)
    medrep.medrep_intro_text()
    medrep.medrep_core_exec()
    medrep.save()

def convert_to_pdf(report):
    attempts = 5
    for attempt in range(attempts):
        try:
            basepath = 'Output\\Reports'
            docxpath = join(basepath, report)
            pdf_basepath = 'Output\\Reports\\PDF'
            pdfpath = join(pdf_basepath, report.replace('docx','pdf'))
            convert(docxpath, pdfpath)
            break
        except Exception as e:
            if attempt < 2:
                print(f"Attempt {attempt + 1} failed for {report}: {e}")
            else:
                print(f"{report} FAILED TO CONVERT WITH ERROR {e}")

if __name__ == "__main__":

    # settings
    pd.options.mode.chained_assignment = None  # default='warn'

    # Delete existing reports
    ask_delete_reports = sg.popup_yes_no("Wilt u de bestaande rapporten verwijderen?")
    if ask_delete_reports == 'Yes':
        util.empty_folder('Output/Reports')
        util.empty_folder('Output/Reports/PDF')

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

    #Handling unknowns
    print('Handling unknowns [...]')
    handler = HandlingUnknowns(complete_dataframe)
    handler.detect_unknowns()
    handler.correct_unknowns()
    complete_dataframe = handler.dataframe
    util.store_dataframe(complete_dataframe, 'complete')
    handler.detect_unknowns()
    print('Handling unknowns DONE')

    unique_sample_id_list = complete_dataframe['sample_id'].unique().tolist()

    # Farmacogenetic Reports generation
    print('Generating farmacogenetic reports [...]')
    timer_start = timer()
    partial_generate_farmacogenetic_report = partial(generate_farmacogenetic_report, dataframe=complete_dataframe)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_farmacogenetic_report, unique_sample_id_list)
    timer_end = timer()
    farmacogenetics_generation_time = timer_end - timer_start
    print('Generating farmacogenetic reports DONE')

    # Infosheet generation
    print('Generating info sheets [...]')
    timer_start = timer()
    partial_generate_infosheet = partial(generate_infosheet, dataframe=complete_dataframe)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_infosheet, unique_sample_id_list)
    timer_end = timer()
    infosheets_generation_time = timer_end - timer_start
    print('Generating info sheets [DONE]')

    # Nutrinomics Reports generation
    print('Generating nutrinomics reports [...]')
    timer_start = timer()
    partial_generate_nutrinomics_report = partial(generate_nutrinomics_report, dataframe=complete_dataframe)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_nutrinomics_report, unique_sample_id_list)
        # ValueError: Length of values (26) does not match length of index (23) betekent dat er genen missen uit het source bestand
    timer_end = timer()
    nutrinomics_generation_time = timer_end - timer_start
    print('Generating nutrinomics reports [DONE]')

    """
    # Medication report generation
    print('Generating medication reports [...]')
    timer_start = timer()
    partial_generate_medication_report = partial(generate_medication_report, dataframe=complete_dataframe)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_medication_report, unique_sample_id_list)
    timer_end = timer()
    medication_generation_time = timer_end - timer_start
    print('Generating medication reports [DONE]')
    """
    # Filling in customer data
    file_is_present = sg.popup_yes_no("Heeft u het bestand met de klantdata?")
    if file_is_present == 'Yes':
        print('Filling in customer data [...]')
        CustomerData().fill_customer_data()
        print('Filling in customer data [DONE]')

    # Export to PDF
    ask_pdf_generation = sg.popup_yes_no("Wilt u de PDF bestanden aanmaken?")
    if ask_pdf_generation == 'Yes':
        print('Exporting to PDF [...]')
        reports = util.get_reports()
        '''
        print(f'Generating {len(reports)} PDF\'s')
        with Pool(cpu_count()) as pool:
            pool.map(convert_to_pdf, reports)
        '''
        try:
            convert('Output/Reports/','Output/Reports/PDF')
        except:
            pdf_reports = util.get_reports('Output\\Reports\\PDF')
            if len(pdf_reports) == len(reports):
                pass
            else:
                missed_conversions = []
                print('ERROR ENCOUNTERED\n{} out of {} reports converted.\nMissed conversions:')
                for pdf in pdf_reports:
                    pdf_report = pdf.replace('pdf','docx')
                    if pdf_report not in reports:
                        missed_conversions.append(pdf_report)
                for report in missed_conversions:
                    print(report)
        print('Exporting to PDF [DONE]')

    # Diagnostics
    print('Generating diagnostic reports [...]')
    generation_times = [farmacogenetics_generation_time, infosheets_generation_time,
                            nutrinomics_generation_time] #, medication_generation_time
    Diagnostics.GeneralDiagnostics().metadata(generation_times, unique_sample_id_list)
    Diagnostics.GeneralDiagnostics().sample_data(complete_dataframe)
    Diagnostics.PharmacoDiagnostics().pharmaco_reports_diagnostics()
    Diagnostics.InfosheetDiagnostics().infosheet_diagnostics()
    Diagnostics.NutrinomicsDiagnostics().nutrinomics_diagnostics()
    print('Generating diagnostic reports [DONE]')

    # Open all Word files
    ask_open_reports = sg.popup_yes_no("Wilt u de gegenereerde rapporten openen?\nLET OP! Dit opent ALLE rapporten")
    if ask_open_reports == 'Yes':
        util.open_all_reports()

    print('\nPROGRAM EXECUTED SUCCESSFULLY')