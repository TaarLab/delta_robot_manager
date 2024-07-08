import cv2
import numpy as np
import delta_manager.camera as Camera
from delta_manager.delta_manager import DeltaManager


def click_event(event, u, v, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'Pixel: ({u}, {v})')

        z_fom = 0
        z_obj = 0
        

        [x, y, z] = Camera.pixel_to_robot_coordinates(
            (u, v), 
            z_obj=z_fom+z_obj, 
            gripper='pichgooshti',
            robot_capturing_coord=np.array(Delta.read_forward())
        )
        z -= (z_obj/2)
        #for safty
        # z += 5

        print(f'Robot: ({x:.2f}, {y:.2f}, {z:.2f})')

        Delta.move_with_time(x, y, z+10, 3)
        Delta.move_with_time(x, y, z, 3)


Delta = DeltaManager()
Delta.connect_gripper()

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

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
    key_pressed = cv2.waitKey(1)
    if key_pressed == 27:   # Esc key
        break
    elif key_pressed == ord(' '): 
        cv2.imwrite('./Images/image'+str(image_counter)+'.jpg', frame)
        print(f'image {image_counter} saved.')
        image_counter += 1
    elif key_pressed == ord('f'):
        current_position = Delta.read_forward()
        print(f'Current position: {current_position}')
    elif key_pressed == ord('u'):
        x,y,z = Delta.read_forward()
        Delta.move_with_time(x, y, z+0.5, 2)
    elif key_pressed == ord('d'):
        x,y,z = Delta.read_forward()
        Delta.move_with_time(x, y, z-0.5, 2)
    elif key_pressed == ord('o'):
        Delta.open_gripper()
    elif key_pressed == ord('l'):
        Delta.open_gripper_aBit()
    elif key_pressed == ord('c'):
        Delta.close_gripper()
    elif key_pressed == ord('h'): 
        Delta.go_home()
    elif key_pressed == ord('e'): 
        Delta.rotate_gripper(-45)
    elif key_pressed == ord('q'): 
        Delta.rotate_gripper(45)


cap.release()
cv2.destroyAllWindows()
