# This is where the pharmacist info sheet is generated

# Imports
from docx.shared import Pt, Cm
from WordDocument import WordEditing as wd
import ELT

class InfoSheet(wd):
    def __init__(self, sample_id, dataframe):
        super().__init__(sample_id, dataframe)
        self.pharmacy_data = ELT.Extract().pharmacydata()

    def standard_text(self):
        self.heading("Apotheker informatieblad", chosen_size=16, lined=True, colour=(0,0,0), is_bold=False)
        run = self.document.add_paragraph().add_run("Naam :\nGeboortedatum :")
        self.styled_run(run, font_size=12, is_bold=True, is_underlined=True)
        run = self.document.add_paragraph().add_run(
            "\nApothekers registreren in hun informatiesysteem de farmacogenetische resultaten van een DNA test. Doel is dat het informatiesysteem automatisch een melding geeft als er sprake is van een contra indicatie bij het klaarmaken van medicijnen."
            "\n\nNiet alle genen uit het rapport kunnen worden geregistreerd in het informatie systeem. Wel de belangrijkste (klinisch relevante) genen, die een rol spelen bij de meest voorgeschreven medicijnen."
            "\n\nOm deze registratie zo gemakkelijk mogelijk te maken is onderstaand overzicht opgesteld. U kunt dit uitprinten en aan uw apotheker en/of  huisarts geven.")
        self.styled_run(run)

    def infosheet_IA(self):
        """
        The infosheet Information Area (IA) contains/returns the dataframe with the information needed for the
        information sheet.
        First a subset of the complete dataframe is taken containing only the specified sample id, and the genes
        reported in the infosheet aka those relevant to GP's.
        Second the GP code and infosystem text are determined and added to the IA dataframe.
        :return: Dataframe ready to be transformed into the infosheet Word table.
        """

        infosheet_genes = [
            "COMT",
            "CYP1A2",
            "CYP2B6",
            "CYP2C9",
            "CYP2C19",
            "CYP2D6",
            "CYP3A4",
            "CYP3A5",
            "DPYD",
            "HLA-B*1502",
            "MTHFR677",
            "SLCO1B1",
            "TPMT",
            "UGT1A1",
            "VKORC1"
        ]
        df = self.dataframe[self.dataframe['sample_id'] == self.sample_id]
        df = df[df['gene'].isin(infosheet_genes)]
        df.drop(['sample_id'], axis='columns', inplace=True)
        df.rename(columns={'gene': 'Gen', 'phenotype': 'Fenotype/functie', 'genotype': 'Uitslag'}, inplace=True)

        pharmacy_data = self.pharmacy_data
        pharmacy_codes = []
        infosystem_texts = []
        for gen, phenotype, genotype in zip(df['Gen'], df['Fenotype/functie'], df['Uitslag']):
            pharmacy_data_view = pharmacy_data[pharmacy_data['Gen'] == gen]
            pharmacy_data_view = pharmacy_data_view[pharmacy_data_view['Fenotype/Functie'] == phenotype]
            if pharmacy_data_view.shape[0] != 1:
                pharmacy_data_view = pharmacy_data_view[pharmacy_data_view['Uitslag'].isin([genotype, 'Anders'])]
                if pharmacy_data_view.shape[0] != 1:
                    pharmacy_data_view = pharmacy_data_view[pharmacy_data_view['Uitslag'] == genotype]
            if pharmacy_data_view.shape[0] == 1:
                pharmacy_codes.append(pharmacy_data_view['code'].item())
                infosystem_texts.append(pharmacy_data_view['Systeemoutput'].item())
            else:
                pharmacy_codes.append('-')
                infosystem_texts.append('Is (nog) niet verwerkt in het infosysteem')

        df['Code'] = pharmacy_codes
        df['Infosysteem'] = infosystem_texts
        return df

    def table(self):
        """
                Creates a Word table from a dataframe
                :param self.dataframe: The dataframe to become a table
                :param: style: The style of the table, default is Table Grid.
                :return: A Word table in the specified document
                """
        df = self.infosheet_IA()

        # add a table to the end and create a reference variable
        # extra row is so we can add the header row
        t = self.document.add_table(df.shape[0] + 1, df.shape[1])
        t.style = "Table Grid"

        # add the header rows.
        for j in range(df.shape[-1]):
            header_cells = t.rows[0].cells
            paragraph = header_cells[j].paragraphs[0]
            run = paragraph.add_run(df.columns[j])
            run.bold = True
            run.font.name = 'Calibri'
            run.font.size = Pt(11)

        # add the rest of the data frame
        for i in range(df.shape[0]):
            for j in range(df.shape[-1]):
                normal_cells = t.rows[i + 1].cells
                paragraph = normal_cells[j].paragraphs[0]
                run = paragraph.add_run(str(df.values[i, j]))
                run.font.name = 'Calibri'
                run.font.size = Pt(11)

        """
        counter = 1
        
        for i in range(df.shape[0]):
            if util.common_data(list(df.iloc[i]), normal_phenotypes) == False:
                self.change_table_row(t.rows[counter], font_color="FF0000")
            counter += 1
        """

        normal_phenotypes = ["NM", "NF", "non-expressor", "negatief","non-expresser"]
        for phenotype, counter in zip(df['Fenotype/functie'], range(len(df))):
            if phenotype not in normal_phenotypes:
                self.change_table_row(t.rows[counter+1], font_color="FF0000") #The +1 is because of the header row

        t.allow_autofit = False
        width_dict = {0: 2.38, 1: 2.82, 2: 3.00, 3: 2.25, 4: 6.8}
        for i in range(len(width_dict)):
            for cell in t.columns[i].cells:
                cell.width = Cm(width_dict[i])

    def save(self):
        """
        Saves the document with a name based on the customer id and the type of document.
        :return:
        """
        document_name = 'InfoSheet' + "_" + self.sample_id + ".docx"
        self.document.save(f"Output\\Reports\\{document_name}")