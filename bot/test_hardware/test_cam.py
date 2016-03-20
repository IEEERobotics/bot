import cv2

cam = cv2.VideoCapture(0)



cam.set(3,300)
cam.set(4,400)

ret, frame = cam.read()

print "X: ", cam.get(3)
print "Y: ", cam.get(4)

print ret
print frame

cv2.imwrite('hd_cam.png', frame)
