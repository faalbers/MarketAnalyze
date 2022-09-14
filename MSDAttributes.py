import DataScrape as DS
import logging

attrReplace = {
    'MarketWatchQuotes': 'SYMBOL:MIC',
    'MorningStarQuotes': 'SYMBOL:MIC',
    'MorningStarQuoteData': 'SYMBOL:MIC',
    'MarketWatchQuoteData': 'SYMBOL:MIC',
    'MarketWatchHoldingsData': 'SYMBOL:MIC',
    'ETradeQuoteData': 'SYMBOL',
    'ETradeMFQuoteData': 'SYMBOL',
    'CISOs': 'CISO',
    'MICs': 'MIC',
    'MICToCISO': 'MIC',
    'CISOToMIC': 'CISO',
    }

attributeDocs = {
    'CISOs': {
        '__doc__': 'Country ISO code list'
    },
    'MICs': {
        '__doc__': 'Exchange Market ISO code list',
        'MIC': {
            'Name': {
                '__doc__': 'Descriptive Full Exchange Market Name'
            },
            'Country': {
                '__doc__': "Country for Exchange Market in the form of 'XX - Country Name'. XX is the Country ISO code. Used to extract CISO of MIC"
            }
        }
    },
    'MICToCISO': {
        '__doc__': 'Exchange Market ISO code to Country ISO codes Link list '
    },
    'CISOToMIC': {
        '__doc__': 'Country ISO code to Exchange Market ISO codes Link list '
    },
    'MarketWatchQuotes': {
        '__doc__': 'Quotes and base data scraped from MarketWatch Mutual Fund and Stock Lists',
        'SYMBOL:MIC': {
            '__doc__': "List of Quotes in form 'SYMBOL:MIC'",
            'Name': {
                '__doc__': 'Descriptive Full Quote Name.'
            },
            'Country': {
                '__doc__': 'Country of Equity'
            }
        }
    },
    }

def dictRecurse(data, parentKey, attributes):
    if type(data) == dict:
        for attr, subAttributes in data.items():
            if parentKey in attrReplace:
                attr = attrReplace[parentKey]
            
            if not attr in  attributes:
                attributes[attr] = {'__doc__': ''}
            
            dictRecurse(subAttributes, attr, attributes[attr])

def writeDocs(attributes, attributeDocs):
    for attr, subAttributesDocs in attributeDocs.items():
        if attr in attributes:
            if attr == '__doc__':
                attributes['__doc__'] = subAttributesDocs
            else:
                writeDocs(attributes[attr], subAttributesDocs)

def logAttributes(attributes, level):
    attrList = list(attributes.keys())
    attrList.sort()
    for attr in attrList:
        subAttributes = attributes[attr]
        if attr != '__doc__':
            logging.info('%s%s: %s' % ('    ' * level, attr, subAttributes['__doc__']))
            logAttributes(subAttributes, level+1)

def keepOnlyKeys(keys, data):
    popKeys = set(data.keys()).difference(keys)
    for key in popKeys: data.pop(key)
    print(len(data))

def quoteFilter(MSData, log=True):
    all = set(MSData['MarketWatchQuotes'].keys())
    mwqdFunds = set()
    mwqdStocks = set()
    mwqdIndexes = set()
    mwqdNoTypes = set()
    mwqdstFunds = set()
    mwqdstStocks = set()
    mwqdstETFs = set()
    mwqdstADRs = set()
    mwqdstIndexes = set()
    mwqdstUS = set()
    mwqdstOthers = set()
    mwqdstNoTypes = set()
    types = set()
    for quote, data in MSData['MarketWatchQuoteData'].items():
        if 'Type' in data:
            if 'Type' in data and data['Type'] == 'fund': mwqdFunds.add(quote)
            elif 'Type' in data and data['Type'] == 'stock': mwqdStocks.add(quote)
            elif 'Type' in data and data['Type'] == 'index': mwqdIndexes.add(quote)
        else:
            mwqdNoTypes.add(quote)
        
        if 'SubType' in data:
            types.add(data['SubType'])
            if data['SubType'] == 'Mutual Funds': mwqdstFunds.add(quote)
            elif data['SubType'] == 'Stocks': mwqdstStocks.add(quote)
            elif data['SubType'] == 'ETFs': mwqdstETFs.add(quote)
            elif data['SubType'] == 'ADRs': mwqdstADRs.add(quote)
            elif data['SubType'] == 'Index': mwqdstIndexes.add(quote)
            elif data['SubType'] == 'United States': mwqdstUS.add(quote)
            else: mwqdstOthers.add(quote)
        else:
            mwqdstNoTypes.add(quote)

    print(types)
    if log:
        logging.info("MarketWatchQuoteData:")
        logging.info("Quotes          : %s" % len(MSData['MarketWatchQuoteData']))
        logging.info("Type == 'fund'  : %s" % len(mwqdFunds))
        logging.info("  SubType == 'Mutual Funds' : %s" % len(mwqdFunds.intersection(mwqdstFunds)))
        logging.info("  SubType == 'Stocks'       : %s" % len(mwqdFunds.intersection(mwqdstStocks)))
        logging.info("  SubType == 'ETFs'         : %s" % len(mwqdFunds.intersection(mwqdstETFs)))
        logging.info("  SubType == 'ADRs'         : %s" % len(mwqdFunds.intersection(mwqdstADRs)))
        logging.info("  SubType == 'Index'        : %s" % len(mwqdFunds.intersection(mwqdstIndexes)))
        logging.info("  SubType == 'United States': %s" % len(mwqdFunds.intersection(mwqdstUS)))
        logging.info("  SubType ==  Other         : %s" % len(mwqdFunds.intersection(mwqdstOthers)))
        logging.info("  SubType ==  No Sub Type   : %s" % len(mwqdFunds.intersection(mwqdstNoTypes)))
        logging.info("Type == 'stock' : %s" % len(mwqdStocks))
        logging.info("  SubType == 'Mutual Funds' : %s" % len(mwqdStocks.intersection(mwqdstFunds)))
        logging.info("  SubType == 'Stocks'       : %s" % len(mwqdStocks.intersection(mwqdstStocks)))
        logging.info("  SubType == 'ETFs'         : %s" % len(mwqdStocks.intersection(mwqdstETFs)))
        logging.info("  SubType == 'ADRs'         : %s" % len(mwqdStocks.intersection(mwqdstADRs)))
        logging.info("  SubType == 'Index'        : %s" % len(mwqdStocks.intersection(mwqdstIndexes)))
        logging.info("  SubType == 'United States': %s" % len(mwqdStocks.intersection(mwqdstUS)))
        logging.info("  SubType ==  Other         : %s" % len(mwqdStocks.intersection(mwqdstOthers)))
        logging.info("  SubType ==  No Sub Type   : %s" % len(mwqdStocks.intersection(mwqdstNoTypes)))
        logging.info("Type == 'index' : %s" % len(mwqdIndexes))
        logging.info("  SubType == 'Mutual Funds' : %s" % len(mwqdIndexes.intersection(mwqdstFunds)))
        logging.info("  SubType == 'Stocks'       : %s" % len(mwqdIndexes.intersection(mwqdstStocks)))
        logging.info("  SubType == 'ETFs'         : %s" % len(mwqdIndexes.intersection(mwqdstETFs)))
        logging.info("  SubType == 'ADRs'         : %s" % len(mwqdIndexes.intersection(mwqdstADRs)))
        logging.info("  SubType == 'Index'        : %s" % len(mwqdIndexes.intersection(mwqdstIndexes)))
        logging.info("  SubType == 'United States': %s" % len(mwqdIndexes.intersection(mwqdstUS)))
        logging.info("  SubType ==  Other         : %s" % len(mwqdIndexes.intersection(mwqdstOthers)))
        logging.info("  SubType ==  No Sub Type   : %s" % len(mwqdIndexes.intersection(mwqdstNoTypes)))
        logging.info("Type ==  No Type: %s" % len(mwqdNoTypes))
        logging.info("  SubType == 'Mutual Funds' : %s" % len(mwqdNoTypes.intersection(mwqdstFunds)))
        logging.info("  SubType == 'Stocks'       : %s" % len(mwqdNoTypes.intersection(mwqdstStocks)))
        logging.info("  SubType == 'ETFs'         : %s" % len(mwqdNoTypes.intersection(mwqdstETFs)))
        logging.info("  SubType == 'ADRs'         : %s" % len(mwqdNoTypes.intersection(mwqdstADRs)))
        logging.info("  SubType == 'Index'        : %s" % len(mwqdNoTypes.intersection(mwqdstIndexes)))
        logging.info("  SubType == 'United States': %s" % len(mwqdNoTypes.intersection(mwqdstUS)))
        logging.info("  SubType ==  Other         : %s" % len(mwqdNoTypes.intersection(mwqdstOthers)))
        logging.info("  SubType ==  No Sub Type   : %s" % len(mwqdNoTypes.intersection(mwqdstNoTypes)))
        logging.info('')

    mwqFunds = set()
    mwqStocks = set()
    mwqETFs = set()
    mwqCEFs = set()
    mwqIndexes = set()
    mwqNones = set()
    for quote, data in MSData['MarketWatchQuotes'].items():
        if data['Type'] == 'FUND': mwqFunds.add(quote)
        elif data['Type'] == 'STOCK': mwqStocks.add(quote)
        elif data['Type'] == 'ETF': mwqETFs.add(quote)
        elif data['Type'] == 'CEF': mwqCEFs.add(quote)
        elif data['Type'] == 'INDEXE': mwqIndexes.add(quote)
        elif data['Type'] == None: mwqNones.add(quote)
    mwqNotNones = set(MSData['MarketWatchQuotes'].keys()).difference(mwqNones)
    
    if log:
        logging.info("MarketWatchQuote:")
        logging.info("Quotes          : %s" % len(MSData['MarketWatchQuotes']))
        logging.info("Type == 'FUND'  : %s" % len(mwqFunds))
        logging.info("  SubType == 'Mutual Funds' : %s" % len(mwqFunds.intersection(mwqdstFunds)))
        logging.info("  SubType == 'Stocks'       : %s" % len(mwqFunds.intersection(mwqdstStocks)))
        logging.info("  SubType == 'ETFs'         : %s" % len(mwqFunds.intersection(mwqdstETFs)))
        logging.info("  SubType == 'ADRs'         : %s" % len(mwqFunds.intersection(mwqdstADRs)))
        logging.info("  SubType == 'Index'        : %s" % len(mwqFunds.intersection(mwqdstIndexes)))
        logging.info("  SubType == 'United States': %s" % len(mwqFunds.intersection(mwqdstUS)))
        logging.info("  SubType ==  Other         : %s" % len(mwqFunds.intersection(mwqdstOthers)))
        logging.info("  SubType ==  No Sub Type   : %s" % len(mwqFunds.intersection(mwqdstOthers)))
        logging.info("Type == 'STOCK' : %s" % len(mwqStocks))
        logging.info("  SubType == 'Mutual Funds' : %s" % len(mwqStocks.intersection(mwqdstFunds)))
        logging.info("  SubType == 'Stocks'       : %s" % len(mwqStocks.intersection(mwqdstStocks)))
        logging.info("  SubType == 'ETFs'         : %s" % len(mwqStocks.intersection(mwqdstETFs)))
        logging.info("  SubType == 'ADRs'         : %s" % len(mwqStocks.intersection(mwqdstADRs)))
        logging.info("  SubType == 'Index'        : %s" % len(mwqStocks.intersection(mwqdstIndexes)))
        logging.info("  SubType == 'United States': %s" % len(mwqStocks.intersection(mwqdstUS)))
        logging.info("  SubType ==  Other         : %s" % len(mwqStocks.intersection(mwqdstOthers)))
        logging.info("  SubType ==  No Sub Type   : %s" % len(mwqStocks.intersection(mwqdstOthers)))
        logging.info("Type == 'ETF'   : %s" % len(mwqETFs))
        logging.info("  SubType == 'Mutual Funds' : %s" % len(mwqETFs.intersection(mwqdstFunds)))
        logging.info("  SubType == 'Stocks'       : %s" % len(mwqETFs.intersection(mwqdstStocks)))
        logging.info("  SubType == 'ETFs'         : %s" % len(mwqETFs.intersection(mwqdstETFs)))
        logging.info("  SubType == 'ADRs'         : %s" % len(mwqETFs.intersection(mwqdstADRs)))
        logging.info("  SubType == 'Index'        : %s" % len(mwqETFs.intersection(mwqdstIndexes)))
        logging.info("  SubType == 'United States': %s" % len(mwqETFs.intersection(mwqdstUS)))
        logging.info("  SubType ==  Other         : %s" % len(mwqETFs.intersection(mwqdstOthers)))
        logging.info("  SubType ==  No Sub Type   : %s" % len(mwqETFs.intersection(mwqdstOthers)))
        logging.info("Type == 'CEF'   : %s" % len(mwqCEFs))
        logging.info("  SubType == 'Mutual Funds' : %s" % len(mwqCEFs.intersection(mwqdstFunds)))
        logging.info("  SubType == 'Stocks'       : %s" % len(mwqCEFs.intersection(mwqdstStocks)))
        logging.info("  SubType == 'ETFs'         : %s" % len(mwqCEFs.intersection(mwqdstETFs)))
        logging.info("  SubType == 'ADRs'         : %s" % len(mwqCEFs.intersection(mwqdstADRs)))
        logging.info("  SubType == 'Index'        : %s" % len(mwqCEFs.intersection(mwqdstIndexes)))
        logging.info("  SubType == 'United States': %s" % len(mwqCEFs.intersection(mwqdstUS)))
        logging.info("  SubType ==  Other         : %s" % len(mwqCEFs.intersection(mwqdstOthers)))
        logging.info("  SubType ==  No Sub Type   : %s" % len(mwqCEFs.intersection(mwqdstOthers)))
        logging.info("Type == 'INDEXE': %s" % len(mwqIndexes))
        logging.info("  SubType == 'Mutual Funds' : %s" % len(mwqIndexes.intersection(mwqdstFunds)))
        logging.info("  SubType == 'Stocks'       : %s" % len(mwqIndexes.intersection(mwqdstStocks)))
        logging.info("  SubType == 'ETFs'         : %s" % len(mwqIndexes.intersection(mwqdstETFs)))
        logging.info("  SubType == 'ADRs'         : %s" % len(mwqIndexes.intersection(mwqdstADRs)))
        logging.info("  SubType == 'Index'        : %s" % len(mwqIndexes.intersection(mwqdstIndexes)))
        logging.info("  SubType == 'United States': %s" % len(mwqIndexes.intersection(mwqdstUS)))
        logging.info("  SubType ==  Other         : %s" % len(mwqIndexes.intersection(mwqdstOthers)))
        logging.info("  SubType ==  No Sub Type   : %s" % len(mwqIndexes.intersection(mwqdstOthers)))
        logging.info("Type ==  None   : %s" % len(mwqNones))
        logging.info("  SubType == 'Mutual Funds' : %s" % len(mwqNones.intersection(mwqdstFunds)))
        logging.info("  SubType == 'Stocks'       : %s" % len(mwqNones.intersection(mwqdstStocks)))
        logging.info("  SubType == 'ETFs'         : %s" % len(mwqNones.intersection(mwqdstETFs)))
        logging.info("  SubType == 'ADRs'         : %s" % len(mwqNones.intersection(mwqdstADRs)))
        logging.info("  SubType == 'Index'        : %s" % len(mwqNones.intersection(mwqdstIndexes)))
        logging.info("  SubType == 'United States': %s" % len(mwqNones.intersection(mwqdstUS)))
        logging.info("  SubType ==  Other         : %s" % len(mwqNones.intersection(mwqdstOthers)))
        logging.info("  SubType ==  No Sub Type   : %s" % len(mwqNones.intersection(mwqdstOthers)))
        logging.info('')
    
    # create quotes filter
    # fQuotes = mwqdstFunds.union(mwqdstETFs)
    # fQuotes = mwqdstStocks.union(mwqdstADRs)
    # fQuotes = mwqdFunds.intersection(mwqdstNoTypes)

    # fQuotes = mwqdNoTypes.intersection(mwqFunds)
    # fQuotes = mwqdNoTypes.intersection(mwqETFs)
    # fQuotes = mwqCEFs.intersection(mwqdstStocks)
    # fQuotes = mwqCEFs.intersection(mwqdstStocks)
    # fQuotes = mwqdstETFs

    # # MutualFunds
    # fQuotes = mwqdstFunds.union(mwqdstETFs).union(mwqFunds).union(mwqETFs).union(mwqCEFs)

    # # Stocks
    # fQuotes = mwqdstStocks.union(mwqdstADRs).union(mwqStocks).difference(mwqdFunds)

    # all
    fQuotes = all


    # return sorted quote list
    fQuotes = list(fQuotes)
    fQuotes.sort()
    return fQuotes

if __name__ == "__main__":
    DS.setupLogging('MSDAttributes.log', timed=False, new=True)
    scrapedFileName = 'M_DATA_SCRAPED'
    # scrapedFileName = 'M_DATA_SCRAPED_BACKUP_01'
    MSData = DS.getData(scrapedFileName)

    # quotes = quoteFilter(MSData)
    # logging.info('Quotes Count: %s'% len(quotes))
    # keepOnlyKeys(quotes, MSData['MorningStarQuoteData'])
    # keepOnlyKeys(quotes, MSData['MarketWatchQuoteData'])
    # keepOnlyKeys(quotes, MSData['MarketWatchHoldingsData'])

    attributes = {}
    dictRecurse(MSData, '', attributes)
    writeDocs(attributes, attributeDocs)
    logAttributes(attributes, 0)

    # logging.info('')
    # for quote in quotes:
    #     logging.info(quote)
