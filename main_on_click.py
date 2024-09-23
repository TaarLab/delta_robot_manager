import cv2
import numpy as np
import delta_manager.camera as Camera
from delta_manager.delta_manager import DeltaManager


def click_event(event, u, v, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'Clicked pixel: ({u}, {v})')
    
        # z_fom = 2
        z_fom = 0
        z_obj = 0
        

        [x, y, z] = Camera.pixel_to_robot_coordinates(
            (u, v), 
            z_obj=z_fom+z_obj, 
            gripper='2f85',
            robot_capturing_coord=np.array(Delta.read_forward())
        )
        z -= (z_obj/2)

        print(f'Robot: ({x:.2f}, {y:.2f}, {z:.2f})')

        Delta.move_with_time(x, y, z+6, 3)
        Delta.move_with_time(x, y, z+1, 3)


Delta = DeltaManager()

cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)

WIDTH = 4000
HEIGHT = 4000
fourcc = cv2.VideoWriter_fourcc(*'XVID')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)


width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print([width,height])

image_counter = 0

while True:
    _, frame = cap.read()

    # Undistort the frame
    frame = Camera.undistort(frame)
    
    # Image show
    cv2.namedWindow('image')
    # cv2.resizeWindow('image', 800, 600)
    cv2.setMouseCallback('image', click_event)
    cv2.imshow('image', frame)

    # Image save
    key_pressed = cv2.waitKeyEx(1)

    if key_pressed == 27:   # Esc key
        break
    # elif key_pressed == ord(' '): 
    #     cv2.imwrite('./Images/image'+str(image_counter)+'.jpg', frame)
    #     print(f'image {image_counter} saved.')
    #     image_counter += 1
    elif key_pressed == ord('f'):
        current_position = Delta.read_forward()
        print(f'Current position: {current_position}')
    elif key_pressed == ord('u'):
        x,y,z = Delta.read_forward()
        Delta.move_with_time(x, y, z+0.1, 2)
    elif key_pressed == ord('d'):
        x,y,z = Delta.read_forward()
        Delta.move_with_time(x, y, z-0.1, 2)
    elif key_pressed == 2424832: # left
        x,y,z = Delta.read_forward()
        Delta.move_with_time(x+0.1, y, z, 2)
    elif key_pressed == 2555904: # right
        x,y,z = Delta.read_forward()
        Delta.move_with_time(x-0.1, y, z, 2)
    elif key_pressed == 2490368: # up
        x,y,z = Delta.read_forward()
        Delta.move_with_time(x, y-0.1, z, 2)
    elif key_pressed == 2621440: # down
        x,y,z = Delta.read_forward()
        Delta.move_with_time(x, y+0.1, z, 2)
    elif key_pressed == ord('m'):
        input_str = input('Enter x, y, z: ')
        x, y, z = input_str.split(',')
        Delta.move_with_time(float(x), float(y), float(z), 5)
    elif key_pressed == ord('o'):
        Delta.delta_open_gripper()
    elif key_pressed == ord('c'):
        Delta.delta_close_gripper()
    elif key_pressed == ord('h'): 
        Delta.go_home()
    elif key_pressed == ord('e'): 
        Delta.delta_rotate_gripper(-2)
    elif key_pressed == ord('q'): 
        Delta.delta_rotate_gripper(2)
    elif key_pressed == ord('s'):
        Delta.delta_stop_server()


cap.release()
cv2.destroyAllWindows()
