from PyQt5 import QtCore
from .player import Player, GhostingPlayer
import re
import json

__all__ = ['McBasicLib']


class McBasicLib(QtCore.QObject):
    """
    Provide basic functions and parsers for Minecraft Java Edition Server.
    """

    # Signals
    sig_input = QtCore.pyqtSignal(tuple)  # (Player, str) tuple, the player object and what he said.
    
    def __init__(self, logger, core):
        super().__init__(core)
        self.core = core
        self.logger = logger
        Player.logger = logger
        core.sig_command.connect(self.on_command)
        core.sig_server_output.connect(self.on_server_output)

    @QtCore.pyqtSlot(str)
    def on_command(self, cmd):
        self.sig_input.emit((GhostingPlayer(), cmd))

    @QtCore.pyqtSlot(list)
    def on_server_output(self, lines):
        for line in lines:
            match_obj = re.match(r'.*?<(\w+?)> (.*)', line)
            if match_obj:  # some players said something
                player = match_obj.group(1)
                text = match_obj.group(2)
                self.logger.debug('Player {} said: {}'.format(player, text))
                self.sig_input.emit((Player(player), text))

    def say(self, text):
        self.core.write_server('/say {}'.format(text))

    def tellraw(self, player, json_str):
        if player.is_console():
            self.logger.direct_output(json_str)
        else:
            self.core.write_server('/tellraw {} {}'.format(player.name, json_str))

    def tell(self, player, text, color='yellow', bold=False):
        if player.is_console():
            self.logger.direct_output(text)
        else:
            tell_obj = {
                'text': text,
                'color': color,
                'bold': bold
            }
            self.core.write_server('/tellraw {} {}'.format(player.name, json.dumps(tell_obj)))
