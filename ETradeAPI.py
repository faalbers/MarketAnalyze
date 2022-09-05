import DataScrape as DS
from rauth import OAuth1Service
import webbrowser, logging, json, time, configparser
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count

def getSession():
    config = configparser.ConfigParser()
    config.read('ETrade.ini')

    etrade = OAuth1Service(
        name="etrade",
        consumer_key=config["DEFAULT"]["CONSUMER_KEY"],
        consumer_secret=config["DEFAULT"]["CONSUMER_SECRET"],
        request_token_url="https://api.etrade.com/oauth/request_token",
        access_token_url="https://api.etrade.com/oauth/access_token",
        authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
        base_url='https://api.etrade.com')
    
    request_token, request_token_secret = etrade.get_request_token(
        params={"oauth_callback": "oob", "format": "json"})

    authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
    webbrowser.open(authorize_url)
    text_code = input("Please accept agreement and enter text code from browser: ")

    session = etrade.get_auth_session(request_token,
                                    request_token_secret,
                                    params={"oauth_verifier": text_code})
    
    return session

def getQuoteProc(entries):
    variables, session = entries
    symbol = variables[0]
    detailFlag = variables[1]
    log = variables[2]

    # if log:
    #     logging.info(entries)

    url = 'https://api.etrade.com/v1/market/quote/' + symbol + '.json'
    headers = {'Connection': 'close'}
    params = {}
    if detailFlag != '':
        params['detailFlag'] = detailFlag
    response = session.get(url, params=params, headers=headers)

    return json.loads(response.text)

def unblockSleep(poolVariable, getProc):
    sleepTime = 0
    sleepTimeMax = 600
    timeIncrement = 15
    while True:
        result = getProc(poolVariable)
        if 'Error' in result and result['Error']['message'] == 'Number of requests exceeded the rate limit set':
            sleepTime += timeIncrement
            if sleepTime >= sleepTimeMax:
                return None
            time.sleep(timeIncrement)
        else:
            break
    return sleepTime

def multiGet(poolVariables, session, getProc):
    # fill temporary empty data list
    data = [None] * len(poolVariables)

    # create index list to pool variables
    pVarIndices = list(range(len(poolVariables)))

    cpuCount = cpu_count() * 4
    multiPool = Pool(cpuCount)
    while len(pVarIndices) != 0:
        # check index list of pool variables that still need to be done
        # and create current poolVariables
        pVarsRetry = [(poolVariables[i], session) for i in pVarIndices]

        # run multi getQuote on them
        results = multiPool.map(getProc, pVarsRetry)

        pVarIndex = 0
        pVarBlockedIndices = []
        for result in results:
            if 'Error' in result and result['Error']['message'] == 'Number of requests exceeded the rate limit set':
                    # add to retry pool
                    pVarBlockedIndices.append(pVarIndices[pVarIndex])
            else:
                data[pVarIndices[pVarIndex]] = result
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
            logging.info('retrying poolVariable: %s' % poolVariables[pVarIndices[0]])
            sleepTime = unblockSleep((poolVariables[pVarIndices[0]], session), getProc)
            if sleepTime == None:
                logging.info('tried too long, skipping symbol: %s' % poolVariables[pVarIndices[0]])
                pVarIndices.remove(pVarIndices[0])
            else:
                logging.info('tried for %s seconds' % sleepTime)
    return data

def multiQuotes(symbols, session, detailFlag='', log=False):
    data = []
    poolVariables = [[symbol, detailFlag, log] for symbol in symbols]
    results = multiGet(poolVariables, session, getQuoteProc)

    for result in results:
        if 'QuoteResponse' in result and 'QuoteData' in result['QuoteResponse']:
            data.append(result['QuoteResponse']['QuoteData'][0])
        else:
            data.append({})
    
    return data

def endSession(session):
    url = 'https://api.etrade.com/oauth/revoke_access_token'
    session.get(url)
    