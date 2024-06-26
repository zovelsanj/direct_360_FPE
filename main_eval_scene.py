import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from config import read_config
from data_manager import DataManager
from direct_floor_plan_estimation import DirectFloorPlanEstimation
from utils.visualization.vispy_utils import plot_color_plc
from utils.enum import CAM_REF
from utils.data_utils import flatten_lists_of_lists
from utils.visualization.room_utils import plot_curr_room_by_patches, plot_all_rooms_by_patches
from utils.visualization.room_utils import plot_floor_plan, plot_all_planes, plot_planes_rooms_patches
from utils.eval_utils import evaluate_corners_pr, evaluate_rooms_pr
from utils.io import read_scene_list
from utils.eval_utils import evaluate_scene, dump_images, dump_result, dump_fpe_geometry


def main(opt):
    config_file = opt.cfg
    output_dir = opt.results
    cfg = read_config(config_file=config_file)

    cfg["data.scene"] = opt.scene_name.split("_")[0]
    cfg["data.scene_version"] = opt.scene_name.split("_")[1]
    cfg['data.use_gt_poses'] = True

    dt = DataManager(cfg)
    fpe = DirectFloorPlanEstimation(dt)
    list_ly = dt.get_list_ly(cam_ref=CAM_REF.WC_SO3)

    for ly in list_ly:
        fpe.estimate(ly)

    fpe.eval_room_overlapping()
    fpe.masking_ocg_map()

    if cfg['data.use_gt_poses']:
        points_gt = fpe.dt.pcl_gt      # (3, N)

    room_corner_list = fpe.compute_room_shape_all()
    image_room_id = plot_all_rooms_by_patches(fpe)
    image_final_fp = plot_floor_plan(room_corner_list, fpe.global_ocg_patch)
    room_corner_list = [x.T for x in room_corner_list]  # Make it (N, 2)
    if cfg['data.use_gt_poses']:
        result_dict, images_dict = evaluate_scene(
            room_corner_list,
            fpe.dt.room_corners,
            points_gt,
            axis_corners=fpe.dt.axis_corners
        )
        result_dict['scene'] = cfg['data.scene']
        images_dict['scene'] = cfg['data.scene']
        images_dict['room_id'] = image_room_id
        images_dict['final_fp'] = image_final_fp

    # Saving the results
    results_dir = os.path.join(output_dir, f"{cfg['data.scene']}_{cfg['data.scene_version']}")
    os.makedirs(results_dir, exist_ok=True)

    if cfg['data.use_gt_poses']:

        # GT data for references
        dt.save_gt_rooms(results_dir)

        # Estimated VO-SCALE and density 2d function
        fpe.scale_recover.save_estimation(results_dir)

        #  Estimated results
        dump_images(images_dict, results_dir)

        # writing results
        dump_result([result_dict], output_dir)

    #writing fpe geomtery
    dump_fpe_geometry(room_corner_list, results_dir)

def get_passed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene_name', type=str, default="1LXtFkjw3qL_0", help='MP3D scene with its version e.g 1LXtFkjw3qL_0')
    parser.add_argument('--results', type=str, default="./test", help='Output directory for results')
    parser.add_argument('--cfg', type=str, default="./config/config.yaml", help='Config file')
    opt = parser.parse_args()
    return opt

if __name__ == '__main__':

    opt = get_passed_args()
    main(opt)
