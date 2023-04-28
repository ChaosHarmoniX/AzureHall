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

class MainComponent:
    def begin_play(self):
        # 绑定每一帧的回调函数
        Owner = self.uobject.get_owner()
        Owner.bind_event("OnMainTask", self.main_task)
        return
        
        # 预处理
        self.opt = Options().parse() # 一些配置，比如batch_size，gpu_id等
        ue.print_string("in python: begin_play--opt")
        print(self.opt)
        
        self.sc = gen.MHFormer()
        ue.print_string("in python: begin_play--MHFormer")
        
        self.relight = Relight(self.opt)
        ue.print_string("in python: begin_play--Relight")
        
        self.matte = Matte(self.opt)
        ue.print_string("in python: begin_play--Matte")
        
        
        
    def main_task(self):
        
        return
        # 从图片流中读取一帧
        ret, frame = self.sc.get_img()
        
        # 图片流结束
        if ret == False:
            return
        
        exr = [] # TODO: UE生成EXR图片，需要转换成sh
        
        # light = np.asarray(exr)
        # frame = np.asarray(frame)
        frame = np.ndarray((1024, 1024, 3))
        light = np.ndarray((9, 3))
        
        mask = self.matte.matte(frame)
        relighted_image = self.relight.relight(frame, mask, light, need_normalize = True)
        relighted_image = relighted_image.astype(np.uint8)
        key_points = self.sc.get_3D_kpt()
        
        # TODO: 把关键帧传给UE
        print("image:\n", relighted_image[0])
        print("key_points:\n", key_points[0])