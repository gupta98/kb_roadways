from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType

import sys
import os
import sqlite3
import getpass

import essential_functions as ef

from AddTransport import *
from UpdateTransport import *
from AddCompany import *
from UpdateCompany import *
from AddVehicleOwner import *
from UpdateVehicleOwner import *
from AddDriver import *
from UpdateDriver import *
from AddCar import *
from UpdateCar import *
from BillSubmission import *
from PaymentStatus import *

MainWindowUI, _ = loadUiType("__GUIs/MainWindow.ui")


class MainApp(QMainWindow, MainWindowUI):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.childWindow = None

        self.database_path = ".\\__Database\\"
        self.database_name = "kb_roadways.db"
        self.db_con = None
        self.cursor = None

        self.desktop = f"C:\\Users\\{getpass.getuser()}\\Desktop\\"

        self.handleButtons()
        self.setAtMiddle()
        self.establishDatabaseConnectionAndPerformNecessaryTasks()


    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def handleButtons(self):
        self.btnAddTransport.clicked.connect(self.btnAddTransportClicked)
        self.btnUpdateTransports.clicked.connect(self.btnUpdateTransportClicked)

        self.btnAddCompany.clicked.connect(self.btnAddCompanyClicked)
        self.btnUpdateCompanies.clicked.connect(self.btnUpdateCompanyClicked)

        self.btnAddVehicleOwner.clicked.connect(self.btnAddVehicleOwnerClicked)
        self.btnUpdateVehicleOwners.clicked.connect(self.btnUpdateVehicleOwnersClicked)

        self.btnAddDriver.clicked.connect(self.btnAddDriverClicked)
        self.btnUpdateDrivers.clicked.connect(self.btnUpdateDriversClicked)

        self.btnAddCar.clicked.connect(self.btnAddCarClicked)
        self.btnUpdateCars.clicked.connect(self.btnUpdateCarsClicked)

        self.btnBillSubmission.clicked.connect(self.btnBillSubmissionClicked)
        self.btnPaymentStatus.clicked.connect(self.btnPaymentStatusClicked)

    def establishDatabaseConnectionAndPerformNecessaryTasks(self):
        database = self.database_path + self.database_name
        if not os.path.exists(database):
            db_file = open(database, "wb")
            db_file.close()

        self.db_con = sqlite3.connect(self.database_path + self.database_name)
        self.cursor = self.db_con.cursor()

        transports_table_query = """
            CREATE TABLE IF NOT EXISTS
                TRANSPORTS(
                    TRANSPORT_ID INTEGER PRIMARY KEY AUTOINCREMENT, SOURCE_ID INTEGER, SOURCE TEXT, 
                    SOURCE_ROAD TEXT, SOURCE_CITY TEXT, SOURCE_DISTRICT TEXT, SOURCE_PIN TEXT,
                    DESTINATION_ID INTEGER, DESTINATION TEXT, DESTINATION_ROAD TEXT, DESTINATION_CITY TEXT, 
                    DESTINATION_DISTRICT TEXT, DESTINATION_PIN TEXT, DATE_STRING TEXT, FULL_DATE INTEGER, YEAR INTEGER, 
                    MONTH INTEGER, DAY INTEGER, VEHICLE_OWNER_ID INTEGER, VEHICLE_OWNER_NAME TEXT, CAR_ID INTEGER, 
                    CAR_NO TEXT, DRIVER_ID INTEGER, DRIVER_NAME TEXT, CONTRACT_AMOUNT_WITH_COMPANY REAL, 
                    CONTRACT_AMOUNT_WITH_VEHICLE_OWNER REAL, PROFIT REAL, GOODS_UNIT TEXT, NO_OF_UNIT INTEGER, 
                    COST_PER_UNIT TEXT, TOTAL_COST REAL, DEBITS TEXT, CREDITS TEXT, DEBIT_AMOUNT REAL,
                    CREDIT_AMOUNT REAL, NOTES TEXT, INVOICE_NO TEXT, LR_NO TEXT, BILL_GENERATION INTEGER, 
                    BILL_GENERATED INTEGER, BILL_GENERATED_DATE_STRING TEXT, BILL_GENERATED_FULL_DATE INTEGER, 
                    BILL_GENERATED_YEAR INTEGER, BILL_GENERATED_MONTH INTEGER, BILL_GENERATED_DAY INTEGER
                );
        """
        self.cursor.execute(transports_table_query)

        companies_table_query = """
            CREATE TABLE IF NOT EXISTS
                COMPANIES(
                    COMPANY_ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT, ADDRESS TEXT, CONTACT_NO INTEGER, NOTES TEXT
                );
        """
        self.cursor.execute(companies_table_query)

        vehicle_owners_table_query = """
            CREATE TABLE IF NOT EXISTS
                VEHICLE_OWNERS(
                    VEHICLE_OWNER_ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT, ADDRESS TEXT, CONTACT_NO INTEGER, NOTES TEXT
                );
        """
        self.cursor.execute(vehicle_owners_table_query)

        drivers_table_query = """
            CREATE TABLE IF NOT EXISTS
                DRIVERS(
                   DRIVER_ID INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT, ADDRESS TEXT, CONTACT_NO INTEGER, VEHICLE_OWNER_ID INTEGER, NOTES TEXT
                );
        """
        self.cursor.execute(drivers_table_query)

        cars_table_query = """
            CREATE TABLE IF NOT EXISTS
                CARS(
                   CAR_ID INTEGER PRIMARY KEY AUTOINCREMENT, CAR_NO TEXT, VEHICLE_OWNER_ID INTEGER, NOTES TEXT
                );
        """
        self.cursor.execute(cars_table_query)

        bill_submissions_table_query = """
            CREATE TABLE IF NOT EXISTS
                BILL_SUBMISSIONS(
                    BILL_SUBMISSION_ID INTEGER PRIMARY KEY AUTOINCREMENT, BILL_NUMBER TEXT, PAYABLE_AMOUNT REAL,
                    AMOUNT_RECEIVED REAL, DATE_STRING TEXT, FULL_DATE INTEGER, YEAR INTEGER, MONTH INTEGER, 
                    DAY INTEGER, BILL_GENERATED_FOR TEXT, TRANSPORT_IDS TEXT, HTML TEXT
                );
        """
        self.cursor.execute(bill_submissions_table_query)


    def btnAddTransportClicked(self):
        self.childWindow = AddTransportApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
        else:
            QMessageBox.critical(self, self.childWindow.shouldOpenFalseShortMessage, self.childWindow.shouldOpenFalseLongMessage)

    def btnUpdateTransportClicked(self):
        self.childWindow = UpdateTransportApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
        else:
            QMessageBox.critical(self, self.childWindow.shouldOpenFalseShortMessage, self.childWindow.shouldOpenFalseLongMessage)

    def btnAddCompanyClicked(self):
        self.childWindow = AddCompanyApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()

    def btnUpdateCompanyClicked(self):
        self.childWindow = UpdateCompanyApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
        else:
            QMessageBox.critical(self, "No Company Found!", "Please insert one company before updating company.")

    def btnAddVehicleOwnerClicked(self):
        self.childWindow = AddVehicleOwnerApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()

    def btnUpdateVehicleOwnersClicked(self):
        self.childWindow = UpdateVehicleOwnerApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
        else:
            QMessageBox.critical(self, "No Vehicle Owner Found!", "Please insert one vehicle owner before updating vehicle owner.")

    def btnAddDriverClicked(self):
        self.childWindow = AddDriverApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
        else:
            QMessageBox.critical(self, "No Vehicle Owner Found!", "Please insert one vehicle owner before adding driver.")

    def btnUpdateDriversClicked(self):
        self.childWindow = UpdateDriverApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
        else:
            QMessageBox.critical(self, "No Vehicle Owner Found!", "Please insert one vehicle owner before updating driver.")

    def btnAddCarClicked(self):
        self.childWindow = AddCarApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
        else:
            QMessageBox.critical(self, "No Vehicle Owner Found!", "Please insert one vehicle owner before adding driver.")

    def btnUpdateCarsClicked(self):
        self.childWindow = UpdateCarApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
        else:
            QMessageBox.critical(self, "No Vehicle Owner Found!", "Please insert one vehicle owner before updating driver.")

    def btnBillSubmissionClicked(self):
        self.childWindow = BillSubmissionApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()

    def btnPaymentStatusClicked(self):
        self.childWindow = PaymentStatusUIApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
