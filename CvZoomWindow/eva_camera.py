import cv2

import cvzoomwindow


# Zoom Windowの作成
zw = cvzoomwindow.CvZoomWindow("Zoom Window")

zw.zoom_fit(640, 480)

# カメラを開く
cap = cv2.VideoCapture(0)

while True:
    # 画像をキャプチャする
    ret, frame = cap.read()

    # 画像を表示する
    zw.imshow(frame, False)

    # `q`キーを押すとループを終了する
    if cv2.waitKey(1) == ord('q'):
        break

# カメラを閉じる
cap.release()
# すべてのウィンドウを閉じる
cv2.destroyAllWindows()