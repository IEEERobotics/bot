"""Bot controller client that uses the Leap Motion device."""
# Based on Sample.py included with LeapSDK 0.8.0

import sys
import time
from collections import namedtuple

try:
    import Leap
    # NOTE Gestures are currently disabled; we could use a tap gesture to fire?
except:
    sys.stderr.write("ERROR: This module cannot be run without the Leap SDK")
    raise

ControlRange = namedtuple('ControlRange',
                          ['min', 'zero_min', 'zero_max', 'max'])
pitchRange = ControlRange(-30.0, -10.0, 10.0, 30.0)  # -ve is forward
rollRange = ControlRange(-30.0, -10.0, 10.0, 30.0)  # -ve is to the right
yawRange = ControlRange(-30.0, -10.0, 10.0, 30.0)  # -ve is to the left


class LeapClient(Leap.Listener, client.Client):

    """Translates Leap Motion input to commands, sends to a control server.

    TODO: Maintain state using on_connect(), on_disconnect()?

    """

    def on_init(self, controller):
        """Build logger, connect to ZMQ server.

        :param controller: Leap controller object.

        """
        client.Client.__init__(self)
        self.isProcessing = False  # Semaphore to prevent asynchronous clashes

    def on_connect(self, controller):
        """Not much going on, just log that we're connected.

        :param controller: Leap controller object.

        """
        self.logger.info("Connected to Leap device")

    def on_disconnect(self, controller):
        """Not much going on, just log that we're disconnected.

        :param controller: Leap controller object.

        """
        # NOTE: not dispatched when running in a debugger.
        self.logger.info("Disconnected from Leap device")

    def on_exit(self, controller):
        """Close connection to ZMQ server.

        :param controller: Leap controller object.

        """
        self.cleanUp()

    def on_frame(self, controller):
        """Process Leap update, send control message to bot.

        :param controller: Leap controller object.

        """
        if self.isProcessing:
            return
        self.isProcessing = True  # Lock

        frame = controller.frame()  # Get the most recent frame

        forward = 0.
        strafe = 0.
        turn = 0.

        if not frame.hands.is_empty:
            hand = frame.hands[0]  # Get the first hand
            fingers = hand.fingers  # Get list of fingers on this hand
            # NOTE: Useful hand properties: hand.sphere_radius,
            #   hand.palm_position, hand.palm_normal, hand.direction

            # Proceed only if 3 or more fingers are seen and other
            #   criteria met (to prevent flaky behavior)
            position = hand.palm_position
            position[0] # x
            position[1] # y
            position[2] # z
            # TODO Use a state machine to prevent abrupt changes
            # Max hand height (z-position), min fingers; TODO other filters
            if z <= 40 and len(fingers) >= 3:
                # Calculate the hand's pitch, roll, and yaw angles
                pitch = hand.direction.pitch * Leap.RAD_TO_DEG
                roll = hand.palm_normal.roll * Leap.RAD_TO_DEG
                yaw = hand.direction.yaw * Leap.RAD_TO_DEG

                # Compute control values based on position and orientation
                # * Scheme 1: pitch = forward/backward vel.,
                #   roll = left/right strafe vel., yaw = left/right turn vel.
                forward = self.pitch_to_fwd(pitch)
                strafe = self.roll_to_strafe(roll)
                turn = self.yaw_to_turn(yaw)

        # Send control values as command to server (TODO perhaps at a
        #   reduced frequency? use GCode-like conventions?)
        # TODO move this to a different thread
        if forward != 0 or strafe != 0 or turn != 0:
            self.send_fwd_strafe_turn(forward, strafe, turn)
        self.isProcessing = False  # release

    def pitch_to_fwd(self, pitch):
        """Convert sensed pitch value to a forward speed.

        :param pitch: Sensed pitch of hand, used to get forward speed.
        :type pitch: float
        :returns: Forward speed of robot corresponding to given pitch.

        """
        # If pitch is outside deadband (zero span)
        if pitch <= pitchRange.zero_min or pitchRange.zero_max <= pitch:
            # Clamp pitch to [min, max] range
            if pitch < pitchRange.min:
                pitch = pitchRange.min
            elif pitch > pitchRange.max:
                pitch = pitchRange.max

            # Compute forward velocity as ratio of current pitch to pitch range
            if pitch < 0:
                # forward: +ve
                return (pitch - pitchRange.zero_min) / \
                       (pitchRange.min - pitchRange.zero_min)
            else:
                # backward: -ve
                return -(pitch - pitchRange.zero_max) / \
                        (pitchRange.max - pitchRange.zero_max)

    def roll_to_strafe(self, roll):
        """Convert sensed roll value to a strafe speed.

        :param roll: Sensed roll of hand, used to get strafe speed.
        :type roll: float
        :returns: Strafe speed of robot corresponding to given roll.

        """
        # If roll is outside deadband (zero span)
        if roll <= rollRange.zero_min or rollRange.zero_max <= roll:
            # Clamp roll to [min, max] range
            if roll < rollRange.min:
                roll = rollRange.min
            elif roll > rollRange.max:
                roll = rollRange.max

            # Compute strafe velocity as ratio of current roll to roll range
            if roll < 0:
                # Strafe left: -ve
                return (roll - rollRange.zero_min) / \
                       (rollRange.min - rollRange.zero_min)
            else:
                # Strafe right: +ve
                return -(roll - rollRange.zero_max) / \
                        (rollRange.max - rollRange.zero_max)

    def yaw_to_turn(self, yaw):
        """Convert sensed yaw value to a turn speed.

        :param yaw: Sensed yaw of hand, used to get turn speed.
        :type yaw: float
        :returns: Turn speed of robot corresponding to given yaw.

        """
        # If yaw is outside deadband (zero span)
        if yaw <= yawRange.zero_min or yawRange.zero_max <= yaw:
            # Clamp yaw to [min, max] range
            if yaw < yawRange.min:
                yaw = yawRange.min
            elif yaw > yawRange.max:
                yaw = yawRange.max

            # Compute turn velocity as ratio of current yaw to
            #   yaw range (TODO check sign convention)
            if yaw < 0:
                # Turn left: +ve
                return (yaw - yawRange.zero_min) / \
                       (yawRange.min - yawRange.zero_min)
            else:
                # Turn right: -ve
                return -(yaw - yawRange.zero_max) / \
                        (yawRange.max - yawRange.zero_max)


def main():
    """Build/start our Leap client and general Leap controller."""
    # Create a custom listener and Leap Motion controller
    leapClient = LeapClient()
    leapController = Leap.Controller()

    # Have the listener receive events from the controller
    leapController.add_listener(leapClient)
    time.sleep(0.5)  # Yield so that on_connect() can happen first

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."  # [info]
    sys.stdin.readline()

    # Remove the sample listener when done
    leapController.remove_listener(leapClient)


if __name__ == "__main__":
    main()
