import logging

logging.PROGRESS = 21
logging.SUCCESS = 22
logging.addLevelName(logging.PROGRESS, "PROGRESS")
logging.addLevelName(logging.SUCCESS, "SUCCESS")
logging.progress = lambda msg, * args, ** kwargs: logging.log(logging.PROGRESS, msg, * args, ** kwargs)
logging.success = lambda msg, * args, ** kwargs: logging.log(logging.SUCCESS, msg, * args, ** kwargs)
