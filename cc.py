import urllib.request
import json
import re

def CurrencyConverter(amount, from_currency, to_currency):
    APIURL = "https://api.exchangeratesapi.io/latest"

    rates = {}

    req = urllib.request.Request(APIURL, headers={'User-Agent': 'Vinyl/CD Webscraper'})
    data = urllib.request.urlopen(req).read()
    data = json.loads(data.decode('utf-8'))
    CClist = data["rates"]

    initial_amount = amount
    if from_currency != "EUR":
        amount = amount / CClist[from_currency]

    if to_currency == "EUR":
        return ("€ " + ("%0.2f" % amount))
    elif to_currency == "PLN":
        return (("%0.2f" % (amount * CClist[to_currency])) + " zł")
    elif to_currency == "GBP":
        return ("£ " + ("%0.2f" % (amount * CClist[to_currency])))
    elif to_currency == "CHF":
        return ("CHF " + ("%0.2f" % (amount * CClist[to_currency])))
    else:
        print('Error with handling the currency converter: no to_currency recognised.')
        return ("%0.2f" % (amount * CClist[to_currency]))

def ConverterDodax(priceOG, currency):
    priceCC = re.sub('\s+', '', priceOG) #use RegEx to remove whitespace (Dodax specified)
    priceCC = float(priceCC.replace(",", ".").replace("€", "").replace("£", "").replace("CHF", "").replace("zł", ""))

    if priceOG.find('€') != -1:
        price = CurrencyConverter(priceCC, "EUR", currency)
    if priceOG.find('zł') != -1:
        price = CurrencyConverter(priceCC, "PLN", currency)
    if priceOG.find('CHF') != -1:
        price = CurrencyConverter(priceCC, "CHF", currency)
    if priceOG.find('£') != -1:
        price = CurrencyConverter(priceCC, "GBP", currency)

    return price
