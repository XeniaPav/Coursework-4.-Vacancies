import json
from abc import ABC, abstractmethod
import requests
import os

class API(ABC):
    """
    Абстрактный класс для подключения к API сайтов
    """
    @abstractmethod
    def get_vacancies(self, keyword, quantity):
        pass

class HeadHunterAPI(API):
    """
    Класс для подключения к сайту hh.ru и поиска вакансий
    """
    def get_vacancies(self, keyword, quantity):
        url_hh = 'https://api.hh.ru/vacancies'
        vacancies_hh = requests.get(url_hh, params={'text': keyword, 'currency': 'RUR', 'host': 'hh.ru'}).json()
        vacancy = {}
        for i in range(0, quantity):
            try:
                vacan = {'name': vacancies_hh['items'][i]['name'], 'payment_to': vacancies_hh['items'][i]['salary']['to'], 'payment_from': vacancies_hh['items'][i]['salary']['from'], 'town': vacancies_hh['items'][i]['area']['name'], 'requirement': vacancies_hh['items'][i]['snippet']['requirement']}
            except TypeError:
                vacan = {
                    'name': vacancies_hh['items'][i]['name'],
                    'payment_to': 0,
                    'payment_from': 0,
                    'town': vacancies_hh['items'][i]['area']['name'],
                    'requirement': vacancies_hh['items'][i]['snippet']['requirement']
                }
            vacancy[vacancies_hh['items'][i]['id']] = vacan
        return vacancy

class Vacancy:
    """
    Класс для работы с вакансией
    """
    def __init__(self, name=None, payment_to=0, payment_from=0, town=None, requirement=None):
        self.name = name
        try:
            self.payment_to: int = payment_to
        except AttributeError:
            self.payment_to: int = 0
        try:
            self.payment_from: int = payment_from
        except AttributeError:
            self.payment_from: int = 0
        self.town = town
        self.requirement = requirement
        if self.payment_to is None and self.payment_from is None:
            self.salary = 0
        elif self.payment_from is None:
            self.salary = self.payment_to
        elif self.payment_to is None:
            self.salary = self.payment_from
        else:
            self.salary = (self.payment_from + self.payment_to) / 2

    def __lt__(self, other):
        return self.salary < other.salary

    def __str__(self):
        return f'''Название вакансии: {self.name}
Средняя зарплата: {int(self.salary)}
Город: {self.town}
Описание: {self.requirement[0:100]}'''


class JSONSave(ABC):
    """
    Абстрактный класс для сохранения данных в json-файл
    """
    @abstractmethod
    def to_json(self, getted_vac):
        """
        Функция для первичного сохранения в пустой файл
        :param getted_vac: словарь из вакансий
        :return: None
        """
        pass

    @abstractmethod
    def add_vacancy(self, getted_vac):
        """
        Функция для добавления вакансий в уже заполненный файл
        :param getted_vac: словарь из вакансий
        :return: None
        """
        pass

    @abstractmethod
    def delete_vacancy(self, getted_vac):
        """
        Функция для удаления вакансии из файла
        :param getted_vac: экземпляр класса Vacancy
        :return: None
        """
        pass


class JSONSaver(JSONSave):
    """
    Класс для работы с json-файлом
    """
    def __init__(self, file='saved_vacancies.json'):
        self.file = file

    def to_json(self, getted_vac):
        """
        Функция для первичного сохранения в пустой файл
        :param getted_vac: словарь из вакансий
        :return: None
        """
        with open(os.path.abspath(self.file), 'w', encoding='utf=8') as f:
            json.dump(getted_vac, f, ensure_ascii=False, indent=2)

    def add_vacancy(self, getted_vac):
        """
        Функция для добавления вакансий в уже заполненный файл
        :param getted_vac: словарь из вакансий
        :return: None
        """
        getted_vac = json.dumps(getted_vac)
        getted_vac = json.loads(str(getted_vac))
        b = json.load(open(os.path.abspath(self.file), 'r', encoding='utf=8'))
        for key, items in getted_vac.items():
            b[key] = items
        json.dump(b, open(os.path.abspath(self.file), 'w', encoding='utf=8'), ensure_ascii=False, indent=2)

    def read_vacancy(self):
        b = json.load(open(os.path.abspath(self.file), 'r', encoding='utf=8'))
        vacancies_list = []
        for key, item in b.items():
            vacancies_list.append(Vacancy(item['name'],
                                          item['payment_to'],
                                          item['payment_from'],
                                          item['town'],
                                          item['requirement']))
        return vacancies_list

    def delete_vacancy(self, del_vac):
        """
        Функция для удаления вакансии из файла
        :param del_vac: экземпляр класса Vacancy
        :return: None
        """
        del_vac = json.dumps(del_vac.__dict__)
        del_vac = json.loads(str(del_vac))
        name = del_vac['name']
        town = del_vac['town']
        b = json.load(open(os.path.abspath(self.file), 'r', encoding='utf=8'))
        for key, items in list(b.items()):
            if items['name'] == name and items['town'] == town:
                b.pop(key, items)
        json.dump(b, open(os.path.abspath(self.file), 'w', encoding='utf=8'), ensure_ascii=False, indent=2)

    def view_vacancies(self):
        """
        Функция для просмотра вакансий из файла
        :param view_vac: экземпляр класса Vacancy
        :return: None
        """
        vac_list_json = open("saved_vacancies.json", "r", encoding='utf=8')
        vac_list = json.load(vac_list_json)
        list = []
        for key, value in vac_list.items():
            list.append(value)
        for i in list:
            print(f"""Название вакансии: {i['name']}\nЗарплата: {i['payment_to']} - {i['payment_to']}\nГород: {i['town']}\nТребования: {i['requirement']}""")

