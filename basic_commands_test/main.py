# This is a sample Python script.
# работало относительно нормально на версии симулятора v62, на v70 всё пошло по одному месту и отладка была заброшена
import requests
from time import sleep
from math import fabs, floor

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
token = "?token=53bf07a4-99de-4d15-80df-2103f25c8cb8e8f82f49-5d24-4d10-885e-bede8fa8bdad&"
robot_cells_url = "http://127.0.0.1:8801/api/v1/robot-cells/"

current_coordinates = [15, 0]
rows, cols = 16, 16
visited_cells = [[0 for i in range(cols)] for j in range(rows)]
answer = [[0 for i in range(cols)] for j in range(rows)]

normal_angle = 0

robot_ip = "192.168.68.187"

sensors = 0

zero_angle = 0

id = "3536AF962E7A4A53"

move_forward_distance = 180

def main():
    # Use a breakpoint in the code line below to debug your script.

    # global normal_angle
    # while not check_if_done():
    #     read_sensors()
    #     walls_by_robot = detect_walls(sensors)
    #     if visited_cells[current_coordinates[0]][current_coordinates[1]] == 0:
    #         visited_cells[current_coordinates[0]][current_coordinates[1]] = 1
    #         # print(f"walls_by_robot {walls_by_robot}")
    #     if not walls_by_robot[1]:
    #         turn_right(90)
    #         normal_angle = (normal_angle + 90) % 360
    #     elif not walls_by_robot[0]:
    #         pass
    #     elif not walls_by_robot[3]:
    #         turn_left(90)
    #         normal_angle = (normal_angle + 270) % 360
    #     else:
    #         turn_right(180)
    #         normal_angle = (normal_angle + 180) % 360
    #
    #     move_forward(move_forward_distance)
    #
    #     if normal_angle == 0:
    #         current_coordinates[0] -= 1
    #     elif normal_angle == 90:
    #         current_coordinates[1] += 1
    #     elif normal_angle == 180:
    #         current_coordinates[0] += 1
    #     elif normal_angle == 270:
    #         current_coordinates[1] -= 1
    #
    #     if (current_coordinates[0] == 7 or current_coordinates[0] == 8) \
    #             and (current_coordinates[1] == 7 or current_coordinates[1] == 8):
    #         break
    #     print(sensors)

    # sleep(0.33)
    # print(get_sensor_data())
    # for i in range(30):
    #     turn_right()
    # move_forward()
    # turn_left()
    # # turn_180()
    for i in range(10):
        read_sensors()
        print(sensors)
        turn_right(90)
        sleep(2)


def read_sensors():
    global sensors
    sensors = requests.post(f"http://{robot_ip}/sensor", json={"id": id, "type": "all"}).json()


def manage_zero_angle():
    global sensors, zero_angle

    sensors = read_sensors()
    zero_angle = sensors['imu']['yaw']


def get_labirint_angle():
    return (sensors['imu']['yaw'] + 360 - zero_angle) % 360


def move_forward(x):
    return requests.post(f"http://{robot_ip}/move", json={"id": id, "direction": "forward", "len": x})


def move_backward(x):
    return requests.post(f"http://{robot_ip}/move", json={"id": id, "direction": "backward", "len": x})


def turn_right(x):
    labirint_angle = get_labirint_angle()
    ostatok = labirint_angle % 90
    if ostatok != 0:
        if ostatok < 30:
            x -= ostatok
        elif ostatok > 60:
            x += 90 - ostatok

    return requests.post(f"http://{robot_ip}/move", json={"id": id, "direction": "right", "len": x})


def turn_left(x):
    labirint_angle = get_labirint_angle()
    ostatok = labirint_angle % 90
    if ostatok != 0:
        if ostatok < 30:
            x += ostatok
        elif ostatok > 60:
            x -= 90 - ostatok

    return requests.post(f"http://{robot_ip}/move", json={"id": id, "direction": "left", "len": x})


def drive_pwm(pwm_l, time_l, pwm_r, time_r):
    return requests.post(f"http://{robot_ip}/motor", json={"id": id, "l": pwm_l, "r": pwm_r, "l_time": time_l, "r_time": time_r})


def pwm_turn_right():
    global sensors
    read_sensors()
    # TODO ПРОВЕРКА НАЧАЛЬНОГО УГЛА
    initial_angle = get_labirint_angle()
    drive_pwm(200, 0.2, -200, 0.2)
    sleep(0.2)
    drive_pwm(0, 1, 0, 1)
    sleep(1)
    read_sensors()
    print(f"initial {initial_angle} current {get_labirint_angle()}")
    while (get_labirint_angle() + 360 - initial_angle) % 360 != 90:
        if (get_labirint_angle() + 360 - initial_angle) % 360 < 90:
            drive_pwm(80, 0.2, -80, 0.2)
        else:
            drive_pwm(-80, 0.2, 80, 0.2)
        sleep(0.2)
        drive_pwm(0, 0.2, 0, 0.2)
        sleep(0.2)
        read_sensors()
        print(f"current {get_labirint_angle()} diff {get_labirint_angle() + 360 - initial_angle}")



def check_if_done():
    is_done = True
    for i in range(cols):
        for j in range(rows):
            if visited_cells[i][j] == 0:
                is_done = False
                break
    return is_done


def detect_walls(sensor_data):
    # округлить угол до десятков
    rounded_angle = round(get_labirint_angle(), -1)

    # print(f"rounded angle {rounded_angle}")

    sensor_distances = [sensor_data['laser']['4'] < 80,
                        sensor_data['laser']['5'] < 80,
                        sensor_data['laser']['1'] < 80,
                        sensor_data['laser']['2'] < 80]

    # print(f"sensor distances {sensor_distances}")

    walls = [sensor_distances[(4 + 4 - rounded_angle // 90) % 4],
             sensor_distances[(4 + 1 - rounded_angle // 90) % 4],
             sensor_distances[(4 + 2 - rounded_angle // 90) % 4],
             sensor_distances[(4 + 3 - rounded_angle // 90) % 4]]

    # print(f"walls {walls}")
    answer[current_coordinates[0]][current_coordinates[1]] = new_code(walls)

    return sensor_distances


def new_code(arr):
    if arr[0] == False and arr[1] == False and arr[2] == False and arr[3] == False:
        kod_new = 0
    elif arr[0] == False and arr[1] == False and arr[2] == False and arr[3] == True:
        kod_new = 1
    elif arr[0] == True and arr[1] == False and arr[2] == False and arr[3] == False:
        kod_new = 2
    elif arr[0] == False and arr[1] == True and arr[2] == False and arr[3] == False:
        kod_new = 3
    elif arr[0] == False and arr[1] == False and arr[2] == True and arr[3] == False:
        kod_new = 4
    elif arr[0] == False and arr[1] == False and arr[2] == True and arr[3] == True:
        kod_new = 5
    elif arr[0] == False and arr[1] == True and arr[2] == True and arr[3] == False:
        kod_new = 6
    elif arr[0] == True and arr[1] == True and arr[2] == False and arr[3] == False:
        kod_new = 7
    elif arr[0] == True and arr[1] == False and arr[2] == False and arr[3] == True:
        kod_new = 8
    elif arr[0] == False and arr[1] == True and arr[2] == False and arr[3] == True:
        kod_new = 9
    elif arr[0] == True and arr[1] == False and arr[2] == True and arr[3] == False:
        kod_new = 10
    elif arr[0] == True and arr[1] == True and arr[2] == True and arr[3] == False:
        kod_new = 11
    elif arr[0] == True and arr[1] == True and arr[2] == False and arr[3] == True:
        kod_new = 12
    elif arr[0] == True and arr[1] == False and arr[2] == True and arr[3] == True:
        kod_new = 13
    elif arr[0] == False and arr[1] == True and arr[2] == True and arr[3] == True:
        kod_new = 14
    elif arr[0] == True and arr[1] == True and arr[2] == True and arr[3] == True:
        kod_new = 15

    return kod_new


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
