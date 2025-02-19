"""contains packages global constants"""
import pathlib

from ipydatagrid import TextRenderer, Expr, VegaExpr
from ipyautoui._utils import frozenmap

# https://www.python.org/dev/peps/pep-0603/
# https://github.com/MagicStack/immutables
# ^
DIR_MODULE = pathlib.Path(__file__).parent
DIR_EXAMPLE = DIR_MODULE.parents[1] / "examples"
PATH_VJSF_TEMPLATE = DIR_MODULE / "vjsf.vue"

BUTTON_WIDTH_MIN = "44px"
BUTTON_WIDTH_MEDIUM = "90px"
BUTTON_HEIGHT_MIN = "25px"
ROW_WIDTH_MEDIUM = "120px"
ROW_WIDTH_MIN = "60px"
BUTTON_MIN_SIZE = frozenmap(width=BUTTON_WIDTH_MIN, height=BUTTON_HEIGHT_MIN)
# ---------------------------

TRUE_BUTTON_KWARGS = frozenmap(
    icon="check",
    style={"button_color": "lightgreen"},
    # button_style="success",
    tooltip="true",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=True,
)

FALSE_BUTTON_KWARGS = frozenmap(
    icon="times",
    style={"button_color": "tomato"},
    # button_style="success",
    tooltip="false",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=True,
)

DASH_BUTTON_KWARGS = frozenmap(
    icon="circle",
    style={"button_color": "lightyellow"},
    # button_style="success",
    tooltip="",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=True,
)
LOAD_BUTTON_KWARGS = frozenmap(
    icon="upload",
    # style={"button_color":"white"},
    button_style="info",
    layout={"width": BUTTON_WIDTH_MIN},
    disabled=False,
)
# ---------------------------
ADD_BUTTON_KWARGS = frozenmap(
    icon="plus",
    style={},
    button_style="success",
    tooltip="add item",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=False,
)
REMOVE_BUTTON_KWARGS = frozenmap(
    icon="minus",
    style={},
    button_style="danger",
    tooltip="remove item",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=False,
)
BLANK_BUTTON_KWARGS = frozenmap(
    icon="",
    style={"button_color": "white"},
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=True,
)

DOWNARROW_BUTTON_KWARGS = frozenmap(
    icon="arrow-down",
    layout={"width": "300px"},
    disabled=True,
    style={"button_color": "white"},
)


KWARGS_DATAGRID_DEFAULT = frozenmap(
    header_renderer=TextRenderer(
        vertical_alignment="top", horizontal_alignment="center",
    )
)

TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT = "solid yellow 2px"
OPEN_BN_COLOR = "white"
KWARGS_OPENPREVIEW = frozenmap(
    icon="eye",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    tooltip="preview",
    # button_style="warning", #"primary", "success", "info", "warning", "danger"
    style={"font_weight": "bold"},  # ,'button_color':OPEN_BN_COLOR
)
KWARGS_OPENFILE = frozenmap(
    icon="file",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    tooltip="open file with system software",
    style={"font_weight": "bold" } #, "button_color": OPEN_BN_COLOR},
)
KWARGS_OPENFOLDER = frozenmap(
    icon="folder",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    tooltip="open folder in file-browser",
    style={"font_weight": "bold"} #, "button_color": OPEN_BN_COLOR},
)

KWARGS_DISPLAY = frozenmap(
    icon="plus",
    tooltip="display all files",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=False,
)
KWARGS_DISPLAY_ALL_FILES = frozenmap(
    {**dict(KWARGS_DISPLAY), **{"tooltip": "display all files"}}
)

KWARGS_COLLAPSE = frozenmap(
    icon="minus",
    tooltip="collapse",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=False,
)
KWARGS_COLLAPSE_ALL_FILES = frozenmap(
    {**dict(KWARGS_COLLAPSE), **{"tooltip": "collapse all files"}}
)

KWARGS_HOME_DISPLAY_FILES = frozenmap(
    icon="home",
    tooltip="display default files",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    disabled=False,
)


# documentinfo ------------------------------
#  update this with WebApp data. TODO: delete this?
ROLES = (
    "Design Lead",
    "Project Engineer",
    "Engineer",
    "Project Coordinator",
    "Project Administrator",
    "Building Performance Modeller",
)

MAP_JSONSCHEMA_TO_IPYWIDGET = frozenmap(
    **{
        "minimum": "min",
        "maximum": "max",
        "enum": "options",
        "default": "value",
        "description": "autoui_description",
    }
)
#  ^ this is how the json-schema names map to ipywidgets.


def load_test_constants():
    """only in use for debugging within the package. not used in production code.

    Returns:
        module: test_constants object
    """
    from importlib.machinery import SourceFileLoader

    path_testing_constants = DIR_MODULE.parents[1] / "tests" / "constants.py"
    test_constants = SourceFileLoader(
        "constants", str(path_testing_constants)
    ).load_module()
    return test_constants


def display_template_ui_model():
    from ipyautoui import test_schema
    from ipyautoui.autodisplay import PreviewPy

    display(PreviewPy(test_schema, docstring_priority=False))


def DISPLAY_AUTOUI_EXAMPLE():
    display_template_ui_model()
