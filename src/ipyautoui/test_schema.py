"""
An example schema definition that demonstrates the current capability of the AutoUi class
"""
import typing
from enum import Enum
from pydantic import Field, conint, constr
from ipyautoui.basemodel import BaseModel
from pydantic.color import Color
from datetime import datetime, date
import pathlib
import pandas as pd
from pathlib import PurePosixPath

# from ipyautoui.custom.modelrun import RunName

STR_MARKDOWN = """
See details here: [__commonmark__](https://commonmark.org/help/)

or press the question mark button. 
"""

DATAGRID_TEST_VALUE = [
    {
        "string": "important string",
        "integer": 1,
        "floater": 3.14,
        "something_else": 324,
    },
    {"string": "update", "integer": 4, "floater": 3.12344, "something_else": 123},
    {"string": "evening", "integer": 5, "floater": 3.14, "something_else": 235},
    {"string": "morning", "integer": 5, "floater": 3.14, "something_else": 12},
    {"string": "number", "integer": 3, "floater": 3.14, "something_else": 123},
]



class NestedObject(BaseModel):
    """description in docstring"""

    string1: str = Field(default="adsf", description="a description about my string")
    int_slider1: conint(ge=0, le=3) = 2
    int_text1: int = 1


class RecursiveNest(BaseModel):
    """description in RecursiveNest docstring"""

    string1: str = Field(default="adsf", description="a description about my string")
    int_slider1: conint(ge=0, le=3) = 2
    int_text1: int = 1
    nested: NestedObject = Field(default=None)


class DataFrameCols(BaseModel):
    string: str = Field("string", aui_column_width=100)
    integer: int = Field(1, aui_column_width=80)
    floater: float = Field(3.1415, aui_column_width=70, aui_sig_fig=3)
    something_else: float = Field(324, aui_column_width=100)


class TestDataFrame(BaseModel):
    """a description of TestDataFrame"""

    dataframe: typing.List[DataFrameCols] = Field(
        default_factory=lambda: [], format="dataframe"
    )
    
class GenderEnum(str, Enum):
    """available genders. this is just an example."""

    male = "male"
    female = "female"
    other = "other"
    not_given = "not_given"


class TestAutoLogicSimple(BaseModel):
    """this is a test UI form to demonstrate how pydantic class can be used to generate an ipywidget input form. 
    only simple datatypes used (i.e. not lists/arrays or objects)
    """

    string: str = Field(default="adsf", description="a description about my string")
    int_slider: conint(ge=0, le=3) = 2
    int_text: int = 1
    int_range_slider: tuple[int, int] = Field(default=(0, 3), ge=0, le=4)  # check
    float_slider: float = Field(default=2.2, ge=0, le=3)
    float_text: float = 2.2
    float_text_locked: float = Field(default=2.2, disabled=True)
    float_range_slider: tuple[float, float] = Field(default=(0, 2.2), ge=0, le=3.5)
    checkbox: bool = True
    dropdown: GenderEnum = None
    dropdown_edge_case: GenderEnum = Field(
        default=GenderEnum.female, description="updated description"
    )
    dropdown_simple: str = Field(default="asd", enum=["asd", "asdf"])
    combobox: str = Field(
        default="asd", enum=["asd", "asdf"], autoui="ipyautoui.autowidgets.Combobox",
    )
    text: constr(min_length=0, max_length=20) = "short text"
    text_area: constr(min_length=0, max_length=800) = Field(
        "long text " * 50, description="long text field"
    )
    markdown: str = Field(
        STR_MARKDOWN, description="markdown widget!", format="markdown"
    )
    # file_chooser: pathlib.Path = pathlib.Path(".") # TODO: serialisation / parsing round trip not working...


class TestTypesWithComplexSerialisation(BaseModel):
    """all of these types need to be serialised to json and parsed back to objects upon reading..."""

    file_chooser: pathlib.Path = pathlib.Path(
        "."
    )  # TODO: serialisation / parsing round trip not working...
    date_picker: typing.Optional[
        date
    ] = date.today()  # TODO: serialisation / parsing round trip not working...
    datetime_picker: typing.Optional[
        datetime
    ] = datetime.now()  # TODO: update with ipywidgets-v8
    color_picker_ipywidgets: Color = "#f5f595"


class TestAutoLogic(TestAutoLogicSimple):
    """this is a test UI form to demonstrate how pydantic class can be used to generate an ipywidget input form"""

    complex_serialisation: TestTypesWithComplexSerialisation = Field(default=None)
    select_multiple_non_constrained: typing.List[GenderEnum] = Field(
        default=["male", "female"],
        description="select multiple, non-constrained, allows duplicates",
    )  # TODO: make this work. requires handling the "anyOf" JSON link
    select_multiple_from_list: typing.List[str] = Field(
        default=["male", "female"],
        enum=["male", "female", "other", "not_given"],
        description="simple select multiple from list",
    )
    # select_multiple_search: typing.List[str] = Field(
    #     default=["male", "female"],
    #     enum=["male", "female", "other", "not_given"],
    #     autoui="ipyautoui.custom.multiselect_search.MultiSelectSearch",
    # )
    # FIXME: Needing refactor or cleanup -@jovyan at 8/23/2022, 10:28:36 PM
    # select_multiple_search needs a wrapper that calls it from a schema var

    array: typing.List[str] = Field(default=[], max_items=5)
    objects_array: typing.List[NestedObject] = Field(default=[], max_items=5)
    # file_upload # TODO: how best to implement this? could auto-save to another location...
    run_name: str = Field(
        default="000-lean-description", autoui="ipyautoui.autowidgets.RunName", zfill=3,
    )
    datagrid: typing.List[DataFrameCols] = Field(
        default=DATAGRID_TEST_VALUE,
        # default_factory=lambda: DATAGRID_TEST_VALUE, # TODO: AutoUi isn't getting data when set using default_factory. make this work!
        format="DataFrame",
    )
    # datagrid_from_dataframe: str = Field(
    #     default=pd.DataFrame.from_dict({"test": [0, 1], "df": [1, 2]}),
    #     format="DataFrame",
    # )
    nested: NestedObject = Field(default=None)
    recursive_nest: RecursiveNest = Field(default=None)

    class Config:
        json_encoders = {PurePosixPath: str}


class TestObjects(BaseModel):
    string: str = Field(default="adsf", description="a description about my string")
    nested: NestedObject = Field(default=None)
    recursive_nest: RecursiveNest = Field(default=None)


class TestArrays(BaseModel):
    array_strings: typing.List[str] = Field(
        default=["f", "d"], max_items=5, min_items=2
    )
    array_strings1: typing.List[str] = Field(default=[], max_length=5, min_length=2)
    array_objects: typing.List[NestedObject] = Field(default=[], max_items=5)
    # array_mixed: typing.List[typing.Union[NestedObject, str]] = Field(default=[], max_items=5)
    # TODO: do we want to support this?


class TestVjsf(BaseModel):
    objects_array_styled: typing.List[NestedObject] = Field(
        description="styled array, only works with AutoVjsf",
        default=[],
        max_items=5,
        x_itemTitle="titleProp",
        x_options={"arrayItemCardProps": {"outlined": True}},
    )
    color_picker_vjsf: str = Field(
        default="#f5f595",
        format="hexcolor",
        description='a color. "format" field is required to make vjsf work',
    )
    color_picker_vjsf_swatches: str = Field(
        "#f5f595",
        format="hexcolor",
        description='a color. "format" field is required to make vjsf work',
        x_props={
            "showSwatches": True,
            "hideCanvas": True,
            "hideInputs": True,
            "hideModeSwitch": True,
        },
    )
