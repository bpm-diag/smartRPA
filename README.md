# ComputerLogger

#### Log user interactions with the computer.

<p align="center">
    <a href="https://www.python.org/" alt="Activity">
        <img src="https://img.shields.io/badge/Python-3.8-blue?style=flat&labelColor=3776AB&color=3776AB&logo=python&logoColor=white" /></a>
    <a href="#computerlogger" alt="Activity">
        <img src="https://img.shields.io/badge/Javascript-6-blue?style=flat&labelColor=F7DF1E&color=F7DF1E&logo=javascript&logoColor=white" /></a>
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
        <img src="https://img.shields.io/badge/Edge-80-blue?style=flat&labelColor=0078D7&color=0078D7&logo=microsoft-edge&logoColor=white" /></a>
    <a href="#computerlogger" alt="Activity">
        <img src="https://img.shields.io/badge/Opera-66-blue?style=flat&labelColor=FF1B2D&color=FF1B2D&logo=opera&logoColor=white" /></a>
</p>

<p align="center">
  <img src="docs/gui.jpg" width="80%" /> 
</p>

## Installation and execution:

1. **Install dependencies**

```
pip3 install -r requirements.txt
```

2. **Install browser extension** 

The browser extension supports 4 major browsers (<a href="https://gs.statcounter.com/browser-market-share/desktop/" target="_blank">80% market share combined</a>).

- [_Google Chrome_](https://www.google.com/chrome/): load unpacked `browserlogger` directory in `chrome://extensions/`
- [_Mozilla Firefox_](https://www.mozilla.org/en-US/firefox/new/): load unpacked `browserlogger` directory in `about:debugging#/runtime/this-firefox` or install [`browserlogger-1.0.3.xpi`](https://github.com/marco2012/SystemLogger/tree/master/modules/browserlogger/web-ext-artifacts/browserlogger-1.0.3.xpi)
- [_New Microsoft Edge_](https://www.microsoft.com/en-us/edge): load unpacked `browserlogger` directory in `edge://extensions/`
- [_Opera_](https://www.opera.com/): load unpacked `browserlogger` directory in `opera:extensions`

3. **Install Excel Addin (MacOS Only)**
The excel addin is required to enable logging only on MacOS. [`NodeJS`](https://nodejs.org/en/download/) must be installed. 
```
cd modules/excelAddinMac 
npm install 
npm start
```

Once installed, choose the `Home` tab in Excel, and then choose the `Show Taskpane` button in the ribbon to open the add-in task pane.

4. **Run main logger**

```
python3 mainLogger.py
```

The resulting log csv file will be in `/logs` directory.

## Modules

The project is composed by the following modules:

-   [x] GUI
-   [x] CSV server logger
-   [x] System logger
-   [x] Browser logger
-   [x] Office logger
-   [x] Clipboard logger

A complete list of features for each module is available in [`features.pdf`](https://github.com/marco2012/SystemLogger/blob/master/docs/Features.pdf)

## Project structure

```
.
├── README.md
├── docs
│   └── Features.pdf
├── mainLogger.py
├── modules
│   ├── browserlogger
│   ├── clipboardEvents.py
│   ├── officeEvents.py
│   └── systemEvents.py
├── requirements.txt
└── utils
    ├── GUI.py
    ├── consumerServer.py
    ├── icons
    ├── removeEmptyLogs.py
    └── utils.py
```
