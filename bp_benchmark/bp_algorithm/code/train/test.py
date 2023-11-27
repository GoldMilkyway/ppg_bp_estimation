#%%
import os
import argparse

from time import time, ctime
from omegaconf import OmegaConf
from core.solver_s2s import Solver as solver_s2s
from core.solver_s2l import SolverS2l as solver_s2l

import coloredlogs, logging
coloredlogs.install()
logger = logging.getLogger(__name__)  

####
from utils_ import *
####


def main(args):        
    if os.path.exists(args.config_file) == False:         
        raise RuntimeError("config_file {} does not exist".format(args.config_file))

    time_start = time()
    config = OmegaConf.load(args.config_file)
    config = merge_config_parser(config, args)

    if config.exp.model_type in ['unet1d', 'ppgiabp', 'vnet']:
        solver = solver_s2s(config)
    elif config.exp.model_type in ['resnet1d','spectroresnet','mlpbp', 'convtr']:
        solver = solver_s2l(config)

    solver.test()
    time_now = time()
    logger.warning(f"Time Used: {ctime(time_now-time_start)}")

    # =============================================================================
    # output
    # =============================================================================


#%%
if __name__=='__main__':
    parser = get_parser()
    main(parser.parse_args())