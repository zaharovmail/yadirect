# Получение баланса из личного кабинета - РАБОТАЕТ
import config
import requests
from requests.exceptions import ConnectionError
from time import sleep
import json
import datetime

day = str(datetime.date.today())
yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
day7 = str(datetime.date.today() - datetime.timedelta(days=7))
day10 = str(datetime.date.today() - datetime.timedelta(days=10))
day30 = str(datetime.date.today() - datetime.timedelta(days=30))
day365 = str(datetime.date.today() - datetime.timedelta(days=365))

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

    # Кодирование тела запроса в JSON
    body = json.dumps(body, indent=4)


    # Запуск цикла для выполнения запросов
    # Если получен HTTP-код 200, то выводится содержание отчета
    # Если получен HTTP-код 201 или 202, выполняются повторные запросы
    while True:
        try:
            req = requests.post(config.ReportsURL4, body)
            req.encoding = 'utf-8'  # Принудительная обработка ответа в кодировке "UTF-8"
            if req.status_code == 400:
                info = ("Параметры запроса указаны неверно или достигнут лимит отчетов в очереди")
                break
            elif req.status_code == 200:
                r = req.json()
                info = [r['data']['Accounts'][0]['Login'], r['data']['Accounts'][0]['Amount'], r['data']['Accounts'][0]['Currency']]
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

        # Обработка ошибки, если не удалось соединиться с сервером API Директа
        except ConnectionError:
            # В данном случае мы рекомендуем повторить запрос позднее
            info = ("Произошла ошибка соединения с сервером API")
            # Принудительный выход из цикла
            break

        # Если возникла какая-либо другая ошибка
        except:
            # В данном случае мы рекомендуем проанализировать действия приложения
            info = r
            # Принудительный выход из цикла
            break
    return info

def yaStat(token, login):
    headers = {
        # OAuth-токен. Использование слова Bearer обязательно
        "Authorization": "Bearer " + token,
        # Логин клиента рекламного агентства
        "Client-Login": login,
        # Язык ответных сообщений
        "Accept-Language": "ru",
        # Режим формирования отчета
        "processingMode": "auto"
        # Формат денежных значений в отчете
        # "returnMoneyInMicros": "false",
        # Не выводить в отчете строку с названием отчета и диапазоном дат
        # "skipReportHeader": "true",
        # Не выводить в отчете строку с названиями полей
        # "skipColumnHeader": "true",
        # Не выводить в отчете строку с количеством строк статистики
        # "skipReportSummary": "true"
    }


    # Создание тела запроса
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

    # Кодирование тела запроса в JSON
    body = json.dumps(body, indent=4)


    # Запуск цикла для выполнения запросов
    # Если получен HTTP-код 200, то выводится содержание отчета
    # Если получен HTTP-код 201 или 202, выполняются повторные запросы
    while True:
        try:
            req = requests.post(config.ReportsURL5, body, headers=headers)
            req.encoding = 'utf-8'  # Принудительная обработка ответа в кодировке UTF-8
            if req.status_code == 400:
                info = ("Параметры запроса указаны неверно или достигнут лимит отчетов в очереди")
                break
            elif req.status_code == 200:
                a = "RequestId: {}".format(req.headers.get("RequestId", False))
                b = "Содержание отчета: \n{}".format(u(req.text))
                info = f"{a}\n{b}"
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

            # Обработка ошибки, если не удалось соединиться с сервером API Директа
        except ConnectionError:
            # В данном случае мы рекомендуем повторить запрос позднее
            info = ("Произошла ошибка соединения с сервером API")
            # Принудительный выход из цикла
            break

            # Если возникла какая-либо другая ошибка
        except:
            # В данном случае мы рекомендуем проанализировать действия приложения
            info = ("Произошла непредвиденная ошибка")
            # Принудительный выход из цикла
            break

    return info