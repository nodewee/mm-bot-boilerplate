import logging
import traceback


def handle(blaze, error):
    logging.error(error, exc_info=True)
    print(error)
    print(traceback.format_exc())
