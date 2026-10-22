# Курс и студент

Основы проектирования графического интерфейса компьютерных систем 

6233-010402D Асташин С.В.

# Лабораторная работа №1

Приложение на Python и PyQt5. В окне находятся надпись и кнопка.
Первое нажатие заменяет надпись картинкой, следующее возвращает текст.
Переключать можно сколько угодно раз.

## Запуск

Нужен Python 3.8 или новее; для этой работы можно использовать Python 3.12.

1. Установите расширение **Python** от Microsoft, если его ещё нет.
2. Откройте терминал VS Code и выполните:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe lab1\main.py
```

Активация окружения не нужна: команды напрямую используют Python из `.venv`.
Если команда `py` не найдена, в первой строке используйте `python`.

На Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python lab1/main.py
```

## Как работает программа

`MainWindow` наследуется от `QMainWindow`. Форма загружается через `uic.loadUi()`.
`QLabel` показывает текст или картинку, а `QPushButton` служит кнопкой.
Сигнал `clicked` подключён к слоту `toggle_content()` через `connect()`.

Переменная `showing_image` хранит текущее состояние. Для картинки используется
`QPixmap` и метод `setPixmap()`, для текста — `setText()`. При масштабировании
сохраняются пропорции изображения.

Цвета и скругления задаются таблицей стилей Qt в `main.ui`, а тень карточки —
через `QGraphicsDropShadowEffect` в `main.py`.

## Документация

- [PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Установка PyQt5](https://pypi.org/project/PyQt5/5.15.11/)
