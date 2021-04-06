import time
import sys
from threading import Thread

import  serial
import  serial.tools.list_ports

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from window_station import *
from calculatio import trans_position,get_angle_from_com_response

#存放命令集合（字典），从文件读取
order_dict = {'查找':'%R1Q,50013:2'}

#固定点坐标
point1 = []
point2 = []
get_point = []


class MyMainWindow(QMainWindow , Ui_MainWindow , QObject):
    def __init__(self ):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        self.readflag =False
        self.AddItem_com()
        self.com1 = serial.Serial
        self.send_button.setEnabled(False)
        self.Connect_Button.clicked.connect(self.connect)
        self.Find_Button.clicked.connect(self.find_point)
        self.Move_Button.clicked.connect(self.move_point)
        self.send_button.clicked.connect(self.send_ord)
        self.input_point.clicked.connect(self.refrush_point)
        self.get_single.connect(self.deal)

        #记录发送与接受数据，应当一一对应。字典不适用，相同键不能出现两次，但是会出先相同命令发送多次
        self.send_list = []
        self.result_list = []

    get_single = pyqtSignal(str)
    def AddItem_com(self):
        port_list = list(serial.tools.list_ports.comports())
        self.com_Baud.addItems(['2400','4800','9600','19200','38400','57600','115200'])
        self.com_Port.addItem('/dev/ttyUSB0')
        self.com_Port.addItem('/dev/ttyAMA0')
        if len(port_list) != 0:
            for i in range(0, len(port_list)):
                self.com_Port.addItem(str(port_list[i])[0:4])

    def connect(self):
        if(self.Connect_Button.text() == "断开"):
            self.Connect_Button.setText('连接')
            self.send_button.setEnabled(False)
            self.readflag = False
            self.com1.close()
            self.plainTextEdit.appendPlainText("断开成功")
            return
        try:
            self.com1 = serial.Serial(str(self.com_Port.currentText()), int(self.com_Baud.currentText()))
            if (self.com1.isOpen() == True):
                self.readflag = True
                self.send_button.setEnabled(True)
                self.plainTextEdit.appendPlainText("连接成功")
                self.Connect_Button.setText('断开')
                read = Thread(target=self.get_date)
                read.start()
            else:
                self.plainTextEdit.appendPlainText("连接失败")
        except Exception as e:
            self.plainTextEdit.appendPlainText(str(e))
    def get_date(self):
        time.sleep(0.1)
        while self.readflag:
            if self.com1.inWaiting():
                try:
                    # data = self.open_com.read_all().decode("utf-8")
                    data = self.com1.readline().decode("utf-8")
                    print(len(data))
                    if len(data) > 10:
                        # print(data.length)
                        self.get_single.emit(str(data))
                        print(data)
                except Exception as e:
                    print(str(e))
        # print(data.type)
        # ad = data
        #                 get_angle_from_com_response(str(ad))
        #         except serial.SerialException as e:
        #             # There is no new data from serial port
        #             return None
        #         except TypeError as e:
        #             # Disconnect of USB->UART occured
        #             self.open_com.close()
        #             return None
        #         else:
        #             # Some data was received
        #             return data
    def send_ord(self):
        if (self.com1.isOpen() == True):
            t = '\b\r' + self.send_text.text()+'\n'
            send_bytes = self.com1.write(t.encode('utf-8'))
            #get_angel_cmd = '\b\r%R1Q,50013:2\n'
            #send_bytes = self.com1.write(get_angel_cmd.encode('utf-8'))
            self.plainTextEdit.appendPlainText(self.send_text.text()+'\r\n' + str(send_bytes))
            self.send_list.append(self.send_text.text())
        else:
            self.plainTextEdit.appendPlainText('先连接串口')

    def find_point(self):
        #查找点的命令
        text = ""
        try:
            if (self.com1.isOpen() == True):
                self.com1.write(text)
            else:
                self.plainTextEdit.appendPlainText('请先打开串口')
        except Exception as e:
            self.plainTextEdit.appendPlainText('请先打开串口')

    def move_point(self):
        #根据输入的xyz数据，生成相应命令发送
        t1 = self.lineEdit_6.text()
        t2 = self.lineEdit_7.text()
        t3 = self.lineEdit_8.text()
        text = ""
        try:
            if (self.com1.isOpen() == True):
                self.com1.write(text)
            else:
                self.plainTextEdit.appendPlainText('请先打开串口')
        except Exception as e:
            self.plainTextEdit.appendPlainText('请先打开串口')

    def deal(self , text):
        #刷新界面输出
        self.plainTextEdit.appendPlainText(text)
        #处理返回结果
        temp_point = get_angle_from_com_response(text)
        if temp_point is None:
            return
        else:
            n,e,z = trans_position(float(temp_point[0]) , float(temp_point[1]) , float(temp_point[2]))
            get_p = [n,e,z]
            get_point.append(get_p)
        if(len(get_point) <= 5):
            try:
                self.lineEdit_2.setText(str(get_point[0][0]) +','+ str(get_point[0][1]) +','+ str(get_point[0][2]))
                self.lineEdit.setText(str(get_point[1][0]) +',' + str(get_point[1][1]) +','+ str(get_point[1][2]))
                self.lineEdit_5.setText(str(get_point[2][0])+',' + str(get_point[2][1])+',' + str(get_point[2][2]))
                self.lineEdit_3.setText(str(get_point[3][0])+',' + str(get_point[3][1])+',' + str(get_point[3][2]))
                self.lineEdit_4.setText(str(get_point[4][0])+',' + str(get_point[4][1])+',' + str(get_point[4][2]))
                get_point.clear()
            except Exception as e:
                print(str(e))
        else:
            tem = get_point[5]
            self.lineEdit_2.setText(str(get_point[5]))
            self.lineEdit.setText('')
            self.lineEdit_5.setText('')
            self.lineEdit_3.setText('')
            self.lineEdit_4.setText('')
            get_point.clear()
            get_point.append(tem)

    def refrush_point(self):
        try:
            point1 = [float(self.input1_1.text()), float(self.input1_2.text()), float(self.input1_3.text())]
            point2 = [float(self.input2_1.text()), float(self.input2_2.text()), float(self.input2_3.text())]
        except Exception as e:
            print('请输入')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec_())