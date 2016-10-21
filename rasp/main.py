#-*- coding: utf-8 -*-
from picamera import PiCamera
from time import sleep
from serial import Serial
import os, os.path
import threading
import socket

class Camera:
    url = 'images/'
    sleep_time = 3
    
    def __init__(self, rotation):
        self.cam = PiCamera()
        self.cam.rotation = rotation
        
    def image_capture(self, amount):
        self.cam.start_preview()

        for i in range(amount):
            self.image_save()

        self.cam.stop_preview()
        
    def image_save(self):
        sleep(self.sleep_time)
        self.cam.capture(self.url+'image%s.jpg' %len(os.listdir(self.url)))

    def close(self):
        self.cam.close()


class SocketConnection:
    #host = '169.254.164.187'
    host = '192.168.137.87'
    port = 51716

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    def start(self):
        self.socket.listen(5)
        self.client, self.address = self.socket.accept()
        print "Connected with: ", self.address
        self.client.sendall("ack")
        self.client.sendall("done")
        threading.Thread(target=self.receive).start()

    def receive(self):
        while True:
            if self.decode(self.client.recv(512)):
                self.client.sendall("done")
            else:
                self.client.sendall("error")
            
    def decode(self, order):
        self.client.sendall("ack")
        if order == "p":
            Main.camera.image_capture(1)
            self.send_image(Camera.url+'image%s.jpg' %(len(os.listdir(Camera.url))-1))
            return True
        else:
            return Main.uart.send(order)

    def send_image(self, url):
        img = open(url, 'rb')
        data = img.read()
        img.close()
        print "sending", url
        self.client.sendall(data)
        self.client.send("end")
        sleep(1)
        print "sent"
        

class UartConnection:
    def __init__(self):
        self.serial_port = Serial('/dev/ttyAMA0',9600,timeout=1)
        self.serial_port.flushInput()
        if not self.serial_port.isOpen():
            self.serial_port.open()
        threading.Thread(target=self.receive).start()

    def receive(self):
        while True:
            self.data = self.serial_port.read(self.serial_port.inWaiting())
            if len(self.data) > 0:
                print "data from arduino:", self.data
            #Main.connection.socket.sendall(self.data)
    
    def send(self, data):
        print "sending to arduino:", data
        self.serial_port.write(data)
        return True
        # ZROBIC RETURN CZY SIE UDALO
    
class Main:
    def __init__(self):
        Main.uart = UartConnection()
        Main.camera = Camera(180)
        Main.connection = SocketConnection()
        Main.connection.start()     

main = Main()
