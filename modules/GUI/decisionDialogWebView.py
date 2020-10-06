import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import pandas
from bs4 import BeautifulSoup


def dataframeToHTML(keywordsDataframe: pandas.DataFrame):
    html_doc = """
    <html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1, shrink-to-fit=no"
    />

    <!-- Bootstrap CSS -->
    <link
      rel="stylesheet"
      href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
      integrity="sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z"
      crossorigin="anonymous"
    />
    <style>
      .max-cell-width {
        max-width: 350px;
      }
      .min-cell-width {
        min-width: 150px;
      }
    </style>
  </head>
  <body>
    <nav class="navbar navbar-expand-md navbar-dark bg-primary">
      <a class="navbar-brand mx-auto" href="#">Select trace to execute</a>
    </nav>

    <div class="container-fluid pt-3">
      <table id="decisionTable" class="table table-sm table-responsive table-hover">
        <thead class="thead-light">
          <tr>
            <th scope="col">Case ID</th>
            <th scope="col">Category</th>
            <th scope="col">Application</th>
            <th scope="col">Events</th>
            <th scope="col">Hostname</th>
            <th scope="col">URL</th>
            <th scope="col">Keywords</th>
            <th scope="col">Path</th>
            <th scope="col">Clipboard</th>
            <th scope="col">Cells</th>
            <th scope="col">ID</th>
          </tr>
        </thead>
        <tbody>
        
        </tbody>
        </table>
    </div>

    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script
      src="https://code.jquery.com/jquery-3.5.1.slim.min.js"
      integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj"
      crossorigin="anonymous"
    ></script>
    <script
      src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"
      integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN"
      crossorigin="anonymous"
    ></script>
    <script
      src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"
      integrity="sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8shuf57BaghqFfPlYxofvL8/KUEfYiJOMMV+rV"
      crossorigin="anonymous"
    ></script>
        <script>
      function getSelectedTrace() {
        let caseid;
        let radios = document.getElementsByName("group1");
        for (let i = 0, length = radios.length; i < length; i++) {
          if (radios[i].checked) {
            caseid = radios[i].value;
            break;
          }
        }
        return caseid;
      }
      $("#decisionTable tr").click(function () {
        $(this).find("th input:radio").prop("checked", true);
      });
    </script>
  </body>
</html>
    """
    soup = BeautifulSoup(html_doc, 'lxml')
    tbody = soup.find('tbody')

    for trace in keywordsDataframe.values:
        caseID = trace[0]

        tr = soup.new_tag('tr')

        # radio
        th = soup.new_tag('th')
        div = soup.new_tag('div', attrs={"class": "form-check"})
        radio_input = soup.new_tag("input", attrs={"class": "form-check-input",
                                                   "name": "group1",
                                                   "type": "radio",
                                                   "value": str(caseID)})
        label = soup.new_tag('label', attrs={"class": "form-check-label"})
        label.string = str(caseID)
        div.append(radio_input)
        div.append(label)
        th.append(div)
        tr.append(th)

        for column in range(len(trace)):
            # case id is already added above
            if column == 0:
                continue
            # url column should be wider
            elif column == 5:
                td = soup.new_tag('td', attrs={"class": "text-break text-wrap",
                                               "style": "min-width: 300px; max-width: 500px;"})
            else:
                td = soup.new_tag('td', attrs={"class": "text-break text-wrap min-cell-width max-cell-width"})
            value = trace[column]
            td.string = str(value)
            tr.append(td)

        tbody.append(tr)

    return soup.prettify()


class DecisionDialogWebView(QDialog):
    def __init__(self, df: pandas.DataFrame):
        super(DecisionDialogWebView, self).__init__()
        # instance variables
        self.df = df
        # numberOfTraces = len(self.df['case:concept:name'].drop_duplicates())
        self.selectedTrace = None

        self.__controls()
        self.__layout()

    def __controls(self):
        self.browser = QWebEngineView()
        text = dataframeToHTML(self.df)
        self.browser.setHtml(text)
        self.browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.browser.load(QUrl.fromLocalFile('/Users/marco/Desktop/decision.html'))

    def __layout(self):
        self.setWindowTitle("Decision point")
        self.vBox = QVBoxLayout()
        self.getTraceButton = QPushButton("Select trace")
        self.vBox.addWidget(self.browser)
        self.vBox.addWidget(self.getTraceButton, alignment=Qt.AlignCenter | Qt.AlignBottom)
        self.setLayout(self.vBox)

        self.getTraceButton.clicked.connect(self.updateBounds)

    def updateBounds(self):
        self.browser.page().runJavaScript("getSelectedTrace()", self.getBounds)

    def getBounds(self, trace):
        self.accept()
        self.selectedTrace = trace
        print(self.selectedTrace)


if __name__ == '__main__':
    from io import StringIO

    k = StringIO(""",case:concept:name,category,application,events,hostname,url,keywords,path,clipboard,cells,id
0,1005090352791000,Browser,Chrome,typed,corsidilaurea.uniroma1.it,https://corsidilaurea.uniroma1.it/,,,,,
1,1005090509725000,Browser,Chrome,"changeField, link","www.google.com, www.uniroma1.it","https://www.google.com/, https://www.uniroma1.it/it/",uniroma1,,,,
""")
    df = pandas.read_csv(k, index_col=0).fillna('')
    app = QtWidgets.QApplication(sys.argv)
    window = DecisionDialogWebView(df)
    window.show()
    app.exec_()
