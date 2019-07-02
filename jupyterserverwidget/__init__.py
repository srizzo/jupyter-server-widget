from .serverwidgetmagics import ServerWidgetMagics

def load_ipython_extension(ipython):
    ipython.register_magics(ServerWidgetMagics)
