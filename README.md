# ComputerLogger

<p align="center">
    <a href="https://www.python.org/" alt="Activity">
        <img src="https://img.shields.io/badge/Python-v3.8.1-blue?style=flat&logo=python&logoColor=white" /></a>
    <a href="#" alt="Activity">
        <img src="https://img.shields.io/badge/Windows-10-blue?style=flat&logo=windows&logoColor=white" /></a>
    <a href="#" alt="Activity">
        <img src="https://img.shields.io/badge/MacOS-10.14-blue?style=flat&logo=apple&logoColor=white" /></a>
    <a href="#" alt="Activity">
        <img src="https://img.shields.io/badge/Progress-70%25-green?style=flat&logo=visual-studio-code&logoColor=white" /></a>
</p>

Log user interactions with the computer. 

Supports both Windows 10 and MacOS.

## Installation and execution:

1. **Install dependencies**
```
pip3 install -r requirements.txt
```
2. **Install browser extension** for *Google Chrome* (loading the unpacked `browserlogger` directory in `chrome://extensions/`) and *Mozilla Firefox* ([`browserlogger.xpi`](https://github.com/marco2012/SystemLogger/tree/master/modules/browserlogger/web-ext-artifacts/browserlogger.xpi))

3. **Run main logger**
```
python3 mainLogger.py
```

The resulting log csv file will be in `/logs` directory.

## Modules
The project is composed by the following modules:
- [x] GUI
- [x] CSV server logger
- [ ] System logger
- [x] Browser logger
- [ ] Office logger
- [x] Clipboard logger


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