import logging
from logging.handlers import RotatingFileHandler


class SingletonLogger:
    """
    SingletonLogger Class

    The `SingletonLogger` class provides a singleton implementation of a logger using Python's logging module. This ensures that only one instance of the logger is created, which can be used across different modules for consistent logging.

    Attributes:
        _instance (SingletonLogger): The singleton instance of the logger.
        name (str): The name of the logger.
        log_file (str): The file path for the log file.
        logger (logging.Logger): The logger instance.

    Methods:
        __new__(cls, name=__name__, log_file="app.log"):
            Creates a new instance of SingletonLogger if it does not already exist, and sets up the logging handlers.
            :param name: The name of the logger.
            :param log_file: The file path for the log file.
            :return: The singleton logger instance.

        _setup_handlers(self):
            Sets up the logging handlers (file and console) and formatters for the logger.

    Usage:
        logger = SingletonLogger()
        logger.info("This is an info message")
    """
    _instance = None

    def __new__(cls, name=__name__, log_file="app.log"):
        if cls._instance is None:
            # Erstellen einer neuen Instanz
            cls._instance = super(SingletonLogger, cls).__new__(cls)
            cls._instance._initialized = False
            cls._instance.name = name
            cls._instance.log_file = log_file
            cls._instance.logger = logging.getLogger(name)
            cls._instance.logger.setLevel(logging.INFO)
            cls._instance._setup_handlers()
            cls._instance._initialized = True
        return cls._instance.logger

    def _setup_handlers(self):
        # File handler
        file_handler = RotatingFileHandler(self.log_file, maxBytes=2000000000, backupCount=5)
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

