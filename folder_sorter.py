import asyncio
from pathlib import Path
import shutil
from module_normalize import normalize
import module_parser as parser


async def handle_files(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.name))


def handle_other(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.name))


async def handle_archive(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(filename.name.replace(filename.suffix, ''))

    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(filename.resolve()), str(folder_for_file.resolve()))
    except shutil.ReadError:
        print(f'Помилка! Це не архів {filename}!')
        folder_for_file.rmdir()
        return None
    filename.unlink()


def handle_folder(folder: Path):
    try:
        folder.rmdir()
    except OSError:
        print(f'Помилка видалення папки {folder}')


async def sort_files(folder: Path):
    list_tasks = []
    for k, v in parser.REGISTER_EXTENSIONS.items():
        for file in v:
            if k == 'JPEG' or k == 'JPG' or k == 'SVG' or k == 'PNG':
                list_tasks.append(asyncio.create_task(handle_files(file, folder / 'images' / k)))
            elif k == 'MP3' or k == 'OGG' or k == 'WAV' or k == 'AMR':
                list_tasks.append(asyncio.create_task(handle_files(file, folder / 'audio' / k)))
            elif k == 'AVI' or k == 'MP4' or k == 'MKV' or k == 'MOV':
                list_tasks.append(asyncio.create_task(handle_files(file, folder / 'video' / k)))
            elif k == 'DOC' or k == 'DOCX' or k == 'TXT' or k == 'PDF' or k == 'PPTX' or k == 'XLSX':
                list_tasks.append(asyncio.create_task(handle_files(file, folder / 'documents' / k)))
            elif k == 'ZIP' or k == 'GZ' or k == 'TAR':
                list_tasks.append(asyncio.create_task(handle_archive(file, folder / 'archives' / k)))
            else:
                list_tasks.append(asyncio.create_task(handle_other(file, folder / 'other' / 'OTHERS')))
    await asyncio.gather(*list_tasks)

    for folder in parser.FOLDERS[::-1]:
        handle_folder(folder)


async def main(folder: Path):
    parser.scan(folder)
    await sort_files(folder)


if __name__ == '__main__':
    folder_for_scan = Path(r'C:\Users\User\Desktop\xlam').resolve()
    asyncio.run(main(folder_for_scan))
