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

"""simple markdown widget"""
# %run __init__.py
# %load_ext lab_black

# +
import ipywidgets as widgets
import functools
import traitlets
from IPython.display import Markdown, clear_output, display
import immutables

frozenmap = immutables.Map

# +
BUTTON_MIN_SIZE = frozenmap(**{"width": "41px", "height": "25px"})
EXAMPLE_MARKDOWN = """
# Markdown Example

**Markdown** is a plain text format for writing _structured documents_, based on formatting conventions from email and usenet.

See details here: [__commonmark__](https://commonmark.org/help/)

## lists

- **bold**
- *italic*
- `inline code`
- [links](https://www.markdownguide.org/basic-syntax/)

## numbers

1. item 1
1. item 1
1. item 1

"""

HEADER = """
# H1

## H2

### H3

...
"""

BOLD = """
**bold text**
"""

ITALIC = """
*italic text*
"""

LIST = """
- list item 1
- list item 2
- list item 3
"""

NUMBERED = """
1. item 1
1. item 2
1. item 3
"""

IMAGE = """
![relative path to image from the markdown file](rel/path/to/image.png)
"""

LINK = """
[commonmark-help](https://commonmark.org/help/)
"""

MAP_MARKDOWN = frozenmap(
    **{
        "bn_header": HEADER,
        "bn_bold": BOLD,
        "bn_italic": ITALIC,
        "bn_list": LIST,
        "bn_numbered": NUMBERED,
        "bn_image": IMAGE,
        "bn_link": LINK,
    }
)


# -


def markdown_buttons():
    """generate markdown widget button bar"""
    bn_header = widgets.Button(icon="fa-heading", layout=dict(BUTTON_MIN_SIZE))
    bn_bold = widgets.Button(icon="fa-bold", layout=dict(BUTTON_MIN_SIZE))
    bn_italic = widgets.Button(icon="fa-italic", layout=dict(BUTTON_MIN_SIZE))
    bn_list = widgets.Button(icon="fa-list", layout=dict(BUTTON_MIN_SIZE))
    bn_numbered = widgets.Button(icon="fa-list-ol", layout=dict(BUTTON_MIN_SIZE))
    bn_image = widgets.Button(icon="fa-image", layout=dict(BUTTON_MIN_SIZE))
    bn_link = widgets.Button(icon="fa-link", layout=dict(BUTTON_MIN_SIZE))
    bn_blank = widgets.Button(
        display=True, style={"button_color": "white"}, layout=dict(BUTTON_MIN_SIZE)
    )
    bn_help = widgets.ToggleButton(icon="question", layout=dict(BUTTON_MIN_SIZE))
    bx_buttons = widgets.HBox()
    bx_buttons.children = [
        bn_header,
        bn_bold,
        bn_italic,
        bn_list,
        bn_numbered,
        bn_image,
        bn_link,
        bn_blank,
        bn_help,
    ]
    return (
        bx_buttons,
        bn_header,
        bn_bold,
        bn_italic,
        bn_list,
        bn_numbered,
        bn_image,
        bn_link,
        bn_help,
    )


class MarkdownWidget(widgets.VBox):
    """a simple markdown widget for editing snippets of markdown text"""

    _value = traitlets.Unicode(allow_none=True)  # default=""

    def __init__(self, value=None):
        self._init_form()
        self._init_controls()
        if value is None:
            pass
        else:
            self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.text.value = value

    def _init_form(self):
        super().__init__()
        self.text = widgets.Textarea(layout={"width": "400px", "height": "300px"})
        self.rendered = widgets.Output()
        self.example_text = widgets.Textarea(
            value=EXAMPLE_MARKDOWN,
            disabled=True,
            layout={"width": "400px", "height": "300px"},
        )
        self.example_rendered = widgets.Output()
        self.bx_markdown = widgets.HBox()
        self.bx_markdown.children = [self.text, self.rendered]
        (
            self.bx_buttons,
            self.bn_header,
            self.bn_bold,
            self.bn_italic,
            self.bn_list,
            self.bn_numbered,
            self.bn_image,
            self.bn_link,
            self.bn_help,
        ) = markdown_buttons()
        self.children = [self.bx_buttons, self.bx_markdown]

    def _init_controls(self):
        self.text.observe(self._text, names="value")
        self.bn_help.observe(self._bn_help, names="value")
        for k, v in MAP_MARKDOWN.items():
            getattr(self, k).on_click(
                functools.partial(self._add_markdown_text, text=v)
            )

    def _add_markdown_text(self, on_click, text="text"):
        self.value = self.value + text

    def _bn_help(self, onchange):
        if self.bn_help.value:
            self.bx_markdown.children = [self.example_text, self.example_rendered]
            with self.example_rendered:
                clear_output()
                display(Markdown(self.example_text.value))
        else:
            self.bx_markdown.children = [self.text, self.rendered]

    def _text(self, onchange):
        self._value = self.text.value
        with self.rendered:
            clear_output()
            display(Markdown(self.text.value))


if __name__ == "__main__":
    ui = MarkdownWidget()
    display(ui)

