# korean_lunar_calendar
> Library to convert Korean lunar-calendar to proleptic Gregorian calendar.

## Overview
Korean calendar and Chinese calendar is same lunar calendar but have different date.

For more on Lunar Calendar, you can read [KoreanLunarCalendar.md](./KoreanLunarCalendar.md).

This follow the KARI(Korea Astronomy and Space Science Institute)
한국 양음력 변환 (한국천문연구원 기준) - 네트워크 연결 불필요
```
음력 지원 범위 (1000년 01월 01일 ~ 2050년 11월 18일)
Korean Lunar Calendar (1000-01-01 ~ 2050-11-18)

양력 지원 범위 (1000년 02월 13일 ~ 2050년 12월 31일)
Gregorian Calendar (1000-02-13 ~ 2050-12-31)
```
[Example Site](https://usingsky.github.io/korean_lunar_calendar_js)

## Docs

- [korean\_lunar\_calendar](#korean_lunar_calendar)
	- [Overview](#overview)
	- [Docs](#docs)
	- [Install](#install)
	- [Import](#import)
	- [Example](#example)
	- [Validation](#validation)
	- [Docker](#docker)
	- [Contribute/Dev](#contributedev)
		- [VSCode](#vscode)
		- [Auto-docstring](#auto-docstring)
		- [Install dev/test packages](#install-devtest-packages)
		- [Static Type Checker `[dev]`](#static-type-checker-dev)
		- [Linter `[dev]`](#linter-dev)
		- [Formatter `[dev]`](#formatter-dev)
		- [Tox `[dev, tox]`](#tox-dev-tox)
		- [pre-commit `[pre-commit]`](#pre-commit-pre-commit)
	- [Other languages](#other-languages)




## Install

```bash
pip install korean_lunar_calendar
```

## Import

```python
from korean_lunar_calendar import KoreanLunarCalendar
```

## Example

Korean Solar Date -> Korean Lunar Date (양력 -> 음력)

```python
calendar = KoreanLunarCalendar()

# params : year(년), month(월), day(일)
calendar.set_solar_date(2017, 6, 24)

# Lunar Date (ISO Format)
print(calendar.lunar_iso_format())

# Korean GapJa String
print(calendar.get_gap_ja_string())

# Chinese GapJa String
print(calendar.get_chinese_gap_ja_string())
```

```
[Result]
2017-05-01 Intercalation
정유년 병오월 임오일 (윤월)
丁酉年 丙午月 壬午日 (閏月)
```

Korean Lunar Date -> Korean Solar Date (음력 -> 양력)

```python
calendar = KoreanLunarCalendar()

# params : year(년), month(월), day(일), intercalation(윤달여부)
calendar.set_lunar_date(1956, 1, 21, False)

# Solar Date (ISO Format)
print(calendar.solar_iso_format())

# Korean GapJa String
print(calendar.get_gap_ja_string())

# Chinese GapJa String
print(calendar.get_chinese_gap_ja_string())
```

```
[Result]
1956-03-03
병신년 경인월 기사일
丙申年 庚寅月 己巳日
```

## Validation

Check for invalid date input

```python
calendar = KoreanLunarCalendar()

# invalid date
calendar.set_lunar_date(99, 1, 1, False) # => return False
calendar.set_solar_date(2051, 1, 1) # => return False

# OK
calendar.set_lunar_date(1000, 1, 1, False) # => return True
calendar.set_solar_date(2050, 12, 31) # => return True
```

## Docker

If you want to run it in a Docker container (general ubuntu container using `uv` & python 3.13), you can:
* Build the image:
	```bash
	make docker-build
	# or
	NAME='korean_lunar_calendar' bash -c 'docker build -t $NAME -f ./Docker/Dockerfile .'
	```
* Run the container (mounting the repo directory):
	```bash
	make docker-run
	# or
	NAME='korean_lunar_calendar' bash -c 'docker run --rm -it -v .:/root/korean_lunar_calendar --name $NAME $NAME'
	```
* Access the container:
	```bash
	make docker-bash
	# or
	NAME='korean_lunar_calendar' bash -c 'docker exec -it $NAME /bin/bash'
	```


## Contribute/Dev

### VSCode

`.vscode` contains:
* the prefered default settings: `settings.json`
* the recommended extension, to ease your coding experience: `extensions.json`\
	Heading to `Extensions`, you can look for `@recommended`, this will list the extensions from the file list. You are then free to install the ones you want.

The list is as follow:
* `"charliermarsh.ruff"`: ''A Visual Studio Code extension with support for the Ruff linter and formatter.''
* `"gruntfuggly.todo-tree"`: ''Show TODO, FIXME, etc. comment tags in a tree view''
* `"ms-python.debugpy"`: ''Python Debugger extension using debugpy.''
* `"ms-python.mypy-type-checker"`: ''Type checking support for Python files using Mypy.''
* `"ms-python.python"`: ''Python language support with extension access points for IntelliSense (Pylance), Debugging (Python Debugger), linting, formatting, refactoring, unit tests, and more.''
* `"ms-vscode.makefile-tools"`: ''Provide makefile support in VS Code: C/C++ IntelliSense, build, debug/run.''
* `"njpwerner.autodocstring"`: ''Generates python docstrings automatically'' 
* `"oderwat.indent-rainbow"`: ''Makes indentation easier to read'', Color the indentations
* `"redhat.vscode-yaml"`: ''YAML Language Support by Red Hat, with built-in Kubernetes syntax support''

### Auto-docstring

Following a Google Docstring Template (`docstring_template.mustache`), and taking informations from the function prototype/header (including type annotations), the VSCode extension `"njpwerner.autodocstring"`, allows you to auto-generate the skeleton of the docstring, simply by typing `"""` rightly indented under the function prototype/header, and `Enter` when prompted `Generate Docstring`.

This allows to keep consistency in the docstring while leveraging the typing of the function prototype/header.

### Install dev/test packages

Install all the packages, including the ones for testing `[dev, tox]`, and for pre-commit hook `[pre-commit]`:
```bash
make dev-install
# or
uv sync --all-groups
```

### Static Type Checker `[dev]`

```bash
make mypy
# or
uv run mypy .
```

### Linter `[dev]`

```bash
make lint
# or
uv run ruff check .
```

### Formatter `[dev]`

```bash
make format
# or
uv run ruff format --diff .
```

### Tox `[dev, tox]`

`tox` handles the creation of python environments (in `.tox/`) with different python versions, and allows to thus run the tests for all these python versions.

In its current configuration (`tox.ini`), it runs:
* the tests for different python versions (from py3.5 to py3.13)
* the formatter
* the linter
* the static type checker

To run it:
```bash
make tox-rerun
# or
uv run tox --parallel
```
If you want to force the recreation of the environments:
```bash
make tox-run
# or
uv run tox -r --parallel
```
* `-r`, `--recreate`: recreate the tox environments


### pre-commit `[pre-commit]`

`pre-commit` is a package that allows to easily integrate steps that will be triggered before commit when you call `git commit`. This is normally done by asking `pre-commit` to install the steps (see `.pre-commit-config.yaml`) as a git hook:
```bash
make pre-commit-enforce
# or
uv run pre-commit install
```
These steps are selected from a collection and are versioned. To understand to the latest versions:
```bash
make update-pre-commit-hooks
# or
uv run pre-commit autoupdate
```
If you do not want to use it as a pre-commit git hook, you can just directly run it:
```bash
make pre-commit
# or
uv run pre-commit run --all-files --show-diff-on-failure
```



## Other languages

- Java : [https://github.com/usingsky/KoreanLunarCalendar](https://github.com/usingsky/KoreanLunarCalendar)
- Python : [https://github.com/usingsky/korean_lunar_calendar_py](https://github.com/usingsky/korean_lunar_calendar_py)
- Javascript : [https://github.com/usingsky/korean_lunar_calendar_js](https://github.com/usingsky/korean_lunar_calendar_js)


