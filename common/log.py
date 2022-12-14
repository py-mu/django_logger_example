import logging
import os.path
from logging import config

from loguru import logger


# 1.ðï¸åå£°æä¸ä¸ªç±»ç»§æ¿logging.Handler(å¶ä½ä¸ä»¶åå¦çè¡£æ)
class InterceptTimedRotatingFileHandler(logging.Handler):
    """
    èªå®ä¹åå°æ¶é´åæ»æ¥å¿è®°å½å¨
    ç¼ºå°å½åç©ºé´
    """

    def __init__(self, filename, when='d', interval=1, backupCount=15, encoding="utf-8", delay=False, utc=False,
                 atTime=None, logging_levels="all"):
        super(InterceptTimedRotatingFileHandler, self).__init__()
        filename = os.path.abspath(filename)
        when = when.lower()
        # 2.ðï¸éè¦æ¬å°ç¨ä¸åçæä»¶ååä¸ºä¸åæ¥å¿çç­éå¨
        self.logger_ = logger.bind(sime=filename)
        self.filename = filename
        key_map = {
            'h': 'hour',
            'w': 'week',
            's': 'second',
            'm': 'minute',
            'd': 'day',
        }
        # æ ¹æ®è¾å¥æä»¶æ ¼å¼åæ¶é´åæ»è®¾ç«æä»¶åç§°
        rotation = "%d %s" % (interval, key_map[when])
        retention = "%d %ss" % (backupCount, key_map[when])
        time_format = "{time:%Y-%m-%d_%H-%M-%S}"
        if when == "s":
            time_format = "{time:%Y-%m-%d_%H-%M-%S}"
        elif when == "m":
            time_format = "{time:%Y-%m-%d_%H-%M}"
        elif when == "h":
            time_format = "{time:%Y-%m-%d_%H}"
        elif when == "d":
            time_format = "{time:%Y-%m-%d}"
        elif when == "w":
            time_format = "{time:%Y-%m-%d}"
        level_keys = ["info"]
        # 3.ðï¸æå»ºä¸ä¸ªç­éå¨
        levels = {
            "debug": lambda x: "DEBUG" == x['level'].name.upper() and x['extra'].get('sime') == filename,
            "error": lambda x: "ERROR" == x['level'].name.upper() and x['extra'].get('sime') == filename,
            "info": lambda x: "INFO" == x['level'].name.upper() and x['extra'].get('sime') == filename,
            "warning": lambda x: "WARNING" == x['level'].name.upper() and x['extra'].get('sime') == filename}
        # 4. ðï¸æ ¹æ®è¾åºæå»ºç­éå¨
        if isinstance(logging_levels, str):
            if logging_levels.lower() == "all":
                level_keys = levels.keys()
            elif logging_levels.lower() in levels:
                level_keys = [logging_levels]
        elif isinstance(logging_levels, (list, tuple)):
            level_keys = logging_levels
        for k, f in {_: levels[_] for _ in level_keys}.items():

            # 5.ðï¸ä¸ºé²æ­¢éå¤æ·»å sinkï¼èéå¤åå¥æ¥å¿ï¼éè¦å¤æ­æ¯å¦å·²ç»è£è½½äºå¯¹åºsinkï¼é²æ­¢å¶ä½¿ç¨ç§æï¼åå¤æ¨ªè·³ã
            filename_fmt = filename.replace(".log", "_%s_%s.log" % (time_format, k))
            # noinspection PyUnresolvedReferences,PyProtectedMember
            file_key = {_._name: han_id for han_id, _ in self.logger_._core.handlers.items()}
            filename_fmt_key = "'{}'".format(filename_fmt)
            if filename_fmt_key in file_key:
                continue
                # self.logger_.remove(file_key[filename_fmt_key])
            self.logger_.add(
                filename_fmt,
                retention=retention,
                encoding=encoding,
                level=self.level,
                rotation=rotation,
                compression="tar.gz",  # æ¥å¿å½æ¡£èªè¡åç¼©æä»¶
                delay=delay,
                enqueue=True,
                filter=f
            )

    def emit(self, record):
        try:
            level = self.logger_.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        # 6.ðï¸æå½åå¸§çæ æ·±åº¦åå°åçå¼å¸¸çå æ æ·±åº¦ï¼ä¸ç¶å°±æ¯å½åå¸§åçå¼å¸¸èæ æ³åæº¯
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        self.logger_.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def simple_log_injector(conf):
    """
    å¯¹åç½®æ¥å¿è¿è¡åå°
    ä¿®æ¹é»è®¤çlogging rootè¾åº
    """
    config.dictConfig(conf)
    logging.setLoggerClass(logging.getLogger('django').__class__)
    logging.root = logging.getLogger('django')