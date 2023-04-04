from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType

import sys
from datetime import datetime as dt
import sqlite3

from UpdateVehicleOwner import *

AddVehicleOwnerUI, _ = loadUiType("__GUIs/AddVehicleOwner.ui")


class AddVehicleOwnerApp(QMainWindow, AddVehicleOwnerUI):
    def __init__(self, parent=None):
        super(AddVehicleOwnerApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.setAtMiddle()
        self.handleButtons()

        self.shouldOpen = True
        self.childWindow = None

        self.parent = parent
        self.db_con = self.parent.db_con
        self.cursor = self.parent.cursor

    def setAtMiddle(self):
        desktop_resolution = QDesktopWidget().screenGeometry()
        widget_geometry = self.geometry()
        widget_x = (desktop_resolution.width() - widget_geometry.width()) // 2
        widget_y = (desktop_resolution.height() - widget_geometry.height()) // 2
        self.move(widget_x, widget_y)
        self.setFixedSize(widget_geometry.width(), widget_geometry.height())

    def handleButtons(self):
        self.btnViewVehicleOwners.clicked.connect(self.btnViewVehicleOwnersClicked)
        self.btnReset.clicked.connect(self.btnResetClicked)
        self.btnCreateVehicleOwner.clicked.connect(self.btnCreateVehicleOwnerClicked)

    def btnViewVehicleOwnersClicked(self):
        self.childWindow = UpdateVehicleOwnerApp(parent=self.parent)
        if self.childWindow.shouldOpen:
            self.childWindow.show()
    
    def btnResetClicked(self):
        self.leVehicleOwnerName.setText("")
        self.teVehicleOwnerAddress.setText("")
        self.leContactNo.setText("")
        self.teNotes.setText("")

    def btnCreateVehicleOwnerClicked(self):

        vehicle_owner_name = self.leVehicleOwnerName.text()
        if not vehicle_owner_name:
            QMessageBox.critical(self, "No Vehicle Owner Name", "Please insert vehicle owner name!")
        else:
            vehicle_owner_address = self.teVehicleOwnerAddress.toPlainText()
            if not vehicle_owner_address:
                QMessageBox.critical(self, "No Vehicle Owner Address", "Please insert vehicle owner address!")
            else:
                contact_no = self.leContactNo.text()
                if not contact_no:
                    QMessageBox.critical(self, "No Contact Number", "Please insert contact number!")
                elif not set(contact_no).issubset(set("0123456789")):
                    QMessageBox.critical(self, "Invalid Contact Number", "Please insert valid digit!")
                else:
                    contact_no = int(contact_no)

                    insert_query = f"""
                        INSERT INTO VEHICLE_OWNERS(
                                NAME,
                                ADDRESS,
                                CONTACT_NO,
                                NOTES
                            )
                            VALUES(
                                '{vehicle_owner_name}',
                                '{vehicle_owner_address}',
                                {contact_no},
                                '{self.teNotes.toPlainText()}'
                            );
                    """
                    self.cursor.execute(insert_query)
                    self.db_con.commit()

                    QMessageBox.information(self, "Done!", "Vehicle Owner Added Successfully!")
                    self.btnResetClicked()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddVehicleOwnerApp()
    window.show()
    sys.exit(app.exec_())
