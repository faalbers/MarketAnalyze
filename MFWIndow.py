from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QCheckBox, QComboBox
from PyQt6 import uic
import DataScrape as DS

class MFWindow(QMainWindow):
    def __init__(self):
        super(MFWindow, self).__init__()

        # load ui file
        uic.loadUi('MFWindow.ui', self)

        dataFileName = 'MF_DATA'
        self.MFData = DS.getData(dataFileName)

        self.MFData['CountryToMarkets'] = {}
        self.MFData['MarketToCountries'] = {}
        self.MFData['FundTypes'] = set()
        for quote, data in self.MFData['Quotes'].items():
            if not data['Market']['Country'] in self.MFData['CountryToMarkets']:
                self.MFData['CountryToMarkets'][data['Market']['Country']] = set()
            self.MFData['CountryToMarkets'][data['Market']['Country']].add(data['Market']['Name'])
            
            if not data['Market']['Name'] in self.MFData['MarketToCountries']:
                self.MFData['MarketToCountries'][data['Market']['Name']] = set()
            self.MFData['MarketToCountries'][data['Market']['Name']].add(data['Market']['Country'])

            if data['Fund']['Type'] == None:
                self.MFData['FundTypes'].add('N/A')
            else:
                self.MFData['FundTypes'].add(data['Fund']['Type'])
        
        self.countryChecks = QVBoxLayout()
        self.marketChecks = QVBoxLayout()
        self.fundTypeChecks = QVBoxLayout()
        self.allCountries()
        self.allMarkets()
        self.allFundTypes()

        self.bondsStocksCheck.setStyleSheet('margin-left:200;');
        self.bondsStocksCheck.setChecked(False)
        self.bondsStocksCheck.stateChanged.connect(self.bondsStocksChanged)
        self.bondsStocksChanged()

        self.minSBRatio.setValue(0)
        self.minSBRatio.valueChanged.connect(self.minSBChanged)

        self.maxSBRatio.setValue(100)
        self.maxSBRatio.valueChanged.connect(self.maxSBChanged)

        # self.setStyle()
        # self.capCombo.currentIndexChanged.connect(self.setStyle)
        # self.styleCombo.currentIndexChanged.connect(self.setStyle)
        # self.qualityCombo.currentIndexChanged.connect(self.setStyle)
        # self.sensitivityCombo.currentIndexChanged.connect(self.setStyle)

        self.msRating1.setChecked(True)
        self.msRating2.setChecked(True)
        self.msRating3.setChecked(True)
        self.msRating4.setChecked(True)
        self.msRating5.setChecked(True)
        self.msRatingNA.setChecked(True)

        self.makeData.clicked.connect(self.updateQuotes)

    def buildFundTypesCheckList(self):
        for i in reversed(range(self.fundTypeChecks.count())): 
            self.fundTypeChecks.itemAt(i).widget().setParent(None)
        for fundType in self.fundTypes:
            checkBox = QCheckBox(fundType)
            checkBox.setChecked(True)
            # checkBox.stateChanged.connect(self.countriesChanged)
            self.fundTypeChecks.addWidget(checkBox)
        self.fundTypeContents.setLayout(self.fundTypeChecks)
        self.selAllFundType.clicked.connect(self.checkAllFundType)
        self.unSelAllFundType.clicked.connect(self.uncheckAllFundType)
        # # self.updateQuotes()

    def checkAllFundType(self):
        for i in range(self.fundTypeChecks.count()):
            self.fundTypeChecks.itemAt(i).widget().setChecked(True)
    
    def uncheckAllFundType(self):
        for i in range(self.fundTypeChecks.count()):
            self.fundTypeChecks.itemAt(i).widget().setChecked(False)
    
    def allFundTypes(self):
        self.fundTypes = list(self.MFData['FundTypes'])
        self.fundTypes.sort()
        self.buildFundTypesCheckList()

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
        self.countries = list(self.MFData['CountryToMarkets'].keys())
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
                for market in self.MFData['CountryToMarkets'][self.countries[i]]:
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
        self.markets = list(self.MFData['MarketToCountries'].keys())
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
                for country in self.MFData['MarketToCountries'][self.markets[i]]:
                    self.countries.add(country)
        self.countries = list(self.countries)
        self.countries.sort()
        self.buildCountriesCheckList()

    def bondsStocksChanged(self):
        if self.bondsStocksCheck.isChecked():
            self.minSBRatio.setEnabled(True)
            self.maxSBRatio.setEnabled(True)
        else:
            self.minSBRatio.setEnabled(False)
            self.maxSBRatio.setEnabled(False)

    # def setStyle(self):
    #     self.stockCap = self.capCombo.currentText()
    #     self.stockStyle = self.styleCombo.currentText()
    #     self.bondCreditQ = self.qualityCombo.currentText()
    #     self.bondInterestRateS = self.sensitivityCombo.currentText()
    #     print(self.stockCap)
    #     print(self.stockStyle)
    #     print(self.bondCreditQ)
    #     print(self.bondInterestRateS)

    def minSBChanged(self):
        value = self.minSBRatio.value()
        if value > self.maxSBRatio.value():
            self.maxSBRatio.setValue(value)

    def maxSBChanged(self):
        value = self.maxSBRatio.value()
        if value < self.minSBRatio.value():
            self.minSBRatio.setValue(value)
    
    def updateQuotes(self):
        marketNames = set()
        for i in range(self.marketChecks.count()):
            widget = self.marketChecks.itemAt(i).widget()
            if widget.isChecked() == True:
                marketNames.add(self.markets[i])

        stockCap = self.capCombo.currentText()
        stockStyle = self.styleCombo.currentText()
        bondCreditQ = self.qualityCombo.currentText()
        bondInterestRateS = self.sensitivityCombo.currentText()

        ratings = set()
        if self.msRating1.isChecked() == True: ratings.add(1)
        if self.msRating2.isChecked() == True: ratings.add(2)
        if self.msRating3.isChecked() == True: ratings.add(3)
        if self.msRating4.isChecked() == True: ratings.add(4)
        if self.msRating5.isChecked() == True: ratings.add(5)
        if self.msRatingNA.isChecked() == True: ratings.add(None)

        # print(ratings)

        minSBRatio = float(self.minSBRatio.value())
        maxSBRatio = float(self.maxSBRatio.value())

        fundTypes = set()
        for i in range(self.fundTypeChecks.count()):
            widget = self.fundTypeChecks.itemAt(i).widget()
            if widget.isChecked() == True:
                if self.fundTypes[i] == 'N/A':
                    fundTypes.add(None)
                else:
                    fundTypes.add(self.fundTypes[i])
        # print(fundTypes)

        quotes = []
        for quote, data in self.MFData['Quotes'].items():
            if not data['Market']['Name'] in marketNames: continue

            if not data['Data']['MorningStarRating'] in ratings: continue
            
            if not data['Fund']['Type'] in fundTypes: continue

            if self.etradeOpen.isChecked() and data['Data']['ETradeAvailbility'] != 'Open': continue

            if self.bondsStocksCheck.isChecked():
                sbRatio = data['Data']['AssetAllocation']['StocksBondsRatio']
                if sbRatio == None: continue
                if not (sbRatio[0] >= minSBRatio and sbRatio[0] <= maxSBRatio): continue

            if self.minYieldCheck.isChecked():
                if data['Data']['Yield'] == None: continue
                if data['Data']['Yield'][0] < self.minYield.value(): continue

            if self.maxExpenseCheck.isChecked():
                edata = data['Data']['Expense']
                if edata['NetExpenseRatio'] == None and edata['AdjExpenseRatio'] == None: continue
                expenseRatio = 0.0
                if edata['NetExpenseRatio'] != None and edata['NetExpenseRatio'][0] > expenseRatio:
                    expenseRatio = edata['NetExpenseRatio'][0]
                if edata['AdjExpenseRatio'] != None and edata['AdjExpenseRatio'][0] > expenseRatio:
                    expenseRatio = edata['AdjExpenseRatio'][0]
                if expenseRatio > self.maxExpense.value(): continue
            
            if self.maxInvestCheck.isChecked():
                if data['Data']['MinInvestment'] != None and data['Data']['MinInvestment'][0] > self.maxInvest.value(): continue

            if stockCap != 'N/A':
                if data['Data']['Stocks']['Cap'] != stockCap: continue

            if stockStyle != 'N/A':
                if data['Data']['Stocks']['Style'] != stockStyle: continue

            if bondCreditQ != 'N/A':
                if data['Data']['Bonds']['CreditQuality'] != bondCreditQ: continue

            if bondInterestRateS != 'N/A':
                if data['Data']['Bonds']['InterestRateSensitivity'] != bondInterestRateS: continue
            
            quotes.append(quote)

        self.quoteCount.display(len(quotes))

        if self.doSaveCSV.isChecked(): self.saveCSV(quotes)

    def saveCSV(self, quotes):
        CSVFileName = 'MF_ANALYZE_DATA.csv'
        out = ''
        out += 'Symbol, Name, Family, Type, MSRating,'
        out += 'ExpenseRatio %, Yield %,'
        # out += 'MinInvestment, ETrade,'
        out += 'MinInvestment,'
        # out += 'Stocks %, Cap, Style,'
        # out += 'Bonds %, CreditQuality, InterestRateSensitivity,'
        out += 'Stocks %, Bonds %, S/B Ratio %,'
        out += 'Cap, Style, CreditQuality, InterestRateSensitivity,'
        out += 'Market, ETrade'
        out += '\n'

        for quote in quotes:
            fund = self.MFData['Quotes'][quote]['Fund']
            market = self.MFData['Quotes'][quote]['Market']
            data = self.MFData['Quotes'][quote]['Data']

            symbol = '"%s"' % fund['Symbol']
            name = '"%s"' % fund['Name']
            ftype = '"%s"' % fund['Type']
            marketName = '"%s"' % market['Name']

            family = 'N/A'
            if fund['Family'] != None:
                family = '"%s"' % fund['Family']

            msrating = 'N/A'
            if data['MorningStarRating'] != None: msrating = data['MorningStarRating']
            
            expenseRatio = 'N/A'
            edata = data['Expense']
            if not (edata['NetExpenseRatio'] == None and edata['AdjExpenseRatio'] == None):
                expenseRatio = 0.0
                if edata['NetExpenseRatio'] != None and edata['NetExpenseRatio'][0] > expenseRatio:
                    expenseRatio = edata['NetExpenseRatio'][0]
                if edata['AdjExpenseRatio'] != None and edata['AdjExpenseRatio'][0] > expenseRatio:
                    expenseRatio = edata['AdjExpenseRatio'][0]

            Yield = 'N/A'
            if data['Yield'] != None: Yield = data['Yield'][0]

            mininvest = 'N/A'
            if data['MinInvestment'] != None: mininvest = data['MinInvestment'][0]

            aadata = data['AssetAllocation']
            stocks = 'N/A'
            if aadata['Stocks'] != None: stocks = aadata['Stocks'][0]
            
            bonds = 'N/A'
            if aadata['Bonds'] != None: bonds = aadata['Bonds'][0]

            sdata = data['Stocks']
            cap = 'N/A'
            if sdata['Cap'] != None: cap = sdata['Cap']
            
            style = 'N/A'
            if sdata['Style'] != None: style = sdata['Style']

            bdata = data['Bonds']
            cquality = 'N/A'
            if bdata['CreditQuality'] != None: cquality = bdata['CreditQuality']
            
            irsensitivity = 'N/A'
            if bdata['InterestRateSensitivity'] != None: irsensitivity = bdata['InterestRateSensitivity']

            sbratio = 'N/A'
            if aadata['StocksBondsRatio'] != None: sbratio = aadata['StocksBondsRatio'][0]

            etradeAvailable = 'N/A'
            if data['ETradeAvailbility'] != None: etradeAvailable = '"%s"' % data['ETradeAvailbility']

            out += '%s,%s,%s,%s,%s,' % (symbol, name, family, ftype, msrating)
            out += '%s,%s,' % (expenseRatio, Yield)
            # # out += '%s,%s,' % (mininvest, etradeAvailable)
            out += '%s,' % (mininvest)
            # out += '%s,%s,%s,' % (stocks, cap, style)
            # out += '%s,%s,%s,' % (bonds, cquality, irsensitivity)
            out += '%s,%s,%s,' % (stocks, bonds, sbratio)
            out += '%s,%s,%s,%s,' % (cap, style, cquality, irsensitivity)
            out += '%s,%s' % (marketName, etradeAvailable)
            out += '\n'

        with open(CSVFileName, 'w', encoding='utf-8') as f:
            f.write(out)
        
        self.doSaveCSV.setChecked(False)
    
