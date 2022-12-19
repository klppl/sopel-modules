#!/usr/bin/python
# -*- coding: utf-8 -*-
# Module for sopel. Will fetch html from avanza.se and display latest data in your IRC channel.
# https://github.com/senilio/sopel

import sys
import os
import requests, json
import re
import locale

locale.setlocale(locale.LC_ALL, 'sv_SE')

def avanzaStringToFloat(inputString):
    try:
        f = float(inputString.replace(',', '.'))
    except:
        f = 0.0
    return f

def avanzaStringToInt(inputString):
    try:
        return int(re.sub('[^0-9]', '', inputString))
    except ValueError:
        return 0
    
def getTickerInfoAvanza(ticker, quick=False):
    base_url = u'https://www.avanza.se/ab/component/orderbook_search/?query={0}&collection=STOCK&onlyTradable=false&pageType=stock&orderTypeView='

    r = requests.get(base_url.format(ticker))
    if not r.status_code == 200:
        return None

    response = r.text
    data = json.loads(response)
    if not data:
        return None
    firstObj = data[0]
    info_url = firstObj.get('url')

    stockUrl = 'https://www.avanza.se{0}'.format(info_url)
    r = requests.get(stockUrl)

    res = {}
    res['url'] = stockUrl
    res['urlAbout'] = stockUrl.replace('om-aktien', 'om-bolaget')

    if quick is True:
        return res  

    lastPriceUpdate = re.findall('<span class="lastPrice SText bold"><span class="pushBox roundCorners3" data-e2e="quoteLastPrice" title="Senast uppdaterad: ([0-9:]+)">([,\d]+)</span></span>', r.text)
    res['lastUpdate'] = lastPriceUpdate[0][0]
    res['lastPrice'] = avanzaStringToFloat(lastPriceUpdate[0][1])

    dataOrderbookName = re.findall('data-orderbook_name="(.*)"', r.text)
    res['orderBookName'] = dataOrderbookName[0]

    dataOrderbookCurrency = re.findall('data-orderbook_currency="(.*)"', r.text)
    res['orderBookCurrency'] = dataOrderbookCurrency[0]
    
    changePercent = re.findall('<span class="changePercent SText bold \w+">(.*)\s+\%</span>', r.text)
    res['changePercent'] = avanzaStringToFloat(changePercent[0])
     
    owners = re.findall('hos Avanza</span></dt>\r\n.*<dd><span>(.*)</span></dd>', r.text)
    res['numOwners'] = avanzaStringToInt(owners[0])

    try:
        networth = re.findall('rde MSEK</span></dt>\r\n.*<dd><span>(.*)</span>', r.text)
        res['networth'] = networth[0]
    except:
        res['networth'] = None

    peTal = re.findall('P/E-tal</span></dt>\r\n.*<dd><span>(.*)</span>', r.text)
    res['peTal'] = peTal[0]

    highestPrice = re.findall('<span class="highestPrice SText bold">(.*)</span>', r.text)
    res['highestPrice'] = avanzaStringToFloat(highestPrice[0])

    lowestPrice = re.findall('<span class="lowestPrice SText bold">(.*)</span>', r.text)
    res['lowestPrice'] = avanzaStringToFloat(lowestPrice[0])

    totalVolumeTraded = re.findall('<span class="totalVolumeTraded SText bold">(.*)</span>', r.text)
    res['totalVolumeTraded'] = avanzaStringToInt(totalVolumeTraded[0])

    ticker = re.findall('data-short_name="(.*)"', r.text)
    res['ticker'] = ticker[0]

    try:
        totalValueTraded = re.findall('<span class="totalValueTraded">(.*)</span>', r.text)
        res['totalValueTraded'] = avanzaStringToInt(totalValueTraded[0])
    except:
        res['totalValueTraded'] = None

    return res


def getTickerInfoAvanzaFund(ticker, quick=False):
    base_url = u'https://www.avanza.se/ab/component/orderbook_search/?query={0}&collection=FUND&onlyTradable=false&pageType=fund&orderTypeView='

    r = requests.get(base_url.format(ticker))
    if not r.status_code == 200:
        return None

    response = r.text
    data = json.loads(response)
    if not data:
        return None
    firstObj = data[0]
    info_url = firstObj.get('url')

    fundUrl = 'https://www.avanza.se{0}'.format(info_url)
    r = requests.get(fundUrl)

    res = {}
    res['url'] = fundUrl
    #res['urlAbout'] = fundUrl.replace('om-aktien', 'om-bolaget')

    if quick is True:
        return res  

    lastPrice = re.findall('itemprop="price" content="(.*)"', r.text)
    res['lastPrice'] = avanzaStringToFloat(lastPrice[0])

    dataOrderbookName = re.findall('data-orderbook_name="(.*)"', r.text)
    res['orderBookName'] = dataOrderbookName[0]

    dataOrderbookCurrency = re.findall('data-orderbook_currency="(.*)"', r.text)
    res['orderBookCurrency'] = dataOrderbookCurrency[0]
    
    morningstarRating = re.findall('<dt><span>Morningstar rating</span></dt>\r\n.*<span>(.*)</span>', r.text)
    res['rating'] = morningstarRating[0].split(' ')[0]

    fundStarted = re.findall('<dt><span>Fondens startdatum</span></dt>\r\n.*<span>(.*)</span>', r.text)
    res['fundStarted'] = fundStarted[0]

    changePercentDay = re.findall('<td class="tLeft">En dag</td>\r\n.*\r\n.*<td class="last">(.*)</td>', r.text)
    res['changePercentDay'] = avanzaStringToFloat(changePercentDay[0])
     
    changePercentWeek = re.findall('<td class="tLeft">En vecka</td>\r\n.*\r\n.*<td class="last">(.*)</td>', r.text)
    res['changePercentWeek'] = avanzaStringToFloat(changePercentWeek[0])

    changePercentMonth = re.findall('<td class="tLeft">En m.nad</td>\r\n.*\r\n.*<td class="last">(.*)</td>', r.text)
    res['changePercentMonth'] = avanzaStringToFloat(changePercentMonth[0])

    changePercentThreeMonths = re.findall('<td class="tLeft">Tre m.nader</td>\r\n.*\r\n.*<td class="last">(.*)</td>', r.text)
    res['changePercentThreeMonths'] = avanzaStringToFloat(changePercentThreeMonths[0])

    changePercentSixMonths = re.findall('<td class="tLeft">Sex m.nader</td>\r\n.*\r\n.*<td class="last">(.*)</td>', r.text)
    res['changePercentSixMonths'] = avanzaStringToFloat(changePercentSixMonths[0])

    changePercentOneYear = re.findall('<td class="tLeft">Ett .r</td>\r\n.*\r\n.*<td class="last">(.*)</td>', r.text)
    res['changePercentOneYear'] = avanzaStringToFloat(changePercentOneYear[0])

    changePercentThreeYears = re.findall('<td class="tLeft">Tre .r</td>\r\n.*\r\n.*<td class="last">(.*)</td>', r.text)
    res['changePercentThreeYears'] = avanzaStringToFloat(changePercentThreeYears[0])

    changePercentFiveYears = re.findall('<td class="tLeft">Fem .r</td>\r\n.*\r\n.*<td class="last">(.*)</td>', r.text)
    res['changePercentFiveYears'] = avanzaStringToFloat(changePercentFiveYears[0])

    changePercentTenYears = re.findall('<td class="tLeft">Fem .r</td>\r\n.*\r\n.*<td class="last">(.*)</td>', r.text)
    res['changePercentTenYears'] = avanzaStringToFloat(changePercentTenYears[0])

    updated = re.findall('Historik per den (\d+-\d+-\d+)', r.text)
    res['updated'] = updated[0]

    ppmNumber = re.findall('<dt><span>PPM-nummer</span></dt>\r\n.*<span>(.*)</span>', r.text)
    res['ppm'] = ppmNumber[0]
    
    return res

def getOutput(res):
    if res['changePercent'] < 0:
        change = '{0:n}%'.format(res['changePercent'])
        try:
            change = formatting.color(change, formatting.colors.RED)
        except:
            pass
    elif res['changePercent'] > 0:
        change = '{0:+n}%'.format(res['changePercent'])
        try:
            change = formatting.color(change, formatting.colors.GREEN)
        except:
            pass
    else:
        change = "0.00%"


    msg = u'{0} ({1}) : {1}: {2} {3} ({4}) '.format(res['orderBookName'], res['ticker'], res['lastPrice'], res['orderBookCurrency'], change)
#    msg = u'^B{0} ({1})^B: {2} {3} ({4}). '.format(res['orderBookName'], res['ticker'], locale.currency(res['lastPrice'], symbol=False), res['orderBookCurrency'], change)
#   msg += u'^BDay range:^B {0}-{1}. '.format(locale.currency(res['lowestPrice'], symbol=False), locale.currency(res['highestPrice'], symbol=False))
    msg += u'Day range: {0}-{1}. '.format(res['lowestPrice'], res['highestPrice'])
    msg += u'Day volume: {0:n}. '.format(res['totalVolumeTraded'])
    if res['totalValueTraded']:
        msg += u'Day revenue: {0:n} {1}. '.format(res['totalValueTraded'], res['orderBookCurrency'])
    if res['networth']:
        msg += u'Net worth: {0} MSEK. '.format(res['networth'])
    if res['peTal'] != '-':
        msg += u'P/E: {0}. '.format(res['peTal'])
    msg += u'Shareholders: {0:n}. (Updated: {1})'.format(res['numOwners'], res['lastUpdate'])
    return msg

def percentageColor(pct):
    if pct < 0:
        change = '{0:n}%'.format(pct)
        try:
            change = formatting.color(change, formatting.colors.RED)
        except:
            pass

    elif pct > 0:
        change = '{0:+n}%'.format(pct)
        try:
            change = formatting.color(change, formatting.colors.GREEN)
        except:
            pass

    elif pct == 0:
        change = "0.00%"

    else:
        change = ''

    return change


def getOutputFund(res):
    msg = u'^B{0}^B: {1} {2}. '.format(res['orderBookName'], res['lastPrice'], res['orderBookCurrency'])
#    msg = u'^B{0}^B: {1} {2}. '.format(res['orderBookName'], locale.currency(res['lastPrice'], symbol=False), res['orderBookCurrency'])

    msg += u'1W: {0}. '.format(percentageColor(res['changePercentWeek']), symbol=False)
    msg += u'1M: {0}. '.format(percentageColor(res['changePercentMonth']), symbol=False)
    msg += u'6M: {0}. '.format(percentageColor(res['changePercentSixMonths']), symbol=False)
    msg += u'1Y: {0}. '.format(percentageColor(res['changePercentOneYear']), symbol=False)
    msg += u'3Y: {0}. '.format(percentageColor(res['changePercentThreeYears']), symbol=False)
    msg += u'5Y: {0}. '.format(percentageColor(res['changePercentFiveYears']), symbol=False)
    msg += u'10Y: {0}. '.format(percentageColor(res['changePercentTenYears']), symbol=False)
    if res['ppm'] != '-':    msg += u'PPM: {0}. '.format(res['ppm'], symbol=False)
    msg += u'Started: {0}. '.format(res['fundStarted'], symbol=False)
    if res['rating'] != '-': msg += u'Rating: {0}. '.format(res['rating'], symbol=False)
    msg += u'Last update: {0}. '.format(res['updated'], symbol=False)
    return msg

def getAvanzaReportDates(ticker):
    da = getTickerInfoAvanza(ticker, quick=True)
    if da is None:
        return da

    r = requests.get(da['urlAbout'])

    t = re.findall('<h3 class="bold">Kommande(.*?)<h3 class="bold">Tidigare', r.text ,re.DOTALL|re.MULTILINE)
    output = []
    if t:
        da = re.sub('\s{2,}', '', t[0])
        info = re.findall('<dt><span>([-\w]+?)</span></dt><dd><span>(.*?)</span></dd>', da, re.DOTALL|re.MULTILINE)

        for i in info:
            output.append(i[0] + ' : ' + re.sub('<.*?>', '  ', i[1]))

    return output

if __name__ == "__main__":
    # test parsing function without sopel bot
    tickers = 'ASTG,hennes'
    tickers = tickers.split(',')
    for t in tickers:
        try:
            da = getTickerInfoAvanza(t)
            if da is None:
                raise TypeError('I need a valid ticker name')
            msg = getOutput(da)
            print (msg)
        except (IndexError, TypeError) as e:
            print (e.message)
#
#    try:
#        da = getAvanzaReportDates('telia')
#        if da is None:
#            raise TypeError('I need a valid ticker name')
#        for r in da[:5]:
#            print r
#    except (IndexError, TypeError) as e:
#        print e.message
    
    sys.exit(0)

from sopel import module
from sopel import formatting

@module.commands('a', 'avanza', 'aza', 'ava', 'az')
def avanza(bot, trigger):
    ticker = trigger.group(2)
    if not ticker:
        ticker = '123'

    tickers = ticker.split(',')
    for ticker in tickers:
        try:
            res = getTickerInfoAvanza(ticker)
            if res is None:
                raise TypeError('I need a valid ticker name. My lady.')
            msg = getOutput(res)
            bot.say(msg)

        except (IndexError, TypeError) as e:
            bot.say('I need a valid ticker name. My lady.')

@module.commands('af', 'azf', 'fund', 'fond', 'ppm')
def avanzafunds(bot, trigger):
    ticker = trigger.group(2)
    if not ticker:
        ticker = '123'

    tickers = ticker.split(',')
    for ticker in tickers:
        try:
            res = getTickerInfoAvanzaFund(ticker)
            if res is None:
                raise TypeError('I need a valid ticker name. My lady.')
            msg = getOutputFund(res)
            bot.say(msg)

        except (IndexError, TypeError) as e:
            bot.say('I need a valid ticker name. My lady.')

@module.commands('azr')
def avanzar(bot, trigger):
    try:
        ticker = trigger.group(2)
        if not ticker:
            ticker = '123'

        res = getAvanzaReportDates(ticker)
        if res is None:
            raise TypeError('I need a valid ticker name.')
        for r in res[:5]:
            bot.say(r)

    except (IndexError, TypeError) as e:
        bot.say(e.message)


#### CUSTOM TICKERS ####

@module.commands('felia', 'telia')
def felia(bot, trigger):
    ticker = trigger.group(2)
    if not ticker:
        ticker = 'telia'
        res = getTickerInfoAvanza(ticker)
        msg = getOutput(res)
        bot.say(msg)


@module.commands('elbil', 'tesla', '🚙', '🚗')
def elbil(bot, trigger):
    ticker = trigger.group(2)
    if not ticker:
        ticker = 'tesla'
        res = getTickerInfoAvanza(ticker)
        msg = getOutput(res)
        bot.say(msg)

@module.commands('👆', 'finger')
def finger(bot, trigger):
    ticker = trigger.group(2)
    if not ticker:
        ticker = 'Fingerprint Cards B'
        res = getTickerInfoAvanza(ticker)
        msg = getOutput(res)
        bot.say(msg)


