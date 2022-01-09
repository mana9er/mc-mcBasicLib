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
    sig_input = QtCore.pyqtSignal(tuple)    # (Player, str) tuple, the player object and what he said.
    sig_login = QtCore.pyqtSignal(object)   # the player who just logged-in.
    sig_logout = QtCore.pyqtSignal(object)  # the player who just logged-out.
    sig_death = QtCore.pyqtSignal(tuple)    # TODO: detect the death of player.
    
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
            # detect player input
            match_obj = re.match(r'.*?<(\w+?)> (.*)', line)
            if match_obj:  # some players said something
                player = match_obj.group(1)
                text = match_obj.group(2)
                self.logger.debug('Player {} said: {}'.format(player, text))
                self.sig_input.emit((Player(player), text))
                return
            # detect login / logout
            # don't need to exclude player input (already handled)
            match_obj = re.match(r'[^<>]*?\[Server thread/INFO\].*?:\s*(\w+)\s*(joined|left) the game$', line)
            if match_obj:  # some player joined the game
                player = match_obj.group(1)
                if match_obj.group(2) == 'joined':
                    self.logger.debug('Player {} joined the game'.format(player))
                    self.sig_login.emit(Player(player))
                elif match_obj.group(2) == 'left':
                    self.logger.debug('Player {} left the game'.format(player))
                    self.sig_logout.emit(Player(player))
                return
            

    def say(self, text):
        self.core.write_server('/say {}'.format(text))

    def tellraw(self, player, json_str):
        if isinstance(player, Player) and player.is_console():
            self.logger.direct_output(json_str)
        else:
            if isinstance(player, Player):
                player_name = player.name
            else:
                player_name = player
            self.core.write_server('/tellraw {} {}'.format(player_name, json_str))

    def tell(self, player, text, color='yellow', bold=False):
        if isinstance(player, Player) and player.is_console():
            self.logger.direct_output(text)
        else:
            tell_obj = {
                'text': text,
                'color': color,
                'bold': bold
            }
            if isinstance(player, Player):
                player_name = player.name
            else:
                player_name = player
            self.core.write_server('/tellraw {} {}'.format(player_name, json.dumps(tell_obj)))
