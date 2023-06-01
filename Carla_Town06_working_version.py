import math
import carla
from carla import Actor
from carla import Vector3D
from datetime import date
from datetime import datetime


###
# CONSTANT VARIABLES
###
RELATIVE_PATH = "./output_data/"
ABSOLUTE_PATH = "~/CarlaTable/rawData/"
DELTA_V_CAP = 1e-5
DELTA_T = 0.02


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
ego_vehicle_spawn_point = carla.Transform(carla.Location(x=-272, y=-18, z=0.281494), \
                                          carla.Rotation(pitch=0.000000, yaw=0.0, roll=0.000000))
ego_vehicle = world.spawn_actor(blueprint_library.find('vehicle.tesla.model3'), ego_vehicle_spawn_point)
# ego_vehicle = world.spawn_actor(blueprint_library.find('vehicle.ford.mustang'), ego_vehicle_spawn_point)


# sets the camera to focus on ego_vehicle
def setSpectator(ego_vehicle:Actor, spectator:Actor) -> None:
    spectator_transform = ego_vehicle.get_transform()
    spectator.set_transform(carla.Transform(spectator_transform.location + \
                            carla.Location(x=0, y=0,z=30), carla.Rotation(pitch=-90)))

    
# return True if ego vehicle is moving at constant velocity
def is_at_const_speed(ego_vehicle:Actor, pre_ego_vehicle_velocity:Vector3D) -> bool:
    ego_vehicle_velocity = ego_vehicle.get_velocity()
    return ((abs(ego_vehicle_velocity.x - pre_ego_vehicle_velocity.x) <= DELTA_V_CAP) & \
            (abs(ego_vehicle_velocity.y - pre_ego_vehicle_velocity.y) <= DELTA_V_CAP) & \
            (abs(ego_vehicle_velocity.z - pre_ego_vehicle_velocity.z) <= DELTA_V_CAP))


# helper function, collects data to be recorded
def get_vehicle_info(ego_vehicle:Actor) -> str:
    ego_vehicle_velocity = ego_vehicle.get_velocity()
    ego_vehicle_transform = ego_vehicle.get_transform()
    ego_vehicle_location = ego_vehicle_transform.location
    ego_vehicle_rotation = ego_vehicle_transform.rotation  # pitch-y, yaw-z, roll-x
    ego_vehicle_velocity_data = str(ego_vehicle_velocity.x) + "," \
                              + str(ego_vehicle_velocity.y) + "," \
                              + str(ego_vehicle_velocity.z)
    ego_vehicle_location_data = str(ego_vehicle_location.x) + "," \
                              + str(ego_vehicle_location.y) + "," \
                              + str(ego_vehicle_location.z)
    ego_vehicle_rotation_data = str(ego_vehicle_rotation.pitch) + "," \
                              + str(ego_vehicle_rotation.yaw) + "," \
                              + str(ego_vehicle_rotation.roll)
    data = ego_vehicle_velocity_data + "," + ego_vehicle_location_data + "," + ego_vehicle_rotation_data
    return data


# return name of the file that raw data will write to  
def create_file_name(ego_vehicle_throttle:float, ego_vehicle_steer:float) -> str:
    today = date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    file_name = RELATIVE_PATH + "raw_data_throttle=" + str(ego_vehicle_throttle) + "_steer=" \
                + str(ego_vehicle_steer) + "_" + str(today) + "_" + str(current_time) +".csv"
    return file_name

def write_to_file(file_name:str, data:str) -> None:
    f = open(file_name, "a")
    f.write(data)
    f.close()
    return None

# main loop where all key actions take place
def loop(throttle:float, steer:float, ego_vehicle:Actor, spectator:Actor, file_name:str) -> None:
    data = ""
    # initialization
    pre_ego_vehicle_velocity = carla.Vector3D(0.0, 0.0, 0.0)
    frame_zero = world.get_snapshot().frame
    at_const_speed = False
    elapsed_seconds = 0.0
    while True:
#     while (elapsed_seconds <= 100) & (not at_const_speed):
        setSpectator(ego_vehicle, spectator)
        
        ego_vehicle_throttle = throttle
        ego_vehicle_steer = steer
        ego_vehicle.apply_control(carla.VehicleControl(throttle=ego_vehicle_throttle, steer=ego_vehicle_steer))
        
        vehicle_info = get_vehicle_info(ego_vehicle)
        
        snapshot = world.get_snapshot()
        frame = snapshot.frame - frame_zero
        elapsed_seconds = snapshot.elapsed_seconds
        delta_seconds = snapshot.delta_seconds
        platform_timestamp = snapshot.platform_timestamp
        
        data = str(frame) + "," + str(elapsed_seconds) + "," + str(delta_seconds) + "," + \
                str(platform_timestamp) + "," + str(vehicle_info) + "\n"
        print(elapsed_seconds)
        at_const_speed = is_at_const_speed(ego_vehicle, pre_ego_vehicle_velocity)
        write_to_file(file_name, data)
        world.tick()
    return None


# wraper of the main loop and handles trivials
def run_once(ego_vehicle:Actor, throttle:float, steer:float) -> None:
    spectator = world.get_spectator()
    data = "frame, elapsed_seconds, delta_seconds, platform_timestamp, \
            speed_x, speed_y, speed_z, \
            location_x, location_y, location_z, pitch, yaw, roll \n"
    file_name = create_file_name(throttle, steer)
    write_to_file(file_name, data)
    loop(throttle, steer, ego_vehicle, spectator, file_name)
    return None

    
    
run_once(ego_vehicle, throttle=0.15, steer=0)