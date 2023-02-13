# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
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

# +
"""General widget for editing data"""
# %run __init__.py
# %run ../__init__.py
# %load_ext lab_black
# TODO: move editgrid.py to root
import traitlets as tr
import typing as ty
import logging
import traceback
import pandas as pd
import ipywidgets as w
from IPython.display import clear_output
from markdown import markdown
from pydantic import BaseModel, Field

import ipyautoui.autoipywidget as aui
from ipyautoui.custom.buttonbars import CrudButtonBar
from ipyautoui._utils import frozenmap
from ipyautoui.constants import BUTTON_WIDTH_MIN
from ipyautoui.custom.autogrid import AutoGrid

MAP_TRANSPOSED_SELECTION_MODE = frozenmap({True: "column", False: "row"})
# TODO: rename "add" to "fn_add" so not ambiguous...

# +
import warnings

warnings.filterwarnings("ignore")
# REVIEW: Using for now as "No such comm" warning and "UserWarning: Index name of 'index' is not round-trippable" keep popping up.
# Should be resolved at a later date but will ignore for now as not crucial to fix
# -


class DataHandler(BaseModel):
    fn_get_all_data: ty.Callable
    fn_post: ty.Callable
    fn_patch: ty.Callable
    fn_delete: ty.Callable
    fn_copy: ty.Callable


if __name__ == "__main__":

    class TestModel(BaseModel):
        string: str = Field("string", title="Important String")
        integer: int = Field(40, title="Integer of somesort")
        floater: float = Field(1.33, title="floater")

    def test_save():
        print("Saved.")

    def test_revert():
        print("Reverted.")

    ui = aui.AutoObject(schema=TestModel)
    display(ui)

if __name__ == "__main__":
    ui.show_savebuttonbar = True
    display(ui.value)

if __name__ == "__main__":
    ui.value = {"string": "adfs", "integer": 2, "floater": 1.22}


class RowEditor:
    fn_add: ty.List[ty.Callable[[ty.Any, dict], None]]  # post
    fn_edit: ty.List[ty.Callable[[ty.Any, dict], None]]  # patch
    fn_move: ty.Callable
    fn_copy: ty.Callable
    fn_delete: ty.Callable


# +
class UiDelete(w.HBox):
    value = tr.Dict(default_value={})
    columns = tr.List(allow_none=True, default_value=None)

    @tr.observe("value")
    def observe_value(self, on_change):
        self._update_display()

    @tr.observe("columns")
    def observe_columns(self, on_change):
        if self.columns is not None:
            self.message_columns.value = f"columns shown: {str(self.columns)}"
        else:
            self.message_columns.value = "---"
        self._update_display()

    @property
    def value_summary(self):
        if self.columns is not None:
            return {
                k: {k_: v_ for k_, v_ in v.items() if k_ in self.columns}
                for k, v in self.value.items()
            }
        else:
            return self.value

    def _update_display(self):
        with self.out_delete:
            clear_output()
            display(self.value_summary)

    def __init__(self, fn_delete: ty.Callable = lambda: print("delete"), **kwargs):
        super().__init__(**kwargs)
        self.fn_delete = fn_delete
        self.out_delete = w.Output()
        self.bn_delete = w.Button(
            icon="exclamation-triangle",
            button_style="danger",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.vbx_messages = w.VBox()
        self.message = w.HTML(
            "⚠️<b>warning</b>⚠️ - <i>pressing button will permanently delete rows from"
            " grid</i>"
        )
        self.message_columns = w.HTML(f"---")
        self.vbx_messages.children = [
            self.message,
            self.message_columns,
            self.out_delete,
        ]
        self.children = [self.bn_delete, self.vbx_messages]
        self._init_controls()

    def _init_controls(self):
        self.bn_delete.on_click(self._bn_delete)

    def _bn_delete(self, onclick):
        self.fn_delete()


if __name__ == "__main__":
    delete = UiDelete()
    display(delete)
# -

if __name__ == "__main__":
    delete.value = {"key": {"col1": "value1", "col2": "value2"}}


# +
class UiCopy(w.HBox):
    index = tr.Integer()  # row index copying from... improve user reporting

    def __init__(
        self,
        fn_copy_beginning: ty.Callable = lambda: print(
            "duplicate selection to beginning"
        ),
        fn_copy_inplace: ty.Callable = lambda: print(
            "duplicate selection to below current"
        ),
        fn_copy_end: ty.Callable = lambda: print("duplicate selection to end"),
        fn_copy_to_selection: ty.Callable = lambda: print(
            "select new row/col to copy to"
        ),
        transposed: bool = False,
    ):
        super().__init__()
        self.fn_copy_beginning = fn_copy_beginning
        self.fn_copy_inplace = fn_copy_inplace
        self.fn_copy_end = fn_copy_end
        self.fn_copy_to_selection = fn_copy_to_selection
        self.map_action = {
            "duplicate selection to beginning": self.fn_copy_beginning,
            "duplicate selection to below current": self.fn_copy_inplace,
            "duplicate selection to end": self.fn_copy_end,
            "select new row/col to copy to": self.fn_copy_to_selection,
        }
        self.ui_copytype = w.RadioButtons(
            options=list(self.map_action.keys()),
            value="duplicate selection to end",
        )
        self.bn_copy = w.Button(
            icon="copy",
            button_style="success",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.vbx_messages = w.VBox()
        self.message = w.HTML("ℹ️ <b>Note</b> ℹ️ - <i>copy data from selected row")
        self.message_columns = w.HTML(f"---")
        self.vbx_messages.children = [
            self.message,
            self.message_columns,
            self.ui_copytype,
        ]
        self.children = [self.bn_copy, self.vbx_messages]
        self._init_controls()

    def _init_controls(self):
        self.bn_copy.on_click(self._bn_copy)

    def _bn_copy(self, onclick):
        self.map_action[self.ui_copytype.value]()


if __name__ == "__main__":
    display(UiCopy())


# -


class EditGrid(w.VBox):
    _value = tr.Tuple()  # using a tuple to guarantee no accidental mutation
    warn_on_delete = tr.Bool()
    show_copy_dialogue = tr.Bool()
    close_crud_dialogue_on_action = tr.Bool()

    @tr.observe("warn_on_delete")
    def observe_warn_on_delete(self, on_change):
        if self.warn_on_delete:
            self.ui_delete.layout.display = ""
        else:
            self.ui_delete.layout.display = "None"

    @tr.observe("show_copy_dialogue")
    def observe_show_copy_dialogue(self, on_change):
        if self.show_copy_dialogue:
            self.ui_copy.layout.display = ""
        else:
            self.ui_copy.layout.display = "None"

    @property
    def value(self):
        return self._value

    @property
    def transposed(self):
        return self.grid.transposed

    @transposed.setter
    def transposed(self, value: bool):
        self.grid.transposed = value

    def _update_value_from_grid(self):
        self._value = self.grid.records()

    @value.setter
    def value(self, value):
        if value == [] or value is None:
            self.grid.data = self.grid.get_default_data()
        else:
            self.grid.data = self.grid._init_data(pd.DataFrame(value))

        # HOTFIX: Setting data creates bugs out transforms currently so reset transform applied
        _transforms = self.grid._transforms
        self.grid.transform([])  # Set to no transforms
        self.grid.transform(_transforms)  # Set to previous transforms

    def __init__(
        self,
        schema: ty.Union[dict, ty.Type[BaseModel]],
        value: ty.Optional[list[dict[str, ty.Any]]] = None,
        by_alias: bool = False,
        by_title: bool = True,
        datahandler: ty.Optional[DataHandler] = None,
        ui_add: ty.Optional[ty.Callable] = None,
        ui_edit: ty.Optional[ty.Callable] = None,
        ui_delete: ty.Optional[ty.Callable] = None,
        ui_copy: ty.Optional[ty.Callable] = None,
        warn_on_delete: bool = False,
        show_copy_dialogue: bool = False,
        close_crud_dialogue_on_action: bool = False,
        description: str = "",
        **kwargs,
    ):
        self.description = w.HTML(description)
        self.by_title = by_title
        self.by_alias = by_alias
        self.datahandler = datahandler
        self.grid = AutoGrid(schema, data=pd.DataFrame(value), by_alias=self.by_alias, **kwargs)

        self._init_form()
        if ui_add is None:
            self.ui_add = AutoObjectFiltered(self.row_schema, app=self)
        else:
            self.ui_add = ui_add(self.row_schema, app=self)
        if ui_edit is None:
            self.ui_edit = AutoObjectFiltered(self.row_schema, app=self)
        else:
            self.ui_edit = ui_edit(self.row_schema, app=self)
        if ui_delete is None:
            self.ui_delete = UiDelete()
        else:
            self.ui_delete = ui_delete()
        self.ui_delete.layout.display = "None"
        if ui_copy is None:
            self.ui_copy = UiCopy()
        else:
            self.ui_copy = ui_copy()
        self.ui_copy.layout.display = "None"
        self.warn_on_delete = warn_on_delete
        # self.show_copy_dialogue = show_copy_dialogue
        self.show_copy_dialogue = False
        # ^ TODO: delete this when that functionality is added
        self.close_crud_dialogue_on_action = close_crud_dialogue_on_action
        self.ui_delete.fn_delete = self._delete_selected
        self._update_value_from_grid()
        self._init_row_controls()
        self.stk_crud = w.Stack(
            children=[self.ui_add, self.ui_edit, self.ui_copy, self.ui_delete]
        )
        self.children = [
            self.description,
            self.buttonbar_grid,
            self.stk_crud,
            self.grid,
        ]
        self._init_controls()

    def _init_row_controls(self):
        self.ui_edit.show_savebuttonbar = True
        self.ui_edit.savebuttonbar.fns_onsave = [self._patch, self._save_edit_to_grid]
        self.ui_edit.savebuttonbar.fns_onrevert = [self._set_ui_edit_to_selected_row]
        self.ui_add.show_savebuttonbar = True
        self.ui_add.savebuttonbar.fns_onsave = [self._post, self._save_add_to_grid]
        self.ui_add.savebuttonbar.fns_onrevert = [self._set_ui_add_to_default_row]

    @property
    def schema(self):
        return self.grid.schema

    @property
    def row_schema(self):
        return self.grid.schema["items"]

    @property
    def model(self):
        return self.grid.model

    def _init_form(self):
        super().__init__()
        self.buttonbar_grid = CrudButtonBar(
            add=self._add,
            edit=self._edit,
            copy=self._copy,
            delete=self._delete,
            # backward=self.setview_default,
            show_message=False,
        )
        self.addrow = w.VBox()
        self.editrow = w.VBox()

    def _init_controls(self):
        self.grid.observe(self._observe_selections, "selections")
        self.grid.observe(self._grid_changed, "count_changes")
        self.buttonbar_grid.observe(self._setview, "active")

    def _observe_selections(self, onchange):
        if self.buttonbar_grid.edit.value:
            self._set_ui_edit_to_selected_row()
        if self.buttonbar_grid.delete.value:
            self._set_ui_delete_to_selected_row()

    # @debounce(0.1)  # TODO: make debounce work if too slow...
    def _grid_changed(self, onchange):
        # debouncer used to allow editing whole rows in 1 go
        # without updating the `value` on every cell edit.
        self._update_value_from_grid()

    def _setview(self, onchange):
        if self.buttonbar_grid.active is None:
            self.stk_crud.selected_index = None
        else:
            self.stk_crud.selected_index = int(self.buttonbar_grid.active.value)

    def _check_one_row_selected(self):
        if len(self.grid.selected_indexes) > 1:
            raise Exception(
                markdown("  👇 _Please only select ONLY one row from the table!_")
            )

    # edit row
    # --------------------------------------------------------------------------
    def _validate_edit_click(self):
        if len(self.grid.selected_indexes) == 0:
            raise ValueError(
                "you must select an index (row if transposed==True, col if"
                " transposed==True)"
            )
        self._check_one_row_selected()

    def _save_edit_to_grid(self):
        if self.datahandler is not None:
            self._reload_all_data()
        else:
            changes = self.grid.set_item_value(
                self.grid.selected_index, self.ui_edit.value
            )

        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.edit.value = False

    def _set_ui_edit_to_selected_row(self):
        self.ui_edit.value = self.grid.selected
        self.ui_edit.savebuttonbar.unsaved_changes = False

    def _patch(self):
        if self.datahandler is not None:
            self.datahandler.fn_patch(self.ui_edit.value)

    def _edit(self):
        try:
            self._validate_edit_click()
            self._set_ui_edit_to_selected_row()

        except Exception as e:
            self.buttonbar_grid.edit.value = False
            self.buttonbar_grid.message.value = markdown(
                "  👇 _Please select one row from the table!_ "
            )
            traceback.print_exc()

    # --------------------------------------------------------------------------

    # add row
    # --------------------------------------------------------------------------
    def _save_add_to_grid(self):
        if self.datahandler is None:
            if not self.grid._data["data"]:  # If no data in grid
                self.value = tuple([self.ui_add.value])
            else:
                # Append new row onto data frame and set to grid's data.
                # Call setter. syntax below required to avoid editing in place.
                self.value = tuple(list(self.value) + [self.ui_add.value])
        else:
            self._reload_all_data()
        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.add.value = False

    def _set_ui_add_to_default_row(self):
        if self.ui_add.value == self.grid.default_row:
            self.ui_add.savebuttonbar.unsaved_changes = False
        else:
            self.ui_add.savebuttonbar.unsaved_changes = True

    def _post(self):
        if self.datahandler is not None:
            self.datahandler.fn_post(self.ui_add.value)

    def _add(self):
        self._set_ui_add_to_default_row()

    # --------------------------------------------------------------------------

    # copy
    # --------------------------------------------------------------------------

    def _get_selected_data(self):  # TODO: is this required? is it dupe from DataGrid?
        if self.grid.selected_index is not None:
            li_values_selected = [
                self.value[i] for i in sorted([i for i in self.grid.selected_indexes])
            ]
        else:
            li_values_selected = []
        return li_values_selected

    def _copy_selected_inplace(self):
        pass

    def _copy_selected_to_beginning(self):
        pass

    def _copy_selected_to_end(self):
        self.value = tuple(list(self.value) + self._get_selected_data())
        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.copy.value = False

    def _copy(self):
        try:
            if self.grid.selected_indexes == []:
                self.buttonbar_grid.message.value = markdown(
                    "  👇 _Please select a row from the table!_ "
                )
            else:
                if not self.show_copy_dialogue:
                    if self.datahandler is not None:
                        for value in self._get_selected_data():
                            self.datahandler.fn_copy(value)
                        self._reload_all_data()
                    else:
                        self._copy_selected_to_end()
                        # ^ add copied values. note. above syntax required to avoid editing in place.

                    self.buttonbar_grid.message.value = markdown("  📝 _Copied Data_ ")
                    self.buttonbar_grid.copy.value = False

                else:
                    print("need to implement show copy dialogue")
        except Exception as e:
            self.buttonbar_grid.message.value = markdown(
                "  👇 _Please select a row from the table!_ "
            )
            traceback.print_exc()

    # --------------------------------------------------------------------------

    # delete
    # --------------------------------------------------------------------------
    def _reload_all_data(self):
        if self.datahandler is not None:
            self.value = self.datahandler.fn_get_all_data()

    def _delete_selected(self):
        if self.datahandler is not None:
            value = [self.value[i] for i in self.grid.selected_indexes]
            for v in value:
                self.datahandler.fn_delete(v)
            self._reload_all_data()
        else:
            self.value = [
                value
                for i, value in enumerate(self.value)
                if i not in self.grid.selected_indexes
            ]
            # ^ Only set for values NOT in self.grid.selected_indexes
        self.buttonbar_grid.message.value = markdown("  🗑️ _Deleted Row_ ")
        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.delete.value = False

    def _set_ui_delete_to_selected_row(self):
        logging.info(f"delete: {self.grid.selected_dict}")
        self.ui_delete.value = self.grid.selected_dict

    def _delete(self):
        try:
            if len(self.grid.selected_indexes) > 0:
                if not self.warn_on_delete:
                    self.buttonbar_grid.delete.value = False
                    self._delete_selected()
                else:
                    self.ui_delete.value = self.grid.selected_dict
            else:
                self.buttonbar_grid.delete.value = False
                self.buttonbar_grid.message.value = markdown(
                    "  👇 _Please select at least one row from the table!_"
                )

        except Exception as e:
            print("delete error")
            traceback.print_exc()


class AutoObjectFiltered(aui.AutoObject):
    """This extended AutoObject class relies on EditGrid and a row_schema dictionary.

    The AutoObject will update its rows based on the visible rows of the grid.
    """

    def __init__(self, row_schema: dict, app: EditGrid, *args, **kwargs):
        self.app = app
        self._selections = []
        super().__init__(row_schema, *args, **kwargs)
        if self.app is not None:
            self.app.grid.observe(self._update_order, "_visible_rows")
            self.app.grid.observe(
                self._save_previous_selections, "selections"
            )  # Re-apply selection after updating transforms

    def _get_visible_fields(self):
        """Get the list of fields that are visible in the DataGrid."""
        if isinstance(self.app.grid.get_visible_data().index, pd.MultiIndex) is True:
            title_idx = self.app.grid.get_visible_data().index.names.index("title")
            visible_titles = [
                v[title_idx] for v in self.app.grid.get_visible_data().index
            ]
            return [
                k
                for k, v in self.app.row_schema["properties"].items()
                if v["title"] in visible_titles
            ]
        elif isinstance(self.app.grid.get_visible_data().index, pd.Index) is True:
            return [
                k
                for k, v in self.app.row_schema["properties"].items()
                if v["title"] in self.app.grid.get_visible_data().index
            ]

        else:
            raise Exception("Index obtained not of correct type.")

    def _update_order(self, onchange):
        """Update order instance of AutoObject based on visible fields in the DataGrid."""
        if self.app.transposed is True:
            self.order = self._get_visible_fields()
            self.app.grid.selections = self._selections

    def _save_previous_selections(self, onchange):
        if self.app.grid.selections:
            self._selections = self.app.grid.selections


if __name__ == "__main__":
    # Test: EditGrid instance with multi-indexing.
    AUTO_GRID_DEFAULT_VALUE = [
        {
            "string": "important string",
            "integer": 1,
            "floater": 3.14,
        },
    ]
    AUTO_GRID_DEFAULT_VALUE = AUTO_GRID_DEFAULT_VALUE * 4

    class DataFrameCols(BaseModel):
        string: str = Field("string", column_width=100, section="a")
        integer: int = Field(1, column_width=80, section="a")
        floater: float = Field(None, column_width=70, aui_sig_fig=3, section="b")

    class TestDataFrame(BaseModel):
        """a description of TestDataFrame"""

        __root__: ty.List[DataFrameCols] = Field(
            default=AUTO_GRID_DEFAULT_VALUE,
            format="dataframe",
            datagrid_index_name=("section", "title"),
        )

    description = markdown(
        "<b>The Wonderful Edit Grid Application</b><br>Useful for all editing purposes"
        " whatever they may be 👍"
    )
    editgrid = EditGrid(
        schema=TestDataFrame,
        description=description,
        ui_add=None,
        ui_edit=None,
        warn_on_delete=True,
        show_copy_dialogue=False,
        close_crud_dialogue_on_action=False,
    )
    editgrid.observe(lambda c: print("_value changed"), "_value")
    display(editgrid)


if __name__ == "__main__":
    # Test: Using AutoObjectFiltered
    editgrid = EditGrid(
        schema=TestDataFrame,
        description=description,
        ui_add=AutoObjectFiltered,
        ui_edit=AutoObjectFiltered,
        warn_on_delete=True,
    )
    editgrid.observe(lambda c: print("_value changed"), "_value")
    editgrid.transposed = True
    display(editgrid)

if __name__ == "__main__":
    from ipyautoui.demo_schemas import CoreIpywidgets
    from ipyautoui.autoipywidget import AutoObject

    #     class TestDataFrame(BaseModel):
    #         """a description of TestDataFrame"""

    #         __root__: ty.List[CoreIpywidgets] = Field(
    #             [CoreIpywidgets().dict()], format="dataframe"
    #         )
    # TODO: ^ fix this

    class TestDataFrame(BaseModel):
        """a description of TestDataFrame"""

        __root__: ty.List[DataFrameCols] = Field(
            [
                DataFrameCols(
                    string="String",
                    integer=1,
                    floater=2.5,
                ).dict()
            ],
            format="dataframe",
        )

    description = markdown(
        "<b>The Wonderful Edit Grid Application</b><br>Useful for all editing purposes"
        " whatever they may be 👍"
    )
    editgrid = EditGrid(
        schema=TestDataFrame,
        description=description,
        ui_add=None,
        ui_edit=None,
        warn_on_delete=True,
    )
    editgrid.observe(lambda c: print("_value changed"), "_value")
    display(editgrid)

if __name__ == "__main__":
    editgrid.transposed = True

if __name__ == "__main__":

    class TestDataFrame(BaseModel):
        __root__: ty.List[DataFrameCols] = Field(
            default=AUTO_GRID_DEFAULT_VALUE, format="dataframe"
        )


if __name__ == "__main__":
    from ipyautoui import AutoUi
    from ipyautoui.autoipywidget import AutoObject

    ui = AutoObject(schema=TestDataFrame)
    ui.align_horizontal = True
    ui.auto_open = True
    ui.observe(lambda c: print("_value change"), "_value")
    ui.di_widgets["__root__"].observe(lambda c: print("grid _value change"), "_value")
    display(ui)
