import DataScrape as DS
import logging

def fixValue(attr, subData, attributes):
    currencies = [
        'NT$','HK$','Z$','R$','$',
        '£','₹','€','¥','₩','৳','₺','₪','₸','kr.','kr','kn','₫','zł','₱','₦','₵','ден','дин.','КМ','₴',
        'ج.م.\u200f','د.ا.\u200f','د.ت.\u200f','د.ك.\u200f','د.م.\u200f','ر.ع.\u200f',
        'د.ب.\u200f','ر.ق.\u200f','د.إ.\u200f','ر.س.\u200f','د.ع.\u200f',
        'RM','MK','USh','Sh','CFA','ZK','Ksh','Ft','Rs','Rp','S/','Bs.S','฿','රු.','лв.','CHF','Kč','R','P','c','p']
    mults = 'KMBTp'
    if type(subData) == str and attr != 'Name' and attr != 'Symbol':
        for currency in currencies:
            if currency in subData:
                unit = currency
                numtest = subData.replace(unit,'')
                if len(numtest) > 0 and numtest[-1] in mults:
                    mult = numtest[-1]
                    numtest = numtest.replace(mult,'')
                    unit = mult + unit
                numtest = numtest.replace(',','')
                numTestDigits = numtest.replace('.','')
                if numTestDigits == '': break
                if numTestDigits[0] == '-': numTestDigits = numTestDigits[1:]
                if numTestDigits.isnumeric():
                    logging.info('')
                    logging.info('%s: %s' % (attr, subData))
                    subData = [float(numtest), unit]
                    logging.info('%s: %s' % (attr, subData))
                    attributes.add(attr)
                    return subData
                break
    return subData

def dictRecurse(data,newData,attributes):
    if type(data) == dict:
        for attr, subData in data.items():
            if type(subData) == dict:
                newData[attr] = {}
                dictRecurse(subData,newData[attr],attributes)
            elif type(subData) == list:
                newData[attr] = []
                dictRecurse(subData,newData[attr],attributes)
            else:
                newData[attr] = fixValue(attr, subData, attributes)
    elif type(data) == list:
        for subData in data:
            if type(subData) == dict:
                newData.append({})
                dictRecurse(subData,newData[-1],attributes)
            elif type(subData) == list:
                newData.append([])
                dictRecurse(subData,newData[-1],attributes)
            else:
                newData.append(fixValue('blah', subData, attributes))

if __name__ == "__main__":
    DS.setupLogging('fixCurrency.log', timed=False, new=True)
    scrapedFileName = 'M_DATA_SCRAPED'
    MSData = DS.getData(scrapedFileName)

    attributes = set()
    NewMSData = {}
    dictRecurse(MSData, NewMSData, attributes)
    print(attributes)

    DS.saveData(NewMSData, 'M_DATA_SCRAPED_FIXED')
