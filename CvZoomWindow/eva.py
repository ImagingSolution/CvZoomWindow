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

# ズーム
for i in range(10):
    zw.zoom(1.1)
    zw.waitKey(10)

zw.waitKey()

# パン（平行移動）
for i in range(10):
    zw.zoom(1/1.1)
    zw.waitKey(10)

for i in range(10):
    zw.pan(50, 0)
    zw.waitKey(10)

for i in range(10):
    zw.pan(0, 50)
    zw.waitKey(10)

for i in range(10):
    zw.pan(-50, -50)
    zw.waitKey(10)   

zw.waitKey()

def mouse_callback(obj, event, w_x, w_y, flags, params, img_x, img_y):
    print(event, w_x, w_y, flags, params, img_x, img_y)

zw.set_mouse_callback(mouse_callback)

zw.waitKey()




