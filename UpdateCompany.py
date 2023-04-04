from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType

import sys
import os
from datetime import datetime as dt
import sqlite3
import pandas as pd
import getpass

import essential_functions as ef

UpdateCompanyUI, _ = loadUiType("__GUIs/UpdateCompany.ui")


class UpdateCompanyApp(QMainWindow, UpdateCompanyUI):
    def __init__(self, parent=None):
        super(UpdateCompanyApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.setAtMiddle()
        self.handleButtons()

        self.shouldOpen = True
        self.company_id_dict = {}
        self.selected_company = ()

        self.lwCompanyList.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.parent = parent
        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor

        self.makeTheListOfAllCompanies()

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def handleButtons(self):
        self.lwCompanyList.doubleClicked.connect(self.viewCompanyDetails)
        self.btnDownloadSelected.clicked.connect(self.btnDownloadSelectedPressed)
        self.btnDownloadAll.clicked.connect(self.btnDownloadAllPressed)
        self.btnUpdate.clicked.connect(self.btnUpdatePressed)
        self.btnDelete.clicked.connect(self.btnDeletePressed)

    def makeTheListOfAllCompanies(self):
        select_query = """
            SELECT
                COMPANY_ID, NAME
            FROM
                COMPANIES;
        """
        self.cursor.execute(select_query)

        self.company_id_dict.clear()
        self.lwCompanyList.clear()
        companies = self.cursor.fetchall()
        company_counter = 1
        z_fill_length = len(str(len(companies)))

        if companies:
            for company_id, company_name in companies:
                key = f"{str(company_counter).zfill(z_fill_length)} - {company_name}"
                self.company_id_dict[key] = company_id
                self.lwCompanyList.addItem(key)
                company_counter += 1

    def viewCompanyDetails(self):
        company_id = self.company_id_dict[self.lwCompanyList.selectedItems()[0].text()]
        select_query = f"""
            SELECT
                *
            FROM
                COMPANIES
            WHERE
                COMPANY_ID = {company_id};
        """
        self.cursor.execute(select_query)

        self.selected_company = details = self.cursor.fetchall()[0]

        self.leCompanyName.setText("")
        self.leContactNo.setText("")
        self.teCompanyAddress.setText("")
        self.teNotes.setText("")

        self.leCompanyName.setText(f"{details[1]}")
        self.teCompanyAddress.setText(f"{details[2]}")
        self.leContactNo.setText(f"{details[3]}")
        self.teNotes.setText(f"{details[4]}")

    def btnDownloadSelectedPressed(self):
        company_ids = [f"{self.company_id_dict[company.text()]}" for company in self.lwCompanyList.selectedItems()]
        if not company_ids:
            QMessageBox.critical(self, "No Company Selected!", "Please select at least one company!")
        else:
            columns = ["COMPANY_ID", "NAME", "ADDRESS", "CONTACT_NO", "NOTES"]
            df = pd.DataFrame(columns=columns)

            select_query = f"""
                SELECT
                    *
                FROM
                    COMPANIES
                WHERE
                    COMPANY_ID IN ({', '.join(company_ids)})
                ORDER BY
                    COMPANY_ID;
            """
            self.cursor.execute(select_query)

            for company in self.cursor.fetchall():
                df = df.append({
                    "COMPANY_ID" : company[0],
                    "NAME" : company[1],
                    "ADDRESS" : company[2],
                    "CONTACT_NO" : company[3],
                    "NOTES" : company[4]
                }, ignore_index=True)

            with open("__Files\\lastfilesavelocation.txt", "r") as file:
                path = file.read()
            if not os.path.exists(path):
                path = f"C:\\Users\\{getpass.getuser()}\\Desktop\\"
            with open("__Files\\lastfilesavelocation.txt", "w") as file:
                file.write(path)

            filename = QFileDialog.getSaveFileName(self, 'Save File', path)[0]
            if filename:

                if not filename.lower().endswith(".xlsx"):
                    filename += ".xlsx"
                df.to_excel(filename, index=False)

                QMessageBox.information(self, "Done!", "File saved successfully!")

                with open("__Files\\lastfilesavelocation.txt", "w") as file:
                    file.write("\\".join(filename.replace("/", "\\").split("\\")[:-1]))

    def btnDownloadAllPressed(self):
        select_query = f"""
            SELECT
                *
            FROM
                COMPANIES
            ORDER BY
                COMPANY_ID;
        """
        self.cursor.execute(select_query)
        companies = self.cursor.fetchall()

        if not companies:
            QMessageBox.critical(self, "No Company Exist!", "There is no company in database!")
        else:
            columns = ["COMPANY_ID", "NAME", "ADDRESS", "CONTACT_NO", "NOTES"]
            df = pd.DataFrame(columns=columns)

            for company in companies:
                df = df.append({
                    "COMPANY_ID": company[0],
                    "NAME": company[1],
                    "ADDRESS": company[2],
                    "CONTACT_NO": company[3],
                    "NOTES": company[4]
                }, ignore_index=True)

            with open("__Files\\lastfilesavelocation.txt", "r") as file:
                path = file.read()
            if not os.path.exists(path):
                path = f"C:\\Users\\{getpass.getuser()}\\Desktop\\"
            with open("__Files\\lastfilesavelocation.txt", "w") as file:
                file.write(path)

            filename = QFileDialog.getSaveFileName(self, 'Save File')[0]
            if filename:
                if not filename.lower().endswith(".xlsx"):
                    filename += ".xlsx"
                df.to_excel(filename, index=False)

                QMessageBox.information(self, "Done!", "File saved successfully!")

                with open("__Files\\lastfilesavelocation.txt", "w") as file:
                    file.write("\\".join(filename.replace("/", "\\").split("\\")[:-1]))

    def btnUpdatePressed(self):

        if not self.selected_company:
            QMessageBox.critical(self, "No Company Selected!", "Please select a company to update!")
        else:
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

                        answer = QMessageBox.question(self, "Update?", f"This will update {self.selected_company[1]}. Continue?", QMessageBox.Yes | QMessageBox.No)
                        if answer == QMessageBox.Yes:

                            update_query = f"""
                                UPDATE
                                    COMPANIES
                                SET
                                    NAME = '{company_name}',
                                    ADDRESS = '{company_address}',
                                    CONTACT_NO = {contact_no},
                                    NOTES = '{self.teNotes.toPlainText()}'
                                WHERE
                                    COMPANY_ID = {self.selected_company[0]};
                            """
                            self.cursor.execute(update_query)
                            self.db_con.commit()
                            self.makeTheListOfAllCompanies()

                            QMessageBox.information(self, "Done!", "Company Updated Successfully!")

    def btnDeletePressed(self):
        company_ids = [f"{self.company_id_dict[company.text()]}" for company in self.lwCompanyList.selectedItems()]
        if not company_ids:
            QMessageBox.critical(self, "No Company Selected!", "Please select at lease one company to delete!")
        else:

            answer = QMessageBox.question(self, "Delete?", "This will delete the companies permanently. Continue?", QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:

                delete_query = f"""
                    DELETE
                    FROM
                        COMPANIES
                    WHERE
                        COMPANY_ID IN ({', '.join(company_ids)});
                """
                self.cursor.execute(delete_query)
                self.db_con.commit()

                self.company_id_dict.clear()
                self.selected_company = ()

                self.lwCompanyList.clear()
                self.leCompanyName.setText("")
                self.teCompanyAddress.setText("")
                self.leContactNo.setText("")
                self.teNotes.setText("")

                self.makeTheListOfAllCompanies()

                QMessageBox.information(self, "Done!", "Companies Deleted Successfully!")




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UpdateCompanyApp()
    window.show()
    sys.exit(app.exec_())
