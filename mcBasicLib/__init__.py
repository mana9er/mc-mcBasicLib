from PyQt5 import QtCore
from .basic import McBasicLib
from .player import Player, GhostingPlayer

dependencies = []


class Export(QtCore.QObject):
    sig_input = QtCore.pyqtSignal(tuple)
    def __init__(self):
        super().__init__()


def load(logger, core):
    # Function "load" is required by mana9er-core.
    lib_inst = McBasicLib(logger, core)
    exports = Export()
    exports.Player = Player
    exports.GhostingPlayer = GhostingPlayer
    lib_inst.sig_input.connect(exports.sig_input)
    exports.say = lib_inst.say
    exports.tellraw = lib_inst.tellraw
    exports.tell = lib_inst.tell
    return exports