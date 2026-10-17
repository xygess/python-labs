import asyncio
import httpx
import anyio
from prettytable import PrettyTable
from pathlib import Path
from urllib.parse import urlsplit


def create_directory():
    try:
        folder = Path(input())
        folder.mkdir(exist_ok=True, parents=True)
        test_file = folder / '.permission_test'
        test_file.touch(exist_ok=True)
        test_file.unlink()
    except OSError as esc:
        print(f"Системная ошибка: {esc}")
        print("Попробуйте ввести путь еще раз")
        folder = create_directory()
    return folder


async def download_image(url, file, client, download_status):
    try:
        async with client.stream('GET', url) as response:
            try:
                response.raise_for_status()
                if not response.headers.get('content-type', '').startswith('image/'):
                    print(f"URL ведет не к изображению")
                    download_status[url][0] = 'Ошибка'
                    return
                async with await anyio.open_file(file, 'wb') as w_file:
                    async for chunk in response.aiter_bytes(chunk_size=1024):
                        await w_file.write(chunk)
            except httpx.HTTPStatusError as exc:
                print(f"Ошибка HTTP {exc.response.status_code} при запросе к {exc.request.url}")
                download_status[url][0] = 'Ошибка'
            except OSError as exc:
                print(f"Системная ошибка: {exc}")
                download_status[url][0] = 'Ошибка'
        if download_status[url][0] != 'Ошибка':
            download_status[url][0] = 'Успех'
    except httpx.RequestError as exc:
        print(f"Ошибка соединения: {exc}")
        download_status[url][0] = 'Ошибка'
    except httpx.InvalidURL as exc:
        print(f"Некорректный URL: {exc}")
        download_status[url][0] = 'Ошибка'


def render(download_status):
    result = PrettyTable()
    result.field_names = ['Ссылка', 'Статус']
    for i in download_status:
        result.add_row([i, download_status[i][0]])
    result.align = 'l'
    print(result)

async def main():
    folder = create_directory()
    url = await asyncio.to_thread(input)
    tasks = []
    download_status = {}
    async with httpx.AsyncClient(follow_redirects=True) as client:
        while url:
            download_status[url] = download_status.get(url, ['Ожидание', 0])
            download_status[url][1] += 1
            try:
                file = folder / Path(urlsplit(url)[2]).name
            except ValueError as exc:
                print(f"Некорректный URL: {exc}")
                download_status[url][0] = 'Ошибка'
                url = await asyncio.to_thread(input)
                continue
            task = asyncio.create_task(download_image(url, file, client, download_status))
            tasks.append(task)
            url = await asyncio.to_thread(input)
        if any(not task.done() for task in tasks):
            print('Ожидаем загрузку всех файлов...')
        await asyncio.gather(*tasks)
    render(download_status)


if __name__ == "__main__":
    asyncio.run(main())