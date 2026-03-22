from logging import Handler, LogRecord

from tqdm import tqdm


class TqdmWriteLogHandler(Handler):
    def emit(self, record: LogRecord) -> None:
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)
