import os
import sys
path = "E:/MyProject/UE/Python/VirtualStudio/"
sys.path.insert(0, path)
from lib.options import * # TODO: 改了lib名字
from MODNet.app.matte import Matte
from BodyRelight.app.relight import Relight
import MHFormer.app.gen as gen
import cv2
import numpy as np

import unreal_engine as ue
from unreal_engine.enums import EPixelFormat

import matplotlib
# 让matplotlib强制在引擎内显示, 而不是在python后台显示
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class MainComponent:
    def begin_play(self):        
        '''
        预处理: 配置
        '''
        self.opt = Options().parse() # 一些配置，比如batch_size，gpu_id等
        # ue.print_string("in python: begin_play--opt")
        # print(self.opt)
        
        '''
        预处理: 关键点
        '''
        self.sc = gen.MHFormer()
        # ue.print_string("in python: begin_play--MHFormer")
        
        '''
        预处理: 重打光
        '''
        self.relight = Relight(self.opt)
        # ue.print_string("in python: begin_play--Relight")
        self.matte = Matte(self.opt)
        # ue.print_string("in python: begin_play--Matte")
        
        
        '''
        预处理: 绑定UI材质
        '''
        # 纹理的宽、高、DPI
        self.width = 1280
        self.height = 720
        dpi = 72.0
        
        # 创建UE纹理
        self.texture = ue.create_transient_texture(self.width, self.height, EPixelFormat.PF_R8G8B8A8)
        
        # 创建绘pyplot绘图工具
        self.fig = plt.figure(0)
        self.fig.set_dpi(dpi)
        self.fig.set_figwidth(self.width/dpi)
        self.fig.set_figheight(self.height/dpi)
        
        # 获取拥有该组件的Actor
        Owner = self.uobject.get_owner()
        
        # 得到Owner的Plane组件, 修改它的材质, 设置材质参数"Graph"
        Owner.M_UI.set_material_texture_parameter('Graph', self.texture)
        
        # 绑定回调函数
        Owner.bind_event("OnMainTask", self.main_task)
        return
        
        
    def main_task(self):    
        # 从图片流中读取一帧
        ret, frame = self.sc.get_img()
        
        # 图片流结束
        if ret == False:
            return
        
        '''
        关键点
        '''
        # TODO: 根据关键点, 设置角色位置
        key_points = self.sc.get_3D_kpt()
        self.set_key_point(key_points)
    
        '''
        重打光
        '''
        # TODO: UE生成EXR图片，需要转换成sh
        exr = [] 
        
        # 将EXR给到Relight, 生成重新打光的图片
        # frame = np.ndarray((1024, 1024, 3))
        # light = np.ndarray((9, 3))
        
        light = np.load('E:/MyProject/UE/Python/VirtualStudio/BodyRelight/datas/LIGHT/env_sh.npy')[1]
        frame = np.asarray(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        mask = self.matte.matte(frame)
        relighted_image = self.relight.relight(frame, mask, light, need_normalize = True)
        relighted_image = relighted_image.astype(np.uint8)
        
        # 将重打光后的图像转化为PF_R8G8B8A8格式
        image_shape = mask.shape + (4,)
        image = np.zeros(image_shape)
        image[:,:,0] = relighted_image[:,:,0] / 255.0
        image[:,:,1] = relighted_image[:,:,1] / 255.0
        image[:,:,2] = relighted_image[:,:,2] / 255.0
        image[:,:,3] = mask / 255.0
        
        # 清除原有图片
        plt.clf()
        # 省略坐标轴、刻度线、背景
        plt.axis('off')
        plt.xticks([])
        plt.yticks([])
        plt.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0,wspace=0)
        self.fig.set_facecolor((0.0, 0.0, 0.0, 0.0))
        # 根据数组绘制图片
        plt.imshow(image)
        self.fig.canvas.draw()
        
        # 将图片传给UE
        img = self.fig.canvas.buffer_rgba()
        self.texture.texture_set_data(img)
        return
        
    # 设置关键点
    def set_key_point(self, key_points):
        # 设置Owner的属性, 与每隔关键点对应
        Owner = self.uobject.get_owner()
        delta = 120.0
        for i in range(17):
            Owner.SetPosition(i, key_points[i][0]*delta, key_points[i][1]*delta, key_points[i][2]*delta)
        
        # Owner.Pelvis_Position.x = key_points[0][0]
        # Owner.Thigh_R_Position.x = key_points[1][0]
        # Owner.Calf_R_Position.x = key_points[2][0]
        # Owner.Foot_R_Position.x = key_points[3][0]
        # Owner.Thigh_L_Position.x = key_points[4][0]
        # Owner.Calf_L_Position.x = key_points[5][0]
        # Owner.Foot_L_Position.x = key_points[6][0]
        # Owner.Neck_Position.x = key_points[9][0]
        # Owner.Head_Position.x = key_points[10][0]
        # Owner.Upperarm_L_Position.x = key_points[11][0]
        # Owner.Lowerarm_L_Position.x = key_points[12][0]
        # Owner.Hand_L_Position.x = key_points[13][0]
        # Owner.Upperarm_R_Position.x = key_points[14][0]
        # Owner.Lowerarm_R_Position.x = key_points[15][0]
        # Owner.Hand_R_Position.x = key_points[16][0]
        return