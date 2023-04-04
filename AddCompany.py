from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType

import sys
from datetime import datetime as dt
import sqlite3

from UpdateCompany import *

AddCompanyUI, _ = loadUiType("__GUIs/AddCompany.ui")


class AddCompanyApp(QMainWindow, AddCompanyUI):
    def __init__(self, parent=None):
        super(AddCompanyApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.setAtMiddle()
        self.handleButtons()

        self.shouldOpen = True
        self.childWindow = None

        self.parent = parent
        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def handleButtons(self):
        self.btnViewCompanies.clicked.connect(self.btnViewCompaniesClicked)
        self.btnReset.clicked.connect(self.btnResetClicked)
        self.btnCreateCompany.clicked.connect(self.btnCreateCompanyClicked)

    def btnViewCompaniesClicked(self):
        self.childWindow = UpdateCompanyApp(parent=self.parent)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
    
    def btnResetClicked(self):
        self.leCompanyName.setText("")
        self.teCompanyAddress.setText("")
        self.leContactNo.setText("")
        self.teNotes.setText("")

    def btnCreateCompanyClicked(self):

        company_name = self.leCompanyName.text()
        if not company_name:
            QMessageBox.critical(self, "No Company Name", "Please insert company name!")
        else:
            company_address = self.teCompanyAddress.toPlainText()
            if not company_address:
                QMessageBox.critical(self, "No Company Address", "Please insert company address!")
            else:
                contact_no = self.leContactNo.text()
                if not contact_no:
                    QMessageBox.critical(self, "No Contact Number", "Please insert contact number!")
                elif not set(contact_no).issubset(set("0123456789")):
                    QMessageBox.critical(self, "Invalid Contact Number", "Please insert valid digit!")
                else:
                    contact_no = int(contact_no)

                    insert_query = f"""
                        INSERT INTO COMPANIES(
                                NAME,
                                ADDRESS,
                                CONTACT_NO,
                                NOTES
                            )
                            VALUES(
                                '{company_name}',
                                '{company_address}',
                                {contact_no},
                                '{self.teNotes.toPlainText()}'
                            );
                    """
                    self.cursor.execute(insert_query)
                    self.db_con.commit()

                    QMessageBox.information(self, "Done!", "Company Added Successfully!")
                    self.btnResetClicked()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddCompanyApp()
    window.show()
    sys.exit(app.exec_())
