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
    # scrapedFileName = 'M_DATA_SCRAPED'
    scrapedFileName = 'M_DATA_SCRAPED'
    dataFileName = 'MF_DATA'

    DS.setupLogging('MFDataCreate.log', timed=False, new=True)
    # DS.setupLogging('Types.log', timed=False, new=False)

    MSData = DS.getData(scrapedFileName)
    MFData = {}
    MFData['Quotes'] = {}

    # get all funds quotes and sort them
    quotes = set()
    mwq_FUND = set()
    for quote, data in MSData['MarketWatchQuotes'].items():
        if data['Type'] == 'FUND': mwq_FUND.add(quote)
        elif data['Type'] == 'ETF': mwq_FUND.add(quote)
    
    mwqd_fund = set()
    for quote, data in MSData['MarketWatchQuoteData'].items():
        if 'Type' in data and data['Type'] == 'fund': mwqd_fund.add(quote)
    
    quotes = mwq_FUND.union(mwqd_fund)
    print(len(quotes))

    # get quotes with same symbol to find actual quote for ETrade data
    # add ETSymbol to MarketWatchQuotes if found
    etradeQuotes = {}
    for quote in quotes:
        symbol = quote.split(':')[0]
        data = MSData['MarketWatchQuotes'][quote]
        if not symbol in etradeQuotes: etradeQuotes[symbol] = set()
        etradeQuotes[symbol].add(quote)
    for symbol, symbolQuotes in etradeQuotes.items():
        etData = MSData['ETradeQuoteData'][symbol]
        for quote in symbolQuotes:
            MSData['MarketWatchQuotes'][quote]['ETSymbol'] = None
            if 'All' in etData:
                exchangeCode = etData['All']['primaryExchange']
                MIC = quote.split(':')[1]
                if MIC in MSData['MICs']:
                    operatingMIC = MSData['MICs'][MIC]['OperatingMic']
                    if operatingMIC in ETexchToOpMIC[exchangeCode]:
                        MSData['MarketWatchQuotes'][quote]['ETSymbol'] = symbol
            elif 'MutualFund' in etData:
                MIC = quote.split(':')[1]
                if MIC in MSData['MICToCISO']:
                    CISO = list(MSData['MICToCISO'][MIC])[0]
                    if CISO == 'US':
                        MSData['MarketWatchQuotes'][quote]['ETSymbol'] = symbol
    
    quotes = list(quotes)
    quotes.sort()
    
    values = set()
    symbolVals= set()
    symbolCounts = {}
    for quote in quotes:
        quoteSplits = quote.split(':')

        # skip quotes with no market
        MIC = quoteSplits[1]
        if MIC == '': continue
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
                'MWQ_Type': None,
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
                'AdjExpenseRatio': None
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
        fund['Name'] = MSData['MarketWatchQuotes'][quote]['Name']
        qdata = MSData['MarketWatchQuotes'][quote]
        fund['Types']['MWQ_Type'] = qdata['Type']
        for fCISO, fcountry in MSData['CISOs'].items():
            if 'Country' in qdata:
                if fcountry.startswith(qdata['Country']):
                    fund['Country'] = fcountry
                    fund['CISO'] = fCISO

        # handle MarketWatchQuoteData
        qdata = MSData['MarketWatchQuoteData'][quote]
        try:
            fund['Types']['MWQD_Type'] = qdata['Type']
        except: pass
        try:
            fund['Types']['MWQD_SubType'] = qdata['SubType']
        except: pass
        # try:
        #     if qdata['SubType'] == 'Mutual Funds':
        #         fund['Type'] = 'MutualFund'
        #     elif qdata['SubType'] == 'ETFs':
        #         fund['Type'] = 'ETF'
        # except: pass

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
        try:
            data['AssetAllocation']['Stocks'] = MSData['MarketWatchHoldingsData'][quote]['AssetAllocation']['Stocks']
        except: pass
        try:
            data['AssetAllocation']['Bonds'] = MSData['MarketWatchHoldingsData'][quote]['AssetAllocation']['Bonds']
        except: pass
        try:
            data['AssetAllocation']['Convertible'] = MSData['MarketWatchHoldingsData'][quote]['AssetAllocation']['Convertible']
        except: pass
        try:
            data['AssetAllocation']['Other'] = MSData['MarketWatchHoldingsData'][quote]['AssetAllocation']['Other']
        except: pass
        try:
            data['AssetAllocation']['Cash'] = MSData['MarketWatchHoldingsData'][quote]['AssetAllocation']['Cash']
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
        if MSData['MarketWatchQuotes'][quote]['ETSymbol'] != None:
            symbol = MSData['MarketWatchQuotes'][quote]['ETSymbol']
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
        if fund['Types']['MWQ_Type'] == 'ETF' or fund['Types']['MWQD_SubType'] == 'ETFs' or fund['Types']['ETQD_SubType'] == 'ETF':
            fund['Type'] = 'Exchange Traded Fund'
        elif fund['Types']['MWQ_Type'] == 'CEF':
            fund['Type'] = 'Closed End Fund'
        elif fund['Types']['ETQD_Type'] == 'MMF':
            fund['Type'] = 'Money Market Fund'
        elif fund['Types']['MWQ_Type'] == 'FUND' or fund['Types']['MWQD_SubType'] == 'Mutual Funds' or fund['Types']['ETQD_Type'] == 'MF':
            fund['Type'] = 'Mutual Fund'
    
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
