from config import read_config
from data_manager import DataManager
from src import DirectFloorPlanEstimation
from utils.visualization.vispy_utils import plot_color_plc
import numpy as np
from utils import Enum


def main(config_file):
    cfg = read_config(config_file=config_file)
    dt = DataManager(cfg)
    fpe = DirectFloorPlanEstimation(dt)
    vis = Visualization(fpe)
    list_ly = dt.get_list_ly(cam_ref=Enum.cam_ref.WC_SO3)
    
    for ly in list_ly:
        fpe.estimate(ly)
        vis.update()
                
    list_rooms_est = fpe.list_rooms
    list_rooms_gt = dt.get_list_rooms_gt()
    
    evaluate(list_rooms_est, list_rooms_gt)
    plot_2d_fpe(list_rooms_est)
    plot_2d_fpe(list_rooms_gt)
    
    plot_3D_FPE(list_rooms_est)
    plot_3D_FPE(list_rooms_gt)
    


if __name__ == '__main__':
    # TODO read from  passed args
    config_file = "./config/config.yaml"
    main(config_file=config_file)
