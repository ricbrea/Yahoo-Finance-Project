import bs4 as bs
import requests

html = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
soup = bs.BeautifulSoup(html.text, 'lxml')

tickers = []

table = soup.find('table', {'class': 'wikitable sortable'})
rows = table.findAll('tr')[1:]
for row in rows:
    ticker = row.findAll('td')[0].text
    tickers.append(ticker[:-1])

#print(tickers)

#with open(r'sp500companies.txt', 'w') as fp:
#    for item in tickers:
#        # write each item on a new line
#        fp.write("%s\n" % item)
#    print('Done')

with open(r'sp500companies.txt', 'r') as fp:
    for line in fp:
        # remove linebreak from a current name
        # linebreak is the last character of each line
        x = line[:-1]

        # add current item to the list
        tickers.append(x)

# display list
print(tickers)
