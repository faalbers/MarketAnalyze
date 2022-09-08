from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QCheckBox, QComboBox
from PyQt6 import uic
import DataScrape as DS

class STWindow(QMainWindow):
    def __init__(self):
        super(STWindow, self).__init__()

        # load ui file
        uic.loadUi('STWindow.ui', self)

        dataFileName = 'ST_DATA'
        self.STData = DS.getData(dataFileName)

        self.STData['CountryToMarkets'] = {}
        self.STData['MarketToCountries'] = {}
        self.STData['Sectors'] = set()
        self.STData['Types'] = set()
        for quote, data in self.STData['Quotes'].items():
            if not data['Market']['Country'] in self.STData['CountryToMarkets']:
                self.STData['CountryToMarkets'][data['Market']['Country']] = set()
            self.STData['CountryToMarkets'][data['Market']['Country']].add(data['Market']['Name'])
            
            if not data['Market']['Name'] in self.STData['MarketToCountries']:
                self.STData['MarketToCountries'][data['Market']['Name']] = set()
            self.STData['MarketToCountries'][data['Market']['Name']].add(data['Market']['Country'])

            if data['Stock']['Sector'] == None:
                self.STData['Sectors'].add('N/A')
            else:
                self.STData['Sectors'].add(data['Stock']['Sector'])
        
            if data['Stock']['Type'] == None:
                self.STData['Types'].add('N/A')
            else:
                self.STData['Types'].add(data['Stock']['Type'])
        
        self.countryChecks = QVBoxLayout()
        self.marketChecks = QVBoxLayout()
        self.sectorChecks = QVBoxLayout()
        self.typeChecks = QVBoxLayout()
        self.allCountries()
        self.allMarkets()
        self.allSectors()
        self.allTypes()

        self.makeData.clicked.connect(self.updateQuotes)

    def buildSectorsCheckList(self):
        for i in reversed(range(self.sectorChecks.count())): 
            self.sectorChecks.itemAt(i).widget().setParent(None)
        for sector in self.sectors:
            checkBox = QCheckBox(sector)
            checkBox.setChecked(True)
            # checkBox.stateChanged.connect(self.countriesChanged)
            self.sectorChecks.addWidget(checkBox)
        self.sectorContents.setLayout(self.sectorChecks)
        self.selAllSectors.clicked.connect(self.checkAllSectors)
        self.unSelAllSectors.clicked.connect(self.uncheckAllSectors)
        # # self.updateQuotes()

    def checkAllSectors(self):
        for i in range(self.sectorChecks.count()):
            self.sectorChecks.itemAt(i).widget().setChecked(True)
    
    def uncheckAllSectors(self):
        for i in range(self.sectorChecks.count()):
            self.sectorChecks.itemAt(i).widget().setChecked(False)
    
    def allSectors(self):
        self.sectors = list(self.STData['Sectors'])
        self.sectors.sort()
        self.buildSectorsCheckList()

    def buildTypesCheckList(self):
        for i in reversed(range(self.typeChecks.count())): 
            self.typeChecks.itemAt(i).widget().setParent(None)
        for type in self.types:
            checkBox = QCheckBox(type)
            checkBox.setChecked(True)
            # checkBox.stateChanged.connect(self.countriesChanged)
            self.typeChecks.addWidget(checkBox)
        self.typeContents.setLayout(self.typeChecks)
        self.selAllTypes.clicked.connect(self.checkAllTypes)
        self.unSelAllTypes.clicked.connect(self.uncheckAllTypes)
        # # self.updateQuotes()

    def checkAllTypes(self):
        for i in range(self.typeChecks.count()):
            self.typeChecks.itemAt(i).widget().setChecked(True)
    
    def uncheckAllTypes(self):
        for i in range(self.typeChecks.count()):
            self.typeChecks.itemAt(i).widget().setChecked(False)

    def allTypes(self):
        self.types = list(self.STData['Types'])
        self.types.sort()
        self.buildTypesCheckList()

    def buildCountriesCheckList(self):
        for i in reversed(range(self.countryChecks.count())): 
            self.countryChecks.itemAt(i).widget().setParent(None)
        for country in self.countries:
            checkBox = QCheckBox(country)
            checkBox.setChecked(True)
            checkBox.stateChanged.connect(self.countriesChanged)
            self.countryChecks.addWidget(checkBox)
        self.countriesContents.setLayout(self.countryChecks)
        self.selAllCountries.clicked.connect(self.checkAllCountries)
        self.unSelAllCountries.clicked.connect(self.uncheckAllCountries)
        self.showAllCountries.clicked.connect(self.allCountriesClick)
        # self.updateQuotes()

    def checkAllCountries(self):
        for i in range(self.countryChecks.count()):
            self.countryChecks.itemAt(i).widget().setChecked(True)
    
    def uncheckAllCountries(self):
        for i in range(self.countryChecks.count()):
            self.countryChecks.itemAt(i).widget().setChecked(False)
    
    def allCountries(self):
        self.countries = list(self.STData['CountryToMarkets'].keys())
        self.countries.sort()
        self.buildCountriesCheckList()
    
    def allCountriesClick(self):
        self.allCountries()
        self.allMarkets()

    def countriesChanged(self):
        self.markets = set()
        for i in range(self.countryChecks.count()):
            widget = self.countryChecks.itemAt(i).widget()
            if widget.isChecked() == True:
                for market in self.STData['CountryToMarkets'][self.countries[i]]:
                    self.markets.add(market)
        self.markets = list(self.markets)
        self.markets.sort()
        self.buildMarketsCheckList()

    def buildMarketsCheckList(self):
        for i in reversed(range(self.marketChecks.count())): 
            self.marketChecks.itemAt(i).widget().setParent(None)
        for market in self.markets:
            checkBox = QCheckBox(market)
            checkBox.setChecked(True)
            checkBox.stateChanged.connect(self.marketsChanged)
            self.marketChecks.addWidget(checkBox)
        self.marketContents.setLayout(self.marketChecks)
        self.selAllMarkets.clicked.connect(self.checkAllMarkets)
        self.unSelAllMarkets.clicked.connect(self.uncheckAllMarkets)
        self.showAllMarkets.clicked.connect(self.allMarketsClick)
        # self.updateQuotes()

    def checkAllMarkets(self):
        for i in range(self.marketChecks.count()):
            self.marketChecks.itemAt(i).widget().setChecked(True)
    
    def uncheckAllMarkets(self):
        for i in range(self.marketChecks.count()):
            self.marketChecks.itemAt(i).widget().setChecked(False)

    def allMarkets(self):
        self.markets = list(self.STData['MarketToCountries'].keys())
        self.markets.sort()
        self.buildMarketsCheckList()

    def allMarketsClick(self):
        self.allMarkets()
        self.allCountries()

    def marketsChanged(self):
        self.countries = set()
        for i in range(self.marketChecks.count()):
            widget = self.marketChecks.itemAt(i).widget()
            if widget.isChecked() == True:
                for country in self.STData['MarketToCountries'][self.markets[i]]:
                    self.countries.add(country)
        self.countries = list(self.countries)
        self.countries.sort()
        self.buildCountriesCheckList()

    def updateQuotes(self):
        marketNames = set()
        for i in range(self.marketChecks.count()):
            widget = self.marketChecks.itemAt(i).widget()
            if widget.isChecked() == True:
                marketNames.add(self.markets[i])

        sectors = set()
        for i in range(self.sectorChecks.count()):
            widget = self.sectorChecks.itemAt(i).widget()
            if widget.isChecked() == True:
                if self.sectors[i] == 'N/A':
                    sectors.add(None)
                else:
                    sectors.add(self.sectors[i])

        types = set()
        for i in range(self.typeChecks.count()):
            widget = self.typeChecks.itemAt(i).widget()
            if widget.isChecked() == True:
                if self.types[i] == 'N/A':
                    types.add(None)
                else:
                    types.add(self.types[i])

        quotes = []
        for quote, data in self.STData['Quotes'].items():
            if not data['Market']['Name'] in marketNames: continue

            if not data['Stock']['Sector'] in sectors: continue
            
            if not data['Stock']['Type'] in types: continue

            if self.yieldCheck.isChecked():
                if data['Data']['Yield'] == None: continue
                if data['Data']['Yield'][0] < self.yieldMin.value(): continue

            if self.dividendCheck.isChecked():
                if data['Data']['Dividend'] == None: continue
                if data['Data']['Dividend'][0] < self.dividendMin.value(): continue

            if self.peRatioCheck.isChecked():
                if data['Data']['P/ERatio'] == None: continue
                if data['Data']['P/ERatio'] > self.peRatioMax.value(): continue

            if self.epsCheck.isChecked():
                if data['Data']['EPS'] == None: continue
                if data['Data']['EPS'][0] < self.epsMin.value(): continue

            if self.betaCheck.isChecked():
                if data['Data']['Beta'] == None: continue
                if data['Data']['Beta'] < self.betaMin.value(): continue

            if self.perf5DayCheck.isChecked():
                if data['Data']['Performance']['5Day'] == None: continue
                if data['Data']['Performance']['5Day'][0] < self.perf5DayMin.value(): continue

            if self.perf1MonthCheck.isChecked():
                if data['Data']['Performance']['1Month'] == None: continue
                if data['Data']['Performance']['1Month'][0] < self.perf1MonthMin.value(): continue

            if self.perf3MonthCheck.isChecked():
                if data['Data']['Performance']['3Month'] == None: continue
                if data['Data']['Performance']['3Month'][0] < self.perf3MonthMin.value(): continue

            if self.perfYtdCheck.isChecked():
                if data['Data']['Performance']['Ytd'] == None: continue
                if data['Data']['Performance']['Ytd'][0] < self.perfYtdMin.value(): continue

            if self.perf1YearCheck.isChecked():
                if data['Data']['Performance']['1Year'] == None: continue
                if data['Data']['Performance']['1Year'][0] < self.perf1YearMin.value(): continue

            quotes.append(quote)

        self.quoteCount.display(len(quotes))

        if self.doSaveCSV.isChecked(): self.saveCSV(quotes)

    def saveCSV(self, quotes):
        CSVFileName = 'ST_ANALYZE_DATA.csv'
        out = ''
        out += 'Symbol, Name, Type, Sector,'
        out += 'Yield %, P/ERatio,'
        out += 'EPS, Cur,'
        out += 'Dividend, Cur, DivDate,'
        out += 'Beta,'
        out += '5Day %, 1Month %, 3Month %, Ytd %, 1Year %,'
        out += 'Market'
        out += '\n'

        for quote in quotes:
            stock = self.STData['Quotes'][quote]['Stock']
            market = self.STData['Quotes'][quote]['Market']
            data = self.STData['Quotes'][quote]['Data']

            symbol = '"%s"' % stock['Symbol']
            name = '"%s"' % stock['Name']
            marketName = '"%s"' % market['Name']

            type = 'N/A'
            if stock['Type'] != None: type = stock['Type']

            sector = 'N/A'
            if stock['Sector'] != None: sector = stock['Sector']

            Yield = 'N/A'
            if data['Yield'] != None: Yield = data['Yield'][0]

            PERatio = 'N/A'
            if data['P/ERatio'] != None: PERatio = data['P/ERatio']

            EPS = 'N/A'
            EPSCurrency = 'N/A'
            if data['EPS'] != None:
                EPS = data['EPS'][0]
                EPSCurrency = data['EPS'][1]
            
            dividend = 'N/A'
            dividendCurrency = 'N/A'
            dividendDate = 'N/A'
            if data['Dividend'] != None:
                dividend = data['Dividend'][0]
                dividendCurrency = data['Dividend'][1]
            if data['DividendDate'] != None:
                dividendDate = data['DividendDate']

            beta = 'N/A'
            if data['Beta'] != None: beta = data['Beta']
            
            p5Day = 'N/A'
            if data['Performance']['5Day'] != None: p5Day = data['Performance']['5Day'][0]

            p1Month = 'N/A'
            if data['Performance']['1Month'] != None: p1Month = data['Performance']['1Month'][0]

            p3Month = 'N/A'
            if data['Performance']['3Month'] != None: p3Month = data['Performance']['3Month'][0]

            pYtd = 'N/A'
            if data['Performance']['Ytd'] != None: pYtd = data['Performance']['Ytd'][0]

            p1Year = 'N/A'
            if data['Performance']['1Year'] != None: p1Year = data['Performance']['1Year'][0]

            out += '%s,%s,%s,%s,' % (symbol, name, type, sector)
            out += '%s,%s,' % (Yield, PERatio)
            out += '%s,%s,' % (EPS, EPSCurrency)
            out += '%s,%s,"%s",' % (dividend, dividendCurrency, dividendDate)
            out += '%s,' % (beta)
            out += '%s,%s,%s,%s,%s,' % (p5Day, p1Month, p3Month, pYtd, p1Year)
            out += '%s' % (marketName)
            out += '\n'

        with open(CSVFileName, 'w', encoding='utf-8') as f:
            f.write(out)
        
        self.doSaveCSV.setChecked(False)
    