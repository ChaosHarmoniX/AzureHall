import os
import sys
path = "E:/MyProject/UE/Python/VirtualStudio/"
# sys.path.insert(0, path + 'VirtualStudio/')
sys.path.insert(0, path)
from lib.options import * # TODO: 改了lib名字
from MODNet.app.matte import Matte
from BodyRelight.app.relight import Relight
import MHFormer.app.gen as gen
import numpy as np
import cv2

        
# 预处理: 配置
opt = Options().parse() # 一些配置，比如batch_size，gpu_id等
print(opt)

'''
预处理: 关键点
'''
sc = gen.MHFormer()

'''
预处理: 重打光
'''
relight = Relight(opt)
matte = Matte(opt)

    
def work():
    # 从图片流中读取一帧
    ret, frame = sc.get_img()

    # 图片流结束
    if ret == False:
        return

    '''
    关键点
    '''
    # TODO: 根据关键点, 设置角色位置
    key_points = sc.get_3D_kpt()


    '''
    重打光
    '''
    # TODO: UE生成EXR图片，需要转换成sh
    exr = [] 

    # 将EXR给到Relight, 生成重新打光的图片
    # frame = np.ndarray((1024, 1024, 3))
    # light = np.ndarray((9, 3))

    light = np.load('E:/MyProject/UE/Python/VirtualStudio/BodyRelight/datas/LIGHT/env_sh.npy')[0]
    frame = np.asarray(frame)
    print(frame.shape)
    

    mask = matte.matte(frame)
    print(mask.shape)
    
    relighted_image = relight.relight(frame, mask, light, need_normalize = True)
    cv2.imwrite('D:/Default/Desktop/UE/relighted_image.jpg', relighted_image)
    
    
    # relighted_image = relighted_image.astype(np.uint8)
    relighted_image_contiguous = np.ascontiguousarray(relighted_image)
    cv2.imwrite('D:/Default/Desktop/UE/relighted_image_contiguous.jpg', relighted_image_contiguous)

    # TODO: 将重打光后的图片传给UE(图片)
    
work()