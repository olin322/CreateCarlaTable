import math
import carla
from carla import Actor
from carla import Vector3D
from carla import Transform, Location, Rotation
from datetime import date
from datetime import datetime


###
# CONSTANT VARIABLES
###
RELATIVE_PATH = "./output_data/"
ABSOLUTE_PATH = "/home/carla/CarlaTable/rawData/"
DEBUG_LOG_PATH = "/home/carla/CarlaTable/log/"
DELTA_V_CAP = 1e-5
FREQUENCY = 1000
DELTA_T = 1 / FREQUENCY
HEADER = ["velocity_x(m/s), velocity_y(m/s), velocity_z(m/s)", "location_x, location_y, location_z", \
         "pitch, yaw, roll", "acceleration_x(m/s^2), acceleration_y(m/s^2), acceleration_z(m/s^2)", \
         "angular_velocity_x(deg/s), angular_velocity_y(deg/s), angular_velocity_z(deg/s)"]


# Connect to the client and retrieve the world object
client = carla.Client('localhost', 2000)
# load map 
# NOTE: It is critical to load_world FIRST before
# calling "world = cliend.get_world()"
client.load_world('Town06')
world = client.get_world()
settings = world.get_settings()

# set rendering mode
# settings.no_rendering_mode = True

settings.synchronous_mode = True # Enables synchronous mode
settings.fixed_delta_seconds = DELTA_T
world.apply_settings(settings)

# get blueprint
level = world.get_map()
weather = world.get_weather()
blueprint_library = world.get_blueprint_library()

# Get the blueprint library and filter for the vehicle blueprints
# vehicle_blueprints = world.get_blueprint_library().filter('*vehicle*')

# good spawn point for Town06
ego_vehicle_spawn_point = Transform(Location(x=-272, y=-18, z=0.281494), \
                                    Rotation(pitch=0.000000, yaw=0.0, roll=0.000000))
ego_vehicle = world.spawn_actor(blueprint_library.find('vehicle.tesla.model3'), \
                                ego_vehicle_spawn_point)
# ego_vehicle = world.spawn_actor(blueprint_library.find('vehicle.ford.mustang'), \
#                                 ego_vehicle_spawn_point)


# sets the camera to focus on ego_vehicle
def setSpectator(ego_vehicle:Actor, spectator:Actor) -> None:
    spectator_transform = ego_vehicle.get_transform()
    spectator.set_transform(carla.Transform(spectator_transform.location + \
                            carla.Location(x=0, y=0,z=30), carla.Rotation(pitch=-90)))

#     !!!!!!!!!!!!!!!!!!
# return True if ego vehicle is moving at constant velocity
def is_at_const_speed(ego_vehicle_velocity:Vector3D, pre_ego_vehicle_velocity:Vector3D) -> bool:
#     ego_vehicle_velocity = ego_vehicle.get_velocity()
    print(abs(ego_vehicle_velocity.x - pre_ego_vehicle_velocity.x))
    return ((abs(ego_vehicle_velocity.x - pre_ego_vehicle_velocity.x) < DELTA_V_CAP) & \
            (abs(ego_vehicle_velocity.y - pre_ego_vehicle_velocity.y) < DELTA_V_CAP) & \
            (abs(ego_vehicle_velocity.z - pre_ego_vehicle_velocity.z) < DELTA_V_CAP))


# helper function, collects data to be recorded
def get_vehicle_velocity_info(vehicle:Actor) -> str:
    vehicle_velocity = vehicle.get_velocity()
    data = str(vehicle_velocity.x) + "," \
         + str(vehicle_velocity.y) + "," \
         + str(vehicle_velocity.z)
    return data

def get_vehicle_location_info(vehicle:Actor) -> str:
    vehicle_transform = vehicle.get_transform()
    vehicle_location = vehicle_transform.location
    data = str(vehicle_location.x) + "," \
         + str(vehicle_location.y) + "," \
         + str(vehicle_location.z)
    return data
    
def get_vehicle_rotation_info(vehicle:Actor) -> str:
    vehicle_transform = vehicle.get_transform()
    vehicle_rotation = vehicle_transform.rotation  # pitch-y, yaw-z, roll-x
    data = str(vehicle_rotation.pitch) + "," \
         + str(vehicle_rotation.yaw) + "," \
         + str(vehicle_rotation.roll)
    return data

def get_vehicle_acceleration_info(vehicle:Actor) -> str:
    vehicle_acceleration = vehicle.get_acceleration()
    data = str(vehicle_acceleration.x) + "," \
         + str(vehicle_acceleration.y) + "," \
         + str(vehicle_acceleration.z)
    return data

def get_angular_velocity_info(vehicle:Actor) -> str:
    vehicle_angular_velocity = vehicle.get_angular_velocity()
    data = str(vehicle_angular_velocity.x) + "," \
         + str(vehicle_angular_velocity.y) + "," \
         + str(vehicle_angular_velocity.z)\
#     if(vehicle_angular_velocity == None):
#         print("angular_velocity_not_available")
    return data

# return name of the file that raw data will write to  
def create_file_name(ego_vehicle_throttle:float, ego_vehicle_steer:float) -> str:
    today = date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    file_name = "raw_data_throttle=" + str(ego_vehicle_throttle) + "_steer=" \
              + str(ego_vehicle_steer) + "_" + str(today) + "_" + str(current_time) +".csv"
    return file_name

def write_to_file(file_name:str, data:str) -> None:
    f = open(file_name, "a")
    f.write(data)
    f.close()
    return None

### Constants
REC_FUNC = [get_vehicle_velocity_info, get_vehicle_location_info, get_vehicle_rotation_info, \
           get_vehicle_acceleration_info, get_angular_velocity_info]

# main loop where all key actions take place
def loop(throttle:float, steer:float, ego_vehicle:Actor, spectator:Actor, \
         file_name:str, rec_choice:list) -> None:
    # initialization
    start_time_in_real_world = datetime.utcnow()
    pre_ego_vehicle_velocity = Vector3D(0.0, 0.0, 0.0)
    frame_zero = world.get_snapshot().frame
    at_const_speed = False
    elapsed_seconds = 0.0
#     while True:
#     while elapsed_seconds <= 100:
#     while (not at_const_speed):
    while (elapsed_seconds <= 60) | (not at_const_speed):
        setSpectator(ego_vehicle, spectator)
        
        ego_vehicle_throttle = throttle
        ego_vehicle_steer = steer
        ego_vehicle.apply_control(carla.VehicleControl(\
                        throttle=ego_vehicle_throttle, steer=ego_vehicle_steer))
        
        snapshot = world.get_snapshot()
        frame = snapshot.frame - frame_zero
        elapsed_seconds = snapshot.elapsed_seconds
        delta_seconds = snapshot.delta_seconds
        platform_timestamp = snapshot.platform_timestamp
        
#         print(elapsed_seconds)
        ego_vehicle_velocity = ego_vehicle.get_velocity()
        at_const_speed = is_at_const_speed(ego_vehicle_velocity, pre_ego_vehicle_velocity) \
                         & (elapsed_seconds >= 5)
#         print(at_const_speed)
        delta_velocity = Vector3D(ego_vehicle_velocity.x - pre_ego_vehicle_velocity.x, 
                                  ego_vehicle_velocity.y - pre_ego_vehicle_velocity.y,
                                  ego_vehicle_velocity.z - pre_ego_vehicle_velocity.z)
        pre_ego_vehicle_velocity = ego_vehicle_velocity
        write_to_file(DEBUG_LOG_PATH + "debug_log_" + file_name, str(delta_velocity)+"\n")
        data = str(frame) + "," + str((datetime.utcnow() - start_time_in_real_world).total_seconds()) + "," + str(elapsed_seconds) + "," + \
               str(delta_seconds) + "," + str(platform_timestamp)
        for i in range(5):
            if rec_choice[i]:
                data += ", " + REC_FUNC[i](ego_vehicle)
        data += "\n"
        write_to_file(ABSOLUTE_PATH+file_name, data)
        
        world.tick()
    return None


# wraper of the main loop and handles trivials
def run_once(ego_vehicle:Actor, throttle:float, steer:float, \
            rec_choice = [{"rec_velocity":True}, {"rec_location":True}, \
                          {"rec_rotation":True}, {"rec_acceleration":True}, \
                          {"rec_angular_velocity":True}]) -> None:
    ego_vehicle.show_debug_telemetry(True)
    data = "frame, real_world_time_stamp, elapsed_seconds, delta_seconds, platform_timestamp"
    for i in range(5):
        if rec_choice[i]:
            data += ", "
            data += HEADER[i]
    data += "\n"
    spectator = world.get_spectator()
    file_name = create_file_name(throttle, steer)
    write_to_file(ABSOLUTE_PATH+file_name, data)
    loop(throttle, steer, ego_vehicle, spectator, file_name, rec_choice)
    return None

    
rec_choice = [1, 1, 0, 1, 1]
throttle = 0.99
steer = 0.0
run_once(ego_vehicle, throttle, steer, rec_choice)



# https://softhints.com/increase-cell-width-jupyter-notebook/

# from IPython.display import display, HTML
# display(HTML("<style>.container { width:100% !important; }</style>"))


# import psutil
# import subprocess
# import sys
# import time

#     def poll_gpus(self, flatten=False):
#         """
#         Query GPU utilisation, and sanitise results

#         Returns
#         -------
#         list of lists of utilisation stats
#             For each GPU (outer list), there is a list of utilisations
#             corresponding to each query (inner list), as a string.
#         """
#         res = subprocess.check_output(
#             ['nvidia-smi',
#              '--query-gpu=' + self.gpu_query,
#              '--format=csv,nounits,noheader']
#             )
#         lines = [i_res for i_res in res.decode().split('\n') if i_res != '']
#         data = [[val.strip() if 'Not Supported' not in val else 'N/A'
#                  for val in line.split(',')
#                  ] for line in lines]
#         if flatten:
#             data = [y for row in data for y in row]
#         return data


#     def poll_cpu(self):
#         """
#         Fetch current CPU, RAM and Swap utilisation

#         Returns
#         -------
#         float
#             CPU utilisation (percentage)
#         float
#             RAM utilisation (percentage)
#         float
#             Swap utilisation (percentage)
#         """
#         return (
#             psutil.cpu_percent(),
#             psutil.virtual_memory().percent,
#             psutil.swap_memory().percent,
#             )