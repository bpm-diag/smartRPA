# ComputerLogger

<p align="center">
    <a href="https://www.python.org/" alt="Activity">
        <img src="https://img.shields.io/badge/Python-3.8-blue?style=flat&labelColor=3776AB&color=3776AB&logo=python&logoColor=white" /></a>
    <a href="#computerlogger" alt="Activity">
        <img src="https://img.shields.io/badge/Windows-10-blue?style=flat&labelColor=0078D6&color=0078D6&logo=windows&logoColor=white" /></a>
    <a href="#computerlogger" alt="Activity">
        <img src="https://img.shields.io/badge/MacOS-10.14-blue?style=flat&labelColor=999999&color=999999&logo=apple&logoColor=white" /></a>
    </br>
    <a href="#computerlogger" alt="Activity">
        <img src="https://img.shields.io/badge/Office-365-blue?style=flat&labelColor=E74025&color=E74025&logo=microsoft-office&logoColor=white" /></a>
    <a href="#computerlogger" alt="Activity">
        <img src="https://img.shields.io/badge/Chrome-80-blue?style=flat&labelColor=EDAD00&color=EDAD00&logo=google-chrome&logoColor=white" /></a>
    <a href="#computerlogger" alt="Activity">
        <img src="https://img.shields.io/badge/Firefox-72-blue?style=flat&labelColor=FF7139&color=FF7139&logo=mozilla-firefox&logoColor=white" /></a>
</p>

Log user interactions with the computer.

## Installation and execution:

1. **Install dependencies**

```
pip3 install -r requirements.txt
```

2. **Install browser extension** 
- _Google Chrome_: load unpacked `browserlogger` directory in `chrome://extensions/`
- _Mozilla Firefox_: load unpacked `browserlogger` directory in `about:debugging#/runtime/this-firefox` or install [`browserlogger-1.0.1.xpi`](https://github.com/marco2012/SystemLogger/tree/master/modules/browserlogger/web-ext-artifacts/browserlogger-1.0.1.xpi)

3. **Run main logger**

```
python3 mainLogger.py
```

The resulting log csv file will be in `/logs` directory.

## Modules

The project is composed by the following modules:

-   [x] GUI
-   [x] CSV server logger
-   [ ] System logger
-   [x] Browser logger
-   [ ] Office logger
-   [x] Clipboard logger

## Project structure

```
.
├── README.md
├── __pycache__
│   └── mainLogger.cpython-38.pyc
├── mainLogger.py
├── modules
│   ├── __init__.py
│   ├── __pycache__
│   ├── browserlogger
│   ├── clipboardEvents.py
│   ├── officeEvents.py
│   └── systemEvents.py
├── requirements.txt
└── utils
    ├── GUI.py
    ├── GUI_old.py
    ├── __init__.py
    ├── __pycache__
    ├── consumerServer.py
    └── icons
```
