import cv2

import cvzoomwindow

# Image loading
img = cv2.imread("image.bmp")

# Instance of CvZoomWindow class
zw = cvzoomwindow.CvZoomWindow(
    "Zoom Window" # Name of the window 
    )

# Displays an image
zw.imshow(img)

# Waits for a pressed key.
cv2.waitKey()
