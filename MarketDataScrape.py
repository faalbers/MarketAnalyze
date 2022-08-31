import DataScrape as DS
from bs4 import BeautifulSoup
import logging
from datetime import datetime

# --- TOOLS ---

def quotesNeedScrape(MData, dataName, needScrape=True, seconds=0, minutes=0, hours=0, days=0):
    if not dataName in MData: return []
    minuteSecs = 60
    hourSecs = minuteSecs * 60
    daySecs = hourSecs * 24
    totalSecs = days * daySecs + hours * hourSecs + minutes * minuteSecs + seconds
    nowTime = datetime.now()
    quotesDone = set()
    for quote, data in MData[dataName].items():
        diffSecs = (nowTime - data['ScrapeTag']).total_seconds()
        if diffSecs <= totalSecs:
            quotesDone.add(quote)
    quotes = set(MData[dataName].keys())
    if needScrape:
        quotes = list(quotes.difference(quotesDone))
    else:
        quotes = list(quotesDone)
    return quotes

def cleanUpAttributes(attributes, capitalize=True, upper=False):
    data = {}
    for attr, value in attributes.items():
        attrName = ''
        currencies = '$£₹€¥₩'
        mults = 'KMBTp'
        
        # capitalize sub parts of attribute name
        for attrPart in attr.split():
            # if attrPart.startswith('('): continue
            # elif attrPart.startswith('%'): continue
            attrPart = attrPart.replace('.','')
            if upper:
                attrName = attrName + attrPart.upper()
            elif capitalize:
                attrName = attrName + attrPart.capitalize()
            else:
                attrName = attrName + attrPart
            
        if value == '' or value == 'N/A' or value == '-':
            data[attrName] = None
            continue

        # turn values into a list if not already a list
        values = [value]
        if type(value) == list:
            values = value
        cleanedValues = []
        for val in values:
            if val == '' or val == 'N/A' or val == '-':
                cleanedValues.append(None)
                continue

            if '★' in val:
                cleanedValues.append(len(val))
                continue
            
            splitValue = val.split()
            firstValue = splitValue[0].replace(',','')
            if len(splitValue) == 2 and firstValue.replace('.','').isnumeric():
                cleanedValues.append([float(firstValue), splitValue[1]])
                continue

            if val.endswith('%'):
                numtest = val.replace('%','')
                numtest = numtest.replace(',','')
                if numtest.replace('.','').replace('-','').isnumeric():
                    val = [float(numtest), '%']
                    cleanedValues.append(val)
                    continue
            
            if len(val) > 0 and val[0] in currencies:
                unit = val[0]
                numtest = val.replace(val[0],'')
                if len(numtest) > 0 and numtest[-1] in mults:
                    mult = numtest[-1]
                    numtest = numtest.replace(mult,'')
                    unit = mult + unit
                numtest = numtest.replace(',','')
                if numtest.replace('.','').isnumeric():
                    val = [float(numtest), unit]
                    cleanedValues.append(val)
                    continue
            
            if len(val) > 0 and val[-1] in mults:
                mult = val[-1]
                numtest = val.replace(mult,'')
                numtest = numtest.replace(',','')
                if numtest.replace('.','').isnumeric():
                    val = [float(numtest), mult]
                    cleanedValues.append(val)
                    continue
            
            if val.strip('-').replace('.','').replace(',','').isnumeric():
                val = float(val.replace(',',''))
                cleanedValues.append(val)
                continue

            cleanedValues.append(val)

        if len(cleanedValues) > 1:
            data[attrName] = cleanedValues
        elif len(cleanedValues) == 0:
            data[attrName] = None
        else:
            data[attrName] = cleanedValues[0]

    return data

# --- MULTI PROCS ---

def marketWatchStockPagesProc(letter):
    # logging.info('scraping MarketWatch pages from letter: %s' % letter)
    pages = None

    url = 'https://www.marketwatch.com/tools/markets/stocks/a-z/%s/1000' % letter
    r = DS.getRequest(url)
    if r == None:
        statusCode = 500
    else:
        statusCode = r.status_code

    if statusCode != 200:
        return [statusCode, pages]

    soup = BeautifulSoup(r.text, 'html.parser')

    paginations = soup.find_all('ul', class_='pagination')

    if len(paginations) == 1: return [statusCode, 1]

    pages = int(paginations[1].find_all('a')[-1].text.split('-')[-1])

    return [statusCode, pages]

def marketWatchFundPagesProc(letter):
    # logging.info('scraping MarketWatch pages from letter: %s' % letter)
    pages = None

    url = 'https://www.marketwatch.com/tools/markets/funds/a-z/%s/1000' % letter
    r = DS.getRequest(url)
    if r == None:
        statusCode = 500
    else:
        statusCode = r.status_code

    if statusCode != 200:
        return [statusCode, pages]

    soup = BeautifulSoup(r.text, 'html.parser')

    paginations = soup.find_all('ul', class_='pagination')

    if len(paginations) == 1: return [statusCode, 1]

    pages = int(paginations[1].find_all('a')[-1].text.split('-')[-1])

    return [statusCode, pages]

def marketWatchQuotesProc(url):
    data = []
    r = DS.getRequest(url)
    if r == None:
        statusCode = 500
    else:
        statusCode = r.status_code

    if statusCode != 200:
        return [statusCode, data]

    soup = BeautifulSoup(r.text, 'html.parser')

    tbody = soup.find('tbody')
    trs = tbody.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        symbol = tds[0].a.small.text[1:-1]
        name = tds[0].a.text.split(';')[0]
        country = tds[1].text
        exchange = tds[2].text
        sector = None
        if len(tds) > 3:
            sector = tds[3].text
        data.append('%s:%s:%s:%s:%s' % (symbol, exchange, country, name, sector))

    return [statusCode, data]

def quoteSearchOtherMSBS4Proc(quote):
    data = {}
    symbolSplits = quote.split(':')
    symbol = symbolSplits[0]
    areas = ['us', 'foreign']
    statusCode = None
    for area in areas:
        # https://www.morningstar.com/search/us-securities?query=VITAX
        # https://www.morningstar.com/search/foreign-securities?query=SNX
        url = 'https://www.morningstar.com/search/%s-securities?query=%s' % (area, symbol)
        r = DS.getRequest(url)
        if r == None:
            statusCode = 500
        else:
            statusCode = r.status_code
        
        if statusCode != 200: continue

        soup = BeautifulSoup(r.text, 'html.parser')

        empty = soup.find('div', class_='search-%s-securities__empty' % area)
        if empty != None: continue

        section = soup.find('section', class_='search-%s-securities' % area)
        if section == None: continue
        for div in section.find_all('div', class_='mdc-security-module search-%s-securities__hit' % area):
            href = div.a['href']
            if href.startswith('/search'): continue
            splits = href.split('/')
            foundSymbol = splits[3].upper()
            if foundSymbol != symbol: continue
            foundMIC = splits[2].upper()
            foundType = splits[1].upper()[:-1]
            foundQuote = '%s:%s' % (foundSymbol, foundMIC)
            if foundQuote == quote:
                data[foundQuote] = {'Type': foundType}
            else:
                foundName = div.a.text
                data[foundQuote] = {'Symbol': foundSymbol, 'MIC': foundMIC, 'Name': foundName, 'Type': foundType}

    return [statusCode, data]

def quoteDataMSBS4Proc(quote_type):
    data = {}
    splits = quote_type[0].split(':')
    symbol = splits[0]
    MIC = splits[1]
    stype = quote_type[1]
    if stype == 'None': return [200, data]

    url = 'https://www.morningstar.com/%sS/%s/%s/quote' % (stype, MIC, symbol)

    r = DS.getRequest(url)
    if r == None:
        statusCode = 500
    else:
        statusCode = r.status_code

    if statusCode != 200:
        return [statusCode, data]

    soup = BeautifulSoup(r.text, 'html.parser')

    morningStars = soup.find('span', class_='mdc-security-header__star-rating')
    if morningStars != None:
        data['Rating'] = int(morningStars['title'].split()[0])

    # Only FUND type pages have accessible non JavaScript data, sadly
    if stype == 'FUND':
        content = soup.find('div', {'class': 'fund-quote__data'})
        if content == None: return [statusCode, data]
        attrValues = {}
        for item in content.find_all('div', {'class': 'fund-quote__item'}):
            # get attribute names
            label = item.find('div', {'class': 'fund-quote__label'})
            attributes = label.text.strip()
            attributes = attributes.split(' / ')
            
            # get values
            value = item.find('div', {'class': 'fund-quote__value'})
            values = []
            if value != None:
                values = value.text.strip().split('/')
                for i in range(len(values)): values[i] = values[i].strip().replace('\t','').replace('\n',' ')
            else:
                values = item.find_all('span')[-1].text.strip().split('/')
                for i in range(len(values)): values[i] = values[i].strip()
            
            if len(attributes) != len(values): continue
            for i in range(len(attributes)):
                attrValues[attributes[i]] = values[i]
    
        for attr, val in cleanUpAttributes(attrValues).items():
            data[attr] = val

    return [statusCode, data]

def quoteDataMWBS4Proc(quote):
    data = {}
    symbolSplits = quote.split(':')
    symbol = symbolSplits[0]
    MIC = symbolSplits[1]
    # https://www.marketwatch.com/investing/fund/SNX?iso=XASX
    fundStart = 'https://www.marketwatch.com/investing/fund'
    url = '%s/%s?iso=%s' % (fundStart, symbol, MIC)

    r = DS.getRequest(url)
    if r == None:
        statusCode = 500
    else:
        statusCode = r.status_code

    if statusCode != 200:
        return [statusCode, data]
    
    # check redirection
    urlRedirect = r.url
    splits = urlRedirect.split('/')
    
    # quote not found
    if splits[3].startswith('search'):
        return [statusCode, data]
    
    data['Type'] = splits[4]

    soup = BeautifulSoup(r.text, 'html.parser')


    market = soup.find('span', {'class': 'company__market'})
    data['Market'] = None
    if market != None:
        data['Market'] = market.text.strip()
    
    subType = soup.find('ol', {'itemtype': 'http://schema.org/BreadcrumbList'})
    data['SubType'] = None
    if subType != None:
        elems = subType.find_all('li')
        data['SubType'] = elems[3].text.strip()

    primary = soup.find('div', {'class': 'region region--primary'})

    # Find Key Data
    foundData = {}
    for li in primary.find_all('li', {'class': 'kv__item'}):
        elems = []
        for elem in li.text.strip().split('\n'):
            if elem == '': continue
            elems.append(elem)
        foundData[elems[0]] = elems[1:]
    foundData = cleanUpAttributes(foundData)
    data['KeyData'] = foundData

    # Find data tables
    for table in primary.find_all('table'):
        classElems = table['class']
        header = None
        parent = table.parent
        while header == None:
            header = parent.header
            parent = parent.parent
        dataKey = header.text.strip().replace(' ', '').replace('.', '')
        if 'no-heading' in classElems:
            foundData = {}
            for tr in table.find_all('tr'):
                elems = []
                for elem in tr.text.strip().split('\n'):
                    if elem == '': continue
                    elems.append(elem)
                foundData[elems[0]] = elems[1:]
            foundData = cleanUpAttributes(foundData)
            if dataKey in data:
                for key, value in foundData.items(): data[dataKey][key] = value
            else:
                data[dataKey] = foundData
        else:
            attributes = []
            for th in table.thead.tr.find_all('th'):
                attributes.append(th.text.strip())
            tableRows = []
            for tr in table.tbody.find_all('tr'):
                elems = []
                for td in tr.find_all('td'):
                    elems.append(td.text.strip())
                tableRows.append(elems)
            foundRows = []
            for values in tableRows:
                foundData = {}
                valIdx = 0
                for attr in attributes:
                    foundData[attr] = values[valIdx]
                    valIdx += 1
                foundData = cleanUpAttributes(foundData)
                foundRows.append(foundData)
            if dataKey in data:
                data[dataKey] += foundRows
            else:
                data[dataKey] = foundRows

    return [statusCode, data]

def holdingsDataMWBS4Proc(quote):
    data = {}
    symbolSplits = quote.split(':')
    symbol = symbolSplits[0]
    MIC = symbolSplits[1]
    fundStart = 'https://www.marketwatch.com/investing/fund'
    url = '%s/%s/holdings?iso=%s' % (fundStart, symbol, MIC)

    r = DS.getRequest(url)
    if r == None:
        statusCode = 500
    else:
        statusCode = r.status_code

    if statusCode != 200:
        return [statusCode, data]
    
    # check redirection
    urlRedirect = r.url
    splits = urlRedirect.split('/')
    
    # quote not found
    if splits[3].startswith('search'):
        return [statusCode, data]
    
    soup = BeautifulSoup(r.text, 'html.parser')

    primary = soup.find('div', {'class': 'region region--primary'})

    # Find Key Data
    foundData = {}
    for li in primary.find_all('li', {'class': 'kv__item'}):
        elems = []
        for elem in li.text.strip().split('\n'):
            if elem == '': continue
            elems.append(elem)
        foundData[elems[0]] = elems[1:]
    foundData = cleanUpAttributes(foundData)
    data['KeyData'] = foundData

    # Find data tables
    for table in primary.find_all('table'):
        classElems = table['class']
        header = None
        parent = table.parent
        while header == None:
            header = parent.header
            parent = parent.parent
        dataKey = header.text.strip().replace(' ', '').replace('.', '')
        if 'no-heading' in classElems:
            foundData = {}
            for tr in table.find_all('tr'):
                elems = []
                for elem in tr.text.strip().split('\n'):
                    if elem == '': continue
                    elems.append(elem)
                foundData[elems[0]] = elems[1:]
            foundData = cleanUpAttributes(foundData)
            if dataKey in data:
                for key, value in foundData.items(): data[dataKey][key] = value
            else:
                data[dataKey] = foundData
        else:
            attributes = []
            for th in table.thead.tr.find_all('th'):
                attributes.append(th.text.strip())
            tableRows = []
            for tr in table.tbody.find_all('tr'):
                elems = []
                for td in tr.find_all('td'):
                    elems.append(td.text.strip())
                tableRows.append(elems)
            foundRows = []
            for values in tableRows:
                foundData = {}
                valIdx = 0
                for attr in attributes:
                    foundData[attr] = values[valIdx]
                    valIdx += 1
                foundData = cleanUpAttributes(foundData)
                foundRows.append(foundData)
            if dataKey in data:
                data[dataKey] += foundRows
            else:
                data[dataKey] = foundRows

    return [statusCode, data]

# --- MAIN SCRAPERS ---

def getBASEData(dataFileName):
    logging.info('Retrieving BASE Data')
    MData = DS.getData(dataFileName)
    BData = DS.getData('BASE_DATA_SCRAPED')
    
    for dataName in BData.keys():
        MData[dataName] = BData[dataName]
    
    if not DS.saveData(MData, dataFileName):
        logging.info('%s: Stop saving data and exit program' % dataFileName)
        exit(0)


def getQuotesMWBS4(dataFileName):
    logging.info('Retrieving all Quotes from MarketWatch')
    MData = DS.getData(dataFileName)
    dataName = 'MarketWatchQuotes'
    if not dataName in MData: MData[dataName] = {}

    # get page url links
    urls = []

    # scrape for alphabetic list pages
    letters = ['0-9']+[chr(x) for x in range(65, 91)]
    resultsS = DS.multiScrape(letters, marketWatchStockPagesProc)
    resultsF = DS.multiScrape(letters, marketWatchFundPagesProc)

    lIndex = 0
    for letter in letters:
        pages = resultsS[1][lIndex]
        if pages != None:
            for x in range(pages):
                urls.append('https://www.marketwatch.com/tools/markets/stocks/a-z/%s/%s' % (letter, (x+1)))
        pages = resultsF[1][lIndex]
        if pages != None:
            for x in range(pages):
                urls.append('https://www.marketwatch.com/tools/markets/funds/a-z/%s/%s' % (letter, (x+1)))
        lIndex = lIndex + 1

    # get quotes from MarketWatch pages
    results = DS.multiScrape(urls, marketWatchQuotesProc)
    if 403 in results[0]:
        logging.info('At least one page was blocked')

    # create quotes set
    for result in results[1]:
        for data in result:
            splits = data.split(':')
            symbol = splits[0]
            mic = splits[1]
            country = splits[2]
            name = splits[3]
            sector = splits[4]
            quote = '%s:%s' % (symbol, mic)
            if not quote in MData[dataName]:
                MData[dataName][quote] = {}
            MData[dataName][quote]['ScrapeTag'] = datetime.now()
            MData[dataName][quote]['Symbol'] = symbol
            MData[dataName][quote]['MIC'] = mic
            MData[dataName][quote]['Country'] = country
            MData[dataName][quote]['Name'] = name
            MData[dataName][quote]['Sector'] = sector

    logging.info('Total quotes in data: %s' % len(MData[dataName]))
    
    if not DS.saveData(MData, dataFileName):
        logging.info('%s: Stop saving data and exit program' % dataFileName)
        exit(0)

def addSimilarQuotesMSBS4(dataFileName):
    logging.info('Adding similar quotes from MorningStar Search to MarketWatch quotes')
    MData = DS.getData(dataFileName)
    dataName = 'MarketWatchQuotes'
    if not dataName in MData:
        logging.info('No existing quotes found in data !' % dataName)
        return
    
    quotes = list(MData[dataName].keys())
    mwQuoteCount = len(quotes)

    sTotal = len(quotes)
    for block in DS.makeMultiBlocks(quotes, 300):
        logging.info('Symbols search with MorningStar: %s' % sTotal)
        results = DS.multiScrape(block, quoteSearchOtherMSBS4Proc)

        sIndex = 0
        for data in results[1]:
            quote = block[sIndex]
            for fquote, fdata in data.items():
                if not fquote in MData[dataName]:
                    MData[dataName][fquote] = {}
                MData[dataName][fquote]['ScrapeTag'] = datetime.now()
                MData[dataName][fquote]['Type'] = None
                for attr, value in fdata.items():
                    MData[dataName][fquote][attr] = value
            sIndex += 1

        if not DS.saveData(MData, dataFileName):
            logging.info('%s: Stop saving data and exit program' % dataFileName)
            exit(0)
        
        sTotal = sTotal - len(block)
    
    addCount = len(MData[dataName].keys()) - mwQuoteCount
    logging.info('Added %s more quotes to %s' % (addCount, dataName))

def getQuoteDataMSBS4(dataFileName, seconds=0, minutes=0, hours=0, days=0):
    logging.info('Retrieving quote data from MorningStar')
    MData = DS.getData(dataFileName)
    dataName = 'MorningStarQuoteData'
    if not 'MarketWatchQuotes' in MData:
        logging.info('No MarketWatchQuotes found in data !')
        return
    if not dataName in MData: MData[dataName] = {}

    # find quotes that need to be checked  by MorningStar
    mwQuotes = set(MData['MarketWatchQuotes'].keys())
    msQuotes = set(MData[dataName].keys())
    msTodoQuotes = set(quotesNeedScrape(MData, dataName, seconds=seconds, minutes=minutes, hours=hours, days=days))
    toDoQuotes = mwQuotes.difference(msQuotes.difference(msTodoQuotes))

    quotes = []
    for quote in toDoQuotes:
        quotes.append([quote, MData['MarketWatchQuotes'][quote]['Type']])
    
    sTotal = len(quotes)
    for block in DS.makeMultiBlocks(quotes, 300):
        logging.info('Scrape quote data from MorningStar: %s' % sTotal)
        results = DS.multiScrape(block, quoteDataMSBS4Proc)

        sIndex = 0
        for data in results[1]:
            quote = block[sIndex][0]
            if not quote in MData[dataName]: MData[dataName][quote] = {}
            MData[dataName][quote]['ScrapeTag'] = datetime.now()
            for attr, value in data.items():
                MData[dataName][quote][attr] = value
            sIndex += 1

        if not DS.saveData(MData, dataFileName):
            logging.info('%s: Stop saving data and exit program' % dataFileName)
            exit(0)
        
        sTotal = sTotal - len(block)

def getQuoteDataMWBS4(dataFileName, seconds=0, minutes=0, hours=0, days=0):
    logging.info('Retrieving quote data from MarketWatch')
    MData = DS.getData(dataFileName)
    dataName = 'MarketWatchQuoteData'
    if not 'MarketWatchQuotes' in MData:
        logging.info('No MarketWatchQuotes found in data !')
        return
    if not dataName in MData: MData[dataName] = {}

    # update quotes that are in MarketWatchQuotes and that need to be updated
    allQuotes = set(MData['MarketWatchQuotes'].keys())
    mwQuotesNotNeedScrape = set(quotesNeedScrape(MData, dataName, needScrape=False, seconds=seconds, minutes=minutes, hours=hours, days=days))
    quotes = list(allQuotes.difference(mwQuotesNotNeedScrape))
    # quotes = ['VITAX:XNAS']
    # quotes = ['AAPL:XNAS']
    # quotes = ['NBI:XNAS']
    # quotes = ['SHOP:XBUE']
    # quotes = ['BANX:XNAS']

    sTotal = len(quotes)
    for block in DS.makeMultiBlocks(quotes, 40):
        logging.info('Quotes to scrape quote data with MarketWatch: %s' % sTotal)
        results = DS.multiScrape(block, quoteDataMWBS4Proc, retryStatusCode=403)

        sIndex = 0
        for data in results[1]:
            quote = block[sIndex]
            if not quote in MData[dataName]: MData[dataName][quote] = {}
            MData[dataName][quote]['ScrapeTag'] = datetime.now()
            for attr, value in data.items():
                MData[dataName][quote][attr] = value
            sIndex += 1

        if not DS.saveData(MData, dataFileName):
            logging.info('%s: Stop saving data and exit program' % dataFileName)
            exit(0)
        
        sTotal = sTotal - len(block)

def getHoldingsDataMWBS4(dataFileName, seconds=0, minutes=0, hours=0, days=0):
    logging.info('Retrieving holdings data from MarketWatch')
    MData = DS.getData(dataFileName)
    dataName = 'MarketWatchHoldingsData'
    if not 'MarketWatchQuoteData' in MData:
        logging.info('No MarketWatchQuoteData found in data !')
        return
    if not dataName in MData: MData[dataName] = {}

    # update fund quotes that are in MarketWatchQuoteData and that need to be updated
    allQuotes = set()
    for quote, data in MData['MarketWatchQuoteData'].items():
        if 'Type' in data and data['Type'] == 'fund':
            ftype = MData['MarketWatchQuotes'][quote]['Type']
            if ftype == 'FUND' or ftype == None:
                allQuotes.add(quote)
    mwhQuotesNotNeedScrape = set(quotesNeedScrape(MData, dataName, needScrape=False, seconds=seconds, minutes=minutes, hours=hours, days=days))
    quotes = list(allQuotes.difference(mwhQuotesNotNeedScrape))
    # quotes = ['VITAX:XNAS']
    # quotes = ['AAPL:XNAS']
    # quotes = ['NBI:XNAS']
    
    sTotal = len(quotes)
    for block in DS.makeMultiBlocks(quotes, 100):
        logging.info('Quotes to scrape holdings data with MarketWatch: %s' % sTotal)
        results = DS.multiScrape(block, holdingsDataMWBS4Proc, retryStatusCode=403)

        sIndex = 0
        for data in results[1]:
            quote = block[sIndex]
            if not quote in MData[dataName]: MData[dataName][quote] = {}
            MData[dataName][quote]['ScrapeTag'] = datetime.now()
            for attr, value in data.items():
                MData[dataName][quote][attr] = value
            sIndex += 1

        if not DS.saveData(MData, dataFileName):
            logging.info('%s: Stop saving data and exit program' % dataFileName)
            exit(0)
        
        sTotal = sTotal - len(block)

if __name__ == "__main__":
    DS.setupLogging('MarketDataScrape.log', timed=True, new=False)
    scrapedFileName = 'M_DATA_SCRAPED'
    historyUpdateDays = 10

    # # copy Base Data to MMarket Data
    # getBASEData(scrapedFileName)

    # # create MData by retrieving quotes from MarketWatch
    # # 61476 quotes = 00:00:18
    # getQuotesMWBS4(scrapedFileName)

    # # Search for more quotes through MorningStar and add type
    # # 102699 quotes = 01:58:21
    # addSimilarQuotesMSBS4(scrapedFileName)

    # # get quote data from MorningStar
    # # 107428 quotes = 01:35:15
    # getQuoteDataMSBS4(scrapedFileName, days=historyUpdateDays)

    # # get quote data from MarketWatch
    # # 133313 quotes = 24:03:13
    # getQuoteDataMWBS4(scrapedFileName, days=historyUpdateDays)
    
    # # get quote data from MarketWatch
    # # 30600 quotes = 06:54:42
    # getHoldingsDataMWBS4(scrapedFileName, days=historyUpdateDays)
