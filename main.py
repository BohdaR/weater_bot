import json
import requests
import pandas
from bs4 import BeautifulSoup

URL = 'https://weather.com/uk-UA/weather/tenday/l/fbd9abfe47326bb176f53692f407ed025fc2916883a34ff763c16c8ba7b25f75'
FILE_NAME = 'weather.json'


def get_data(url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,uk;q=0.8,uk-UA;q=0.7,ru;q=0.6',
        'cache-control': 'max-age=0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/100.0.4896.88 Safari/537.36 '
    }
    r = requests.get(url=url, headers=headers).text
    soup = BeautifulSoup(r, 'lxml')
    details = soup.find_all(class_='DetailsSummary--DetailsSummary--2HluQ DetailsSummary--fadeOnOpen--vFCc_')
    content = []

    for el in details:
        try:
            day = el.find(class_='DetailsSummary--daypartName--2FBp2').text.strip()
        except Exception as ex:
            day = 'Невідомий день'
        content.append({
            'day': day,
            'max_temp': el.find('span', class_='DetailsSummary--highTempValue--3Oteu').text.strip(),
            'min_temp': el.find('span', class_='DetailsSummary--lowTempValue--3H-7I').text.strip(),
            'sky': el.find('span', class_='DetailsSummary--extendedData--365A_').text.strip(),
            'precipitation': el.find('span', {'data-testid': "PercentageValue"}).text.strip(),
            'wind': el.find('span', class_='Wind--windWrapper--3aqXJ undefined').text.strip(),
        })
    save_to_json(content=content, file_name=FILE_NAME)


def save_to_json(content, file_name='rezult.json'):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(content, file, indent=4, ensure_ascii=False)

    df = pandas.DataFrame.from_dict(content)
    df.to_csv('./weather.csv')
    # df.to_excel('./weather.xlsx')


def main():
    get_data(URL)


if __name__ == '__main__':
    main()
