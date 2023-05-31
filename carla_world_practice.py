# import carla

# print("import carla success")

# import sys

# print(sys.version)

# import carla
# import random

# # ./CarlaUE4.sh -quality-level=Low
# # ./CarlaUE4.sh -quality-level=epic
# # ./CarlaUE4.sh -RenderOffScreen


# # Connect to the client and retrieve the world object
# client = carla.Client('localhost', 2000)
# world = client.get_world()


# # Setting synchronous mode
# # By default, CARLA runs in asynchronous mode.
# # Synchronous mode must be enabled before loading or reloading the world: 
# # Differing timestamps can arise if the world is not in synchronous mode 
# # from the very beginning. This can generate small differences in physics 
# # simulation and in the life cycle of objects such as traffics lights.
# settings = world.get_settings()
# settings.synchronous_mode = True # Enables synchronous mode
# settings.fixed_delta_seconds = 0.02 # (default is 0.05)
# world.apply_settings(settings)

# # set no_rendering_mode
# settings = world.get_settings()
# settings.no_rendering_mode = True
# world.apply_settings(settings)
# # settings.no_rendering_mode = False
# # world.apply_settings(settings)

# #imoprt map
# client.load_world('Town01')


# # get blueprint
# level = world.get_map()
# weather = world.get_weather()
# blueprint_library = world.get_blueprint_library()

# step = 0
# while step <= 10:
#     world.tick()
#     print(step)
#     step += 1
    
# # carla.terminate() ???

import carla
import random

# Connect to the client and retrieve the world object
client = carla.Client('localhost', 2000)
# load map
# NOTE: It is critical to load_world FIRST before
# calling "world = cliend.get_world()"
client.load_world('Town01')
world = client.get_world()
settings = world.get_settings()

# set rendering mode
# settings.no_rendering_mode = True

settings.synchronous_mode = True # Enables synchronous mode
settings.fixed_delta_seconds = 0.05 # (default is 0.05)

world.apply_settings(settings)


# get blueprint
level = world.get_map()
weather = world.get_weather()
blueprint_library = world.get_blueprint_library()

# Get the blueprint library and filter for the vehicle blueprints
vehicle_blueprints = world.get_blueprint_library().filter('*vehicle*')

# Get the map's spawn points
spawn_points = world.get_map().get_spawn_points()



# Spawn 50 vehicles randomly distributed throughout the map 
# for each spawn point, we choose a random vehicle from the blueprint library
# for i in range(0,10):
#     world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(spawn_points))


# print(spawn_points)
ego_vehicle_spawn_point = carla.Transform(carla.Location(x=151.119736, y=198.759842, z=0.299438), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
# ego_vehicle = world.spawn_actor(random.choice(vehicle_blueprints.filter('tesla')), ego_vehicle_spawn_point)
ego_vehicle = world.spawn_actor(blueprint_library.find('vehicle.tesla.model3'), ego_vehicle_spawn_point)
# ego_vehicle = world.spawn_actor(blueprint_library.find('vehicle.ford.mustang'), ego_vehicle_spawn_point)

from datetime import date
from datetime import datetime

today = date.today()
now = datetime.now()
current_time = now.strftime("%H:%M:%S")






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
spectator = world.get_spectator()

elapsed_seconds = 0.0
data = "frame, elapsed_seconds, delta_seconds, platform_timestamp, speed_x, speed_y, speed_z \n"
frame_zero = world.get_snapshot().frame

while elapsed_seconds <=20.0:    
    transform = ego_vehicle.get_transform()
    spectator.set_transform(carla.Transform(transform.location + carla.Location(x=0, y=0,z=30), \
                                            carla.Rotation(pitch=-90)))
#     print(transform)
#     ego_vehicle.set_autopilot(True)
    ego_vehicle_throttle = 1
    ego_vehicle_steer = 0.0
    ego_vehicle.apply_control(carla.VehicleControl(throttle=ego_vehicle_throttle, steer=ego_vehicle_steer))
    v = ego_vehicle.get_velocity()
    snapshot = world.get_snapshot()
    
    frame = snapshot.frame - frame_zero
    elapsed_seconds =snapshot.elapsed_seconds
    delta_seconds = snapshot.delta_seconds
    platform_timestamp = snapshot.platform_timestamp
    
    data += str(frame) + "," + str(elapsed_seconds) + "," + str(delta_seconds) + "," + \
            str(platform_timestamp) + "," + str(v.x) + "," + str(v.y) + "," + str(v.z) + "\n"
    print(elapsed_seconds)
    world.tick()
    
file_name = "./raw_data_throttle_" + str(ego_vehicle_throttle) + "_steer_" \
            + str(ego_vehicle_steer) + str(today) + str(now) +".csv"
f = open(file_name, "w")
f.write(data)
f.close()


# 3 ways to write to csv file
# https://stackoverflow.com/questions/37289951/how-to-write-to-a-csv-line-by-line

# ##text=List of strings to be written to file
# with open('csvfile.csv','wb') as file:
#     for line in text:
#         file.write(line)
#         file.write('\n')


# import csv

# with open(<path to output_csv>, "wb") as csv_file:
#         writer = csv.writer(csv_file, delimiter=',')
#         for line in data:
#             writer.writerow(line)


# f = open('csvfile.csv','w')
# f.write('hi there\n') #Give your csv text here.
# ## Python will convert \n to os.linesep
# f.close()



# get date

# from datetime import date

# today = date.today()
# print("Today's date:", today)


# Method 1

# from datetime import datetime

# now = datetime.now()

# current_time = now.strftime("%H:%M:%S")
# print("Current Time =", current_time)


# Method 2

# import time

# t = time.localtime()
# current_time = time.strftime("%H:%M:%S", t)
# print(current_time)



# example 
# from datetime import datetime
# import pytz

# # Get the timezone object for New York
# tz_NY = pytz.timezone('America/New_York') 

# # Get the current time in New York
# datetime_NY = datetime.now(tz_NY)

# # Format the time as a string and print it
# print("NY time:", datetime_NY.strftime("%H:%M:%S"))

# # Get the timezone object for London
# tz_London = pytz.timezone('Europe/London')

# # Get the current time in London
# datetime_London = datetime.now(tz_London)

# # Format the time as a string and print it
# print("London time:", datetime_London.strftime("%H:%M:%S"))






# town = 'Town0'
# num = 1
# for i in range(5):
#     mapname = town+str(num+i)
#     print(mapname)
#     client.load_world(mapname)


#     # get blueprint
#     level = world.get_map()
#     weather = world.get_weather()
#     blueprint_library = world.get_blueprint_library()

#     step = 0
#     while step <= 10:
#         world.tick()
#         print(step)
#         step += 1

# carla.terminate()