__version__ = "0.0.1"

import math
import cv2

from cvzoomwindow import affine

class CvZoomWindow:

    def __init__(self, winname : str, back_color = (128, 128, 0), inter = cv2.INTER_NEAREST):
        '''Instantiate the CvZoomWindow class.

        Parameters
        ----------
        winname : str
            Name of the window
        back_color : tuple, optional
            background color, by default (128, 128, 0)
        inter : optional
            interpolation methods, by default cv2.INTER_NEAREST
        '''

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

        self.__mouse_event_enabled = True
        self.__mouse_down_flag = False

        self.__mouse_callback_func = None

        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)

        # コールバック関数の登録
        cv2.setMouseCallback(winname, self._onMouse, winname)

    @property
    def winname(self) -> str:
        '''Get window name

        Returns
        -------
        str
            window name
        '''
        return self.__winname
    
    @property
    def zoom_delta(self) -> float:
        return self.__zoom_delta
    @zoom_delta.setter
    def zoom_delta(self, value : float):
        '''Get and set the zoom factor per notch of the mouse wheel.

        Parameters
        ----------
        value : float
            zoom factor per notch of the mouse wheel.( > 1)
        '''
        self.__zoom_delta = value

    @property
    def scale(self) -> float:
        '''Gets the current image display zoom factor.
        '''      
        return self.__affine_matrix[0, 0]

    @property
    def min_scale(self) -> float:
        return self.__min_scale
    @min_scale.setter
    def min_scale(self, value : float):
        '''Gets and sets the minimum display zoom factor.

        Parameters
        ----------
        value : float
            minimum zoom factor
        '''
        self.__min_scale = value

    @property
    def max_scale(self) -> float:
        return self.__max_scale
    @max_scale.setter
    def max_scale(self, value : float):
        '''Gets and sets the maximum display zoom factor.

        Parameters
        ----------
        value : float
            maximum zoom factor.
        '''
        self.__max_scale = value

    @property
    def inter(self):
        return self.__inter 
    @inter.setter
    def inter(self, value):
        '''Gets and sets the interpolation mode.(OpenCV enum cv::InterpolationFlags)
        '''
        self.__inter = value

    @property
    def mouse_event_enabled(self) -> bool:
        return self.__mouse_event_enabled
    @mouse_event_enabled.setter
    def mouse_event_enabled(self, value : bool):
        '''Enables(True)/disables(False) image scaling and movement by mouse operation.

        Parameters
        ----------
        value : bool
            mouse operation enable
        '''
        self.__mouse_event_enabled = value

    @property
    def affine_matrix(self):
        return self.__affine_matrix 
    @affine_matrix.setter
    def affine_matrix(self, value):
        '''Gets and sets the affine transformation matrix.

        Parameters
        ----------
        value : np.ndarray
            affine matrix
        '''
        self.__affine_matrix = value

    @property
    def bright_disp_enabled(self) -> bool:
        return self.__bright_disp_enabled 
    @bright_disp_enabled.setter
    def bright_disp_enabled(self, value : bool):
        '''Gets and sets the display/non-display settings for luminance values.

        Parameters
        ----------
        value : bool
            True : display
            False : non-display
        '''
        self.__bright_disp_enabled = value

    @property
    def grid_disp_enabled (self) -> bool:
        return self.__grid_disp_enabled 
    @grid_disp_enabled .setter
    def grid_disp_enabled (self, value : bool):
        '''Gets and sets the display/non-display settings for grid lines

        Parameters
        ----------
        value : bool
            True : display
            False : non-display
        '''
        self.__grid_disp_enabled  = value

    @property
    def grid_color (self):
        return self.__grid_color 
    @grid_color .setter
    def grid_color (self, value):
        '''Gets and sets the color of the grid lines.

        Parameters
        ----------
        value : 
            Line color.
        '''
        self.__grid_color  = value   

    @property
    def min_grid_disp_scale(self) -> float:
        return self.__min_grid_disp_scale
    @min_grid_disp_scale.setter
    def min_grid_disp_scale(self, value : float):
        '''Minimum scale factor for displaying grid lines

        Parameters
        ----------
        value : float
            Minimum scale
        '''
        self.__min_grid_disp_scale = value

    @property
    def min_bright_disp_scale(self) -> float:
        return self.__min_bright_disp_scale
    @min_bright_disp_scale.setter
    def min_bright_disp_scale(self, value : float):
        '''Gets or sets the minimum scale factor at which luminance values are to be displayed.

        Parameters
        ----------
        value : float
            minimum scale
        '''
        self.__min_bright_disp_scale = value

    @property
    def displayed_image(self):
        '''Gets the image displayed in the window.
        '''
        return self.__disp_image
        
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

    def redraw_image(self):
        '''Image redraw
        '''

        if self.__src_image is None:
            return
        
        try:
            _, _, win_width, win_height = cv2.getWindowImageRect(self.__winname)
        except:
            #print('redraw_image error')
            return

        self.__disp_image = cv2.warpAffine(self.__src_image, self.__affine_matrix[:2,], (win_width, win_height), flags = self.__inter, borderValue = self.__back_color)
        
        if self.__grid_disp_enabled is True:
            if self.__affine_matrix[0, 0] > self.__min_grid_disp_scale:
                # Grid線を表示する条件が揃っているとき
                self._draw_grid_line()

        if self.__bright_disp_enabled is True:
            if self.__affine_matrix[0, 0] > self.__min_bright_disp_scale:
                # 輝度値を表示する条件が揃っているとき
                self._draw_bright_value()
                
        
        cv2.imshow(self.__winname, self.__disp_image)
        #cv2.waitKey(1)            

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
        try:
            _, _, win_width, win_height = cv2.getWindowImageRect(self.__winname)
        except:
            print('zoom_fit error')
            return

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
        self.__affine_matrix = affine.scaleMatrix(scale).dot(self.__affine_matrix)
        # あまり部分を中央に寄せる
        self.__affine_matrix = affine.translateMatrix(offsetx, offsety).dot(self.__affine_matrix)

        # 描画
        self.redraw_image()
        
    def zoom(self, delta : float):
        '''Zoom in/out the image based on the center of the window.

        Parameters
        ----------
        delta : _type_
            relative zoom factor
            value > 1 : zoom up
            value < 1 : zoom down
        '''
        # 画像表示領域のサイズ
        try:
            _, _, win_width, win_height = cv2.getWindowImageRect(self.__winname)
        except:
            #print('zoom error')
            return

        self.zoom_at(delta, win_width/2.0, win_height/2.0)

    def zoom_at(self, delta: float, wx : float, wy : float):
        '''Scale up/down the image based on the specified coordinates of the window.

        Parameters
        ----------
        delta : float
            relative zoom factor
        wx : float
            Window X-coordinate
        wy : float
            Window Y-coordinate
        '''

        if delta >= 1.0:
            # マウスホイールを上に回したとき、画像の拡大
            if self.__affine_matrix[0, 0] * delta > self.__max_scale:
                return
            self.__affine_matrix = affine.scaleAtMatrix(delta, wx, wy).dot(self.__affine_matrix)
              
        elif delta > 0.0:
            # マウスホイールを下に回したとき、画像の縮小
            if self.__affine_matrix[0, 0] * delta < self.__min_scale:
                return
            self.__affine_matrix = affine.scaleAtMatrix(delta, wx, wy).dot(self.__affine_matrix)
        else:
            return

        self.redraw_image()

    def pan(self, tx : float, ty : float):
        '''Moves and displays images.

        Parameters
        ----------
        tx : float
            Amount of movement in X direction
        ty : float
            Amount of movement in Y direction
        '''
        self.__affine_matrix = affine.translateMatrix(tx, ty).dot(self.__affine_matrix)
        self.redraw_image()

    def destroyWindow(self):
        '''Delete Window
        '''
        cv2.destroyWindow(self.__winname)

    def resizeWindow(self, width : int, height : int):
        '''Sets the window size.

        Parameters
        ----------
        width : int
            Window Width
        height : int
            Window Height
        '''
        cv2.resizeWindow(self.__winname, width, height)

    def _callback_handler(self, func, *args):
        return func(*args)
    
    def set_mouse_callback(self, callback_func):
        '''Registers a callback function for mouse operations.

        Parameters
        ----------
        callback_func : 
            callback function
        '''
        self.__mouse_callback_func = callback_func

    def image_to_window_point(self, img_x : float, img_y : float):
        '''Converts image coordinates to window coordinates.

        Parameters
        ----------
        img_x : float
            X coordinate of image
        img_y : float
            Y coordinate of image

        Returns
        -------
        (win_x : float, win_y : float)
        win_x : float
            X coordinate of window
        win_y : float
            Y coordinate of window
        '''
        point = affine.afiinePoint(self.__affine_matrix , img_x, img_y)
        return point[0], point[1]

    def window_to_image_point(self, w_x, w_y):
        '''Converts window coordinates to image coordinates.

        Parameters
        ----------
        w_x : float
            X coordinate of window
        w_y : float
            Y coordinate of window

        Returns
        -------
        (img_x : float, img_y : float)
        img_x : float
            X coordinate of image
        img_y : float
            Y coordinate of image
        '''
        invMat = affine.inverse(self.__affine_matrix)
        point = affine.afiinePoint(invMat , w_x, w_y)
        return point[0], point[1]

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

        if self.__mouse_callback_func is not None:
            invMat = affine.inverse(self.__affine_matrix)
            point = affine.afiinePoint(invMat , x, y)
            self._callback_handler(self.__mouse_callback_func, self, event, x, y, flags, params, point[0], point[1], self.affine_matrix[0,0])        

        if self.__mouse_event_enabled is False:
            # マウスイベントが無効の場合
            return

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

        elif event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.zoom_at(self.__zoom_delta, x, y)
            else:
                self.zoom_at(1/self.__zoom_delta, x, y)

        elif event == cv2.EVENT_LBUTTONDBLCLK:
            # 左ボタンをダブルクリックしたとき、画像全体を表示(zoom_fit)
            self.zoom_fit()

        elif event == cv2.EVENT_RBUTTONDBLCLK:
            # マウスの右ボタンがダブルクリックされたとき、等倍表示にする
            self.__affine_matrix = affine.scaleAtMatrix(1/self.__affine_matrix[0, 0], x, y).dot(self.__affine_matrix)
            self.redraw_image()

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
        try:
            _, _, win_width, win_height = cv2.getWindowImageRect(self.__winname)
        except:
            print('_image_disp_rect error')
            return

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

    def _draw_bright_value(self):

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

        if self.__affine_matrix[0, 0] > 100:
            thick = 2
        else:
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