from PyQt5 import QtCore
from .player import Player, GhostingPlayer
from .advancement import Advancement, AdvancementInfo
from .death import DeathMsg, DeathMsgInfo
import re
import json

__all__ = ['McBasicLib']


class McBasicLib(QtCore.QObject):
    """
    Provide basic functions and parsers for Minecraft Java Edition Server.
    """

    # Signals
    sig_input = QtCore.pyqtSignal(tuple)            # (Player, str) tuple, the player object and what he said.
    sig_login = QtCore.pyqtSignal(object)           # the player who just logged-in.
    sig_logout = QtCore.pyqtSignal(object)          # the player who just logged-out.
    sig_death = QtCore.pyqtSignal(object)           # a DeathMsg object.
    sig_advancement = QtCore.pyqtSignal(object)     # an Advancement object.
    
    def __init__(self, logger, core):
        super().__init__(core)
        self.core = core
        self.logger = logger
        Player.logger = logger
        self.online_player_list = set()
        self.deathmsg_re_patterns = self._gen_re_patterns_for_death_msg()
        core.sig_command.connect(self.on_command)
        core.sig_server_output.connect(self.on_server_output)
        core.sig_server_start.connect(self.on_server_start)
        core.sig_server_stop.connect(self.on_server_stop)
        self.sig_login.connect(self.on_player_login)
        self.sig_logout.connect(self.on_player_logout)

    @QtCore.pyqtSlot(str)
    def on_command(self, cmd):
        self.sig_input.emit((GhostingPlayer(), cmd))

    @QtCore.pyqtSlot(list)
    def on_server_output(self, lines):
        for line in lines:
            self._parse_output(line)

    def _parse_output(self, line):
        # detect player input
        match_obj = re.match(r'[^<>]*?\[Server thread/INFO\].*?:\s*<(\w+?)> (.*)', line)
        if match_obj:  # some players said something
            player = match_obj.group(1)
            text = match_obj.group(2)
            self.logger.debug('Player {} said: {}'.format(player, text))
            self.sig_input.emit((Player(player), text))
            return
        # detect login / logout
        # don't need to exclude player input (already handled)
        match_obj = re.match(r'[^<>]*?\[Server thread/INFO\].*?:\s*(\w+) (joined|left) the game$', line)
        if match_obj:  # some player joined the game
            player = match_obj.group(1)
            if match_obj.group(2) == 'joined':
                self.logger.debug('Player {} joined the game'.format(player))
                self.sig_login.emit(Player(player))
            elif match_obj.group(2) == 'left':
                self.logger.debug('Player {} left the game'.format(player))
                self.sig_logout.emit(Player(player))
            return
        # detect advancement
        # actually we have 3 different types: advancement, challenge, and goal.
        advc_patterns = [
            r'[^<>]*?\[Server thread/INFO\].*?:\s*(\w+) has made the advancement \[(.+)\]$',
            r'[^<>]*?\[Server thread/INFO\].*?:\s*(\w+) has completed the challenge \[(.+)\]$',
            r'[^<>]*?\[Server thread/INFO\].*?:\s*(\w+) has reached the goal \[(.+)\]$',
        ]
        for i, pattern in enumerate(advc_patterns):
            match_obj = re.match(pattern, line)
            if match_obj:
                player = match_obj.group(1)
                advc_name = match_obj.group(2)
                advc_id = AdvancementInfo.get_id_by_name(advc_name)
                if advc_id is None:
                    self.logger.error('unrecognized advancement name: ' + advc_name)
                    return
                advc_obj = Advancement(player, advc_id, i)
                self.sig_advancement.emit(advc_obj)
                return
        # detect death info
        death_patterns = DeathMsgInfo.death_patterns
        for pattern in death_patterns:
            # use substring match for better performance
            if pattern in line:
                self._parse_death_msg(line)  # do further parse in this function
                return

    def _parse_death_msg(self, line):
        for re_pattern in self.deathmsg_re_patterns:
            match_obj = re.match(re_pattern['pattern'], line)
            if match_obj:
                death_info = {}
                for i, param in enumerate(re_pattern['params']):
                    extracted = match_obj.group(i + 1)
                    death_info[param] = extracted
                death_obj = DeathMsg(re_pattern['id'], death_info)
                self.sig_death.emit(death_obj)
                return

    def _gen_re_patterns_for_death_msg(self):
        en_formats = DeathMsgInfo.death_msg_formats['en']
        re_patterns = []
        for i, text in enumerate(en_formats):
            pattern = [r'[^<>]*?\[Server thread/INFO\].*?:\s*']
            params = []
            parts = text.split('{')
            pattern.append(re.escape(parts[0]))
            for part in parts[1:]:
                param = part.split('}')[0]
                params.append(param)
                pattern.append('(.+?)')
                pattern.append(re.escape(part.split('}')[1]))
            pattern.append('$')
            pattern = ''.join(pattern)
            re_patterns.append({
                'id': i,
                'pattern': pattern,
                'params': params,
            })
        return re_patterns

    def say(self, text):
        self.core.write_server('/say {}'.format(text))

    def tellraw(self, player, json_str):
        if isinstance(player, Player) and player.is_console():
            self.logger.direct_output(json_str)
        else:
            if len(self.online_player_list) == 0:
                return  # do not execute when there's nobody online
            player = str(player)
            self.core.write_server('/tellraw {} {}'.format(player, json_str))

    def tell(self, player, text, color='yellow', bold=False):
        if isinstance(player, Player) and player.is_console():
            self.logger.direct_output(text)
        else:
            if len(self.online_player_list) == 0:
                return  # do not execute when there's nobody online
            tell_obj = {
                'text': text,
                'color': color,
                'bold': bold
            }
            player = str(player)
            self.core.write_server('/tellraw {} {}'.format(player, json.dumps(tell_obj)))

    def get_online_player_list(self):
        return list(self.online_player_list)

    @QtCore.pyqtSlot(object)
    def on_player_login(self, player):
        # `player` here is an object
        player = player.name
        self.online_player_list.add(player)
        self.logger.debug('Online player list changed to: {}'.format(self.online_player_list))
    
    @QtCore.pyqtSlot(object)
    def on_player_logout(self, player):
        # `player` here is an object
        player = player.name
        self.online_player_list.remove(player)
        self.logger.debug('Online player list changed to: {}'.format(self.online_player_list))

    @QtCore.pyqtSlot()
    def on_server_start(self):
        self.online_player_list.clear()
    
    @QtCore.pyqtSlot()
    def on_server_stop(self):
        self.online_player_list.clear()
