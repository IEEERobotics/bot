from bot.hardware.complex_hardware.camera_reader import Camera

import bot.lib.lib as lib


config = lib.get_config()

cam_model = config["dagu_arm"]["camera"]
print config[cam_model]

c = Camera(config[cam_model])


c.infinite_demo()
