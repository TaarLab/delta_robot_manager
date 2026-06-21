import time
import serial
import serial.tools.list_ports as port_list
# import delta_manager.camera as Camera
import delta_manager.client as Client


class DeltaManager():
    SERIAL_BAUD_RATE = 1000000  # Updated from 38400 for the new gripper
    
    def __init__(self, debug_mode=False):
        self.DEBUG_MODE = debug_mode
        # Initialize current position for debug mode
        self.current_position = [0, 0, -37]  # Start at home position
        self.current_gripper_angle = [0, 90, 180]  # Track gripper angle

    ## Gripper functions
    def connect_gripper(self, ):
        if self.DEBUG_MODE:
            print("[DEBUG] Connecting to gripper...")
            print("[DEBUG] Available ports would be scanned")
            print("[DEBUG] Gripper would be connected on COM/ttyACM port with CH340")
            self.gripper = None  # Still set to None in debug mode
            return
        else:
            self.gripper = None
            available_ports = self.get_all_ports()
            for port in available_ports:
                port_name = self.get_port_name(port)
                if 'COM' in port_name or 'ttyACM' in port_name:  #TODO: check if this works on linux
                    if 'CH340' in self.get_description(port):
                        self.gripper = serial.Serial(
                            port_name, 
                            self.SERIAL_BAUD_RATE, 
                            timeout=None
                        )    
            
            if self.gripper:
                self.gripper.write(f"\r\n".encode("utf-8"))
                print("Gripper connected")
                time.sleep(5)
            else:
                # raise Exception("Gripper not found")
                print("Gripper not found")

    def get_all_ports(self, ):
        if self.DEBUG_MODE:
            print("[DEBUG] Getting all ports...")
            return [("COM3", "USB Serial Port"), ("ttyACM0", "CH340")]
        else:
            return [tuple(p) for p in list(port_list.comports())]

    def get_port_name(self, port):
        return port[0]
    
    def get_description(self, port):
        return port[1]
    
    def open_gripper(self, ):
        if self.DEBUG_MODE:
            print("[DEBUG] opening gripper")
        else:
            self.gripper.write("cg1\n".encode("utf-8"))
            # self.wait_till_done_gripper()
            print("opening gripper")

    def open_gripper_slightly(self, ):
        if self.DEBUG_MODE:
            print("[DEBUG] opening gripper a little bit")
        else:
            self.gripper.write("cg2\n".encode("utf-8"))
            self.gripper.reset_input_buffer()
            # self.wait_till_done_gripper()
            print("opening gripper a little bit")

    def close_gripper(self, ):
        if self.DEBUG_MODE:
            print("[DEBUG] closing gripper")
        else:
            self.gripper.write("cg2\n".encode("utf-8"))
            self.gripper.reset_input_buffer()
            # self.wait_till_done_gripper()
            print("closing gripper")

    def close_gripper_with_feedback(self, ):
        if self.DEBUG_MODE:
            print("[DEBUG] close gripper with feedback")
            print("[DEBUG] for feedback from gripper")
            time.sleep(1)
            return "Done"  
        else:
            self.gripper.write(f"g".encode("utf-8"))
            print("closing gripper")
            self.gripper.reset_input_buffer()
            result = self.wait_till_done_gripper(wait_for_failed=True)
            return result
            
    def rotate_gripper(self, x=0, y=90, z=180):
        if self.DEBUG_MODE:
            self.current_gripper_angle = [x, y, z]
            print(f"[DEBUG] rotate gripper to X:{x} Y:{y} Z:{z}")
        else:
            command = f"cr{x}-{y}-{z}\n"
            self.gripper.write(command.encode("utf-8"))
            print(f"rotating gripper to X:{x} Y:{y} Z:{z}")
            
    def home_rotation(self):
        """Quick helper to send the default cr0-90-180 homing command"""
        self.rotate_gripper(0, 90, 180)

    def force_gripper(self, real_fz, desired_fz, f_x):
        if self.DEBUG_MODE:
            print(f"[DEBUG] setting gripper force: real_fz={real_fz}, desired_fz={desired_fz}, f_x={f_x}")
        else:
            # Matches the f{real_fz}-{desired_fz}-{f_x} 
            command = f"f{real_fz:.2f}-{desired_fz:.2f}-{f_x:.2f}\n"
            self.gripper.write(command.encode("utf-8"))
            print(f"setting gripper force target to {desired_fz}N")
    
    def wait_till_done_gripper(self, wait_for_failed=False):
        if self.DEBUG_MODE:
            time.sleep(1)
            print("[DEBUG] wait for gripper to complete operation")
            return "Done"
        else:
            while 1:
                result = self.gripper.readline().decode("utf-8")
                print(f"Gripper: {result}")
                if result[0:4] == "Done":
                    break
                elif result[0:6] == "failed" and wait_for_failed:
                    break
            return result

    ## Delta functions
    def wait_till_done_robot(self, ):
        if self.DEBUG_MODE:
            print("[DEBUG] Waiting to complete operation")
            time.sleep(1)
            return "success" 
        else:
            while 1:
                result = Client.Result
                print(f"Robot: {result}")
                if result == "success":
                    break
            return result

    def go_home(self, ):
        if self.DEBUG_MODE:
            self.current_position = [0, 0, -37]
            print("[DEBUG] move robot to home position (0, 0, -37)")
            return
        else:
            self.move(0, 0, -37)
            self.wait_till_done_robot()
            print("going home")

    def move(self, x, y, z):
        if z>-30:
            print("PLEASE ENTER NEGATIVE NUMBERS BETWEEN -37,-65")
            return
        if self.DEBUG_MODE:
            self.current_position = [x, y, z]
            print(f"[DEBUG] moving to {x}, {y}, {z}")
            return
        else:
            print(f'moving to {x}, {y}, {z}')
            Client.order("move", f"{x},{y},{z}")
            self.wait_till_done_robot()
        
    def move_with_time(self, x, y, z, t):
        if z>-30:
            print("PLEASE ENTER NEGATIVE NUMBERS BETWEEN -37,-65")
            return
        if self.DEBUG_MODE: 
            self.current_position = [x, y, z]
            print(f"[DEBUG] moving to {x}, {y}, {z} in {t} seconds")
            return
        else:
            print(f"moving to {x}, {y}, {z} in {t} seconds")
            Client.order("movefast", f"{x},{y},{z},{t}")
            self.wait_till_done_robot()

    def read_forward(self, ):
        if self.DEBUG_MODE:
            print(f"[DEBUG] Read current robot position ({self.current_position[0]:.3f}, {self.current_position[1]:.3f}, {self.current_position[2]:.3f})")
            return self.current_position.copy()
        else:
            Client.order("command", "forward")
            robot_current_coordinate = [Client.Result[1], Client.Result[2], Client.Result[3]]
            return robot_current_coordinate

    def delta_stop_server(self, ):
        if self.DEBUG_MODE:
            print("[DEBUG] Stop Delta server")
            print('Delta is now offline...')
            return
        else:
            Client.order("command", "stop")
            print('Delta is now offline...')

    def delta_rotate_gripper(self, angle):
        if self.DEBUG_MODE:
            self.current_gripper_angle += int(angle)
            print(f"[DEBUG] Rotate Delta gripper {angle} degrees (total angle: {self.current_gripper_angle}°)")
            return
        else:
            Client.order("rotate", f"{angle}")
            print(f'Delta is rotating gripper {angle} degrees')

    def delta_open_gripper(self, ):
        if self.DEBUG_MODE:
            print("[DEBUG] Open Delta gripper")
            print('Gripper is now open')
            return
        Client.order("command", "opengripper")
        print('Gripper is now open')
        
    def delta_close_gripper(self, ):
        if self.DEBUG_MODE:
            print("[DEBUG] Close Delta gripper")
            print('Gripper is now close')
            return
        Client.order("command", "closegripper")
        print('Gripper is now close')
