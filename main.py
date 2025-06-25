from parser import load_team_from_url, parse_showdown_team, get_base_stats
from models import Pokemon, BattleState, OpponentPokemon

pokepaste_url = "https://pokepast.es/45e2ed168db6ed11"

try:
    team_txt = load_team_from_url(pokepaste_url)
    parsed_team = parse_showdown_team(team_txt)

    your_team = []
    for mon in parsed_team:
        base = get_base_stats(mon["name"])
        if base:
            poke = Pokemon(
                name=mon["name"],
                level=mon.get("level", 100),
                nature=mon.get("nature"),
                item=mon.get("item"),
                ability=mon.get("ability"),
                evs=mon.get("evs"),
                moves=mon.get("moves"),
                types=base["types"],
                base_stats=base["stats"]
            )
            your_team.append(poke)
        else:
            print(f"⚠️ Skipping {mon['name']} due to API issue")


    print("\nYour Team:")
    for mon in your_team:
        print(mon)
        print("  Abilities:" + " " + (mon.ability))
        print("  Moves:", ", ".join(mon.moves))
        print("  Total Stats:")
        for stat, val in mon.total_stats.items():
            print(f"    {stat}: {val}")
        print()

except Exception as e:
    print("❌ Error loading team:", e)

battle = BattleState(your_team)
enemy_input = input("Enter enemy Pokémon (comma-separated): ")
enemy_names = [name.strip() for name in enemy_input.split(",") if name.strip()]
battle.opponent_team = [OpponentPokemon(name) for name in enemy_names]

if battle.opponent_team:
    battle.current_enemy = battle.opponent_team[0]

for mon in battle.opponent_team:
    base = get_base_stats(mon.name)
    if base:
        mon.types = base["types"]
        mon.base_stats = base["stats"]
        mon.max_stats = mon.calculate_max_stats()
    else:
        print(f"⚠️ Failed to fetch data for {mon.name}")

stat_abbr = {
    "hp": "HP",
    "attack": "AT",
    "defense": "DF",
    "special-attack": "SA",
    "special-defense": "SD",
    "speed": "SP"
}

print("\nEnemy Team:")
for mon in battle.opponent_team:
    print(mon.name)
    print(f"  Types: {', '.join(mon.types)}")
    print("  Stats:")
    for stat, val in mon.base_stats.items():
        base_val = mon.base_stats[stat]
        max_val = mon.max_stats.get(stat, "N/A")
        abbr = stat_abbr.get(stat, stat[:2].upper())
        print(f"    {abbr:<2}  Base: {base_val:<4} Max: {max_val}")
    print()
