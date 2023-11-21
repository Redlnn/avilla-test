from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop


def replace_logger(loop: "AbstractEventLoop", level: str = 'INFO'):
    import logging
    import sys
    import traceback

    from loguru import logger

    from utils import loguru_exc_callback, loguru_exc_callback_async, loguru_handler

    logging.basicConfig(handlers=[loguru_handler], level=0, force=True)

    for name in logging.root.manager.loggerDict:
        _logger = logging.getLogger(name)
        for handler in _logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                _logger.removeHandler(handler)

    logger.remove()
    logger.add(sys.stderr, level=level, enqueue=True)

    loop.set_exception_handler(loguru_exc_callback_async)
    traceback.print_exception = loguru_exc_callback
