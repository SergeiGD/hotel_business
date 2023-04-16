from typing import Optional
from hotel_business_module.settings import settings
import uuid
import os
from .protocols import SupportsReading


class FileManager:
    @staticmethod
    def save_file(file: SupportsReading, file_name: str, old_path: Optional[str] = None):
        if old_path is not None:
            # удаляем старую фотографию, если грузим новую
            try:
                os.remove(old_path)
            except OSError:
                pass
        # генерируем имя файла
        # получаем расширение
        extension = file_name.split('.')[-1]
        full_path = f'{settings.MEDIA_DIR}/{uuid.uuid4().hex}.{extension}'
        with open(full_path, 'wb') as file_object:
            content = file.read()
            file_object.write(content)
        return full_path

    @staticmethod
    def delete_file(path: str):
        try:
            os.remove(path)
        except OSError:
            pass
