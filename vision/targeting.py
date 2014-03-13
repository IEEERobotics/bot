"""Target_detect.py
Authored by Rahul Krishna. Updated 3-11-14.
Works with Micrsoft lifecam VX-5000.
Detects all squares in the image, returns pixel locations of square vertices.
Can open a window to display detected target; this is disabled by default.
"""
# TODO: Update documentation to better reflect overall function

import lib.lib as lib

import sys
import numpy as np
import cv2
import cv


# TODO: Remove these parameter definitions as they are already in cv2 or cv2.cv
# Define camera parameters
CV_CAP_PROP_POS_MSEC = 0
CV_CAP_PROP_POS_FRAMES = 1
CV_CAP_PROP_POS_AVI_RATIO = 2
CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4
CV_CAP_PROP_FPS = 5
CV_CAP_PROP_POS_FOURCC = 6
CV_CAP_PROP_POS_FRAME_COUNT = 7
CV_CAP_PROP_BRIGHTNESS = 8
CV_CAP_PROP_CONTRAST = 9
CV_CAP_PROP_SATURATION = 10
CV_CAP_PROP_HUE = 11
CV_CAP_PROP_AUTO_EXPOSURE = 12

CV_CAPTURE_PROPERTIES = tuple({
    CV_CAP_PROP_POS_MSEC,
    CV_CAP_PROP_POS_FRAMES,
    CV_CAP_PROP_POS_AVI_RATIO,
    CV_CAP_PROP_FRAME_WIDTH,
    CV_CAP_PROP_FRAME_HEIGHT,
    CV_CAP_PROP_FPS,
    CV_CAP_PROP_POS_FOURCC,
    CV_CAP_PROP_POS_FRAME_COUNT,
    CV_CAP_PROP_BRIGHTNESS,
    CV_CAP_PROP_CONTRAST,
    CV_CAP_PROP_SATURATION,
    CV_CAP_PROP_HUE,
    CV_CAP_PROP_AUTO_EXPOSURE})

CV_CAPTURE_PROPERTIES_NAMES = [
    "CV_CAP_PROP_POS_MSEC",
    "CV_CAP_PROP_POS_FRAMES",
    "CV_CAP_PROP_POS_AVI_RATIO",
    "CV_CAP_PROP_FRAME_WIDTH",
    "CV_CAP_PROP_FRAME_HEIGHT",
    "CV_CAP_PROP_FPS",
    "CV_CAP_PROP_POS_FOURCC",
    "CV_CAP_PROP_POS_FRAME_COUNT",
    "CV_CAP_PROP_BRIGHTNESS",
    "CV_CAP_PROP_CONTRAST",
    "CV_CAP_PROP_SATURATION",
    "CV_CAP_PROP_HUE",
    "CV_CAP_PROP_AUTO_EXPOSURE"]


def angle_cos(p0, p1, p2):
    """Find the cosine of the angle between two vectors.

    Vectors specified by points: (p1 to p0) and (p1 to p2)

    """
    d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))


class TargetLocator(object):
    """A visual target locator for IEEE SECon 2014 hardware comp."""

    default_device = 0  # device number (0 is first), or recorded video file
    default_width, default_height = (320, 240)  # default image size
    default_auto_exposure = 5.0  # NOTE: needs to be calibrated

    min_contour_area = 1000  # minimum pixel area contours to be considered

    def __init__(self, device=default_device):
        # * Load system configuration
        self.config = lib.get_config()

        # * Get and store logger object
        self.logger = lib.get_logger()

        # * Initialize members
        # ** Inpute device (will be set later in __init__)
        self.capture = None
        self.width = 0
        self.height = 0
        self.auto_exposure = 1.0

        # ** Image processing
        self.imageIn = None  # input image
        self.res = None  # result/output image (TODO: use separate imageOut)
        self.squares = []  # list of squares found

        # *** Morphology kernel
        self.kernel_rect = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        self.kernel_fat_cross = np.uint8([
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 0, 0]])  # custom morph kernel: fat cross
        self.kernel_inv_cross = np.uint8([
            [1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 0, 1, 1, 1]])  # custom morph kernel: inverted cross

        self.kernel = self.kernel_inv_cross  # pick kernel that works best
        self.logger.debug("Morph. kernel: {}".format(self.kernel))

        # ** Final output
        self.location = None  # target location

        # Open default input device (camera)
        if self.open_device(device):
            self.logger.info("Opened device: {}".format(device))
        else:
            self.logger.error("Failed to open device: {}".format(device))

        # Set initial camera parameters (NOTE: may crash with recorded video)
        self.set_frame_size()  # use defaults
        self.set_auto_exposure()  # use defaults

    def open_device(self, device=0):
        # Open input device [API: cv]
        self.capture = cv.CaptureFromCAM(0)
        return self.capture is not None

    def close_device(self):
        self.capture = None
        #del self.capture  # NOTE: is this required?

    def get_frame_size(self):
        return self.width, self.height  # NOTE: query device?

    def set_frame_size(self, width=default_width, height=default_height):
        # Set camera frame size [API: cv]
        if self.capture is not None:
            self.width = width
            self.height = height
            cv.SetCaptureProperty(
                self.capture, CV_CAP_PROP_FRAME_WIDTH, self.width)
            cv.SetCaptureProperty(
                self.capture, CV_CAP_PROP_FRAME_HEIGHT, self.height)

    def get_auto_exposure(self):
        return self.auto_exposure  # NOTE: query device?

    def set_auto_exposure(self, value=default_auto_exposure):
        # Set camera's auto-exposure value [API: cv]
        if self.capture is not None:
            self.auto_exposure = value
            cv.SetCaptureProperty(
                self.capture, CV_CAP_PROP_AUTO_EXPOSURE, self.auto_exposure)

    # TODO: @lib.api_call?
    def find_target(self):
        """Find target location in current camera image."""
        if self.capture is None:
            return self.location  # no input, can't do anything!

        # Capture camera frame [API: cv]
        img = cv.QueryFrame(self.capture)
        self.imageIn = np.asarray(img[:, :], dtype=np.uint8)
        # TODO: check cv to cv2 conversion; use cv2 API from here on?

        # Call appropriate internal work-horse method
        self._find_target_squares(img)
        if self.location is not None:
            self.logger.info(
                "Target @ (%6.2f, %6.2f)", self.location[0], self.location[1])

        # Return location (NOTE: must be set by internal method)
        return self.location

    def _find_target_squares(self, img):
        """Find target location using the squares method."""
        # Create compatible intermediate images
        col_edge = cv.CreateImage((img.width, img.height), 8, 3)
        dst = cv.CreateImage(cv.GetSize(img), 8, 1)
        color_dst = cv.CreateImage(cv.GetSize(img), 8, 3)
        storage = cv.CreateMemStorage(0)

        # Convert to grayscale
        gray = cv.CreateImage((img.width, img.height), 8, 1)
        edge = cv.CreateImage((img.width, img.height), 8, 1)
        hsv = cv2.cvtColor(np.asarray(img[:, :]), cv2.COLOR_BGR2HSV)
        # NOTE: This converts from cv-style image to cv2-style image

        # TODO: Move the following block to __init__()
        # Define range of Red color in HSV
        # working Range [0 64 55], [24 255 255] and [163 64 55] [179 255 255]
        # See wiki to see what the values mean.
        # Basically, changing the first element changes the RED limit

        # If red values look unsatisfactory, there are two thing you could do:
        # 1. Extend RED range.
        #   Increase the value of the first element in upper_red array
        #   (the default is 12) or (and) decrease first element in lower_red1.
        # 2. To compensate for lighting effect, decrease the last element of
        #   lower_red and lower_red1 array.

        lower_red = np.array([0, 64, 55], dtype=np.uint8)
        upper_red = np.array([12, 255, 255], dtype=np.uint8)

        lower_red1 = np.array([169, 64, 55], dtype=np.uint8)
        upper_red1 = np.array([179, 255, 255], dtype=np.uint8)

        # Threshold the image to get only Red color
        mask1 = cv2.inRange(hsv, lower_red, upper_red)
        mask2 = cv2.inRange(hsv, lower_red1, upper_red1)

        # Perform an OR operation to get the FINAL MASK, morph to smooth
        mask3 = np.bitwise_or(mask1, mask2)
        mask = cv2.morphologyEx(mask3, cv2.MORPH_CLOSE, self.kernel)
        #mask = cv2.dilate(mask3, self.kernel, iterations=1)

        # Bitwise-AND mask and original image to extract the target
        self.res = cv2.bitwise_and(
            np.asarray(img[:, :]), np.asarray(img[:, :]),
            mask=np.asarray(mask[:, :]))

        # Squares is the array that has the pixel locations of the vertices
        self.squares = self.find_squares(self.res)
        if self.squares:
            self.logger.debug("%d squares", len(self.squares))
            #print "Squares: {}".format(self.squares)  # [verbose]

            # Process squares array and set self.location to (x, y) pair
            centroids = []
            for square in self.squares:
                # TODO: Reject this square if aspect ratio is too skewed
                centroid = np.mean(square, axis=0)
                centroids.append(centroid)  # TODO: faster numpy way?
            centroids = np.array(centroids)
            #print "Centroids:", centroids  # [verbose]
            mean_centroid = np.mean(centroids, axis=0)  # 2D mean
            sd_centroid = np.std(centroids, axis=0)  # 2D standard deviation
            #print "Mean:", mean_centroid, ", s.d.:", sd_centroid  # [verbose]

            good_centroids = centroids[np.all(
                np.abs(centroids - mean_centroid) <= (1.2 * sd_centroid),
                axis=1)]
            #print "Good:", good_centroids  # [verbose]

            # TODO: Reject all if s.d. is greater than half of mean side length

            if good_centroids.size > 0:
                self.location = np.mean(good_centroids, axis=0)
                return  # don't fall-through and return None!

        self.location = None  # None if target not found

    def find_squares(self, img):
        """Find and return all squares in given (thresholded) image."""
        img = cv2.GaussianBlur(img, (5, 5), 0)
        squares = []
        for gray in cv2.split(img):  # NOTE: iterate over R, G and B planes?
            for thrs in xrange(0, 255, 26):  # NOTE: so many thresholds reqd.?
                # Compute binary image (canny-dilate/threshold)
                if thrs == 0:
                    binary = cv2.Canny(gray, 0, 50, apertureSize=5)
                    binary = cv2.dilate(binary, None)
                    # NOTE: We should probably dilate after threshold as well
                else:
                    retval, binary = cv2.threshold(
                        gray, thrs, 255, cv2.THRESH_BINARY)

                # Find contours (NOTE: repeating this many times can be slow)
                contours, hierarchy = cv2.findContours(
                    binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

                # Iterate over contours, find ones which look like squares
                for cnt in contours:
                    cnt_len = cv2.arcLength(cnt, True)
                    cnt = cv2.approxPolyDP(cnt, 0.02 * cnt_len, True)
                    if (len(cnt) == 4 and
                            cv2.contourArea(cnt) > self.min_contour_area and
                            cv2.isContourConvex(cnt)):  # TODO: max area?
                        cnt = cnt.reshape(-1, 2)
                        max_cos = np.max(
                            [angle_cos(cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4])
                                for i in xrange(4)])
                        if max_cos < 0.1:
                            squares.append(cnt)
        return squares

    def display_input(self):
        if self.imageIn is not None:
            cv2.imshow("Input", self.imageIn)

    def display_output(self):
        # Display squares found in image (NOTE: this draws on res image)
        if self.squares:
            cv2.drawContours(self.res, self.squares, -1, (0, 255, 0), 3)
            # Paint target, if located
            if self.location is not None:
                cv2.circle(
                    self.res, (int(self.location[0]), int(self.location[1])),
                    3, (0, 255, 255), -1)
        cv2.imshow("Output", self.res)  # NOTE: someone needs to call waitKey

    def clean_up(self):
        self.close_device()


def runTargetLocator(device=TargetLocator.default_device, gui=False):
    """A standalone driver for testing TargetLocator."""

    targetLocator = TargetLocator(device)
    print "run(): Starting main loop Ctrl+C here or Esc on image to quit..."
    while True:
        try:
            loc = targetLocator.find_target()
            if loc is not None:
                x, y = loc[0], loc[1]  # test unpacking
                #print "run(): (x, y) = ({:6.2f}, {:6.2f})".format(x, y)

            if gui:
                targetLocator.display_input()
                targetLocator.display_output()
                key = cv.WaitKey(10)
                if key == 0x1b:
                    break
                key &= 0xff  # use lower 8 bits only
                if key == ' ':
                    print "run() [PAUSED] Press any key to continue..."
                    cv2.waitKey()
                    print "run() [RESUMED]"

        except KeyboardInterrupt:
            break

    targetLocator.clean_up()
    print "run(): Done."


if __name__ == "__main__":
    runTargetLocator(
        sys.argv[1] if len(sys.argv) > 1 else TargetLocator.default_device,
        gui=True)
