import logging

def startLogging(logFile):
    # formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
    formatter = logging.Formatter('%(levelname)s : %(message)s')
    
    fh = logging.FileHandler(logFile)
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)
    
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = []
    logger.addHandler(fh)
    logger.addHandler(sh)
    
    return logger


def stopLogging(logger):
    for handler in logger.handlers:
    	logger.removeHandler(handler)
    	handler.flush()
    	handler.close()
    return