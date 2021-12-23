# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.3
#   kernelspec:
#     display_name: Python [conda env:ipyautoui]
#     language: python
#     name: conda-env-ipyautoui-xpython
# ---

import ipywidgets as widgets
from traitlets import HasTraits, Unicode, default, validate, TraitError
import re
from dataclasses import dataclass, asdict
import typing


@dataclass
class RunNameInputs:
    index: int = 1
    disabled_index: bool = False
    zfill: int = 2
    enum: typing.List = None
    delimiter: str = '-'
    description_length: int = None
    allow_spaces: bool = False
    order: tuple = ('index', 'enum', 'description')
    pattern: str = None

    def __post_init__(self):
        li = list(self.order)
        if self.index is None:
            li = [l for l in li if l!='index'] 
        if self.enum is None:
            li = [l for l in li if l!='enum'] 
        if self.description_length is None:
            li = [l for l in li if l!='description'] 
        self.order = tuple(li)
        if len(self.order) < 1:
            raise ValueError('you must include 1 of index, enum or description')
        
        di={}
        di['index'] = "[0-9]" * self.zfill + f"[{self.delimiter}]"
        di['enum'] = f"[a-z,A-Z,0-9]*[{self.delimiter}]"
        di['description'] = f".+[{self.delimiter}]"
        p = ""
        for l in self.order:
            try:
                p += di[l]
            except:
                pass
        self.pattern = p[:-3]      


class RunName(widgets.HBox, HasTraits):
    """widget for creating an modelling iteration name to a defined format from component parts
    
    Example:
        value = '000-lean-short_description_of_model-run'
        enum = ['lean', 'clean', 'green']
        zfill = 2
    """
    value = Unicode()
    
    @validate('value')
    def _valid_value(self, proposal):
        val = proposal['value']
        matched = re.match(self.inputs.pattern, val) #
        if not bool(matched):
            print(self.inputs.pattern)
            print(val)
            raise TraitError(f'string musts have format: {self.inputs.pattern}')#
        return val
    
    def __init__(self, value = None,
                    index: int = 1,
                    disabled_index: bool = True,
                    zfill: int = 2,
                    enum: typing.List = ['lean','clean', 'green'],
                    delimiter: str = '-',
                    description_length: int = 30,
                    allow_spaces: bool = False,
                    order=('index', 'enum', 'description')
                ):
        di = {k:v for k, v in locals().items() if k != 'value' and k != 'self' and k!='__class__'}
        super().__init__()
        self.inputs = RunNameInputs(**di)
        if value is not None:
            self.value = value
        self._init_RunName()
        self._init_controls()
        self.update_name('change')
        
    @property
    def get_options(self):
        if self.inputs.enum is None:
            return []
        else:
            return self.inputs.enum 
        
    def _init_RunName(self):
        try:
            index, enum, description = self.value.split(self.inputs.delimiter, self.inputs.sections)
        except:
            index, enum, description = None, None, 'description'
        self.index = widgets.IntText(value=index,layout={'width':'50px'}, disabled=self.inputs.disabled_index)
        self.enum = widgets.Dropdown(value=enum, options=self.get_options, layout={'width':'100px'})
        self.description = widgets.Text(value=description)
        self.name = widgets.Text(disabled=True)
        di = {}   
        di['index'] = self.index
        di['enum'] = self.enum
        di['description'] = self.description
        children = []
        for l in self.inputs.order:
            try:
                children.append(di[l])
            except:
                pass
        self.children = children + [self.name]
        
    def _init_controls(self):
        self.index.observe(self.update_name, names='value')
        self.enum.observe(self.update_name, names='value')
        self.description.observe(self.update_name, names='value')
        
    def update_name(self, on_change):
        di = {}
        di['enum'] = str(self.enum.value) + self.inputs.delimiter
        di['index'] = str(self.index.value).zfill(self.inputs.zfill) + self.inputs.delimiter
        di['description'] = self.description.value.replace(self.inputs.delimiter,'_') + self.inputs.delimiter
        if not self.inputs.allow_spaces:
            di['description'] = di['description'].replace(' ','_')
        if self.inputs.description_length is not None:
            di['description'] = di['description'][0:self.inputs.description_length]
        v = ""
        for l in self.inputs.order:
            try: 
                v += di[l]
            except:
                pass
        self.name.value = v[:-1]   
        self.value = self.name.value


if __name__ == "__main__":
    run = RunName()
    display(run)
