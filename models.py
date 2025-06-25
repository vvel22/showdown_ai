class Pokemon:
    def __init__(self, name, level=100, nature=None, item=None, ability=None, evs=None, moves=None, types=None, base_stats=None):
        self.name = name
        self.level = level
        self.nature = nature
        self.item = item
        self.ability = ability
        self.evs = self.parse_evs(evs)
        self.moves = moves or []
        self.types = types or []
        self.base_stats = base_stats or {}
        self.total_stats = self.calculate_total_stats()

    def parse_evs(self, ev_string):
        if not ev_string:
            return {}
        evs = {}
        for part in ev_string.split("/"):
            val, stat = part.strip().split(" ")
            evs[stat.lower()] = int(val)
        return evs

    def nature_modifiers(self):
        natures = {
            "adamant":     ("attack", "sp. atk"),
            "modest":      ("sp. atk", "attack"),
            "timid":       ("speed", "attack"),
            "jolly":       ("speed", "sp. atk"),
            "bold":        ("defense", "attack"),
            "calm":        ("sp. def", "attack"),
            "careful":     ("sp. def", "sp. atk"),
            "impish":      ("defense", "sp. atk"),
            # Add more as needed
        }
        return natures.get(self.nature.lower(), (None, None)) if self.nature else (None, None)

    def calculate_total_stats(self):
        nature_plus, nature_minus = self.nature_modifiers()
        total = {}
        for stat_name, base in self.base_stats.items():
            ev = self.evs.get(stat_name, 0)
            iv = 31  # assume perfect IVs
            if stat_name == "hp":
                total_val = ((2 * base + iv + (ev // 4)) * self.level) // 100 + self.level + 10
            else:
                nature_mult = 1.0
                if stat_name == nature_plus:
                    nature_mult = 1.1
                elif stat_name == nature_minus:
                    nature_mult = 0.9
                total_val = (((2 * base + iv + (ev // 4)) * self.level) // 100 + 5)
                total_val = int(total_val * nature_mult)
            total[stat_name] = total_val
        return total

    def __repr__(self):
        return f"{self.name} (Lv{self.level}) - {', '.join(self.types)}"

class OpponentPokemon:
    def __init__(self, name):
        self.name = name
        self.known_moves = []
        self.possible_items = []
        self.ability = None
        self.status = None
        self.current_hp = 100
        self.revealed = False
        self.types = []
        self.base_stats = {}
        self.max_stats = {}

    def calculate_max_stats(self):
        max_stats = {}
        for stat_name, base in self.base_stats.items():
            iv = 31
            ev = 252
            level = 100
            if stat_name == "hp":
                val = ((2 * base + iv + (ev // 4)) * level) // 100 + level + 10
            else:
                val = (((2 * base + iv + (ev // 4)) * level) // 100 + 5)
                val = int(val * 1.1)
            max_stats[stat_name] = val
        return max_stats
    
class BattleState:
    def __init__(self, your_team):
        self.your_team = your_team
        self.opponent_team = []
        self.current_ally = None
        self.current_enemy = None
        self.turn = 1
        self.history = []