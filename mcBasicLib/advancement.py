import os

ASSETS_FILENAME_PREFIX = 'advancement_'
ADVANCEMENT_TYPE_N = 3
class AdvancementInfo:
    advancement_names = {}
    advancement_formats = {}
    
    @classmethod
    def init(cls, plugin_dir):
        assets_dir = os.path.join(plugin_dir, 'assets')
        for asset_file in os.listdir(assets_dir):
            if os.path.isfile(os.path.join(assets_dir, asset_file)):
                if asset_file.startswith(ASSETS_FILENAME_PREFIX):
                    lang = os.path.splitext(asset_file)[0][len(ASSETS_FILENAME_PREFIX):]
                    with open(os.path.join(assets_dir, asset_file), 'r', encoding='utf-8') as cur_lang_file:
                        lines = list(cur_lang_file)
                        names = [line.strip() for line in lines[ADVANCEMENT_TYPE_N:]]
                        formats = [line.strip() for line in lines[:ADVANCEMENT_TYPE_N]]
                        cls.advancement_names[lang] = names
                        cls.advancement_formats[lang] = formats
    
    @classmethod
    def get_id_by_name(cls, name):
        for i, v in enumerate(cls.advancement_names['en']):
            if v == name:
                return i
        return None

class Advancement:
    def __init__(self, player, advancement_id, advancement_type):
        self.player = player
        self.advancement_id = advancement_id
        self.advancement_type = advancement_type
    
    def format(self, lang='en'):
        if not (lang in AdvancementInfo.advancement_names):
            lang = 'en'
        name = AdvancementInfo.advancement_names[lang][self.advancement_id]
        return AdvancementInfo.advancement_formats[lang][self.advancement_type].format(player=str(self.player), name=name)
    
    def get_player(self):
        return self.player
    
    def get_name(self, lang='en'):
        if not (lang in AdvancementInfo.advancement_names):
            lang = 'en'
        return AdvancementInfo.advancement_names[lang][self.advancement_id]
    
    def get_type(self):
        return self.advancement_type