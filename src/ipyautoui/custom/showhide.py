# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %run __init__.py
# %run ../__init__.py
# %load_ext lab_black

# +
import traitlets_paths
import ipywidgets as widgets
import traitlets as t
from IPython.display import clear_output, display
from ipyautoui.constants import KWARGS_COLLAPSE, KWARGS_DISPLAY
import typing


class ShowHide(widgets.VBox):
    """simple show/hide widget that displays output of a callable that is pass as the input"""

    fn_display = t.Callable()
    title = t.Unicode()

    @t.default("fn_display")
    def _fn_display(self):
        return lambda: print("display")

    def __init__(
        self,
        fn_display: typing.Callable = lambda: widgets.HTML("😲"),
        title: str = "title",
        auto_open: bool = False,
        button_width: str = None,
    ):
        """
        Args:
            fn_display: widget our output to display. it is displayed like this:
                `display(self.fn_display())`
            title: 
        """
        self.button_width = button_width
        self._init_form()
        self.fn_display = fn_display
        self.title = title
        if auto_open:
            self.btn_display.value = True
        if button_width is not None:
            self.btn_display.layout.width = "300px"

    def _init_form(self):
        super().__init__(layout=widgets.Layout(border="solid LightCyan 2px"))
        self.hbx_title = widgets.HBox()
        self.btn_display = widgets.ToggleButton(**KWARGS_DISPLAY)
        if self.button_width is not None:
            self.btn_display.layout.width = self.button_width
        self.html_title = widgets.HTML()
        self.out = widgets.Output()
        self.out.layout.display = "None"
        self.hbx_title.children = [self.btn_display, self.html_title]
        self.children = [self.hbx_title, self.out]
        self._observe_fn_display("asd")

    @t.observe("title")
    def _observe_title(self, change):
        self.html_title.value = self.title

    @t.observe("fn_display")
    def _observe_fn_display(self, change):
        self.btn_display.unobserve(None)
        self.btn_display.observe(self.display_out, "value")

    def display_out(self, click):
        with self.out:
            if self.btn_display.value:
                {
                    setattr(self.btn_display, k, v)
                    for k, v in KWARGS_COLLAPSE.items()
                    if k != "layout"
                }
                self.out.layout.display = ""
                clear_output()
                display(self.fn_display())
            else:
                {
                    setattr(self.btn_display, k, v)
                    for k, v in KWARGS_DISPLAY.items()
                    if k != "layout"
                }
                self.out.layout.display = "None"
                clear_output()
# -
if __name__ == "__main__":
    d = ShowHide(auto_open=True)
    display(d)
