import hlt
import logging
from collections import OrderedDict
game = hlt.Game("Nugget 2.0")
logging.info("Starting Nugget")

while True:
    game_map = game.update_map()
    command_queue = []
    ships = game_map.get_me().all_ships()
    planets = game_map.all_planets()

    for ship in ships:
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]
        big_planets = sorted(closest_empty_planets, key=lambda i: i.radius, reverse=True)

        my_ships = game_map.get_me().all_ships()
        closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] not in my_ships]

        # If there are any empty planets, try to dock
        if len(closest_empty_planets) > 1:
            i = 0
            j = 0
            # if closest planets share the radius, pick the biggest radius
            while closest_empty_planets[i].radius == closest_empty_planets[j].radius and j < (len(closest_empty_planets) - 1):
                target_planet = big_planets[0]
                j += 1

            # if different radius, pick the closest planet
            if closest_empty_planets[i].radius != closest_empty_planets[j].radius:
                target_planet = closest_empty_planets[0]

            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                navigate_command = ship.navigate(
                            ship.closest_point_to(target_planet),
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)

                if navigate_command:
                    command_queue.append(navigate_command)

        # If no empty planets, attack enemy ships
        elif len(closest_enemy_ships) > 0:
            target_ship = closest_enemy_ships[0]
            navigate_command = ship.navigate(
                        ship.closest_point_to(target_ship),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=False)

            if navigate_command:
                command_queue.append(navigate_command)

    game.send_command_queue(command_queue)
    # TURN END
# GAME END
