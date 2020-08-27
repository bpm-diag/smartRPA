# ******************************
# UiPath
# Automatically generate RPA script compatible with UiPath. Called by
# GUI when main process is terminated and csv is available.
# ******************************
import sys

sys.path.append('../')  # this way main file is visible from this file
import os
import re
from lxml import etree
import uuid
import pandas
from multiprocessing.queues import Queue
from distutils.dir_util import copy_tree
import utils

# from utils.utils import MAIN_DIRECTORY
MAIN_DIRECTORY = "/Users/marco/Desktop/RPA/smartRPA"  # TEST


class UIPathXAML:

    def __init__(self, XAMLFilename="Main", status_queue: Queue = None):
        self.status_queue = status_queue
        self.RPA_directory = os.path.join(MAIN_DIRECTORY, 'RPA', '2020-test')  # test
        self.filename = XAMLFilename
        self.excelOpened = False
        self.BrowserOpened = False
        self.root = None
        self.sequence_id = 0
        self.typeInto_id = 0
        self.click_id = 0
        self.setToClipboard = 0
        self.browserScope = 0
        self.sendHotkey = 0
        self.navigateTo = 0
        self.comment = 0
        self.openApplication = 0
        self.excelApplication = 0
        self.writeCell = 0
        self.closeTab = 0
        self.saveWorkbook = 0
        self.closeWorkbook = 0

    def __createRoot(self):  # https://stackoverflow.com/a/31074030
        self.xmlns = "http://schemas.microsoft.com/netfx/2009/xaml/activities"
        self.mc = "http://schemas.openxmlformats.org/markup-compatibility/2006"
        self.mva = "clr-namespace:Microsoft.VisualBasic.Activities;assembly=System.Activities"
        self.sap = "http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation"
        self.sap2010 = "http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation"
        self.scg = "clr-namespace:System.Collections.Generic;assembly=mscorlib"
        self.sco = "clr-namespace:System.Collections.ObjectModel;assembly=mscorlib"
        self.x = "http://schemas.microsoft.com/winfx/2006/xaml"
        self.ui = "http://schemas.uipath.com/workflow/activities"

        etree.register_namespace("mc", self.mc)
        etree.register_namespace("mva", self.mva)
        etree.register_namespace("sap", self.sap)
        etree.register_namespace("sap2010", self.sap2010)
        etree.register_namespace("scg", self.scg)
        etree.register_namespace("sco", self.sco)
        etree.register_namespace("x", self.x)
        etree.register_namespace("ui", self.ui)

        nsmap = {
            None: self.xmlns,
            "mc": self.mc,
            "mva": self.mva,
            "sap": self.sap,
            "sap2010": self.sap2010,
            "scg": self.scg,
            "x": self.x,
            "ui": self.ui,
        }

        qnames = {
            etree.QName(self.x, "Class"): "Main",
            etree.QName(self.sap2010, "WorkflowViewState.IdRef"): "ActivityBuilder_1",
            etree.QName(self.mc, "Ignorable"): "sap sap2010",
            etree.QName(self.mva, "VisualBasic.Settings"): "{x:Null}",
        }

        self.root = etree.Element(
            etree.QName(self.xmlns, "Activity"),
            qnames,
            nsmap=nsmap
        )

    def __createTextExpression(self):
        textExpression = etree.Element('TextExpression.NamespacesForImplementation')
        collection = etree.Element(
            etree.QName(self.sco, "Collection"),
            {etree.QName(self.x, "TypeArguments"): "x:String"},
        )
        props = ["System.Activities", "System.Activities.Statements", "System.Activities.Expressions",
                 "System.Activities.Validation", "System.Activities.XamlIntegration", "Microsoft.VisualBasic",
                 "Microsoft.VisualBasic.Activities", "System", "System.Collections", "System.Collections.Generic",
                 "System.Data", "System.Diagnostics", "System.Drawing", "System.IO", "System.Linq", "System.Net.Mail",
                 "System.Xml", "System.Xml.Linq", "UiPath.Core", "UiPath.Core.Activities", "System.Windows.Markup"]
        for text in props:
            s = etree.Element(etree.QName(self.x, "String"))
            s.text = text
            collection.append(s)
        textExpression.append(collection)
        self.root.append(textExpression)

        textExpression = etree.Element('TextExpression.ReferencesForImplementation')
        collection = etree.Element(
            etree.QName(self.sco, "Collection"),
            {etree.QName(self.x, "TypeArguments"): "AssemblyReference"},
        )
        props = ["System.Activities", "Microsoft.VisualBasic", "mscorlib", "System.Data", "System", "System.Drawing",
                 "System.Core", "System.Xml", "System.Xml.Linq", "PresentationFramework", "WindowsBase",
                 "PresentationCore", "System.Xaml", "UiPath.System.Activities", "UiPath.UiAutomation.Activities",
                 "UiPath.System.Activities.Design", "System.ValueTuple", "System.ServiceModel", "UiPath.Excel",
                 "UiPath.Mail", "UiPath.CV"]
        for text in props:
            s = etree.Element("AssemblyReference")
            s.text = text
            collection.append(s)
        textExpression.append(collection)
        self.root.append(textExpression)

    def __createMainSequence(self):
        self.sequence_id += 1
        self.mainSequence = etree.Element(
            etree.QName(None, "Sequence"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Sequence_{self.sequence_id}",
                etree.QName(None, "DisplayName"): "MainSequence"
            },
        )
        variables = etree.Element("Sequence.Variables")
        # variable = etree.Element(
        #     etree.QName(None, "Variable"),
        #     {
        #         etree.QName(self.x, "TypeArguments"): "ui:Browser",
        #         etree.QName(None, "Name"): "browserReference"
        #     },
        # )
        # variables.append(variable)
        variables.extend([
            etree.Element(
                etree.QName(None, "Variable"),
                {
                    etree.QName(self.x, "TypeArguments"): "ui:Browser",
                    etree.QName(None, "Name"): "browserReference"
                },
            ),
            etree.Element(
                etree.QName(None, "Variable"),
                {
                    etree.QName(self.x, "TypeArguments"): "ui:WorkbookApplication",
                    etree.QName(None, "Name"): "spreadsheetReference"
                },
            )
        ])
        state = etree.Element(etree.QName(self.sap, "WorkflowViewStateService.ViewState"))
        dictionary = etree.Element(
            etree.QName(self.scg, "Dictionary"),
            {etree.QName(self.x, "TypeArguments"): "x:String, x:Object"},
        )
        boolean = etree.Element(
            etree.QName(self.x, "Boolean"),
            {etree.QName(self.x, "Key"): "IsExpanded"},
        )
        boolean.text = "True"

        dictionary.append(boolean)
        state.append(dictionary)
        self.mainSequence.append(variables)
        self.mainSequence.append(state)
        self.root.append(self.mainSequence)

    def __createSequence(self, children: list, displayName: str = "Do"):
        self.sequence_id += 1
        sequence = etree.Element(
            etree.QName(None, "Sequence"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Sequence_{self.sequence_id}",
                etree.QName(None, "DisplayName"): displayName
            },
        )
        state = etree.Element(etree.QName(self.sap, "WorkflowViewStateService.ViewState"))
        dictionary = etree.Element(
            etree.QName(self.scg, "Dictionary"),
            {etree.QName(self.x, "TypeArguments"): "x:String, x:Object"},
        )
        boolean = etree.Element(
            etree.QName(self.x, "Boolean"),
            {etree.QName(self.x, "Key"): "IsExpanded"},
        )
        boolean.text = "True"
        dictionary.append(boolean)
        state.append(dictionary)
        sequence.append(state)
        [sequence.append(child) for child in children]
        return sequence

    def createBaseFile(self):
        self.__createRoot()
        self.__createTextExpression()
        self.__createMainSequence()

    def writeXmlToFile(self):
        # uipath_template = os.path.join(MAIN_DIRECTORY, 'utils', 'UiPath_Template')
        # copy_tree(uipath_template, os.path.join(RPA_directory, 'UiPath'))
        filename = os.path.join(self.RPA_directory, 'UiPath', f"{self.filename}.xaml")
        with open(filename, "wb") as writer:
            # etree.indent(self.root, space="	")
            writer.write(etree.tostring(etree.Comment('SmartRPA by marco2012 https://github.com/marco2012/smartRPA'),
                                        pretty_print=True))
            writer.write(etree.tostring(etree.Comment('Developed at DIAG - Sapienza University of Rome'),
                                        pretty_print=True))
            writer.write(etree.tostring(etree.Comment(f'Generated from {self.filename}'),
                                        pretty_print=True))
            writer.write(etree.tostring(self.root, pretty_print=True))

    def __openBrowser(self, url: str = "", activities: list = None):
        openBrowser = etree.Element(
            etree.QName(self.ui, "OpenBrowser"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"OpenBrowser_1",
                etree.QName(None, "CommunicationMethod"): "{x:Null}",
                etree.QName(None, "BrowserType"): "Chrome",
                etree.QName(None, "DisplayName"): "Open Browser",
                etree.QName(None, "Hidden"): "False",
                etree.QName(None, "NewSession"): "True",
                etree.QName(None, "Private"): "False",
                etree.QName(None, "UiBrowser"): "[browserReference]",
                etree.QName(None, "Url"): url,
            },
        )
        body = etree.Element(
            etree.QName(self.ui, "OpenBrowser.Body"),
        )
        activityAction = etree.Element(
            etree.QName(None, "ActivityAction"),
            {etree.QName(self.x, "TypeArguments"): "x:Object"},
        )
        activityActionArgument = etree.Element(
            etree.QName(None, "ActivityAction.Argument"),
        )
        delegateinargument = etree.Element(
            etree.QName(None, "DelegateInArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "x:Object",
                etree.QName(None, "Name"): "ContextTarget"
            },
        )
        activityActionArgument.append(delegateinargument)
        activityAction.append(activityActionArgument)

        if activities:
            activityAction.append(self.__createSequence(activities))

        body.append(activityAction)
        openBrowser.append(body)
        self.mainSequence.append(openBrowser)

    def __attachBrowser(self, activities: list):
        self.browserScope += 1
        attachBrowser = etree.Element(
            etree.QName(self.ui, "BrowserScope"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"BrowserScope_{self.browserScope}",
                etree.QName(None, "Browser"): "[browserReference]",
                etree.QName(None, "BrowserType"): "Chrome",
                etree.QName(None, "SearchScope"): "{x:Null}",
                etree.QName(None, "Selector"): "{x:Null}",
                etree.QName(None, "TimeoutMS"): "{x:Null}",
                etree.QName(None, "DisplayName"): "Attach Browser",
                etree.QName(None, "UiBrowser"): "[browserReference]",
            },
        )
        body = etree.Element(
            etree.QName(self.ui, "BrowserScope.Body"),
        )
        activityAction = etree.Element(
            etree.QName(None, "ActivityAction"),
            {etree.QName(self.x, "TypeArguments"): "x:Object"},
        )
        activityActionArgument = etree.Element(
            etree.QName(None, "ActivityAction.Argument"),
        )
        delegateinargument = etree.Element(
            etree.QName(None, "DelegateInArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "x:Object",
                etree.QName(None, "Name"): "ContextTarget"
            },
        )
        activityActionArgument.append(delegateinargument)
        activityAction.append(activityActionArgument)

        sequence = self.__createSequence(activities)

        activityAction.append(sequence)
        body.append(activityAction)
        attachBrowser.append(body)
        self.mainSequence.append(attachBrowser)

    def __target(self, xpath: str, xpath_full: str, timeout: str = ""):
        css_selector = f"css-selector='{self.__xpathToCssSelector(xpath_full)}'"
        if len(xpath.split(')/')) == 1:
            id = f"id='{self.__getIdFromXpath(xpath)}'"
        else:
            id = f"parentid='{self.__getIdFromXpath(xpath)}'"
        selector = f"<html app='chrome.exe' /><webctrl {css_selector} {id}/>"

        props = {
                etree.QName(None, "ClippingRegion"): "{x:Null}",
                etree.QName(None, "Element"): "{x:Null}",
                etree.QName(None, "Id"): str(uuid.uuid1()),
                etree.QName(None, "Selector"): selector,
            }
        if timeout:
            props[etree.QName(None, "TimeoutMS")] = timeout

        target = etree.Element(
            etree.QName(self.ui, "Target"),
            props
        )
        target_timeout = etree.Element(
            etree.QName(self.ui, "Target.TimeoutMS"),
        )
        target_timeout.append(
            etree.Element(
                etree.QName(None, "InArgument"),
                {etree.QName(self.x, "TypeArguments"): "x:Int32"}
            )
        )
        if not timeout:
            target.append(target_timeout)
        waitForReady = etree.Element(
            etree.QName(self.ui, "Target.WaitForReady"),
        )
        waitForReady.append(
            etree.Element(
                etree.QName(None, "InArgument"),
                {etree.QName(self.x, "TypeArguments"): "ui:WaitForReady"}
            )
        )
        target.append(waitForReady)
        return target

    def __typeInto(self, text: str, xpath: str, xpath_full: str, displayName: str = "Type into 'INPUT'"):
        self.typeInto_id += 1
        typeInto = etree.Element(
            etree.QName(self.ui, "TypeInto"),
            {
                etree.QName(None, "AlterIfDisabled"): "{x:Null}",
                etree.QName(None, "ClickBeforeTyping"): "True",
                etree.QName(None, "DelayBefore"): "{x:Null}",
                etree.QName(None, "DelayBetweenKeys"): "{x:Null}",
                etree.QName(None, "DelayMS"): "{x:Null}",
                etree.QName(None, "EmptyField"): "True",
                etree.QName(None, "SendWindowMessages"): "{x:Null}",
                etree.QName(None, "SimulateType"): "{x:Null}",
                etree.QName(None, "Activate"): "True",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"TypeInto_{self.typeInto_id}",
                etree.QName(None, "Text"): text,
            },
        )
        typeIntoTarget = etree.Element(
            etree.QName(self.ui, "TypeInto.Target"),
        )
        typeIntoTarget.append(self.__target(xpath, xpath_full))
        typeInto.append(typeIntoTarget)
        return typeInto

    def __click(self, xpath: str, xpath_full: str, clickType="CLICK_SINGLE", mouseButton="BTN_LEFT",
                displayName: str = "Click Item"):
        self.click_id += 1
        click = etree.Element(
            etree.QName(self.ui, "Click"),
            {
                etree.QName(None, "AlterIfDisabled"): "{x:Null}",
                etree.QName(None, "DelayBefore"): "{x:Null}",
                etree.QName(None, "DelayMS"): "{x:Null}",
                etree.QName(None, "ClickType"): clickType,
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "KeyModifiers"): "None",
                etree.QName(None, "MouseButton"): mouseButton,
                etree.QName(None, "SendWindowMessages"): "{x:Null}",
                etree.QName(None, "SimulateClick"): "{x:Null}",
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Click_{self.click_id}",
            },
        )

        clickCursorPosition = etree.Element(
            etree.QName(self.ui, "Click.CursorPosition"),
        )
        cursorPosition = etree.Element(
            etree.QName(self.ui, "CursorPosition"),
            {etree.QName(None, "Position"): "Center"}
        )
        offsetx = etree.Element(
            etree.QName(self.ui, "CursorPosition.OffsetX")
        )
        offsetx.append(
            etree.Element(
                etree.QName(None, "InArgument"),
                {etree.QName(self.x, "TypeArguments"): "x:Int32"}
            )
        )
        offsety = etree.Element(
            etree.QName(self.ui, "CursorPosition.OffsetY")
        )
        offsety.append(
            etree.Element(
                etree.QName(None, "InArgument"),
                {etree.QName(self.x, "TypeArguments"): "x:Int32"}
            )
        )
        cursorPosition.extend([offsetx, offsety])
        clickCursorPosition.append(cursorPosition)

        clickTarget = etree.Element(
            etree.QName(self.ui, "Click.Target"),
        )
        clickTarget.append(self.__target(xpath, xpath_full, timeout="800"))

        click.append(clickCursorPosition)
        click.append(clickTarget)
        return click

    def __xpathToCssSelector(self, xpath: str):
        css = re.sub(r'\[(.)\]', '', xpath.lower())
        css = css.replace('/html/', '').replace('/', '>')
        return css

    def __getIdFromXpath(self, xpath: str):
        return xpath[xpath.find("(") + 1:xpath.find(")")].replace('"', '')

    def __navigateTo(self, url: str, displayName: str = "Navigate To"):
        self.navigateTo += 1
        navigateTo = etree.Element(
            etree.QName(self.ui, "NavigateTo"),
            {
                etree.QName(None, "Browser"): "[browserReference]",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"NavigateTo_{self.navigateTo}",
                etree.QName(None, "Url"): url,
            },
        )
        return navigateTo

    def __navigateToInNewTab(self, url: str, activities: list = None):
        return self.__openApplication(arguments=f"-new-tab {url}",
                                      path="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                                      selector="<wnd app='chrome.exe'/>", displayName="Navigate in New Tab",
                                      activities=activities)

    def __closeTab(self):
        self.closeTab += 1
        return etree.Element(
            etree.QName(self.ui, "CloseTab"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"CloseTab_{self.comment}",
                etree.QName(None, "Browser"): "{x:Null}",
                etree.QName(None, "DisplayName"): "Close tab",
            },
        )

    def __comment(self, text: str):
        self.comment += 1
        return etree.Element(
            etree.QName(self.ui, "Comment"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Comment_{self.comment}",
                etree.QName(None, "Text"): text,
            },
        )

    def __openApplication(self, arguments: str = "{x:Null}", path="{x:Null}", selector="{x:Null}",
                          displayName: str = "Open Application", activities: list = None):
        self.openApplication += 1
        openApplication = etree.Element(
            etree.QName(self.ui, "OpenApplication"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"OpenApplication_{self.openApplication}",
                etree.QName(None, "ApplicationWindow"): "{x:Null}",
                etree.QName(None, "TimeoutMS"): "{x:Null}",
                etree.QName(None, "WorkingDirectory"): "{x:Null}",
                etree.QName(None, "Arguments"): arguments,
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "FileName"): path,
                etree.QName(None, "Selector"): selector,
            },
        )
        body = etree.Element(
            etree.QName(self.ui, "OpenApplication.Body"),
        )
        activityAction = etree.Element(
            etree.QName(None, "ActivityAction"),
            {etree.QName(self.x, "TypeArguments"): "x:Object"},
        )
        activityActionArgument = etree.Element(
            etree.QName(None, "ActivityAction.Argument"),
        )
        delegateinargument = etree.Element(
            etree.QName(None, "DelegateInArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "x:Object",
                etree.QName(None, "Name"): "ContextTarget"
            },
        )
        activityActionArgument.append(delegateinargument)
        activityAction.append(activityActionArgument)

        if activities:
            activityAction.append(self.__createSequence(activities))

        body.append(activityAction)
        openApplication.append(body)
        return openApplication

    def __setToClipboard(self, text: str, displayName: str = "Set to clipboard"):
        self.setToClipboard += 1
        clipboard = etree.Element(
            etree.QName(self.ui, "SetToClipboard"),
            {
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"SetToClipboard_{self.setToClipboard}",
                etree.QName(None, "Text"): text,
            },
        )
        return clipboard

    def __sendHotkey(self, key: str = "{x:Null}", modifiers: str = "None", displayName: str = "Send Hotkey"):
        self.sendHotkey += 1
        hotkey = etree.Element(
            etree.QName(self.ui, "SendHotkey"),
            {
                etree.QName(None, "ClickBeforeTyping"): "{x:Null}",
                etree.QName(None, "DelayBefore"): "{x:Null}",
                etree.QName(None, "DelayBetweenKeys"): "{x:Null}",
                etree.QName(None, "DelayMS"): "{x:Null}",
                etree.QName(None, "EmptyField"): "{x:Null}",
                etree.QName(None, "SendWindowMessages"): "{x:Null}",
                etree.QName(None, "SpecialKey"): "{x:Null}",
                etree.QName(None, "Activate"): "True",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "Key"): key,
                etree.QName(None, "KeyModifiers"): modifiers,
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"SendHotkey_{self.sendHotkey}",
            }
        )
        sendHotkeyTarget = etree.Element(
            etree.QName(self.ui, "SendHotkey.Target"),
        )
        sendHotkeyTarget.append(self.__target())
        hotkey.append(sendHotkeyTarget)
        return hotkey

    def __excelSpreadsheet(self, workbookPath: str = "", password: str = "{x:Null}", attach=True,
                           displayName: str = "Excel Application Scope", activities: list = None):
        self.openApplication += 1
        if not workbookPath:
            # TODO
            #workbookPath = os.path.join(self.RPA_directory, "UiPathSpreadsheet.xlsx")
            desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
            workbookPath = r"C:\Users\marco\Desktop\excelDemo.xlsx"
        params = {
            etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelApplicationScope_{self.openApplication}",
            etree.QName(None, "Password"): password,
        }
        if attach:
            params[etree.QName(None, "ExistingWorkbook")] = "[spreadsheetReference]"
        else:
            params[etree.QName(None, "Workbook")] = "[spreadsheetReference]"
            params[etree.QName(None, "WorkbookPath")] = workbookPath

        excelApplication = etree.Element(
            etree.QName(self.ui, "ExcelApplicationScope"),
            params
        )
        body = etree.Element(
            etree.QName(self.ui, "ExcelApplicationScope.Body"),
        )
        activityAction = etree.Element(
            etree.QName(None, "ActivityAction"),
            {etree.QName(self.x, "TypeArguments"): "ui:WorkbookApplication"},
        )
        activityActionArgument = etree.Element(
            etree.QName(None, "ActivityAction.Argument"),
        )
        delegateinargument = etree.Element(
            etree.QName(None, "DelegateInArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "ui:WorkbookApplication",
                etree.QName(None, "Name"): "ExcelWorkbookScope"
            },
        )
        activityActionArgument.append(delegateinargument)
        activityAction.append(activityActionArgument)

        if activities:
            activityAction.append(self.__createSequence(activities))

        body.append(activityAction)
        excelApplication.append(body)
        self.mainSequence.append(excelApplication)

    def __writeCell(self, cell: str, sheetName: str, text: str):
        self.writeCell += 1
        displayName = f"Write Cell {cell}"
        writeCell = etree.Element(
            etree.QName(self.ui, "ExcelWriteCell"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelWriteCell_{self.writeCell}",
                etree.QName(None, "Cell"): cell,
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "SheetName"): sheetName,
                etree.QName(None, "Text"): text,
            },
        )
        return writeCell

    def __saveWorkbook(self, displayName: str = "Save Workbook"):
        self.saveWorkbook += 1
        return etree.Element(
            etree.QName(self.ui, "ExcelSaveWorkbook"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelSaveWorkbook_{self.saveWorkbook}",
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __closeWorkbook(self, displayName: str = "Close Workbook"):
        self.closeWorkbook += 1
        return etree.Element(
            etree.QName(self.ui, "ExcelCloseWorkbook"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelSaveWorkbook_{self.closeWorkbook}",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "Workbook"): "[spreadsheetReference]",
            },
        )

    def buildTestFile(self):
        self.__openBrowser(
            "https://docs.google.com/forms/d/e/1FAIpQLSeI8_vYyaJgM7SJM4Y9AWfLq-tglWZh6yt7bEXEOJr_L-hV1A/viewform?formkey=dGx0b1ZrTnoyZDgtYXItMWVBdVlQQWc6MQ",
            activities=[
                self.__typeInto("salve sono salvatore",
                                "/html/body/div/div[2]/form/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input"),
                self.__click(
                    "/html/body/div/div[2]/form/div[2]/div/div[2]/div[3]/div/div/div[2]/div[1]/div/span/div/div[1]/label/div/div[1]/div/div[3]/div")
            ],
        )
        self.__attachBrowser([
            self.__navigateToInNewTab("https://apple.com")
        ])

    def __generateRPAHelper(self, previousCategory, row):
        if previousCategory is None or previousCategory == row['category']:
            return row['category']

    def __generateRPA(self, df: pandas.DataFrame):
        # check if dataframe contains values
        if df.empty:
            return False

        self.mainSequence.append(self.__comment("// Generated using SmartRPA https://github.com/bpm-diag/smartRPA"))

        # if dataframe contains browser related events add openBrowser element
        if not df.query('category=="Browser"').empty:
            url = df.loc[df['category'] == 'Browser', 'browser_url'].iloc[0]
            self.__openBrowser(url=url)

        # if dataframe contains excel events, add excel scope element
        v = df['concept:name'].values
        if 'newWorkbook' in v:
            self.__excelSpreadsheet(workbookPath="", attach=False)
        if 'openWorkbook' in v:
            ow = df.loc[df['concept:name'] == 'openWorkbook']
            path = utils.utils.convertToWindowsPath(ow['event_src_path'], ow['org:resource'])
            self.__excelSpreadsheet(workbookPath=path, attach=False)

        browserActivities = []
        excelActivities = []
        systemActivities = []
        previousCategory = df.loc[0, 'category']

        for index, row in df.iterrows():
            ######
            # Variables
            ######
            try:
                e = row['event_type']
                timestamp = row['timestamp']
                user = row['user']
            except KeyError:
                e = row['concept:name']
                timestamp = row['time:timestamp']
                user = row['org:resource']

            wb = row['workbook']
            sh = row['current_worksheet']
            cell_value = utils.utils.unicodeString(row['cell_content'])
            cell_range = row['cell_range']
            range_number = row['cell_range_number']
            app = row['application']
            cb = utils.utils.processClipboard(row['clipboard_content'])
            path = ""
            currentCategory = row["category"]
            if not pandas.isna(row['event_src_path']) and row['event_src_path'] != '':
                path = row['event_src_path']
                path = utils.utils.convertToWindowsPath(path, user)
                item_name = path.replace('\\', r'\\')
            dest_path = ""
            if not pandas.isna(row['event_dest_path']) and row['event_dest_path'] != '':
                dest_path = row['event_dest_path']
                dest_path = utils.utils.convertToWindowsPath(
                    dest_path, user)
            url = "about:blank"
            if not pandas.isna(row['browser_url']):
                url = row['browser_url']
            id = ""
            if not pandas.isna(row['id']):
                id = row['id']
            xpath = ""
            if not pandas.isna(row['xpath']):
                xpath = row['xpath']
            xpath_full = row['xpath_full']
            value = utils.utils.unicodeString(row['tag_value'])

            ######
            # Check sequence
            ######
            if previousCategory != currentCategory:
                previousCategory = currentCategory
                if browserActivities:
                    self.__attachBrowser(activities=browserActivities)
                    browserActivities.clear()
                if excelActivities:
                    self.__excelSpreadsheet(activities=excelActivities)
                    excelActivities.clear()

            ######
            # Browser
            ######
            if e == "newTab" and int(id) != 0:
                browserActivities.append(self.__navigateToInNewTab(""))
            if e == "selectTab":
                browserActivities.append(self.__sendHotkey(id, "Ctrl", f"Select tab {id}"))
            if e == "closeTab":
                browserActivities.append(self.__closeTab())
            if (e in ["clickLink", "typed", "reload"]) and ('chrome-extension' not in url):
                browserActivities.append(self.__navigateTo(url))
            if e == "mouseClick" or e == "clickButton" or e == "clickRadioButton" or e == "clickCheckboxButton":
                browserActivities.append(
                    self.__click(xpath, xpath_full, displayName=f"Clicking {row['tag_category'].lower()}"))
            if e == "doubleClick" and xpath != '':
                browserActivities.append(self.__click(xpath, xpath_full, clickType="CLICK_DOUBLE"))
            if e == "changeField":
                if row['tag_category'] == "SELECT":
                    pass
                else:
                    browserActivities.append(self.__typeInto(value, xpath, xpath_full))

            ######
            # Excel
            ######
            # if e in ["newWorkbook", "openWorkbook"]:
            #     excelActivities.append(self.__excelSpreadsheet(workbookPath=path, attach=False))
            if e in ["addWorksheet", "WorksheetAdded"]:
                excelActivities.append(self.__writeCell(cell="", sheetName=sh, text=""))
            if e in ["selectWorksheet", "WorksheetActivated"]:
                pass
            if e == "getCell":
                pass
            if e in ["editCellSheet", "editCell", "editRange"]:
                excelActivities.append(self.__writeCell(cell=cell_range, sheetName=sh, text=cell_value))
            if e == "getRange":
                pass
            if e == "saveWorkbook":
                excelActivities.append(self.__saveWorkbook(displayName=f"Save {wb}"))
            if e == "printWorkbook":
                pass
            if e == "closeWindow":
                excelActivities.append(self.__closeWorkbook(displayName=f"Close {wb}"))

            ######
            # System
            ######


        # self.status_queue.put(f"[RPA] Generated UiPath RPA script")

    def generateUiPathRPA(self, df: pandas.DataFrame):
        self.createBaseFile()
        self.__generateRPA(df)
        self.writeXmlToFile()


if __name__ == '__main__':
    df = pandas.read_csv(
        "/Users/marco/Desktop/RPA/smartRPA/RPA/2020-08-25_10-50-43/log/2020-08-25_10-50-43_combined.csv",
        encoding='utf-8-sig')
    UIPathXAML = UIPathXAML()
    UIPathXAML.generateUiPathRPA(df)
    # UIPathXAML.createBaseFile()
    # UIPathXAML.buildTestFile()
    # UIPathXAML.writeXmlToFile()
