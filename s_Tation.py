import time
import sys
import  re
from threading import Thread

import  serial
import  serial.tools.list_ports

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from window_station import *
from calculatio import getNEZ,get_angle_from_com_response,getPosition

#存放命令集合（字典），从文件读取
order_dict = {'查找角度及距离':'%R1Q,50013:2' , '旋转':'%R1Q,50003:0,0,0,0,0,0,0' , '搜索并照准':'%R1Q,9029:0.2618,0.2618,0'}

#固定点坐标（或者作为已知绝对坐标的两个点）
point1 = [0,0,0]
point2 = [0,0,0]

#查找所得点坐标
f_point1 = [0,0,0]
f_point2 = [0,0,0]

#全站仪坐标
location_point = [0,0,0]

#一共5个点两个确定点，一个全站仪坐标点，两个待查找点的列表
#判断该列表内元素个数确定当前流程执行位置。
#[0]存放全站仪坐标点，之后安点顺序排列
point_list = []



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
        self.Meat_Button.clicked.connect(self.mear_point)
        self.send_button.clicked.connect(self.send)
        self.input_button.clicked.connect(self.get_point)
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

    def send(self):
        self.send_ord(self.send_text.text())

    def send_ord(self , text):
        if (self.com1.isOpen() == True):
            t = '\b\r' + text +'\n'
            send_bytes = self.com1.write(t.encode('utf-8'))
            self.plainTextEdit.appendPlainText(self.send_text.text()+'\r\n' + str(send_bytes))
            ord = re.split(':|,', text)[1]
            self.send_list.append(ord)
        else:
            self.plainTextEdit.appendPlainText('先连接串口')

    def find_point(self):
        #查找点的命令
        self.send_ord(order_dict['搜索并照准'])

    def mear_point(self):
        #根据输入的xyz数据，生成相应命令发送
        self.send_ord(order_dict['查找角度及距离'])

    def move_point(self):
        #根据输入的xyz数据，生成相应命令发送
        t1 = self.lineEdit_6.text()
        t2 = self.lineEdit_7.text()
        text = '%R1Q,50003:' + t1 + ',' + t2 + ',0,0,0,0,0';
        self.send_ord(text)

    def deal(self , text):
        self.plainTextEdit.appendPlainText(text)
        if(len(text) < 15):
            return
        #列表为空，查找得到第一个已知绝对坐标点，计算得全站仪坐标点，存入第一点绝对坐标和全站仪坐标。count变为2
        if len(point_list) == 0:
            temp_point = get_angle_from_com_response(text)
            n, e, z = getNEZ(float(temp_point[0]), float(temp_point[1]), float(temp_point[2]))
            getPosition(point1 , n, e, z, location_point)
            point_list.append(location_point)
            point_list.append(point1)
            self.lineEdit_2.setText(str(point_list[1][0]) + ',' + str(point_list[1][1]) + ',' + str(point_list[1][2]))
            self.lineEdit_5.setText(str(point_list[0][0]) + ',' + str(point_list[0][1]) + ',' + str(point_list[0][2]))
            return

        #列表中已有数据，若为2计算更新全站仪坐标，取平均，写入第二点绝对坐标。cout变为3
        if len(point_list)  == 2:
            temp_point = get_angle_from_com_response(text)
            n, e, z = getNEZ(float(temp_point[0]), float(temp_point[1]), float(temp_point[2]))
            getPosition(point2, n, e, z, location_point)
            tem_point =[0,0,0]
            for i in range(3):
                tem_point[i] = (location_point[i] + point_list[0][i]) / 2
            point_list[0] = tem_point
            point_list.append(point2)
            self.lineEdit.setText(str(point_list[1][0]) + ',' + str(point_list[1][1]) + ',' + str(point_list[1][2]))
            self.lineEdit_5.setText(str(point_list[0][0]) + ',' + str(point_list[0][1]) + ',' + str(point_list[0][2]))
            return

        #根据全站仪坐标，和采集得到的角度距离，计算第三个点坐标，存入。count变为4
        if len(point_list) == 3:
            temp_point = get_angle_from_com_response(text)
            n, e, z = getNEZ(float(temp_point[0]), float(temp_point[1]), float(temp_point[2]))
            getPosition(location_point, n, e, z, f_point1)
            point_list.append(f_point1)
            self.lineEdit_3.setText(str(point_list[3][0]) + ',' + str(point_list[3][1]) + ',' + str(point_list[3][2]))
            return

        #根据全站仪坐标，和采集得到的角度距离，计算最后点坐标，存入。count变为5.写入tex
        if len(point_list) == 4:
            temp_point = get_angle_from_com_response(text)
            n, e, z = getNEZ(float(temp_point[0]), float(temp_point[1]), float(temp_point[2]))
            getPosition(location_point, n, e, z, f_point2)
            point_list.append(f_point2)
            self.lineEdit_4.setText(str(point_list[4][0]) + ',' + str(point_list[4][1]) + ',' + str(point_list[4][2]))
            try:
                with open("test.txt", "a") as f:
                    for i in range(len(point_list)):
                        f.write('[' + str(point_list[i][0]) + ',' + str(point_list[i][1]) + ',' + str(point_list[i][2]) + '];')
                    f.write('\r\n')
            except Exception as e:
                print(str(e))
            return

        #清空列表，执行count=0时代码
        if len(point_list) == 5:
            for i in range(len(point1)):
                point1[i] = f_point1[i]
                point2[i] = f_point1[i]
            point_list.clear()
            temp_point = get_angle_from_com_response(text)
            n, e, z = getNEZ(float(temp_point[0]), float(temp_point[1]), float(temp_point[2]))
            getPosition(point1, n, e, z, location_point)
            point_list.append(location_point)
            point_list.append(point1)

            self.lineEdit_2.setText(str(point_list[1][0]) + ',' + str(point_list[1][1]) + ',' + str(point_list[1][2]))
            self.lineEdit_5.setText(str(point_list[0][0]) + ',' + str(point_list[0][1]) + ',' + str(point_list[0][2]))
            self.lineEdit.setText('')
            self.lineEdit_3.setText('')
            self.lineEdit_4.setText('')
            return

    def get_point(self):
        try:
            point1[0] = float(self.input1_1.text())
            point1[1] = float(self.input1_2.text())
            point1[2] = float(self.input1_3.text())
            point2[0] = float(self.input2_1.text())
            point2[1] = float(self.input2_2.text())
            point2[2] = float(self.input2_3.text())
        except Exception as e:
            print(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec_())