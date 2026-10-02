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
- **Этап 4. Основные команды** — настоящие `ls` и `cd` с текущей
  директорией и путями (`.`, `..`, `~`), новые команды `history`,
  `rev` и `cat`.

Внешних зависимостей нет, требуется Python 3.8+.

## Структура проекта

```
src/
  main.py               точка входа
  emulator/
    config.py           параметры командной строки, создание VFS
    parser.py           парсер строки ввода
    errors.py           исключения команд
    commands.py         реестр команд, history, exit, vfs-save
    filecmds.py         команды ls, cd, cat, rev
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
| `--vfs PATH` | Путь к директории — источнику VFS. Последний компонент пути становится именем VFS в приглашении (`--vfs vfs/deep` → `deep:/$`). Без параметра используется пустая VFS с именем `vfs` |
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
| `scripts/start_basic.txt` | Команды `ls` и `cd` без ошибок (для `vfs/deep`) |
| `scripts/start_errors.txt` | Ошибочные строки и `exit` с кодом 3 |
| `scripts/start_interactive.txt` | Скрипт без `exit`, затем интерактивный режим |
| `scripts/start_vfs.txt` | Все команды этапов 1–3, работа с VFS и ошибки; копию VFS сохраняет в `out/vfs_copy` (запускать из корня проекта) |
| `scripts/start_commands.txt` | Команды этапа 4 (`ls`, `cd`, `history`, `rev`, `cat`) во всех режимах и с ошибками (для `vfs/deep`) |

## Команды

Пути в командах — пути внутри VFS: абсолютные (`/home/user`),
относительные от текущей директории (`docs/report.txt`), с `.` и `..`,
а также `~` — домашняя директория, которой является корень VFS.
Текущая директория отображается в приглашении: `deep:/home/user$`.

| Команда | Поведение |
|---|---|
| `ls [-a] [-l] [PATH...]` | Без путей — содержимое текущей директории. Для директории выводит содержимое по алфавиту, для файла — его путь. `-a` показывает скрытые файлы (имя начинается с `.`), `-l` — длинный формат: тип (`d`/`-`), размер в байтах, имя. Опции объединяются (`-al`). Для нескольких путей содержимое выводится блоками с заголовком `PATH:` |
| `cd [PATH]` | Переходит в директорию; без аргумента — в корень (`~`) |
| `cat FILE...` | Выводит содержимое файлов, объединяя их по порядку |
| `rev FILE...` | Выводит строки файлов с символами в обратном порядке |
| `history [N]` | Выводит пронумерованную историю всех введенных команд (включая ошибочные и сам `history`); с `N` — только `N` последних |
| `vfs-save PATH` | Сохраняет VFS на диск (см. выше) |
| `exit [код]` | Завершает работу с кодом возврата (по умолчанию 0) |

Содержимое файлов для `cat` и `rev` читается как UTF-8 (некорректные
байты заменяются символом `�`), окончания строк Windows приводятся
к `
`. Чтение стандартного ввода не поддерживается, поэтому `cat`
и `rev` требуют хотя бы один файл.

### Обработка ошибок команд

Если команда получила несколько путей и часть из них ошибочна, для
корректных путей вывод печатается, а для ошибочных — сообщения
об ошибках.

| Ситуация | Сообщение |
|---|---|
| Неизвестная команда | `foo: command not found` |
| Путь не найден | `ls: cannot access 'x': No such file or directory`, `cd: x: No such file or directory`, `cat: x: No such file or directory` |
| Файл вместо директории | `cd: a.txt: Not a directory` |
| Директория вместо файла | `cat: docs: Is a directory`, `rev: docs: Is a directory` |
| Неизвестная опция `ls` | `ls: invalid option -- 'z'` |
| `cat`/`rev` без файлов | `cat: missing file operand` |
| Лишние аргументы `cd`, `history`, `exit` | `cd: too many arguments` |
| Нечисловой аргумент `history`, `exit` | `history: abc: numeric argument required` |
| Отрицательный аргумент `history` | `history: -3: invalid option` |
| Скрипт не найден | `emulator: cannot read script '...': No such file or directory` |

Ошибки команд выводятся в stderr и не прерывают работу эмулятора.
Пустая строка игнорируется, `Ctrl+D` (`Ctrl+Z` в Windows) завершает
работу, `Ctrl+C` прерывает ввод текущей строки.

## Функции

| Элемент | Описание |
|---|---|
| Приглашение | `<имя VFS>:<текущая директория>$ ` |
| `parse(line)` | Делит ввод на команду и аргументы по пробелам |
| `Shell.execute(line)` | Выполняет строку, добавляет ее в историю, возвращает вывод команды |
| `Shell.resolve(path)`, `Shell.find(path)` | Разбирают путь относительно текущей директории и находят узел VFS |
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
| `Vfs`, `VfsDir`, `VfsFile` | Узлы VFS в памяти; `Vfs.count()` — число директорий и файлов, `Vfs.get(parts)` — поиск узла |
| `split_path(path, cwd)`, `format_path(parts)` | Разбор пути VFS в список компонентов и обратно |
| `cmd_ls`, `cmd_cd`, `cmd_cat`, `cmd_rev`, `cmd_history` | Команды этапа 4 |
| `CommandError(message, output)` | Ошибка команды с частичным выводом |

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
| `scripts/test_commands` | Все режимы `ls`, `cd`, `history`, `rev`, `cat` и их ошибки на `vfs/deep` |
| `scripts/test_script` | Скрипт со всеми командами, скрипт с ошибками и кодом возврата, переход в интерактивный режим, отсутствующий скрипт |
| `scripts/test_params` | Оба параметра в любом порядке, `--help`, неизвестный параметр, параметр без значения |

## Примеры использования

Команды этапа 4 (фрагмент `scripts/start_commands.txt`):

```
> python src/main.py --vfs vfs/deep
[debug] emulator parameters:
[debug]   vfs    = vfs/deep
[debug]   script = None
[debug] VFS 'deep' loaded into memory: 13 directories, 10 files
deep:/$ ls
etc  home  readme.txt  tmp  var
deep:/$ ls -al /home/user
-       26 .profile
d        - docs
d        - music
deep:/$ ls /nope /etc
/etc:
app  hosts
ls: cannot access '/nope': No such file or directory
deep:/$ cd /home/user/docs
deep:/home/user/docs$ cat report.txt drafts/draft1.txt
Annual report
=============
Everything is fine.
First draft of the report.
deep:/home/user/docs$ rev drafts/draft1.txt
.troper eht fo tfard tsriF
deep:/home/user/docs$ cat drafts
cat: drafts: Is a directory
deep:/home/user/docs$ cd ../..
deep:/home$ cd /readme.txt
cd: /readme.txt: Not a directory
deep:/home$ history 3
    8  cd ../..
    9  cd /readme.txt
   10  history 3
deep:/home$ exit
```

Сохранение VFS:

```
deep:/$ vfs-save out/deep_copy
vfs-save: VFS 'deep' saved to 'out/deep_copy'
deep:/$ vfs-save out/deep_copy
vfs-save: 'out/deep_copy': directory is not empty
deep:/$ vfs-save
vfs-save: usage: vfs-save PATH
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
