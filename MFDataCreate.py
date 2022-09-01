import DataScrape as DS
import logging

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
    for quote, data in MSData['MarketWatchQuoteData'].items():
        if 'SubType' in data:
            if data['SubType'] == 'Mutual Funds' or data['SubType'] == 'ETFs':
                quotes.add(quote)
    for quote, data in MSData['MarketWatchQuotes'].items():
        if data['Type'] == 'FUND' or data['Type'] == 'ETF' or data['Type'] == 'CEF':
            quotes.add(quote)
    quotes = list(quotes)
    quotes.sort()
    
    values = set()
    for quote in quotes:
        quoteSplits = quote.split(':')

        # skip quotes with no market
        MIC = quoteSplits[1]
        if MIC == '': continue

        MFData['Quotes'][quote] = {}

        # create data structure
        fund = {
            'Symbol': None,
            'Name': None,
            'Country': None,
            'CISO': None,
            'Type': None
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
            'ETradeAvailbility': None,
            'MorningStarRating': None,
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


        fund['Symbol'] = quoteSplits[0]
        fund['Name'] = MSData['MarketWatchQuotes'][quote]['Name']
        for fCISO, fcountry in MSData['CISOs'].items():
            if 'Country' in MSData['MarketWatchQuotes'][quote]:
                if fcountry.startswith(MSData['MarketWatchQuotes'][quote]['Country']):
                    fund['Country'] = fcountry
                    fund['CISO'] = fCISO

        market['MIC'] = MIC
        market['Name'] = MSData['MICs'][MIC]['Name']
        market['CISO'] = list(MSData['MICToCISO'][MIC])[0]
        market['Country'] = MSData['CISOs'][market['CISO']]

        # handle MarketWatchQuoteData
        qdata = MSData['MarketWatchQuoteData'][quote]
        try:
            if qdata['SubType'] == 'Mutual Funds':
                fund['Type'] = 'MutualFund'
            elif qdata['SubType'] == 'ETFs':
                fund['Type'] = 'ETF'
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

        # handle MarketWatchQuoteData
        qdata = MSData['MarketWatchQuotes'][quote]
        try:
            if qdata['Type'] == 'ETF':
                fund['Type'] = 'ETF'
            elif qdata['Type'] == 'CEF':
                fund['Type'] = 'CEF'
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

        # # etrade data
        # if 'ETradeQuoteData' in MSData:
        #     qdata = MSData['ETradeQuoteData'][quote]
        #     if 'MutualFund' in qdata:
        #         if qdata['MutualFund']['availability'] == 'Open to New Buy and Sell':
        #             data['ETradeAvailbility'] = 'Open'
        #         else:
        #             data['ETradeAvailbility'] = 'Close'

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
