<p align="center">
<img width="100%" src="docs/readme-header.png"><br/><br/>
    <a href="https://www.python.org/downloads/release/python-381/" alt="Activity">
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
        <img src="https://img.shields.io/badge/Opera-66-blue?style=flat&labelColor=FF1B2D&color=FF1B2D&logo=opera&logoColor=white" /></a> <br/><br/>
  <img width="80%" src="docs/gui.jpg"/> 


</p>

## Installation and execution:

#### 1. **Install dependencies**

```bash
pip3 install -r requirements.txt
```

For RPA you must also install `automagica` [(details here)](https://github.com/marco2012/ComputerLogger#RPA)
```bash
pip3 install -U automagica
```

#### 2. **Install browser extension** 

The browser extension supports 4 major browsers (<a href="https://gs.statcounter.com/browser-market-share/desktop/" target="_blank">80% market share combined</a>).

- [_Google Chrome_](https://www.google.com/chrome/): load unpacked `browserlogger` directory in `chrome://extensions/`
- [_Mozilla Firefox_](https://www.mozilla.org/en-US/firefox/new/): load unpacked `browserlogger` directory in `about:debugging#/runtime/this-firefox` or install [`browserlogger-1.0.3.xpi`](https://github.com/marco2012/ComputerLogger/tree/master/modules/browserlogger/web-ext-artifacts/browserlogger-1.0.3.xpi)
- [_Microsoft Edge (chromium)_](https://www.microsoft.com/en-us/edge): load unpacked `browserlogger` directory in `edge://extensions/`
- [_Opera_](https://www.opera.com/): load unpacked `browserlogger` directory in `opera:extensions`

#### 3. **Install Excel Addin (MacOS Only)**
The excel addin is required to enable logging <u>only on MacOS</u>. [`NodeJS`](https://nodejs.org/en/download/) must be installed to run this addin. 
```bash
cd modules/excelAddinMac 
npm install 
npm start
```

Once installed, choose the `Home` tab in Excel, and then choose the `Show Taskpane` button in the ribbon to open the add-in task pane.

#### 4. **Run main logger**

```bash
python3 mainLogger.py
```

The resulting log csv file will be in `/logs` directory.

https://github.com/marco2012/ComputerLogger/blob/master/docs/Features.pdf)

## RPA

*Robotic Process Automation* scripts are automatically generated for each log in `/RPA` directory

The following additional dependency is required for RPA:

```bash
pip3 install -U automagica
```
On Windows, if you get the error  `Cannot open include file: 'openssl/opensslv.h': No such file or directory` 

1. Install [Win32 OpenSSL v1.1.1d (32bit)](https://slproweb.com/download/Win32OpenSSL-1_1_1d.exe).
2. Open CMD as Admin and type:

```bash
set LIB=C:\Program Files (x86)\OpenSSL-Win32\lib;%LIB%
set INCLUDE=C:\Program Files (x86)\OpenSSL-Win32\include;%INCLUDE%
pip3 install -U automagica
```

## Modules

The project is composed by the following modules:

-   [x] GUI
-   [x] CSV server logger
-   [x] System logger
-   [x] Browser logger
-   [x] Office logger
-   [x] Clipboard logger

A complete list of features for each module is available in [`features.pdf`](https://github.com/marco2012/ComputerLogger/blob/master/docs/Features.pdf)

## Project structure

```
.
├── README.md
├── RPA
├── docs
├── logs
├── mainLogger.py
├── modules
│   ├── browserlogger
│   ├── clipboardEvents.py
│   ├── excelAddinMac
│   ├── officeEvents.py
│   └── systemEvents.py
├── requirements.txt
└── utils
    ├── GUI.py
    ├── config.py
    ├── consumerServer.py
    ├── generateRPAScript.py
    └── utils.py

```
