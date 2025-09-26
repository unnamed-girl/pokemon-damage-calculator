# def test_terrain_order():
#     # Pelipper is FASTER, so its sunny
#     assert (
#         Format.gen9vgc()
#         .game(
#             PokemonBuilder("ninetales").iv(Stat.Speed, 0).ability(Ability.Drought),
#             PokemonBuilder("pelipper").ev(Stat.Speed, 252).ability(Ability.Drizzle),
#         )
#         .field.weather
#         == Weather.RainDance
#     )
