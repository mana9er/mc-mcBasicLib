import json


class Player:
    
    def __init__(self, name):
        self.name = name

    def is_console(self):
        return False

    def is_op(self):
        try:
            with open('ops.json', 'r', encoding='utf-8') as opf:
                ops = json.load(opf)
                for op in ops:
                    if op['name'] == self.name:
                        return True
                return False
        except (OSError, IOError):
            Player.logger.error('Fail to open ops.json when checking op permission. \
                This is probably caused by a wrong working directory or an old version of Minecraft server.')
            return False


class GhostingPlayer(Player):
    
    def __init__(self):
        super(GhostingPlayer, self).__init__('CONSOLE')

    def is_console(self):
        return True
    
    def is_op(self):
        return True