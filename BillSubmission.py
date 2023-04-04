from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType

import sys
import os
import sqlite3
import getpass
from itertools import zip_longest as zl
from pypdf import PdfMerger

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

BillSubmissionWindowUI, _ = loadUiType("__GUIs/BillSubmission.ui")


class BillSubmissionApp(QMainWindow, BillSubmissionWindowUI):
    def __init__(self, parent=None):
        super(BillSubmissionApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.childWindow = None

        self.parent = parent

        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor

        self.desktop = f"C:\\Users\\{getpass.getuser()}\\Desktop\\"
        self.shouldOpen = True

        self.company_id_dict = {}
        self.company_name_dict = {}
        self.vehicle_owner_id_dict = {}
        self.vehicle_owner_name_dict = {}
        self.bill_submission_id_dict = {}

        # self.lwGeneratedCompanyBills.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.setDefaultData()
        self.setDefaultDates()
        self.handleButtons()
        self.setAtMiddle()

    def getLastLocation(self):
        with open("__Files\\lastfilesavelocation.txt", "r") as file:
            path = file.read()
        if not os.path.exists(path):
            path = self.desktop
        with open("__Files\\lastfilesavelocation.txt", "w") as file:
            file.write(path)
        return path

    def setLastLocation(self, path):
        with open("__Files\\lastfilesavelocation.txt", "w") as file:
            file.write("\\".join(path.replace("/", "\\").split("\\")[:-1]))

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def setDefaultData(self):
        self.bill_submission_id_dict.clear()
        self.lwGeneratedCompanyBills.clear()
        select_query = """
            SELECT
                BILL_SUBMISSIONS.BILL_SUBMISSION_ID, BILL_SUBMISSIONS.DATE_STRING, 
                COMPANIES.NAME, BILL_SUBMISSIONS.FULL_DATE
            FROM
                BILL_SUBMISSIONS, COMPANIES
            WHERE
                BILL_SUBMISSIONS.BILL_GENERATED_FOR = COMPANIES.COMPANY_ID;
        """
        self.cursor.execute(select_query)
        bill_submissions = self.cursor.fetchall()
        bill_submissions.sort(reverse=True, key=lambda x: (x[3], x[0]))
        bill_submission_counter = 1
        for bill_submission_id, bill_submission_date, company_name, _ in bill_submissions:
            key = f"{bill_submission_counter} - {company_name} - {bill_submission_date}"
            self.bill_submission_id_dict[key] = bill_submission_id
            self.lwGeneratedCompanyBills.addItem(key)
            bill_submission_counter += 1


        self.company_id_dict.clear()
        self.company_name_dict.clear()
        self.cbCompanies.clear()
        select_query = """
            SELECT DISTINCT
                COMPANIES.COMPANY_ID, COMPANIES.NAME
            FROM
                COMPANIES, TRANSPORTS
            WHERE
                COMPANIES.COMPANY_ID = TRANSPORTS.SOURCE_ID
                AND
                TRANSPORTS.BILL_GENERATION = 1
                AND
                TRANSPORTS.BILL_GENERATED = 0;
        """
        self.cursor.execute(select_query)
        companies = self.cursor.fetchall()
        company_counter = 1
        for company_id, company_name in companies:
            key = f"{company_counter} - {company_name}"
            self.company_id_dict[key] = company_id
            self.company_name_dict[company_id] = company_name
            self.cbCompanies.addItem(key)
            company_counter += 1


        self.vehicle_owner_id_dict.clear()
        self.vehicle_owner_name_dict.clear()
        self.cbVehicleOwners.clear()
        select_query = """
            SELECT DISTINCT
                VEHICLE_OWNERS.VEHICLE_OWNER_ID, VEHICLE_OWNERS.NAME
            FROM
                VEHICLE_OWNERS, TRANSPORTS
            WHERE
                VEHICLE_OWNERS.VEHICLE_OWNER_ID = TRANSPORTS.VEHICLE_OWNER_ID;
        """
        self.cursor.execute(select_query)
        vehicle_owners = self.cursor.fetchall()
        vehicle_owner_counter = 1
        for vehicle_owner_id, vehicle_owner_name in vehicle_owners:
            key = f"{vehicle_owner_counter} - {vehicle_owner_name}"
            self.vehicle_owner_id_dict[key] = vehicle_owner_id
            self.vehicle_owner_name_dict[vehicle_owner_id] = vehicle_owner_name
            self.cbVehicleOwners.addItem(key)
            vehicle_owner_counter += 1

    def setDefaultDates(self):
        # Generated Bills #
        select_query = """
            SELECT
                MIN(FULL_DATE), MAX(FULL_DATE)
            FROM
                BILL_SUBMISSIONS;
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
            self.deLowestTransportDateCompanyGeneratedBill.setDate(QDate(year, month, day))
            self.deHighestTransportDateCompanyGeneratedBill.setDate(QDate(year, month, day))
        else:
            lowest_day = int(lowest_day)
            highest_day = int(highest_day)

            year = lowest_day // 10000
            month = lowest_day % 10000 // 100
            day = lowest_day % 10000 % 100
            self.deLowestTransportDateCompanyGeneratedBill.setDate(QDate(year, month, day))

            year = highest_day // 10000
            month = highest_day % 10000 // 100
            day = highest_day % 10000 % 100
            self.deHighestTransportDateCompanyGeneratedBill.setDate(QDate(year, month, day))

        # Generate Bills #
        select_query = f"""
            SELECT
                MIN(FULL_DATE), MAX(FULL_DATE)
            FROM
                TRANSPORTS
            WHERE
                SOURCE_ID = {self.company_id_dict.get(self.cbCompanies.currentText(), 0)}
                AND
                BILL_GENERATION = 1
                AND
                BILL_GENERATED = 0;
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
            self.deLowestTransportDateCompanyGenerateBill.setDate(QDate(year, month, day))
            self.deHighestTransportDateCompanyGenerateBill.setDate(QDate(year, month, day))
        else:
            lowest_day = int(lowest_day)
            highest_day = int(highest_day)

            year = lowest_day // 10000
            month = lowest_day % 10000 // 100
            day = lowest_day % 10000 % 100
            self.deLowestTransportDateCompanyGenerateBill.setDate(QDate(year, month, day))

            year = highest_day // 10000
            month = highest_day % 10000 // 100
            day = highest_day % 10000 % 100
            self.deHighestTransportDateCompanyGenerateBill.setDate(QDate(year, month, day))

        # Vehicle Owner Bills #
        select_query = f"""
            SELECT
                MIN(FULL_DATE), MAX(FULL_DATE)
            FROM
                TRANSPORTS
            WHERE
                VEHICLE_OWNER_ID = {self.vehicle_owner_id_dict.get(self.cbVehicleOwners.currentText(), 0)};
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
            self.deLowestTransportDateVehicleOwner.setDate(QDate(year, month, day))
            self.deHighestTransportDateVehicleOwner.setDate(QDate(year, month, day))
        else:
            lowest_day = int(lowest_day)
            highest_day = int(highest_day)

            year = lowest_day // 10000
            month = lowest_day % 10000 // 100
            day = lowest_day % 10000 % 100
            self.deLowestTransportDateVehicleOwner.setDate(QDate(year, month, day))

            year = highest_day // 10000
            month = highest_day % 10000 // 100
            day = highest_day % 10000 % 100
            self.deHighestTransportDateVehicleOwner.setDate(QDate(year, month, day))

    def handleButtons(self):
        self.cbCompanies.currentTextChanged.connect(self.cbCompaniesTextChanged)
        self.cbVehicleOwners.currentTextChanged.connect(self.cbVehicleOwnersTextChanged)

        self.btnGenerateCompanyBill.clicked.connect(self.btnGenerateCompanyBillClicked)
        self.btnViewVehicleOwnerBill.clicked.connect(self.btnViewVehicleOwnerBillClicked)
        self.btnViewCompanyBill.clicked.connect(self.btnViewCompanyBillClicked)
        self.lwGeneratedCompanyBills.doubleClicked.connect(self.btnViewCompanyBillClicked)

        self.deLowestTransportDateCompanyGeneratedBill.dateChanged.connect(self.deLowestHighestTransportDateCompanyGeneratedBillChanged)
        self.deHighestTransportDateCompanyGeneratedBill.dateChanged.connect(self.deLowestHighestTransportDateCompanyGeneratedBillChanged)

    def deLowestHighestTransportDateCompanyGeneratedBillChanged(self):
        self.bill_submission_id_dict.clear()
        self.lwGeneratedCompanyBills.clear()

        low_date_range = ef.dateToInt(self.deLowestTransportDateCompanyGeneratedBill.text())
        high_date_range = ef.dateToInt(self.deHighestTransportDateCompanyGeneratedBill.text())

        select_query = f"""
            SELECT
                BILL_SUBMISSIONS.BILL_SUBMISSION_ID, BILL_SUBMISSIONS.DATE_STRING, 
                COMPANIES.NAME, BILL_SUBMISSIONS.FULL_DATE
            FROM
                BILL_SUBMISSIONS, COMPANIES
            WHERE
                BILL_SUBMISSIONS.BILL_GENERATED_FOR = COMPANIES.COMPANY_ID
                AND
                {low_date_range} <= BILL_SUBMISSIONS.FULL_DATE
                AND
                BILL_SUBMISSIONS.FULL_DATE <= {high_date_range};
        """
        self.cursor.execute(select_query)
        bill_submissions = self.cursor.fetchall()
        bill_submissions.sort(reverse=True, key=lambda x: (x[3], x[0]))
        bill_submission_counter = 1
        for bill_submission_id, bill_submission_date, company_name, _ in bill_submissions:
            key = f"{bill_submission_counter} - {company_name} - {bill_submission_date}"
            self.bill_submission_id_dict[key] = bill_submission_id
            self.lwGeneratedCompanyBills.addItem(key)
            bill_submission_counter += 1

    def cbCompaniesTextChanged(self):
        # Generate Bills #
        select_query = f"""
            SELECT
                MIN(FULL_DATE), MAX(FULL_DATE)
            FROM
                TRANSPORTS
            WHERE
                SOURCE_ID = {self.company_id_dict.get(self.cbCompanies.currentText(), 0)}
                AND
                BILL_GENERATION = 1
                AND
                BILL_GENERATED = 0;
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
            self.deLowestTransportDateCompanyGenerateBill.setDate(QDate(year, month, day))
            self.deHighestTransportDateCompanyGenerateBill.setDate(QDate(year, month, day))
        else:
            lowest_day = int(lowest_day)
            highest_day = int(highest_day)

            year = lowest_day // 10000
            month = lowest_day % 10000 // 100
            day = lowest_day % 10000 % 100
            self.deLowestTransportDateCompanyGenerateBill.setDate(QDate(year, month, day))

            year = highest_day // 10000
            month = highest_day % 10000 // 100
            day = highest_day % 10000 % 100
            self.deHighestTransportDateCompanyGenerateBill.setDate(QDate(year, month, day))

    def cbVehicleOwnersTextChanged(self):
        select_query = f"""
            SELECT
                MIN(FULL_DATE), MAX(FULL_DATE)
            FROM
                TRANSPORTS
            WHERE
                VEHICLE_OWNER_ID = {self.vehicle_owner_id_dict.get(self.cbVehicleOwners.currentText(), 0)};
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
            self.deLowestTransportDateVehicleOwner.setDate(QDate(year, month, day))
            self.deHighestTransportDateVehicleOwner.setDate(QDate(year, month, day))
        else:
            lowest_day = int(lowest_day)
            highest_day = int(highest_day)

            year = lowest_day // 10000
            month = lowest_day % 10000 // 100
            day = lowest_day % 10000 % 100
            self.deLowestTransportDateVehicleOwner.setDate(QDate(year, month, day))

            year = highest_day // 10000
            month = highest_day % 10000 // 100
            day = highest_day % 10000 % 100
            self.deHighestTransportDateVehicleOwner.setDate(QDate(year, month, day))

    def generateHtmlForVehicleOwner(self, vehicle_owner_id, low_date_range, high_date_range, pdf_save_path):
        select_query = f"""
            SELECT
                TRANSPORT_ID, VEHICLE_OWNER_NAME, SOURCE, DESTINATION, DATE_STRING, CAR_NO, DRIVER_NAME, FULL_DATE,
                INVOICE_NO, LR_NO, DEBITS, CREDITS, DEBIT_AMOUNT, CREDIT_AMOUNT, NOTES, CONTRACT_AMOUNT_WITH_VEHICLE_OWNER 
            FROM
                TRANSPORTS
            WHERE
                VEHICLE_OWNER_ID = {vehicle_owner_id}
                AND
                {low_date_range} <= FULL_DATE
                AND
                FULL_DATE <= {high_date_range};
        """
        self.cursor.execute(select_query)
        transports = self.cursor.fetchall()
        transports.sort(key=lambda x: (x[7], x[0]))

        temp_file_path = ".\\__Files\__Temp\\"
        pdf_files = []

        for transport in transports:
            transport_id = int(transport[0])
            vehicle_owner_name = transport[1]
            source = transport[2]
            destination = transport[3]
            date_string = transport[4]
            vehicle_no = transport[5]
            driver_name = transport[6]
            full_date = int(transport[7])
            invoice_no = transport[8]
            lr_no = transport[9]
            debitList = json.loads(transport[10])
            creditList = json.loads(transport[11])
            debit_amount = round(float(transport[12]), 2)
            credit_amount = round(float(transport[13]), 2)
            notes = transport[14].replace("\n", "<br>")
            contract_amount_with_vehicle_owner = round(float(transport[15]), 2)

            HTML = f"""
                <html>
                    <body>
                    
                        <center><font size="20"><b>K.B. Roadways</b></font></center>
                        <center><font size="5"><b>{vehicle_owner_name}</b></font></center>
                        
                        <center>
                            <table border="0" cellspacing="0" cellpadding="2">
                                <tr>
                                    <td><b>From : </b></td>
                                    <td>{source}</td>
                                </tr>
                                <tr>
                                    <td><b>To : </b></td>
                                    <td>{destination}</td>
                                </tr>
                                <tr>
                                    <td><b>Date : </b></td>
                                    <td>{date_string}</td>
                                </tr>
                                <tr>
                                    <td><b>Vehicle No. : </b></td>
                                    <td>{vehicle_no}</td>
                                </tr>
                                <tr>
                                    <td><b>Driver : </b></td>
                                    <td>{driver_name}</td>
                                </tr>
                                <tr>
                                    <td><b>Invoice No. : </b></td>
                                    <td>{invoice_no}</td>
                                </tr>
                                <tr>
                                    <td><b>LR No. : </b></td>
                                    <td>{lr_no}</td>
                                </tr>
                            </table>
                        </center>
                        
                        <br>
                        
                        <center>
                            <table border="1" cellspacing="2" cellpadding="4">
                                
                                <tr>
                                    <td colspan="4" align="center">
                                        {vehicle_owner_name} A/c
                                    </td>
                                </tr>
                                
                                <tr>
                                    <td colspan="2" align="left">
                                        Dr.
                                    </td>
                                    <td colspan="2" align="right">
                                        Cr.
                                    </td>
                                </tr>
                                
                                <tr>
                                    <td>
                                        Particulars
                                    </td>
                                    <td>
                                        Amount(₹)
                                    </td>
                                    <td>
                                        Particulars
                                    </td>
                                    <td>
                                        Amount(₹)
                                    </td>
                                </tr>
            """

            for tup in zl(debitList, creditList):
                dr = tup[0]
                if dr is not None:
                    dr_particular = dr[1]
                    dr_amount = ef.formatNumber(round(float(dr[2]), 2))
                else:
                    dr_particular = ""
                    dr_amount = ""

                cr = tup[1]
                if cr is not None:
                    cr_particular = cr[1]
                    cr_amount = ef.formatNumber(round(float(cr[2]), 2))
                else:
                    cr_particular = ""
                    cr_amount = ""

                HTML += f"""
                
                                    <tr>
                                        <td>
                                            {dr_particular}
                                        </td>
                                        <td>
                                            {dr_amount}
                                        </td>
                                        <td>
                                            {cr_particular}
                                        </td>
                                        <td>
                                            {cr_amount}
                                        </td>
                                    </tr>
                                    
                """

            HTML += f"""
                                <tr>
                                    <td colspan="2" align="right">
                                        ₹ {debit_amount}
                                    </td>
                                    <td colspan="2" align="right">
                                        ₹ {credit_amount}
                                    </td>
                                </tr>
                                
                            </table>
                        </center>
                        
                        <br>
                        
                        <center>
                            <b>NOTE: <b>{notes}
                        </center>
                        
                        <br>
                        
                        <center>
                            <b>Contract With Vehicle Owner :</b> ₹ {ef.formatNumber(round(contract_amount_with_vehicle_owner, 2))}<br>
                            <b>Remaining Payment :</b> ₹ {ef.formatNumber(round(contract_amount_with_vehicle_owner - credit_amount, 2))}
                        </center>
                    
                    </body>
                </html>
            """

            filename = f"{temp_file_path}{transport_id}.pdf"
            pdf_files.append(filename)
            self.htmlToPDF(HTML, filename)

        merger = PdfMerger()
        for pdf in pdf_files:
            merger.append(pdf)
        merger.write(pdf_save_path)
        merger.close()

        for pdf in pdf_files:
            os.remove(pdf)

        QMessageBox.information(self, "Done!", "Bill generated successfully!!")

    def generateHtmlForCompany(self, company_id, bill_number, low_date_range, high_date_range, pdf_save_path):
        select_query = f"""
            SELECT
                TRANSPORT_ID, DATE_STRING, CAR_NO, LR_NO, INVOICE_NO, FULL_DATE,
                SOURCE_CITY, DESTINATION_CITY, NO_OF_UNIT, CONTRACT_AMOUNT_WITH_COMPANY
            FROM
                TRANSPORTS
            WHERE
                SOURCE_ID = {company_id}
                AND
                {low_date_range} <= FULL_DATE
                AND
                FULL_DATE <= {high_date_range}
                AND
                BILL_GENERATION = 1
                AND                
                BILL_GENERATED = 0;
        """
        self.cursor.execute(select_query)
        transports = self.cursor.fetchall()
        transports.sort(key=lambda x: (x[5], x[0]))

        select_query = f"""
            SELECT
                NAME, ADDRESS
            FROM
                COMPANIES
            WHERE
                COMPANY_ID = {company_id};
        """
        self.cursor.execute(select_query)
        company = self.cursor.fetchall()
        company_name = company[0][0]
        company_address = company[0][1].replace("\n", "<br>")

        today = dt.now()
        day = today.day
        month = today.month
        year = today.year
        today = f"{str(day).zfill(2)}-{ef.monthNoToMonthStr(month)}-{year}"

        transport_ids = []

        HTML = f"""
            <html>
                <body>
                    <table align="center" border="1" cellspacing="1" cellpadding="10">
                    
                        <tr rowspan="6" valign="center">
                            <td colspan="5">
                                <font size="6"><b>K.B. ROADWAYS.</b></font><br>
                                491, G.T. Road, Mahesh<br>
                                Serampore, Hooghly<br>
                                Email - <a href = "mailto:b.bhusan2011@rediffmail.com">b.bhusan2011@rediffmail.com</a><br>
                                PAN NO: AHSPK8452D<br>
                                GSTIN No: 19AHSPK8452D2ZV<br>
                            </td>
                            <td colspan="4">
                                <font size="6"><b>{company_name}</b></font><br>
                                {company_address}
                            </td>
                        </tr>
                        
                        <tr valign="center">
                            <td colspan="5">
                                <b>BILL NO:</b> {bill_number}
                            </td>
                            <td colspan="4">
                                <b>DATE:</b> {today}
                            </td>
                        </tr>
                        
                        <tr align="center" valign="center">
                            <td><b>SL</b></td>
                            <td><b>DATE</b></td>
                            <td><b>VEHICLE NO.</b></td>
                            <td><b>L.R. NO</b></td>
                            <td><b>INVOICE NO.</b></td>
                            <td><b>FROM</b></td>
                            <td><b>TO</b></td>
                            <td><b>VEHI TYPE</b></td>
                            <td><b>FREIGHT</b></td>
                        </tr>
        """

        total_amount = 0
        for ind, transport in enumerate(transports):
            transport_id = transport[0]
            transport_ids.append(transport_id)

            date_string = transport[1]
            vehicle_no = transport[2]
            lr_no = transport[3]
            invoice_no = transport[4]
            full_date = transport[5]
            source_city = transport[6]
            destination_city = transport[7]
            no_of_unit = transport[8]
            contract_amount_with_company = round(float(transport[9]), 2)

            HTML += f"""
                            <tr align="center" valign="center">
                                <td>{ind + 1}</td>
                                <td>{date_string}</td>
                                <td>{vehicle_no}</td>
                                <td>{lr_no}</td>
                                <td>{invoice_no}</td>
                                <td>{source_city}</td>
                                <td>{destination_city}</td>
                                <td>{no_of_unit}</td>
                                <td>{ef.formatNumber(contract_amount_with_company)}</td>
                            </tr>
                            
            """
            total_amount += float(contract_amount_with_company)
            total_amount = round(float(total_amount), 2)

        HTML += f"""
        
                        <tr align="center" valign="center">
                            <td colspan="7">{ef.numberToText(total_amount)} ONLY/-</td>
                            <td colspan="2">Rs. {ef.formatNumber(total_amount)}/-</td>
                        </tr>
                        
                        <tr colspan="9">
                            <td colspan="9"></td>
                        </tr>
                        
                        <tr rowspan="6" align="center">
                            <td colspan="9">
                                <table border="0">
                                    <tr>
                                        <td colspan="3" align="left"><b><u>RTGS DETAILS:</u></b></td>
                                    </tr>
                                    <tr>
                                        <td><b>BANK:</b></td>
                                        <td></td>
                                        <td>AXIS BANK LTD.</td>
                                    </tr>
                                    <tr>
                                        <td><b>BRANCH:</b></td>
                                        <td></td>
                                        <td>SERAMPORE</td>
                                    </tr>
                                    <tr>
                                        <td><b>A/C No.:</b></td>
                                        <td></td>
                                        <td>916020035015697</td>
                                    </tr>
                                    <tr>
                                        <td><b>IFSC CODE:</b></td>
                                        <td></td>
                                        <td>UTIB0000443</td>
                                    </tr>
                                    <tr>
                                        <td><b>MICR CODE:</b></td>
                                        <td></td>
                                        <td>700211034</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    
                    </table>
                </body>
            </html>
        """

        insert_query = f"""
            INSERT INTO BILL_SUBMISSIONS(
                   BILL_NUMBER, PAYABLE_AMOUNT, AMOUNT_RECEIVED, DATE_STRING, FULL_DATE,
                   YEAR, MONTH, DAY, BILL_GENERATED_FOR, TRANSPORT_IDS , HTML
                )
                VALUES(
                    '{bill_number}',
                    {total_amount},
                    {0.00},
                    '{today}',
                    {ef.dateToInt(today)},
                    {year},
                    {month},
                    {day},
                    {company_id},
                    '{json.dumps(transport_ids)}',
                    '{HTML}'
                );
        """
        self.cursor.execute(insert_query)
        self.db_con.commit()

        today = dt.now()
        year = today.year
        month = today.month
        day = today.day
        bill_generated_date_string = f"{str(day).zfill(2)}-{ef.monthNoToMonthStr(month)}-{year}"
        bill_generated_full_date = int(f"{year}{str(month).zfill(2)}{str(day).zfill(2)}")

        update_query = f"""
            UPDATE
                TRANSPORTS
            SET
                BILL_GENERATED = 1,
                BILL_GENERATED_DATE_STRING = '{bill_generated_date_string}',
                BILL_GENERATED_FULL_DATE = {bill_generated_full_date},
                BILL_GENERATED_YEAR = {year},
                BILL_GENERATED_MONTH = {month},
                BILL_GENERATED_DAY = {day}
            WHERE
                TRANSPORT_ID IN ({', '.join([str(transport_id) for transport_id in transport_ids])});
        """
        self.cursor.execute(update_query)
        self.db_con.commit()

        self.setDefaultData()
        self.setDefaultDates()

        self.htmlToPDF(HTML, pdf_save_path)
        QMessageBox.information(self, "Done!", "Bill generated successfully!")

    def htmlToPDF(self, html, path):
        doc = QTextDocument()
        doc.setHtml(html)

        if os.path.exists(path):
            os.remove(path)

        printer = QPrinter()
        printer.setOutputFileName(path)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setPageSize(QPrinter.A4)
        printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)

        doc.print_(printer)

    def btnGenerateCompanyBillClicked(self):
        if self.cbCompanies.currentText():
            if not self.leBillNumber.text().strip():
                QMessageBox.critical(self, "No Bill Number!", "Please Provide Bill Number!")
            else:
                filename = QFileDialog.getSaveFileName(self, 'Save File', self.getLastLocation())[0]
                if filename:
                    if not filename.lower().endswith(".pdf"):
                        filename = filename + ".pdf"
                    low_date_range = ef.dateToInt(self.deLowestTransportDateCompanyGenerateBill.text())
                    high_date_range = ef.dateToInt(self.deHighestTransportDateCompanyGenerateBill.text())
                    self.generateHtmlForCompany(self.company_id_dict[self.cbCompanies.currentText()], self.leBillNumber.text().strip(), low_date_range, high_date_range, filename)
                    self.setLastLocation(filename)

    def btnViewVehicleOwnerBillClicked(self):
        if self.cbVehicleOwners.currentText():
            filename = QFileDialog.getSaveFileName(self, 'Save File', self.getLastLocation())[0]
            if filename:
                if not filename.lower().endswith(".pdf"):
                    filename = filename + ".pdf"
                    low_date_range = ef.dateToInt(self.deLowestTransportDateVehicleOwner.text())
                    high_date_range = ef.dateToInt(self.deHighestTransportDateVehicleOwner.text())
                    self.generateHtmlForVehicleOwner(self.vehicle_owner_id_dict.get(self.cbVehicleOwners.currentText(), -1), low_date_range, high_date_range, filename)
                    self.setLastLocation(filename)

    def btnViewCompanyBillClicked(self):
        if self.lwGeneratedCompanyBills.currentItem() is not None:
            filename = QFileDialog.getSaveFileName(self, 'Save File', self.getLastLocation())[0]
            if filename:
                if not filename.lower().endswith(".pdf"):
                    filename = filename + ".pdf"
                    select_query = f"""
                        SELECT
                            HTML
                        FROM
                            BILL_SUBMISSIONS
                        WHERE
                            BILL_SUBMISSION_ID = {self.bill_submission_id_dict[self.lwGeneratedCompanyBills.currentItem().text()]}
                    """
                    self.cursor.execute(select_query)
                    html = self.cursor.fetchall()[0][0]
                    self.htmlToPDF(html, filename)
                    self.setLastLocation(filename)
                    QMessageBox.information(self, "Done!", "Bill regenerated successfully!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BillSubmissionApp()
    window.show()
    sys.exit(app.exec_())
