"""Centralized Logging Architecture for the OS Simulation Suite.
Maintains persistent audit traces in 'simulation.log' and formats runtime logs.
"""

import logging
import os
from typing import Optional

DEFAULT_LOG_FILE = "simulation.log"


def setup_logger(name: str = "OS_Simulator", log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a structured logger instance."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)-7s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    target_file = log_file or DEFAULT_LOG_FILE
    try:
        fh = logging.FileHandler(target_file, mode="a", encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        print(f"Warning: Unable to attach file logger to {target_file}: {e}")

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)  # keep console clean, errors/warnings surfaced
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


# Global application logger
app_logger = setup_logger("OS_Kernel")

