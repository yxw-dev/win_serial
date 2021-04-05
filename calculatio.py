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

def trans_position(he, ve, dist):
    north = dist * math.cos(math.pi / 2 - ve) * math.cos(he)
    eastern = dist * math.cos(math.pi / 2 - ve) * math.sin(he)
    height = dist * math.sin(math.pi / 2 - ve)
    print('N坐标{}'.format(north))
    print('E坐标{}'.format(eastern))
    print('Z坐标{}'.format(height))
    return north, eastern, height