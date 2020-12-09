import os
import json
from jsonschema import Draft4Validator
from jinja2 import Template


def read_json_file(json_file_path):
    """Загрузка данных из JSON файлов"""
    with open(json_file_path, mode='r') as from_file:
        json_data = json.loads(from_file.read())
    return json_data


class JsonHandler:
    """Обработчик JSON данных"""

    def __init__(self, file_json_data, schema_directory):
        self.file_json_data = file_json_data
        self.schema_directory = schema_directory

    def select_info_from_json(self):
        """Выбирает необходимые данные из JSON файла"""
        json_data = read_json_file(self.file_json_data)
        selected_data = {}
        if json_data:
            for key, value in json_data.items():
                if key == 'event':
                    # Убираем лишние пробелы в название event
                    value = ''.join(value.split())
                    selected_data['event'] = value
                elif key == 'data' and value is not None:
                    selected_data['data'] = value
            return selected_data
        else:
            return 'Ошибка: некорректный JSON файл'

    def search_path_scheme(self):
        """На основе полученных данных из предыдущего метода ищет файл со схемой для валидации JSON данных"""
        event_name = self.select_info_from_json()['event'] if isinstance(self.select_info_from_json(), dict) \
            else 'Ошибка: некорректный JSON файл'
        if 'Ошибка' not in event_name:
            schema_files = os.listdir(self.schema_directory)
            for file in schema_files:
                if event_name in file:
                    full_path_to_schema = os.path.join(self.schema_directory, file)
                    return full_path_to_schema
            return f'Отсутствует схема для валидации данного JSON файла / необходимо использовать схему: {event_name}'
        return 'Ошибка: некорректный JSON файл'


def validate_json():
    validate_instance = Draft4Validator(json_schema)
    errors_instance = []
    for error in validate_instance.iter_errors(json_instance):
        if 'required property' in error.message:
            error = str(error.message)
            error = error.split("'")[1]
            message = f"Отсутствует обязательное свойство '{error}' в JSON файле / необходимо внести данное свойство " \
                      f"в JSON файл"
            errors_instance.append(message)
        elif 'некорректный JSON' in error.message:
            errors_instance.append('Некорректный JSON файл / проведите анализ файла, внесите необходимые изменения '
                                   'в JSON файл')
        elif 'is not of type' in error.message:
            error = str(error.message)
            error = error.split("'")
            if 'None' in error[0]:
                message = f"Значение 'None' не является типом данных '{error[1]}' / необходимо использовать валидные " \
                          f"типы данных, которые описаны в схеме"
            else:
                message = f"Значение '{error[1]}' не является типом данных '{error[3]}' / необходимо использовать " \
                          f"валидные типы данных, которые описаны в схеме"
            errors_instance.append(message)
        else:
            errors_instance.append(error.message)

    if len(errors_instance) == 0:
        errors_instance.append('Ошибок нет. Валидация прошла успешно.')
    return errors_instance


def write_info_data():
    """Формирует словарь для финального отчета"""
    info = {'json_name': event_file}
    if 'Отсутствует схема' in json_schema_file:
        info['errors'] = [json_schema_file]
    else:
        errors = validate_json()
        if isinstance(json_instance, dict) or "'data' равно None" in json_instance:
            info['schema_name'] = json_schema_file.split('/')[-1]
        else:
            info['schema_name'] = ''
        info['errors'] = errors
    return info


def display_info():
    """Генерирует таблицу с данными и сохраняет её в html файл"""
    data = '''
    <!doctype html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
            content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" 
        integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
        <title>Welltory_report</title>
    </head>
    <body>
        <H1 class="text-center">Отчет</H1>
        <table class="table table-bordered">
            <thead>
                <tr class="table table-bordered table-dark text-center">
                    <th scope="col">Имя JSON файла</th>
                    <th scope="col">Имя схемы</th>
                    <th colspan="3" scope="col" class="text-center">Ошибки / Решение</th>
                </tr>
            </thead>
            <tbody>
                {% for errors_string in ERRORS_INFO %}
                <tr>
                    <td>{{ errors_string.json_name }}</td>
                    <td>{{ errors_string.schema_name }}</td>
                    {% for error in errors_string.errors %}
                    {% if 'Отсутствует' in error or 'Некорректный' in error or 'не является типом данных' in error%}
                    <td class="text-danger">{{ error }}</td>
                    {% else %}
                    <td class="text-success">{{ error }}</td>
                    {% endif %}
                    {% endfor %}
                    {% if errors_string.errors|length == 2 %}
                    <td></td>
                    {% elif errors_string.errors|length == 1 %}
                    <td></td>
                    <td></td>
                    {% endif %}
                </tr>
                {% endfor %}
            </tbody>
        </table>    
    </body>
    </html>
    '''
    template = Template(data)
    msg = template.render(ERRORS_INFO=ERRORS_INFO)
    with open('report.html', mode='w', encoding='utf-8') as report_file:
        report_file.write(msg)


if __name__ == '__main__':
    # Путь до родительского каталога(BASE DIR)
    COMMON_PATH = 'D:/task_backend_developer_november_2020/task_folder/'
    # Путь до каталога с JSON файлами
    EVENTS_PATH = os.path.join(COMMON_PATH, 'event/')
    # Путь до каталога с JSON схемами
    SCHEMAS_PATH = os.path.join(COMMON_PATH, 'schema/')
    # Инициализируем массив, в который запишем все данные для финального отчета
    ERRORS_INFO = []

    event_files = os.listdir(EVENTS_PATH)
    for event_file in event_files:
        try:
            json_data_file = os.path.join(EVENTS_PATH, event_file)
            handler_json_data = JsonHandler(json_data_file, SCHEMAS_PATH)
            json_schema_file = handler_json_data.search_path_scheme()
            if isinstance(handler_json_data.select_info_from_json(), dict):
                if handler_json_data.select_info_from_json().__contains__('data'):
                    json_instance = handler_json_data.select_info_from_json()['data']
                    json_schema = read_json_file(json_schema_file)
                else:
                    json_instance = "В JSON файле значение свойства 'data' равно None"
            else:
                json_instance = 'Ошибка: некорректный JSON файл'
            ERRORS_INFO.append(write_info_data())
        except Exception:
            ERRORS_INFO.append(write_info_data())

    display_info()
