from game import location
import game.config as config
from game.display import announce
from game.events import *
from game.items import Item
import random
from game import event
from game.combat import Monster
import game.combat as combat

class Island (location.Location):

    def __init__ (self, x, y, w):
        super().__init__(x, y, w)
        self.name = "island"
        self.symbol = 'J'
        self.visitable = True
        self.starting_location = Campsite(self)
        self.locations = {}
        self.locations["campsite"] = self.starting_location
        self.locations["waterbridge"] = Waterbridge(self)
        self.locations["treasure site"] = Treasuresite(self)
        self.locations["waterfall"] = Waterfall(self)
        self.locations["abandoned fort"] = Abandonedfort(self)

    def enter (self, ship):
        print ("You arrive on an island.")

    def visit (self):
        config.the_player.location = self.starting_location
        config.the_player.location.enter()
        super().visit()

class Campsite (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "campsite"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self
    
    def enter (self):
        announce ("You arrived at a campsite.")

    def HandleCampsite(self):
        choice = input("Do you proceed to light up the campfire?")
        if("yes" in choice.lower()):
            self.HandleCampfire()
        else:
            print("You turn away from the campsite.")

    def HandleCampfire(self):
        announce("You have used the campfire. Your party health has fully recovered")
        for i in config.the_player.get_pirates():
            i.health = i.max_health

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south"):
            announce ("You return to the ship.")
            config.the_player.next_loc = config.the_player.ship
            config.the_player.visiting = False
        elif (verb == "east"):
            config.the_player.next_loc = self.main_location.locations["waterbridge"]
        elif (verb == "west" or verb == "north"):
            announce ("You walk all the way around the campsite to stretch your legs.")
            self.HandleCampsite()

class Goblin(Monster):
    
    def __init__(self):
        attacks = {}
        attacks["strike"] = ["strikes", random.randint(20, 30), (5, 10)]
        super().__init__("Goblin", random.randint(30, 50), attacks, 50 + random.randint(0, 10)) 

class GoblinEvent(event.Event):

    def __init__(self):
        self.name = "Goblin ambush"

    def process(self, world):
        result = {}
        goblins = [Goblin(), Goblin()]  # Assuming there are two goblins in the encounter
        announce("You are ambushed by goblins!")
        combat.Combat(goblins).combat()
        announce("The goblins are defeated. It is now safe to cross the bridge.")
        result["newevents"] = []
        result["message"] = ""
        return result

class Waterbridge(location.SubLocation):
    
    def __init__(self, m):
        super().__init__(m)
        self.name = "waterbridge"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self
        self.event_chance = 100
        self.goblins_defeated = False
        self.goblin_event = GoblinEvent()  # Create the GoblinEvent instance here

    def enter(self):
        announce("You arrived at a waterbridge.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "west":
            announce("You return to the campsite.")
            config.the_player.next_loc = config.the_player.campsite
            config.the_player.visiting = False
        elif verb == "north":
            if not self.goblins_defeated:
                self.goblin_encounter()
            else:
                announce("You cross the bridge safely.")
                config.the_player.next_loc = self.main_location.locations["treasure site"]
                config.the_player.go = True
        elif verb == "south" or verb == "east":
            announce("You can't go south or east, there is no land to walk on besides the bridge up front.")

    def goblin_encounter(self):
        announce("You encounter goblins blocking the bridge!")
        result = self.goblin_event.process(None)  # Process the goblin event
        if "newevents" in result and not result["newevents"]:
            self.goblins_defeated = True  # Set the flag to True after defeating the goblins
            return True  # Goblins were defeated
        return False  # Goblins were not defeated 

class Mierlurk(Monster):
    
    def __init__(self):
        attacks = {}
        attacks["claw"] = ["claws", random.randint(20, 40), (5, 10)]
        super().__init__("Mierlurk", random.randint(60, 80), attacks, 60 + random.randint(0, 10))

class Armor(Item):
    def __init__(self):
        super().__init__("armor", 50)  # Price in shillings
        self.health_boost = 10

class TreasureMap(Item):
    def __init__(self):
        super().__init__("treasure map", 0)  # Price in shillings (irrelevant for this item)

class Treasuresite(location.SubLocation):

    def __init__(self, m):
        super().__init__(m)
        self.name = "treasure site"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self
        self.event_chance = 100
        self.events.append(MierlurkEvent())

    def enter(self):
        announce("You arrived at a treasure site.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "south":
            announce("You return to the waterbridge.")
            config.the_player.next_loc = config.the_player.waterbridge
            config.the_player.visiting = False
        elif verb == "west":
            config.the_player.next_loc = self.main_location.locations["waterfall"]
            config.the_player.go = True
        elif verb == "north" or verb == "east":
            announce("You walk all the way around the treasure site. You find nothing but sand.")

    def miniboss_encounter(self):
        announce("You encounter a Mierlurk!")
        mierlurk = Mierlurk()
        combat.Combat([mierlurk]).combat()
        announce("The Mierlurk is defeated. It seemed to be guarding something...")
        event_result = self.find_treasure()
        if event_result == "dig":
            self.reward_player()

    def find_treasure(self):
        announce("You dig around where the Mierlurk was guarding and find a treasure chest poking out of the sand.")
        announce("Inside the treasure chest, you find armor and a treasure map.")
        return input("Do you want to open the treasure chest? (yes/no): ")

    def reward_player(self):
        armor = Armor()
        treasure_map = TreasureMap()
        config.the_player.add_to_inventory([armor, treasure_map])

class MierlurkEvent(event.Event):

    def __init__(self):
        self.name = "Mierlurk ambush"

    def process(self, world):
        result = {}
        mierlurk = Mierlurk()
        announce("You are ambushed by a Mierlurk!")
        combat.Combat([mierlurk]).combat()
        announce("The Mierlurk is defeated. It seemed to be guarding something...")
        announce("You dig around where the Mierlurk was guarding and find a treasure chest poking out of the sand.")
        announce("Inside the treasure chest, you find armor and a treasure map.")
        announce("The treasure map indicates that there is very good loot at the abandoned fort.")
        result["newevents"] = []
        result["message"] = ""
        return result

class Waterfall(location.SubLocation):

    def __init__(self, m):
        super().__init__(m)
        self.name = "waterfall"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self
        self.riddletrigger = False

    def enter(self):
        announce("You arrived at a waterfall.")
        if not self.riddletrigger:
            self.prompt_riddle()

    def prompt_riddle(self):
        announce("A mysterious voice echoes from behind the waterfall:")
        announce("You seek passage to the abandoned fort? Answer me this riddle:")
        announce("I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?")
        self.riddletrigger = True
        self.solve_riddle()

    def solve_riddle(self):
        choice = input("Your answer: ")
        if choice.lower() == "echo":
            announce("The voice booms with approval: 'Correct! You may proceed to the abandoned fort.'")
            self.reward_player()
            config.the_player.next_loc = self.main_location.locations["abandoned fort"]
        else:
            announce("The voice sighs: 'Incorrect. You may try again later.'")

    def reward_player(self):
        announce("You have guessed correctly. The waterfall blesses your crew with health and luck.")
        for pirate in config.the_player.get_pirates():
            pirate.lucky = True
            pirate.sick = False
            pirate.health = pirate.max_health

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "west":
            announce("You return to the treasure site.")
            config.the_player.next_loc = config.the_player.treasuresite
            config.the_player.visiting = False
        elif verb == "north":
            if self.riddletrigger:  # Check if riddle is solved
                config.the_player.next_loc = self.main_location.locations["abandoned fort"]
            else:
                announce("A mysterious force prevents you from entering. Perhaps you should solve the riddle first.")
        elif verb == "east" or verb == "south":
            announce("You walk all the way around the waterfall. The waterfall looks nice and all, but it seems like there is a passage through the waterfall.")

class Abandonedfort(location.SubLocation):

    def __init__(self, m):
        super().__init__(m)
        self.name = "abandoned fort"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self
        self.event_chance = 100
        self.boss_defeated = False

    def enter(self):
        announce("You arrived at an abandoned fort.")
        if not self.boss_defeated:
            self.boss_fight()
        else:
            announce("You see a room guarded by the giant skeleton. It seems you've already defeated the boss.")
            self.enter_treasure_room()

    def boss_fight(self):
        announce("You encounter a towering figure, a giant skeleton!")
        boss = GiantSkeleton()
        combat.Combat([boss]).combat()
        announce("The giant skeleton collapses to the ground.")
        self.boss_defeated = True
        self.enter_treasure_room()

    def enter_treasure_room(self):
        announce("You enter the room previously guarded by the giant skeleton.")
        announce("You find many golden coins and shillings scattered everywhere!")
        announce("Congratulations! You've found the grand prize.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "south":
            announce("You've gone too far and cannot turn back.")
        elif verb == "north":
            announce("You return to the previous location.")
            config.the_player.next_loc = self.main_location.locations["previous location"]
            config.the_player.go = True
        elif verb in ("east", "west"):
            announce("You walk around the fort, but find nothing of interest.")

class GiantSkeleton(Monster):
    
    def __init__(self):
        attacks = {}
        attacks["strike"] = ["strikes", random.randint(70, 90), (5, 15)]
        super().__init__("Giant Skeleton", random.randint(80, 120), attacks, 80 + random.randint(0, 10))