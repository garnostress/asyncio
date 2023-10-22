import asyncio
from more_itertools import chunked
from function import get_swapi_object
from aiohttp import ClientSession
from function import paste_to_db, prepare_for_orm, make_db_table, drop_db_table
from datetime import datetime

MAX_REQUESTS = 5


async def main(quantity: int):
    """
    Функция принимает количество персонажей, обрабатывает их циклом range и возвращает список словарей с их данными.

    :param quantity: int
        Количество персонажей, обрабатываемое range.
    :return: list
        Список словарей с данными персонажей.

    """

    await drop_db_table()
    await make_db_table()

    async with ClientSession() as client:
        for chunk in chunked(range(1, quantity + 1), MAX_REQUESTS):  # разбиваем запросы на чанки.
            # формируем список корутин, функция получения json персонажей.
            chunk_coro_list = [get_swapi_object(group_name='people', object_id=id_, api_client=client) for id_ in chunk]

            # Асинхронно обрабатываем корутины. На выходе список.
            res_list = await asyncio.gather(*chunk_coro_list)

            # готовим список корутин, функция обработки json персонажей.
            coro_list = [prepare_for_orm(some_json=dict_, client=client) for dict_ in res_list]

            # обрабатываем корутины, получаем список словарей для вставки в БД.
            ready_to_paste_list = await asyncio.gather(*coro_list)

            paste_coro = paste_to_db(ready_to_paste_list)  # делаем корутину по вставке в БД.

            paste_task = asyncio.create_task(paste_coro)  # создаем таск на вставку в БД.
    #
    tasks = asyncio.all_tasks() - {asyncio.current_task(), }  # получаем все открытые таски.
    for task in tasks:  # выполняем все таски принудительно.
        await task


if __name__ == '__main__':
    start = datetime.now()
    result = asyncio.run(main(quantity=100))
    print(datetime.now() - start)
