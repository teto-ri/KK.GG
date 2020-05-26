# API데이터 처리 로깅용 

import logging
import logging.handlers

def status():
    logger = logging.getLogger("status")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s")

    fileHandler = logging.FileHandler("status.log")
    streamHandler = logging.StreamHandler()

    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)