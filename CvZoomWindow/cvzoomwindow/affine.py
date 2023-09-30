# affine.py

__version__ = "0.0.1"

import cv2
import numpy as np

def scaleMatrix(scale):
    '''拡大縮小用アフィン変換行列の取得(X方向とY方向同じ倍率)'''
    mat = identityMatrix() # 3x3の単位行列
    mat[0,0] = scale
    mat[1,1] = scale

    return mat

def scaleXYMatrix(sx, sy):
    '''拡大縮小用アフィン変換行列の取得(X方向とY方向の倍率をぞれぞれ指定)'''
    mat = identityMatrix() # 3x3の単位行列
    mat[0,0] = sx
    mat[1,1] = sy

    return mat

def translateMatrix(tx, ty):
    '''平行移動用アフィン変換行列の取得'''
    mat = identityMatrix() # 3x3の単位行列
    mat[0,2] = tx
    mat[1,2] = ty

    return mat

def rotateMatrix(deg):
    '''回転用アフィン変換行列の取得'''
    mat = identityMatrix() # 3x3の単位行列
    rad = np.deg2rad(deg) # 度をラジアンへ変換
    sin = np.sin(rad)
    cos = np.cos(rad)

    mat[0,0] = cos
    mat[0,1] = -sin
    mat[1,0] = sin
    mat[1,1] = cos

    return mat

def scaleAtMatrix(scale, cx, cy):
    '''点(cx, cy)を基点とした拡大縮小用アフィン変換行列の取得'''

    # 基点の座標を原点へ移動
    mat = translateMatrix(-cx, -cy)
    # 原点周りに拡大縮小
    mat = scaleMatrix(scale).dot(mat)
    # 元の位置へ戻す
    mat = translateMatrix(cx, cy).dot(mat)

    return mat

def rotateAtMatrix(deg, cx, cy):
    '''点(cx, cy)を基点とした回転用アフィン変換行列の取得'''

    # 基点の座標を原点へ移動
    mat = translateMatrix(-cx, -cy)
    # 原点周りに回転
    mat = rotateMatrix(deg).dot(mat)
    # 元の位置へ戻す
    mat = translateMatrix(cx, cy).dot(mat)

    return mat

def afiinePoint(mat, px, py):
    '''点(px, py)をアフィン変換行列(mat)で変換した後の点を取得'''

    srcPoint = np.array([px, py, 1])

    return mat.dot(srcPoint)[:2]

def inverse(mat):
    '''行列の逆行列を求める'''
    return np.linalg.inv(mat)

def identityMatrix():
    '''3x3の単位行列を取得'''
    return np.eye(3, dtype = np.float32) # 3x3の単位行列