import cv2

import cvzoomwindow

# テスト画像の生成
img = cv2.imread("image.bmp")

# Zoom Windowの作成
zw = cvzoomwindow.CvZoomWindow("Zoom Window")
# 画像の表示（Trueは画像全体を表示する）
zw.imshow(img, True)
# 実際に画像を表示する
cv2.waitKey()
