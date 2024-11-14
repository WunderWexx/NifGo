# This is where the farmacogenetic report is generated

# Imports'
import Utilities as util
from docx.shared import Pt, RGBColor, Cm
from WordDocument import WordEditing as wd

class FarmacoGeneticReport(wd):
       def inleiding(self):
              """
              Generates block 1 of all standard text.
              :return:
              """
              self.document.add_picture("Input/Icons/NifGo_logo.png")
              self.heading("\nFarmacogenetisch Rapport")
              self.colour_bar()
              run = self.document.add_paragraph().add_run(
                     "Dit farmacogenetisch rapport geeft een analyse van het DNA en identificeert de relevante genetische variaties en hun effecten op de veiligheid en werkzaamheid van medicijnen. U bent getest op die genen, die de werkzaamheid van uw medicatie kunnen beïnvloeden. Het DNA is geïsoleerd uit speeksel.\n\n"
                     "Dit rapport mag niet worden gebruikt om medicatie te veranderen, zonder begeleiding van een arts of apotheker. Raadpleeg altijd de (huis)arts en/of apotheker en wijzig nooit zelf de voorgeschreven medicijnen.\n\n"
                     "NIFGO adviseert nadrukkelijk om de uitslag van het onderzoek te laten vastleggen in het medische dossier van de (huis)arts. Vraag ook de apotheker om deze gegevens te registreren in het informatiesysteem van de apotheek. Apothekers registreren deze 18 belangrijkste genen in hun informatiesysteem. Na registratie bent u er zeker van, dat de apotheker controleert of de voorgeschreven medicijnen wel passen bij de uitslag van dit onderzoek.\n\n"
                     "Het rapport is persoonlijk en is opgesteld op basis van de huidige kennis en stand van zaken. Daarbij wordt nadrukkelijk het voorbehoud gemaakt, dat het DNA-materiaal van de hier genoemde persoon is."
              )
              run.font.name = "Calibri"
              run.font.size = Pt(12)

       def id_table(self):
              """
              Generates the table containing the customer data.
              :return:
              """
              self.colour_bar()
              customer_table = self.document.add_table(rows=1, cols=6)  # style = "Table Grid"
              customerDatatypes = ["Naam", "Geb. datum", "Code"]
              for type, column in zip(customerDatatypes, range(0, 5, 2)):
                     paragraph = customer_table.cell(0, column).paragraphs[0]
                     run = paragraph.add_run(type)
                     run.bold = True
                     run.font.name = "Calibri"
                     run.font.size = Pt(12)
              paragraph = customer_table.cell(0, 5).paragraphs[0]
              run = paragraph.add_run(self.sample_id)
              run.font.name = "Calibri"
              run.font.size = Pt(12)
              customer_table.allow_autofit = False
              width_dict = {0: 1.30, 1: 6, 2: 2.5, 3: 2.5, 4: 1.25, 5: 2.78}
              for i in range(5):
                     for cell in customer_table.columns[i].cells:
                            cell.width = Cm(width_dict[i])
              self.colour_bar()

       def inhoudsopgave(self):
              """
              Maakt de inhoudsopgave
              :return:
              """
              self.heading("\nInhoudsopgave")
              paragraph = self.document.add_paragraph()
              run = paragraph.add_run("- Overzicht uitslag\n\n"
                                      "- Toelichting uitslag\n\n"
                                      "- Variaties waarop is getest\n\n"
                                      "- Bijlage nutrigenomics (indien aangevraagd)")
              run.font.name = 'Calibri'
              run.font.size = Pt(12)

       def table_heading(self):
              """
              :return: Standard text preceding the table of results from the farmacogenetic research.
              """
              self.document.add_page_break()
              self.heading("De uitslag van het farmacogenetische onderzoek:", lined=True)
              paragraph = self.document.add_paragraph()
              self.linepacing(paragraph, 0.75)
              run = paragraph.add_run(
                     "(rood: afwijkend van normaal gemiddelde fenotype/functie/acetylatie en expressie)")
              run.font.color.rgb = RGBColor(255, 0, 0)
              run.font.name = "Calibri"
              run.font.size = Pt(10)
              run.bold = True

       def uitslag_table(self):
              # Makes a sub dataframe containing only the genes to be reported in the farmacogenetic report
              report_genes = [
                     "CACNA1S",
                     "CFTR",
                     "COMT",
                     "CYP1A2",
                     "CYP2A6",
                     "CYP2B6",
                     "CYP2C8",
                     "CYP2C9",
                     "CYP2C19",
                     "CYP2D6",
                     "CYP2E1",
                     "CYP3A4",
                     "CYP3A5",
                     "CYP4F2",
                     "DPYD",
                     "F2",
                     "F5",
                     "G6PD",
                     "GSTP1",
                     "HLA-B*1502",
                     "IFNL3",
                     "MTHFR1298",
                     "MTHFR677",
                     "MTRNR1",
                     "NAT1",
                     "NAT2",
                     "RYR1",
                     "SLCO1B1",
                     "TPMT",
                     "UGT1A1",
                     "VKORC1",
                     'OPRM1'
              ]
              df = self.dataframe[self.dataframe['sample_id'] == self.sample_id]
              df = df[df['gene'].isin(report_genes)]
              df.drop(['sample_id'], axis= 'columns', inplace=True)
              df.rename(columns={'gene':'Gen', 'phenotype':'Fenotype/functie', 'genotype':'Uitslag'}, inplace=True)

              # Checks if a phenotype is normal for that gene. Is later used in the code to turn text in the table
              # red for non-normal phenotypes
              normal_phenotypes = ["NM", "NF", "RA", "negatief", "non-expressor"]
              pm_normal_genes = ["F2", "F5"]
              def pm_normal_check(location):
                     phenotype_PM_check = "PM" in list(df.iloc[location])
                     gene_check = util.common_data(list(df.iloc[location]), pm_normal_genes)
                     if phenotype_PM_check and gene_check:
                            return True
                     else:
                            return False

              # adds a table to the end and create a reference variable
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

              # adds the rest of the data frame
              for row in range(df.shape[0]):
                     normal_check = util.common_data(list(df.iloc[row]), normal_phenotypes)
                     for column in range(df.shape[-1]):
                            if normal_check or  pm_normal_check(row):
                                   normal_cells = t.rows[row + 1].cells
                                   paragraph = normal_cells[column].paragraphs[0]
                                   run = paragraph.add_run(str(df.values[row, column]))
                            else:
                                   normal_cells = t.rows[row + 1].cells
                                   paragraph = normal_cells[column].paragraphs[0]
                                   run = paragraph.add_run(str(df.values[row, column]))
                                   self.change_table_row(t.rows[row + 1], font_color="FF0000")
                            run.font.name = 'Calibri'
                            run.font.size = Pt(11)

       def verklaring_fenotype(self):
              self.heading("\nVerklaring aanduiding fenotype/functie", chosen_size=11, colour=(68, 84, 106),
                                lined=True)
              # Table of abrivations
              aanduidingTable = self.document.add_table(rows=4, cols=1, style="Table Grid")

              def make_run(text, make_bold=False):
                     global run
                     run = paragraph.add_run(text)
                     run.bold = make_bold
                     run.font.name = "Calibri"
                     run.font.size = Pt(10)

              def fill_cell_with_explanation():
                     for i in range(len(verklaring_text)):
                            if i % 2 == 0:
                                   make_run(verklaring_text[i], make_bold=True)
                            else:
                                   make_run(verklaring_text[i])

              verklaring_text = ["UM", ": (ultra-rapid) ultra snel metabolisme, ", "RM",
                                 ": (rapid) versneld metabolisme;\n", "NM", ": (normal) normaal metabolisme, ", "IM",
                                 ": (intermediate) verminderd metabolisme;\n", "PM",
                                 ": (poor) nauwelijks of geen metabolisme;"]
              paragraph = aanduidingTable.cell(0, 0).paragraphs[0]
              fill_cell_with_explanation()
              verklaring_text = ["VKORC1: NM", ": normale expressie, ", "IM", ": verminderde expressie, ", "UM",
                                 ": verhoogde expressie,", " PM", ": geen of nauwelijks expressie;"]
              paragraph = aanduidingTable.cell(2, 0).paragraphs[0]
              fill_cell_with_explanation()
              verklaring_text = ["Overige: AS:", " Activiteitsscore; ", "IF,NF,DF of PF",
                                 ": respectievelijk een verhoogde, normale, verminderde, of geen functie;"]
              paragraph = aanduidingTable.cell(3, 0).paragraphs[0]
              fill_cell_with_explanation()
              verklaring_text = ["Het *1-allel (wildtype):",
                                 " afwezigheid van een testresultaat voor alle geteste varianten voor dat gen. Dit resultaat sluit de aanwezigheid van mogelijke andere varianten niet uit."]
              paragraph = aanduidingTable.cell(4, 0).paragraphs[0]
              fill_cell_with_explanation()
              # More standard text
       def toelichting(self):
              betrekkingOpGenenDict = {
                     "ABCG2": "Het ABCG2-gen speelt een belangrijke rol in het transport van stoffen in en uit de cellen en heeft belangrijke implicaties voor de response op medicatie en ook detoxificatie van lichaamsvreemde stoffen. Variaties in dit gen kunnen leiden tot verschillen in de functie van dit transporteiwit , wat invloed kan hebben op de effectiviteit en bijwerkingen van bepaalde medicaties. ( w.o. losartan , chemotherapeutica en sommige statines )",
                     "COMT": "is betrokken bij het afbreken van Catecholamines, dit zijn “stress” hormonen, zoals Dopamine en Serotonine. COMT is betrokken bij de morfinebehoefte. Binnen een metanalyse is er ook een associatie gevonden bij atypische antipsychotica. Variaties kunnen leiden tot een verhoogde gevoeligheid voor Methylgroepen.",
                     "CYP1A2": "speelt o.a. een rol bij afbraak van antidepressiva en van Clozapine. CYP1A2 wordt extra geactiveerd door roken en het eten van koolsoorten en geroosterd vlees. Insuline en Omeprazol activeren CYP1A2 extra. Fluvoxamine en Ciprofloxacine, remmen daarentegen de activiteit van CYP1A2. Dat geldt ook voor Bergamotine en Naringenine. Variaties van het CYP1A2 gen beïnvloeden de induceerbaarheid. Niet genetische factoren zijn ook van invloed op de activiteit van CYP1A2. Magnesium en vitamine B5 ondersteunen de activiteit van CYP1A2.",
                     "CYP2B6": "is betrokken bij de omzetting van veel medicijnen. Vooral belangrijk bij antivirale middelen (Efavirenz en Nevirapine), antidepressiva (Bupropion) en pijnstillers (Ketamine en Ifosfamide). Fluxetine en Fluvoxamine worden beschouwd als CYP2B6 remmers. ",
                     "CYP2C9": "bepaalt o.a. de gevoeligheid voor antistolling, zoals o.a. acenocoumarol en het anti-epilecticum Fenytoïne. Knoflook, kurkuma, sesam, Ginkgo biloba, Boswellia, kaneel en kruidnagel remmen de activiteit van CYP2C9. Geoxideerd linolzuur versterkt de activiteit van CYP2C9. Een verlaagd metabolisme kan de concentratie van de werkzame stof verhogen en daardoor oorzaak zijn van bijwerkingen.",
                     "CYP2C19": "is belangrijk bij antistollingsmiddelen, antidepressiva en maagzuurbeschermers. Kurkuma, sesam, St. janskruid, Ginseng en Boswellia-extract remmen de werking van CYP2C19.",
                     "CYP2D6": "is betrokken bij ruim 25% van de voorgeschreven medicijnen, zoals. Metoprolol, Codeïne, Oxycodon, Tramadol, Amitriptyline, Clomipramine, Doxepine, Imipramine, Nortriptyline, Paroxetine, Venlafaxine, Haloperidol, en Risperidon. Voeding(supplementen Cat’sClaw, Kamille, Gember, Gotu Kola, Noni sap, Oregano, Salie en Thym remmen de werking van CYP2D6. De activiteit van CYP2D6 is sterk afhankelijk van gen-duplicatie.",
                     "CYP3A4 ": "is betrokken bij ruim 50% van de voorgeschreven medicijnen. Niet genetisch factoren spelen echter ook een rol. St. Janskruid versterkt de activiteit van CYP3A4. Ginseng, kaneel en vooral grapefruitsap remmen de activiteit van CYP3A4. ",
                     "CYP3A5": "is belangrijk als immuunuppressiva worden voorgeschreven. CYP3A5 is bij de westerse bevolking niet actief.",
                     "DYPD": "Capecitabine is een pro-drug, dat omgezet wordt door DPYD in Fluorouracil en Dihydrofluorouracil. Een lage activiteit van DPYD geeft risico op verhoogde intracellulaire giftige concentraties. Hierdoor neemt het risico op bijwerkingen, zoals Neutropenie, Trombopenie en Hand-foot-syndroom toe.",
                     "G6PD": "speelt een belangrijke rol in de bescherming van rode bloedcellen tegen schade door vrije radicalen (anti-oxidatieve werking). G6PD-deficiëntie is erfelijk. Bij mensen met te weinig G6PD (deficiëntie) verliest de rode bloedcel zijn structuur en functie, waardoor de cellen verhoogd gevoelig worden voor oxidatieve schade. De rode bloedcellen worden versneld afgebroken (bloedarmoede). Vaak zijn er geen symptomen; Bacteriele- en virale infecties maar ook sommige antibiotica of medicijnen tegen malaria kunnen G6Pd activeren. ",
                     "HLA-B*1502": "HLA-genen beïnvloeden de werking van het immuunsysteem. Ze ondersteunen het immuunsysteem om lichaamsvreemde componenten, (bacteriën en virussen) te herkennen en erop te reageren. Bij testen wordt gekeken naar de aanwezigheid van de variatie (positief voor HLA-B*1502.) Bij positiviteit wordt gebruik van Carbamazepine afgeraden om het risico op SJS/TEN te vermijden.",
                     "MTHFR677": "is betrokken bij het foliumzuurmetabolisme. Methotrexaat wordt in het lichaam omgezet in gepolyglutamineerd Methotrexaat. Gepolyglutamineerd methotrexaat remt dihydrofolaatreductase, dat deel uitmaakt van de foliumzuurcyclus. Er zijn 2 variaties in het MTHFR gen onderzocht, die de activiteit van MTHFR beïnvloeden. Positie 1298 en positie 677. Magnesium, zink en B vitamines ondersteunen de activiteit van MTHFR.",
                     "NUDT15": "Dit enzym heeft te maken met de verwerking van thiopurines ( behandeling van auto immuun ziekten en sommige kankersoorten ) de effectiviteit en bijwerkingen van thiopurines kunnen variëren op basis van genetische factoren w.o. sommige  NUDT15-gen mutaties.",
                     "SLCO1B1": "is betrokken bij het transport van medicijnen. Vooral voor statines, maar ook voor rode gistrijst is SLCO1B1 belangrijk. Variaties in het SLCO1B1 gen worden sterk geassocieerd met statine gerelateerde myopathie.",
                     "TPMT": "is betrokken bij omzetting van Thiopurines (zoals Azathioprine, 6-Mercaptopurine en Thioguanine). Dit zijn inactieve pro-drugs, die in het lichaam omgezet worden in de actieve metabolieten: de Thioguaninenucleotiden.",
                     "UGT1A1 ": "belangrijk voor de glucuronidering van medicijnen. Circa 15% van de westerse bevolking heeft een hogere kans op Neutropenie, bij standaarddosering Irinotecan. Lage UGT1A1 activiteit wordt in verband gebracht met de ziekte van Gilbert. Een verlaagde activiteit van UGT1A1 zorgt dus voor een hogere concentratie van “afvalstoffen”. Magnesium en B vitamines ondersteunen de activiteit van UGT1A1.",
                     "VKORC1": "zorgt voor anti-bloedstolling. Het enzym regenereert inactief vitamine K tot de actieve vorm. Cumarines remmen dit proces en zorgen op deze wijze voor een verminderde stollingsactiviteit. Variaties in het VKORC1-gen kunnen het effect van Cumarines verhogen en geven daardoor risico op bloedingen.  Medicijnen, die een rol spelen bij bloedstolling zijn Acetylsalicylzuur, Fenprocoumon, Ascal en Acenocoumarol."
              }
              
              self.document.add_page_break()
              self.heading("Toelichting\n", lined=True)
              run = self.document.add_paragraph().add_run(
                     "Voor veel genen worden de genetische variaties aangegeven met ster en nummer (bijv. *1/*1). De meeste medicijnen worden in het lichaam door enzymen  (eiwitten) afgebroken. Dit proces wordt stofwisseling (metabolisme) genoemd. De voorspelde activiteit van een enzym (fenotype) is genetisch bepaald. CYP3A5 bijvoorbeeld, is een enzym, dat bij de westerse bevolking, in het algemeen geen activiteit heeft. De meeste Nederlanders zullen dus PM als fenotype hebben. De standaard dosering is hier al op afgestemd. Dus voor CYP3A5 is alleen een aanpassing van de dosering nodig, als het fenotype NM, IM, RM of UM is. Sommige genen zorgen voor transport van een medicijn door het lichaam. SLCO1B1 codeert voor een transporteiwit. Variaties kunnen de functie van het gen beïnvloeden. Dit wordt aangegeven met IF, NF, DF of PF (respectievelijk een verhoogde, normale , verminderde of geen functie .CYP1A2 is bij de westerse bevolking zeer actief (*1F/*1F) en wordt aangegeven als normaal metabolisme met een verhoogde induceerbaarheid: NM, (apothekercode 560). Verminderde induceerbaarheid wordt aangegeven met IM (apothekercode 555) en nauwelijks of geen induceerbaarheid met PM (apothekercode 556)."
              )
              run.font.size = Pt(12)
              run.font.name = 'Calibri'
              self.heading("De testuitslagen op pagina 2 hebben betrekking op de volgende genen:", lined=True)
              # Table of gene explanation
              for i, j in zip(["CYP2C8", "NAT1", "OPRM1"], ["CACNA1S", "CYP2C9", "NAT2"]):
                     betrekkingTable = self.document.add_table(rows=0, cols=2, style="Table Grid")
                     betrekkingTable.allow_autofit = False
                     row = 0
                     start_check = False
                     for key, value in betrekkingOpGenenDict.items():
                            if key == j:
                                   start_check = True
                            if start_check:
                                   pass
                            else:
                                   continue
                            if key == i:
                                   betrekkingTable.add_row()
                                   paragraph = betrekkingTable.cell(row, 0).paragraphs[0]
                                   run = paragraph.add_run(key)
                                   run.font.size = Pt(10)
                                   run.font.name = 'Calibri'
                                   run.bold = True
                                   paragraph = betrekkingTable.cell(row, 1).paragraphs[0]
                                   run = paragraph.add_run(value)
                                   run.font.size = Pt(10)
                                   run.font.name = 'Calibri'
                                   row += 1
                                   for cell in betrekkingTable.columns[0].cells:
                                          cell.width = Cm(2.44)
                                   for cell in betrekkingTable.columns[1].cells:
                                          cell.width = Cm(15.53)
                                   self.document.add_page_break()
                                   break
                            else:
                                   betrekkingTable.add_row()
                                   paragraph = betrekkingTable.cell(row, 0).paragraphs[0]
                                   run = paragraph.add_run(key)
                                   run.font.size = Pt(10)
                                   run.font.name = 'Calibri'
                                   run.bold = True
                                   paragraph = betrekkingTable.cell(row, 1).paragraphs[0]
                                   run = paragraph.add_run(value)
                                   run.font.size = Pt(10)
                                   run.font.name = 'Calibri'
                                   row += 1
       def variaties_waarop_is_getest(self):
              getesteVariatiesDict = {
                     "ABCG2": "rs2231142",
                     "COMT": "Val en Met (rs4680)",
                     "CYP1A2": "*1A,*1C,*1F,*1K,*1L,*2,*3,*4,*5,*6,*7,*8,*9,*9+1F,*10,*11,*12,*13,*13+1F,*14,*15,*16,*17,*18,*19,*20,*21",
                     "CYP2B6": "*1,*2,*3,*4,*5,*6,*7,*8,*11,*12,*13,*14,*6+*14,*15,*17,*18,*18.002,*19,*20,*21,*22,*24,*25,*26,*27,*28,*35,*36,*37,*38,*45,*6+*45",
                     "CYP2C9": "*1,*2,*3,*4,*5,*6,*8,*8.005,*9,*10,*11,*12,*13,*14,*15,*16,*17,*18,*19,*20,*21,*23,*24,*25,*28,*29,*30,*31,*32,*34,*36,*2+36,*38,*39,*40,*42,*43,*44,*45,*46,*47,*48,*49,*50,*51,*52,*53,*54,*55,*56,*57,*58",
                     "CYP2C19": "*1,*2,*3,*4.001,*4.002,*5,*6,*7,*8,*9,*10,*12,*13,*14,*15,*16,*17,*18,*19,*22,*23,*25,*26,*28,*34,*35",
                     "CYP2D6": "*1,*2,*3.001,*3.002,*4,*4.009,*4.010,*4.021,*6,*7,*8,*9,*10,*10+R26H,*11,*14,*15,*17,*18,*19,*19.001,*20,*22,*23,*25,*28,*29,*31,*33,*34,*35,*35+R365H,*37,*38,*40,*41,*42,*43,*44,*45,*46,*47,*48,*49,*51,*53,*54,*55,*56.001,*56.002,*62,*69,*70,*71,*73,*75,*82,*84,*86,*88,*95,*100,*102,*103,*107,*109,*114,*117,*121,*124,*139,*142,*146,*154,*164,*171,*5",
                     "CYP3A4": "*1,*2,*3,*4,*5,*6,*7,*8,*9,*10,*11,*12,*13,*14,*15,*16,*17,*18,*19,*20,*22,*23,*26,*37,*38",
                     "CYP3A5": "*1,*3,*6,*7,*8",
                     "DPYD": "c.=,c.61C>T,c.295_298delTCAT,c.557A>G,c.703C>T,c.1129-5923C>G,HapB3,c.1156G>T,c.1679T>G,c.1898delC,c.1905+1G>A,c.2846A>T,c.2983G>T",
                     "G6PD": "B,A,Null",
                     "HLA-B*1502": "*1502",
                     "MTHFR677": "rs1801133",
                     "NUDT15": "*1,*3,*4,*5,*13,*14,*15,*18",
                     "SLCO1B1": "*1,*5",
                     "TPMT": "*1,*2,*3A,*3B,*3C,*3D,*4,*5,*6,*7,*8,*9,*10,*11,*12,*13,*14,*15,*16,*17,*18,*19,*20,*21,*23,*24,*25,*26,*27,*28,*29,*30,*31,*33,*34,*35,*36,*37,*38,*42",
                     "UGT1A1": "*1,*60,*28+60+80+93,*28+60+80,*36+60,*6,*60+80,*27,*27+28+60+80+93,*27+28+60+80,*28",
                     "VKORC1": "*2"
              }

              self.heading("Variaties waarop is getest", lined=True)
              testvariaties_table = self.document.add_table(rows=len(getesteVariatiesDict) + 1, cols=2,
                                                            style="Table Grid")
              self.styled_cell_text(testvariaties_table.cell(0, 0), "Gen", make_bold=True, set_linespacing=True)
              self.styled_cell_text(testvariaties_table.cell(0, 1), "Variaties", make_bold=True, set_linespacing=True)
              for i in range(2):
                     if i == 0:
                            for j, k in zip(range(len(getesteVariatiesDict)), getesteVariatiesDict.keys()):
                                   self.styled_cell_text(testvariaties_table.cell(j + 1, i), text=k,
                                                         set_linespacing=True)
                     else:
                            for j, k in zip(range(len(getesteVariatiesDict)), getesteVariatiesDict.values()):
                                   self.styled_cell_text(testvariaties_table.cell(j + 1, i), text=k,
                                                         set_linespacing=True)
              testvariaties_table.allow_autofit = False
              for cell in testvariaties_table.columns[0].cells:
                     cell.width = Cm(3.19)
              for cell in testvariaties_table.columns[1].cells:
                     cell.width = Cm(14.78)

       def save(self):
              """
              Saves the document with a name based on the customer id and the type of document.
              :return:
              """
              document_name = 'FarmacogeneticReport' + "_" + self.sample_id + ".docx"
              self.document.save(f"Output\\Reports\\{document_name}")