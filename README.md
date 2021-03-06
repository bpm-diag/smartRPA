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

# What is SmartRPA

**Robotic Process Automation (RPA)** is a technology which automates mouse and keyboard interactions by means of a software (SW) robot to remove intensive routines.
The current generation of RPA tools is driven by predefined rules and manual configurations made by expert users rather than automated techniques.

**SmartRPA** is a cross-platform tool that tackles such issues. It allows to easily record event logs and to automatically generating executable RPA scripts that will drive a SW robots in emulating an observed user behavior (previously recorded in dedicated UI logs) during the enactment of a routine of interest.

## Authors

**SmartRPA** has been developed at **DIAG**, Department of Computer, Control, and Management Engineering _Antonio Ruberti_ in **Sapienza University of Rome** by:

- [Simone Agostinelli](https://phd.uniroma1.it/web/SIMONE-AGOSTINELLI_nP1523559_IT.aspx)
- [Marco Lupia](https://marco2012.github.io/)
- [Andrea Marrella](http://www.dis.uniroma1.it/marrella/)
- [Massimo Mecella](http://www.diag.uniroma1.it/users/massimo%20mecella)

The **associated paper** is available on [Springer](https://doi.org/10.1007/978-3-030-58779-6_8), and has been presented at the [RPA Forum](https://congreso.us.es/bpm2020/calls/rpa/) of _18th International Conference on Business Process Management_.

A **screencast** of the tool is available on [Vimeo](https://vimeo.com/marco2012/smartRPA).

## Architecture

The architecture of SmartRPA integrates five main SW components.

<p align="center">
  <img width="55%" src="images/architecture.jpeg"/>
</p>

**Key features** include:

- [x] **Action Logger**, log user behaviour, cross-platform, modular, supports wide range of applications;
- [x] **Log Processing**, generates both CSV and XES event log;
- [x] **Event abstraction**, abstracts events to a higher level;
- [x] **Process Discovery**, selects the most suitable routine variant to automate and generates high-level flowchart diagram, thus skipping completely the manual modeling activity;
- [x] **Decision Points**, discover differencies between multiple traces in a process and build a new routine based on user decisions;
- [x] **RPA**, implements and enacts a SW robot emulating a routine reflecting the observed behavior (either the most frequent one or the one based on decision points). Available both as a cross-platform _Python script_ and as a _UiPath_ project.

A **list of events** supported by the Action Logger is available in [`SmartRPA_events.pdf`](https://github.com/bpm-diag/smartRPA/blob/master/images/SmartRPA_events.pdf).

The full **documentation** of the tool is available [here](https://bpm-diag.github.io/smartRPA/).

# Installation and execution:

**NOTE**: If you only want the action logger to record event logs without further analysis, you can find it [here](https://github.com/bpm-diag/smartRPA/tree/action_logger).

### 1. **Install dependencies**

[Python](https://www.python.org/downloads/) ≥ 3.7 (_64bit_) is required.

- Install [Visual Studio C/C++ Build Tools](#0-visual-studio-windows-only) on Windows and [Brew](https://brew.sh) on MacOS
- Install **project** dependencies _(required to record UI log)_

  ```bash
  pip3 install -r requirements.txt
  ```

- Install **Process Discovery** dependencies _(required to perform process discovery analysis)_

  [Details here](#process-discovery-dependencies)

- Install **RPA** dependencies _(required to run RPA SW Robot)_

  [Details here](#rpa-dependencies)

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

## Process Discovery dependencies

The following dependencies are required to enable process discovery analysis, a key component of the tool.

#### 0) Visual Studio (Windows Only)

<img width="40%" src="images/visual_studio.png">

- On **Windows**, [Visual Studio C/C++ Build Tools](https://visualstudio.microsoft.com/en/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16) must be installed.
  It is vital to install all C++ related development tools like:

  - Windows 10 SDK
  - Visual C++ tools for CMake
  - C++ x64/x86 build tools

  If you encounter errors like `Microsoft Visual C++ 14.0 is required`, [check here](https://www.scivision.co/python-windows-visual-c-14-required/).

#### 1) PM4PY

To enable process discovery techniques you must install [PM4PY](https://pm4py.fit.fraunhofer.de/features) python module.

- On **Windows**:

  1. Make sure you installed [Visual Studio C/C++ Build Tools](#0-visual-studio-windows-only).
  2. Install the latest version of [graphviz](https://www2.graphviz.org/Packages/stable/windows/10/cmake/Release/x64/). Make sure to add it to system PATH. Detailed instructions [here](https://forum.graphviz.org/t/new-simplified-installation-procedure-on-windows/224).
  3. `pip3 install pm4py==1.5.0.1`

    <details>
    <summary>
        Click to show how to <b>fix installation errors</b> on Windows
    </summary>
    </br>

  If you get the error <code>ERROR: Could not find a version that satisfies the requirement ortools</code> make sure you are using <a href="https://www.python.org/downloads/windows/">64bit version of Python3</a>.

    </details>
  <br>

- On **MacOS**:

  1. Make sure you installed [brew](https://brew.sh/) package manager
  2. Install graphviz with `brew install graphviz`
  3. `pip3 install pm4py==1.5.0.1`

    <details>
    <summary>
        Click to show how to <b>fix installation errors</b> on MacOS
    </summary>
    </br>

  If you get an error during installation:

  - If you're on **MacOS 10.14 Mojave**, run the following command as suggested [here](https://github.com/python-pillow/Pillow/issues/3438#issuecomment-435169249), and then, in the same terminal window, install `pm4py` again

    ```
    sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /
    ```

  - If you're on **MacOS 10.15 Catalina**, run the following command as suggested [here](https://github.com/python-pillow/Pillow/issues/3438#issuecomment-543812237), and then, in the same terminal window, install `pm4py` again

    ```
    export CPATH=`xcrun --show-sdk-path`/usr/include
    ```

  - If you're on **MacOS 11.0 Big Sur**, install the latest nightly build version of `scikit-learn` running the following command and then install `pm4py` again

    ```
    pip3 install --pre --extra-index https://pypi.anaconda.org/scipy-wheels-nightly/simple scikit-learn
    ```

    </details>

#### 2) Python-Levenshtein (Windows Only)

This package provides a 4-10x speedup in String Matching.

- On **Windows**:
  1.  Make sure you installed [Visual Studio C/C++ Build Tools](#0-visual-studio-windows-only)
  2.  `pip3 install python-Levenshtein==0.12.0`

## RPA dependencies

SmartRPA generates two types of SW Robots in the `/RPA` directory:

1. a cross-platform executable **Python script**, available on both Windows and MacOS
2. a **UiPath project**, available only on Windows

The advantages of the UiPath integration is that the generated SW Robot can be easily customized by the end user.

### Python script

The cross-platform python script requires the following dependencies to work.

#### 1) Automagica

To run the generated RPA scripts you must install `automagica` module available in the `libraries` directory.

`pip3 install libraries/Automagica-2.0.25-py3-none-any.whl`

  <details>
  <summary>
      Click to show how to <b>fix installation errors</b> on Windows
  </summary>
  </br>

1. Make sure you are using <a href="https://www.python.org/ftp/python/3.8.1/python-3.8.1-amd64.exe">64bit version of Python3</a>
2. Install `Win64 OpenSSL v1.1.1` from <a href="https://slproweb.com/products/Win32OpenSSL.html">this website</a>. When prompted select _"Copy OpenSSL DLLs to: the Windows system directory"_
3. Open CMD as <i>admin</i> and type (one command per line):

```cmd
set LIB=C:\Program Files\OpenSSL-Win64\lib;%LIB%
set INCLUDE=C:\Program Files\OpenSSL-Win64\include;%INCLUDE%
pip3 install libraries/Automagica-2.0.25-py3-none-any.whl
```

</details>

#### 2) Chromedriver

Install _chromedriver_ to enable automation in Google Chrome.

Make sure to install the release that matches your Google Chrome version (check `chrome://settings/help`). A complete list of releases can be found [here](https://pypi.org/project/chromedriver-binary/#history).

```bash
pip3 install chromedriver-binary
```

<details>
<summary>
    Click to show how to <b>fix installation errors</b> on MacOS
</summary>
<br>
If you get the error <code>RuntimeError: Failed to download chromedriver archive</code>

1. Navigate to `/Applications/Python 3.x/` folder
2. Run `Install Certificates.command` file
3. Install the package again

<a href="https://stackoverflow.com/a/42107877">Reference</a>

If you don't find the `Python 3.8` folder under `/Applications`, make sure you installed Python using <a href="https://www.python.org/downloads/mac-osx/">the official installer</a> and not from a package manager like brew.

</details>

### UiPath (Windows Only)

The generated UiPath project requires _UiPath Studio_, available at [https://www.uipath.com/product/studio](https://www.uipath.com/product/studio) .

# Recap

To sum up, you should have installed:

- Action Logger dependencies
  - `pip3 install -r requirements.txt`
  - [Browser extension](#2-install-browser-extension)
  - [Excel AddIn (MacOS Only)](#3-install-excel-addin-macos-only)
- [Process Discovery dependencies](#process-discovery-dependencies)
  - [Visual Studio C/C++ Build Tools (Windows Only)](#0-visual-studio-windows-only)
  - [PM4PY](#1-pm4py)
  - [Python Levenshtein (Windows Only)](#2-python-levenshtein-windows-only)
- [RPA dependencies](#rpa-dependencies)
  - [Python script](#python-script)
    - [Automagica](#1-automagica)
    - [Chromedriver](#2-chromedriver)
  - [UiPath](#uipath-windows-only)

After installing the dependencies, you can [run the tool](#4-run-main-logger).
