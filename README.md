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
        <a href="#computerlogger" alt="Activity">
</p>

Log user interactions with the computer.

## Installation and execution:

1. **Install dependencies**

```
pip3 install -r requirements.txt
```

2. **Install browser extension** for _Google Chrome_ (loading the unpacked `browserlogger` directory in `chrome://extensions/`) and _Mozilla Firefox_ ([`browserlogger.xpi`](https://github.com/marco2012/SystemLogger/tree/master/modules/browserlogger/web-ext-artifacts/browserlogger.xpi))

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
├── mainLogger.py
├── modules
│   ├── browserlogger
│   ├── clipboardEvents.py
│   ├── officeEvents.py
│   └── systemEvents.py
├── requirements.txt
└── utils
    ├── GUI.py
    └── consumerServer.py
```
