__version__ = "0.0.1"

import cv2

from cvzoomwindow import affine

class CvZoomWindow:

    def __init__(self, winname, back_color = (128, 128, 0), inter = cv2.INTER_NEAREST):
        # Window Title
        self.__winname = winname        # namedWindowのタイトル
        self.__back_color = back_color  # 背景色
        self.__inter = inter            # 補間表示モード

        self.__src_image = None
        self.__disp_image = None
        self.__affine_matrix = affine.identityMatrix()
        self.__old_affine_matrix = affine.identityMatrix()

        self.__zoom_delta = 1.5
        self.__min_scale = 0.01
        self.__max_scale = 100

        self.__mouse_down_flag = False

        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)

        # コールバック関数の登録
        cv2.setMouseCallback(winname, self._onMouse, winname)

    def imshow(self, image, zoom_fit : bool = False):
        '''画像の表示

        Parameters
        ----------
        image : np.ndarray
            表示する画像データ
        zoom_fit : bool
            True : ウィンドウ全体に画像を表示する          
            False : ウィンドウ全体に画像を表示しない          
        '''

        if image is None:
            return

        self.__src_image = image

        if zoom_fit is True:
            self.zoom_fit()
        else:
            self.redraw_image()
            cv2.waitKey(1)            

    def redraw_image(self):
        '''画像の再描画
        '''

        if self.__src_image is None:
            return
        
        _, _, win_width, win_height = cv2.getWindowImageRect(self.__winname)

        self.__disp_image = cv2.warpAffine(self.__src_image, self.__affine_matrix[:2,], (win_width, win_height), flags = self.__inter, borderValue = self.__back_color)
        cv2.imshow(self.__winname, self.__disp_image)

    def zoom_fit(self):
        '''画像をウィジェット全体に表示させる'''

        if self.__src_image is None:
            return   

        # 画像表示領域のサイズ
        _, _, win_width, win_height = cv2.getWindowImageRect(self.__winname)
        # 画像のサイズ
        image_width = self.__src_image.shape[1]
        image_height = self.__src_image.shape[0]

        if (image_width * image_height <= 0) or (win_width * win_height <= 0):
            return

        # アフィン変換の初期化
        self.__affine_matrix = affine.identityMatrix()

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0

        if (win_width * image_height) > (image_width * win_height):
            # ウィジェットが横長（画像を縦に合わせる）
            scale = win_height / image_height
            # あまり部分の半分を中央に寄せる
            offsetx = (win_width - image_width * scale) / 2.0
        else:
            # ウィジェットが縦長（画像を横に合わせる）
            scale = win_width / image_width
            # あまり部分の半分を中央に寄せる
            offsety = (win_height - image_height * scale) / 2.0

        # 拡大縮小
        self.__affine_matrix[0, 0] = scale
        self.__affine_matrix[1, 1] = scale
        # あまり部分を中央に寄せる
        self.__affine_matrix = affine.translateMatrix(offsetx, offsety).dot(self.__affine_matrix)

        # 描画
        self.redraw_image()
        cv2.waitKey(1)    

    def destroyWindow(self):
        '''ウィンドウの削除
        '''
        cv2.destroyWindow(self.__winname)

    def waitKey(self, delay : int = 0):
        # キー入力待ち
        return cv2.waitKey(delay)

    def resizeWindow(self, width, height):
        cv2.resizeWindow(self.__winname, width, height)

    def _onMouse(self, event, x, y, flags, params):
        '''マウスのコールバック関数

        Parameters
        ----------
        event : int
            押されたマウスボタンの種類
        x : int
            マウスポインタの画像上のX座標
        y : int
            マウスポインタの画像上のY座標
        flags : int
            Shift, Ctrl, Altキーの押された種類
        params : 
            コールバック関数登録時に渡された値
        '''

        if self.__disp_image is None:
            return

        #print(f"[{x}, {y}] event = {event} flags = {flags} params = {params}")

        if event == cv2.EVENT_LBUTTONDOWN:
            # マウスの左ボタンが押されたとき
            self.__mouse_down_flag = True
            self.__old_affine_matrix = self.__affine_matrix
            self.old_point_x = x
            self.old_point_y = y

        elif event == cv2.EVENT_LBUTTONUP:
            # マウスの左ボタンが離されたとき
            self.__mouse_down_flag = False
            # self.old_point_x = x
            # self.old_point_y = y

        elif event == cv2.EVENT_MOUSEMOVE:
            # マウスが動いているとき
            if self.__mouse_down_flag is True:
                # 画像の平行移動
                # アフィン変換行列の平行移動
                self.__affine_matrix = affine.translateMatrix(x - self.old_point_x, y - self.old_point_y).dot(self.__old_affine_matrix)

                #print(f"[{x}, {y}] event = {event} flags = {flags} params = {params} ({x - self.old_point_x}, {y - self.old_point_y}) {self.__affine_matrix[0, 2]}  {self.__affine_matrix[1, 2]} {self.__old_affine_matrix[0, 2]}  {self.__old_affine_matrix[1, 2]}")

                self.redraw_image()
                cv2.waitKey(1)  

        elif event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                # マウスホイールを上に回したとき、画像の拡大
                if self.__affine_matrix[0, 0] * self.__zoom_delta > self.__max_scale:
                    return
                self.__affine_matrix = affine.scaleAtMatrix(self.__zoom_delta, x, y).dot(self.__affine_matrix)
              
            else:
                # マウスホイールを下に回したとき、画像の縮小
                if self.__affine_matrix[0, 0] / self.__zoom_delta < self.__min_scale:
                    return
                self.__affine_matrix = affine.scaleAtMatrix(1/self.__zoom_delta, x, y).dot(self.__affine_matrix)

            self.redraw_image()
            cv2.waitKey(1)

        elif event == cv2.EVENT_LBUTTONDBLCLK:
            # 左ボタンをダブルクリックしたとき、画像全体を表示(zoom_fit)
            self.zoom_fit()

        elif event == cv2.EVENT_RBUTTONDBLCLK:
            # マウスの右ボタンがダブルクリックされたとき、等倍表示にする
            self.__affine_matrix = affine.scaleAtMatrix(1/self.__affine_matrix[0, 0], x, y).dot(self.__affine_matrix)
            self.redraw_image()
            cv2.waitKey(1)  

    @property
    def winname(self):
        return self.__winname
    
    @property
    def zoom_delta(self):
        return self.__zoom_delta
    @zoom_delta.setter
    def zoom_delta(self, value : float):
        self.__zoom_delta = value

    @property
    def min_scale(self):
        return self.__min_scale
    @min_scale.setter
    def min_scale(self, value : float):
        self.__min_scale = value

    @property
    def max_scale(self):
        return self.__max_scale
    @max_scale.setter
    def max_scale(self, value : float):
        self.__max_scale = value

    @property
    def inter(self):
        return self.__inter 
    @inter.setter
    def inter(self, value):
        '''補間モードの取得／設定
        '''
        self.__inter = value

    @property
    def affine_matrix(self):
        return self.__affine_matrix 
    @affine_matrix.setter
    def affine_matrix(self, value):
        '''アフィン変換行列の取得／設定
        '''
        self.__affine_matrix = value
    