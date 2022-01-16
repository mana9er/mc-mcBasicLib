import os
from PyQt5 import QtCore
from .basic import McBasicLib
from .player import Player, GhostingPlayer
from .advancement import AdvancementInfo
from .death import DeathMsgInfo

dependencies = []


class Export(QtCore.QObject):
    sig_input = QtCore.pyqtSignal(tuple)
    sig_login = QtCore.pyqtSignal(object)
    sig_logout = QtCore.pyqtSignal(object)
    sig_advancement = QtCore.pyqtSignal(object)
    def __init__(self):
        super().__init__()


def load(logger, core):
    # Function "load" is required by mana9er-core.
    lib_inst = McBasicLib(logger, core)
    exports = Export()
    exports.Player = Player
    exports.GhostingPlayer = GhostingPlayer
    lib_inst.sig_input.connect(exports.sig_input)
    lib_inst.sig_login.connect(exports.sig_login)
    lib_inst.sig_logout.connect(exports.sig_logout)
    lib_inst.sig_advancement.connect(exports.sig_advancement)
    exports.say = lib_inst.say
    exports.tellraw = lib_inst.tellraw
    exports.tell = lib_inst.tell
    exports.get_online_player_list = lib_inst.get_online_player_list
    plugin_dir = os.path.join(core.root_dir, 'mcBasicLib')
    AdvancementInfo.init(plugin_dir)
    DeathMsgInfo.init(plugin_dir)
    return exports