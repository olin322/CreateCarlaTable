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
blueprint_library = woret_spectatld.get_blueprint_library()

# Get the blueprint library and filter for the vehicle blueprints
vehicle_blueprints = world.get_blueprint_library().filter('*vehicle*')

# Get the map's spawn points
spawn_points = world.get_map().get_spawn_points()
# print(spawn_points)
ego_vehicle_spawn_point = carla.Transform(carla.Location(x=151.119736, y=198.759842, z=0.299438), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
# ego_vehicle = world.spawn_actor(random.choice(vehicle_blueprints.filter('tesla')), ego_vehicle_spawn_point)
ego_vehicle = world.spawn_actor(blueprint_library.find('vehicle.tesla.model3'), ego_vehicle_spawn_point)
# ego_vehicle = world.spawn_actor(blueprint_library.find('vehicle.ford.mustang'), ego_vehicle_spawn_point)



def create_file_name(ego_vehicle_throttle:float, ego_vehicle_steer:float) -> str:
    today = date.today()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    file_name = RELATIVE_PATH + "raw_data_throttle=" + str(ego_vehicle_throttle) + "_steer=" \
                + str(ego_vehicle_steer) + "_" + str(today) + "_" + str(current_time) +".csv"
    return file_name



# # Create a transform to place the camera on top of the vehicle
# camera_init_trans = carla.Transform(carla.Location(z=1.5))

# # We create the camera through a blueprint that defines its properties
# camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')

# # We spawn the camera and attach it to our ego vehicle
# camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=ego_vehicle)

# # Start camera with PyGame callback
# camera.listen(lambda image: image.save_to_disk('out/%06d.png' % image.frame))


# for vehicle in world.get_actors().filter('*vehicle*'):
#     if vehicle != ego_vehicle:
#         vehicle.set_autopilot(True)


# Transform(Location(x=151.119736, y=198.759842, z=0.299438), Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))


def run_once(ego_vehicle:Actor, throttle: float, steer: float):
    spectator = world.get_spectator()
    elapsed_seconds = 0.0
    data = "frame, elapsed_seconds, delta_seconds, platform_timestamp, speed_x, speed_y, speed_z \n"
    frame_zero = world.get_snapshot().frame
    velocity_pre_frame = carla.Vector3D(0.0, 0.0, 0.0)
    ### TO-DO
    ### exit condition needs to update
    ### exit when vehicle move at constant speed
    while elapsed_seconds <=100.0:
        transform = ego_vehicle.get_transform()
        spectator.set_transform(carla.Transform(transform.location + \
                                carla.Location(x=0, y=0,z=30), \
                                carla.Rotation(pitch=-90)))

#         ego_vehicle.set_autopilot(True)
#         ego_vehicle_throttle = throttle
#         ego_vehicle_steer = steer
#         ego_vehicle.apply_control(carla.VehicleControl(throttle=ego_vehicle_throttle, steer=ego_vehicle_steer))
        
#         ego_vehicle_speed = ego_vehicle.get_velocity()
#         ego_vehicle_transform = ego_vehicle.get_transform()
#         ego_vehicle_location = ego_vehicle_transform.location
#         ego_vehicle_rotation = ego_vehicle_transform.rotation  # pitch-y, yaw-z, roll-x
        
        
        
#         snapshot = world.get_snapshot()
#         frame = snapshot.frame - frame_zeroat_const_speed = False
#         elapsed_seconds =snapshot.elapsed_seconds
#         delta_seconds = snapshot.delta_seconds
#         platform_timestamp = snapshot.platform_timestamp

#         data += str(frame) + "," + str(elapsed_seconds) + "," + str(delta_seconds) + "," + \
#                 str(platform_timestamp) + "," + \
#                 str(ego_vehicle_speed.x) + "," + str(ego_vehicle_speed.y) + "," + str(ego_vehicle_speed.z)\
#                 + "\n"
# #         print(elapsed_seconds)
#         world.tick()

def setSpectator(ego_vehicle:Actor) -> None:
    spectator_transform = ego_vehicle.get_transform()
    spectator.set_transform(carla.Transform(spectator_transform.location + \
                            carla.Location(x=0, y=0,z=30), carla.Rotation(pitch=-90)))


def loop(throttle:float, steer:float, ego_vehicle:Actor, spectator:Actor) -> None:
    velocity_pre_frame = carla.Vector3D(0.0, 0.0, 0.0)
    at_const_speed = False
    while !at_const_speed:
        
        setSpectator(ego_vehicle)
        ego_vehicle_throttle = throttle
        ego_vehicle_steer = steer
        ego_vehicle.apply_control(carla.VehicleControl(throttle=ego_vehicle_throttle, steer=ego_vehicle_steer))
        
        ego_vehicle_speed = ego_vehicle.get_velocity()
        ego_vehicle_transform = ego_vehicle.get_transform()
        ego_vehicle_location = ego_vehicle_transform.location
        ego_vehicle_rotation = ego_vehicle_transform.rotation  # pitch-y, yaw-z, roll-x
        
        
        snapshot = world.get_snapshot()
        frame = snapshot.frame - frame_zero
        elapsed_seconds =snapshot.elapsed_seconds
        delta_seconds = snapshot.delta_seconds
        platform_timestamp = snapshot.platform_timestamp

        data += str(frame) + "," + str(elapsed_seconds) + "," + str(delta_seconds) + "," + \
                str(platform_timestamp) + "," + \
                str(ego_vehicle_speed.x) + "," + str(ego_vehicle_speed.y) + "," + str(ego_vehicle_speed.z)\
                + "\n"
#         print(elapsed_seconds)
        world.tick()
    
    
    file_name = create_file_name(ego_vehicle_throttle, ego_vehicle_steer)
    f = open(file_name, "w")
    f.write(data)
    f.close()
