import datetime
import os
import uuid
import shutil

from PyQt5 import QtCore, QtWidgets, QtGui

PATH = os.getenv("appdata") + "/EldenRing/"
USER = next(os.walk(PATH), (None, [], None))[1][0]  # Set to the first user
SAVE_PATH = PATH + USER + "/ER0000.sl2"
INFO_PATH = os.getcwd() + "/EldenRingSaves/"
INFO_LIST_PATH = INFO_PATH + "data_list.txt"


class SaveInfo:
    def __init__(self, name, date, uid=""):
        self.name = name
        self.date = date
        if uid:
            self.uid = uid
        else:
            self.uid = str(uuid.uuid4())


info_list = []


def read_info():
    if not os.path.exists(INFO_PATH):
        os.makedirs(INFO_PATH)
    if os.path.exists(INFO_LIST_PATH):
        file = open(INFO_LIST_PATH, "r", encoding="utf8")

        for line in file.readlines():
            line = line[:-1].split("\t")
            info_list.append(SaveInfo(line[0], line[1], line[2]))

        file.close()


def write_info(save_info):
    info_list.append(save_info)
    file = open(INFO_LIST_PATH, "a", encoding="utf8")
    file.write(f"{save_info.name}\t{save_info.date}\t{save_info.uid}\n")
    file.close()


def rewrite_info():
    file = open(INFO_LIST_PATH, "w", encoding="utf8")

    for save_info in info_list:
        file.write(f"{save_info.name}\t{save_info.date}\t{save_info.uid}\n")

    file.close()


def translate(text):
    return QtCore.QCoreApplication.translate("Form", text)


def info_to_str(save_info):
    return save_info.name + "\t (" + save_info.uid + ")"


def str_to_info(str_item):
    uid = str_item.split("(")[-1][:-1]

    for info in info_list:
        if info.uid == uid:
            return info
    raise Exception("sync problem")


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.getcwd())
    return os.path.join(base_path, relative_path)


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.center_window()
        self.selectedInfo = None

        # List the stored info
        for info in info_list:
            self.saveListWidget.addItem(info_to_str(info))

    def setup_ui(self):
        self.setObjectName("Form")
        self.setWindowIcon(QtGui.QIcon(resource_path("icon.ico")))
        self.resize(400, 300)

        # Create widgets
        self.saveNameEdit = QtWidgets.QLineEdit(self)
        self.saveNameEdit.setGeometry(QtCore.QRect(20, 20, 251, 31))
        self.saveNameEdit.setObjectName("saveNameEdit")

        self.createButton = QtWidgets.QPushButton(self)
        self.createButton.setGeometry(QtCore.QRect(290, 20, 91, 31))
        self.createButton.setObjectName("createButton")
        self.createButton.clicked.connect(self.create_save)

        self.saveListWidget = QtWidgets.QListWidget(self)
        self.saveListWidget.setGeometry(QtCore.QRect(20, 70, 361, 171))
        self.saveListWidget.setObjectName("saveListView")
        self.saveListWidget.itemClicked.connect(self.select_save)

        self.dateLabel = QtWidgets.QLabel(self)
        self.dateLabel.setGeometry(QtCore.QRect(20, 250, 241, 31))
        self.dateLabel.setObjectName("dateLabel")

        self.loadButton = QtWidgets.QPushButton(self)
        self.loadButton.setGeometry(QtCore.QRect(190, 250, 91, 31))
        self.loadButton.setObjectName("loadButton")
        self.loadButton.clicked.connect(self.load_save)

        self.removeButton = QtWidgets.QPushButton(self)
        self.removeButton.setGeometry(QtCore.QRect(290, 250, 91, 31))
        self.removeButton.setObjectName("removeButton")
        self.removeButton.clicked.connect(self.remove_save)

        # Retranslate ui
        self.setWindowTitle(translate("Elden Ring Save Manager"))
        self.createButton.setText(translate("Create"))
        self.dateLabel.setText(translate(""))
        self.loadButton.setText(translate("Load"))
        self.removeButton.setText(translate("Remove"))

        QtCore.QMetaObject.connectSlotsByName(self)

    def center_window(self):
        rect = self.frameGeometry()
        rect.moveCenter(QtWidgets.QDesktopWidget().availableGeometry().center())
        self.move(rect.topLeft())

    def create_save(self):
        date = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
        name = self.saveNameEdit.text()
        if not name:
            name = date  # Save as time if no name is given
        else:
            self.saveNameEdit.setText(translate(""))

        info = SaveInfo(name, date)

        shutil.copy2(SAVE_PATH, INFO_PATH + info.uid)
        write_info(info)

        self.saveListWidget.addItem(info_to_str(info))

    def select_save(self):
        self.selectedInfo = str_to_info(self.saveListWidget.currentItem().text())
        self.dateLabel.setText(translate("Created at " + self.selectedInfo.date))

    def load_save(self):
        if self.selectedInfo:
            q = QtWidgets.QMessageBox.question(self,
                                               "Load",
                                               "Do you really want to load the save?\n" +
                                               "\"" + self.selectedInfo.name + "\"",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
            if q == QtWidgets.QMessageBox.Yes:
                shutil.copy2(INFO_PATH + self.selectedInfo.uid, SAVE_PATH)
                QtWidgets.QMessageBox.information(self, "Load", "Success")

    def remove_save(self):
        if self.selectedInfo:
            q = QtWidgets.QMessageBox.warning(self,
                                              "Remove",
                                              "Do you really want to remove the save?\n" +
                                              "\"" + self.selectedInfo.name + "\"",
                                              QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                              QtWidgets.QMessageBox.No)
            if q == QtWidgets.QMessageBox.Yes:
                self.saveListWidget.takeItem(self.saveListWidget.currentRow())
                self.dateLabel.setText(translate(""))

                info_list.remove(self.selectedInfo)
                rewrite_info()
                os.remove(INFO_PATH + self.selectedInfo.uid)

                self.selectedInfo = None


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    read_info()
    window = Window()
    window.show()
    status = app.exec_()
    sys.exit(status)
