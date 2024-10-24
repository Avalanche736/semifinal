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

mts_govno = True


def main():
    global mts_govno
    while mts_govno:
        read_sensors()
        manage_movement()


# go forward maintaining right sensor distance variables
forward_typical_pwm = 150
target_right_sensor_value = 65
go_forward_sampling_time = 0.2

angle_coefficient_proportional = 1
angle_coefficient_derivative = 1
angle_coefficient_integral = 1
angle_error = 0
angle_error_derivative = 0
angle_error_integral = 0
adjustment_value_angle = 0

right_sensor_coefficient_proportional = 1
right_sensor_coefficient_derivative = 1
right_sensor_coefficient_integral = 1
right_sensor_error = 0
right_sensor_error_derivative = 0
right_sensor_error_integral = 0
adjustment_value_right_sensor = 0


# called from manage_movement()
def go_forward_adjusting_by_angle_and_right_sensor():
    global forward_typical_pwm, target_right_sensor_value, sensors

    global angle_coefficient_proportional, angle_coefficient_derivative, angle_coefficient_integral, \
        angle_error, angle_error_derivative, angle_error_integral, adjustment_value_angle

    global right_sensor_coefficient_proportional, right_sensor_coefficient_derivative, right_sensor_coefficient_integral, \
        right_sensor_error, right_sensor_error_derivative, right_sensor_error_integral, adjustment_value_right_sensor

    right_sensor_distance = sensors['laser']['5']
    current_angle = get_labyrinth_angle()

    # adjustment by angle
    angle_error_derivative = (((current_angle + 45) % 90 - 45) - angle_error) / go_forward_sampling_time
    angle_error = (current_angle + 45) % 90 - 45  # (current_angle + 45) % 90 - 45 - это ж просто шедевр
    angle_error_integral += angle_error * go_forward_sampling_time

    adjustment_value_angle = angle_error * angle_coefficient_proportional + \
                             angle_error_derivative * angle_coefficient_derivative + \
                             angle_error_integral * angle_coefficient_integral

    # adjustment by right_sensor
    right_sensor_error_derivative = ((target_right_sensor_value - right_sensor_distance) - right_sensor_error) / go_forward_sampling_time
    right_sensor_error = target_right_sensor_value - right_sensor_distance
    right_sensor_error_integral += right_sensor_error * go_forward_sampling_time

    adjustment_value_right_sensor = right_sensor_error * right_sensor_coefficient_proportional + \
                             right_sensor_error_derivative * right_sensor_coefficient_derivative + \
                             right_sensor_error_integral * right_sensor_coefficient_integral

    left_pwm = forward_typical_pwm + adjustment_value_angle - adjustment_value_right_sensor
    right_pwm = forward_typical_pwm - adjustment_value_angle + adjustment_value_right_sensor

    drive_pwm(left_pwm, go_forward_sampling_time, right_pwm, go_forward_sampling_time)
    sleep(go_forward_sampling_time)


len_kletka = 168
len_robot = 88


def manage_movement():
    global len_kletka, len_robot
    right_sensor_distances = sensors['laser']['5']
    forw_sensor_distances = sensors['laser']['4']
    left_sensor_distances = sensors['laser']['2']

    if right_sensor_distances > len_kletka:
        move_forward(len_kletka // 2)
        turn_right(90)
        move_forward(140)

    elif forw_sensor_distances > len_kletka:
        go_forward_adjusting_by_angle_and_right_sensor()

    elif left_sensor_distances > len_kletka:
        move_forward(140)
        turn_left(90)
        move_forward(180)
    else:
        move_forward(len_kletka // 2)
        turn_left(90)
        move_forward(len_kletka // 2)
        turn_left(90)



def read_sensors():
    global sensors
    sensors = requests.post(f"http://{robot_ip}/sensor", json={"id": id, "type": "all"}).json()


def manage_zero_angle():
    global sensors, zero_angle

    sensors = read_sensors()
    zero_angle = sensors['imu']['yaw']


def get_labyrinth_angle():
    return (sensors['imu']['yaw'] + 360 - zero_angle) % 360


def move_forward(x):
    return requests.put(f"http://{robot_ip}/move", json={"id": id, "direction": "forward", "len": x})


def move_backward(x):
    return requests.put(f"http://{robot_ip}/move", json={"id": id, "direction": "backward", "len": x})


def turn_right(x):
    # labirint_angle = get_labirint_angle()
    # ostatok = labirint_angle % 90
    # if ostatok != 0:
    #     if ostatok < 30:
    #         x -= ostatok
    #     elif ostatok > 60:
    #         x += 90 - ostatok

    print(f"check x {x}")

    return requests.put(f"http://{robot_ip}/move", json={"id": id, "direction": "right", "len": x},
                         headers={'Content-Type': 'application/json'})


def turn_left(x):
    labirint_angle = get_labyrinth_angle()
    ostatok = labirint_angle % 90
    if ostatok != 0:
        if ostatok < 30:
            x += ostatok
        elif ostatok > 60:
            x -= 90 - ostatok

    return requests.put(f"http://{robot_ip}/move", json={"id": id, "direction": "left", "len": x})


def drive_pwm(pwm_l, time_l, pwm_r, time_r):
    return requests.put(f"http://{robot_ip}/motor", json={"id": id, "l": pwm_l, "r": pwm_r, "l_time": time_l, "r_time": time_r})


def pwm_turn_right():
    global sensors
    read_sensors()
    # TODO ПРОВЕРКА НАЧАЛЬНОГО УГЛА
    initial_angle = get_labyrinth_angle()
    drive_pwm(200, 0.2, -200, 0.2)
    sleep(0.2)
    drive_pwm(0, 1, 0, 1)
    sleep(1)
    read_sensors()
    print(f"initial {initial_angle} current {get_labyrinth_angle()}")
    while (get_labyrinth_angle() + 360 - initial_angle) % 360 != 90:
        if (get_labyrinth_angle() + 360 - initial_angle) % 360 < 90:
            drive_pwm(80, 0.2, -80, 0.2)
        else:
            drive_pwm(-80, 0.2, 80, 0.2)
        sleep(0.2)
        drive_pwm(0, 0.2, 0, 0.2)
        sleep(0.2)
        read_sensors()
        print(f"current {get_labyrinth_angle()} diff {get_labyrinth_angle() + 360 - initial_angle}")



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
    rounded_angle = round(get_labyrinth_angle(), -1)

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
