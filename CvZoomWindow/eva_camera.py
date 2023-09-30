import cv2

import cvzoomwindow


# Zoom Windowの作成
zw = cvzoomwindow.CvZoomWindow("Zoom Window")

# カメラを開く
cap = cv2.VideoCapture(0)

while True:
    # 画像をキャプチャする
    ret, frame = cap.read()

    # 画像を表示する
    zw.imshow(frame, False)

    # `q`キーを押すとループを終了する
    if zw.waitKey(1) == ord('q'):
        break

# カメラを閉じる
cap.release()
# すべてのウィンドウを閉じる
cv2.destroyAllWindows()