import hlt
import logging
import random
import copy

game = hlt.Game("Nugget")
defense_radius = 14
table = {}
first_move = True

def get_all_enemy_ships(game_map):
    enemy_ships = []
    players = game_map.all_players()
    for player in players:
        if player == game_map.get_me():
            continue
        enemy_ships.extend(player.all_ships())
    return enemy_ships

def is_under_attack(game_map, ship):
    enemies = get_all_enemy_ships(game_map)
    for enemy in enemies:
        if ship.calculate_distance_between(enemy) <= 5:
            return True
    return False

def get_attackers(game_map, ship):
    attackers = []
    enemies = get_all_enemy_ships(game_map)
    for enemy in enemies:
        if ship.calculate_distance_between(enemy) <= 5:
            attackers.append(enemy)
    return attackers

def pop_closest(obj, obj_list):
    min_seen = 1e10
    min_obj = None
    for obj2 in obj_list:
        dist = obj.calculate_distance_between(obj2)
        if dist < min_seen:
            min_seen = dist
            min_obj = obj2
    obj_list.remove(min_obj)
    return min_obj

def get_closest(obj, obj_list):
    min_seen = 1e10
    min_obj = None
    for obj2 in obj_list:
        dist = obj.calculate_distance_between(obj2)
        if dist < min_seen:
            min_seen = dist
            min_obj = obj2
    return min_obj


def get_object_to_object_proximity_list(game_map, obj, f=None):
    if f is None:
        f = lambda x: True
    entities_by_distance = game_map.nearby_entities_by_distance(obj)
    objects_in_distance_order = []
    for distance in sorted(entities_by_distance):
        objects_in_distance_order.extend([(entity, distance) for entity in entities_by_distance[distance] if f(entity)])
    return objects_in_distance_order


# main game logic
while True:
    game_map = game.update_map()
    command_queue = []
    ships = game_map.get_me().all_ships()
    planets = game_map.all_planets()

    # initialize ships
    if first_move:
        my_ships = game_map.get_me().all_ships()
        table[my_ships[0].id] = 'attack'
        table[my_ships[1].id] = 'protect'
        table[my_ships[2].id] = 'protect'

    # update table, remove the dead ships and add the new ones
    free_ships = [ship for ship in ships if
                         ship.docking_status == hlt.entity.Ship.DockingStatus.UNDOCKED]
    all_ships = [ship.id for ship in ships]

    for ship_id in list(table.keys()):
        if ship_id not in all_ships:
            del table[ship_id]

    for ship in free_ships:
        if ship.id not in table:
            table[ship.id] = random.choice(['attack', 'protect'])

    # get information on current layout
    enemy_ships = get_all_enemy_ships(game_map)
    docked_enemy_ships = [enemy for enemy in enemy_ships if
                          enemy.docking_status in [hlt.entity.Ship.DockingStatus.DOCKING,
                                                   hlt.entity.Ship.DockingStatus.DOCKED]]

    docked_ships = [ship for ship in ships if
                       ship.docking_status in [hlt.entity.Ship.DockingStatus.DOCKED,
                                               hlt.entity.Ship.DockingStatus.DOCKING]]

    ships_under_attack = [ship for ship in docked_ships if is_under_attack(game_map, ship)]
    enemy_attackers = [i for ship in ships_under_attack for i in get_attackers(game_map, ship)]

    empty_planets = [planet for planet in planets if
                                 planet.owner in [None, game_map.get_me()] and not planet.is_full()]
    dockable_planets = []
    for planet in empty_planets:
        for _ in range(planet.num_docking_spots):
            dockable_planets.append(planet)

    # assign ships to attack if no dockable planets
    orders = {}
    for ship in free_ships:
        if table[ship.id] == 'protect':
            if len(dockable_planets) > 0:
                target = pop_closest(ship, dockable_planets)
                orders[ship] = target
            else:
                table[ship.id] = 'attack'

    # handle orders for attacks
    docked_enemy_ships_copy = copy.copy(docked_enemy_ships)
    for ship in free_ships:
        if ship in orders:
            continue
        ship_type = table[ship.id]
        if ship_type == 'attack':
            if len(docked_enemy_ships) > 0:
                target = pop_closest(ship, docked_enemy_ships)
                orders[ship] = target
            elif len(docked_enemy_ships_copy) > 0:
                target = get_closest(ship, docked_enemy_ships_copy)
                orders[ship] = target
            else:
                target = get_closest(ship, enemy_ships)
                orders[ship] = target

    # if docked ships under attack
    if len(enemy_attackers) > 0:
        my_attacks = [ship for ship in free_ships if table[ship.id] == 'attack']
        for enemy in enemy_attackers:
            if len(my_attacks) > 0:
                closest_attack = get_closest(enemy, my_attacks)
                if closest_attack.calculate_distance_between(enemy) < defense_radius:
                    orders[closest_attack] = enemy
                    my_attacks.remove(closest_attack)

    # add navigate commands to queue for this turn
    for ship in orders:
        command = None
        target = orders[ship]
        if table[ship.id] == 'protect':
            if ship.can_dock(target):
                command = ship.dock(target)
            else:
                command = ship.navigate(
                    ship.closest_point_to(target),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    ignore_ships=False)
        elif table[ship.id] == 'attack':
            command = ship.navigate(
                ship.closest_point_to(target, min_distance=3),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                angular_step=2,
                ignore_ships=False)

        if command:
            command_queue.append(command)

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    first_move = False
