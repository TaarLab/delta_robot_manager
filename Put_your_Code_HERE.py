import cv2
import numpy as np
import delta_manager.camera as Camera
from delta_manager.delta_manager import DeltaManager

#remove this part in your code it is only for demonstration
np.random.seed(53)
u = np.random.randint(0, 1280, size=5)
v = np.random.randint(0, 720, size=5,)

random_camera_coordinates = np.column_stack((u, v))    

Delta = DeltaManager(debug_mode=True)

# Define Capturing coordinate or use default
capturing_coord = [0,0,-37]

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

WIDTH = 4000
HEIGHT = 4000
fourcc = cv2.VideoWriter_fourcc(*'XVID')
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)


width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Your image size:",[width,height])

def PPO(u,v,obj_height,init_coord,time = 5,is_in_capturing_coord = False, is_mat_there = True):
        if is_mat_there:
            z_fom = 3 
        else:
            z_fom = 0
        
        init_x, init_y, init_z = init_coord[0], init_coord[1], init_coord[2]

        [final_x, final_y, final_z] = Camera.pixel_to_robot_coordinates(
            (u, v), 
            z_obj=z_fom+obj_height, 
            gripper='New_Hand',
            robot_capturing_coord=np.array(init_coord)
        )
        final_z -= (obj_height/2)

        print(f'Robot moving to: ({final_x:.2f}, {final_y:.2f}, {final_z:.2f})')

        if is_in_capturing_coord:
            Delta.move_with_time(final_x, final_y, final_z+6, time)
            Delta.move_with_time(final_x, final_y, final_z, time)
        else:
            # Do Adept cycle
            Delta.move_with_time(init_x, init_y, init_z+6, time)
            Delta.move_with_time(final_x, final_y, final_z+6, time)
            Delta.move_with_time(final_x, final_y, final_z, time)

print("going to capturing coordinate")
Delta.move_with_time(capturing_coord[0],capturing_coord[1],capturing_coord[2],5)

while True:
    _, frame = cap.read()

    # Undistort the frame
    frame = Camera.undistort(frame)

    # Use your model to find objects 
    ## obj coordinates in pixels
    ## in this example we have 5 objects in random positions
    obj_coordinates = random_camera_coordinates

    # Image show
    cv2.namedWindow('image')
    for obj_coord in obj_coordinates:
        cv2.rectangle(frame,obj_coord-40,obj_coord+40,(255,0,0),2)
    cv2.imshow('image', frame)

    # Image save
    key_pressed = cv2.waitKeyEx(1)

    if key_pressed == 27:   # Esc key
        break


# Your Core Research backbone goes here
# Do task planning here 
# Define your PPO here

obj_coord_0 = obj_coordinates[0]
Delta.open_gripper()
init_coord = Delta.read_forward()
PPO(obj_coord[0],obj_coord[1],5,init_coord,5,True)
Delta.close_gripper()

for obj_coord in obj_coordinates:
    Delta.open_gripper()
    init_coord = Delta.read_forward()
    PPO(obj_coord[0],obj_coord[1],5,init_coord,5,False)
    Delta.close_gripper()

Delta.go_home()

cap.release()
cv2.destroyAllWindows()
