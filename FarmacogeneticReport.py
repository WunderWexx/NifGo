# This is where the farmacogenetic report is generated

# Imports'
import Utilities as util
from docx.shared import Pt, RGBColor, Cm
from datetime import date
from WordDocument import WordEditing as wd

class FarmacoGeneticReport(wd):
       def inleiding(self):
              """
              Generates block 1 of all standard text.
              :return:
              """
              self.document.add_picture("Input/Icons/NifGo_logo.png")
              self.heading("\nFarmacogenetisch Rapport {}".format(date.today()))
              self.colour_bar()
              run = self.document.add_paragraph().add_run(
                     "Dit farmacogenetisch rapport geeft een analyse van het DNA en identificeert de relevante genetische variaties en hun effecten op de veiligheid en werkzaamheid van medicijnen. U bent getest op die genen, die de werkzaamheid van uw medicatie kunnen beïnvloeden. DNA is geïsoleerd uit speeksel.\n\n"
                     " Dit rapport mag niet worden gebruikt om medicatie te veranderen, zonder begeleiding van een arts of apotheker. Raadpleeg altijd de (huis)arts en wijzig niet zelf de voorgeschreven medicijnen.\n\n"
                     "NIFGO adviseert de uitslag van het onderzoek te laten vastleggen in het medische dossier van de (huis)arts. Vraag ook de apotheker om deze gegevens te registreren in het informatiesysteem van de apotheek. Apothekers registreren de 15 belangrijkste genen in hun informatiesysteem. Na registratie bent u er zeker van, dat de apotheker controleert of de voorgeschreven medicijnen wel passen bij de uitslag van dit onderzoek.\n\n"
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
              width_dict = {0: 2.63, 1: 3.39, 2: 3.92, 3: 2.5, 4: 2.25, 5: 2.78}
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
              run = paragraph.add_run("- overzicht uitslag\n\n"
                                      "- toelichting uitslag\n\n"
                                      "- variaties waarop is getest\n\n"
                                      "- bijlage medicatiematch\n\n"
                                      "- bijlage nutrigenomics (indien aangevraagd)")
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
                     "VKORC1"
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
              aanduidingTable = self.document.add_table(rows=5, cols=1, style="Table Grid")

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
              verklaring_text = ["NAT1 en 2: RA", ": (rapid) snelle-,   ", "NA", ": (normal) normale-,  ", "IA",
                                 " (intermediate) verminderde-, en ", "SA:", " (slow) langzame acetyleerder;"]
              paragraph = aanduidingTable.cell(1, 0).paragraphs[0]
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
                     "CACNA1S": "codeert voor de structuur en functie van calciumkanalen, die worden aangetroffen in de skeletspieren. Deze kanalen activeren de werking van RYR1-kanalen. Variaties in het CACNA1S-gen kunnen een verhoogd risico geven op maligne hyperthermie, een ernstige reactie op bepaalde anesthetica, die vaak worden gebruikt tijdens operaties en andere invasieve procedures.",
                     "CFTR": "codeert voor een ionkanaalenzym van de ABC-transportenzymen. Variaties van het CFTR-gen kunnen leiden tot ontregeling van het epitheelvochttransport in de longen, pancreas en andere organen. Dit geeft risico op cystische fibrose.",
                     "COMT": "is betrokken bij het afbreken van Catecholamines, dit zijn “stress” hormonen, zoals Dopamine en Serotonine. COMT is betrokken bij de morfinebehoefte. Binnen een metanalyse is er ook een associatie gevonden bij atypische antipsychotica. Variaties kunnen leiden tot een verhoogde gevoeligheid voor Methylgroepen.",
                     "CYP1A2": "speelt o.a. een rol bij afbraak van antidepressiva en van Clozapine. CYP1A2 wordt extra geactiveerd door roken en het eten van koolsoorten en geroosterd vlees. Insuline en Omeprazol activeren CYP1A2 extra. Fluvoxamine en Ciprofloxacine, remmen daarentegen de activiteit van CYP1A2. Dat geldt ook voor Bergamotine en Naringenine. Variaties van het CYP1A2 gen beïnvloeden de induceerbaarheid. Niet genetische factoren zijn ook van invloed op de activiteit van CYP1A2. Magnesium en vitamine B5 ondersteunen de activiteit van CYP1A2.",
                     "CYP2A6": "is verantwoordelijk voor de oxidatie van nicotine en cotinine. Expressie en activiteit van CYP2A6 wordt ook beïnvloed door niet-genetische factoren. Variaties van het CYP2A6 gen zijn van invloed op de werking van Tegafur, Letrozol, Efavirenz, Valproïnezuur, Pilocarpine, Artemisinine, Artesunaat, Cafeïne en Tyrosol en een aantal coumarine-achtige alkaloïden.Pompelmoes en grapefruit remmen de activiteit van CYP2A6.",
                     "CYP2B6": "is betrokken bij de omzetting van veel medicijnen. Vooral belangrijk bij antivirale middelen (Efavirenz en Nevirapine), antidepressiva (Bupropion) en pijnstillers (Ketamine en Ifosfamide). Fluxetine en Fluvoxamine worden beschouwd als CYP2B6 remmers. ",
                     "CYP2C8": "is een belangrijk leverenzym betrokken bij metabolisme van een aantal medicijnen bij behandeling van o.a. kanker en diabetes. CYP2C8 is direct betrokken bij metabolisme van o.a. Ibuprofen. CYP2C8 heeft een indirecte rol bij metabolisme van o.a. Diclofenac. De meest voorkomende variaties, die leiden tot een verlaagd metabolisme  zijn *2 en *3.",
                     "CYP2C9": "bepaalt o.a. de gevoeligheid voor antistolling, zoals o.a. acenocoumarol en het anti-epilecticum Fenytoïne. Knoflook, kurkuma, sesam, Ginkgo biloba, Boswellia, kaneel en kruidnagel remmen de activiteit van CYP2C9. Geoxideerd linolzuur versterkt de activiteit van CYP2C9. Een verlaagd metabolisme kan de concentratie van de werkzame stof verhogen en daardoor oorzaak zijn van bijwerkingen.",
                     "CYP2C19": "is belangrijk bij antistollingsmiddelen, antidepressiva en maagzuurbeschermers. Kurkuma, sesam, St. janskruid, Ginseng en Boswellia-extract remmen de werking van CYP2C19.",
                     "CYP2D6": "is betrokken bij ruim 25% van de voorgeschreven medicijnen, zoals. Metoprolol, Codeïne, Oxycodon, Tramadol, Amitriptyline, Clomipramine, Doxepine, Imipramine, Nortriptyline, Paroxetine, Venlafaxine, Haloperidol, en Risperidon. Voeding(supplementen Cat’sClaw, Kamille, Gember, Gotu Kola, Noni sap, Oregano, Salie en Thym remmen de werking van CYP2D6. De activiteit van CYP2D6 is sterk afhankelijk van gen-duplicatie.",
                     "CYP2E1": "de activiteit van CYP2E1 wordt gestimuleerd door alcohol, roken en de medicijnen Isoniazide en Isopropanol. Daarnaast speelt CYP2E1 een rol bij anesthesie, alcoholconsumptie, diabetes en obesitas. Transvetzuren en geoxideerde vetzuren hebben een negatief effect op de activiteit van CYP2E1. CYP2E1 -PM is een risicofactor voor vervetting van de lever. ",
                     "CYP3A4 ": "is betrokken bij ruim 50% van de voorgeschreven medicijnen. Niet genetisch factoren spelen echter ook een rol. St. Janskruid versterkt de activiteit van CYP3A4. Ginseng, kaneel en vooral grapefruitsap remmen de activiteit van CYP3A4. ",
                     "CYP3A5": "is belangrijk als immuunuppressiva worden voorgeschreven. CYP3A5 is bij de westerse bevolking niet actief.",
                     "CYP4F2": "is betrokken bij het metabolisme van vetzuren en vitamines (E en K). Variaties in het CYP4F2-gen zijn van belang voor het bepalen van de dosering van vitamine K-antagonisten zoals Warfarine, Cumarine en Acenocoumarol. In die zin is er een relatie met de activiteit van VKORC1.",
                     "DYPD ": "Capecitabine is een pro-drug, dat omgezet wordt door DPYD in Fluorouracil en Dihydrofluorouracil. Een lage activiteit van DPYD geeft risico op verhoogde intracellulaire giftige concentraties. Hierdoor neemt het risico op bijwerkingen, zoals Neutropenie, Trombopenie en Hand-foot-syndroom toe.",
                     "F2": "codeert voor Prothrombine, dat belangrijk is voor de bloedstolling. Onder normale omstandigheden is F2 niet actief (PM). F2 wordt pas actief, wanneer en sprake is van een bloeding. F2 zal dan bijdragen aan de stolling. Variatie in F2 geeft risico op een constante activiteit van het gen, die vervolgens kan leiden tot vorming van onnodig bloedstolsels.",
                     "F5": "is ook belangrijk voor de bloedstolling. F5 speelt een rol bij de vorming van Thrombine en Fibrine bij de vorming van een bloedstolsel. Factor 5 dient geïnactiveerd (niet actief) te zijn. Een Factor 5 variatie heeft een zwakke antistollingsreactie op geactiveerd proteïne C als effect. Hierdoor is er kans op een verhoogd risico op veneuze trombose.",
                     "G6PD": "speelt een belangrijke rol in de bescherming van rode bloedcellen tegen schade door vrije radicalen (anti-oxidatieve werking). G6PD-deficiëntie is erfelijk. Bij mensen met te weinig G6PD (deficiëntie) verliest de rode bloedcel zijn structuur en functie, waardoor de cellen verhoogd gevoelig worden voor oxidatieve schade. De rode bloedcellen worden versneld afgebroken (bloedarmoede). Vaak zijn er geen symptomen; Bacteriele- en virale infecties maar ook sommige antibiotica of medicijnen tegen malaria kunnen G6Pd activeren. ",
                     "GSTP1": "codeert voor actieve, functioneel verschillende GSTP1-varianteiwitten en speelt een belangrijke rol in het ontgiftings- en antioxidantensysteem. GSTP1-methylering is in veel onderzoekspapers genoemd als een epigenetische marker voor vroege diagnose van prostaatkanker.",
                     "IFNL3": "of IL28B codeert voor Interferon lambda 3, een enzym, dat betrokken is bij immuunreacties, bijvoorbeeld veroorzaakt door virale infecties. Sommige variaties voorspellen de werkzaamheid van hepatitis C-virus (HCV) -therapieën met bepaalde medicijncombinaties, zoals Telaprevir, Peginterferon alfa2a en Ribavirin.",
                     "MTHFR": "is betrokken bij het foliumzuurmetabolisme. Methotrexaat wordt in het lichaam omgezet in gepolyglutamineerd Methotrexaat. Gepolyglutamineerd methotrexaat remt dihydrofolaatreductase, dat deel uitmaakt van de foliumzuurcyclus. Er zijn 2 variaties in het MTHFR gen onderzocht, die de activiteit van MTHFR beïnvloeden. Positie 1298 en positie 677. Magnesium, zink en B vitamines ondersteunen de activiteit van MTHFR.",
                     "MTRNR1": "codeert voor een enzym, dat de gevoeligheid voor insuline reguleert. MTRNR1 is ook belangrijk voor evenwichtige regulering van andere variabelen, als vochtbalans, concentraties van natrium, kalium en calcium en de bloedsuikerspiegel.",
                     "NAT1": "belangrijk voor de koppelingsreactie tussen lichaamseigen en lichaamsvreemde stoffen zijn de N-acetyltransferases 1 en 2 (NAT1 en NAT2), die verscheidene geneesmiddelen omzetten door aan een aminegroep een acetylgroep te binden. Bij de N-Acetyl Transferase NAT-1 onderscheiden we op gen niveau snelle (rapid: R) en trage (Slow: S) allelen. ",
                     "NAT2": "Bij de N-Acetyl Transferase 2 (NAT-2) onderscheiden we op gen niveau snelle (rapid: R) en trage (Slow: S) allelen. Snelle allelen zijn: *4, *11, *12 en *13. Trage allelen zijn: *5, *6, *7 en *14. Het percentage trage acetyleerders onder de westerse bevolking is  circa 60% en onder de Afrikaanse en Aziatische bevolking circa 45%. Aanwezigheid van een of twee trage allelen geeft een verhoogde kans op levertoxiciteit bij gebruik van o.a. Isoniazide en Hydralazine.",
                     "RYR1": "RYR1 is een enzym dat voornamelijk in skeletspieren wordt aangetroffen en is van invloed op de spierontwikkeling. Varianten in het RYR1-gen zijn geassocieerd met vatbaarheid voor maligne hyperthermie.",
                     "SLCO1B1": "is betrokken bij het transport van medicijnen. Vooral voor statines, maar ook voor rode gistrijst is SLCO1B1 belangrijk. Variaties in het SLCO1B1 gen worden sterk geassocieerd met statine gerelateerde myopathie.",
                     "TPMT": "is betrokken bij omzetting van Thiopurines (zoals Azathioprine, 6-Mercaptopurine en Thioguanine). Dit zijn inactieve pro-drugs, die in het lichaam omgezet worden in de actieve metabolieten: de Thioguaninenucleotiden.",
                     "UGT1A1 ": "belangrijk voor de glucuronidering van medicijnen. Circa 15% van de westerse bevolking heeft een hogere kans op Neutropenie, bij standaarddosering Irinotecan. Lage UGT1A1 activiteit wordt in verband gebracht met de ziekte van Gilbert. Een verlaagde activiteit van UGT1A1 zorgt dus voor een hogere concentratie van “afvalstoffen”. Magnesium en B vitamines ondersteunen de activiteit van UGT1A1.",
                     "VKORC1": "zorgt voor anti-bloedstolling. Het enzym regenereert inactief vitamine K tot de actieve vorm. Cumarines remmen dit proces en zorgen op deze wijze voor een verminderde stollingsactiviteit. Variaties in het VKORC1-gen kunnen het effect van Cumarines verhogen en geven daardoor risico op bloedingen.  Medicijnen, die een rol spelen bij bloedstolling zijn Acetylsalicylzuur, Fenprocoumon, Ascal en Acenocoumarol.",
                     "HLA-B*1502": "HLA-genen beïnvloeden de werking van het immuunsysteem. Ze ondersteunen het immuunsysteem om lichaamsvreemde componenten, (bacteriën en virussen) te herkennen en erop te reageren. Bij testen wordt gekeken naar de aanwezigheid van de variatie (positief voor HLA-B*1502.) Bij positiviteit wordt gebruik van Carbamazepine afgeraden om het risico op SJS/TEN te vermijden.",
                     "OPRM1": "Dit gen is betrokken bij medicijnen voor pijnbestrijding. Variaties in dit gen hebben effect op effectiviteit van deze medicijnen.",
              }
              
              self.document.add_page_break()
              self.heading("Toelichting\n", lined=True)
              run = self.document.add_paragraph().add_run(
                     "Voor veel genen worden de genetische variaties aangegeven met ster en nummer (bijv. *1/*1). De meeste medicijnen worden in het lichaam door enzymen  (eiwitten) afgebroken. Dit proces wordt stofwisseling (metabolisme) genoemd. De voorspelde activiteit van een enzym (fenotype) is genetisch bepaald. CYP3A5 bijvoorbeeld, is een enzym, dat bij de westerse bevolking, in het algemeen geen activiteit heeft. De meeste Nederlanders zullen dus PM als fenotype hebben. De standaard dosering is hier al op afgestemd. Dus voor CYP3A5 is alleen een aanpassing van de dosering nodig, als het fenotype NM, IM, RM of UM is. Dit geldt ook voor Factor 5 en Factor 2; aanpassen van de dosering kan overwogen worden bij fenotype NM, IM."
                     "\n\nSommige genen zorgen voor transport van een medicijn door het lichaam. SLCO1B1 codeert voor een transporteiwit. Variaties kunnen de functie van het gen beïnvloeden. Dit wordt aangegeven met IF, NF, DF of PF (respectievelijk een verhoogde, normale , verminderde of geen functie). Dat geldt ook voor MTRNR1. CYP1A2 is bij de westerse bevolking zeer actief (*1F/*1F) en wordt aangegeven als normaal metabolisme met een verhoogde induceerbaarheid: NM, (apothekercode 560). Verminderde induceerbaarheid wordt aangegveen met IM (apothekercode 555) en nauwelijks of geen induceerbaarheid met PM (apothekercode 556).")
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
                     "CACNA1S": "WT,c.520C>T,c.3257G>A",
                     "CFTR": "WT, F508delCTT en G551D",
                     "COMT": "Val en Met",
                     "CYP1A2": "*1(A,F)",
                     "CYP2A6": "*1,*9",
                     # Alleen *1, *9 voor dit rapport ("*1, *1H, *2, *6, *9, *11, *13, *14, *17, *20, *22, *25 t/m*28, *35(A,B), *41, *44, *4")
                     "CYP2B6": "*1 t/m *4, *12 t/m *22, *24 t/m *28, *35 t/m *38",
                     "CYP2C8": "*1(A, B, C), *2, *3, *4+1C, *5, *7, *8, *10 t/m *14 en P404A",
                     "CYP2C9": "*1 t/m *6, rs9332094C, *9 t/m *13, *15 t/m *21, *23 t/m *26, *29 t/m *32,*34, *36, *38, *39, *40, *42 t/m *58",
                     "CYP2C19": "*1 t/m *10, *12 t/m *19, *22 t/m *28, *34, *35",
                     "CYP2D6": "*1, *4, *4.021, *6  t/m *11, *14, *15, *18, *22, *23, *25, *28, *29, *31, *35, *40,*42,*45, *49, *51, *53 t/m *56.002, *62, *70, *73, *75, *84, *86, *88, *95, *100,*103, *107, *109, *114, *139, *5",
                     "CYP2E1": "*1A, *1B, *3, *4, *5B, *5+1B, *7A, *7A+1B, *7B, *7C, *7C+1B, *4+7A, *4+5+7A,*4+7A+1B, *5A+7A+1B",
                     "CYP3A4": "*1  t/m *20, *22, *23",
                     "CYP3A5": "*1, *2, *3, *3G, *4 t/m *8, *2+3",
                     "CYP4F2": "*1, *2, *3, *2+3",
                     "DPYD": "c.=, c.61C>T, c.295_298delTCAT, c.557A>G, c.703C>T, c.1129,5923C>G, c.1156G>T,c.1679T>G, c.1898delC, c.2846A>T en c.2983G>T",
                     "F2": "rs1799963",
                     "F5": "WT, Leiden, rs6018G, Leiden+rs6018G",
                     "G6PD": "B,A,Null",
                     "GSTP1": "*A, *B, *C",
                     "HLA-B*1502": "*1502",
                     "IFNL3": "rs12979860C en rs12979860T",
                     "MTHFR 1298A>C": "rs1801131",
                     "MTHFR 677C>T": "rs1801133",
                     "MTRNR1": "m.=, m.827A>G, m.1095T>C, m.1494C>T en Null",
                     "NAT1": "*4, *5, *11B, *11C, *14, *15, *17 t/m *19(A,B), *20 t/m *25, *27, *29, *30",
                     "NAT2": "*4,*5,(E, I, L, M, N, O, P, S, X, Y),*6,(G, H, I, J, K, M, O, P, V) *7, *7D, *10, *12(D, E, F, G, H, J, K, O),*13(D, F,) *14(D, F, H, K), *17 t/m *19, *21, *23, *24",
                     "OPRM1": "Rs1799971",
                     "RYR1": "WT,p.1571V+3933C,c.103T>C,c.418G>A,c.487C>T,c.742G>A,c.742G>C,c.1021G>A,\n"
                             "c.1021G>C,c.1565A>C,c.1565A>G,c.1840C>T,c.1841G>T,c.6487C>T,c.6488G>A,\n"
                             "c.6488G>C,c.6502G>A,c.6617C>G,c.6617C>T,c.7007G>A,c.7025A>G,c.7063C>T,\n"
                             "c.7304G>A,c.7354C>T,c.7360C>T,c.7361G>A,c.7372C>T,c.7373G>A,c.11708G>A,\n"
                             "c.14387A>G,c.14477C>T,c.14497C>T,c.14545G>A,c.14582G>A",
                     "SLCO1B1": "*1A, *1B, *5",
                     "TPMT": "*1 t/m *3(A, B, C, D), *4  t/m *21, *23 t/m *37",
                     "UGT1A1": "*1, *60, *28",
                     "UGT2B7": "*2a, *2g, *1a, *1b, *1c, *1d, *3",
                     "VKORC1": "*2",
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