from loguru import logger
import os


def setup_loguru():
    # Main logger: INFO and above
    logger.add(
        f"{os.path.abspath('./logging/logs.log')}",
        rotation="10 MB",
        level="INFO",
        compression="zip",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name: <35} | {message}",
        backtrace=False,
        diagnose=False,
    )

    # Error logger: ERROR and above only
    logger.add(
        f"{os.path.abspath('./logging/errors.log')}",
        rotation="5 MB",
        level="ERROR",
        compression="zip",
        retention="6 months",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name: <35} | {message}",
        backtrace=False,
        diagnose=False,
    )

    return logger
