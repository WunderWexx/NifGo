from docx import Document
import Utilities as util
from pathlib import Path

class nutrigenomics_report:
    def __init__(self, sample_id, dataframe):
        self.sample_id = sample_id
        self.nutri_df = dataframe[dataframe['sample_id'] == sample_id]

    def report_generation(self):
        # Load the Word document
        doc = Document('Input/Templates/Nutrigenomics-2024-12.docx')

        #Fill customer data table with sample code
        sample_code_cell = doc.tables[0].rows[0].cells[5]
        util.change_table_cell(sample_code_cell, bold=True, change_text=f'{self.sample_id}', font_size=10)

        #Fill results table 1
        table1 = doc.tables[1]
        for row in table1.rows[1:]:
            gene = row.cells[0].paragraphs[0].text
            cell = row.cells[2]
            result = self.nutri_df.loc[self.nutri_df['gene'] == gene, 'genotype'].values
            result = result[0] if result.size > 0 else ''
            util.change_table_cell(cell, bold=True, change_text=f' {result}', font_size=9)

        # Fill results table 2
        table1 = doc.tables[2]
        for row in table1.rows[1:]:
            gene = row.cells[0].paragraphs[0].text
            cell = row.cells[2]
            result = self.nutri_df.loc[self.nutri_df['gene'] == gene, 'genotype'].values
            result = result[0] if result.size > 0 else ''
            util.change_table_cell(cell, bold=True, change_text=f' {result}', font_size=9)

        #Save the document
        document_name = 'NutrigenomicsReport' + "_" + self.sample_id + ".docx"
        path = Path("Output/Test/")
        path.mkdir(parents=True, exist_ok=True)
        doc.save(f"Output\\Test\\{document_name}")