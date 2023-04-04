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

UpdateDriverUI, _ = loadUiType("__GUIs/UpdateDriver.ui")


class UpdateDriverApp(QMainWindow, UpdateDriverUI):
    def __init__(self, parent=None):
        super(UpdateDriverApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.setAtMiddle()
        self.handleButtons()

        self.shouldOpen = None
        self.vehicle_owner_id_dict = {}
        self.vehicle_owner_id_inverse_dict = {}
        self.vehicle_owner_id_combobox_index = {}
        self.driver_id_dict = {}
        self.selected_driver = ()

        self.lwDriverList.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.parent = parent
        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor

        self.shouldOpenCheck()
        self.makeTheListOfAllDrivers()

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def handleButtons(self):
        self.lwDriverList.doubleClicked.connect(self.viewDriverDetails)
        self.btnDownloadSelected.clicked.connect(self.btnDownloadSelectedPressed)
        self.btnDownloadAll.clicked.connect(self.btnDownloadAllPressed)
        self.btnUpdate.clicked.connect(self.btnUpdatePressed)
        self.btnDelete.clicked.connect(self.btnDeletePressed)

    def shouldOpenCheck(self):
        select_query = """
            SELECT
                *
            FROM
                VEHICLE_OWNERS;
        """
        self.cursor.execute(select_query)
        vehicle_owners = self.cursor.fetchall()

        vehicle_owner_counter_for_combobox_index = 0
        if vehicle_owners:
            for row in vehicle_owners:
                vehicle_owner_id = row[0]
                vehicle_owner_name = row[1]
                combo_key = f"{vehicle_owner_id} - {vehicle_owner_name}"
                self.vehicle_owner_id_dict[combo_key] = vehicle_owner_id
                self.vehicle_owner_id_inverse_dict[vehicle_owner_id] = combo_key
                self.vehicle_owner_id_combobox_index[combo_key] = vehicle_owner_counter_for_combobox_index
                # self.cbVehicleOwners.addItem(combo_key)
                vehicle_owner_counter_for_combobox_index += 1
            self.shouldOpen = True
        else:
            self.shouldOpen = False

    def makeTheListOfAllDrivers(self):
        select_query = """
            SELECT DRIVER_ID, NAME
            FROM DRIVERS;
        """
        self.cursor.execute(select_query)

        self.driver_id_dict.clear()
        self.lwDriverList.clear()
        drivers = self.cursor.fetchall()
        driver_counter = 1
        z_fill_length = len(str(len(drivers)))

        if drivers:
            for driver_id, driver_name in drivers:
                self.driver_id_dict[f"{str(driver_counter).zfill(z_fill_length)} - {driver_name}"] = driver_id
                self.lwDriverList.addItem(f"{str(driver_counter).zfill(z_fill_length)} - {driver_name}")
                driver_counter += 1

    def viewDriverDetails(self):
        driver_id = self.driver_id_dict[self.lwDriverList.selectedItems()[0].text()]
        select_query = f"""
            SELECT
                *
            FROM
                DRIVERS
            WHERE
                DRIVER_ID = {driver_id}
        """
        self.cursor.execute(select_query)

        self.selected_driver = self.cursor.fetchall()[0]

        self.leDriverName.setText("")
        self.teDriverAddress.setText("")
        self.leContactNo.setText("")
        self.teNotes.setText("")
        self.cbVehicleOwners.clear()

        self.leDriverName.setText(f"{self.selected_driver[1]}")
        self.teDriverAddress.setText(f"{self.selected_driver[2]}")
        self.leContactNo.setText(f"{self.selected_driver[3]}")
        self.teNotes.setText(f"{self.selected_driver[5]}")

        for key in self.vehicle_owner_id_combobox_index:
            self.cbVehicleOwners.addItem(key)
        vehicle_owner_id = int(self.selected_driver[4])
        vehicle_owner_combobox_text = self.vehicle_owner_id_inverse_dict[vehicle_owner_id]
        combobox_index = self.vehicle_owner_id_combobox_index[vehicle_owner_combobox_text]
        self.cbVehicleOwners.setCurrentIndex(combobox_index)


    def btnDownloadSelectedPressed(self):
        driver_ids = [f"{self.driver_id_dict[driver.text()]}" for driver in self.lwDriverList.selectedItems()]
        if not driver_ids:
            QMessageBox.critical(self, "No Driver Selected!", "Please select at least one driver!")
        else:
            columns = ["DRIVER_ID", "NAME", "ADDRESS", "CONTACT_NO", "VEHICLE_OWNER_NAME", "NOTES"]
            df = pd.DataFrame(columns=columns)

            select_query = f"""
                SELECT
                    DRIVERS.*, VEHICLE_OWNERS.NAME
                FROM
                    DRIVERS, VEHICLE_OWNERS
                WHERE
                    DRIVER_ID IN ({','.join(driver_ids)})
                    AND
                    DRIVERS.VEHICLE_OWNER_ID = VEHICLE_OWNERS.VEHICLE_OWNER_ID
                ORDER BY
                    DRIVER_ID;
            """
            self.cursor.execute(select_query)

            for driver in self.cursor.fetchall():
                df = df.append({
                    "DRIVER_ID" : driver[0],
                    "NAME" : driver[1],
                    "ADDRESS" : driver[2],
                    "CONTACT_NO" : driver[3],
                    "NOTES" : driver[4],
                    "VEHICLE_OWNER_NAME": driver[5]
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

    def btnDownloadAllPressed(self):
        select_query = f"""
            SELECT
                DRIVERS.*, VEHICLE_OWNERS.NAME
            FROM
                DRIVERS, VEHICLE_OWNERS
            WHERE
                DRIVERS.VEHICLE_OWNER_ID = VEHICLE_OWNERS.VEHICLE_OWNER_ID
            ORDER BY
                DRIVER_ID;
        """
        self.cursor.execute(select_query)
        drivers = self.cursor.fetchall()

        if not drivers:
            QMessageBox.critical(self, "No Driver Exist!", "There is no driver in database!")
        else:
            columns = ["DRIVER_ID", "NAME", "ADDRESS", "CONTACT_NO", "VEHICLE_OWNER_NAME", "NOTES"]
            df = pd.DataFrame(columns=columns)
            for driver in drivers:
                df = df.append({
                    "DRIVER_ID" : driver[0],
                    "NAME" : driver[1],
                    "ADDRESS" : driver[2],
                    "CONTACT_NO" : driver[3],
                    "NOTES" : driver[4],
                    "VEHICLE_OWNER_NAME": driver[5]
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
        if not self.selected_driver:
            QMessageBox.critical(self, "No Driver Selected!", "Please select a driver to update!")
        else:
            driver_name = self.leDriverName.text()
            if not driver_name:
                QMessageBox.critical(self, "No Driver Name", "Please insert driver's name!")
            else:
                driver_address = self.teDriverAddress.toPlainText()
                if not driver_address:
                    QMessageBox.critical(self, "No Driver Address", "Please insert driver's address!")
                else:
                    contact_no = self.leContactNo.text()
                    if not contact_no:
                        QMessageBox.critical(self, "No Contact Number", "Please insert contact number!")
                    elif not set(contact_no).issubset(set("0123456789")):
                        QMessageBox.critical(self, "Invalid Contact Number", "Please insert valid digit!")
                    else:
                        contact_no = int(contact_no)
                        vehicle_owner_id = self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]

                        answer = QMessageBox.question(self, "Update?", f"This will update {self.selected_driver[1]}. Continue?", QMessageBox.Yes | QMessageBox.No)
                        if answer == QMessageBox.Yes:

                            update_query = f"""
                                UPDATE
                                    DRIVERS
                                SET
                                    NAME = '{driver_name}',
                                    ADDRESS = '{driver_address}',
                                    CONTACT_NO = {contact_no},
                                    VEHICLE_OWNER_ID = {vehicle_owner_id},
                                    NOTES = '{self.teNotes.toPlainText()}'
                                WHERE
                                    DRIVER_ID = {self.selected_driver[0]};
                            """
                            self.cursor.execute(update_query)
                            self.db_con.commit()
                            self.makeTheListOfAllDrivers()

                            QMessageBox.information(self, "Done!", "Driver Updated Successfully!")

    def btnDeletePressed(self):
        driver_ids = [f"{self.driver_id_dict[driver.text()]}" for driver in self.lwDriverList.selectedItems()]
        if not driver_ids:
            QMessageBox.critical(self, "No Driver Selected!", "Please select at lease one driver to delete!")
        else:

            answer = QMessageBox.question(self, "Delete?", "This will delete the drivers permanently. Continue?", QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:

                delete_query = f"""
                    DELETE
                    FROM
                        DRIVERS
                    WHERE
                        DRIVER_ID IN ({','.join(driver_ids)});
                """
                self.cursor.execute(delete_query)
                self.db_con.commit()

                self.driver_id_dict.clear()
                self.selected_driver = ()

                self.lwDriverList.clear()
                self.cbVehicleOwners.clear()
                self.leDriverName.setText("")
                self.teDriverAddress.setText("")
                self.leContactNo.setText("")
                self.teNotes.setText("")

                self.makeTheListOfAllDrivers()

                QMessageBox.information(self, "Done!", "Driver Deleted Successfully!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UpdateDriverApp()
    window.show()
    sys.exit(app.exec_())
