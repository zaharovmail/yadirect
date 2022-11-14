import config
import requests
from requests.exceptions import ConnectionError
from time import sleep
import json
import datetime

yesterday = str(datetime.date.today() - datetime.timedelta(days=1))

# Метод для корректной обработки строк в кодировке UTF-8 как в Python 3, так и в Python 2
import sys

if sys.version_info < (3,):
    def u(x):
        try:
            return x.encode("utf8")
        except UnicodeDecodeError:
            return x
else:
    def u(x):
        if type(x) == type(b''):
            return x.decode('utf8')
        else:
            return x


# Функция получения остатка баланса
def yaBalance(token, login):
    # Создание тела запроса
    body = {
        "method": "AccountManagement",
        "token": token,
        "locale": "ru",
        "param": {
            "Action": "Get"
        },
        "SelectionCriteria": {
            "Logins": [
                login
            ]
        }
    }

    body = json.dumps(body, indent=4)

    while True:
        try:
            req = requests.post(config.ReportsURL4, body)
            req.encoding = 'utf-8'
            if req.status_code == 400:
                info = ("Параметры запроса указаны неверно или достигнут лимит отчетов в очереди")
                break
            elif req.status_code == 200:
                r = req.json()
                info = [r['data']['Accounts'][0]['Login'], r['data']['Accounts'][0]['Amount'],
                        r['data']['Accounts'][0]['Currency']]
                break
            elif req.status_code == 201:
                info = ("Отчет успешно поставлен в очередь в режиме офлайн")
                retryIn = int(req.headers.get("retryIn", 60))
                sleep(retryIn)
            elif req.status_code == 202:
                info = ("Отчет формируется в режиме офлайн")
                retryIn = int(req.headers.get("retryIn", 60))
                sleep(retryIn)
            elif req.status_code == 500:
                info = ("При формировании отчета произошла ошибка. Пожалуйста, попробуйте повторить запрос позднее")
                break
            elif req.status_code == 502:
                info = ("Время формирования отчета превысило серверное ограничение.")
                break
            else:
                r = req.json()
                info = ("Произошла непредвиденная ошибка" + "\n" + r)
                break
        except ConnectionError:
            info = ("Произошла ошибка соединения с сервером API")
            break
        except:
            info = r
            break
    return info


# Функция получения статистики
def yaStat(token, login):
    headers = {
        "Authorization": "Bearer " + token,
        "Client-Login": login,
        "Accept-Language": "ru",
        "processingMode": "auto"
    }
    body = {
        "params": {
            "SelectionCriteria": {
                "DateFrom": yesterday,
                "DateTo": yesterday
            },
            "FieldNames": [
                "Date",
                "Impressions",
                "Clicks",
                "Cost"
            ],
            "ReportName": u(f"ACCOUNT {login}"),
            "ReportType": "ACCOUNT_PERFORMANCE_REPORT",
            "DateRangeType": "CUSTOM_DATE",
            "Format": "TSV",
            "IncludeVAT": "NO",
            "IncludeDiscount": "NO"
        }
    }

    body = json.dumps(body, indent=4)

    while True:
        try:
            req = requests.post(config.ReportsURL5, body, headers=headers)
            req.encoding = 'utf-8'
            if req.status_code == 400:
                info = ("Параметры запроса указаны неверно или достигнут лимит отчетов в очереди")
                break
            elif req.status_code == 200:
                info = format(u(req.text)).replace('Total rows: 1', ' ')
                data = info.split('"')
                header = data[1]
                body = data[2].split()
                info = (
                    f"{header}\nПоказы - {body[5]}\nКлики - {body[6]}\nРасход - {int(body[7]) / 1000000}")
                break
            elif req.status_code == 201:
                info = ("Отчет успешно поставлен в очередь в режиме офлайн")
                retryIn = int(req.headers.get("retryIn", 60))
                sleep(retryIn)
            elif req.status_code == 202:
                info = ("Отчет формируется в режиме офлайн")
                retryIn = int(req.headers.get("retryIn", 60))
                sleep(retryIn)
            elif req.status_code == 500:
                info = ("При формировании отчета произошла ошибка. Пожалуйста, попробуйте повторить запрос позднее")
                break
            elif req.status_code == 502:
                info = ("Время формирования отчета превысило серверное ограничение.")
                break
            else:
                info = ("Произошла непредвиденная ошибка")
                break
        except ConnectionError:
            # В данном случае мы рекомендуем повторить запрос позднее
            info = ("Произошла ошибка соединения с сервером API")
            break
        except:
            info = ("Произошла непредвиденная ошибка")
            break
    return info