from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType

import sys
from datetime import datetime as dt
import sqlite3

import essential_functions as ef
import json

UpdateTransportUI, _ = loadUiType("__GUIs/UpdateTransport.ui")


class UpdateTransportApp(QMainWindow, UpdateTransportUI):
    def __init__(self, parent=None):
        super(UpdateTransportApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.parent = parent

        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor

        self.shouldOpen = None
        self.shouldOpenFalseShortMessage = ""
        self.shouldOpenFalseLongMessage = ""

        self.transport_id_dict = {}
        self.transport_name_dict = {}
        self.company_id_dict = {}
        self.company_name_dict = {}
        self.source_company_cb_index = {}
        self.destination_company_cb_index = {}
        self.vehicle_owner_id_dict = {}
        self.vehicle_owner_name_dict = {}
        self.vehicle_owner_cb_index = {}
        self.driver_id_dict = {'': -1}
        self.driver_name_dict = {-1: ''}
        self.driver_cb_index = {-1: -1}
        self.car_id_dict = {'': -1}
        self.car_number_dict = {-1: ''}
        self.car_cb_index = {-1: -1}

        self.source_address_history_dict = {}
        self.destination_address_history_dict = {}
        self.districts = {}
        self.districts_cb_index = {}

        self.setLowestAndHighestDate()
        self.shouldOpenCheck()
        self.doEssentialWorks()
        self.setAtMiddle()
        self.handleButtons()
        self.performReset()

    def setLowestAndHighestDate(self):
        select_query = """
            SELECT
                MIN(FULL_DATE), MAX(FULL_DATE)
            FROM
                TRANSPORTS;
        """
        self.cursor.execute(select_query)
        days = self.cursor.fetchall()[0]
        lowest_day = days[0]
        highest_day = days[1]

        if lowest_day is None and highest_day is None:
            today = dt.now()
            day = today.day
            month = today.month
            year = today.year
            self.deLowestTransportDate.setDate(QDate(year, month, day))
            self.deHighestTransportDate.setDate(QDate(year, month, day))
        else:
            lowest_day = int(lowest_day)
            highest_day = int(highest_day)

            year = lowest_day // 10000
            month = lowest_day % 10000 // 100
            day = lowest_day % 10000 % 100
            self.deLowestTransportDate.setDate(QDate(year, month, day))

            year = highest_day // 10000
            month = highest_day % 10000 // 100
            day = highest_day % 10000 % 100
            self.deHighestTransportDate.setDate(QDate(year, month, day))

    def shouldOpenCheck(self):
        # Setting Transports #
        self.cbTransports.clear()
        self.transport_id_dict.clear()
        self.transport_name_dict.clear()

        select_query = f"""
            SELECT
                TRANSPORT_ID, SOURCE, DESTINATION, DATE_STRING, FULL_DATE
            FROM
                TRANSPORTS
            WHERE
                {ef.dateToInt(self.deLowestTransportDate.text())} <= FULL_DATE
                AND
                {ef.dateToInt(self.deHighestTransportDate.text())} >= FULL_DATE 
            ORDER BY
                FULL_DATE DESC;
        """
        self.cursor.execute(select_query)
        transports = self.cursor.fetchall()
        transports.sort(reverse=True, key=lambda x: (x[4], x[0]))
        transport_counter = 1
        z_fill_length = len(str(len(transports)))
        self.cbTransports.addItem("---SELECT TRANSPORTS---")
        for transport_id, source, destination, date_string, _ in transports:
            key = f"{str(transport_counter).zfill(z_fill_length)} - {date_string} - {source} -> {destination}"
            self.transport_id_dict[key] = transport_id
            self.transport_name_dict[transport_id] = key
            self.cbTransports.addItem(key)
            transport_counter += 1

        # Setting Companies #
        self.cbSources.clear()
        self.company_id_dict.clear()
        self.company_name_dict.clear()
        self.cbDestinations.clear()
        self.source_company_cb_index.clear()
        self.destination_company_cb_index.clear()
        
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
                key = f"{str(company_counter).zfill(z_fill_length)} - {company_name}"
                self.company_id_dict[key] = company_id
                self.company_name_dict[company_id] = company_name
                self.cbSources.addItem(key)
                self.cbDestinations.addItem(key)
                self.source_company_cb_index[company_id] = company_counter - 1
                self.destination_company_cb_index[company_id] = company_counter - 1
                company_counter += 1
            self.cbSources.setCurrentIndex(0)
            self.cbDestinations.setCurrentIndex(1)

        # Setting Vehicle Owners #
        self.cbVehicleOwners.clear()
        self.vehicle_owner_id_dict.clear()
        self.vehicle_owner_name_dict.clear()
        self.vehicle_owner_cb_index.clear()
        
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
                key = f"{str(vehicle_owner_counter).zfill(z_fill_length)} - {vehicle_owner_name}"
                self.vehicle_owner_id_dict[key] = vehicle_owner_id
                self.vehicle_owner_name_dict[vehicle_owner_id] = vehicle_owner_name
                self.cbVehicleOwners.addItem(key)
                self.vehicle_owner_cb_index[vehicle_owner_id] = vehicle_owner_counter - 1
                vehicle_owner_counter += 1

        self.shouldOpen = True

        # Setting Cars #
        self.cbCarNumbers.clear()
        self.car_id_dict.clear()
        self.car_number_dict.clear()
        self.car_cb_index = {-1: -1}
        
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
                key = f"{str(car_counter).zfill(z_fill_length)} - {car_number}"
                self.car_id_dict[key] = car_id
                self.car_number_dict[car_id] = car_number
                self.cbCarNumbers.addItem(key)
                self.car_cb_index[car_id] = car_counter - 1
                car_counter += 1

        # Setting Drivers #
        self.cbDriverNames.clear()
        self.driver_cb_index = {-1:-1}
        self.driver_id_dict.clear()
        self.driver_name_dict.clear()
        
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
        driver_counter = 1
        drivers = self.cursor.fetchall()
        if drivers:
            z_fill_length = len(str(len(drivers)))
            for driver_id, driver_name in drivers:
                key = f"{str(driver_counter).zfill(z_fill_length)} - {driver_name}"
                self.driver_id_dict[key] = driver_id
                self.driver_name_dict[driver_id] = driver_name
                self.cbDriverNames.addItem(key)
                self.driver_cb_index[driver_id] = driver_counter - 1
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
            new_driver_counter = 1
            z_fill_length = len(str(len(drivers)))
            for driver_id, driver_name, vehicle_owner_name in drivers:
                key = f"{str(new_driver_counter).zfill(z_fill_length)} - {driver_name} ({vehicle_owner_name})"
                self.driver_id_dict[key] = driver_id
                self.driver_name_dict[driver_id] = driver_name
                self.cbDriverNames.addItem(key)
                new_driver_counter += 1
                self.driver_cb_index[driver_id] = driver_counter - 1
                driver_counter += 1

        # Setting Units #
        self.cbVehicleUnit.clear()
        
        self.cbVehicleUnit.addItem("Piece")
        self.cbVehicleUnit.addItem("Litre")
        self.cbVehicleUnit.addItem("Ton")

        # Setting Districts #
        self.cbSourceDistrict.clear()
        self.cbDestinationDistrict.clear()
        
        districts = [
            "Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah",
            "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas",
            "Paschim Medinipur", "Paschim Burdwan", "Purba Burdwan", "Purba Medinipur", "Purulia", "South 24 Parganas",
            "Uttar Dinajpur", "Sunderban", "Ichhemati", "Ranaghat", "Bishnupur", "Jangipur", "Behrampur"
        ]
        districts.sort(key=lambda state: state.upper())
        for ind, district in enumerate(districts):
            self.districts[district] = ind
            self.cbSourceDistrict.addItem(district)
            self.cbDestinationDistrict.addItem(district)
            self.districts_cb_index[district] = ind
        self.cbSourceDistrict.setCurrentIndex(0)
        self.cbDestinationDistrict.setCurrentIndex(0)

    def doEssentialWorks(self):
        self.twDebit.horizontalHeader().setStretchLastSection(True)
        self.twDebit.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.twCredit.horizontalHeader().setStretchLastSection(True)
        self.twCredit.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.chkBillGenerationToggled()

        self.cbVehicleOwnersTextChanged()

        self.leTotalAmountInDebit.setText("₹ 0.00")
        self.leTotalAmountInCredit.setText("₹ 0.00")

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def loadData(self, transport_id):
        select_query = f"""
            SELECT
                *
            FROM
                TRANSPORTS
            WHERE
                TRANSPORT_ID = {transport_id};
        """
        self.cursor.execute(select_query)
        transport_data = self.cursor.fetchall()[0]

        source_id = int(transport_data[1])
        source = transport_data[2]
        source_road = transport_data[3]
        source_city = transport_data[4]
        source_district = transport_data[5]
        source_pin = transport_data[6]
        destination_id = int(transport_data[7])
        destination = transport_data[8]
        destination_road = transport_data[9]
        destination_city = transport_data[10]
        destination_district = transport_data[11]
        destination_pin = transport_data[12]
        date_string = transport_data[13]
        full_date = int(transport_data[14])
        year = int(transport_data[15])
        month = int(transport_data[16])
        day = int(transport_data[17])
        vehicle_owner_id = int(transport_data[18])
        vehicle_owner_name = transport_data[19]
        car_id = int(transport_data[20])
        car_no = transport_data[21]
        driver_id = int(transport_data[22])
        driver_name = transport_data[23]
        contract_amount_with_company = float(transport_data[24])
        contract_amount_with_vehicle_owner = float(transport_data[25])
        profit = float(transport_data[26])
        goods_unit = transport_data[27]
        no_of_unit = int(transport_data[28])
        cost_per_unit = transport_data[29]
        total_cost = float(transport_data[30])
        debits = json.loads(transport_data[31])
        credits = json.loads(transport_data[32])
        debit_amount = float(transport_data[33])
        credit_amount = float(transport_data[34])
        notes = transport_data[35]
        invoice_no = transport_data[36]
        lr_no = transport_data[37]
        bill_generation = int(transport_data[38])
        bill_generated = int(transport_data[39])

        # print(
        #     f"""source_id = {source_id}, source = {source}, source_road = {source_road}, source_city = {source_city}, source_district = {source_district}, source_pin = {source_pin}, destination_id = {destination_id}, destination = {destination}, destination_road = {destination_road}, destination_city = {destination_city}, destination_district = {destination_district}, destination_pin = {destination_pin}, date_string = {date_string}, full_date = {full_date}, year = {year}, month = {month}, day = {day}, vehicle_owner_id = {vehicle_owner_id}, vehicle_owner_name = {vehicle_owner_name}, car_id = {car_id}, car_no = {car_no}, driver_id = {driver_id}, driver_name = {driver_name}, contract_amount_with_company = {contract_amount_with_company}, contract_amount_with_vehicle_owner = {contract_amount_with_vehicle_owner}, profit = {profit}, goods_unit = {goods_unit}, no_of_unit = {no_of_unit}, cost_per_unit = {cost_per_unit}, total_cost = {total_cost}, debits = {debits}, credits = {credits}, notes = {notes}, invoice_no = {invoice_no}, lr_no = {lr_no}, bill_generation = {bill_generation}, bill_generated = {bill_generated}""")

        # Setting Data #
        self.leTransportID.setText(f"TR-{transport_id}")

        self.cbSources.setCurrentIndex(self.source_company_cb_index[source_id])
        self.leSourceAddressRoad.setText(source_road)
        self.leSourceAddressCity.setText(source_city)
        self.cbSourceDistrict.setCurrentIndex(self.districts_cb_index[source_district])
        self.leSourceAddressPin.setText(source_pin)
        self.cbSourceAddressHistory.setCurrentIndex(0)

        self.cbDestinations.setCurrentIndex(self.destination_company_cb_index[destination_id])
        self.leDestinationAddressRoad.setText(destination_road)
        self.leDestinationAddressCity.setText(destination_city)
        self.cbDestinationDistrict.setCurrentIndex(self.districts_cb_index[destination_district])
        self.leDestinationAddressPin.setText(destination_pin)
        self.cbDestinationAddressHistory.setCurrentIndex(0)

        self.cbVehicleOwners.setCurrentIndex(self.vehicle_owner_cb_index[vehicle_owner_id])
        if car_id > 0: self.cbCarNumbers.setCurrentIndex(self.car_cb_index[car_id])
        if driver_id > 0: self.cbDriverNames.setCurrentIndex(self.driver_cb_index[driver_id])

        self.leContractWithCompany.setText(f"{contract_amount_with_company:.2f}")
        self.leContractWithVehicleOwner.setText(f"{contract_amount_with_vehicle_owner:.2f}")
        self.leProfit.setText(f"{profit:.2f}")

        self.cbVehicleUnit.setCurrentIndex(0 if goods_unit == "Piece" else 1 if goods_unit == "Litre" else 2)
        self.leNoOfUnit.setText(str(no_of_unit))
        self.lePricePerUnit.setText(f'{float(cost_per_unit):.2f}' if cost_per_unit else '')
        self.leTotalCost.setText(f"{total_cost:.2f}")

        self.twDebit.setRowCount(0)
        self.twDebit.setRowCount(max(5, len(debits)))
        self.twCredit.setRowCount(0)
        self.twCredit.setRowCount(max(5, len(credits)))
        for ind, particular, amount in debits:
            self.twDebit.setItem(ind-1, 0, QTableWidgetItem(particular))
            self.twDebit.setItem(ind-1, 1, QTableWidgetItem(f"{amount:.2f}"))
        for ind, particular, amount in credits:
            self.twCredit.setItem(ind-1, 0, QTableWidgetItem(particular))
            self.twCredit.setItem(ind-1, 1, QTableWidgetItem(f"{amount:.2f}"))
        self.leTotalAmountInDebit.setText(f"₹ {debit_amount:.2f}")
        self.leTotalAmountInCredit.setText(f"₹ {credit_amount:.2f}")

        self.teNotes.setText(notes)
        self.deTransportDate.setDate(QDate(year, month, day))
        self.leInvoiceNo.setText(invoice_no)
        self.leLrNo.setText(lr_no)
        self.chkBillGeneration.setChecked(bill_generation == 1)
        self.chkBillGenerated.setChecked(bill_generated == 1)

    def handleButtons(self):
        self.cbSources.currentTextChanged.connect(self.cbSourcesTextChanged)
        self.cbDestinations.currentTextChanged.connect(self.cbDestinationsTextChanged)
        self.cbVehicleOwners.currentTextChanged.connect(self.cbVehicleOwnersTextChanged)
        self.cbTransports.currentTextChanged.connect(self.cbTransportsTextChanged)

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

        self.btnUpdateTransport.clicked.connect(self.btnUpdateTransportClicked)
        self.btnReset.clicked.connect(self.btnResetClicked)
        self.btnDeleteTransport.clicked.connect(self.btnDeleteTransportClicked)

        self.chkBillGeneration.toggled.connect(self.chkBillGenerationToggled)
        self.deLowestTransportDate.dateChanged.connect(self.deLowestHighestTransportDateChanged)
        self.deHighestTransportDate.dateChanged.connect(self.deLowestHighestTransportDateChanged)

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

    def deLowestHighestTransportDateChanged(self):
        self.performReset()
        self.shouldOpenCheck()

    def chkBillGenerationToggled(self):
        if not self.chkBillGeneration.isChecked():
            self.chkBillGenerated.setChecked(False)
            self.chkBillGenerated.setEnabled(False)
        else:
            self.chkBillGenerated.setEnabled(True)

    def cbTransportsTextChanged(self):
        if self.cbTransports.currentText() == "---SELECT TRANSPORTS---":
            self.performReset()
        else:
            try:
                transport_id = self.transport_id_dict[self.cbTransports.currentText()]
                self.performReset(all_reset=False)
                self.loadData(transport_id)
            except Exception:
                self.performReset()

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
                SOURCE_ID = {self.company_id_dict.get(self.cbSources.currentText(), 'NULL')}
            ORDER BY
                5 DESC;
        """
        self.cursor.execute(select_query)
        address_histories = self.cursor.fetchall()
        if address_histories:
            for source_road, source_city, source_district, source_pin, full_date in address_histories:
                source_address_histories.append(
                    {
                        "source_road": source_road,
                        "source_city": source_city,
                        "source_district": source_district,
                        "source_pin": source_pin,
                        "full_date": full_date
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
                DESTINATION_ID = {self.company_id_dict.get(self.cbDestinations.currentText(), 'NULL')}
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
        if self.cbVehicleOwners.currentText():
            vehicle_owner = self.vehicle_owner_name_dict[self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]]
            self.lblVehicleOwnerAccountName.setText(f"{vehicle_owner} A/c")

        # Change Cars #
        self.cbCarNumbers.clear()
        self.car_cb_index.clear()
        self.car_id_dict.clear()
        self.car_number_dict.clear()
        self.car_id_dict = {'': -1}
        self.car_number_dict = {-1: ''}

        self.car_cb_index = {-1: -1}
        select_query = f"""
            SELECT
                CAR_ID, CAR_NO
            FROM
                CARS
            WHERE
                VEHICLE_OWNER_ID = {self.vehicle_owner_id_dict.get(self.cbVehicleOwners.currentText(), 'NULL')}
            ORDER BY
                CAR_ID;
        """
        self.cursor.execute(select_query)
        cars = self.cursor.fetchall()
        if cars:
            car_counter = 1
            z_fill_length = len(str(len(cars)))
            for car_id, car_number in cars:
                key = f"{str(car_counter).zfill(z_fill_length)} - {car_number}"
                self.car_id_dict[key] = car_id
                self.car_number_dict[car_id] = car_number
                self.cbCarNumbers.addItem(key)
                self.car_cb_index[car_id] = car_counter - 1
                car_counter += 1

        # Changing Drivers #
        self.cbDriverNames.clear()
        self.driver_cb_index = {-1:-1}
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
                VEHICLE_OWNER_ID = {self.vehicle_owner_id_dict.get(self.cbVehicleOwners.currentText(), 'NULL')}
            ORDER BY
                DRIVER_ID;
        """
        self.cursor.execute(select_query)
        driver_counter = 1
        drivers = self.cursor.fetchall()
        if drivers:
            z_fill_length = len(str(len(drivers)))
            for driver_id, driver_name in drivers:
                key = f"{str(driver_counter).zfill(z_fill_length)} - {driver_name}"
                self.driver_id_dict[key] = driver_id
                self.driver_name_dict[driver_id] = driver_name
                self.cbDriverNames.addItem(key)
                self.driver_cb_index[driver_id] = driver_counter - 1
                driver_counter += 1

        select_query = f"""
            SELECT
                DRIVERS.DRIVER_ID, DRIVERS.NAME, VEHICLE_OWNERS.NAME
            FROM
                DRIVERS, VEHICLE_OWNERS
            WHERE
                DRIVERS.VEHICLE_OWNER_ID = VEHICLE_OWNERS.VEHICLE_OWNER_ID
                AND
                DRIVERS.VEHICLE_OWNER_ID != {self.vehicle_owner_id_dict.get(self.cbVehicleOwners.currentText(), 'NULL')}
            ORDER BY
                DRIVER_ID;
        """
        self.cursor.execute(select_query)
        drivers = self.cursor.fetchall()
        if drivers:
            new_driver_counter = 1
            z_fill_length = len(str(len(drivers)))
            for driver_id, driver_name, vehicle_owner_name in drivers:
                key = f"{str(new_driver_counter).zfill(z_fill_length)} - {driver_name} ({vehicle_owner_name})"
                self.driver_id_dict[key] = driver_id
                self.driver_name_dict[driver_id] = driver_name
                self.cbDriverNames.addItem(key)
                new_driver_counter += 1
                self.driver_cb_index[driver_id] = driver_counter - 1
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

    def btnUpdateTransportClicked(self):
        allOkay = True
        
        if allOkay:
            if self.cbTransports.currentText() == "---SELECT TRANSPORTS---":
                QMessageBox.critical(self, "No Transport Selected!", "Please select a transport!")
                allOkay = False
            else:
                try:
                    transport_id = self.transport_id_dict[self.cbTransports.currentText()]
                except Exception:
                    QMessageBox.critical(self, "No Transport Selected!", "Please select a transport!")
                    allOkay = False

        if allOkay:
            if self.company_id_dict[self.cbSources.currentText()] == self.company_id_dict[
                self.cbDestinations.currentText()]:
                QMessageBox.critical(self, "Source & Destination Are Same", "Please select different destination for a source!")
                allOkay = False

        if allOkay:
            if self.leProfit.text() == "":
                QMessageBox.critical(self, "No Profit", "Profit can't be blank!")
                allOkay = False

        if allOkay:
            if self.leTotalCost.text() == "":
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
                    QMessageBox.critical(self, "No Amount!", f"Row Number {row + 1} Has No Amount In Debit!")
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
            answer = QMessageBox.question(self, "Update?", f"This will update the transport entry for transport id {transport_id}. Continue?", QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:

                select_query = f"""
                    SELECT
                        BILL_GENERATED_DATE_STRING, 
                        BILL_GENERATED_FULL_DATE, 
                        BILL_GENERATED_YEAR, 
                        BILL_GENERATED_MONTH, 
                        BILL_GENERATED_DAY
                    FROM
                        TRANSPORTS
                    WHERE
                        TRANSPORT_ID = {transport_id};
                """
                self.cursor.execute(select_query)
                transport_entry = self.cursor.fetchall()[0]
                bill_generated_year = transport_entry[2]

                try:
                    cost_per_unit = f'{float(self.lePricePerUnit.text()):.2f}'
                except ValueError:
                    cost_per_unit = ''

                if self.chkBillGenerated.isChecked() and not bill_generated_year:
                    bill_generated_year = dt.now().year
                    bill_generated_month = dt.now().month
                    bill_generated_day = dt.now().day
                    bill_generated_full_date = int(f"{str(bill_generated_year).zfill(4)}{str(bill_generated_month).zfill(2)}{str(bill_generated_day).zfill(2)}")
                    bill_generated_date_string = f"{str(bill_generated_day).zfill(2)}-{ef.monthNoToMonthStr(bill_generated_month)}-{str(bill_generated_year).zfill(4)}"
                elif not self.chkBillGenerated.isChecked() and bill_generated_year:
                    bill_generated_year = 0
                    bill_generated_month = 0
                    bill_generated_day = 0
                    bill_generated_full_date = 0
                    bill_generated_date_string = '-'
                else:
                    bill_generated_year = transport_entry[2]
                    bill_generated_month = transport_entry[3]
                    bill_generated_day = transport_entry[4]
                    bill_generated_full_date = transport_entry[1]
                    bill_generated_date_string = transport_entry[0]


                update_query = f"""
                    UPDATE
                        TRANSPORTS
                    SET
                        SOURCE_ID = {self.company_id_dict[self.cbSources.currentText()]},
                        SOURCE = '{self.company_name_dict[self.company_id_dict[self.cbSources.currentText()]]}',
                        DESTINATION_ID = {self.company_id_dict[self.cbDestinations.currentText()]},
                        DESTINATION = '{self.company_name_dict[self.company_id_dict[self.cbDestinations.currentText()]]}',
                        DATE_STRING = '{self.deTransportDate.text()}',
                        FULL_DATE = {ef.dateToInt(self.deTransportDate.text())},
                        YEAR = {int(self.deTransportDate.text().split('-')[2])},
                        MONTH = {ef.monthStrToMonthNo(self.deTransportDate.text().split('-')[1])},
                        DAY = {int(self.deTransportDate.text().split('-')[0])},
                        VEHICLE_OWNER_ID = {self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]},
                        VEHICLE_OWNER_NAME = '{self.vehicle_owner_name_dict[self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]]}',
                        CAR_ID = {self.car_id_dict[self.cbCarNumbers.currentText()]},
                        CAR_NO = '{self.car_number_dict[self.car_id_dict[self.cbCarNumbers.currentText()]]}',
                        DRIVER_ID = {self.driver_id_dict[self.cbDriverNames.currentText()]},
                        DRIVER_NAME = '{self.driver_name_dict[self.driver_id_dict[self.cbDriverNames.currentText()]]}',
                        CONTRACT_AMOUNT_WITH_COMPANY = {round(float(self.leContractWithCompany.text()), 2)},
                        CONTRACT_AMOUNT_WITH_VEHICLE_OWNER = {round(float(self.leContractWithVehicleOwner.text()), 2)},
                        PROFIT = {round(float(self.leProfit.text()), 2)},
                        GOODS_UNIT = '{self.cbVehicleUnit.currentText()}',
                        NO_OF_UNIT = {float(self.leNoOfUnit.text())},
                        COST_PER_UNIT = '{cost_per_unit}',
                        TOTAL_COST = {round(float(self.leTotalCost.text()), 2)},
                        DEBITS = '{json.dumps(debitList)}',
                        CREDITS = '{json.dumps(creditList)}',
                        DEBIT_AMOUNT = {round(float(self.leTotalAmountInDebit.text().replace('₹', '').strip()), 2)},
                        CREDIT_AMOUNT = {round(float(self.leTotalAmountInCredit.text().replace('₹', '').strip()), 2)},
                        NOTES = '{self.teNotes.toPlainText()}',
                        BILL_GENERATION = {int(self.chkBillGeneration.isChecked())},
                        BILL_GENERATED = {int(self.chkBillGenerated.isChecked())},
                        SOURCE_ROAD = '{self.leSourceAddressRoad.text().strip().title()}',
                        SOURCE_CITY = '{self.leSourceAddressCity.text().strip().title()}',
                        SOURCE_DISTRICT = '{self.cbSourceDistrict.currentText().strip().title()}',
                        SOURCE_PIN = '{self.leSourceAddressPin.text().strip().title()}',
                        DESTINATION_ROAD = '{self.leDestinationAddressRoad.text().strip().title()}',
                        DESTINATION_CITY = '{self.leDestinationAddressCity.text().strip().title()}',
                        DESTINATION_DISTRICT = '{self.cbDestinationDistrict.currentText().strip().title()}',
                        DESTINATION_PIN = '{self.leDestinationAddressPin.text().strip().title()}',
                        INVOICE_NO = '{self.leInvoiceNo.text()}',
                        LR_NO = '{self.leLrNo.text()}',
                        BILL_GENERATED_DATE_STRING = '{bill_generated_date_string}',
                        BILL_GENERATED_FULL_DATE = {bill_generated_full_date},
                        BILL_GENERATED_YEAR = {bill_generated_year},
                        BILL_GENERATED_MONTH = {bill_generated_month},
                        BILL_GENERATED_DAY = {bill_generated_day}
                    WHERE
                        TRANSPORT_ID = {transport_id};
                """
                self.cursor.execute(update_query)
                self.db_con.commit()

                self.shouldOpenCheck()
                self.performReset()
                QMessageBox.information(self, "Updated!", f"Entry updated for Transport ID {transport_id}!")

    def btnDeleteTransportClicked(self):
        transport_id = self.leTransportID.text().replace("TR-", "")
        if not transport_id:
            QMessageBox.critical(self, "No Transport Selected!", "Please select at lease one transport entry to delete!")
        else:

            answer = QMessageBox.question(self, "Delete?", "This will delete the transport entry permanently. Continue?", QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:
                transport_id = int(transport_id)
                delete_query = f"""
                    DELETE
                    FROM
                        TRANSPORTS
                    WHERE
                        TRANSPORT_ID = {transport_id};
                """
                self.cursor.execute(delete_query)
                self.db_con.commit()

                # Setting Transports #
                self.cbTransports.clear()
                self.transport_id_dict.clear()
                self.transport_name_dict.clear()
                
                select_query = """
                    SELECT
                        TRANSPORT_ID, SOURCE, DESTINATION, DATE_STRING, FULL_DATE
                    FROM
                        TRANSPORTS
                    ORDER BY
                        FULL_DATE DESC;
                """
                self.cursor.execute(select_query)
                transports = self.cursor.fetchall()
                transport_counter = 1
                z_fill_length = len(str(len(transports)))
                self.cbTransports.addItem("---SELECT TRANSPORTS---")
                for transport_id, source, destination, date_string, _ in transports:
                    key = f"{str(transport_counter).zfill(z_fill_length)} - {date_string} - {source} --> {destination}"
                    self.transport_id_dict[key] = transport_id
                    self.transport_name_dict[transport_id] = key
                    self.cbTransports.addItem(key)
                    transport_counter += 1

                self.performReset()
                QMessageBox.information(self, "Deleted!", f"Entry deleted for Transport ID {transport_id}!")

    def btnResetClicked(self):
        answer = QMessageBox.question(self, "Reset?", "This will remove all the entries. Continue?", QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.performReset()

    def performReset(self, all_reset=True):
        if all_reset:
            try: self.cbTransports.setCurrentIndex(0)
            except Exception: pass
        self.cbSources.setCurrentIndex(0)
        self.cbDestinations.setCurrentIndex(1)
        self.cbVehicleOwners.setCurrentIndex(0)
        try: self.cbCarNumbers.setCurrentIndex(0)
        except Exception: pass
        try: self.cbDriverNames.setCurrentIndex(0)
        except Exception: pass

        today = dt.now()
        day = today.day
        month = today.month
        year = today.year
        self.deTransportDate.setDate(QDate(year, month, day))

        self.leTransportID.setText("")
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
        self.chkBillGenerated.setChecked(False)

        self.cbSourcesTextChanged()
        self.cbDestinationsTextChanged()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UpdateTransportApp()
    window.show()
    sys.exit(app.exec_())
