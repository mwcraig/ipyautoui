# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
"""simple set-up of outputting logging messages to widgets output."""
# %run __init__.py
# %run ../__init__.py
# %load_ext lab_black

import logging
import ipywidgets as w

# import logging.config
import yaml
from ipyautoui.constants import DELETE_BUTTON_KWARGS
from IPython.display import clear_output


# +
class Output(w.Output):
    def register_logger(self, logger, *args, **kwargs):
        """Registers a handler to given logger to send output to output widget"""

        class WidgetLogger(logging.Handler):
            """Class to implement a logging interface that outputs to the
            Output widget"""

            # have a class member to store the existing logger
            logger_instance = logging.getLogger("__name__")

            def __init__(self, output_widget, *args, **kwargs):
                # Initialize the Handler
                logging.Handler.__init__(self, *args)

                # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                # self.setFormatter(formatter)

                # save outer_instance
                self.output = output_widget

                # optional take format
                # setFormatter function is derived from logging.Handler
                for key, value in kwargs.items():
                    if "{}".format(key) == "format":
                        self.setFormatter(value)

                # make the logger send data to this class
                self.logger_instance.addHandler(self)

            def emit(self, record):
                """Overload of logging.Handler method"""

                record = self.format(record)
                self.output.outputs = (
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": (record + "\n"),
                    },
                ) + self.output.outputs

        logger.addHandler(WidgetLogger(self, *args, **kwargs))


class LoggingAccordion(w.Accordion):
    def __init__(
        self,
        loggers=None,
        logging_format=logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        title="Execution Log",
        **kwargs
    ):
        super().__init__(**kwargs)

        if loggers is None:
            loggers = [
                logging.getLogger(name) for name in logging.root.manager.loggerDict
            ]
        self.out = Output()
        [self.out.register_logger(l, format=logging_format) for l in loggers]
        self.bn_clear = w.Button(**DELETE_BUTTON_KWARGS)
        self.title_clear = w.HTML("<i><b>clear logs</b></i>")
        self.hbx_clear = w.HBox([self.bn_clear, self.title_clear])
        self.vbx = w.VBox([self.hbx_clear, self.out])

        self.children = [self.vbx]
        self.titles = (title,)
        self._init_controls()

    def _init_controls(self):
        self.bn_clear.on_click(self._clear_logs)

    def _clear_logs(self, on_click):
        with self.out:
            clear_output()


# -

if __name__ == "__main__":

    def div(a, b):
        try:
            c = a / b
            logger.debug("c = %s", c)
            return c
        except Exception as e:
            logger.error("Exception occurred", exc_info=True)

    class Ui(w.VBox):
        def __init__(self, loggers: list):
            self.a = w.IntText()
            self.b = w.IntText()
            self.c = w.IntText()
            self.out = Output()
            [
                self.out.register_logger(
                    logger,
                    format=logging.Formatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    ),
                )
                for logger in loggers
            ]
            self.acc = w.Tab(children=[self.out], titles=["Execution Log"])
            self.c.disabled = True
            self.div = w.Button(description="operate")
            self.div.on_click(self.on_div)
            super().__init__([self.a, self.b, self.c, self.div, self.acc])

        def on_div(self, b):
            self.c.value = div(self.a.value, self.b.value)

    logger = logging.getLogger(__name__)
    logger.info("This is a debug message")
    logger.level = "INFO"
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    # loggers = [l for l in loggers if "my" in l.name ] + [logger]
    ui = Ui(loggers=loggers)
    display(ui)

if __name__ == "__main__":

    def div(a, b):
        try:
            c = a / b
            logger.debug("c = %s", c)
            return c
        except Exception as e:
            logger.error("Exception occurred", exc_info=True)

    class Ui(w.VBox):
        def __init__(self, loggers: list = None):
            self.a = w.IntText()
            self.b = w.IntText()
            self.c = w.IntText()
            self.div = w.Button(description="operate")
            self.div.on_click(self.on_div)
            self.acc = LoggingAccordion(loggers=loggers)

            super().__init__([self.a, self.b, self.c, self.div, self.acc])

        def on_div(self, b):
            self.c.value = div(self.a.value, self.b.value)

    logger = logging.getLogger(__name__)
    logger.info("This is a debug message")
    logger.level = "INFO"
    ui = Ui()
    display(ui)


