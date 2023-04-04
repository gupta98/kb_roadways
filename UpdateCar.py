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

UpdateCarUI, _ = loadUiType("__GUIs/UpdateCar.ui")


class UpdateCarApp(QMainWindow, UpdateCarUI):
    def __init__(self, parent=None):
        super(UpdateCarApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.setAtMiddle()
        self.handleButtons()

        self.shouldOpen = None
        self.vehicle_owner_id_dict = {}
        self.vehicle_owner_id_inverse_dict = {}
        self.vehicle_owner_id_combobox_index = {}
        self.car_id_dict = {}
        self.selected_car = ()

        self.lwCarList.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.parent = parent
        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor

        self.shouldOpenCheck()
        self.makeTheListOfAllCars()

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def handleButtons(self):
        self.lwCarList.doubleClicked.connect(self.viewCarDetails)
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

    def makeTheListOfAllCars(self):
        select_query = """
            SELECT CAR_ID, CAR_NO
            FROM CARS;
        """
        self.cursor.execute(select_query)

        self.car_id_dict.clear()
        cars = self.cursor.fetchall()
        car_counter = 1
        z_fill_length = len(str(len(cars)))

        if cars:
            for car_id, car_number in cars:
                self.car_id_dict[f"{str(car_counter).zfill(z_fill_length)} - {car_number}"] = car_id
                self.lwCarList.addItem(f"{str(car_counter).zfill(z_fill_length)} - {car_number}")
                car_counter += 1

    def viewCarDetails(self):
        car_id = self.car_id_dict[self.lwCarList.selectedItems()[0].text()]
        select_query = f"""
            SELECT
                *
            FROM
                CARS
            WHERE
                CAR_ID = {car_id}
        """
        self.cursor.execute(select_query)

        self.selected_car = self.cursor.fetchall()[0]

        self.leCarNumber.setText("")
        self.teNotes.setText("")
        self.cbVehicleOwners.clear()

        self.leCarNumber.setText(f"{self.selected_car[1]}")
        self.teNotes.setText(f"{self.selected_car[3]}")

        for key in self.vehicle_owner_id_combobox_index:
            self.cbVehicleOwners.addItem(key)
        vehicle_owner_id = int(self.selected_car[2])
        vehicle_owner_combobox_text = self.vehicle_owner_id_inverse_dict[vehicle_owner_id]
        combobox_index = self.vehicle_owner_id_combobox_index[vehicle_owner_combobox_text]
        self.cbVehicleOwners.setCurrentIndex(combobox_index)


    def btnDownloadSelectedPressed(self):
        car_ids = [f"{self.car_id_dict[car.text()]}" for car in self.lwCarList.selectedItems()]
        if not car_ids:
            QMessageBox.critical(self, "No Car Selected!", "Please select at least one car!")
        else:
            columns = ["CAR_ID", "CAR_NO", "VEHICLE_OWNER_NAME", "NOTES"]
            df = pd.DataFrame(columns=columns)

            select_query = f"""
                SELECT
                    CARS.CAR_ID, CARS.CAR_NO, VEHICLE_OWNERS.NAME, CARS.NOTES
                FROM
                    CARS, VEHICLE_OWNERS
                WHERE
                    CAR_ID IN ({','.join(car_ids)})
                    AND
                    CARS.VEHICLE_OWNER_ID = VEHICLE_OWNERS.VEHICLE_OWNER_ID
                ORDER BY
                    CAR_ID;
            """
            self.cursor.execute(select_query)

            for car in self.cursor.fetchall():
                df = df.append({
                    "CAR_ID" : car[0],
                    "CAR_NO" : car[1],
                    "VEHICLE_OWNER_NAME" : car[2],
                    "NOTES" : car[3]
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
                CARS.CAR_ID, CARS.CAR_NO, VEHICLE_OWNERS.NAME, CARS.NOTES
                FROM
                    CARS, VEHICLE_OWNERS
            WHERE
                CARS.VEHICLE_OWNER_ID = VEHICLE_OWNERS.VEHICLE_OWNER_ID
            ORDER BY
                CAR_ID;
        """
        self.cursor.execute(select_query)
        cars = self.cursor.fetchall()

        if not cars:
            QMessageBox.critical(self, "No Car Exist!", "There is no car in database!")
        else:
            columns = ["CAR_ID", "CAR_NO", "VEHICLE_OWNER_NAME", "NOTES"]
            df = pd.DataFrame(columns=columns)
            for car in cars:
                df = df.append({
                    "CAR_ID" : car[0],
                    "CAR_NO" : car[1],
                    "VEHICLE_OWNER_NAME" : car[2],
                    "NOTES" : car[3]
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
        if not self.selected_car:
            QMessageBox.critical(self, "No Car Selected!", "Please select a car to update!")
        else:
            car_number = self.leCarNumber.text()
            if not car_number:
                QMessageBox.critical(self, "No Car Number", "Please insert car number!")
            else:
                vehicle_owner_id = self.vehicle_owner_id_dict[self.cbVehicleOwners.currentText()]

                answer = QMessageBox.question(self, "Update?", f"This will update {self.selected_car[1]}. Continue?", QMessageBox.Yes | QMessageBox.No)
                if answer == QMessageBox.Yes:

                    update_query = f"""
                        UPDATE
                            CARS
                        SET
                            CAR_NO = '{car_number}',
                            VEHICLE_OWNER_ID = {vehicle_owner_id},
                            NOTES = '{self.teNotes.toPlainText()}'
                        WHERE
                            CAR_ID = {self.selected_car[0]};
                    """
                    self.cursor.execute(update_query)
                    self.db_con.commit()

                    QMessageBox.information(self, "Done!", "Car Updated Successfully!")

    def btnDeletePressed(self):
        car_ids = [f"{self.car_id_dict[car.text()]}" for car in self.lwCarList.selectedItems()]
        if not car_ids:
            QMessageBox.critical(self, "No Car Selected!", "Please select at lease one car to delete!")
        else:
            answer = QMessageBox.question(self, "Delete?", "This will delete the cars permanently. Continue?", QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:

                delete_query = f"""
                    DELETE
                    FROM
                        CARS
                    WHERE
                        CAR_ID IN ({', '.join(car_ids)});
                """
                self.cursor.execute(delete_query)
                self.db_con.commit()

                self.car_id_dict.clear()
                self.selected_car = ()

                self.lwCarList.clear()
                self.cbVehicleOwners.clear()
                self.leCarNumber.setText("")
                self.teNotes.setText("")

                self.makeTheListOfAllCars()

                QMessageBox.information(self, "Done!", "Car Deleted Successfully!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UpdateCarApp()
    window.show()
    sys.exit(app.exec_())
