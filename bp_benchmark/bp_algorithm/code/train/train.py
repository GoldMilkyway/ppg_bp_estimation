import os
os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
import argparse
import random
import numpy as np
import torch
import pytorch_lightning as pl

# Load modules
from core.solver_s2s import Solver as solver_s2s
from core.solver_s2l import SolverS2l as solver_s2l
from core.solver_f2l import SolverF2l as solver_f2l
from core.utils import log_params_mlflow, init_mlflow

from omegaconf import OmegaConf
from time import time, ctime
import mlflow as mf
from shutil import rmtree
from pathlib import Path

import coloredlogs, logging

#############################
import pdb
#############################
coloredlogs.install()
logger = logging.getLogger(__name__)  

SEED = 0
torch.cuda.manual_seed(SEED) 
torch.cuda.manual_seed_all(SEED)
pl.utilities.seed.seed_everything(seed=SEED)


def get_parser():
    parser = argparse.ArgumentParser()
    # general config
    parser.add_argument("--config_file", type=str, help="Path for the config file") 

    ## Controllable ##
    parser.add_argument("--save_model", type=bool, default=False, help="Save model in a directory named model-$MODEL_NAME")
    #### Not use ####
    parser.add_argument("--pl_log", type=bool, default=False, help="Create lr Logs")
    return parser

def merge_config_parser(config,args):
    args_dict = vars(args)

    merged_config = OmegaConf.merge(config, args_dict)

    # Manual Setting for Sweep
    return merged_config

def main(args):        
    if os.path.exists(args.config_file) == False:         
        raise RuntimeError("config_file {} does not exist".format(args.config_file))

    time_start = time()

    # Set Config
    config = OmegaConf.load(args.config_file)
    config = merge_config_parser(config, args)

    #--- get the solver
    if config.exp.model_type in ['unet1d', 'ppgiabp', 'vnet']:
        solver = solver_s2s(config)
    
    ## Our Interest
    elif config.exp.model_type in ['resnet1d','spectroresnet','mlpbp', 'convtr']:
        torch.use_deterministic_algorithms(True)
        solver = solver_s2l(config)

    else:
        solver = solver_f2l(config)
    
    #--- training and logging into mlflow
    init_mlflow(config)
    with mf.start_run(run_name=f"{config.exp.N_fold}fold_CV_Results") as run:
        log_params_mlflow(config)
        cv_metrics = solver.evaluate() # Final Output #dict
        logger.info(cv_metrics)
        mf.log_metrics(cv_metrics) 
   
    time_now = time()
    logger.warning(f"Time Used: {ctime(time_now-time_start)}")


if __name__ == '__main__':
    parser = get_parser()
    main(parser.parse_args())

