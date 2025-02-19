# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: py:light
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

"""
displayfile is used to display certain types of files.
The module lets us preview a file, open a file, and open its directory.

Example:
    ::#

        from ipyautoui.constants import load_test_constants
        from ipyautoui.displayfile import DisplayFile, Markdown
        import ipywidgets as widgets

        DIR_FILETYPES = load_test_constants().DIR_FILETYPES

        fpths = list(pathlib.Path(DIR_FILETYPES).glob("*"))

        # single file
        d = DisplayFile(fpths[7])
        display(d)

"""
# %run __init__.py
# %load_ext lab_black
# TODO: update displayfile_definitions based on the extra work done...
# +
import pathlib
import functools
from wcmatch.pathlib import Path as wcPath
from IPython.display import (
    display,
    clear_output,
    Markdown,
)  # , Image JSON, HTML, IFrame,
import time
import typing
import ipywidgets as widgets
import traitlets
from pydantic import BaseModel, validator, HttpUrl

#  local imports
from ipyautoui.autodisplayfile_renderers import (
    DEFAULT_FILE_RENDERERS,
    handle_compound_ext,
)
from ipyautoui._utils import (
    open_file,
    make_new_path,
    frozenmap,
    get_ext,
    st_mtime_string,
)
from ipyautoui.constants import (
    #  BUTTON_WIDTH_MIN,
    BUTTON_HEIGHT_MIN,
    KWARGS_OPENPREVIEW,
    KWARGS_OPENFILE,
    KWARGS_OPENFOLDER,
    KWARGS_DISPLAY_ALL_FILES,
    KWARGS_COLLAPSE_ALL_FILES,
    KWARGS_HOME_DISPLAY_FILES,
)

# from mf library
# try:
#     from xlsxtemplater import from_excel
# except:
#     pass


# -


def merge_file_renderers(merge_renderers, default_renderers=DEFAULT_FILE_RENDERERS):
    ext_map = {**dict(default_renderers), **merge_renderers}
    return frozenmap(**ext_map)


# +
class DisplayObjectActions(BaseModel):
    """base object with callables for creating a display object"""

    map_renderers: frozenmap = DEFAULT_FILE_RENDERERS
    path: typing.Union[str, pathlib.Path, HttpUrl]
    ext: str = None
    name: str = None
    check_exists: typing.Callable = None
    renderer: typing.Callable = lambda: print("renderer")
    check_date_modified: typing.Callable = None

    class Config:
        arbitrary_types_allowed = True


def check_exists(path):
    if path.is_file() or path.is_dir():
        return True
    else:
        return False


class DisplayFromPath(DisplayObjectActions):
    newroot: pathlib.PureWindowsPath = pathlib.PureWindowsPath("J:/")
    path_new: pathlib.Path = None
    open_file: typing.Callable = None
    open_folder: typing.Callable = None

    @validator("path", always=True)
    def _path(cls, v, values):
        return pathlib.Path(v)

    @validator("path_new", always=True)
    def _path_new(cls, v, values):
        return make_new_path(values["path"], newroot=values["newroot"])
    
    @validator("name", always=True)
    def _name(cls, v, values):
        if values["path"] is not None:
            v = values["path"].name
        return v

    @validator("renderer", always=True)
    def _renderer(cls, v, values):
        ext = values["ext"]
        map_ = values["map_renderers"]
        if ext in map_.keys():
            fn = functools.partial(map_[ext], values["path"])
        else:
            fn = lambda: widgets.HTML("File renderer not found")
        return fn

    @validator("ext", always=True)
    def _ext(cls, v, values):
        if values["path"] is not None:
            v = get_ext(values["path"])
            v = handle_compound_ext(v, map_renderers=values["map_renderers"])
        if v is None:
            ValueError("ext must be given to map data to renderer")
        return v

    @validator("check_exists", always=True)
    def _check_exists(cls, v, values):
        fn = functools.partial(check_exists, values["path"])
        return fn

    @validator("check_date_modified", always=True)
    def _date_modified(cls, v, values):
        p = values["path"]
        if p is not None:
            fn = functools.partial(st_mtime_string, p)
        return fn

    @validator("open_file", always=True)
    def _open_file(cls, v, values):
        p = values["path"]
        if p is not None:
            fn = functools.partial(open_file, p, newroot=values["newroot"])
        return fn

    @validator("open_folder", always=True)
    def _open_folder(cls, v, values):
        p = values["path"]
        if not p.is_dir():
            p = p.parent
        if p is not None:
            fn = functools.partial(open_file, p, newroot=values["newroot"])
        return fn

    class Config:
        arbitrary_types_allowed = True


# TODO: create a DisplayFromRequest actions. for use with API queries...?
class DisplayFromRequest(DisplayObjectActions):
    pass


# -

# TODO: separate out the bit that is display data and display from path...
# TODO: probs useful to have a `value` trait (allowing the object to be updated instead of remade)
#       this probably means having DisplayObject as a base class and extending it for display file... 
class DisplayObject(widgets.VBox):

    auto_open = traitlets.Bool(default_value=False)
    show_openfile = traitlets.Bool(default_value=True)
    show_openfolder = traitlets.Bool(default_value=True)
    show_exists = traitlets.Bool(default_value=True)
    show_openpreview = traitlets.Bool(default_value=True)
    # TODO: 
    # maybe we don't actually need the "show_" traits 
    # as stuff can be hidden using "order"...
    
    order = traitlets.Tuple()

    @traitlets.observe("auto_open")
    def _observe_auto_open(self, change):
        if change["new"]:
            self.openpreview.value = True
        else:
            self.openpreview.value = False

    @traitlets.observe("show_openfile")
    def _observe_show_openfile(self, change):
        if change["new"] and self.display_actions.open_file():
            self.openfile.layout.display = ""
        else:
            self.openfile.layout.display = "None"

    @traitlets.observe("show_openfolder")
    def _observe_show_openfolder(self, change):
        if change["new"]:
            self.openfolder.layout.display = ""
        else:
            self.openfolder.layout.display = "None"

    @traitlets.observe("show_exists")
    def _observe_exists(self, change):
        if change["new"]:
            self.exists.layout.display = ""
        else:
            self.exists.layout.display = "None"

    @traitlets.observe("show_openpreview")
    def _observe_show_openpreview(self, change):
        if change["new"]:
            self.openpreview.layout.display = ""
        else:
            self.openpreview.layout.display = "None"

    @traitlets.validate("order")
    def _validate_order(self, proposal):
        for l in proposal["value"]:
            if l not in self.default_order:
                raise ValueError(
                    """
                    order must include the following: ("exists", "openpreview", "openfile", "openfolder", "name")
                """
                )
        return proposal["value"]

    @traitlets.observe("order")
    def _observe_order(self, change):
        self.bx_bar.children = [getattr(self, l) for l in change["new"]]

    def __init__(
        self,
        display_actions: typing.Type[DisplayObjectActions],
        auto_open=False,
    ):
        self.default_order = ("exists", "openpreview", "openfile", "openfolder", "name")
        self.display_actions = display_actions
        self._init()
        self.auto_open = auto_open
        self.order = self.default_order

    def _init(self):
        super().__init__()
        self._init_form()
        self._init_controls()

    @classmethod
    def from_path(
        cls,
        path,
        newroot=pathlib.PureWindowsPath("J:/"),
        file_renderers=None,
        auto_open=False,
    ):
        if file_renderers is not None:
            file_renderers = merge_file_renderers(file_renderers)
        else:
            file_renderers = DEFAULT_FILE_RENDERERS
        display_actions = DisplayFromPath(
            path=path, newroot=newroot, map_renderers=file_renderers
        )
        return cls(display_actions, auto_open=auto_open)

    # TODO: create a from_request classmethod
    @classmethod
    def from_request(cls, path):
        pass

    def tooltip_openpath(self, path):
        return str(make_new_path(path, newroot=self.display_actions.newroot))

    def _init_form(self):
        self.exists = widgets.Valid(
            value=False,
            disabled=True,
            readout="-",
            tooltip="indicates if file exists",
            layout=widgets.Layout(width="20px", height=BUTTON_HEIGHT_MIN),
        )
        self.openpreview = widgets.ToggleButton(**KWARGS_OPENPREVIEW)
        self.openfile = widgets.Button(**KWARGS_OPENFILE)
        self.openfolder = widgets.Button(**KWARGS_OPENFOLDER)
        self.name = widgets.HTML(
            "<b>{0}</b>".format(self.display_actions.name),
            layout=widgets.Layout(justify_items="center"),
        )
        self.out_caller = widgets.Output()
        self.out = widgets.Output()
        self.out_caller.layout.display = "none"
        self.out.layout.display = "none"
        self.bx_bar = widgets.HBox()
        if isinstance(self.display_actions.path, pathlib.PurePath):
            self.openfile.tooltip = f"""
open file:
{self.tooltip_openpath(self.display_actions.path)}
"""
            self.openfolder.tooltip = f"""
open folder:
{self.tooltip_openpath(self.display_actions.path.parent)}
"""
        self.bx_out = widgets.VBox()
        self.bx_out.children = [self.out_caller, self.out]
        self.children = [self.bx_bar, self.bx_out]
        self.check_exists()

    def _init_controls(self):
        self.openfile.on_click(self._openfile)
        self.openfolder.on_click(self._openfolder)
        self.openpreview.observe(self._openpreview, names="value")

    def check_exists(self):
        if self.display_actions.check_exists is None:
            self.exists.value = False
        elif not self.display_actions.check_exists():
            self.exists.value = False
        elif self.display_actions.check_exists():
            self.exists.value = True
        else:
            raise ValueError("check_exists error")

    def _openpreview(self, onchange):
        if self.openpreview.value:
            self.openpreview.icon = "eye-slash"
            self.out.layout.display = ""

            with self.out:
                if (
                    hasattr(self.display_actions, "path")
                    and self.display_actions.check_exists()
                ):
                    display(self.display_actions.renderer())
                else:
                    display(Markdown("file does not exist"))
        else:
            self.openpreview.icon = "eye"
            self.out.layout.display = "none"
            with self.out:
                clear_output()

    def _openfile(self, sender):
        self.out_caller.layout.display = ""
        with self.out_caller:
            clear_output()
            self.display_actions.open_file()
            time.sleep(5)
            clear_output()
        self.out_caller.layout.display = "none"

    def _openfolder(self, sender):
        self.out_caller.layout.display = ""
        with self.out_caller:
            clear_output()
            self.display_actions.open_folder()
            time.sleep(5)
            clear_output()
        self.out_caller.layout.display = "none"


if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from ipyautoui.autoui import AutoUi
    from ipyautoui.constants import load_test_constants

    tests_constants = load_test_constants()
    DIR_FILETYPES = load_test_constants().DIR_FILETYPES
    paths = list(pathlib.Path(DIR_FILETYPES).glob("*"))
    path = paths[6]
    d = DisplayObject.from_path(path)
    display(d)

if __name__ == "__main__":
    d.order = ("exists", "name", "openpreview", "openfile", "openfolder")
    d.show_exists = False

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic

    user_file_renderers = AutoUi.create_autodisplay_map(
        ext=".aui.json", schema=TestAutoLogic
    )
    path1 = tests_constants.PATH_TEST_AUI

    d = DisplayObject.from_path(path1, file_renderers=user_file_renderers)
    display(d)


class AutoDisplay(traitlets.HasTraits):
    """
    displays the contents of a file in the notebook.
    comes with the following default renderers:
    DEFAULT_FILE_RENDERERS = {
        '.csv': csv_prev,
        '.json': json_prev,
        '.plotly': plotlyjson_prev,
        '.plotly.json': plotlyjson_prev,
        '.vg.json': vegajson_prev,
        '.vl.json': vegalitejson_prev,
        '.ipyui.json': ipyuijson_prev,
        '.yaml': yaml_prev,
        '.yml': yaml_prev,
        '.png': img_prev,
        '.jpg': img_prev,
        '.jpeg': img_prev,
        #'.obj': obj_prev, # add ipyvolume viewer?
        '.txt': txt_prev,
        '.md': md_prev,
        '.py': py_prev,
        '.pdf': pdf_prev,
    }
    user_file_renderers can be passed to class provided they have the correct
    dict format: user_file_renderers = {'.ext': myrenderer}
    notice that the class allows for "compound" filetypes, especially useful for .json files
    if you want to display the data in a specific way.
    """

    #     _paths = traitlets.List()

    #     @validate("_paths")
    #     def _valid_value(self, proposal):
    #         """makes path a wcmatch.Path (for enhanced pattern matching) and filters out directories"""
    #         return [wcPath(p) for p in proposal["value"] if not pathlib.Path(p).is_dir()]

    def __init__(
        self,
        display_objects_actions: typing.List[DisplayObjectActions],
        patterns: typing.Union[str, typing.List] = None,
        title: str = None,
        display_showhide: bool = True,
    ):
        """


        Args:
            paths (typing.List[pathlib.Path]): list of paths to display
            default_file_renderers: default renderers
            user_file_renderers: default = {}, custom user-defined file renderers
            newroot: passed to open_file
            patterns: (str or list), patterns to auto-open
            title: (str), dfeault = None,


        """
        self._init_form()
        self._init_controls()
        self.title = title
        self._display_objects_actions = display_objects_actions

        self.display_objects_actions = display_objects_actions
        self.display_showhide = display_showhide
        self.patterns = patterns

    @classmethod
    def from_paths(
        cls,
        paths: typing.List[pathlib.Path],
        newroot=pathlib.PureWindowsPath("J:/"),
        file_renderers=None,
        patterns: typing.Union[str, typing.List] = None,
        title: str = None,
        display_showhide: bool = True,
    ):
        if file_renderers is not None:
            file_renderers = merge_file_renderers(file_renderers)
        else:
            file_renderers = DEFAULT_FILE_RENDERERS
        if not isinstance(paths, list):
            paths = [pathlib.Path(paths)]

        display_objects_actions = [
            DisplayFromPath(path=path, newroot=newroot, map_renderers=file_renderers)
            for path in paths
        ]
        return cls(
            display_objects_actions,
            patterns=patterns,
            title=title,
            display_showhide=display_showhide,
        )

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        if self.title is None:
            self.box_title.children = []
        else:
            self.box_title.children = [widgets.HTML(self.title)]

    @property
    def display_showhide(self):
        return self._display_showhide

    @display_showhide.setter
    def display_showhide(self, value):
        if hasattr(self, "display_objects") and len(self.display_objects) == 1:
            value = False
        self._display_showhide = value
        if self.display_showhide:
            self.box_showhide.children = [
                widgets.HBox(
                    layout=widgets.Layout(width="24px", height=BUTTON_HEIGHT_MIN)
                ),
                self.b_display_all,
                self.b_collapse_all,
                self.b_display_default,
            ]
        else:
            self.box_showhide.children = []

    @property
    def paths(self):
        return [
            wcPath(d.path) for d in self.display_objects_actions
        ]  # self._paths  # [d.path for d in self.display_objects]

    @property
    def display_objects_actions(self):
        return self._display_objects_actions

    @display_objects_actions.setter
    def display_objects_actions(self, display_objects_actions):
        self._display_objects_actions = display_objects_actions
        self.display_objects = [DisplayObject(d) for d in display_objects_actions]

        self.box_files.children = self.display_objects

    @property
    def patterns(self):
        return self._patterns

    @patterns.setter
    def patterns(self, value):
        self._patterns = value
        if value is None:
            self.b_display_default.layout.display = "None"
            self.auto_open = [False] * len(self.paths)
        else:
            self.auto_open = [p.match(value) for p in self.paths]
            if sum(self.auto_open) == len(self.paths):
                self.b_display_default.layout.display = "None"
            else:
                self.b_display_default.layout.display = ""

    @property
    def auto_open(self):
        return [d.auto_open for d in self.display_objects]

    @auto_open.setter
    def auto_open(self, value):
        [
            setattr(d, "auto_open", v)
            for d, v in dict(zip(self.display_objects, value)).items()
        ]

    def _init_form(self):
        self.b_display_all = widgets.Button(**KWARGS_DISPLAY_ALL_FILES)
        self.b_collapse_all = widgets.Button(**KWARGS_COLLAPSE_ALL_FILES)
        self.b_display_default = widgets.Button(**KWARGS_HOME_DISPLAY_FILES)
        self.box_header = widgets.VBox()
        self.box_showhide = widgets.HBox()
        self.box_title = widgets.HBox()
        self.box_header.children = [self.box_title, self.box_showhide]
        self.box_files = widgets.VBox()
        self.box_form = widgets.VBox()
        self.box_form.children = [self.box_header, self.box_files]

    def _init_controls(self):
        self.b_display_all.on_click(self.display_all)
        self.b_collapse_all.on_click(self.collapse_all)
        self.b_display_default.on_click(self.display_default)

    def display_all(self, onclick=None):
        for d in self.display_objects:
            d.openpreview.value = True

    def collapse_all(self, onclick=None):
        for d in self.display_objects:
            d.openpreview.value = False

    def display_default(self, onclick=None):
        for d, a in zip(self.display_objects, self.auto_open):
            d.openpreview.value = a

    def display(self):
        display(self.box_form)

    def _ipython_display_(self):
        self.display()

    def _activate_waiting(self):
        [d._activate_waiting() for d in self.display_objects]

    def _update_files(self):
        [d._update_file() for d in self.display_objects]


# +
# TODO: render markdown to html using pandoc and rebase relative paths - https://github.com/jgm/pandoc/issues/3752
# TODO: render Vega updating the data path
# TODO: render pdf update the relative path
# TODO: figure out why the spacing between rows is weird

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from ipyautoui.autoui import AutoUi
    from ipyautoui.constants import load_test_constants

    tests_constants = load_test_constants()
    DIR_FILETYPES = load_test_constants().DIR_FILETYPES
    paths = list(pathlib.Path(DIR_FILETYPES).glob("*"))
    ad = AutoDisplay.from_paths(
        paths, newroot=pathlib.PureWindowsPath("C:/")  # , patterns="*.csv"
    )
    display(ad)
# -
if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic

    user_file_renderers = AutoUi.create_autodisplay_map(
        ext=".aui.json", schema=TestAutoLogic
    )

    test_ui = AutoDisplay.from_paths(
        paths=[tests_constants.PATH_TEST_AUI],
        file_renderers=user_file_renderers,
        display_showhide=False,
    )

    display(test_ui)
