import os

ASSETS_FILENAME_PREFIX = 'deathmsg_'
class DeathMsgInfo:
    death_patterns = []
    death_msg_formats = {}

    @classmethod
    def init(cls, plugin_dir):
        assets_dir = os.path.join(plugin_dir, 'assets')
        for asset_file in os.listdir(assets_dir):
            if os.path.isfile(os.path.join(assets_dir, asset_file)):
                if asset_file.startswith(ASSETS_FILENAME_PREFIX):
                    lang = os.path.splitext(asset_file)[0][len(ASSETS_FILENAME_PREFIX):]
                    with open(os.path.join(assets_dir, asset_file), 'r', encoding='utf-8') as cur_lang_file:
                        lines = list(cur_lang_file)
                        lines = [line.strip() for line in lines]
                        cls.death_msg_formats[lang] = lines
        with open(os.path.join(assets_dir, 'pattern_deathmsg.txt'), 'r', encoding='utf-8') as patterns_f:
            lines = list(patterns_f)
            lines = [line.strip() for line in lines]
            cls.death_patterns = lines


class DeathMsg:
    def __init__(self, death_msg_id, death_info):
        self.death_msg_id = death_msg_id
        self.death_info = death_info

    def format(self,lang='en'):
        if lang not in DeathMsgInfo.death_msg_formats:
            lang = 'en'
        return DeathMsgInfo.death_msg_formats[lang][self.death_msg_id].format(**self.death_info)

    def get_victim(self):
        return self.death_info['victim']

    def get_murderer(self):
        return self.death_info.get('murderer', None)

    def get_item(self):
        return self.death_info.get('item', None)
