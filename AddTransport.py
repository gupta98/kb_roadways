from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType

import sys
from datetime import datetime as dt
import sqlite3
import json

import essential_functions as ef

AddTransportUI, _ = loadUiType("__GUIs/AddTransport.ui")


class AddTransportApp(QMainWindow, AddTransportUI):
    def __init__(self, parent=None):
        super(AddTransportApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.parent = parent

        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor

        self.shouldOpen = None
        self.shouldOpenFalseShortMessage = ""
        self.shouldOpenFalseLongMessage = ""

        self.company_id_dict = {}
        self.company_name_dict = {}
        self.vehicle_owner_id_dict = {}
        self.vehicle_owner_name_dict = {}
        self.driver_id_dict = {'': -1}
        self.driver_name_dict = {-1: ''}
        self.car_id_dict = {'': -1}
        self.car_number_dict = {-1: ''}

        self.source_address_history_dict = {}
        self.destination_address_history_dict = {}
        self.districts = {}

        self.shouldOpenCheck()
        if self.shouldOpen:
            self.doEssentialWorks()
            self.setDefaultData()
            self.setAtMiddle()
            self.handleButtons()

    def shouldOpenCheck(self):
        # Setting Companies #
        select_query = """
            SELECT
                COMPANY_ID, NAME
            FROM
                COMPANIES
            ORDER BY
                COMPANY_ID;
        """
        self.cursor.execute(select_query)
        companies = self.cursor.fetchall()
        if len(companies) < 2:
            self.shouldOpen = False
            self.shouldOpenFalseShortMessage = "Insufficient Companies!"
            self.shouldOpenFalseLongMessage = "Please create at least two companies for making a transport entry!"
            return
        else:
            company_counter = 1
            z_fill_length = len(str(len(companies)))
            for company_id, company_name in companies:
                self.company_id_dict[f"{str(company_counter).zfill(z_fill_length)} - {company_name}"] = company_id
                self.company_name_dict[company_id] = company_name
                self.cbSources.addItem(f"{str(company_counter).zfill(z_fill_length)} - {company_name}")
                self.cbDestinations.addItem(f"{str(company_counter).zfill(z_fill_length)} - {company_name}")
                company_counter += 1
            self.cbSources.setCurrentIndex(0)
            self.cbDestinations.setCurrentIndex(1)


        # Setting Vehicle Owners #
        select_query = """
            SELECT
                VEHICLE_OWNER_ID, NAME
            FROM
                VEHICLE_OWNERS
            ORDER BY
                VEHICLE_OWNER_ID;
        """
        self.cursor.execute(select_query)
        vehicle_owners = self.cursor.fetchall()
        if not vehicle_owners:
            self.shouldOpen = False
            self.shouldOpenFalseShortMessage = "Insufficient Vehicle Owners!"
            self.shouldOpenFalseLongMessage = "Please create at least one vehicle owner for making a transport entry!"
            return
        else:
            vehicle_owner_counter = 1
            z_fill_length = len(str(len(vehicle_owners)))
            for vehicle_owner_id, vehicle_owner_name in vehicle_owners:
                self.vehicle_owner_id_dict[f"{str(vehicle_owner_counter).zfill(z_fill_length)} - {vehicle_owner_name}"] = vehicle_owner_id
                self.vehicle_owner_name_dict[vehicle_owner_id] = vehicle_owner_name
                self.cbVehicleOwners.addItem(f"{str(vehicle_owner_counter).zfill(z_fill_length)} - {vehicle_owner_name}")
                vehicle_owner_counter += 1

        self.shouldOpen = True

        # Setting Cars #
        select_query = f"""
            SELECT
                CAR_ID, CAR_NO
            FROM
                CARS
            WHERE
                VEHICLE_OWNER_ID = {self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]} 
            ORDER BY
                CAR_ID;
        """
        self.cursor.execute(select_query)
        cars = self.cursor.fetchall()
        if cars:
            car_counter = 1
            z_fill_length = len(str(len(cars)))
            for car_id, car_number in cars:
                self.car_id_dict[f"{str(car_counter).zfill(z_fill_length)} - {car_number}"] = car_id
                self.car_number_dict[car_id] = car_number
                self.cbCarNumbers.addItem(f"{str(car_counter).zfill(z_fill_length)} - {car_number}")
                car_counter += 1


        # Setting Drivers #
        select_query = f"""
            SELECT
                DRIVER_ID, NAME
            FROM
                DRIVERS
            WHERE
                VEHICLE_OWNER_ID = {self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]} 
            ORDER BY
                DRIVER_ID;
        """
        self.cursor.execute(select_query)
        drivers = self.cursor.fetchall()
        if drivers:
            driver_counter = 1
            z_fill_length = len(str(len(drivers)))
            for driver_id, driver_name in drivers:
                self.driver_id_dict[f"{str(driver_counter).zfill(z_fill_length)} - {driver_name}"] = driver_id
                self.driver_name_dict[driver_id] = driver_name
                self.cbDriverNames.addItem(f"{str(driver_counter).zfill(z_fill_length)} - {driver_name}")
                driver_counter += 1

        select_query = f"""
            SELECT
                DRIVERS.DRIVER_ID, DRIVERS.NAME, VEHICLE_OWNERS.NAME
            FROM
                DRIVERS, VEHICLE_OWNERS
            WHERE
                DRIVERS.VEHICLE_OWNER_ID = VEHICLE_OWNERS.VEHICLE_OWNER_ID
                AND
                DRIVERS.VEHICLE_OWNER_ID != {self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]} 
            ORDER BY
                DRIVER_ID;
        """
        self.cursor.execute(select_query)
        drivers = self.cursor.fetchall()
        if drivers:
            driver_counter = 1
            z_fill_length = len(str(len(drivers)))
            for driver_id, driver_name, vehicle_owner_name in drivers:
                self.driver_id_dict[f"{str(driver_counter).zfill(z_fill_length)} - {driver_name} ({vehicle_owner_name})"] = driver_id
                self.driver_name_dict[driver_id] = driver_name
                self.cbDriverNames.addItem(f"{str(driver_counter).zfill(z_fill_length)} - {driver_name} ({vehicle_owner_name})")
                driver_counter += 1

    def doEssentialWorks(self):
        self.twDebit.horizontalHeader().setStretchLastSection(True)
        self.twDebit.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.twCredit.horizontalHeader().setStretchLastSection(True)
        self.twCredit.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        with open("__Files\\addtransportwarning.txt", "r+") as file:
            if file.read() == "True":

                msgbox = QMessageBox(self)
                msgbox.setWindowTitle("Warning!")
                msgbox.setText("To add a Transport record, first be sure that all necessary\nentries like Companies, Vehicle Owners and Drivers are added to your database.")
                checkbox = QCheckBox("Don't show this message again!")
                msgbox.setCheckBox(checkbox)
                msgbox.exec_()

                if checkbox.isChecked():
                    file.truncate(0) # To delete previous content
                    file.seek(0)
                    file.write("False")

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def setDefaultData(self):
        # Setting Transport ID #
        select_query = """
            SELECT
                TRANSPORT_ID
            FROM
                TRANSPORTS
            ORDER BY
                TRANSPORT_ID DESC;
        """
        self.cursor.execute(select_query)
        transport_ids = self.cursor.fetchall()
        last_transport_id = transport_ids[0][0] if transport_ids else 0
        new_transport_id = last_transport_id + 1
        self.leTransportID.setText(f"TR-{new_transport_id}")

        today = dt.now()
        day = today.day
        month = today.month
        year = today.year
        self.deTransportDate.setDate(QDate(year, month, day))

        # Setting Units #
        self.cbVehicleUnit.addItem("Piece")
        self.cbVehicleUnit.addItem("Litre")
        self.cbVehicleUnit.addItem("Ton")

        # Setting Districts #
        districts = [
            "Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri",
            "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Medinipur",
            "Paschim Burdwan", "Purba Burdwan", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur", "Sunderban",
            "Ichhemati", "Ranaghat", "Bishnupur", "Jangipur", "Behrampur"
        ]
        districts.sort(key=lambda state: state.upper())
        for ind, district in enumerate(districts):
            self.districts[district] = ind
            self.cbSourceDistrict.addItem(district)
            self.cbDestinationDistrict.addItem(district)
        self.cbSourceDistrict.setCurrentIndex(0)
        self.cbDestinationDistrict.setCurrentIndex(0)

        self.cbSourcesTextChanged()
        self.cbDestinationsTextChanged()
        self.cbVehicleOwnersTextChanged()

        self.leTotalAmountInDebit.setText("₹ 0.00")
        self.leTotalAmountInCredit.setText("₹ 0.00")

    def handleButtons(self):
        self.cbSources.currentTextChanged.connect(self.cbSourcesTextChanged)
        self.cbDestinations.currentTextChanged.connect(self.cbDestinationsTextChanged)
        self.cbVehicleOwners.currentTextChanged.connect(self.cbVehicleOwnersTextChanged)

        self.cbSourceAddressHistory.currentTextChanged.connect(self.cbSourceAddressHistoryTextChanged)
        self.cbDestinationAddressHistory.currentTextChanged.connect(self.cbDestinationAddressHistoryTextChanged)

        self.leContractWithCompany.textChanged.connect(self.leContractWithCompanyChanged)
        self.leContractWithVehicleOwner.textChanged.connect(self.leContractWithVehicleOwnerChanged)

        self.leNoOfUnit.textChanged.connect(self.leNoOfUnitChanged)
        self.lePricePerUnit.textChanged.connect(self.lePricePerUnitChanged)

        self.btnTwDebitAddRow.clicked.connect(self.btnTwDebitAddRowClicked)
        self.btnTwDebitRemoveRow.clicked.connect(self.btnTwDebitRemoveRowClicked)
        self.btnTwCreditAddRow.clicked.connect(self.btnTwCreditAddRowClicked)
        self.btnTwCreditRemoveRow.clicked.connect(self.btnTwCreditRemoveRowClicked)

        self.btnCreateTransport.clicked.connect(self.btnCreateTransportClicked)
        self.btnReset.clicked.connect(self.btnResetClicked)

        self.twDebit.itemChanged.connect(self.calculateDebitCreditAmount)
        self.twCredit.itemChanged.connect(self.calculateDebitCreditAmount)

    def calculateDebitCreditAmount(self):
        debit_sum = 0
        for row in range(self.twDebit.rowCount()):
            amount = self.twDebit.item(row, 1)
            amount_text = amount.text() if amount is not None else ""
            try:
                amount_text_float = float(amount_text)
                debit_sum += amount_text_float
            except ValueError:
                continue
        self.leTotalAmountInDebit.setText(f"₹ {debit_sum:.2f}")

        credit_sum = 0
        for row in range(self.twCredit.rowCount()):
            amount = self.twCredit.item(row, 1)
            amount_text = amount.text() if amount is not None else ""
            try:
                amount_text_float = float(amount_text)
                credit_sum += amount_text_float
            except ValueError:
                continue
        self.leTotalAmountInCredit.setText(f"₹ {credit_sum:.2f}")


    def cbSourcesTextChanged(self):
        self.source_address_history_dict = {}
        self.cbSourceAddressHistory.clear()
        self.cbSourceAddressHistory.addItem("---HISTORY---")

        source_address_histories = []

        select_query = f"""
            SELECT
                SOURCE_ROAD, SOURCE_CITY, SOURCE_DISTRICT, SOURCE_PIN, FULL_DATE
            FROM
                TRANSPORTS
            WHERE
                SOURCE_ID = {self.company_id_dict[self.cbSources.currentText()]}
            ORDER BY
                FULL_DATE DESC;
        """
        self.cursor.execute(select_query)
        address_histories = self.cursor.fetchall()
        if address_histories:
            for source_road, source_city, source_district, source_pin, full_date in address_histories:
                source_address_histories.append(
                    {
                        "source_road" : source_road,
                        "source_city" : source_city,
                        "source_district" : source_district,
                        "source_pin" : source_pin,
                        "full_date" : full_date
                    }
                )
            source_address_histories.sort(reverse=True, key=lambda x: int(x["full_date"]))

            checker_set = set()
            for source_address_history in source_address_histories:
                key = f"{source_address_history['source_road']} -- {source_address_history['source_city']} -- {source_address_history['source_district']} -- {source_address_history['source_pin']}"
                if key not in checker_set:
                    checker_set.add(key)
                    self.source_address_history_dict[key] = source_address_history
                    self.cbSourceAddressHistory.addItem(key)

            self.cbSourceAddressHistory.setCurrentIndex(0)

    def cbDestinationsTextChanged(self):
        self.destination_address_history_dict = {}
        self.cbDestinationAddressHistory.clear()
        self.cbDestinationAddressHistory.addItem("---HISTORY---")

        destination_address_histories = []

        select_query = f"""
            SELECT
                DESTINATION_ROAD, DESTINATION_CITY, DESTINATION_DISTRICT, DESTINATION_PIN, FULL_DATE
            FROM
                TRANSPORTS
            WHERE
                DESTINATION_ID = {self.company_id_dict[self.cbDestinations.currentText()]}
            ORDER BY
                FULL_DATE DESC;
        """
        self.cursor.execute(select_query)
        address_histories = self.cursor.fetchall()
        if address_histories:
            for destination_road, destination_city, destination_district, destination_pin, full_date in address_histories:
                destination_address_histories.append(
                    {
                        "destination_road": destination_road,
                        "destination_city": destination_city,
                        "destination_district": destination_district,
                        "destination_pin": destination_pin,
                        "full_date": full_date
                    }
                )
            destination_address_histories.sort(reverse=True, key=lambda x: int(x["full_date"]))

            checker_set = set()
            for destination_address_history in destination_address_histories:
                key = f"{destination_address_history['destination_road']} -- {destination_address_history['destination_city']} -- {destination_address_history['destination_district']} -- {destination_address_history['destination_pin']}"
                if key not in checker_set:
                    checker_set.add(key)
                    self.destination_address_history_dict[key] = destination_address_history
                    self.cbDestinationAddressHistory.addItem(key)

            self.cbDestinationAddressHistory.setCurrentIndex(0)

    def cbSourceAddressHistoryTextChanged(self):
        value = self.source_address_history_dict.get(self.cbSourceAddressHistory.currentText(), None)
        if value is not None:
            self.cbSourceDistrict.setCurrentIndex(self.districts[value['source_district']])
            self.leSourceAddressRoad.setText(value['source_road'])
            self.leSourceAddressCity.setText(value['source_city'])
            self.leSourceAddressPin.setText(value['source_pin'])

    def cbDestinationAddressHistoryTextChanged(self):
        value = self.destination_address_history_dict.get(self.cbDestinationAddressHistory.currentText(), None)
        if value is not None:
            self.cbDestinationDistrict.setCurrentIndex(self.districts[value['destination_district']])
            self.leDestinationAddressRoad.setText(value['destination_road'])
            self.leDestinationAddressCity.setText(value['destination_city'])
            self.leDestinationAddressPin.setText(value['destination_pin'])

    def cbVehicleOwnersTextChanged(self):
        vehicle_owner = self.vehicle_owner_name_dict[self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]]
        self.lblVehicleOwnerAccountName.setText(f"{vehicle_owner} A/c")

        # Change Cars #
        self.cbCarNumbers.clear()
        self.car_id_dict.clear()
        self.car_number_dict.clear()
        self.car_id_dict = {'': -1}
        self.car_number_dict = {-1: ''}

        select_query = f"""
            SELECT
                CAR_ID, CAR_NO
            FROM
                CARS
            WHERE
                VEHICLE_OWNER_ID = {self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]} 
            ORDER BY
                CAR_ID;
        """
        self.cursor.execute(select_query)
        cars = self.cursor.fetchall()
        if cars:
            car_counter = 1
            z_fill_length = len(str(len(cars)))
            for car_id, car_name in cars:
                self.car_id_dict[f"{str(car_counter).zfill(z_fill_length)} - {car_name}"] = car_id
                self.car_number_dict[car_id] = car_name
                self.cbCarNumbers.addItem(f"{str(car_counter).zfill(z_fill_length)} - {car_name}")
                car_counter += 1

        # Change Drivers #
        self.cbDriverNames.clear()
        self.driver_id_dict.clear()
        self.driver_name_dict.clear()
        self.driver_id_dict = {'': -1}
        self.driver_name_dict = {-1: ''}

        select_query = f"""
            SELECT
                DRIVER_ID, NAME
            FROM
                DRIVERS
            WHERE
                VEHICLE_OWNER_ID = {self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]} 
            ORDER BY
                DRIVER_ID;
        """
        self.cursor.execute(select_query)
        drivers = self.cursor.fetchall()
        if drivers:
            driver_counter = 1
            z_fill_length = len(str(len(drivers)))
            for driver_id, driver_name in drivers:
                self.driver_id_dict[f"{str(driver_counter).zfill(z_fill_length)} - {driver_name}"] = driver_id
                self.driver_name_dict[driver_id] = driver_name
                self.cbDriverNames.addItem(f"{str(driver_counter).zfill(z_fill_length)} - {driver_name}")
                driver_counter += 1

        select_query = f"""
            SELECT
                DRIVERS.DRIVER_ID, DRIVERS.NAME, VEHICLE_OWNERS.NAME
            FROM
                DRIVERS, VEHICLE_OWNERS
            WHERE
                DRIVERS.VEHICLE_OWNER_ID = VEHICLE_OWNERS.VEHICLE_OWNER_ID
                AND
                DRIVERS.VEHICLE_OWNER_ID != {self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]} 
            ORDER BY
                DRIVER_ID;
        """
        self.cursor.execute(select_query)
        drivers = self.cursor.fetchall()
        if drivers:
            driver_counter = 1
            z_fill_length = len(str(len(drivers)))
            for driver_id, driver_name, vehicle_owner_name in drivers:
                self.driver_id_dict[
                    f"{str(driver_counter).zfill(z_fill_length)} - {driver_name} ({vehicle_owner_name})"] = driver_id
                self.driver_name_dict[driver_id] = driver_name
                self.cbDriverNames.addItem(
                    f"{str(driver_counter).zfill(z_fill_length)} - {driver_name} ({vehicle_owner_name})")
                driver_counter += 1

    def leContractWithCompanyChanged(self):
        contract_with_company = self.leContractWithCompany.text()
        if contract_with_company != "":
            try:
                float(contract_with_company)
                self.calculateProfit()
            except ValueError:
                self.leProfit.setText("")

    def leContractWithVehicleOwnerChanged(self):
        contract_with_vehicle_owner = self.leContractWithVehicleOwner.text()
        if contract_with_vehicle_owner != "":
            try:
                float(contract_with_vehicle_owner)
                self.calculateProfit()
            except ValueError:
                self.leProfit.setText("")

    def calculateProfit(self):
        contract_with_company = self.leContractWithCompany.text()
        contract_with_vehicle_owner = self.leContractWithVehicleOwner.text()

        if contract_with_company and contract_with_vehicle_owner:
            try:
                contract_with_company = float(contract_with_company)
                contract_with_vehicle_owner = float(contract_with_vehicle_owner)

                if contract_with_company > 0 and contract_with_vehicle_owner > 0:
                    self.leProfit.setText(f"{round(contract_with_company - contract_with_vehicle_owner, 2):.2f}")
                else:
                    self.leProfit.setText("")

            except Exception:
                self.leProfit.setText("")
        else:
            self.leProfit.setText("")

    def leNoOfUnitChanged(self):
        no_of_unit = self.leNoOfUnit.text()
        if no_of_unit != "":
            try:
                float(no_of_unit)
                self.calculateTotalCost()
            except ValueError:
                self.leTotalCost.setText("")
        else:
            self.leTotalCost.setText("")

    def lePricePerUnitChanged(self):
        price_per_unit = self.lePricePerUnit.text()
        if price_per_unit != "":
            try:
                float(price_per_unit)
                self.calculateTotalCost()
            except ValueError:
                self.leTotalCost.setText("")
        else:
            self.leTotalCost.setText("")

    def calculateTotalCost(self):
        no_of_unit = self.leNoOfUnit.text()
        price_per_unit = self.lePricePerUnit.text()

        if no_of_unit and price_per_unit:
            try:
                no_of_unit = float(no_of_unit)
                price_per_unit = float(price_per_unit)

                if no_of_unit > 0 and price_per_unit > 0:
                    self.leTotalCost.setText(f"{round(no_of_unit * price_per_unit, 2):.2f}")
                else:
                    self.leTotalCost.setText("")

            except Exception:
                self.leTotalCost.setText("")
        else:
            self.leTotalCost.setText("")

    def btnTwDebitAddRowClicked(self):
        self.twDebit.setRowCount(self.twDebit.rowCount() + 1)

    def btnTwDebitRemoveRowClicked(self):
        rows = list({idx.row() for idx in self.twDebit.selectedIndexes()})
        if rows:
            answer = QMessageBox.critical(self, "Delete!", "Are you want to delete the selected rows?", QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:
                rows.sort(reverse=True)
                for row in rows:
                    self.twDebit.removeRow(row)

            self.calculateDebitCreditAmount()

    def btnTwCreditAddRowClicked(self):
        self.twCredit.setRowCount(self.twCredit.rowCount() + 1)

    def btnTwCreditRemoveRowClicked(self):
        rows = list({idx.row() for idx in self.twCredit.selectedIndexes()})
        if rows:
            answer = QMessageBox.critical(self, "Delete!", "Are you want to delete the selected rows?", QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:
                rows.sort(reverse=True)
                for row in rows:
                    self.twCredit.removeRow(row)

            self.calculateDebitCreditAmount()

    def btnCreateTransportClicked(self):
        allOkay = True

        if allOkay:
                if not self.leSourceAddressRoad.text().strip():
                    QMessageBox.critical(self, "No Road", "Please give a road for source company address!")
                    allOkay = False
                else:
                    if not self.leSourceAddressCity.text().strip():
                        QMessageBox.critical(self, "No City", "Please give a city for source company address!")
                        allOkay = False
                    else:
                        if not self.leSourceAddressPin.text().strip():
                            QMessageBox.critical(self, "No PIN", "Please give a PIN for source company address!")
                            allOkay = False

        if allOkay:
                if not self.leDestinationAddressRoad.text().strip():
                    QMessageBox.critical(self, "No Road", "Please give a road for destination company address!")
                    allOkay = False
                else:
                    if not self.leDestinationAddressCity.text().strip():
                        QMessageBox.critical(self, "No City", "Please give a city for destination company address!")
                        allOkay = False
                    else:
                        if not self.leDestinationAddressPin.text().strip():
                            QMessageBox.critical(self, "No PIN", "Please give a PIN for destination company address!")
                            allOkay = False

        if allOkay:
            if self.company_id_dict[self.cbSources.currentText()] == self.company_id_dict[self.cbDestinations.currentText()]:
                QMessageBox.critical(self, "Source & Destination Are Same", "Please select different destination for a source!")
                allOkay = False

        if allOkay:
            if self.leProfit.text().strip() == "":
                QMessageBox.critical(self, "No Profit", "Profit can't be blank!")
                allOkay = False

        if allOkay:
            if self.leTotalCost.text().strip() == "":
                QMessageBox.critical(self, "No Total Cost", "Total cost can't be blank!")
                allOkay = False

        if allOkay:
            if self.leInvoiceNo.text().strip() == "":
                QMessageBox.critical(self, "No Invoice No", "Invoice No can't be blank!")
                allOkay = False

        if allOkay:
            debitList = []
            for row in range(self.twDebit.rowCount()):
                particular = self.twDebit.item(row, 0)
                particular_text = particular.text() if particular is not None else ""

                amount = self.twDebit.item(row, 1)
                amount_text = amount.text() if amount is not None else ""
                if particular_text and amount_text:
                    try:
                        amount_text_float = float(amount_text)
                        if amount_text_float < 0:
                            QMessageBox.critical(self, "Invalid Amount!", f"Row Number {row + 1} Has A Negative Amount In Debit!")
                            allOkay = False
                            break
                    except ValueError:
                        QMessageBox.critical(self, "Invalid Entry!", f"Row Number {row + 1} Has An Invalid Entry As Amount In Debit!")
                        allOkay = False
                        break

                if particular_text and amount_text:
                    debitList.append([len(debitList) + 1, particular_text, float(amount_text)])
                elif particular_text and not amount_text:
                    QMessageBox.critical(self, "No Amount!", f"Row Number {row+1} Has No Amount In Debit!")
                    allOkay = False
                    break
                elif not particular_text and amount_text:
                    QMessageBox.critical(self, "No Particular!", f"Row Number {row + 1} Has No Particular In Debit!")
                    allOkay = False
                    break

        if allOkay:
            creditList = []
            for row in range(self.twCredit.rowCount()):
                particular = self.twCredit.item(row, 0)
                particular_text = particular.text() if particular is not None else ""

                amount = self.twCredit.item(row, 1)
                amount_text = amount.text() if amount is not None else ""

                if particular_text and amount_text:
                    try:
                        amount_text_float = float(amount_text)
                        if amount_text_float < 0:
                            QMessageBox.critical(self, "Invalid Amount!", f"Row Number {row + 1} Has A Negative Amount In Credit!")
                            allOkay = False
                            break
                    except ValueError:
                        QMessageBox.critical(self, "Invalid Entry!", f"Row Number {row + 1} Has An Invalid Entry As Amount In Credit!")
                        allOkay = False
                        break

                if particular_text and amount_text:
                    creditList.append([len(creditList) + 1, particular_text, float(amount_text)])
                elif particular_text and not amount_text:
                    QMessageBox.critical(self, "No Amount!", f"Row Number {row + 1} Has No Amount In Credit!")
                    allOkay = False
                    break
                elif not particular_text and amount_text:
                    QMessageBox.critical(self, "No Particular!", f"Row Number {row + 1} Has No Particular In Credit!")
                    allOkay = False
                    break

        if allOkay:

            try:
                cost_per_unit = f'{float(self.lePricePerUnit.text()):.2f}'
            except ValueError:
                cost_per_unit = ''

            insert_query = f"""
                INSERT INTO TRANSPORTS(
                    TRANSPORT_ID, SOURCE_ID, SOURCE, DESTINATION_ID, DESTINATION, DATE_STRING, FULL_DATE, YEAR, MONTH, 
                    DAY, VEHICLE_OWNER_ID, VEHICLE_OWNER_NAME, CAR_ID, CAR_NO, DRIVER_ID, DRIVER_NAME, 
                    CONTRACT_AMOUNT_WITH_COMPANY, CONTRACT_AMOUNT_WITH_VEHICLE_OWNER, PROFIT, GOODS_UNIT, NO_OF_UNIT, 
                    COST_PER_UNIT, TOTAL_COST, DEBITS, CREDITS, DEBIT_AMOUNT, CREDIT_AMOUNT, NOTES, BILL_GENERATION, 
                    BILL_GENERATED, SOURCE_ROAD, SOURCE_CITY, SOURCE_DISTRICT, SOURCE_PIN, DESTINATION_ROAD, 
                    DESTINATION_CITY, DESTINATION_DISTRICT, DESTINATION_PIN, INVOICE_NO, LR_NO, 
                    BILL_GENERATED_DATE_STRING, BILL_GENERATED_FULL_DATE, BILL_GENERATED_YEAR, BILL_GENERATED_MONTH, 
                    BILL_GENERATED_DAY
                )
                VALUES(
                    {int(self.leTransportID.text().replace("TR-", ""))},
                    {self.company_id_dict[self.cbSources.currentText()]},
                    '{self.company_name_dict[self.company_id_dict[self.cbSources.currentText()]]}',
                    {self.company_id_dict[self.cbDestinations.currentText()]},
                    '{self.company_name_dict[self.company_id_dict[self.cbDestinations.currentText()]]}',
                    '{self.deTransportDate.text()}',
                    {ef.dateToInt(self.deTransportDate.text())},
                    {int(self.deTransportDate.text().split('-')[2])},
                    {ef.monthStrToMonthNo(self.deTransportDate.text().split('-')[1])},
                    {int(self.deTransportDate.text().split('-')[0])},
                    {self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]},
                    '{self.vehicle_owner_name_dict[self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]]}',
                    {self.car_id_dict[self.cbCarNumbers.currentText()]},
                    '{self.car_number_dict[self.car_id_dict[self.cbCarNumbers.currentText()]]}',
                    {self.driver_id_dict[self.cbDriverNames.currentText()]},
                    '{self.driver_name_dict[self.driver_id_dict[self.cbDriverNames.currentText()]]}',
                    {round(float(self.leContractWithCompany.text()), 2)},
                    {round(float(self.leContractWithVehicleOwner.text()), 2)},
                    {round(float(self.leProfit.text()), 2)},
                    '{self.cbVehicleUnit.currentText()}',
                    {float(self.leNoOfUnit.text())},
                    '{cost_per_unit}',
                    {round(float(self.leTotalCost.text()), 2)},
                    '{json.dumps(debitList)}',
                    '{json.dumps(creditList)}',
                    {round(float(self.leTotalAmountInDebit.text().replace('₹', '').strip()), 2)},
                    {round(float(self.leTotalAmountInCredit.text().replace('₹', '').strip()), 2)},
                    '{self.teNotes.toPlainText()}',
                    {int(self.chkBillGeneration.isChecked())},
                    {0},
                    '{self.leSourceAddressRoad.text().strip().title()}',
                    '{self.leSourceAddressCity.text().strip().title()}',
                    '{self.cbSourceDistrict.currentText().strip().title()}',
                    '{self.leSourceAddressPin.text().strip().title()}',
                    '{self.leDestinationAddressRoad.text().strip().title()}',
                    '{self.leDestinationAddressCity.text().strip().title()}',
                    '{self.cbDestinationDistrict.currentText().strip().title()}',
                    '{self.leDestinationAddressPin.text().strip().title()}',
                    '{self.leInvoiceNo.text()}',
                    '{self.leLrNo.text()}',
                    '-',
                    {0},
                    {0},
                    {0},
                    {0}
                );
            """
            self.cursor.execute(insert_query)
            self.db_con.commit()

            self.leTransportID.setText(f"TR-{int(self.leTransportID.text().replace('TR-', '')) + 1}")
            self.performReset()
            QMessageBox.information(self, "Inserted!", "New transport entry created!")


    def btnResetClicked(self):
        answer = QMessageBox.question(self, "Reset?", "This will remove all the entries. Continue?", QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.performReset()

    def performReset(self):
        self.cbSources.setCurrentIndex(0)
        self.cbDestinations.setCurrentIndex(1)
        self.cbVehicleOwners.setCurrentIndex(0)

        today = dt.now()
        day = today.day
        month = today.month
        year = today.year
        self.deTransportDate.setDate(QDate(year, month, day))

        self.leContractWithCompany.setText("")
        self.leContractWithVehicleOwner.setText("")
        self.leProfit.setText("")
        self.leNoOfUnit.setText("")
        self.lePricePerUnit.setText("")
        self.leTotalCost.setText("")
        self.teNotes.setText("")
        self.leInvoiceNo.setText("")
        self.leLrNo.setText("")

        try: self.cbSourceAddressHistory.setCurrentIndex(0)
        except Exception: pass
        try: self.cbDestinationAddressHistory.setCurrentIndex(0)
        except Exception: pass
        self.cbSourceDistrict.setCurrentIndex(0)
        self.cbDestinationDistrict.setCurrentIndex(0)
        self.leSourceAddressRoad.setText("")
        self.leSourceAddressCity.setText("")
        self.leSourceAddressPin.setText("")
        self.leDestinationAddressRoad.setText("")
        self.leDestinationAddressCity.setText("")
        self.leDestinationAddressPin.setText("")
        self.leTotalAmountInDebit.setText("₹ 0.00")
        self.leTotalAmountInCredit.setText("₹ 0.00")

        self.twDebit.setRowCount(0)
        self.twDebit.setRowCount(5)
        self.twCredit.setRowCount(0)
        self.twCredit.setRowCount(5)

        self.chkBillGeneration.setChecked(False)

        self.cbSourcesTextChanged()
        self.cbDestinationsTextChanged()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddTransportApp()
    window.show()
    sys.exit(app.exec_())
