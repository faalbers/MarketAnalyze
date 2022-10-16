import DataScrape as DS
import logging

ETexchToOpMIC = {
    '': [],
    'NSDQ': ['XNAS', 'XNYS'],
    'NYSE': ['XNYS', 'XNAS', 'XCBO'],
    'AMEX': ['XNYS'],
    'PK': ['FINR', 'OTCM'],
    'BATS': ['XCBO', 'XNYS'],
    'US': ['FINR'],
    'ISE': [],
    'OTHER': [],
}

if __name__ == "__main__":
    scrapedFileName = 'M_DATA_SCRAPED'
    dataFileName = 'MF_DATA'

    DS.setupLogging('MFDataCreate.log', timed=False, new=True)
    # DS.setupLogging('Types.log', timed=False, new=False)

    MSData = DS.getData(scrapedFileName)
    MFData = {}
    MFData['Quotes'] = {}

    # get all funds quotes and sort them
    msq_FUND = set()
    for quote, data in MSData['MorningStarQuotes'].items():
        if data['Type'] == 'FUND': msq_FUND.add(quote)
        elif data['Type'] == 'ETF': msq_FUND.add(quote)
    
    mwqd_fund = set()
    for quote, data in MSData['MarketWatchQuoteData'].items():
        if 'Type' in data and data['Type'] == 'fund': mwqd_fund.add(quote)
    
    quotes = list(msq_FUND.union(mwqd_fund))
    quotes.sort()

    # get all symbols with their quote names and upper cased real names
    symbolsAll = {}
    for quote in quotes:
        # clean up name and make upper
        name = None
        if quote in MSData['MarketWatchQuotes']:
            name = MSData['MarketWatchQuotes'][quote]['Name']
        elif quote in MSData['MorningStarQuotes']:
            name = MSData['MorningStarQuotes'][quote]['Name']
        name = name.replace('.','').replace("'",'')
        if '(' in name and ')' in name:
            splits = name.split('(')
            name = splits[0].strip()
            for split in splits[1:]:
                name += ' '+split.split(')')[1].strip()
        name = name.upper()
        
        # get symbol
        symbol = quote.split(':')[0]
        if not symbol in symbolsAll:
            symbolsAll[symbol] = {}
        symbolsAll[symbol][quote] = name.upper()
    
    # sort quotes by same name
    symbols = {}
    for symbol, squotes in symbolsAll.items():
        symbols[symbol] = {}
        for quote, name in squotes.items():
            if not name in symbols[symbol]:
                symbols[symbol][name] = []
            symbols[symbol][name].append(quote)

    # create ETRADE symbol reference
    etQuotes = {}
    for symbol, names in symbols.items():
        etData = MSData['ETradeQuoteData'][symbol]
        for name, nquotes in names.items():
            for quote in nquotes:
                etQuotes[quote] = None
                if 'All' in etData:
                    exchangeCode = etData['All']['primaryExchange']
                    MIC = quote.split(':')[1]
                    if MIC in MSData['MICs']:
                        operatingMIC = MSData['MICs'][MIC]['OperatingMic']
                        if operatingMIC in ETexchToOpMIC[exchangeCode]:
                            etQuotes[quote] = symbol
                elif 'MutualFund' in etData:
                    MIC = quote.split(':')[1]
                    if MIC in MSData['MICToCISO']:
                        CISO = list(MSData['MICToCISO'][MIC])[0]
                        if CISO == 'US':
                            etQuotes[quote] = symbol
    
    values = set()
    symbolVals= set()
    symbolCounts = {}
    for quote in quotes:
        quoteSplits = quote.split(':')

        # skip quotes with no market
        MIC = quoteSplits[1]
        if MIC == '': continue
        elif not MIC in MSData['MICs']: continue
        
        symbol = quoteSplits[0]

        MFData['Quotes'][quote] = {}

        # create data structure
        fund = {
            'Symbol': None,
            'Name': None,
            'Family': None,
            'Country': None,
            'CISO': None,
            'Type': None,
            'Types': {
                'MSQ_Type': None,
                'MWQD_Type': None,
                'MWQD_SubType': None,
                'ETQD_Type': None,
                'ETQD_SubType': None,
            },
        }
        MFData['Quotes'][quote]['Fund'] = fund

        market = {
            'MIC': None,
            'Name': None,
            'CISO': None,
            'Country': None
        }
        MFData['Quotes'][quote]['Market'] = market
        
        data = {
            'MinInvestment': None,
            'Yield': None,
            'MorningStarRating': None,
            'ETradeAvailbility': None,
            'Expense': {
                'NetExpenseRatio': None,
                'TotalExpenseRatio': None,
                'ExpenseRatio': None,
                'AdjExpenseRatio': None,
                'FrontLoad': None
            },
            'Bonds': {
                'CreditQuality': None,
                'InterestRateSensitivity': None
            },
            'Stocks': {
                'Cap': None,
                'Style': None
            },
            'AssetAllocation': {
                'Stocks': None,
                'Bonds': None,
                'Convertible': None,
                'Other': None,
                'Cash': None,
                'StocksBondsRatio': None
            }
        }
        MFData['Quotes'][quote]['Data'] = data

        fund['Symbol'] = symbol
        market['MIC'] = MIC
        market['Name'] = MSData['MICs'][MIC]['Name']
        market['CISO'] = list(MSData['MICToCISO'][MIC])[0]
        market['Country'] = MSData['CISOs'][market['CISO']]

        # handle MarketWatchQuotes
        if quote in MSData['MarketWatchQuotes']:
            qdata = MSData['MarketWatchQuotes'][quote]
            fund['Name'] = qdata['Name']
            fund['Name'] = fund['Name'].replace('(%s)' % symbol, '').strip()
            for fCISO, fcountry in MSData['CISOs'].items():
                if fcountry.startswith(qdata['Country']):
                    fund['Country'] = fcountry
                    fund['CISO'] = fCISO

        # handle MorningStarQuotes
        if quote in MSData['MorningStarQuotes']:
            qdata = MSData['MorningStarQuotes'][quote]
            if fund['Name'] == None:
                fund['Name'] = qdata['Name']
            fund['Types']['MSQ_Type'] = qdata['Type']

        # handle MarketWatchQuoteData
        qdata = MSData['MarketWatchQuoteData'][quote]
        try:
            fund['Types']['MWQD_Type'] = qdata['Type']
        except: pass
        try:
            fund['Types']['MWQD_SubType'] = qdata['SubType']
        except: pass
        try:
            data['Expense']['FrontLoad'] = qdata['Fees&Expenses']['FrontLoad']
        except: pass

        try:
            data['MinInvestment'] = qdata['MinInvestment']['Standard(taxable)']
        except: pass
        try:
            data['Yield'] = qdata['KeyData']['Yield']
        except: pass
        try:
            data['Expense']['NetExpenseRatio'] = qdata['KeyData']['NetExpenseRatio']
        except: pass
        try:
            data['Expense']['TotalExpenseRatio'] = qdata['Fees&Expenses']['TotalExpenseRatio']
        except: pass
            
        # handle MorningStarQuoteData
        if quote in MSData['MorningStarQuoteData']:
            qdata = MSData['MorningStarQuoteData'][quote]
            try:
                data['Bonds']['CreditQuality'] = qdata['CreditQuality']
                data['Bonds']['InterestRateSensitivity'] = qdata['InterestRateSensitivity']
            except: pass
            try:
                splits = qdata['InvestmentStyle'].split()
                data['Stocks']['Cap'] = splits[0]
                data['Stocks']['Style'] = splits[1]
            except: pass
            try:
                data['MorningStarRating'] = qdata['Rating']
            except: pass
            try:
                if qdata['ExpenseRatio'] == '—':
                    data['Expense']['ExpenseRatio'] = None
                elif type(qdata['ExpenseRatio']) == float:
                    data['Expense']['ExpenseRatio'] = [0.0 , '%']
                else:
                    data['Expense']['ExpenseRatio'] = qdata['ExpenseRatio']
            except: pass
            try:
                if qdata['AdjExpenseRatio'] == '—':
                    data['Expense']['AdjExpenseRatio'] = None
                elif type(qdata['AdjExpenseRatio']) == float:
                    data['Expense']['AdjExpenseRatio'] = [0.0 , '%']
                else:
                    data['Expense']['AdjExpenseRatio'] = qdata['AdjExpenseRatio']
            except: pass

        # # get name and deduct strategies from name
        # data['Name'] = MSData['MarketWatchQuotes'][quote]['Name']
        # data['Strategies'] = set()
        # if 'ETF' in data['Name'].upper():
        #     data['Strategies'].add('ETF')
        # if 'BOND' in data['Name'].upper():
        #     data['Strategies'].add('BOND')
        # if 'INCOME' in data['Name'].upper():
        #     data['Strategies'].add('INCOME')
        # if 'GROWTH' in data['Name'].upper():
        #     data['Strategies'].add('GROWTH')
        # if 'VALUE' in data['Name'].upper():
        #     data['Strategies'].add('VALUE')
        # if 'EQUITY' in data['Name'].upper():
        #     data['Strategies'].add('EQUITY')
        # if 'INDEX' in data['Name'].upper():
        #     data['Strategies'].add('INDEX')
        # if 'TARGET' in data['Name'].upper():
        #     data['Strategies'].add('TARGET')
        # if 'GLOBAL' in data['Name'].upper():
        #     data['Strategies'].add('GLOBAL')
        # if 'INTERNATIONAL' in data['Name'].upper() or 'INTL' in data['Name'].upper():
        #     data['Strategies'].add('INTERNATIONAL')
        # if 'EMERGING' in data['Name'].upper():
        #     data['Strategies'].add('EMERGING')
        # if 'BALANCED' in data['Name'].upper() and not 'RISK' in data['Name'].upper():
        #     data['Strategies'].add('BALANCED')
        # if 'BALANCED' in data['Name'].upper() and 'RISK' in data['Name'].upper():
        #     data['Strategies'].add('BALANCEDRISK')

        # handle MarketWatchHoldingsData
        if quote in MSData['MarketWatchHoldingsData']:
            qdata = MSData['MarketWatchHoldingsData'][quote]
            try:
                data['AssetAllocation']['Stocks'] = qdata['AssetAllocation']['Stocks']
            except: pass
            try:
                data['AssetAllocation']['Bonds'] = qdata['AssetAllocation']['Bonds']
            except: pass
            try:
                data['AssetAllocation']['Convertible'] = qdata['AssetAllocation']['Convertible']
            except: pass
            try:
                data['AssetAllocation']['Other'] = qdata['AssetAllocation']['Other']
            except: pass
            try:
                data['AssetAllocation']['Cash'] = qdata['AssetAllocation']['Cash']
            except: pass

        stocksAmount =  0.0
        if data['AssetAllocation']['Stocks'] != None:
            stocksAmount = data['AssetAllocation']['Stocks'][0]
        if stocksAmount >= 0.0 and stocksAmount <= 100.0:
            bondsAmount =  0.0
            if data['AssetAllocation']['Bonds'] != None:
                bondsAmount = data['AssetAllocation']['Bonds'][0]
            if bondsAmount >= 0.0 and bondsAmount <= 100.0:
                total = bondsAmount+stocksAmount
                if total != 0.0:
                    data['AssetAllocation']['StocksBondsRatio'] = [(stocksAmount / total) * 100.0, '%']

        # handle ETrade data
        if etQuotes[quote] != None:
            symbol = etQuotes[quote]
            symbolData = MSData['ETradeQuoteData'][symbol]
            if 'MutualFund' in symbolData:
                fund['Family'] = symbolData['MutualFund']['fundFamily']
                if symbolData['MutualFund']['availability'] == 'Open to New Buy and Sell':
                    data['ETradeAvailbility'] = 'Open'
                else:
                    data['ETradeAvailbility'] = 'Closed'
            if 'Product' in symbolData:
                fund['Types']['ETQD_Type'] = symbolData['Product']['securityType']
                if 'securitySubType' in symbolData['Product']:
                    fund['Types']['ETQD_SubType'] = symbolData['Product']['securitySubType']

        # create main type
        if fund['Types']['MSQ_Type'] == 'ETF' or fund['Types']['MWQD_SubType'] == 'ETFs' or fund['Types']['ETQD_SubType'] == 'ETF':
            fund['Type'] = 'Exchange Traded Fund'
        elif fund['Types']['MSQ_Type'] == 'CEF':
            fund['Type'] = 'Closed End Fund'
        elif fund['Types']['ETQD_Type'] == 'MMF':
            fund['Type'] = 'Money Market Fund'
        elif fund['Types']['MSQ_Type'] == 'FUND' or fund['Types']['MWQD_SubType'] == 'Mutual Funds' or fund['Types']['ETQD_Type'] == 'MF':
            fund['Type'] = 'Mutual Fund'
        fund.pop('Types')
    print(values)

    # log quotes
    logging.info('Fund Quotes: %s' % len(MFData['Quotes']))
    for quote, data in MFData['Quotes'].items():
        logging.info(quote)
        for attribute, value in data.items():
            logging.info('%s: %s' % (attribute,value))
        logging.info('')
    
    if not DS.saveData(MFData, dataFileName):
        logging.info('%s: Stop saving data and exit program' % dataFileName)
        exit(0)
