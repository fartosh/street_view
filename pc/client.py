import os
import sys
import socket
import threading
import numpy as np
from PIL import Image
from PyQt4 import uic, QtCore
from PyQt4.QtGui import *


class MainWindow(QMainWindow):
    # IP = '192.168.137.13'
    IP = '192.168.137.87'
    PORT = '51716'

    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi('gui.ui', self)
        self.con = Connection()
        self.con.display.connect(self.show_image)
        self.con.refresh("background.png")
        self.ipLine.setText(MainWindow.IP)
        self.portLine.setText(MainWindow.PORT)

        self.connectButton.clicked.connect(self.connection)
        self.pictureButton.clicked.connect(self.picture)
        self.palette_red = QPalette()
        self.palette_red.setColor(QPalette.Foreground, QtCore.Qt.red)
        self.palette_black = QPalette()
        self.palette_black.setColor(QPalette.Foreground, QtCore.Qt.black)

    def keyPressEvent(self, event):
        key = event.key()

        if event.isAutoRepeat():
            return

        if key == QtCore.Qt.Key_W:
            self.forwardLabel.setPalette(self.palette_red)
        if key == QtCore.Qt.Key_S:
            self.backwardLabel.setPalette(self.palette_red)
        if key == QtCore.Qt.Key_A:
            self.leftLabel.setPalette(self.palette_red)
        if key == QtCore.Qt.Key_D:
            self.rightLabel.setPalette(self.palette_red)

    def keyReleaseEvent(self, event):
        key = event.key()

        if event.isAutoRepeat():
            return

        if key == QtCore.Qt.Key_W:
            self.forwardLabel.setPalette(self.palette_black)
            self.con.send("w")
        if key == QtCore.Qt.Key_S:
            self.backwardLabel.setPalette(self.palette_black)
            self.con.send("s")
        if key == QtCore.Qt.Key_A:
            self.leftLabel.setPalette(self.palette_black)
            self.con.send("a")
        if key == QtCore.Qt.Key_D:
            self.rightLabel.setPalette(self.palette_black)
            self.con.send("d")

    def connection(self):
        self.con.connectt(self.ipLine.text(), int(self.portLine.text()))

    def picture(self):
        self.con.send("p")

    @QtCore.pyqtSlot(str)
    def show_image(self, url):
        self.pictureView.setPixmap(QPixmap(url))


class Connection(QtCore.QObject):
    display = QtCore.pyqtSignal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bufor = ""
        self.ack = False
        self.done = False

    def refresh(self, url):
        self.display.emit(url)

    def connectt(self, ip, port):
        print "connecting with (", ip, ",", port, ")"
        self.socket.connect((ip, port))
        print "connected"
        threading.Thread(target=self.receive).start()

    def receive(self):
        while True:
            data = self.socket.recv(200000)
            if data == "ack":
                self.ack = True
                print data
                continue

            if data == "done":
                print data
                self.done = True
                continue

            if data == "error":
                print "ERROR"
                continue

            if data.endswith("end"):
                self.bufor += data
                self.bufor = self.bufor[:-3]
                self.save(self.bufor, "images/img"+str(len(os.listdir("images/")))+".jpg")
                self.bufor = ""
                continue
            else:
                self.bufor += data
                continue

    def send(self, order):
        if self.done is False or self.ack is False:
            print "no ack or no done"
            return
        self.done = False
        self.ack = False
        self.socket.sendall(order)
        print "sending:", order

    def save(self, data, url):
        print "saving to:", url
        image = open(url, 'wb')
        image.write(data)
        image.close()
        print "image saved"
        self.refresh(url)
        return


if __name__ == '__main__':
    qApp = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()

    sys.exit(qApp.exec_())
