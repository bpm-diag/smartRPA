<p align="center">
<img width="100%" src="images/readme-header.png"><br/><br/>
    <a href="https://www.python.org/downloads/" alt="Activity">
        <img src="https://img.shields.io/badge/Python-3.8 (x64)-blue?style=flat&labelColor=3776AB&color=3776AB&logo=python&logoColor=white" /></a>
    <a href="#" alt="Activity">
        <img src="https://img.shields.io/badge/Javascript-ES6-blue?style=flat&labelColor=F7DF1E&color=F7DF1E&logo=javascript&logoColor=white" /></a>
    <a href="#" alt="Activity">
        <img src="https://img.shields.io/badge/Windows-10-blue?style=flat&labelColor=0078D6&color=0078D6&logo=windows&logoColor=white" /></a>
    <a href="#" alt="Activity">
        <img src="https://img.shields.io/badge/MacOS-10.15-blue?style=flat&labelColor=999999&color=999999&logo=apple&logoColor=white" /></a>
    </br>
    <a href="https://www.office.com/" alt="Activity">
        <img src="https://img.shields.io/badge/Office-365-blue?style=flat&labelColor=E74025&color=E74025&logo=microsoft-office&logoColor=white" /></a>
    <a href="https://www.google.com/chrome/" alt="Activity">
        <img src="https://img.shields.io/badge/Chrome-85-blue?style=flat&labelColor=EDAD00&color=EDAD00&logo=google-chrome&logoColor=white" /></a>
    <a href="https://www.mozilla.org/en-US/firefox" alt="Activity">
        <img src="https://img.shields.io/badge/Firefox-72-blue?style=flat&labelColor=FF7139&color=FF7139&logo=mozilla-firefox&logoColor=white" /></a>
    <a href="https://www.microsoft.com/en-us/edge" alt="Activity">
        <img src="https://img.shields.io/badge/Edge-80-blue?style=flat&labelColor=0078D7&color=0078D7&logo=microsoft-edge&logoColor=white" /></a>
    <a href="https://www.opera.com/" alt="Activity">
        <img src="https://img.shields.io/badge/Opera-66-blue?style=flat&labelColor=FF1B2D&color=FF1B2D&logo=opera&logoColor=white" /></a> 
    <br/>
    <a href="#"><img src="https://img.shields.io/badge/Sapienza University of Rome-blue?style=flat&labelColor=781A2D&color=781A2D&logoColor=white" /></a> 
  <br/><br/>
  <img width="80%" src="images/gui.png"/>

</p>

# This version only includes the Action Logger.

If you want the full tool with process discovery and RPA capabilities, check the [`master` branch](https://github.com/bpm-diag/smartRPA/tree/master).

# Installation and execution:

### 1. **Install dependencies**

[Python](https://www.python.org/downloads/) ≥ 3.7 (_64bit_) is required.

- <details>
  <summary>
      Install <a href="https://visualstudio.microsoft.com/en/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16">Visual Studio C/C++ Build Tools</a> on Windows
  </summary>
  </br>

  <img width="40%" src="images/visual_studio.png">

  It is vital to install all C++ related development tools like:

  - Windows 10 SDK
  - Visual C++ tools for CMake
  - C++ x64/x86 build tools

  If you encounter errors like `Microsoft Visual C++ 14.0 is required`, [check here](https://www.scivision.co/python-windows-visual-c-14-required/).

  </details>

- Install [Brew](https://brew.sh) on MacOS
- Install **project** dependencies

  ```bash
  pip3 install -r requirements.txt
  ```

### 2. **Install browser extension**

The browser extension is required to log browser events. It is available in `extensions/browserlogger` and supports 4 major browsers:

- [_Google Chrome_](https://www.google.com/chrome/): load unpacked `browserlogger` directory in `chrome://extensions/`

- [_Mozilla Firefox_](https://www.mozilla.org/en-US/firefox/new/): install [`browserlogger.xpi`](https://github.com/bpm-diag/smartRPA/blob/develop/extensions/browserlogger/browserlogger.xpi?raw=true) in `about:addons`

- [_Microsoft Edge (chromium)_](https://www.microsoft.com/en-us/edge): load unpacked `browserlogger` directory in `edge://extensions/`

- [_Opera_](https://www.opera.com/): load unpacked `browserlogger` directory in `opera:extensions`

Once main logger is running, **you must click** on the browser extension to enable it.

### 3. **Install Excel Addin (MacOS Only)**

The excel addin is required to log Excel events <u>only on MacOS</u>.

[`Node.js`](https://nodejs.org/en/download/) must be installed to run this addin.

```bash
cd extensions/excelAddinMac
npm install # install dependencies
npm start   # sideload Add-in
npm stop    # stop server
```

<details>
<summary>
    Click to show how to <b>activate the Add-in</b> in Excel
</summary>
</br>

<ol type="a">
  <li>Start the Action Logger selecting Excel module</li>
  <li>Go to <code>Insert</code> tab</li>
  <li>Click on the small down-arrow to the right of <code>My Add-ins</code> > <code>OfficeLogger</code></li>
  <img width="50%" src="images/excel_logger.png">
  <li>Go to <code>Home</code> tab</li>
  <li>Click the <code>Show Taskpane</code> button in the ribbon</li>
  <li>Enable the checkbox</li>
</ol>

If you don't find <code>OfficeLogger</code> under <code>My Add-ins</code>, copy <code>extensions/excelAddinMac/manifest.xml</code> into <code>~/Library/Containers/com.microsoft.Excel/Data/Documents/wef</code>, as described <a href="https://docs.microsoft.com/en-us/office/dev/add-ins/testing/sideload-an-office-add-in-on-ipad-and-mac#sideload-an-add-in-in-office-on-mac">here</a>.

</details>

### 4. **Run main logger**

```bash
python3 main.py
```

<details>
<summary>
    Click to show how to <b>fix</b> <code>ModuleNotFoundError</code> error on Windows
</summary>
</br>

If you have installed all the [dependencies](#1-install-dependencies)(`pip3 install -r requirements.txt `) but you still get <code>ModuleNotFoundError</code>, run the tool with:

```bash
py main.py
```

</details>
<br>

The resulting event log will be saved in `/RPA` directory.

**NOTE**: In the Action Logger, when selecting a *Microsoft Office* program to log, it will automatically be opened. This is required to correctly handle events. The opened window should not be closed until logging is completed.
