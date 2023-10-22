import asyncio

from models import Session, SwapiPeople
from models import engine, Base


async def make_db_table():
    """Функция делает миграцию в БД и создает таблицы."""

    async with engine.begin() as connection:  # Код создает миграции в БД. Такой код нужен для асинхронного прогр-я.
        await connection.run_sync(Base.metadata.create_all)


async def drop_db_table():
    """Функция делает миграцию в БД и удаляет таблицы."""

    async with engine.begin() as connection:  # Код удаляет миграции в БД. Такой код нужен для асинхронного прогр-я.
        await connection.run_sync(Base.metadata.drop_all)


async def get_swapi_object(group_name: str, object_id: int, api_client):
    """
    Функция возвращает json с данными персонажа по запрашиваемому ID.

    :param group_name:
        Имя группы объекта - people, films или другие.
    :param api_client:
        Сессионный клиент.
    :param object_id: int
        Id объекта.
    :return: dict
        Json-словарь с данными объекта.
    """

    url = 'https://swapi.dev/api'  # адрес для обращения
    response = await api_client.get(f'{url}/{group_name}/{object_id}/')  # Делаем запрос к API.
    # Т.к. функция асинхронная, не забываем await, чтобы получить результат работы, а не корутину.

    json_data = await response.json()  # функция асинх, поэтому ставим await и получаем json.
    return json_data


async def prepare_for_orm(some_json: dict, client):
    """
    Функция принимается на вход json-файл и заменяет ссылки во всех полях на их значения. Если ссылок несколько,
    значения объединяются в строку.

    :param some_json: dict
        json персонажа.
    :param client:
        Сессионный клиент.
    :return: dict
        Подготовленный json с замененными значениями ссылок.
    """

    for key, value in some_json.items():  # словарь, где в одном из значений список ссылок.
        if type(value) == list:  # если в значении список ссылок,
            response_coro_list = [client.get(link) for link in value]  # асинхронно формируем коро объекты запросов.
            response_list = await asyncio.gather(*response_coro_list)  # обрабатываем.

            json_coro_list = [response.json() for response in response_list]  # асинхронно получаем json'ы.
            json_data_list = await asyncio.gather(*json_coro_list)  # Обрабатываем. На выходе список json-объектов.

            temp_list = []  # создаем временный список и добавляем туда значения выбранного поля - имя, название или пр.
            for json_data in json_data_list:
                if json_data.get('name') is not None:  # если в словаре есть ключ name, то
                    temp_list.append(json_data.get('name'))  # добавляем промежуточный список значение для склейки.
                else:
                    temp_list.append(json_data.get('title'))  # иначе добавляем значение по title.
            some_json[key] = (', '.join(temp_list))  # объединяем все значения в строку.

    # Получение названия планеты.
    link = some_json.get('homeworld')  # получаем ссылку на планету.
    # print(link)
    if link is None:  # если ссылки нет,
        some_json['homeworld'] = None  # устанавливаем значение None для записи в БД.
    else:
        response = await client.get(link)  # Переходим по ссылке планеты.
        json_data = await response.json()  # Получаем json.
        some_json['homeworld'] = json_data.get('name')  # устанавливаем значение имени в json для записи в БД.

    return some_json


async def paste_to_db(object_json_list):
    """
    Функция принимает список json-файлов персонажей и вставляет данные в БД.

    :param object_json_list: list
        Список json-файлов для обработки.
    :return: None
        None.
    """

    async with Session() as session:  # создаем сессию для работы с БД.
        insert_list = []  # список для хранения готовых объектов класса SwapiPeople.
        for person_json in object_json_list:  # циклом создаем объекты класса.
            person = SwapiPeople(birth_year=person_json.get('birth_year'),
                                 eye_color=person_json.get('eye_color'),
                                 films=person_json.get('films'),
                                 gender=person_json.get('gender'),
                                 hair_color=person_json.get('hair_color'),
                                 height=person_json.get('height'),
                                 homeworld=person_json.get('homeworld'),
                                 mass=person_json.get('mass'),
                                 name=person_json.get('name'),
                                 skin_color=person_json.get('skin_color'),
                                 species=person_json.get('species'),
                                 starships=person_json.get('starships'),
                                 vehicles=person_json.get('vehicles')
                                 )
            insert_list.append(person)  # Добавляем в список.
        session.add_all(insert_list)  # Комплексно добавляем данные в БД.
        await session.commit()  # Сохраняем в БД.
