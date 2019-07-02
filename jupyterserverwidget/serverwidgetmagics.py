from .serverwidget import ServerWidget

from ipywidgets.widgets import HBox
from IPython.core.magic import line_magic, cell_magic, Magics, magics_class
from IPython.display import display

@magics_class
class ServerWidgetMagics(Magics):
    @line_magic
    def server(self, line=''):
        display(ServerWidget(line))

    @cell_magic
    def servers(self, line='', cell=None):
        display(HBox([ServerWidget(l) for l in cell.splitlines()]))
