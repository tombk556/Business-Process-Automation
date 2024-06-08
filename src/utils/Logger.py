import logging
from logging.handlers import RotatingFileHandler


class SingletonLogger:
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

