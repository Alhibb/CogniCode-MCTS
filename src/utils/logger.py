import logging
import sys
from colorama import Fore, Style, init

init(autoreset=True)

def setup_logger(name: str = "CogniCode"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} - %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()