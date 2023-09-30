import numpy as np
import cv2

import cvzoomwindow

# テスト画像の生成
#image = np.zeros((480, 640, 3), dtype = np.uint8)
image = np.zeros((480, 640), dtype = np.uint8)
cv2.line(image, (0, 0), (639, 479), (255, 255, 255), 3, cv2.LINE_AA)
cv2.line(image, (0, 479), (639, 0), (255, 255, 255), 3, cv2.LINE_AA)

# Zoom Windowの作成
zw = cvzoomwindow.CvZoomWindow("Zoom Window")
# 画像の表示（Trueは画像全体を表示する）
zw.imshow(image, True)
# 実際に画像を表示する
cv2.waitKey()
