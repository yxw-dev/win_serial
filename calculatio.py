import re
import math


def get_angle_from_com_response(response):
    response_str = re.split(':|,', response)[2:]
    print(response_str)
    print(response_str[0])
    try:
        asd = int(response_str[0])

        if asd == 0:
            print("水平角度：{}".format(response_str[1]))
            print("竖直角度：{}".format(response_str[2]))
            print("斜距：{}".format(response_str[3]))
            point = [response_str[1] , response_str[2],response_str[3]]
            return  point
            # horizontal = float(response_str[1])
            # vertical = float(response_str[2])
            # dist = float(response_str[3])
            # trans_position(horizontal, vertical, dist)
    except:
        return False

def getNEZ(he, ve, dist):
    north = dist * math.cos(math.pi / 2 - ve) * math.cos(he)
    eastern = dist * math.cos(math.pi / 2 - ve) * math.sin(he)
    height = dist * math.sin(math.pi / 2 - ve)
    print('N坐标{}'.format(north))
    print('E坐标{}'.format(eastern))
    print('Z坐标{}'.format(height))
    return float('%.4f'%north), float('%.4f'%eastern), float('%.4f'%height)

def getPosition(p11, N0, E0, Z0, p33):
    p33[0] = p11[0] + N0
    p33[1] = p11[1] - E0
    p33[2] = p11[2] - Z0