# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
# %run __init__.py
# %load_ext lab_black

# uncomment next lines to enable hot reloading of vue template(s). (needs the watchdog package)
import ipywidgets as widgets
import ipyvue
import ipyvuetify as v
import traitlets

ipyvue.watch(".")


class AutoVjsf(v.VuetifyTemplate):
    template_file = "vjsf.vue"
    vjsf_loaded = traitlets.Bool(False).tag(sync=True)
    value = traitlets.Dict(default_value={}).tag(sync=True)
    schema = traitlets.Dict().tag(sync=True)
    valid = traitlets.Bool(False).tag(sync=True)


# -

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic

    test = TestAutoLogic()
    sch = test.schema()
    ui = AutoVjsf(schema=sch)
    display(ui)
