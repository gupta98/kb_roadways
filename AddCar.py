from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType

import sys
from datetime import datetime as dt
import sqlite3

from UpdateCar import *

AddCarUI, _ = loadUiType("__GUIs/AddCar.ui")


class AddCarApp(QMainWindow, AddCarUI):
    def __init__(self, parent=None):
        super(AddCarApp, self).__init__(parent)
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
        self.btnViewCars.clicked.connect(self.btnViewCarsClicked)
        self.btnReset.clicked.connect(self.btnResetClicked)
        self.btnCreateCar.clicked.connect(self.btnCreateCarClicked)

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

    def btnViewCarsClicked(self):
        self.childWindow = UpdateCarApp(parent=self)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
        else:
            QMessageBox.critical(self, "No Vehicle Owner Found!", "Please insert one vehicle owner before updating driver.")
    
    def btnResetClicked(self):
        self.leCarNumber.setText("")
        self.cbVehicleOwners.setCurrentIndex(0)
        self.teNotes.setText("")

    def btnCreateCarClicked(self):
        car_number = self.leCarNumber.text()
        if not car_number:
            QMessageBox.critical(self, "No Car Number", "Please insert car number!")
        else:
            insert_query = f"""
                INSERT INTO CARS(
                        CAR_NO,
                        VEHICLE_OWNER_ID,
                        NOTES
                    )
                    VALUES(
                        '{car_number}',
                        {self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]},
                        '{self.teNotes.toPlainText()}'
                    );
            """
            self.cursor.execute(insert_query)
            self.db_con.commit()

            QMessageBox.information(self, "Done!", "Car Added Successfully!")
            self.btnResetClicked()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddCarApp()
    window.show()
    sys.exit(app.exec_())
