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
    cv2.waitKey(10)

cv2.waitKey()

for i in range(10):
    zw.zoom(1/1.1)
    cv2.waitKey(10)

# パン（平行移動）
for i in range(10):
    zw.pan(50, 0)
    cv2.waitKey(10)

for i in range(10):
    zw.pan(0, 50)
    cv2.waitKey(10)

for i in range(10):
    zw.pan(-50, -50)
    cv2.waitKey(10)   

cv2.waitKey()

print("zoom_fit")
zw.zoom_fit(256, 256)
cv2.waitKey()


point = zw.image_to_window_point(0, 0)
print(point)
point = zw.window_to_image_point(point[0], point[1])
print(point)

def mouse_callback(obj, event, w_x, w_y, flags, params, img_x, img_y, scale):
    print(event, w_x, w_y, flags, params, img_x, img_y, scale)


zw.set_mouse_callback(mouse_callback)

cv2.waitKey()




