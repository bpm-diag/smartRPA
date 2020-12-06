# ******************************
# UiPath
# Automatically generate RPA script compatible with UiPath. Called by
# GUI when main process is terminated and csv is available.
# ******************************
import difflib
import ntpath
import modules
import utils
import string
from distutils.dir_util import copy_tree
from multiprocessing.queues import Queue
import pandas
import uuid
from lxml import etree
import re
import os
import sys
from collections import defaultdict
import ntpath
import modules.events.systemEvents
from deprecated.sphinx import deprecated

sys.path.append('../')  # this way main file is visible from this file


class UIPathXAML:
    """
    Automatically generate RPA script compatible with UiPath. Called by
    GUI when main process is terminated and csv is available.
    """

    def __init__(self, csv_file_path: str, status_queue: Queue, df: pandas.DataFrame):
        """

        :param csv_file_path: path of event log csv
        :param status_queue: queue to print messages on GUI
        :param df: dataframe of a trace of execution to automate
        """

        # either most frequent dataframe or original dataframe
        self.df = df
        self.df1 = self.__df_without_duplicates()
        self.status_queue = status_queue
        # directories
        self.csv_file_path = csv_file_path
        self.RPA_directory = utils.utils.getRPADirectory(self.csv_file_path)
        self.UiPath_directory = os.path.join(self.RPA_directory, utils.utils.SW_ROBOT_FOLDER, 'UiPath')
        # xaml attributes
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
        self.closeApplication = 0
        self.startProcess = 0
        self.createFile = 0
        self.createDirectory = 0
        self.moveFile = 0
        self.powerpointApplicationCard = 0
        self.insertSlide = 0
        self.switch = 0
        self.inputDialog = 0

    # dataframe utils
    @deprecated(version='1.2.0', reason="Not in use anymore since decision point analysis now occurs before RPA script generation.")
    def __df_without_duplicates(self):
        """
        Filter unsupported events from dataframe, namely events that

        :return: dataframe without unsupported events
        """
        unsupported = ["selectTab", "closeTab", "selectWorksheet", "WorksheetActivated",
                       "closePresentation", "savePresentation", "newPresentation", "saveDocument",
                       "printWorkbook", "getRange", "getCell", "saveWorkbook"]
        # remove rows not supported by uipath
        self.df = self.df[~self.df['concept:name'].isin(unsupported)]
        # add hostname column to dataframe
        self.df['browser_url_hostname'] = \
            self.df['browser_url'].apply(lambda url: utils.utils.getHostname(url)).fillna('')
        # add duplicated column to dataframe, boolean indicating if each row is duplicated
        # The rows with duplicated = True are unique, the other ones should run in separate cases of a switch
        duplication_subset = ['concept:name', 'category', 'application', 'browser_url_hostname', 'xpath']
        self.df['duplicated'] = self.df.duplicated(subset=duplication_subset, keep=False)
        # dataframe without duplicates and with 'duplicated' column indicated if the row should go to main sequence or switch
        return self.df.drop_duplicates(subset=duplication_subset, ignore_index=True, keep='first')

    @deprecated(version='1.2.0', reason="Not in use anymore since decision point analysis now occurs before RPA script generation.")
    def __howManyDecisionVariables(self):
        """
        return number of groups that will be converted into switch statements in UiPath
        used to determine how many variables should be added to main sequence

        :return: number of decision points
        """


        # group rows based on 'duplicated' value
        # rows with duplicated=True should go to main sequence, otherwise they should go in a switch case
        # https://towardsdatascience.com/pandas-dataframe-group-by-consecutive-same-values-128913875dba
        g = self.df1.groupby((self.df1['duplicated'].shift() != self.df1['duplicated']).cumsum())
        # create list of groups
        gl = [g.get_group(x)['duplicated'].iloc[0] for x in g.groups]
        # return number of groups with duplicated = False
        return gl.count(False)

    # def __equalGroups(self, g: pandas.DataFrameGroupBy, a: int, b: int, duplication_subset: list):
    #     return g.get_group(a)[duplication_subset].reset_index(drop=True).equals(
    #         g.get_group(b)[duplication_subset].reset_index(drop=True))

    @deprecated(version='1.2.0', reason="Not in use anymore since decision point analysis now occurs before RPA script generation.")
    def __generateTraceKeywords(self, options: list):
        """
        Used to generate keywords dataframe to explain different decision to user.

        Not in use anymore since decision point analysis now occurs before RPA script generation.

        :param options: list of traces
        :return: keywords dataframe
        """
        keywords = defaultdict(str)
        for trace in options:
            df2 = self.df.loc[(self.df['case:concept:name'] == trace) & (~self.df['duplicated'])]
            category = ','.join(df2['category'].unique())
            keywords[trace] += f"- {trace} -> CATEGORY: {category}"
            if 'Browser' in category:
                hostname = ','.join(df2['browser_url_hostname'].unique())
                keywords[trace] += f", URL: {hostname}"
                tag_value = ','.join(filter(None, map(lambda x: ntpath.basename(x), df2['tag_value'].unique())))
                if tag_value:
                    keywords[trace] += f", KEYWORDS: {tag_value}"
            if 'OperatingSystem' in category:
                path = ','.join(filter(None, df2['event_src_path'].unique()))
                if path:
                    keywords[trace] += f", PATH: {path}"
            if 'MicrosoftOffice' in category:
                cells = ','.join(filter(None, df2['cell_range'].unique()))
                if cells:
                    keywords[trace] += f", CELLS: {cells}"
                # take only the first 30 characters of cell content
                cell_content = ','.join(filter(None, map(lambda x: x[:30], df2['cell_content'].unique())))
                if cell_content:
                    keywords[trace] += f", KEYWORDS: {cell_content}"
        return list(keywords.values())

    # base
    def __createRoot(self):
        """
        Generate XML root with namespace declarations. The base XML file for UiPath starts here.

        reference https://stackoverflow.com/a/31074030

        """
        self.xmlns = "http://schemas.microsoft.com/netfx/2009/xaml/activities"
        self.mc = "http://schemas.openxmlformats.org/markup-compatibility/2006"
        self.mva = "clr-namespace:Microsoft.VisualBasic.Activities;assembly=System.Activities"
        self.sap = "http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation"
        self.sap2010 = "http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation"
        self.scg = "clr-namespace:System.Collections.Generic;assembly=mscorlib"
        self.sco = "clr-namespace:System.Collections.ObjectModel;assembly=mscorlib"
        self.x = "http://schemas.microsoft.com/winfx/2006/xaml"
        self.ui = "http://schemas.uipath.com/workflow/activities"
        self.upab = "clr-namespace:UiPath.PowerPoint.Activities.Business;assembly=UiPath.PowerPoint.Activities"
        self.upadb = "clr-namespace:UiPath.PowerPoint.Activities.Design.Business;assembly=UiPath.PowerPoint.Activities"

        etree.register_namespace("mc", self.mc)
        etree.register_namespace("mva", self.mva)
        etree.register_namespace("sap", self.sap)
        etree.register_namespace("sap2010", self.sap2010)
        etree.register_namespace("scg", self.scg)
        etree.register_namespace("sco", self.sco)
        etree.register_namespace("x", self.x)
        etree.register_namespace("ui", self.ui)
        etree.register_namespace("upab", self.upab)
        etree.register_namespace("upadb", self.upadb)

        nsmap = {
            None: self.xmlns,
            "mc": self.mc,
            "mva": self.mva,
            "sap": self.sap,
            "sap2010": self.sap2010,
            "scg": self.scg,
            "x": self.x,
            "ui": self.ui,
            "upab": self.upab,
            "upadb": self.upadb,
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
        """
        Append required text expressions to XML root

        """
        textExpression = etree.Element(
            'TextExpression.NamespacesForImplementation')
        collection = etree.Element(
            etree.QName(self.sco, "Collection"),
            {etree.QName(self.x, "TypeArguments"): "x:String"},
        )
        props = ["System.Activities", "System.Activities.Statements", "System.Activities.Expressions",
                 "System.Activities.Validation", "System.Activities.XamlIntegration", "Microsoft.VisualBasic",
                 "Microsoft.VisualBasic.Activities", "System", "System.Collections", "System.Collections.Generic",
                 "System.Data", "System.Diagnostics", "System.Drawing", "System.IO", "System.Linq", "System.Net.Mail",
                 "System.Xml", "System.Xml.Linq", "UiPath.Core", "UiPath.Core.Activities", "System.Windows.Markup",
                 "UiPath.Excel", "UiPath.PowerPoint.Activities", "UiPath.CV"]
        for text in props:
            s = etree.Element(etree.QName(self.x, "String"))
            s.text = text
            collection.append(s)
        textExpression.append(collection)
        self.root.append(textExpression)

        textExpression = etree.Element(
            'TextExpression.ReferencesForImplementation')
        collection = etree.Element(
            etree.QName(self.sco, "Collection"),
            {etree.QName(self.x, "TypeArguments"): "AssemblyReference"},
        )
        props = ["System.Activities", "Microsoft.VisualBasic", "mscorlib", "System.Data", "System", "System.Drawing",
                 "System.Core", "System.Xml", "System.Xml.Linq", "PresentationFramework", "WindowsBase",
                 "PresentationCore", "System.Xaml", "UiPath.System.Activities", "UiPath.UiAutomation.Activities",
                 "UiPath.System.Activities.Design", "System.ValueTuple", "System.ServiceModel", "UiPath.Excel",
                 "UiPath.CV", "UiPath.PowerPoint.Activities"]
        for text in props:
            s = etree.Element("AssemblyReference")
            s.text = text
            collection.append(s)
        textExpression.append(collection)
        self.root.append(textExpression)

    def __createMainSequence(self):
        """
        Create main sequence that will contain all other sequences and events and append it to root.

        """
        self.sequence_id += 1
        self.mainSequence = etree.Element(
            etree.QName(None, "Sequence"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Sequence_{self.sequence_id}",
                etree.QName(None, "DisplayName"): "MainSequence"
            },
        )
        variables = etree.Element("Sequence.Variables")
        variablesList = [
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
            ),
        ]
        for i in range(self.__howManyDecisionVariables()):
            variablesList.append(
                etree.Element(
                    etree.QName(None, "Variable"),
                    {
                        etree.QName(self.x, "TypeArguments"): "x:String",
                        etree.QName(None, "Name"): f"decision{i}"
                    },
                ),
            )
        variables.extend(variablesList)
        state = etree.Element(etree.QName(
            self.sap, "WorkflowViewStateService.ViewState"))
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

    def __createSequence(self, activities: list, displayName: str = "Do", key=None):
        """
        Create UiPath sequence element, which is a container for other elements.

        :param activities: list of activities inside the sequence
        :param displayName: name of the sequence
        :param key:
        :return: sequence
        """
        self.sequence_id += 1
        props = {
            etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Sequence_{self.sequence_id}",
            etree.QName(None, "DisplayName"): displayName
        }
        if key:
            props[etree.QName(self.x, "Key")] = str(key)
        sequence = etree.Element(
            etree.QName(None, "Sequence"),
            props
        )
        state = etree.Element(etree.QName(
            self.sap, "WorkflowViewStateService.ViewState"))
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
        [sequence.append(child) for child in activities]
        return sequence

    def createBaseFile(self):
        """
        Create base XAML file for UiPath.

        * create root element
        * add text expressions
        * add main sequence
        """
        self.__createRoot()
        self.__createTextExpression()
        self.__createMainSequence()

    def writeXmlToFile(self):
        """
        Copy UiPath template directory into current project and write XAML to file
        """
        RPA_filename = utils.utils.getFilename(
            self.csv_file_path).strip('_combined')
        uipath_template = os.path.join(
            utils.utils.MAIN_DIRECTORY, 'utils', 'UiPath_Template')
        copy_tree(uipath_template, self.UiPath_directory)
        filename = os.path.join(self.UiPath_directory, f"{RPA_filename}.xaml")
        with open(filename, "wb") as writer:
            writer.write(etree.tostring(etree.Comment('SmartRPA by marco2012 https://github.com/marco2012/smartRPA'),
                                        pretty_print=True))
            writer.write(etree.tostring(self.root, pretty_print=True))

    def __comment(self, text: str):
        """
        Create comment element
        :param text: text inside the comment
        :return: append comment to main sequence
        """
        self.comment += 1
        c = etree.Element(
            etree.QName(self.ui, "Comment"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Comment_{self.comment}",
                etree.QName(None, "Text"): text,
            },
        )
        self.mainSequence.append(c)

    @deprecated(version='1.2.0', reason="Not in use anymore since decision point analysis now occurs before RPA script generation.")
    def __inputDialog(self, options: list, label: str = None, title: str = "Decision point", displayName: str = None):
        """
        Create input dialog element

        :param options: list of options to display in dialog
        :param label: label of input dialog
        :param title: title of input dialog
        :param displayName: name of input dialog
        :return: input dialog
        """
        formattedOptions = '[{' + ', '.join(['"%s"' % x for x in options]) + '}]'
        if not displayName:
            displayName = f"Decision point {self.switch}"
        if not label:
            keywords = self.__generateTraceKeywords(options)
            n = "+Environment.NewLine+Environment.NewLine+"
            label = '"Which path do you want to take?:"' + n + \
                    n.join(['"%s"' % x for x in keywords])
        self.inputDialog += 1
        inputDialog = etree.Element(
            etree.QName(self.ui, "InputDialog"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"InputDialog_{self.inputDialog}",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "IsPassword"): "False",
                etree.QName(None, "Label"): f"[{label}]",
                etree.QName(None, "Title"): title,
                etree.QName(None, "Options"): formattedOptions,
            },
        )
        result = etree.Element(
            etree.QName(self.ui, "InputDialog.Result")
        )
        outArgument = etree.Element(
            etree.QName(None, "OutArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "x:String",
            }
        )
        outArgument.text = f"[decision{self.switch}]"
        result.append(outArgument)
        inputDialog.append(result)
        return inputDialog

    @deprecated(version='1.2.0', reason="Not in use anymore since decision point analysis now occurs before RPA script generation.")
    def __switch(self, caseActivities: dict, defaulActivity=None, condition=None, displayName: str = "Switch"):
        """
        Create switch element. Before each switch, an input dialog is needed to ask the user which case to choose

        :param caseActivities: dictionary of activities divided by trace
        :param defaulActivity: default case to execute
        :param condition: switch condition
        :param displayName: name of switch element
        :return: switch element
        """

        self.mainSequence.append(
            self.__inputDialog(options=list(caseActivities.keys()))
        )
        # if a specific condition is not provided, I use the decision variable previously declared in the main sequence
        # and used by the input variable to store the user choice.
        # there are N decision variables based on how many switches there will be, named decision0 to decisionN
        # each time the __switch function is called, the self.switch that starts from 0 number is incremented
        # as well as the decision variable
        if not condition:
            condition = f"decision{self.switch}"

        self.switch += 1
        switcher = {
            int: "x:Int32",
            str: "x:String",
            bool: "x:Boolean",
        }
        switch = etree.Element(
            etree.QName(None, "Switch"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Switch`1_{self.switch}",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(self.x, "TypeArguments"): switcher.get(type(condition), "x:Object"),
                etree.QName(None, "Expression"): f"[{condition}]",
            },
        )
        default = etree.Element(
            etree.QName(None, "Switch.Default"),
        )
        if defaulActivity:
            default.append(self.__createSequence([defaulActivity]))
        switch.append(default)

        for key, value in caseActivities.items():
            switch.append(self.__createSequence(activities=value, key=key))

        self.mainSequence.append(switch)

    # browser
    def __openBrowser(self, url: str = "", activities: list = None):
        """
        Open browser. This sequence contains browser events and it's used only once at the beginning of the project.

        :param url: open at specific url
        :param activities: list of activities to append
        :return: append open browser sequence to main sequence
        """
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
        """
        Attach browser element.
        This sequence contains browser events and it attaches to the OpenBrowser sequence created at the beginning.
        It is used every time there are browser events.

        :param activities: list of activities to append
        :return: Attach browser element
        """
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

        activityAction.append(self.__createSequence(
            activities, displayName="Browser events"))
        body.append(activityAction)
        attachBrowser.append(body)
        return attachBrowser
        # self.mainSequence.append(attachBrowser)

    def __target(self, xpath: str = "", xpath_full: str = "", idx: str = "",
                 app: str = "", title: str = "", timeout: str = "1000"):
        """
        Target element to click on.

        :param xpath: xpath of web element
        :param xpath_full: full xpath of web element
        :param idx: index of element in page
        :param app: name of the browser used to navigate (e.g. google chrome)
        :param title: title of the window of the browser
        :param timeout: timeout after which action is dismissed if element is not found
        :return: target element
        """
        selector = "{x:Null}"
        if xpath and xpath_full:
            css_selector = f"css-selector='{self.__xpathToCssSelector(xpath_full)}'"
            if len(xpath.split(')/')) == 1:
                id = f"id='{self.__getIdFromXpath(xpath)}'"
            else:
                id = f"parentid='{self.__getIdFromXpath(xpath)}'"
            if idx:
                elemIndex = f"idx='{idx}'"
            else:
                elemIndex = ""
            selector = f"<html app='chrome.exe' /><webctrl {css_selector} {id} {elemIndex}/>"
        elif app and title:
            selector = f"<wnd app='{app}' title='{title}' />"
        elif app:
            selector = f"<wnd app='{app}' />"

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

    def __typeInto(self,
                   text: str,
                   xpath: str = "", xpath_full: str = "", idx: str = "",
                   app: str = "", title: str = "",
                   displayName: str = "Type into 'INPUT'", emptyField: bool = True,
                   timeout: str = "1000", newLine: bool = False):
        """
        TypeInto element to type into web fields.

        Uses __target() method to create target element.

        :param text: text to be typed
        :param xpath: xpath of web element
        :param xpath_full: full xpath of web element
        :param idx: index  of web element
        :param app: name of the program used to navigate (e.g. google chrome)
        :param title: title of the window of the browser
        :param displayName: name of TypeInto element
        :param emptyField: if True, field is empied before typing
        :param timeout: timeout after which action is dismissed if element is not found
        :param newLine: add new line after typing
        :return: TypeInto element
        """
        self.typeInto_id += 1
        typeInto = etree.Element(
            etree.QName(self.ui, "TypeInto"),
            {
                etree.QName(None, "AlterIfDisabled"): "{x:Null}",
                etree.QName(None, "ClickBeforeTyping"): "True",
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "DelayBefore"): "{x:Null}",
                etree.QName(None, "DelayBetweenKeys"): "{x:Null}",
                etree.QName(None, "DelayMS"): "{x:Null}",
                etree.QName(None, "EmptyField"): str(emptyField),
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
        if xpath and xpath_full:
            target = self.__target(
                xpath=xpath, xpath_full=xpath_full, idx=idx, timeout=timeout)
        elif app and title:
            target = self.__target(app=app, title=title, timeout=timeout)
        else:
            target = self.__target(timeout=timeout)
        typeIntoTarget.append(target)
        typeInto.append(typeIntoTarget)
        return typeInto

    def __click(self, xpath: str, xpath_full: str, clickType="CLICK_SINGLE", mouseButton="BTN_LEFT",
                displayName: str = "Click Item"):
        """
        Element to click on web objects

        :param xpath: xpath of web element
        :param xpath_full: full xpath of web element
        :param clickType: type of click (single, double click)
        :param mouseButton: button of mouse to click (left, right, middle)
        :param displayName: name of click element in uipath
        :return: Click element
        """
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
        """
        Convert XPATH to CSS selector.

        The action logger records the XPATH for each web element so it can easily be identified by the SW robot.
        UiPath does not support selection of web elements using XPATH (which is more accurate), so conversion to CSS selector is needed.

        :param xpath:
        :return:
        """
        css = re.sub(r'\[([0-9]+)\]', '', xpath.lower())
        css = css.replace('/html/', '').replace('/', '>')
        return css

    def __getIdFromXpath(self, xpath: str):
        """
        Get ID of element from xpath

        :param xpath: xpath of web element
        :return: id of element
        """
        return xpath[xpath.find("(") + 1:xpath.find(")")].replace('"', '')

    def __getIdxFromXpath(self, a: str, b: str, list_index: int):
        """
        Compare current xpath to previous one to find differences in index.

        Since XPATH selection is not supported by UiPath, CSS selection is used.
        With this method, web elements are identified using their relative index on the page.

        This method calculates the index of an element relative to another.

        For example, in a google form, 3 consecutive text field have index 0 to 3.

        :param a: xpath of first element
        :param b: xpath of second element
        :param list_index: list of xpath column in dataframe
        :return: index of current element
        """

        # if list_index is 0, previous xpath is None so return empty string
        # to be comparable, xpath should have the same parent but they should not be equal,
        # otherwise difference would be 0
        if list_index > 0 and a != b and self.__getIdFromXpath(a) == self.__getIdFromXpath(b):
            # list of numbers
            aa = re.findall(r"\[\s*\+?(-?\d+)\s*\]", a)
            bb = re.findall(r"\[\s*\+?(-?\d+)\s*\]", b)
            idx = [j for i, j in zip(aa, bb) if i != j]
            try:
                return idx[0]
            except IndexError:
                return ""
        else:
            return ""

    def __navigateTo(self, url: str, displayName: str = "Navigate To"):
        """
        Element to navigate on a page

        :param url: url to open
        :param displayName: name of element in UiPath
        :return: navigateTo element
        """
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

    # def __navigateToInNewTab(self, url: str, activities: list = None):
    #     return self.__openApplication(arguments=f"-new-tab {url}",
    #                                   fileName="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    #                                   selector="<wnd app='chrome.exe'/>", displayName="Navigate in New Tab",
    #                                   activities=activities)

    def __closeTab(self):
        """
        Element to close tab

        :return: closeTab element
        """
        self.closeTab += 1
        return etree.Element(
            etree.QName(self.ui, "CloseTab"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"CloseTab_{self.closeTab}",
                etree.QName(None, "Browser"): "{x:Null}",
                etree.QName(None, "DisplayName"): "Close tab",
            },
        )

    # excel
    def __excelSpreadsheet(self, workbookPath: str = "", password: str = "{x:Null}", attach=True,
                           displayName: str = "Excel Application Scope", activities: list = None):
        """
        Element to handle excel spreadsheets.

        :param workbookPath: path of workbook to open
        :param password: workbook password (if present)
        :param attach: if True, attaches to a workbook already opened by UiPath, without opening it again
        :param displayName: name of element in UiPAth
        :param activities: list of activities to perform on opened excel workbook
        :return: ExcelApplicationScope element
        """
        self.openApplication += 1
        if workbookPath == "":
            workbookPath = os.path.join(
                self.UiPath_directory, "UiPathSpreadsheet.xlsx")
        params = {
            etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelApplicationScope_{self.openApplication}",
            etree.QName(None, "Password"): password,
        }
        if attach:
            params[etree.QName(None, "ExistingWorkbook")
            ] = "[spreadsheetReference]"
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
            activityAction.append(self.__createSequence(
                activities, displayName="Excel events"))

        body.append(activityAction)
        excelApplication.append(body)
        # self.mainSequence.append(excelApplication)
        return excelApplication

    def __writeCell(self, cell: str, sheetName: str, text: str):
        """
        Write excel cell

        :param cell: position cell to write
        :param sheetName: name of sheet
        :param text: text to write
        :return: ExcelWriteCell element
        """
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
        """
        Save opened workbook

        :param displayName: name of element in UiPath
        :return: ExcelSaveWorkbook element
        """
        self.saveWorkbook += 1
        return etree.Element(
            etree.QName(self.ui, "ExcelSaveWorkbook"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelSaveWorkbook_{self.saveWorkbook}",
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __closeWorkbook(self, displayName: str = "Close Workbook"):
        """
        Close opened workbook

        :param displayName: name of element in UiPath
        :return: ExcelCloseWorkbook element
        """
        self.closeWorkbook += 1
        return etree.Element(
            etree.QName(self.ui, "ExcelCloseWorkbook"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"ExcelSaveWorkbook_{self.closeWorkbook}",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "Workbook"): "[spreadsheetReference]",
            },
        )

    # system
    def __openApplication(self, arguments: str = "{x:Null}", fileName: str = "{x:Null}", selector: str = "{x:Null}",
                          displayName: str = "Open Application", activities: list = None):
        """
        element to open specified application

        :param arguments: path of program to open
        :param fileName: name of program to open
        :param selector: windows selector
        :param displayName: name of element in UiPath
        :param activities: list of activities
        :return: OpenApplication element
        """
        self.openApplication += 1
        openApplication = etree.Element(
            etree.QName(self.ui, "OpenApplication"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"OpenApplication_{self.openApplication}",
                etree.QName(None, "ApplicationWindow"): "{x:Null}",
                etree.QName(None, "TimeoutMS"): "1000",
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "WorkingDirectory"): "{x:Null}",
                etree.QName(None, "Arguments"): arguments,
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "FileName"): fileName,
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

    def __openFileFolder(self, path: str, itemName: str):
        """
        open file or folder in windows explorer

        :param path: path of file or folder to open
        :param itemName: name of file or folder to open
        :return: OpenApplication element
        """
        return self.__openApplication(arguments=path,
                                      displayName=f"Open {itemName}",
                                      fileName="C:\\Windows\\explorer.exe",
                                      selector="<wnd app='explorer.exe' cls='CabinetWClass' />")

    def __closeApplication(self, app: str, title: str, displayName: str = "Start Process"):
        """
        Element to close an open application

        :param app: name of the application to close
        :param title: title of the application window
        :param displayName: name of the element in UiPath
        :return: CloseApplication element
        """
        self.closeApplication += 1
        close = etree.Element(
            etree.QName(self.ui, "CloseApplication"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"CloseApplication_{self.closeApplication}",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "ContinueOnError"): "True",
            },

        )
        closeApplicationTarget = etree.Element(
            etree.QName(self.ui, "CloseApplication.Target"),
        )
        closeApplicationTarget.append(self.__target(
            app=app, title=title, timeout="1000"))
        close.append(closeApplicationTarget)
        return close

    def __startProcess(self, path: str, displayName: str = "Start Process"):
        """
        Element to start specified process


        :param path: path of process to start
        :param displayName: name of element in UiPath
        :return: StartProcess element
        """
        self.startProcess += 1
        return etree.Element(
            etree.QName(self.ui, "StartProcess"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"StartProcess_{self.startProcess}",
                etree.QName(None, "Arguments"): "{x:Null}",
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "FileName"): path,
                etree.QName(None, "WorkingDirectory"): "{x:Null}",
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __setToClipboard(self, text: str, displayName: str = "Set to clipboard"):
        """
        Set specified text to clipboard

        :param text: text to be set to clipboard
        :param displayName: name of element in UiPath
        :return: SetToClipboard element
        """
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
        """
        Element to type specified sequence of keys

        :param key: letter to press
        :param modifiers: modifiers to press (like CTRL, ALT, etc)
        :param displayName: name of element in UiPath
        :return: SendHotkey element
        """
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

    def __createFile(self, path: str, displayName: str = "Create file"):
        """
        Element to create a file

        :param path: path of file to be created
        :param displayName: name of element in UiPath
        :return: CreateFile element
        """
        self.createFile += 1
        return etree.Element(
            etree.QName(self.ui, "CreateFile"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"CreateFile_{self.createFile}",
                etree.QName(None, "ContinueOnError"): "{x:Null}",
                etree.QName(None, "Name"): "{x:Null}",
                etree.QName(None, "Path"): path,
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __createDirectory(self, path: str, displayName: str = "Create file"):
        """
        Element to create a directory

        :param path: path of directory to be created
        :param displayName: name of element in UiPath
        :return: CreateDirectory element
        """
        self.createDirectory += 1
        return etree.Element(
            etree.QName(self.ui, "CreateDirectory"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"CreateDirectory_{self.createDirectory}",
                etree.QName(None, "ContinueOnError"): "{x:Null}",
                etree.QName(None, "Path"): path,
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __moveFile(self, from_path: str, to_path: str, displayName: str = "Move file"):
        """
        Element to move a file/folder

        :param from_path: path where te file/folder is
        :param to_path: destination path where to move the file/folder
        :param displayName: name of element in UiPath
        :return: MoveFile element
        """
        self.moveFile += 1
        return etree.Element(
            etree.QName(self.ui, "MoveFile"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"MoveFile_{self.moveFile}",
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "Destination"): to_path,
                etree.QName(None, "Overwrite"): "True",
                etree.QName(None, "Path"): from_path,
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    def __delete(self, path: str, displayName: str = "Delete file"):
        """
        Element to delete a file/folder

        :param path: path where te file/folder is
        :param displayName: name of element in UiPath
        :return: Delete element
        """
        self.moveFile += 1
        return etree.Element(
            etree.QName(self.ui, "Delete"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"Delete_{self.moveFile}",
                etree.QName(None, "ContinueOnError"): "True",
                etree.QName(None, "Path"): path,
                etree.QName(None, "DisplayName"): displayName,
            },
        )

    # powerpoint
    def __powerpointScope(self, num_slides: int, path: str = "", displayName: str = "PowerPoint Presentation"):
        """
        Element to handle powerpoint events.

        :param num_slides: number of slides to add to the presentation
        :param path: path of powerpoint presentation. If empty create a new file.
        :param displayName: name of element in UiPath
        :return: PowerPointApplicationCard element
        """
        self.powerpointApplicationCard += 1
        position = self.powerpointApplicationCard
        if not path:
            path = os.path.join(self.UiPath_directory, "presentation.xlsx")
        powerpointApplication = etree.Element(
            etree.QName(self.upadb, "PowerPointApplicationCard"),
            {
                etree.QName(self.sap2010,
                            "WorkflowViewState.IdRef"): f"PowerPointApplicationCard_{self.powerpointApplicationCard}",
                etree.QName(None, "Password"): "{x:Null}",
                etree.QName(None, "CreateIfNotExists"): "True",
                etree.QName(None, "DisplayName"): displayName,
                etree.QName(None, "PresentationPath"): path,
            }
        )
        body = etree.Element(
            etree.QName(self.upadb, "PowerPointApplicationCard.Body"),
        )
        activityAction = etree.Element(
            etree.QName(None, "ActivityAction"),
            {etree.QName(self.x, "TypeArguments")
             : "ui:IPresentationQuickHandle"},
        )
        activityActionArgument = etree.Element(
            etree.QName(None, "ActivityAction.Argument"),
        )
        delegateinargument = etree.Element(
            etree.QName(None, "DelegateInArgument"),
            {
                etree.QName(self.x, "TypeArguments"): "ui:IPresentationQuickHandle",
                etree.QName(None, "Name"): "powerpointReference"
            },
        )
        activityActionArgument.append(delegateinargument)
        activityAction.append(activityActionArgument)

        slides = [self.__insertSlide(position)
                  for position in range(1, num_slides + 1)]
        activityAction.append(self.__createSequence(
            slides, displayName="Powerpoint events"))

        body.append(activityAction)
        powerpointApplication.append(body)
        return powerpointApplication

    def __insertSlide(self, position):
        """
        Add slides to a presentation.

        :param position: where to add slides
        :return: InsertSlideX element
        """
        self.insertSlide += 1
        return etree.Element(
            etree.QName(self.upab, "InsertSlideX"),
            {
                etree.QName(self.sap2010, "WorkflowViewState.IdRef"): f"InsertSlideX_{self.insertSlide}",
                etree.QName(None, "LayoutName"): "{x:Null}",
                etree.QName(None, "SlideMasterName"): "{x:Null}",
                etree.QName(None, "DisplayName"): "Insert Slide",
                etree.QName(None, "InsertPosition"): str(position),
                etree.QName(None, "Presentation"): "[powerpointReference]",
            },
        )

    # generate RPA
    def __createOpenBrowser(self, df: pandas.DataFrame):
        """
        Method to insert openBrowser element at the beginning of the XAML file if browser events are present in the event log.

        :param df: input dataframe
        """
        # if dataframe contains browser related events add openBrowser element
        if not df.query('category=="Browser"').empty:
            url = df.loc[df['category'] == 'Browser', 'browser_url'].iloc[0]
            self.__openBrowser(url=url)

    def __createOpenExcel(self, df: pandas.DataFrame):
        """
        Method to insert openExcel element at the beginning of the XAML file if excel events are present in the event log.

        :param df: input dataframe
        """
        # if dataframe contains excel events, add excel scope element
        v = df['concept:name'].values
        if 'newWorkbook' in v:
            self.mainSequence.append(self.__excelSpreadsheet(workbookPath="", attach=False))
        if 'openWorkbook' in v:
            wb_path = df.loc[df['concept:name'] ==
                             'openWorkbook', 'event_src_path'].iloc[0]
            os_user = df['org:resource'].iloc[0]
            path = utils.utils.convertToWindowsPath(wb_path, os_user)
            self.mainSequence.append(self.__excelSpreadsheet(workbookPath=path, attach=False))

    def __generateActivities(self, df: pandas.DataFrame, row: pandas.Series):
        """
        Helper method called for each row of the dataframe to convert an event into a UiPath XML node.

        :param df: input dataframe
        :param row: current row of dataframe
        :return: XML node
        """
        ######
        # Variables
        ######
        # backwards compatibility with older logs
        try:
            e = row['event_type']
            timestamp = row['timestamp']
            user = row['user']
        except KeyError:
            e = row['concept:name']
            timestamp = row['time:timestamp']
            user = row['org:resource']

        cell_value = utils.utils.unicodeString(row['cell_content'])
        app = row['application']
        cb = utils.utils.processClipboard(row['clipboard_content'])
        path = ""
        item_name = ""
        if not pandas.isna(row['event_src_path']) \
                and row['event_src_path'] != '' \
                and '.tmp' not in row['event_src_path']:
            path = row['event_src_path']
            path = utils.utils.convertToWindowsPath(path, user)
            item_name = path.replace('\\', r'\\')
        dest_path = ""
        if not pandas.isna(row['event_dest_path']) \
                and row['event_dest_path'] != '' \
                and '.tmp' not in row['event_dest_path']:
            dest_path = row['event_dest_path']
            dest_path = utils.utils.convertToWindowsPath(dest_path, user)
        url = "about:blank"
        if not pandas.isna(row['browser_url']):
            url = row['browser_url']
        id = ""
        if not pandas.isna(row['id']):
            id = row['id']
        xpath = row['xpath']
        xpath_full = row['xpath_full']
        value = utils.utils.unicodeString(row['tag_value'])

        if e in ["logonComplete"]:
            return None

        ######
        # Browser
        ######
        if e == "newTab" and int(id) != 0:
            # browserActivities.append(self.__navigateToInNewTab(""))
            self.__comment("new tab event not supported by UiPath")
            return None
        if e == "selectTab":
            # browserActivities.append(self.__sendHotkey(id, "Ctrl", f"Select tab {id}"))
            return None
        if e == "closeTab":
            # browserActivities.append(self.__closeTab())
            return None
        if (e in ["clickLink", "typed", "reload", "link", "formSubmit"]) and not (
                any([x in url for x in ['chrome-extension', 'chrome-search://']])):
            return self.__navigateTo(url)
        if e == "mouseClick" or e == "clickButton" or e == "clickRadioButton" or e == "clickCheckboxButton":
            return self.__click(xpath, xpath_full, displayName=f"Clicking {row['tag_category'].lower()}")
        if e == "doubleClick" and xpath != '':
            return self.__click(xpath, xpath_full, clickType="CLICK_DOUBLE")
        if e == "changeField":
            if row['tag_category'] == "SELECT":
                return None
            else:
                # list of all xpaths in the dataframe having changeField as concept name
                # so the user inserted text in an input
                list_of_xpaths = df.loc[df['concept:name']
                                        == 'changeField']['xpath'].tolist()
                # current xpath
                b = xpath
                # index of current xpath
                list_index = list_of_xpaths.index(b)
                # previous xpath
                a = list_of_xpaths[list_index - 1]
                # compare current xpath to previous one to find differences
                # pass index of current xpath because if it's 0, previous is None so idx is empty
                idx = self.__getIdxFromXpath(a, b, list_index)
                return self.__typeInto(text=value, xpath=xpath, xpath_full=xpath_full, idx=idx, timeout="2000")

        ######
        # Excel
        ######
        if e in ["addWorksheet", "WorksheetAdded"]:
            return self.__writeCell(cell="", sheetName=row['current_worksheet'], text="")
        if e in ["selectWorksheet", "WorksheetActivated"]:
            return None
        if e == "getCell":
            return None
        if e in ["editCellSheet", "editCell", "editRange"]:
            return self.__writeCell(cell=row['cell_range'], sheetName=row['current_worksheet'], text=cell_value)
        if e == "getRange":
            return None
        if e == "saveWorkbook":
            return self.__saveWorkbook(displayName=f"Save {row['workbook']}")
        if e == "printWorkbook":
            return None
        if e == "closeWindow":
            return self.__closeWorkbook(displayName=f"Close {row['workbook']}")

        ######
        # System
        ######
        if (e == "copy" or e == "cut") and not pandas.isna(cb):
            return self.__setToClipboard(cb)
        if e == "paste" and row['category'] != 'Browser' and app != 'Excel':
            return self.__typeInto(text=cb, app=app + '*', title=row["title"],
                                   displayName=f"Paste into {row['title']}", emptyField=False, newLine=True)
        if e in ["pressHotkey", "hotkey"]:
            if 'hotkey' in df.columns:
                hotkey = row["hotkey"]
            else:
                hotkey = row["id"]
            modifiers = ', '.join(
                list(map(lambda x: string.capwords(x), hotkey.split('+')[:-1])))
            return self.__sendHotkey(key=hotkey[-1], modifiers=modifiers,
                                     displayName=f"Press {hotkey.upper()} - {row['description']}")
        if e in ["openFile", "openFolder"] and path:
            return self.__openFileFolder(path, item_name)
        if e == "programOpen":
            # don't open excel or powerpoint if there are events related to them in dataframe because it is already handled
            try:
                event_list = df['event_type'].tolist()
            except KeyError:
                event_list = df['concept:name'].tolist()
            if (app in ["EXCEL.EXE", "Microsoft Excel", "Microsoft Excel (MacOS)", "Microsoft Powerpoint",
                        "POWERPNT.EXE"]) and any(
                i in event_list for i in ["newWorkbook", "selectWorksheet", "WorksheetActivated", "newPresentation"]):
                return None
            if path and ntpath.basename(path) not in modules.events.systemEvents.programs_to_ignore:
                return self.__startProcess(path, displayName=f"Open {app}")
        if e == "programClose" and app not in modules.events.systemEvents.programs_to_ignore:
            title = row['title']
            displayName = f"Close {title}" if title else f"Close {app}"
            return self.__closeApplication(
                app=app + '*', title=row["title"], displayName=displayName)
        if e == "created" and path:
            if os.path.splitext(path)[1]:  # file
                return self.__createFile(path, displayName=f"Create {item_name}")
            else:  # directory
                return self.__createDirectory(path, displayName=f"Create {item_name}")
        if e == "Mount":
            self.mac_source_filepath = path
        if e in ["moved", "Unmount"] and path:
            # logs recorded on mac do not have dest_path
            if not dest_path:
                dest_path = path
                path = self.mac_source_filepath

            new_name = utils.utils.unicodeString(ntpath.basename(dest_path))
            if os.path.dirname(path) == os.path.dirname(dest_path):
                displayName = f"Rename file as {new_name}"
            else:
                displayName = f"Move file to {new_name}"
            return self.__moveFile(path, dest_path, displayName)
        if e == "deleted" and path:
            return self.__delete(path, displayName=f"Delete {item_name}")

        # word
        if e == "newDocument":
            return self.__startProcess(r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.exe",
                                       displayName="Open Word")
        if e == "saveDocument":
            return None

        # powerpoint
        if e == "newPresentation":
            # presPath = path if path else ""
            # self.__powerpointScope(path=presPath, insertSlide=False)
            return None
        if e == "newPresentationSlide" and not self.ppt_slides_inserted:
            self.ppt_slides_inserted = True
            presPath = path if path else ""
            num_slides = len(
                df[df['concept:name'] == 'newPresentationSlide'])
            return self.__powerpointScope(num_slides, path=presPath)
        if e == "savePresentation":
            return None
        if e == "closePresentation":
            return None

    # def __generateRPAWithDecision(self, df: pandas.DataFrame, decision: bool = False):
    #
    #     # at least 2 traces are needed for decision point
    #     if decision:
    #         assert len(df['case:concept:name'].drop_duplicates()) >= 2
    #
    #     # add comment to main sequence
    #     self.__comment("// Generated using SmartRPA available at https://github.com/bpm-diag/smartRPA")
    #
    #     # backwards compatibility
    #     if 'xpath_full' not in df.columns:
    #         df['xpath_full'] = df['xpath']
    #         self.__comment("// Clicking and typing into web elements is not supported with this event log. "
    #                        "Record log again with the latest version of SmartRPA")
    #
    #     # create open browser and open excel activities
    #     # all the other events relative to excel and browse are attached to this activities using sequence variables
    #     self.__createOpenBrowser(df)
    #     self.__createOpenExcel(df)
    #
    #     # lists to store xml nodes relative to different categories
    #     browserActivities = []
    #     excelActivities = []
    #     systemActivities = []
    #
    #     # dictionary with 2 keys: case id of a trace and category of events belonging to that trace
    #     # 2 keys are needed to keep track of different categories for each trace
    #     caseActivities = defaultdict(lambda: defaultdict(list))
    #
    #     # variables used when creating xml nodes
    #     self.ppt_slides_inserted = False
    #     #
    #     self.mac_source_filepath = ""
    #
    #     # previous category is used to detect a change in category and it's initialised as the category of the first row
    #     # When a change happens, nodes are added to sequence and lists are emptied
    #     previousCategory = df.loc[0, 'category']
    #     df['previousDuplicated'] = df['duplicated'].shift(1) if decision else True
    #
    #     for index, row in df.iterrows():
    #
    #         # define variables
    #         # duplicated row is only available when performing decision points
    #         duplicated = row['duplicated'] if decision else True
    #         previousDuplicated = row['previousDuplicated']
    #         caseid = row['case:concept:name']
    #         app = row['application']
    #         currentCategory = row["category"]
    #
    #         # define conditions used to determine when to append xml nodes to main sequence or switch
    #         # if category changes a new sequence should be written
    #         categoryChange = (previousCategory != currentCategory) and not \
    #             ((previousCategory == 'OperatingSystem' and currentCategory == 'Clipboard') or
    #              (previousCategory == 'Clipboard' and currentCategory == 'OperatingSystem'))
    #         # these categories should all be appended to system list
    #         if (currentCategory == "MicrosoftOffice" and app in ["Microsoft Word", "Microsoft Powerpoint"]) \
    #                 or (currentCategory == "Clipboard"):
    #             currentCategory = 'OperatingSystem'
    #         # on last loop iteration all the remaining xml nodes should be written
    #         lastIndex = (index == len(df) - 1)
    #         # determine if entering switch block or vice versa
    #         enterSwitch = previousDuplicated is True and duplicated is False
    #         exitSwitch = previousDuplicated is False and duplicated is True
    #
    #         # generate UiPath XML node relative to specific row
    #         xmlNode = self.__generateActivities(df, row)
    #         if xmlNode is None:
    #             continue
    #
    #         # add to main sequence
    #         if duplicated:
    #             if currentCategory == "Browser":
    #                 browserActivities.append(xmlNode)
    #             if app == "Microsoft Excel":
    #                 excelActivities.append(xmlNode)
    #             if currentCategory == "OperatingSystem":
    #                 systemActivities.append(xmlNode)
    #         # add to switch case
    #         else:
    #             caseActivities[caseid][currentCategory].append(xmlNode)
    #
    #         # handle switch
    #         # if decision analysis and there are at least 2 cases in switch and
    #         # the switch case is finished so the next row will go in main sequence
    #         # or this is the last index
    #         if decision and len(caseActivities) >= 2 and (exitSwitch or lastIndex):
    #             # wrap low level xml events into specific sequence based on type
    #             for key in caseActivities.keys():
    #                 if caseActivities[key]["Browser"]:
    #                     x = self.__attachBrowser(activities=caseActivities[key]["Browser"])
    #                     caseActivities[key]["Browser"] = [x]
    #                 if caseActivities[key]["MicrosoftOffice"]:
    #                     x = self.__excelSpreadsheet(activities=caseActivities[key]["MicrosoftOffice"])
    #                     caseActivities[key]["MicrosoftOffice"] = [x]
    #                 if caseActivities[key]["OperatingSystem"]:
    #                     x = self.__createSequence(activities=caseActivities[key]["OperatingSystem"],
    #                                               displayName="System events")
    #                     caseActivities[key]["OperatingSystem"] = [x]
    #             # if there are activities for the switch I need to flatten the sublists
    #             # for each key before creating the switch
    #             activities = defaultdict(list)
    #             for key, value in caseActivities.items():
    #                 activities[key].extend(value["Browser"])
    #                 activities[key].extend(value["MicrosoftOffice"])
    #                 activities[key].extend(value["OperatingSystem"])
    #             self.__switch(caseActivities=activities)
    #             # empty caseActivities dictionary for later use
    #             caseActivities.clear()
    #
    #         # if there is a change in category but I'm still inside a switch case
    #         # or I entered a switch case or this is the last index
    #         if (categoryChange and not exitSwitch) or enterSwitch or lastIndex:
    #
    #             if categoryChange:
    #                 self.previousCategory = currentCategory
    #
    #             # wrap xml nodes with sequence and append to main sequence
    #             if browserActivities:
    #                 x = self.__attachBrowser(activities=browserActivities)
    #                 self.mainSequence.append(x)
    #                 browserActivities.clear()
    #             if excelActivities:
    #                 x = self.__excelSpreadsheet(activities=excelActivities)
    #                 self.mainSequence.append(x)
    #                 excelActivities.clear()
    #             if systemActivities:
    #                 x = self.__createSequence(systemActivities, displayName="System events")
    #                 self.mainSequence.append(x)
    #                 systemActivities.clear()
    #
    #     self.status_queue.put(f"[UiPath] Generated UiPath RPA script")

    def __generateRPA(self, df: pandas.DataFrame):
        """
        Main method to generate UiPath SW robot.

        The main steps are:

        1. Add comment with SmartRPA link to UiPath file
        2. Create open browser and open excel activities if the corresponding events are present in the dataframe
        3. create activities dictionary to store XML nodes divided by category.

        For each row in the dataframe:

        * generate XML node from event
        * append node to activities dictionary based on its categoru
        * when there is a change in category of in the last loop iteration, write nodes to main XAML sequence

        :param df: input dataframe of trace to automate
        """
        # add comment to main sequence
        self.__comment("// Generated using SmartRPA available at https://github.com/bpm-diag/smartRPA")

        # backwards compatibility
        if 'xpath_full' not in df.columns:
            df['xpath_full'] = df['xpath']
            self.__comment("// Clicking and typing into web elements is not supported with this event log. "
                           "Record log again with the latest version of SmartRPA")

        # create open browser and open excel activities
        # all the other events relative to excel and browse are attached to this activities using sequence variables
        self.__createOpenBrowser(df)
        self.__createOpenExcel(df)

        # dictionary of lists to store xml nodes relative to different categories
        activities = defaultdict(list)

        # variables used when creating xml nodes
        self.ppt_slides_inserted = False
        self.mac_source_filepath = ""

        # previous category is used to detect a change in category and it's initialised as the category of the first row
        # When a change happens, nodes are added to sequence and lists are emptied
        df['previousCategory'] = df['category'].shift()

        for index, row in df.iterrows():

            # define variables
            currentCategory = row["category"]
            previousCategory = row["previousCategory"]

            # if category changes, a new sequence should be written
            categoryChange = (index > 0) and \
                             (previousCategory != currentCategory) and not \
                                 ((previousCategory == 'OperatingSystem' and currentCategory == 'Clipboard') or (
                                         previousCategory == 'Clipboard' and currentCategory == 'OperatingSystem'))
            # word and powerpoint events should all be appended to system list
            if (currentCategory == "MicrosoftOffice" and
                row['application'] in ["Microsoft Word", "Microsoft Powerpoint"]) or \
                    (currentCategory == "Clipboard"):
                currentCategory = 'OperatingSystem'
            # on last loop iteration all the remaining xml nodes should be written
            lastIndex = (index == len(df) - 1)

            # generate UiPath XML node relative to specific row
            xmlNode = self.__generateActivities(df, row)
            if xmlNode is not None:
                # add to main sequence
                activities[currentCategory].append(xmlNode)

            # if there is a change in category or this is the last index
            if categoryChange or lastIndex:
                # wrap xml nodes with sequence and append to main sequence
                if activities["Browser"]:
                    x = self.__attachBrowser(activities=activities["Browser"])
                    self.mainSequence.append(x)
                if activities["MicrosoftOffice"] or activities["MSOffice"]:
                    x = self.__excelSpreadsheet(activities=activities["MicrosoftOffice"])
                    self.mainSequence.append(x)
                if activities["OperatingSystem"]:
                    x = self.__createSequence(activities["OperatingSystem"], displayName="System events")
                    self.mainSequence.append(x)
                activities.clear()

        self.status_queue.put(f"[UiPath] Generated UiPath RPA script")

    def generateUiPathRPA(self, decision: bool = False):
        """
        Method called by GUI to start UiPath SW Robot generation process.

        :param decision: If decision is False, dataframe of the most frequent trace is passed, else dataframe of the entire process
        """
        self.createBaseFile()
        # if decision, I should use df1, dataframe without duplicates,
        # duplicated events should go to main sequence only once
        dataframe = self.df1 if decision else self.df.reset_index(drop=True)
        # self.__generateRPAWithDecision(dataframe, decision)
        self.__generateRPA(dataframe)
        self.writeXmlToFile()
