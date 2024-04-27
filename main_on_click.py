import cv2
import numpy as np
import delta_manager.camera as Camera
from delta_manager.delta_manager import DeltaManager


def click_event(event, u, v, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'Clicked pixel: ({u}, {v})')
    
        z_fom = 2
        z_obj = 1.9
        
        [x, y, z] = Camera.pixel_to_robot_coordinates(
            (u, v), 
            camera_height=50,
            z_obj=z_fom+z_obj, 
            gripper='2f85',
            robot_capturing_coord=np.array(Delta.read_forward())
        )
        z -= z_obj
        print(f'Robot: ({x:.2f}, {y:.2f}, {z:.2f})')

        Delta.move(x, y, z+10)
        Delta.move(x, y, z)


Delta = DeltaManager()
Delta.connect_gripper()

cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)

image_counter = 0

while True:
    _, frame = cap.read()

    # Undistort the frame
    frame = Camera.undistort(frame)
    
    # Image show
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 800, 600)
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
        Delta.open_gripper_slightly()
    elif key_pressed == ord('c'):
        Delta.close_gripper()
    elif key_pressed == ord('h'): 
        Delta.go_home()
    elif key_pressed == ord('e'): 
        Delta.rotate_gripper(-90)
    elif key_pressed == ord('q'): 
        Delta.rotate_gripper(90)
    elif key_pressed == ord('s'):
        Delta.delta_stop_server()


cap.release()
cv2.destroyAllWindows()
