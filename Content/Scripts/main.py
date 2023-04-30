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


import unreal_engine as ue
from unreal_engine.enums import EPixelFormat

class MainComponent:
    def begin_play(self):
        # 绑定每一帧的回调函数
        Owner = self.uobject.get_owner()
        Owner.bind_event("OnMainTask", self.main_task)
        
        # 预处理: 配置
        self.opt = Options().parse() # 一些配置，比如batch_size，gpu_id等
        ue.print_string("in python: begin_play--opt")
        print(self.opt)
        
        '''
        预处理: 关键点
        '''
        self.sc = gen.MHFormer()
        ue.print_string("in python: begin_play--MHFormer")
        
        '''
        预处理: 重打光
        '''
        self.relight = Relight(self.opt)
        ue.print_string("in python: begin_play--Relight")
        self.matte = Matte(self.opt)
        ue.print_string("in python: begin_play--Matte")
        
        
        '''
        预处理: 绑定UI材质
        '''
        # 纹理的宽、高、DPI
        width = 720
        height = 1280
        # 创建UE纹理
        self.texture = ue.create_transient_texture(width, height, EPixelFormat.PF_R8G8B8A8)
        
        # 获取拥有该组件的Actor
        Owner = self.uobject.get_owner()
        
        # 得到Owner的Plane组件, 修改它的材质, 设置材质参数"Graph"
        Owner.M_UI.set_material_texture_parameter('Graph', self.texture)
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
        
        light = np.load('E:/MyProject/UE/Python/VirtualStudio/BodyRelight/datas/LIGHT/env_sh.npy')[0]
        frame = np.asarray(frame)
        
        mask = self.matte.matte(frame)
        relighted_image = self.relight.relight(frame, mask, light, need_normalize = True)
        # relighted_image = relighted_image.astype(np.uint8)
        
        # TODO: 将重打光后的图片传给UE(图片)
        relighted_image_contiguous = np.ascontiguousarray(relighted_image/255)
        self.texture.texture_set_data(relighted_image_contiguous)
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