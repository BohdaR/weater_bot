import json
import requests
import pandas
import pymysql
import pymysql.cursors
from bs4 import BeautifulSoup


DAILY_URL = 'https://weather.com/uk-UA/weather/tenday/l/fbd9abfe47326bb176f53692f407ed025fc2916883a34ff763c16c8ba7b25f75'
HOURLY_URL = 'https://weather.com/uk-UA/weather/hourbyhour/l/fbd9abfe47326bb176f53692f407ed025fc2916883a34ff763c16c8ba7b25f75'
HEADERS = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,uk;q=0.8,uk-UA;q=0.7,ru;q=0.6',
        'cache-control': 'max-age=0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/100.0.4896.88 Safari/537.36 '
    }
FILE_NAME = 'weather'


def get_daily_data(url, headers):
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


def get_hourly_data(url, headers):
    r = requests.get(url=url, headers=headers).text
    soup = BeautifulSoup(r, 'lxml')
    details = soup.find_all('details', class_='DaypartDetails--DayPartDetail--1up3g')
    days = soup.find_all('h2', class_='HourlyForecast--longDate--1tdaJ')
    day = days[0].text
    count = 0
    content = []
    for el in details:
        hour = el.find('h3', class_='DetailsSummary--daypartName--2FBp2').text
        temperature = el.find('span', class_='DetailsSummary--tempValue--1K4ka').text
        sky = el.find('span', class_='DetailsSummary--extendedData--365A_').text
        precipitation = el.find('span', {'data-testid': "PercentageValue"}).text,
        wind = el.find('span', class_='Wind--windWrapper--3aqXJ').text
        
        if hour == '0:00':
            count +=1
            day = days[count].text

        content.append({
                'hour': hour,
                'precipitation': precipitation[0],
                'temperature': temperature,
                'sky': sky,
                'wind': wind,
                'day': day,
            })
            
    save_to_json(content=content, file_name='hourly')


def save_to_json(content, file_name='rezult'):
    with open(f'{file_name}.json', 'w', encoding='utf-8') as file:
        json.dump(content, file, indent=4, ensure_ascii=False)

    df = pandas.DataFrame.from_dict(content)
    df.to_csv(f'./{file_name}.csv')
    # df.to_excel(f'./{file_name}.xlsx')


def main():
    try:
        connection = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="BohdaR",
            password='Bodya#08752',
            database='test',
            cursorclass=pymysql.cursors.DictCursor
        )
        connection.autocommit(True)
        
    except Exception as ex:
        print(ex)
        return 1

    get_daily_data(DAILY_URL, HEADERS)
    get_hourly_data(HOURLY_URL, HEADERS)


if __name__ == '__main__':
    main()
