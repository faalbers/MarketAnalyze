import DataScrape as DS
from bs4 import BeautifulSoup
import logging

# --- TOOLS ---

def cleanUpAttributes(attributes, capitalize=True, upper=False):
    data = {}
    for attr, value in attributes.items():
        attrName = ''
        currencies = '$£₹€¥₩'
        mults = 'KMBTp'
        
        for attrPart in attr.split():
            if attrPart.startswith('('): continue
            elif attrPart.startswith('%'): continue
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

        values = [value]
        if type(value) == list:
            values = value
        cleanedValues = []
        for val in values:
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

def MICDataBS4Proc(iso):
    data = {}

    url = 'https://www.iotafinance.com/en/Detail-view-MIC-code-%s.html' % iso

    r = DS.getRequest(url, maxRetries=1)
    if r == None:
        statusCode = 500
    else:
        statusCode = r.status_code

    if statusCode != 200:
        return [statusCode, data]
    
    soup = BeautifulSoup(r.text, 'html.parser')

    section = soup.find('section', class_='ml0 mt-10')
    if section == None: return [statusCode, data]
    for content in section.contents:
        if content == None: continue
        splits = content.text.strip().split('\n')
        if splits == ['']: continue
        data[splits[0].replace(':', '')] = splits[2].strip()
        if len(splits) >= 6:
            data[splits[3].replace(':', '')] = splits[5].strip()

    if '' in data: data.pop('')

    return [statusCode, data]

# --- MAIN SCRAPERS ---

def getCISOBS4(dataFileName):
    logging.info('Retrieving CISO')
    BData = DS.getData(dataFileName)
    if not 'CISOs' in BData: BData['CISOs'] = {}

    url = 'https://www.iban.com/country-codes'
    r = DS.getRequest(url)
    if r == None:
        statusCode = 500
    else:
        statusCode = r.status_code

    if statusCode != 200:
        logging.info('Could not find CISO !')
        return
    
    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.find('table', {'id': 'myTable'})

    for tr in table.find_all('tr'):
        elements = tr.text.split('\n')
        if elements[1] == 'Country': continue
        BData['CISOs'][elements[2]] = elements[1]
    
    # adding unknown
    BData['CISOs']['XX'] = 'Unknown'

    if not DS.saveData(BData, dataFileName):
        logging.info('%s: Stop saving data and exit program' % dataFileName)
        exit(0)

def getMICBS4(dataFileName):
    logging.info('Retrieving MIC')
    BData = DS.getData(dataFileName)
    if not 'MICs' in BData: BData['MICs'] = {}

    url = 'https://www.iotafinance.com/en/ISO-10383-Market-Identification-Codes-MIC.html'
    r = DS.getRequest(url)
    if r == None:
        statusCode = 500
    else:
        statusCode = r.status_code

    if statusCode != 200:
        logging.info('Could not find Stock MIC !')
        return
    
    soup = BeautifulSoup(r.text, 'html.parser')

    for element in soup.find_all('li', {'class': 'mic-list-element'}):
        names = element.find('div', {'class': 'row'}).find_all('div')
        BData['MICs'][names[0].text.strip()] = {}
        BData['MICs'][names[0].text.strip()]['Name'] = names[2].text.strip()

    # add missing MICs
    BData['MICs']['XJAS'] = {}
    BData['MICs']['XJAS']['Name'] = 'Tokyo Stock Exchange Jasdaq'
    BData['MICs']['XVTX'] = {}
    BData['MICs']['XVTX']['Name'] = 'SIX Swiss Exchange - Blue Chips Segment'

    if not DS.saveData(BData, dataFileName):
        logging.info('%s: Stop saving data and exit program' % dataFileName)
        exit(0)

def getMICDataBS4(dataFileName, seconds=0, minutes=0, hours=0, days=0):
    logging.info('Retrieving MIC Data')
    BData = DS.getData(dataFileName)
    if not 'MICs' in BData:
        logging.info('No MIC in data !')
        return

    MICs = list(BData['MICs'].keys())

    sTotal = len(MICs)

    for block in DS.makeMultiBlocks(MICs, 50):
        logging.info('Get MIC Data: %s' % sTotal)
        MICData = DS.multiScrape(block, MICDataBS4Proc, retryStatusCode=500)

        sIndex = 0
        for data in MICData[1]:
            iso = block[sIndex]
            for attr, value in cleanUpAttributes(data).items():
                # skip MarketName, it already exists
                if attr == 'MarketName':
                    attr = 'Name'
                # fix values with % in name
                if type(value) == list:
                    value = [str(v) for v in value]
                    value = ' '.join(value)
                
                BData['MICs'][iso][attr] = value

            sIndex += 1
        
        sTotal = sTotal - len(block)

    # Ad more
    BData['MICs']['GREY'] = {
        'Acronym': '---',
        'Comment': '---',
        'Country': 'US - United States of America',
        'CreationDate': '---',
        'LastChange': '---',
        'MarketCategory': 'Not Specified (NSPD)',
        'Mic': 'GREY',
        'MicCodeType': 'Market segment MIC',
        'Name': 'OTC Pink Market Grey Market',
        'OperatingMic': 'OTCM',
        'Status': None,
        'WebSite': None}

    if not DS.saveData(BData, dataFileName):
        logging.info('%s: Stop saving data and exit program' % dataFileName)
        exit(0)

def getMICCISOLinks(dataFileName):
    logging.info('Create MIC <-> CISO links')
    BData = DS.getData(dataFileName)
    if not 'MICs' in BData:
        logging.info('No MIC in data !')
        return
    if not 'CISOs' in BData:
        logging.info('No CISO Codes in data !')
        return
    BData['MICToCISO'] = {}
    for MIC , data in BData['MICs'].items():
        if 'Country' in data:
            CISO = data['Country'].split(' - ')[0]
            if not MIC in BData['MICToCISO']:
                BData['MICToCISO'][MIC] = set()
            BData['MICToCISO'][MIC].add(CISO)
            if not CISO in BData['CISOs']:
                logging.info('Missing CISO: %s' % data['Country'])
    BData['CISOToMIC'] = {}
    for MIC , CISOSet in BData['MICToCISO'].items():
        for CISO in CISOSet:
            if not CISO in BData['CISOToMIC']:
                BData['CISOToMIC'][CISO] = set()
            BData['CISOToMIC'][CISO].add(MIC)
    if not DS.saveData(BData, dataFileName):
        logging.info('%s: Stop saving data and exit program' % dataFileName)
        exit(0)

if __name__ == "__main__":
    scrapedFileName = 'BASE_DATA_SCRAPED'
    DS.setupLogging('BASEDataScrape.log', timed=True, new=True)

    # retrieving CISO codes
    # 00:00:00
    getCISOBS4(scrapedFileName)

    # retrieving MIC
    # 00:00:00
    getMICBS4(scrapedFileName)

    # retrieving MIC data
    # 2305 MICs = 00:10:04 (blocked)
    getMICDataBS4(scrapedFileName)

    # Create MIC to CISO and CISO to MIC link data
    # 00:00:00
    getMICCISOLinks(scrapedFileName)

