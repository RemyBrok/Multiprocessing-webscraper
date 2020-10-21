import requests
from bs4 import BeautifulSoup, SoupStrainer
import lxml.html
from cc import CurrencyConverter, ConverterDodax
import concurrent.futures
import unidecode

def MakeList(input, currency, artist, title):
    """ Returns a list we can loop through with our threading function """
    websites = []
    id = 1

    extensions = ['nl/nl-nl/', 'co.uk/en-gb/', 'ch/de-ch/', 'de/de-de/', 'at/de-at/', 'fr/fr-fr/', 'pl/pl-pl/', 'it/it-it/', 'es/es-es/']
    for extension in extensions:
        websites.append([f'https://www.dodax.{extension}', input, currency, artist, title, id])
        id += 1

    websites.append(['https://www.jpc.de', input, currency, artist, title, id])
    return websites

def Threading(input, artist, title, currency):
    """ Main function that use threading for webscraping and return values in a list back"""
    if __name__ == 'dodaxprocessor':
        with concurrent.futures.ThreadPoolExecutor() as executor:
            websites = MakeList(input, currency, artist, title) # make a list of what we wanna excecute
            results = executor.map(Scraper, websites) #send list to function and thread

            list = [] # make empty list for the results
            for result in results:
                for r in result:
                    list.append(r) #put in a list of results in a list

            return list

def FilterNoise(InputScraper, InputUser):
    """ Function to check the input against the scraped content"""
    if InputUser and not InputScraper:
        return False #Yes user input no artist scraped
    if not InputUser:
        return True #No user input so we return values.
    cInputScraper = unidecode.unidecode(InputScraper).lower()
    cInputUser = unidecode.unidecode(InputUser).lower()
    cInputUser = cInputUser.replace("the ", "").replace("a ", "")
    for word in cInputUser.split():
        if word in cInputScraper:
            return True

def Scraper(ListInput):
    """ Scraper functions that uses BeautifulSoup to check on websites and return a list with values"""
    list = []
    website = ListInput[0]
    input = ListInput[1]
    currency = ListInput[2]
    InputArtist = ListInput[3]
    WebsiteID = ListInput[5]
    counter = 0

    if ListInput[0][12:17] == 'dodax':
        websitetitle = website[12:]
        if websitetitle == 'dodax.es/es-es/':
            input = input.replace("vinyl", "vinilo")

        data = requests.get(f'{website}/search/?s={input}')
        strainerDodax = SoupStrainer('div', attrs={'class': 'row h-100'})
        soup = BeautifulSoup(data.text, 'lxml', parse_only=strainerDodax)

        list.append([1, websitetitle[0:-7], 0, 0, website, WebsiteID])

        for content in soup.find_all('div', { 'class': 'row h-100' }):
            if content.find('p', { 'class': 'product_type' }):
                type = content.find('p', { 'class': 'product_type' }).text
            else:
                type = None

            if type != "Single (Vinyl)" and type != "LP (Vinyl)" and type != "CD" and type != "LP (Vinilo)":
                break #not the type we want. break out loop.

            if content.find('p', { 'class': 'product_from' }):
                artist = content.find('p', { 'class': 'product_from' }).text
            else:
                artist = None

            if content.find('p', { 'class': 'product_title font_bold' }):
                title = content.find('p', { 'class': 'product_title font_bold' }).text
            else:
                title = None

            if content.find('a', { 'class': 'col-12 js-product'}):
                url = website + content.find('a', { 'class': 'col-12 js-product'}).get('href')
            else:
                url = '#'

            for s in content.find_all('div', {'class': 'col-12 related_sect mt-auto' }):
                if s.find('span').text:
                    price = ConverterDodax(s.find('span').text, currency)
                else:
                    price = None

                if not FilterNoise(title, ListInput[4]):
                    break

                if FilterNoise(artist, InputArtist):
                    list.append([artist, title, type, price, url, WebsiteID])
                    counter += 1

        if(counter == 0):
            list.pop() #nothing found -> delete shop

    if ListInput[0][12:15] == 'jpc': # Do JPC Stuff
        data = requests.get(f'https://www.jpc.de/s/{input}')
        soup = BeautifulSoup(data.text, 'lxml', parse_only=SoupStrainer('main'))

        list.append([1, 'JPC.de', 0, 0, 'https://www.jpc.de', WebsiteID])

        if soup.find('main', { 'class': 'product'}):
            artist = soup.find('a', { 'class': 'search-link' }).text.strip()
            title = soup.find('div', { 'class': 'box title' }).text.strip()
            type = soup.find('em', { 'class': 'open-help-layer' }).text.strip()
            price = soup.find('span', { 'itemprop': 'price' }).text.strip()
            url = soup.find('a', { 'class': 'link-back' }).get('href')
            list.append([artist, title, type, price, url, WebsiteID])
            counter += 1
        else:
            for content in soup.find_all('div', { 'class': 'content' }):
                if not content.find('div', { 'class': 'medium' }): #check if there is product type
                    break

                if not content.find('div', { 'class': 'medium' }):
                    break

                type = content.find('div', { 'class': 'medium' }).text.strip()
                if type.find('LP') == -1 and type.find('CD') == -1 and type.find('Single') == -1:
                    break

                price = content.find('div', { 'class': 'price' }).text.strip()
                price = price.replace(" ", "").replace("EUR", "").replace(",", ".").replace("*", "")
                price = CurrencyConverter(float(price), "EUR", currency)

                if content.find('div', { 'class': 'by' }):
                    artist = content.find('div', { 'class': 'by' }).text.strip()
                else:
                    artist = None

                if content.find('div', { 'class': 'title' }):
                    title = content.find('div', { 'class': 'title' }).text.strip()
                else:
                    title = None

                if not FilterNoise(title, ListInput[4]):
                    break

                url = 'https://www.jpc.de' + content.find('a').get('href')
                if FilterNoise(artist, InputArtist):
                    counter += 1
                    list.append([artist, title, type, price, url, WebsiteID])

        if counter == 0:
            list.pop()

    return list

if __name__ == '__main__':
    pass
