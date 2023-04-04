from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType

import sys
from datetime import datetime as dt
import sqlite3

from UpdateDriver import *

AddDriverUI, _ = loadUiType("__GUIs/AddDriver.ui")


class AddDriverApp(QMainWindow, AddDriverUI):
    def __init__(self, parent=None):
        super(AddDriverApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.setAtMiddle()
        self.handleButtons()

        self.parent = parent
        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor

        self.shouldOpen = None
        self.childWindow = None
        self.vehicle_owner_id_dict = {}

        self.shouldOpenCheck()

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def handleButtons(self):
        self.btnViewDrivers.clicked.connect(self.btnViewDriversClicked)
        self.btnReset.clicked.connect(self.btnResetClicked)
        self.btnCreateDriver.clicked.connect(self.btnCreateDriverClicked)

    def shouldOpenCheck(self):
        select_query = """
            SELECT
                *
            FROM
                VEHICLE_OWNERS;
        """
        self.cursor.execute(select_query)
        vehicle_owners = self.cursor.fetchall()

        if vehicle_owners:
            for row in vehicle_owners:
                vehicle_owner_id = row[0]
                vehicle_owner_name = row[1]
                combo_key = f"{vehicle_owner_id} - {vehicle_owner_name}"
                self.vehicle_owner_id_dict[combo_key] = vehicle_owner_id
                self.cbVehicleOwners.addItem(combo_key)
            self.shouldOpen = True
        else:
            self.shouldOpen = False

    def btnViewDriversClicked(self):
        self.childWindow = UpdateDriverApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
        else:
            QMessageBox.critical(self, "No Vehicle Owner Found!", "Please insert one vehicle owner before updating driver.")
    
    def btnResetClicked(self):
        self.leDriverName.setText("")
        self.teDriverAddress.setText("")
        self.cbVehicleOwners.setCurrentIndex(0)
        self.leContactNo.setText("")
        self.teNotes.setText("")

    def btnCreateDriverClicked(self):

        driver_name = self.leDriverName.text()
        if not driver_name:
            QMessageBox.critical(self, "No Driver Name", "Please insert driver name!")
        else:
            driver_address = self.teDriverAddress.toPlainText()
            if not driver_address:
                QMessageBox.critical(self, "No Driver Address", "Please insert driver address!")
            else:
                contact_no = self.leContactNo.text()
                if not contact_no:
                    QMessageBox.critical(self, "No Contact Number", "Please insert contact number!")
                elif not set(contact_no).issubset(set("0123456789")):
                    QMessageBox.critical(self, "Invalid Contact Number", "Please insert valid digit!")
                else:
                    contact_no = int(contact_no)

                    insert_query = f"""
                        INSERT INTO DRIVERS(
                                NAME,
                                ADDRESS,
                                CONTACT_NO,
                                VEHICLE_OWNER_ID,
                                NOTES
                            )
                            VALUES(
                                '{driver_name}',
                                '{driver_address}',
                                {contact_no},
                                {self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]},
                                '{self.teNotes.toPlainText()}'
                            );
                    """
                    self.cursor.execute(insert_query)
                    self.db_con.commit()

                    QMessageBox.information(self, "Done!", "Driver Added Successfully!")
                    self.btnResetClicked()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddDriverApp()
    window.show()
    sys.exit(app.exec_())
