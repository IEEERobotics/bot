"""Logic for line following."""

import lib.lib as lib
import lib.exceptions as ex


class Follower(object):

    """Follow a line. Subclass for specific hardware/methods."""

    def __init__(self):
        """Build and store logger."""
        self.logger = lib.get_logger()
        self.logger.debug("Follower has logger")

    def follow(self, cmd):
        """Accept and handle fire commands.

        TODO(dfarrell07): This is a stub

        :param cmd: Description of fire action to execute.

        """
        self.logger.debug("Follow cmd: {}".format(cmd))
        self.always_work(cmd)

    def always_work(self, cmd):
        """Temp method to simulate successful results.

        :param cmd: Command to successfully return from.
        :raises: FollowerException, IntersectionException, BoxException

        """
        if cmd["expected_result"] == str(ex.FollowerException()):
            raise ex.FollowerException()
        elif cmd["expected_result"] == str(ex.IntersectionException()):
            raise ex.IntersectionException()
        elif cmd["expected_result"] == str(ex.BoxException()):
            raise ex.BoxException()
        else:
            self.logger.error("Unknown follow expected_result: "
                              "{}".format(cmd["expected_result"]))
