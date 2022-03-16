from config import read_config, overwrite_scene_data
from config.config import overwite_version
from data_manager import DataManager
from src import DirectFloorPlanEstimation
from utils.visualization.vispy_utils import plot_color_plc
from utils.enum import CAM_REF
import numpy as np
from utils.data_utils import flatten_lists_of_lists
import matplotlib.pyplot as plt
from utils.visualization.room_utils import plot_curr_room_by_patches, plot_all_rooms_by_patches
from utils.visualization.room_utils import plot_floor_plan
from utils.room_id_eval_utils import eval_2D_room_id_iou, summarize_results_room_id_iou
from utils.io import read_csv_file, save_csv_file
import os


def main(config_file, scene_list_file, version):
    # ! Reading list of scenes
    list_scenes = read_csv_file(scene_list_file)

    cfg = read_config(config_file=config_file)
    for param in (4, 5, 6, 7, 8, 20, 15, 10, 1):
        ver = version + f"_clip{param}"
        cfg["room_id.clipped_ratio"] = param 
                    
        # ! Running every scene
        for scene in list_scenes:
            overwrite_scene_data(cfg, scene)
            overwite_version(cfg, ver)
            
            dt = DataManager(cfg)

            fpe = DirectFloorPlanEstimation(dt)
            
            fpe.compute_non_sequential_fpe()

            eval_2D_room_id_iou(fpe)
            fpe.dt.save_config()
            


if __name__ == '__main__':
    # TODO read from  passed args
    config_file = "./config/config.yaml"
    scene_list_file = './data/all_scenes_list.csv'
    version = 'test_gt_room_id_no_weight_new'

    main(config_file, scene_list_file, version)
