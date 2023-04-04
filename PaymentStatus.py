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


PaymentStatusUI, _ = loadUiType("__GUIs/PaymentStatus.ui")


class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        QMessageBox.information(None, "Read Only Area!", "You can only modify RECEIVED AMOUNT column.")


class PaymentStatusUIApp(QMainWindow, PaymentStatusUI):
    def __init__(self, parent=None):
        super(PaymentStatusUIApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.parent = parent
        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor
        self.shouldOpen = True

        delegate = ReadOnlyDelegate(self)
        self.twPaymentDetails.setItemDelegateForColumn(0, delegate)
        self.twPaymentDetails.setItemDelegateForColumn(1, delegate)
        self.twPaymentDetails.setItemDelegateForColumn(2, delegate)
        self.twPaymentDetails.setItemDelegateForColumn(3, delegate)
        self.twPaymentDetails.setItemDelegateForColumn(4, delegate)

        self.setAtMiddle()
        self.handleButtons()
        self.setDefaultData()

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def setDefaultData(self):
        select_query = """
            SELECT
                BILL_SUBMISSIONS.BILL_SUBMISSION_ID, BILL_SUBMISSIONS.BILL_NUMBER, 
                BILL_SUBMISSIONS.DATE_STRING, BILL_SUBMISSIONS.PAYABLE_AMOUNT, 
                BILL_SUBMISSIONS.AMOUNT_RECEIVED, BILL_SUBMISSIONS.FULL_DATE,
                COMPANIES.NAME
            FROM
                BILL_SUBMISSIONS, COMPANIES
            WHERE
                COMPANIES.COMPANY_ID = BILL_SUBMISSIONS.BILL_GENERATED_FOR;
        """
        self.cursor.execute(select_query)
        bills = self.cursor.fetchall()
        bills.sort(key=lambda x: (x[5], x[0]))

        self.twPaymentDetails.setRowCount(0)
        self.twPaymentDetails.setRowCount(len(bills))

        for ind, bill in enumerate(bills):
            bill_submission_id = int(bill[0])
            bill_no = bill[1]
            date_string = bill[2]
            payable_amount = round(float(bill[3]), 2)
            amount_received = round(float(bill[4]), 2)
            company_name = bill[6]

            self.twPaymentDetails.setItem(ind, 0, QTableWidgetItem(str(bill_submission_id)))
            self.twPaymentDetails.setItem(ind, 1, QTableWidgetItem(bill_no))
            self.twPaymentDetails.setItem(ind, 2, QTableWidgetItem(company_name))
            self.twPaymentDetails.setItem(ind, 3, QTableWidgetItem(date_string))
            self.twPaymentDetails.setItem(ind, 4, QTableWidgetItem(str(payable_amount)))
            self.twPaymentDetails.setItem(ind, 5, QTableWidgetItem(str(amount_received)))

    def handleButtons(self):
        self.btnUpdatePaymentStatus.clicked.connect(self.btnUpdatePaymentStatusPressed)

    def allAmountsAreValid(self):
        for row in range(self.twPaymentDetails.rowCount()):
            amount = self.twPaymentDetails.item(row, 5).text()
            try:
                float(amount)
            except Exception:
                return row, False
        return -1, True

    def btnUpdatePaymentStatusPressed(self):
        row, status = self.allAmountsAreValid()
        if not status:
            QMessageBox.critical(self, "Invalid Amount!", f"Row {row + 1} has invalid amount!")
        else:
            for row in range(self.twPaymentDetails.rowCount()):
                bill_submission_id = int(self.twPaymentDetails.item(row, 0).text())
                amount = round(float(self.twPaymentDetails.item(row, 5).text()), 2)

                update_query = f"""
                    UPDATE
                        BILL_SUBMISSIONS
                    SET
                        AMOUNT_RECEIVED = {amount}
                    WHERE
                        BILL_SUBMISSION_ID = {bill_submission_id};
                """
                self.cursor.execute(update_query)
                self.db_con.commit()

            QMessageBox.information(self, "Done!", "All Payment Details Are Updated Successfully!")





if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PaymentStatusUIApp()
    window.show()
    sys.exit(app.exec_())
