import logging
from datetime import datetime
import settings

logging.basicConfig(level=logging.INFO,
                    filename=f'{settings.log_dir}/{datetime.today().strftime("%Y-%m-%d")}_full.log',
                    filemode="a",
                    format="[%(levelname)s] %(message)s",
                    datefmt='%H:%M:%S',
                    )


class DebugFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)

    def emit(self, record):
        if not record.levelno == logging.DEBUG:
            return
        super().emit(record)


class InfoFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)

    def emit(self, record):
        if not record.levelno == logging.INFO:
            return
        super().emit(record)


class WarringFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)

    def emit(self, record):
        if not record.levelno == logging.WARNING:
            return
        super().emit(record)


class ErrorFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)

    def emit(self, record):
        if not record.levelno == logging.ERROR:
            return
        super().emit(record)


class CriticalFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)

    def emit(self, record):
        if not record.levelno == logging.CRITICAL:
            return
        super().emit(record)


class StdoutFormatter(logging.Formatter):

    white = "\x1b[37m"
    green = "\x1b[32m"
    yellow = "\x1b[33;20m"
    red = "\x1b[35;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(levelname)s] %(message)s"  # (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: white + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(__name__)

# deb_hand = DebugFileHandler(f'{settings.log_dir}/{datetime.today().strftime("%Y-%m-%d")}_debug.log')
# deb_hand.setFormatter(logging.Formatter("%(message)s"))
# logger.addHandler(deb_hand)

inf_hand = InfoFileHandler(f'{settings.log_dir}/{datetime.today().strftime("%Y-%m-%d")}_info.log')
inf_hand.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(inf_hand)

war_hand = WarringFileHandler(f'{settings.log_dir}/{datetime.today().strftime("%Y-%m-%d")}_warnings.log')
war_hand.setFormatter(logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(message)s", '%H:%M:%S'))
logger.addHandler(war_hand)

err_hand = ErrorFileHandler(f'{settings.log_dir}/{datetime.today().strftime("%Y-%m-%d")}_warnings.log')
err_hand.setFormatter(logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(message)s", '%H:%M:%S'))
logger.addHandler(err_hand)

cri_hand = CriticalFileHandler(f'{settings.log_dir}/{datetime.today().strftime("%Y-%m-%d")}_warnings.log')
cri_hand.setFormatter(logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(message)s", '%H:%M:%S'))
logger.addHandler(cri_hand)

cons_hand = logging.StreamHandler()
cons_hand.setFormatter(StdoutFormatter())
logger.addHandler(cons_hand)



# for i in range(5):
#     logger.debug('DEEEEEEEEBBBBBBBBBBBUUUUUUUUUUGGGG')
#     logger.info('IIIIIIIIINNNNNNNNNNNNNFFFFFFFFOOOOOOO')
#     logger.warning('WWWWWWAAAAAAAARRRRRRRNNNNNNIIIIIIIIIINNNNNNNNGGGG')
#     logger.error('EEEEEEEERRRRRRRRRRROOOOOOOOOORRRRRRRR')
#     logger.critical('CCCRRRRIIITTTIIICCAAALL')
