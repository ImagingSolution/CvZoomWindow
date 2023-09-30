# CvZoomWindow
CvNameWindow class that adds zoom and pan functions to OpenCV's namedWindow

![CvZoomWindow](https://github.com/ImagingSolution/CvZoomWindow/assets/29155364/b8ef1e5e-31ad-4735-9576-1efe370c01f0)

## Install

```
pip install cvzoomwindow
```



## Sample

```python
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
```



## How to operate

| mouse operation              | operation                    |
| ---------------------------- | ---------------------------- |
| Double click of left button  | Display the entire image     |
| Double click of right button | Equal-size display of images |
| Left button drag             | Moving Images                |
| Mouse wheel up               | Zoom up                      |
| Mouse wheel down             | Zoom down                    |



