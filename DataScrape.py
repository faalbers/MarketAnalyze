import logging, pickle, time, requests
from os.path import exists
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count

def setupLogging(filename, new=True, timed=False):
    filemode = 'a'
    if new: filemode = 'w'
    formatStr = '%(message)s'
    datefmtStr = '%m/%d/%Y %I:%M:%S %p'
    if timed:
        formatStr = '%(asctime)s: %(message)s'
    logging.basicConfig(
        filename=filename, encoding='utf-8', level=logging.INFO, filemode=filemode,
        format=formatStr, datefmt=datefmtStr
        )

def getData(fileName):
    dataFile = '%s.pickle' % fileName
    data = {}
    if exists(dataFile):
        with open(dataFile, 'rb') as f:
            data = pickle.load(f)
    else:
        logging.info('data file not found: %s' % dataFile)
    return data

def saveData(data, fileName):
    with open('SaveData.check', 'r') as f:
        if len(f.read()) > 0:
            return False
    dataFile = '%s.pickle' % fileName
    with open(dataFile, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    return True

# chop data list into block lists
def makeMultiBlocks(data, blockSize):
    multiBlocks = []
    dataCopy = data.copy()
    dataSize = len(dataCopy)
    while(dataSize > 0):
        last = dataSize
        if last > blockSize: last = blockSize

        multiBlocks.append(dataCopy[:last])

        dataCopy = dataCopy[last:]
        dataSize = len(dataCopy)

    return multiBlocks

def getRequest(url, maxRetries=10):
    headers =  {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
    statusCode = 500
    retries = 0
    r = None
    while(retries <= maxRetries and statusCode == 500):
        retries = retries + 1
        try:
            r = requests.get(url, headers=headers)
            statusCode = r.status_code
        except:
            r = None
    return r    

def unblockSleep(poolVariable, scrapeProc, retryStatusCode):
    sleepTime = 0
    sleepTimeMax = 600
    timeIncrement = 15
    blocked = True
    while blocked:
        data = scrapeProc(poolVariable)
        if data[0] != retryStatusCode: break
        sleepTime += timeIncrement
        if sleepTime >= sleepTimeMax:
            return None
        time.sleep(timeIncrement)
    return sleepTime

def multiScrape(poolVariables, scrapeProc, retryStatusCode=None):
    # fill temporary empty data list
    data = [ [None] * len(poolVariables), [None] * len(poolVariables)]

    # create index list to pool variables
    pVarIndices = list(range(len(poolVariables)))

    cpuCount = cpu_count() * 4
    multiPool = Pool(cpuCount)
    while len(pVarIndices) != 0:
        # check index list of pool variables that still need to be done
        # and create current poolVariables
        pVarsRetry = [poolVariables[i] for i in pVarIndices]

        # run multi scrape on them
        results = multiPool.map(scrapeProc, pVarsRetry)

        # create lists of statusCodes and data
        rStatusCodes = []
        rData = []
        for result in results:
            rStatusCodes.append(result[0])
            rData.append(result[1])

        # go through status codes and find retry codes
        # retrieve the retry poolVariable indices 
        pVarIndex = 0
        pVarBlockedIndices = []
        for statusCode in rStatusCodes:
            if retryStatusCode != None and statusCode == retryStatusCode:
                # add to retry pool
                pVarBlockedIndices.append(pVarIndices[pVarIndex])
            else:
                # fill in done data
                data[0][pVarIndices[pVarIndex]] = statusCode
                data[1][pVarIndices[pVarIndex]] = rData[pVarIndex]
            pVarIndex += 1
        
        # if none need to be retried empty the indices list 
        if len(pVarBlockedIndices) == 0:
            # if none need to be retried empty the indices list 
            pVarIndices = []
        else:
            # setup next indices list and do a sleep before retry
            pVarIndices = pVarBlockedIndices

            # keep retrying first blocked one till status code isn't blocked
            logging.info('%s blocked attempts' % len(pVarBlockedIndices))
            # logging.info('retrying poolVariable: %s' % pVarsRetry[pVarIndices[0]])
            logging.info('retrying poolVariable: %s' % poolVariables[pVarIndices[0]])
            # sleepTime = unblockSleep(pVarsRetry[pVarIndices[0]], scrapeProc, retryStatusCode)
            sleepTime = unblockSleep(poolVariables[pVarIndices[0]], scrapeProc, retryStatusCode)
            if sleepTime == None:
                # logging.info('tried too long, skipping symbol: %s' % pVarsRetry[pVarIndices[0]])
                logging.info('tried too long, skipping symbol: %s' % poolVariables[pVarIndices[0]])
                data[0][pVarIndices[0]] = 200
                data[1][pVarIndices[0]] = {}
                pVarIndices.remove(pVarIndices[0])
            else:
                logging.info('tried for %s seconds' % sleepTime)
    return data
