from game import location
import game.config as config
from game.display import announce
from game.events import *

class KraggyRockIsland(location.Location):
    def __init__(self, x, y, w):
        super().__init__(x, y, w)
        self.name = "Kraggy Rock Island"
        self.symbol = 'K'
        self.visitable = True
        self.starting_location = RockyBeach(self)
        self.locations = {}
        self.locations["beach"] = self.starting_location
        self.locations["cave"] = Cave(self)
        self.locations["rocks"] = Rocks(self)
        self.locations["fire_pit"] = FirePit(self)
        self.locations["strange_boulder"] = StrangeBoulder(self)

    def enter(self, ship):
        print("Arrived at Kraggy Rock Island.")

    def visit(self):
        config.the_player.location = self.starting_location
        config.the_player.location.enter()
        super().visit()

class RockyBeach(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "Rocky Beach"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

    def enter(self):
        announce("You've made landfall at Kraggy Rock Island and landed on a rocky beach.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "south":
            announce("You return to your ship.")
            config.the_player.next_loc = config.the_player.ship
            config.the_player.visiting = False
        elif verb == "north":
            config.the_player.next_loc = self.main_location.locations["cave"]
        elif verb in ["east", "west"]:
            announce("You walk all the way around the island on the beach. There is nothing but rocks.")

class Cave(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "Cave"
        self.verbs['exit'] = self

    def enter(self):
        announce("You enter a dark cave. The air is thick with mystery.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "exit":
            config.the_player.next_loc = self.main_location.locations["beach"]

class Rocks(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "Rocks"
        self.verbs['talk'] = self

    def enter(self):
        announce("You find yourself surrounded by sharp cliffs and rugged edges.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "talk":
            announce("You hear faint chanting in the distance.")

class FirePit(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "Fire Pit"
        self.verbs['smoke'] = self

    def enter(self):
        announce("You stumble upon a fire pit with smoke billowing into the sky.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "smoke":
            announce("You follow the smoke signal and encounter a mysterious figure.")

class StrangeBoulder(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "Strange Boulder"
        self.verbs['defeat'] = self

    def enter(self):
        announce("You spot a strange boulder with boots sticking out from beneath it.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "defeat":
            announce("You prepare to face the ghost of Kaptain Kragg.")

