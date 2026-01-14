import util

def till_entity(entity):
    needs_soil = {Entities.Pumpkin, Entities.Carrot, Entities.Sunflower}
    should_be_soil = (entity in needs_soil)
    is_soil = (get_ground_type() == Grounds.Soil)

    if should_be_soil != is_soil:
        till()


def grow(entity):
    if can_harvest():
        harvest()
    type = get_entity_type()
    if (type == None) or (type == Entities.Dead_Pumpkin) or (type == Entities.Grass):
        till_entity(entity)
        plant(entity)


def get_entity_yield(entity):
    item = util.entity_to_item(entity)
    start_amount = num_items(item)
    till_entity(entity)
    plant(entity)
    while not can_harvest():
        pass
    harvest()
    return num_items(item) - start_amount


def default_yield(update):
    default = {
        Entities.Bush: 80,
        Entities.Carrot: 80,
        Entities.Grass: 16,
        Entities.Pumpkin: 4, # multiply * 6
        Entities.Sunflower: 1,
        Entities.Tree: 400,
    }
    if update:
        for ent in default:
            default[ent] = get_entity_yield(ent)
    return default


def item_to_grow(item):
    convert = {
        Items.Carrot: carrot,
        Items.Hay: grass,
        Items.Power: power,
        Items.Pumpkin: pumpkin,
        Items.Wood: wood,
    }
    return convert[item]


def grass():
    polyculture(Entities.Grass)


def carrot():
    polyculture(Entities.Carrot)


def wood():
    # Wood is a special case since it can be bush or tree
    polyculture("wood")


def polyculture(entity):
    companions = {}
    world_size = get_world_size()

    for _ in range(world_size):
        x = get_pos_x()
        for _ in range(world_size):
            y = get_pos_y()
            # First, check if need to plant a companion on this position
            if (x, y) in companions:
                grow(companions[(x, y)])
                companions.pop((x, y))
            else:
                # Otherwise, we grow our resource
                if entity == "wood":
                    if (x + y) % 2 == 0:
                        grow(Entities.Bush)
                    else:
                        grow(Entities.Tree)
                else:
                    grow(entity)

                # And check if this resource has a companion
                plant_type, (xx, yy) = get_companion()
                if plant_type:
                    companions[(xx, yy)] = plant_type

            move(North)
        move(East)


def pumpkin():
    util.goto(0, 0)
    # Farm pumpkins in multiple cycles
    # 1. First loop, plant
    plant_one_field(grow, Entities.Pumpkin)

    # 2. Second loop, check pumpkins and create list.
    replaced_pumpkins = []
    world_size = get_world_size()
    for x in range(world_size):
        for y in range(world_size):
            ent = get_entity_type()
            if ent == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
                replaced_pumpkins.append((get_pos_x(), get_pos_y()))
            elif ent != Entities.Pumpkin:
                harvest()
                plant(Entities.Pumpkin)
                replaced_pumpkins.append((get_pos_x(), get_pos_y()))
            move(North)
        move(East)

    # 3. Only check the replaced pumpkins
    while len(replaced_pumpkins) > 0:
        for pos in replaced_pumpkins[:]:   # ← iterate o=ver a copy of the list to prevent index shifting
            util.goto(pos[0], pos[1])
            if get_entity_type() == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
            if can_harvest():
                replaced_pumpkins.remove(pos)

    # Harvest one big pumpkin
    harvest()


def power():
    util.goto(0, 0)
    measured_power = {}
    world_size = get_world_size()
    for x in range(world_size):
        for y in range(world_size):
            grow(Entities.Sunflower)
            measured_power[(get_pos_x(), get_pos_y())] = measure()
            move(North)
        move(East)

    max_power = 15
    while max_power >= 7:
        for pos in measured_power:
            if measured_power[pos] == max_power:
                util.goto(pos[0], pos[1])
                harvest()
        max_power -= 1


def plant_one_field(func, args):
    world_size = get_world_size()
    for x in range(world_size):
        for y in range(world_size):
            func(args)
            move(North)
        move(East)
