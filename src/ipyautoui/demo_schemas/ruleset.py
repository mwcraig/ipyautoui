# ---
# jupyter:
#   jupytext:
#     custom_cell_magics: kql
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# %run ../_dev_maplocal_params.py
# %load_ext lab_black

# %%
from enum import Enum
from pydantic import ConfigDict, BaseModel, Field, RootModel
from ipyautoui import AutoUi
from ipyautoui.autoobject import AutoObject
from ipyautoui._utils import html_link
import typing as ty
from enum import Enum


# %%
class StrEnum(str, Enum):
    pass


class RuleSetType(str, Enum):
    """how the rules logically multiply. Must be `AND` for schedules"""

    AND: str = "AND"
    OR: str = "OR"


RevitCategoriesEnum = StrEnum(
    "RevitCategoriesEnum",
    {
        "OST_AnalyticSpaces": "Analytical Spaces",
        "OST_DuctTerminal": "Air Terminals",
        "OST_ElectricalEquipment": "Electrical Equipment",
        "OST_ElectricalFixtures": "Electrical Fixtures",
        "OST_MEPAnalyticalAirLoop": "Air Systems",
        "OST_MEPAnalyticalWaterLoop": "Water Loops",
        "OST_MEPSpaces": "Spaces",
        "OST_PipeAccessory": "Pipe Accessories",
        "OST_PipeCurves": "Pipes",
        "OST_PipeFitting": "Pipe Fittings",
        "OST_PipeInsulations": "Pipe Insulations",
        "OST_PipingSystem": "Piping Systems",
        "OST_PlumbingFixtures": "Plumbing Fixtures",
        "OST_Sprinklers": "Sprinklers",
    },
)

RevitOperatorsEnum = StrEnum(
    "RevitOperatorsEnum",
    {
        "BeginsWith": "begins with",
        "Contains": "contains",
        # "EndsWith": "ends with",
        # "Equals": "equals",
        # "GreaterOrEqual": "is greater than or equal to",
        # "Greater": "is greater than",
        # "HasNoValueParameter": "has no value",
        # "HasValueParameter": "has value",
        # "IsAssociatedWithGlobalParameter": "?",
        # "IsNotAssociatedWithGlobalParameter": "?",
        # "LessOrEqual": "is less than or equal to",
        # "Less": "is less than",
        # "NotBeginsWith": "does not begin with",
        # "NotContains": "does not contain",
        # "NotEndsWith": "does not end with",
        # "NotEquals": "dont not equal",
        # "SharedParameterApplicable": "?",
    },
)


class CategoriesEnum(RootModel):
    root: RevitCategoriesEnum


class Rule(BaseModel):
    categories: list[CategoriesEnum] = Field(  # RevitCategoriesEnum
        title="Categories",  # TODO: this is pydantic bug (should generate title from field name)
        description="Revit MEP categories to filter by (i.e. revit object must belong to categories defined here). If empty, all categories are included.",
    )
    parameter: str = Field(
        description="name of schedule parameter against which to apply filter rule",
        examples=["a", "ab"],  # get_property_names(),
    )
    operator: RevitOperatorsEnum = Field(
        title="Logical Operator",
        description="logical operator used to evaluate parameter value against value below",
    )
    value: str = Field(
        "",
        description="Value to filter by. Evaluates to the appropriate type. Leave empty if none required (e.g. has value operator)",
        examples=[
            "a",
            "ab",
        ],  # get_uniclass_product_codes() + get_uniclass_system_codes(),
    )
    model_config = ConfigDict(json_schema_extra=dict(autoui="ipyautoui.demo_schemas.ruleset.rule_ui"))
    # NOTE: can use "__main__.rule_ui" if you import it into the location you want to use it


URL_REVIT_FILTERS = "https://help.autodesk.com/view/RVT/2023/ENU/?guid=GUID-400FD74B-00E0-4573-B3AC-3965E65CBBDB"
DI_UNICLASS_PR = {
    "Pr_15": "Pr_15 - Preparatory products",
    "Pr_15_31": "Pr_15_31 - Formless preparatory products",
    "Pr_15_31_04": "Pr_15_31_04 - Applied cleaning and treatment products",
}
DI_UNICLASS_SS = {
    "Ss_55": "Ss_55 - Piped supply systems",
    "Ss_55_70_38": "Ss_55_70_38 - Hot and cold water supply systems",
    "Ss_55_70_95": "Ss_55_70_95 - Water distribution network systems",
}

UniclassProducts = StrEnum("Uniclass Product Codes", DI_UNICLASS_PR)
UniclassProducts.__doc__ = "A list of valid Uniclass Product codes"
UniclassSystems = StrEnum("Uniclass Product Codes", DI_UNICLASS_SS)
UniclassSystems.__doc__ = "A list of valid Uniclass System codes"


def get_property_names():  # TODO: overwrite this
    return ["Product Classification", "System Classification"]


def get_uniclass_product_codes():
    return UniclassProducts._member_names_


def get_uniclass_system_codes():
    return UniclassSystems._member_names_


def get_value_kwargs(property_name):
    if property_name == "Product Classification":
        return {"ensure_option": True, "options": get_uniclass_product_codes()}
    elif property_name == "System Classification":
        return {"ensure_option": True, "options": get_uniclass_system_codes()}
    else:
        return {"ensure_option": False, "options": []}


class RuleUi(AutoObject):  # RuleUi extends AutoObject allowing customisation
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.di_widgets["parameter"].options = get_property_names()
        self._init_RuleUi_controls()

    def _init_RuleUi_controls(self):
        self.di_widgets["parameter"].observe(self._update_rule_value, "value")

    def _update_rule_value(self, on_change):
        if self.di_widgets["parameter"].value != "":
            wi = self.di_widgets["value"]
            di = get_value_kwargs(on_change["new"])
            for k, v in di.items():
                setattr(wi, k, v)
            if wi.value not in di["options"]:
                wi.value = ""
        else:
            pass


def rule_ui(value=None, **kwargs):
    ui = RuleUi.from_schema(Rule)
    ui.open_nested = True
    if value is not None:
        ui.value = value
    return ui


ScheduleRuleSet = ty.ForwardRef("ScheduleRuleSet")


class ScheduleRuleSet(BaseModel):
    set_type: RuleSetType = Field(default=RuleSetType.AND, disabled=True)
    rule_sets: ty.List[ty.Union[Rule, ScheduleRuleSet]] = Field(
        description="""
rules return a boolean for the logical evaluation defined below for every item within the categories defined
"""
    )

    model_config = ConfigDict(json_schema_extra=dict(open_nested=True))


ScheduleRuleSet.__doc__ = (
    """REAL-WORLD CUSTOM EXAMPLE! A set of rules that defines what equipment specifications will appear in a given schedule.<br>
Rules must evaluate to True for the item to be included in a schedule
Analogous to filter rules in
"""
    + html_link(URL_REVIT_FILTERS, "Revit.")
    + "<br><b>This is the basis of a customised example from the wild!</b>"
    + "<br>---"
)

# %%
if __name__ == "__main__":
    from IPython.display import display

    # m, s = _init_model_schema(ObjSet)
    ui = AutoObject.from_schema(ScheduleRuleSet)
    display(ui)

# %%
