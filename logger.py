import logging
import logging.config

class Logger:
    def __init__(self, moduleName:str ,loggerType = 'root'):
        
        logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
        self.logger = logging.getLogger(loggerType)
        self.logger.info("{} Logger Initiated".format(moduleName))
        self.moduleName = moduleName

    def debug(self, logMessage:str):
        self.logger.debug("| {} | {}".format(self.moduleName,logMessage))
        return

    def info(self, logMessage:str):
        self.logger.info("| {} | {}".format(self.moduleName,logMessage))
        return

    def warning(self, logMessage:str):
        self.logger.warning("| {} | {}".format(self.moduleName,logMessage))
        return

    def error(self, logMessage:str):
        self.logger.error("| {} | {}".format(self.moduleName,logMessage),exc_info= True)
        return 

    def critical(self, logMessage:str):
        self.logger.critical("| {} | {}".format(self.moduleName,logMessage),exc_info= True)
        return 