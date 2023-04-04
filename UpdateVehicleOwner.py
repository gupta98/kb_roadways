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

UpdateVehicleOwnerUI, _ = loadUiType("__GUIs/UpdateVehicleOwner.ui")


class UpdateVehicleOwnerApp(QMainWindow, UpdateVehicleOwnerUI):
    def __init__(self, parent=None):
        super(UpdateVehicleOwnerApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.setAtMiddle()
        self.handleButtons()

        self.shouldOpen = True
        self.vehicle_owner_id_dict = {}
        self.selected_vehicle_owner = ()

        self.lwVehicleOwnerList.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.parent = parent
        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor

        self.makeTheListOfAllVehicleOwners()

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def handleButtons(self):
        self.lwVehicleOwnerList.doubleClicked.connect(self.viewVehicleOwnerDetails)
        self.btnDownloadSelected.clicked.connect(self.btnDownloadSelectedPressed)
        self.btnDownloadAll.clicked.connect(self.btnDownloadAllPressed)
        self.btnUpdate.clicked.connect(self.btnUpdatePressed)
        self.btnDelete.clicked.connect(self.btnDeletePressed)

    def makeTheListOfAllVehicleOwners(self):
        select_query = """
            SELECT VEHICLE_OWNER_ID, NAME
            FROM VEHICLE_OWNERS;
        """
        self.cursor.execute(select_query)

        self.vehicle_owner_id_dict.clear()
        self.lwVehicleOwnerList.clear()
        vehicle_owners = self.cursor.fetchall()
        vehicle_owner_counter = 1
        z_fill_length = len(str(len(vehicle_owners)))

        if vehicle_owners:
            for vehicle_owner_id, vehicle_owner_name in vehicle_owners:
                self.vehicle_owner_id_dict[f"{str(vehicle_owner_counter).zfill(z_fill_length)} - {vehicle_owner_name}"] = vehicle_owner_id
                self.lwVehicleOwnerList.addItem(f"{str(vehicle_owner_counter).zfill(z_fill_length)} - {vehicle_owner_name}")
                vehicle_owner_counter += 1

    def viewVehicleOwnerDetails(self):
        vehicle_owner_id = self.vehicle_owner_id_dict[self.lwVehicleOwnerList.selectedItems()[0].text()]
        select_query = f"""
            SELECT
                *
            FROM
                VEHICLE_OWNERS
            WHERE
                VEHICLE_OWNER_ID = {vehicle_owner_id}
        """
        self.cursor.execute(select_query)

        self.selected_vehicle_owner = details = self.cursor.fetchall()[0]
        print(self.selected_vehicle_owner)

        self.leVehicleOwnerName.setText("")
        self.teVehicleOwnerAddress.setText("")
        self.leContactNo.setText("")
        self.teNotes.setText("")

        self.leVehicleOwnerName.setText(f"{details[1]}")
        self.teVehicleOwnerAddress.setText(f"{details[2]}")
        self.leContactNo.setText(f"{details[3]}")
        self.teNotes.setText(f"{details[4]}")

    def btnDownloadSelectedPressed(self):
        vehicle_owner_ids = [f"{self.vehicle_owner_id_dict[vehicle_owner.text()]}" for vehicle_owner in self.lwVehicleOwnerList.selectedItems()]
        if not vehicle_owner_ids:
            QMessageBox.critical(self, "No Vehicle Owner Selected!", "Please select at least one vehicle owner!")
        else:
            columns = ["VEHICLE_OWNER_ID", "NAME", "ADDRESS", "CONTACT_NO", "NOTES"]
            df = pd.DataFrame(columns=columns)

            select_query = f"""
                SELECT
                    *
                FROM
                    VEHICLE_OWNERS
                WHERE
                    VEHICLE_OWNER_ID IN ({','.join(vehicle_owner_ids)})
                ORDER BY
                    VEHICLE_OWNER_ID;
            """
            self.cursor.execute(select_query)

            for vehicle_owner in self.cursor.fetchall():
                df = df.append({
                    "VEHICLE_OWNER_ID" : vehicle_owner[0],
                    "NAME" : vehicle_owner[1],
                    "ADDRESS" : vehicle_owner[2],
                    "CONTACT_NO" : vehicle_owner[3],
                    "NOTES" : vehicle_owner[4]
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
                *
            FROM
                VEHICLE_OWNERS
            ORDER BY
                VEHICLE_OWNER_ID;
        """
        self.cursor.execute(select_query)
        vehicle_owners = self.cursor.fetchall()

        if not vehicle_owners:
            QMessageBox.critical(self, "No Vehicle Owner Exist!", "There is no vehicle owner in database!")
        else:
            columns = ["VEHICLE_OWNER_ID", "NAME", "ADDRESS", "CONTACT_NO", "NOTES"]
            df = pd.DataFrame(columns=columns)
            for vehicle_owner in vehicle_owners:
                df = df.append({
                    "VEHICLE_OWNER_ID": vehicle_owner[0],
                    "NAME": vehicle_owner[1],
                    "ADDRESS": vehicle_owner[2],
                    "CONTACT_NO": vehicle_owner[3],
                    "NOTES": vehicle_owner[4]
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
        if not self.selected_vehicle_owner:
            QMessageBox.critical(self, "No Vehicle Owner Selected!", "Please select a vehicle owner to update!")
        else:
            vehicle_owner_name = self.leVehicleOwnerName.text()
            if not vehicle_owner_name:
                QMessageBox.critical(self, "No Vehicle Owner Name", "Please insert vehicle owner's name!")
            else:
                vehicle_owner_address = self.teVehicleOwnerAddress.toPlainText()
                if not vehicle_owner_address:
                    QMessageBox.critical(self, "No Vehicle Owner Address", "Please insert vehicle owner's address!")
                else:
                    contact_no = self.leContactNo.text()
                    if not contact_no:
                        QMessageBox.critical(self, "No Contact Number", "Please insert contact number!")
                    elif not set(contact_no).issubset(set("0123456789")):
                        QMessageBox.critical(self, "Invalid Contact Number", "Please insert valid digit!")
                    else:
                        contact_no = int(contact_no)

                        answer = QMessageBox.question(self, "Update?", f"This will update {self.selected_vehicle_owner[1]}. Continue?", QMessageBox.Yes | QMessageBox.No)
                        if answer == QMessageBox.Yes:

                            update_query = f"""
                                UPDATE
                                    VEHICLE_OWNERS
                                SET
                                    NAME = '{vehicle_owner_name}',
                                    ADDRESS = '{vehicle_owner_address}',
                                    CONTACT_NO = {contact_no},
                                    NOTES = '{self.teNotes.toPlainText()}'
                                WHERE
                                    VEHICLE_OWNER_ID = {self.selected_vehicle_owner[0]};
                            """
                            self.cursor.execute(update_query)
                            self.db_con.commit()
                            self.makeTheListOfAllVehicleOwners()

                            QMessageBox.information(self, "Done!", "Vehicle Owner Updated Successfully!")

    def btnDeletePressed(self):
        vehicle_owner_ids = [f"{self.vehicle_owner_id_dict[vehicle_owner.text()]}" for vehicle_owner in self.lwVehicleOwnerList.selectedItems()]
        if not vehicle_owner_ids:
            QMessageBox.critical(self, "No Vehicle Owner Selected!", "Please select at lease one vehicle owner to delete!")
        else:

            answer = QMessageBox.question(self, "Delete?", "This will delete the vehicle owners permanently. Continue?", QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:

                delete_query = f"""
                    DELETE
                    FROM
                        VEHICLE_OWNERS
                    WHERE
                        VEHICLE_OWNER_ID IN ({','.join(vehicle_owner_ids)});
                """
                self.cursor.execute(delete_query)
                self.db_con.commit()

                self.vehicle_owner_id_dict.clear()
                self.selected_vehicle_owner = ()

                self.lwVehicleOwnerList.clear()
                self.leVehicleOwnerName.setText("")
                self.teVehicleOwnerAddress.setText("")
                self.leContactNo.setText("")
                self.teNotes.setText("")

                self.makeTheListOfAllVehicleOwners()

                QMessageBox.information(self, "Done!", "Vehicle Owners Deleted Successfully!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UpdateVehicleOwnerApp()
    window.show()
    sys.exit(app.exec_())
