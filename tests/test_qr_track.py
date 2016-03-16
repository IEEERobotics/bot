mport bot.lib.lib as lib
from bot.hardware.complex_hardware.robot_arm import RobotArm
import time

ninety = [90]*5
config = lib.get_config()
arm_config = config["dagu_arm"]
arm = RobotArm(arm_config)
#arm.rail.DisplacementConverter(3)
arm.joint_center_on_qr()

