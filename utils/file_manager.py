from typing import Optional
from hotel_business_module.settings import settings
import uuid
import os
import aiofiles
from .protocols import SupportsReading, SupportsAsyncReading


class FileManager:
    @staticmethod
    def __prepare_uploading(file_name: str, old_path: str):
        """
        Общие подготовительные действия перед сохранением
        :param file_name: наименование файла
        :param old_path: старый путь (если перезагружаем фотографию)
        :return:
        """
        if old_path is not None:
            # удаляем старую фотографию, если грузим новую
            FileManager.delete_file(old_path)
        # получаем расширение
        extension = file_name.split('.')[-1]
        # генерируем имя файла
        full_path = f'{settings.MEDIA_DIR}/{uuid.uuid4().hex}.{extension}'
        return full_path

    @classmethod
    def save_file(cls, file: SupportsReading, file_name: str, old_path: Optional[str] = None):
        """
        Cсинхронное сохранение файла
        :param file: файл
        :param file_name: наименование файла
        :param old_path: старый путь (если перезагружаем фотографию)
        :return:
        """
        full_path = cls.__prepare_uploading(file_name, old_path)
        with open(full_path, 'wb') as file_object:
            content = file.read()
            file_object.write(content)
        return full_path

    @classmethod
    async def asave_file(cls, file: SupportsAsyncReading, file_name: str, old_path: Optional[str] = None):
        """
        Асинхронное сохранение файла
        :param file:  file-like объект с async инерфейсом
        :param file_name: наименование файла
        :param old_path: старый путь (если перезагружаем фотографию)
        :return:
        """
        full_path = cls.__prepare_uploading(file_name, old_path)
        async with aiofiles.open(full_path, 'wb') as file_object:
            content = await file.read()
            await file_object.write(content)
        return full_path

    @staticmethod
    def delete_file(path: str):
        """
        Безопасное уаление файла
        :param path: путь до файла
        :return:
        """
        try:
            os.remove(path)
        except OSError:
            pass
