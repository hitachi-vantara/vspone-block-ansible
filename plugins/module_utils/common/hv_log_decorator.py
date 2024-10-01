import inspect
import os.path

try:
    from ..common.hv_log import Log
except ImportError:
    from common.hv_log import Log

from functools import wraps

logger = Log()


class LogDecorator:
    """Class containing logging functionalities and decorators."""

    @staticmethod
    def log(self, message):
        caller_frame = inspect.stack()[2]
        filename = os.path.basename(caller_frame.filename)
        line_number = caller_frame.lineno
        logger.writeDebug(
            f"{filename}:{self.__class__.__name__}.{self._current_method}:[{line_number}] {message}"
        )

    @staticmethod
    def truncate_string(s, length):
        return (s[:length] + "...") if len(s) > length else s

    @classmethod
    def debug_methods(cls, target_class):
        """Class decorator to add logging to all methods of the target class."""

        def loggable_method(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                self._current_method = func.__name__
                arg_list = [repr(a) for a in args]
                arg_list += [f"{k}={v!r}" for k, v in kwargs.items()]
                LogDecorator.log(self, f"ENTER: Params:({', '.join(arg_list)})")
                # arg_list = [f"{k}={v!r}" for k, v in kwargs.items()]
                # arg_list += [f"arg{i}={a!r}" for i, a in enumerate(args)]
                # LogDecorator.log(self, f"ENTER: Params:({', '.join(arg_list)})")

                # _self = args[0]  # Extract 'self' from args
                # self._current_method = func.__name__
                # sig = inspect.signature(func)
                # arg_list = []
                # bound_args = sig.bind(*args, **kwargs)
                # for param_name, param_value in bound_args.arguments.items():
                #     if param_name != 'self':  # Exclude 'self' from the log message
                #         arg_list.append(f"{param_name}={param_value!r}")
                # LogDecorator.log(self, f"ENTER: Params:({', '.join(arg_list)})")

                result = func(self, *args, **kwargs)

                if isinstance(result, bytes):
                    LogDecorator.log(
                        self, f"EXIT: Result is a bytes object and cannot be logged."
                    )
                elif isinstance(result, str):
                    max_chars = 1000
                    if len(result) > max_chars:
                        result = LogDecorator.truncate_string(result, max_chars)
                        LogDecorator.log(
                            self, f"EXIT: Result:   .....truncated"
                        )
                    LogDecorator.log(self, f"EXIT:")
                else:
                    LogDecorator.log(self, f"EXIT: ")
                return result

            return wrapper

        for attribute_name, attribute in vars(target_class).items():
            if callable(attribute) and not attribute_name.startswith("__"):
                setattr(target_class, attribute_name, loggable_method(attribute))
        return target_class
