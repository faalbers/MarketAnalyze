import DataScrape as DS
import logging

if __name__ == "__main__":
    scrapedFileName = 'M_DATA_SCRAPED'
    dataFileName = 'ST_DATA'

    DS.setupLogging('STDataCreate.log', timed=False, new=True)
    # DS.setupLogging('Types.log', timed=False, new=False)

    MSData = DS.getData(scrapedFileName)
    STData = {}
    STData['Quotes'] = {}

    # get all stock quotes and sort them
    quotes = set()
    for quote, data in MSData['MarketWatchQuoteData'].items():
        if 'SubType' in data:
            if data['SubType'] == 'Stocks' or data['SubType'] == 'ADRs':
                quotes.add(quote)
    for quote, data in MSData['MarketWatchQuotes'].items():
        if data['Type'] == 'STOCK':
            if 'Type' in MSData['MarketWatchQuoteData'][quote] and MSData['MarketWatchQuoteData'][quote]['Type'] == 'fund':
                continue
            quotes.add(quote)
    quotes = list(quotes)
    quotes.sort()
    
    values = set()
    for quote in quotes:
        quoteSplits = quote.split(':')

        # skip quotes with no market
        MIC = quoteSplits[1]
        if MIC == '': continue
        elif not MIC in MSData['MICs']: continue

        STData['Quotes'][quote] = {}

        # create data structure
        stock = {
            'Symbol': None,
            'Name': None,
            'Country': None,
            'CISO': None,
            'Type': None,
            'Sector': None,
        }
        STData['Quotes'][quote]['Stock'] = stock

        market = {
            'MIC': None,
            'Name': None,
            'CISO': None,
            'Country': None
        }
        STData['Quotes'][quote]['Market'] = market
        
        data = {
            'Yield': None,
            'P/ERatio': None,
            'EPS': None,
            'Dividend': None,
            'DividendDate': None,
            'Beta': None,
            'Performance': {
                '5Day': None,
                '1Month': None,
                '3Month': None,
                'Ytd': None,
                '1Year': None,
            },
        }
        STData['Quotes'][quote]['Data'] = data

        stock['Symbol'] = quoteSplits[0]
        stock['Name'] = MSData['MarketWatchQuotes'][quote]['Name']
        for fCISO, fcountry in MSData['CISOs'].items():
            if 'Country' in MSData['MarketWatchQuotes'][quote]:
                if fcountry.startswith(MSData['MarketWatchQuotes'][quote]['Country']):
                    stock['Country'] = fcountry
                    stock['CISO'] = fCISO

        market['MIC'] = MIC
        market['Name'] = MSData['MICs'][MIC]['Name']
        market['CISO'] = list(MSData['MICToCISO'][MIC])[0]
        market['Country'] = MSData['CISOs'][market['CISO']]

        # handle MarketWatchQuoteData
        qdata = MSData['MarketWatchQuoteData'][quote]
        try:
            data['Type'] = qdata['SubType']
        except: pass
        try:
            data['Yield'] = qdata['KeyData']['Yield']
        except: pass
        try:
            data['P/ERatio'] = qdata['KeyData']['P/eRatio']
        except: pass
        try:
            data['EPS'] = qdata['KeyData']['Eps']
        except: pass
        try:
            data['Dividend'] = qdata['KeyData']['Dividend']
        except: pass
        try:
            data['DividendDate'] = qdata['KeyData']['Ex-dividendDate']
        except: pass
        try:
            data['Beta'] = qdata['KeyData']['Beta']
        except: pass
        try:
            data['Performance']['5Day'] = qdata['Performance']['5Day']
        except: pass
        try:
            data['Performance']['1Month'] = qdata['Performance']['1Month']
        except: pass
        try:
            data['Performance']['3Month'] = qdata['Performance']['3Month']
        except: pass
        try:
            data['Performance']['Ytd'] = qdata['Performance']['Ytd']
        except: pass
        try:
            data['Performance']['1Year'] = qdata['Performance']['1Year']
        except: pass


        # handle MarketWatchQuoteData
        qdata = MSData['MarketWatchQuotes'][quote]
        try:
            if qdata['Sector'] != '':
                stock['Sector'] = qdata['Sector']
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
    logging.info('Stock Quotes: %s' % len(STData['Quotes']))
    for quote, data in STData['Quotes'].items():
        logging.info(quote)
        for attribute, value in data.items():
            logging.info('%s: %s' % (attribute,value))
        logging.info('')
    
    if not DS.saveData(STData, dataFileName):
        logging.info('%s: Stop saving data and exit program' % dataFileName)
        exit(0)
