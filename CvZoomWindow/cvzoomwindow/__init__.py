__version__ = "0.0.1"

import math
import cv2

from cvzoomwindow import affine

class CvZoomWindow:

    def __init__(self, winname, back_color = (128, 128, 0), inter = cv2.INTER_NEAREST):

        self.__winname = winname        # namedWindowのタイトル
        self.__back_color = back_color  # 背景色
        self.__inter = inter            # 補間表示モード

        self.__src_image = None
        self.__disp_image = None
        self.__affine_matrix = affine.identityMatrix()
        self.__old_affine_matrix = affine.identityMatrix()

        self.__zoom_delta = 1.5
        self.__min_scale = 0.01
        self.__max_scale = 300

        self.__bright_disp_enabled = True # 輝度値の表示／非表示設定
        self.__min_bright_disp_scale = 30 # 輝度値を表示する最小倍率
        self.__grid_disp_enabled = True # グリッド線の表示／非表示設定
        self.__grid_color = (128, 128, 0) # グリッド線の色
        self.__min_grid_disp_scale = 20 # グリッド線を表示する最小倍率

        self.__mouse_down_flag = False

        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)

        # コールバック関数の登録
        cv2.setMouseCallback(winname, self._onMouse, winname)


    @property
    def winname(self) -> str:
        return self.__winname
    
    @property
    def zoom_delta(self) -> float:
        return self.__zoom_delta
    @zoom_delta.setter
    def zoom_delta(self, value : float):
        self.__zoom_delta = value

    @property
    def scale(self) -> float:
        '''表示倍率の取得
        '''      
        return self.__affine_matrix[0, 0]

    @property
    def min_scale(self) -> float:
        return self.__min_scale
    @min_scale.setter
    def min_scale(self, value : float):
        self.__min_scale = value

    @property
    def max_scale(self) -> float:
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


    @property
    def bright_disp_enabled(self) -> bool:
        return self.__bright_disp_enabled 
    @bright_disp_enabled.setter
    def bright_disp_enabled(self, value : bool):
        '''輝度値の表示／非表示設定
        '''
        self.__bright_disp_enabled = value

    @property
    def grid_disp_enabled (self) -> bool:
        return self.__grid_disp_enabled 
    @grid_disp_enabled .setter
    def grid_disp_enabled (self, value : bool):
        '''グリッド線の表示／非表示設定
        '''
        self.__grid_disp_enabled  = value

    @property
    def grid_color (self):
        return self.__grid_color 
    @grid_color .setter
    def grid_color (self, value):
        '''グリッド線の色
        '''
        self.__grid_color  = value   

    @property
    def min_grid_disp_scale(self) -> float:
        return self.__min_grid_disp_scale
    @min_grid_disp_scale.setter
    def min_grid_disp_scale(self, value : float):
        '''グリッド線を表示する最小倍率

        Parameters
        ----------
        value : float
            _description_
        '''
        self.__min_grid_disp_scale = value

    @property
    def min_bright_disp_scale(self) -> float:
        return self.__min_bright_disp_scale
    @min_bright_disp_scale.setter
    def min_bright_disp_scale(self, value : float):
        '''輝度値を表示する最小倍率

        Parameters
        ----------
        value : float
            _description_
        '''
        self.__min_bright_disp_scale = value
        
    def imshow(self, image, zoom_fit : bool = True):
        '''Image display

        Parameters
        ----------
        image : np.ndarray
            Image data to display
        zoom_fit : bool
            True : Display images in the entire window (default)     
            False :Do not display images in the entire window         
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
        '''Image redraw
        '''

        if self.__src_image is None:
            return
        
        _, _, win_width, win_height = cv2.getWindowImageRect(self.__winname)

        self.__disp_image = cv2.warpAffine(self.__src_image, self.__affine_matrix[:2,], (win_width, win_height), flags = self.__inter, borderValue = self.__back_color)
        
        if self.__grid_disp_enabled is True:
            if self.__affine_matrix[0, 0] > self.__min_grid_disp_scale:
                # Grid線を表示する条件が揃っているとき
                self._draw_grid_line()

        if self.__bright_disp_enabled is True:
            if self.__affine_matrix[0, 0] > self.__min_bright_disp_scale:
                # 輝度値を表示する条件が揃っているとき
                self._draw_bright_line()
                
        
        cv2.imshow(self.__winname, self.__disp_image)

    def zoom_fit(self, image_width : int = 0, image_height : int = 0):
        '''Display the image in the entire window

        Parameters
        ----------
        image_width : int, optional
            Image Width, by default 0
        image_height : int, optional
            Image Height, by default 0
        '''

        if self.__src_image is not None:
            # 画像データが表示されているとき
            # 画像のサイズ
            image_width = self.__src_image.shape[1]
            image_height = self.__src_image.shape[0]
        else:
            # 画像データが表示されていないとき
            if image_width == 0 or image_height == 0:
                # 画像サイズが指定されていないときは、何もしない
                return   

        # 画像表示領域のサイズ
        _, _, win_width, win_height = cv2.getWindowImageRect(self.__winname)

        if (image_width * image_height <= 0) or (win_width * win_height <= 0):
            # 画像サイズもしくはウィンドウサイズが０のとき
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

        # 画素の中心分(0.5画素)だけ移動する。
        self.__affine_matrix = affine.translateMatrix(0.5, 0.5).dot(self.__affine_matrix)
        # 拡大縮小
        #self.__affine_matrix[0, 0] = scale
        #self.__affine_matrix[1, 1] = scale
        self.__affine_matrix = affine.scaleMatrix(scale).dot(self.__affine_matrix)
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

    def set_pixel_callback(self, callback_func):
        pass


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

    def _image_disp_rect(self):
        '''画像を表示している領域を取得する

        Returns
        -------
        _type_
            _description_
        '''

        if self.__src_image is None:
            return False, 0, 0, 0, 0

        # ウィンドウの座標 -> 画像の座標のアフィン変換行列
        invMat = affine.inverse(self.__affine_matrix)

        # 画像の端のウィンドウ上の座標
        # 左上側
        image_top_left_win = affine.afiinePoint(self.__affine_matrix, -0.5, -0.5)
        # 右下側
        image_width = self.__src_image.shape[1]
        image_height = self.__src_image.shape[0]
        image_bottom_right_win = affine.afiinePoint(self.__affine_matrix, image_width-0.5, image_height-0.5)    

        # ウィンドウの端の画像上の座標
        # 画像表示領域のサイズ
        _, _, win_width, win_height = cv2.getWindowImageRect(self.__winname)
        # 左上側
        win_top_left_img = affine.afiinePoint(invMat, -0.5, -0.5)
        # 右下側
        win_bottom_right_img = affine.afiinePoint(invMat, win_width-0.5, win_height-0.5)

        # 画像のはみ出し確認
        # 左側
        if image_top_left_win[0] < 0:
            # 画像の左側がウィンドウの外にはみ出している
            #print("画像の左側がウィンドウの外にはみ出している")

            # ウィンドウの左上の座標の画像上の座標を計算
            #point = affine.afiinePoint(invMat, 0, 0)
            image_left = invMat[0, 2]
            image_left = math.floor(image_left + 0.5) - 0.5

        else:
            # 画像の左側がウィンドウの外にはみ出していない
            #print("画像の左側がウィンドウの外にはみ出していない")
            image_left = -0.5

         # 上側
        if image_top_left_win[1] < 0:
            # 画像の上側がウィンドウの外にはみ出している
            #print("画像の上側がウィンドウの外にはみ出している")

            # ウィンドウの左上の座標の画像上の座標を計算
            #point = affine.afiinePoint(invMat, 0, 0)
            image_top = invMat[1, 2]
            image_top = math.floor(image_top + 0.5) - 0.5
            
        else:
            # 画像の上側がウィンドウの外にはみ出していない
            #print("画像の上側がウィンドウの外にはみ出していない")
            image_top = -0.5

         # 右側
        if image_bottom_right_win[0] > win_width-1:
            # 画像の右側がウィンドウの外にはみ出している
            #print("画像の右側がウィンドウの外にはみ出している")
            # ウィンドウの右下の座標の画像上の座標を計算
            #point = affine.afiinePoint(invMat, win_width-1, win_height-1)
            image_right = invMat[0, 0] * (win_width-1) + invMat[0, 2]
            image_right = math.floor(image_right + 0.5) + 0.5
            pass
        else:
            # 画像の右側がウィンドウの外にはみ出していない
            #print("画像の右側がウィンドウの外にはみ出していない")
            image_right = image_width - 0.5
            pass

         # 下側
        if image_bottom_right_win[1] > win_height-1:
            # 画像の下側がウィンドウの外にはみ出している
            #print("画像の下側がウィンドウの外にはみ出している")
            image_bottom = invMat[1, 1] * (win_height-1) + invMat[1, 2]
            image_bottom = math.floor(image_bottom + 0.5) + 0.5
        else:
            # 画像の下側がウィンドウの外にはみ出していない
            #print("画像の下側がウィンドウの外にはみ出していない")
            image_bottom = image_height - 0.5

        return True, image_left, image_top, image_right, image_bottom

    def _draw_grid_line(self):

        # グリッドの線の表示領域の画像の範囲を計算する
        ret, x0, y0, x1, y1 = self._image_disp_rect()

        if ret is False:
            return

        # 画像の座標-> ウィンドウ座標のアフィン変換行列
        m = self.__affine_matrix

        # 縦線
        py0 = m[1, 1] * y0+ m[1, 2]
        py1 = m[1, 1] * y1+ m[1, 2]
        py0 = math.floor(py0+0.5)
        py1 = math.floor(py1+0.5)
        for x in range(int(x0+0.5), int(x1+0.5)):
            px = m[0, 0] * (x-0.5)+ m[0, 2]
            cv2.line(
                self.__disp_image, 
                (math.floor(px+0.5), py0), 
                (math.floor(px+0.5), py1), 
                self.__grid_color, 
                1)

        # 横線
        px0 = m[0, 0] * x0+ m[0, 2]
        px1 = m[0, 0] * x1+ m[0, 2]
        px0 = math.floor(px0+0.5)
        px1 = math.floor(px1+0.5)
        for y in range(int(y0+0.5), int(y1+0.5)):
            py = m[1, 1] * (y-0.5)+ m[1, 2]
            cv2.line(
                self.__disp_image, 
                (px0, math.floor(py+0.5)), 
                (px1, math.floor(py+0.5)), 
                self.__grid_color, 
                1)

    def _draw_bright_line(self):

        # 輝度値の表示領域の画像の範囲を計算する
        ret, x0, y0, x1, y1 = self._image_disp_rect()

        if ret is False:
            return

        # 画像の座標-> ウィンドウ座標のアフィン変換行列
        m = self.__affine_matrix

        py0 = m[1, 1] * y0+ m[1, 2]
        py1 = m[1, 1] * y1+ m[1, 2]
        py0 = math.floor(py0+0.5)
        py1 = math.floor(py1+0.5)

        px0 = m[0, 0] * x0+ m[0, 2]
        px1 = m[0, 0] * x1+ m[0, 2]
        px0 = math.floor(px0+0.5)
        px1 = math.floor(px1+0.5)

        offset_x = int(m[0, 0] / 90)
        offset_y = int(m[0, 0] / 6)

        offset_r = int(m[0, 0] / 1.58)
        offset_g = int(m[0, 0] / 1.24)
        offset_b = int(m[0, 0] / 1.03)

        fore_r = (0, 0, 200)
        fore_g = (0, 200, 0)
        fore_b = (200, 0, 0)

        thick = 1

        if self.__disp_image.ndim == 3:
            # カラーのとき
            for y in range(int(y0+0.5), int(y1+0.5)):
                for x in range(int(x0+0.5), int(x1+0.5)):
                    px = m[0, 0] * (x-0.5)+ m[0, 2]
                    py = m[1, 1] * (y-0.5)+ m[1, 2]

                    bright = self.__src_image[y, x, :]

                    if bright.max() > 127:
                        fore_color = (0, 0, 0)
                    else:
                        fore_color = (255, 255, 255)

                    # 座標
                    cv2.putText(
                        self.__disp_image,
                        text=f"({x},{y})",
                        org=(math.floor(px+0.5) + offset_x, math.floor(py+0.5) + offset_y),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,#cv2.FONT_HERSHEY_DUPLEX, #cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=m[0, 0] / 200,
                        color=fore_color,
                        thickness = thick)

                    # B
                    cv2.putText(
                        self.__disp_image,
                        text=f"{str(bright[0]).rjust(11)}",
                        org=(math.floor(px+0.5) + offset_x, math.floor(py+0.5) + offset_b),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,#cv2.FONT_HERSHEY_DUPLEX, #cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=m[0, 0] / 200,
                        color=fore_b,
                        thickness = thick)

                    # G
                    cv2.putText(
                        self.__disp_image,
                        text=f"{str(bright[1]).rjust(11)}",
                        org=(math.floor(px+0.5) + offset_x, math.floor(py+0.5) + offset_g),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,#cv2.FONT_HERSHEY_DUPLEX, #cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=m[0, 0] / 200,
                        color=fore_g,
                        thickness = thick)

                    # R
                    cv2.putText(
                        self.__disp_image,
                        text=f"{str(bright[2]).rjust(11)}",
                        org=(math.floor(px+0.5) + offset_x, math.floor(py+0.5) + offset_r),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,#cv2.FONT_HERSHEY_DUPLEX, #cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=m[0, 0] / 200,
                        color=fore_r,
                        thickness = thick)

        else:
            # モノクロのとき
            for y in range(int(y0+0.5), int(y1+0.5)):
                for x in range(int(x0+0.5), int(x1+0.5)):
                    px = m[0, 0] * (x-0.5)+ m[0, 2]
                    py = m[1, 1] * (y-0.5)+ m[1, 2]

                    bright = self.__src_image[y, x]

                    if bright > 127:
                        fore_color = (0, 0, 0)
                    else:
                        fore_color = (255, 255, 255)

                    # 座標
                    cv2.putText(
                        self.__disp_image,
                        text=f"({x},{y})",
                        org=(math.floor(px+0.5) + offset_x, math.floor(py+0.5) + offset_y),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,#cv2.FONT_HERSHEY_DUPLEX, #cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=m[0, 0] / 200,
                        color=fore_color,
                        thickness = thick)

                    # 輝度値
                    cv2.putText(
                        self.__disp_image,
                        text=f"{str(bright).rjust(11)}",
                        org=(math.floor(px+0.5) + offset_x, math.floor(py+0.5) + offset_b),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,#cv2.FONT_HERSHEY_DUPLEX, #cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=m[0, 0] / 200,
                        color=fore_color,
                        thickness = thick)