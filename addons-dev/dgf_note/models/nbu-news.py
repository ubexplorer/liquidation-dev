
from bs4 import BeautifulSoup
import pandas as pd
# import json
import requests

BASE_URL = "https://bank.gov.ua"
SEARCH_URL = "/ua/component/source/news/all"

url = "{}{}".format(BASE_URL, SEARCH_URL)
payload = {'tags': 'supervision', 'page': 1, 'perPage': 100}
headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
webpage = requests.post(url=url, data=payload,headers=headers)
soup = BeautifulSoup(webpage.content, "html.parser")
results = soup.find(attrs={'class':'collection'})
data_results = []

for item in results.children:
    if not isinstance(item, str):
        url = item.find('a').attrs['href']
        title = item.find('a').text
        time = item.find('time').text
        tags_items = item.find_all(attrs={'class':'tag'})
        tags = [tag.find('a').text.strip() for tag in tags_items]
        tags_str = str(tags)
        print(tags_str)

        data_result = {'time': time, 'title': title, 'url': '{}{}'.format(BASE_URL, url), 'tags': tags_str}
        # print(data_result)
        data_results.append(data_result)

times = [x['time'] for x in data_results]
titles = [x['title'] for x in data_results]
urls = [x['url'] for x in data_results]
tags = [x['tags'] for x in data_results]
dict = {'time': times, 'title': titles, 'url': urls, 'tags': tags}

result_data = pd.DataFrame(data_results)
result_data.to_csv('nbu-news.csv', sep=';')










def get_page_data():
    url = "{}{}".format(BASE_URL, SEARCH_URL)
    webpage = requests.get(url=url)
    soup = BeautifulSoup(webpage.content, "html.parser")
    results = soup.find_all(attrs={'class':'search-filter-results'}) # "w0"
    data_results = []

    for item in results.children:
        # div = item.find(attrs={'class': 'tit'})  # [0].attrs
        # title = div.contents[0].attrs['title'].strip()
        # title = str(title).encode('cp1251').decode('utf-8')
        # title = str(title, encoding='utf-8')

        # data_result = {'title': title, 'href': href}
        print(item)
        # data_results.append(data_result)

    return data_results

# range_stop = 8
# data_results = []
# for item in range(1, range_stop):
#     data = get_page_data(item)
#     data_results.extend(data)

# titles = [x['title'] for x in data_results]
# hrefs = [x['href'] for x in data_results]
# dict = {'title': titles, 'href': hrefs}

# result_data = pd.DataFrame(data_results)
# result_data.to_csv('url.csv')





# FILE_PATH = './data.json'

# with open(FILE_PATH, 'w', encoding='utf-8') as output_file:
# 	json.dump(data_results, output_file, indent=2)
