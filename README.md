# Эмулятор командной оболочки (вариант 18)

## Общее описание

Консольное (CLI) приложение на Python, эмулирующее работу командной
строки UNIX-подобной ОС. Проект выполняется поэтапно; текущее
состояние:

- **Этап 1. REPL** — минимальный прототип: диалог с пользователем,
  парсер, команды-заглушки `ls` и `cd`, команда `exit`.
- **Этап 2. Конфигурация** — параметры командной строки (путь к VFS
  и к стартовому скрипту), отладочный вывод параметров при запуске,
  выполнение стартового скрипта.
- **Этап 3. VFS** — виртуальная файловая система: директория на диске
  загружается в память, все операции выполняются только в памяти,
  команда `vfs-save` сохраняет VFS на диск в исходном формате.

Внешних зависимостей нет, требуется Python 3.8+.

## Структура проекта

```
src/
  main.py               точка входа
  emulator/
    config.py           параметры командной строки, создание VFS
    parser.py           парсер строки ввода
    commands.py         команды эмулятора
    shell.py            состояние оболочки и выполнение команд
    repl.py             интерактивный цикл REPL
    script.py           выполнение стартового скрипта
    vfs.py              виртуальная файловая система в памяти
scripts/
  start_*.txt           стартовые скрипты эмулятора
  test_*.bat, test_*.sh скрипты ОС для проверки эмулятора
vfs/                    примеры VFS для тестирования
tests/                  модульные тесты (unittest)
run.bat, run.sh         скрипты запуска
```

## Параметры командной строки

```
python src/main.py [-h] [--vfs PATH] [--script PATH]
```

| Параметр | Описание |
|---|---|
| `--vfs PATH` | Путь к директории — источнику VFS. Последний компонент пути становится именем VFS в приглашении (`--vfs vfs/deep` → `deep:~$`). Без параметра используется пустая VFS с именем `vfs` |
| `--script PATH` | Путь к стартовому скрипту, который выполняется перед интерактивным режимом |
| `-h`, `--help` | Справка по параметрам |

При запуске все параметры и сведения о загруженной VFS печатаются
как отладочный вывод:

```
[debug] emulator parameters:
[debug]   vfs    = vfs/deep
[debug]   script = scripts/start_vfs.txt
[debug] VFS 'deep' loaded into memory: 13 directories, 10 files
```

Неизвестный параметр или параметр без значения — ошибка, код
возврата 2.

## Виртуальная файловая система (VFS)

Источник VFS — директория на диске пользователя. При запуске вся
структура директорий и содержимое файлов (как байты) рекурсивно
читаются в память. Дальнейшие операции выполняются только с памятью;
исходная директория никогда не изменяется. Изменить данные на диске
может только служебная команда `vfs-save`.

Ошибки загрузки VFS выводятся в stderr, эмулятор завершается с кодом 1:

| Ситуация | Сообщение |
|---|---|
| Путь не существует | `emulator: cannot load VFS 'x': no such file or directory` |
| Путь — файл, а не директория | `emulator: cannot load VFS 'x': invalid format, not a directory` |
| Внутри есть ссылка или устройство | `emulator: cannot load VFS: 'x/link': invalid format, unsupported file type` |
| Нет доступа на чтение | `emulator: cannot load VFS 'x': <файл>: Permission denied` |

### Команда `vfs-save PATH`

Сохраняет текущее состояние VFS из памяти на диск в исходном
формате — в виде дерева директорий с файлами. Директория `PATH`
создается; если она уже существует, она должна быть пустой (данные
не перезаписываются).

| Ошибка | Сообщение |
|---|---|
| Нет пути или лишние аргументы | `vfs-save: usage: vfs-save PATH` |
| `PATH` — файл | `vfs-save: 'PATH': not a directory` |
| `PATH` — непустая директория | `vfs-save: 'PATH': directory is not empty` |

### Примеры VFS

| Директория | Содержимое |
|---|---|
| `vfs/minimal` | Минимальная VFS: один файл |
| `vfs/files` | Несколько файлов в одной директории |
| `vfs/deep` | 13 директорий и 10 файлов, до 5 уровней вложенности |
| `vfs/not_a_directory.txt` | Файл для проверки ошибки «неверный формат» |

## Стартовый скрипт

Текстовый файл в UTF-8, одна команда эмулятора на строку.

- Команды выполняются последовательно. Перед выводом команды
  печатается приглашение и сама команда — так имитируется диалог
  с пользователем.
- Строки с ошибками (неизвестная команда, неверные аргументы)
  сообщают об ошибке и пропускаются, выполнение продолжается.
- Пустые строки и строки, начинающиеся с `#`, игнорируются.
- `exit [код]` останавливает скрипт и эмулятор с указанным кодом.
- Если скрипт не вызвал `exit`, эмулятор переходит в интерактивный
  режим.
- Если файл скрипта не найден или не читается, выводится ошибка
  и эмулятор завершается с кодом 1.

| Скрипт | Назначение |
|---|---|
| `scripts/start_basic.txt` | Все команды этапа 1 без ошибок |
| `scripts/start_errors.txt` | Ошибочные строки и `exit` с кодом 3 |
| `scripts/start_interactive.txt` | Скрипт без `exit`, затем интерактивный режим |
| `scripts/start_vfs.txt` | Все команды этапов 1–3, работа с VFS и ошибки; копию VFS сохраняет в `out/vfs_copy` (запускать из корня проекта) |

## Команды

| Команда | Поведение |
|---|---|
| `ls [арг...]` | Заглушка: выводит имя и аргументы |
| `cd [путь]` | Заглушка: выводит имя и аргумент; более одного аргумента — ошибка |
| `vfs-save PATH` | Сохраняет VFS на диск (см. выше) |
| `exit [код]` | Завершает работу с кодом возврата (по умолчанию 0) |

### Обработка ошибок команд

| Ситуация | Сообщение |
|---|---|
| Неизвестная команда | `foo: command not found` |
| Лишние аргументы `cd` | `cd: too many arguments` |
| Лишние аргументы `exit` | `exit: too many arguments` |
| Нечисловой код `exit` | `exit: abc: numeric argument required` |
| Скрипт не найден | `emulator: cannot read script '...': No such file or directory` |

Ошибки команд выводятся в stderr и не прерывают работу эмулятора.
Пустая строка игнорируется, `Ctrl+D` (`Ctrl+Z` в Windows) завершает
работу, `Ctrl+C` прерывает ввод текущей строки.

## Функции

| Элемент | Описание |
|---|---|
| Приглашение | `<имя VFS>:~$ ` |
| `parse(line)` | Делит ввод на команду и аргументы по пробелам |
| `Shell.execute(line)` | Выполняет строку, возвращает вывод команды |
| `execute_line(...)` | Выполняет строку и печатает вывод или ошибку |
| `run_repl(shell)` | Цикл «чтение — выполнение — вывод» до `exit`/EOF |
| `parse_args(argv)` | Разбирает параметры командной строки |
| `vfs_name_from_path(path)` | Получает имя VFS из пути |
| `create_vfs(args)` | Загружает VFS по параметрам или создает пустую |
| `format_config(args)` | Формирует отладочный вывод параметров |
| `format_vfs_info(vfs)` | Формирует отладочный вывод о загруженной VFS |
| `read_script(path)` | Читает строки стартового скрипта |
| `run_script(...)` | Выполняет команды стартового скрипта |
| `load_vfs(path, name)` | Загружает директорию в память |
| `save_vfs(vfs, path)` | Сохраняет VFS из памяти на диск |
| `Vfs`, `VfsDir`, `VfsFile` | Узлы VFS в памяти; `Vfs.count()` — число директорий и файлов |

## Сборка и запуск тестов

Сборка не требуется.

Windows:

```bat
run.bat                                  :: интерактивный режим
run.bat --vfs vfs\deep --script scripts\start_vfs.txt
run.bat test                             :: модульные тесты
```

Linux / macOS:

```sh
./run.sh                                 # интерактивный режим
./run.sh --vfs vfs/deep --script scripts/start_vfs.txt
./run.sh test                            # модульные тесты
```

Либо напрямую: `python src/main.py ...` и
`python -m unittest discover -s tests -v`.

### Скрипты ОС для проверки

Каждый скрипт есть в двух вариантах: `.bat` (Windows) и `.sh`
(Linux/macOS). Скрипты VFS запускают `start_vfs.txt` и показывают
(`.bat`, через `tree`) или сравнивают с оригиналом (`.sh`, через
`diff -r`) копию, сохраненную `vfs-save`.

| Скрипт | Что проверяет |
|---|---|
| `scripts/test_vfs_minimal` | Пустая директория и VFS из одного файла |
| `scripts/test_vfs_files` | VFS из нескольких файлов |
| `scripts/test_vfs_deep` | VFS с 3+ уровнями файлов и папок, путь с завершающим разделителем |
| `scripts/test_vfs_errors` | Несуществующий путь, файл вместо директории, символическая ссылка внутри VFS |
| `scripts/test_script` | Скрипт со всеми командами, скрипт с ошибками и кодом возврата, переход в интерактивный режим, отсутствующий скрипт |
| `scripts/test_params` | Оба параметра в любом порядке, `--help`, неизвестный параметр, параметр без значения |

## Примеры использования

Работа с VFS в интерактивном режиме:

```
> python src/main.py --vfs vfs/deep
[debug] emulator parameters:
[debug]   vfs    = vfs/deep
[debug]   script = None
[debug] VFS 'deep' loaded into memory: 13 directories, 10 files
deep:~$ vfs-save out/deep_copy
vfs-save: VFS 'deep' saved to 'out/deep_copy'
deep:~$ vfs-save out/deep_copy
vfs-save: 'out/deep_copy': directory is not empty
deep:~$ vfs-save
vfs-save: usage: vfs-save PATH
deep:~$ foo
foo: command not found
deep:~$ exit
```

Ошибка загрузки VFS:

```
> python src/main.py --vfs vfs/not_a_directory.txt
[debug] emulator parameters:
[debug]   vfs    = vfs/not_a_directory.txt
[debug]   script = None
emulator: cannot load VFS 'vfs/not_a_directory.txt': invalid format, not a directory
```

Код возврата — 1.

Стартовый скрипт с ошибками (`scripts/start_errors.txt`):

```
> python src/main.py --script scripts/start_errors.txt
[debug] emulator parameters:
[debug]   vfs    = None
[debug]   script = scripts/start_errors.txt
[debug] VFS 'vfs' loaded into memory: 0 directories, 0 files
vfs:~$ ls /home
ls: args=['/home']
vfs:~$ unknown_command arg
unknown_command: command not found
vfs:~$ cd /tmp /var
cd: too many arguments
vfs:~$ pwd
pwd: command not found
vfs:~$ ls after errors
ls: args=['after', 'errors']
vfs:~$ exit abc
exit: abc: numeric argument required
vfs:~$ exit 1 2
exit: too many arguments
vfs:~$ exit 3
```

Код возврата — 3; строка после `exit 3` не выполняется.
