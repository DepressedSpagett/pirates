from game.display import announce, menu
from game import location
import game.config as config
from game.display import announce
from game.events import *
import random

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
        self.locations["cliffs"] = Cliffs(self)
        self.locations["fire_pit"] = FirePit(self)
        self.starting_location.locations["strange_boulder"] = StrangeBoulder(self.starting_location)

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
        self.verbs['explore_beach'] = self

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
        elif verb == "explore_beach":
            config.the_player.next_loc = self.locations["strange_boulder"]

class Cave(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "Cave"
        self.verbs['exit'] = self

    def enter(self):
        announce("You enter a dark cave. The air is thick with mystery.")
        self.explore_cave()

    def explore_cave(self):
        announce("You find yourself in a maze-like cave.")
        while True:
            direction = menu(["Go left", "Go right", "Go straight", "Exit"])
            if direction == 4:
                break
            else:
                self.traverse(direction)

        self.find_kraken_egg()

    def traverse(self, direction):
        roll = random.randint(1, 6)  # Roll a dice
        if roll > 3:  # Roll above 3, no dead end
            announce("You continue your journey through the cave.")
        else:
            announce("You hit a dead end. Time to backtrack.")

    def find_kraken_egg(self):
        announce("After navigating through the maze, you find a section of the cave with a nest.")
        announce("You cautiously approach and discover a kraken egg resting in the nest.")
        self.take_kraken_egg()

    def take_kraken_egg(self):
        decision = menu(["Take the kraken egg", "Leave it"])
        if decision == 1:
            announce("You carefully take the kraken egg.")
            # Add any rewards or consequences for taking the egg
            config.the_player.inventory.append("Kraken Egg")
        else:
            announce("You decide to leave the kraken egg undisturbed.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "exit":
            config.the_player.next_loc = self.main_location.locations["beach"]


class Cliffs(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "Cliffs"
        self.verbs['listen'] = self

    def enter(self):
        announce("You find yourself surrounded by sharp cliffs and rugged edges.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "listen":
            announce("You hear faint chanting in the distance.")
            self.encounter_rock_sage()

    def encounter_rock_sage(self):
        announce("Following the sound of chanting, you come across a mysterious old sage.")
        announce("The sage beckons you closer and presents you with three riddles.")

        correct_answers = 0
        for _ in range(3):
            riddle = self.get_riddle()
            answer = input(f"Sage's Riddle: {riddle} - Your answer: ")
            if self.check_answer(riddle, answer):
                announce("The sage nods in approval.")
                correct_answers += 1
            else:
                announce("The sage shakes his head.")
        
        if correct_answers >= 2:
            announce("Impressed by your wisdom, the sage rewards you with a diamond.")
            config.the_player.inventory.append("Diamond")
        else:
            announce("The sage looks disappointed. You leave without a reward.")

    def get_riddle(self):
        # Define a list of riddles
        riddles = [
            "What has a head, a tail, is brown, and has no legs?",
            "I'm tall when I'm young, and I'm short when I'm old. What am I?",
            "The more you take, the more you leave behind. What am I?"
        ]
        # Randomly select a riddle from the list
        return random.choice(riddles)

    def check_answer(self, riddle, answer):
        # Define a dictionary of correct answers for each riddle
        correct_answers = {
            "What has a head, a tail, is brown, and has no legs?": "Penny",
            "I'm tall when I'm young, and I'm short when I'm old. What am I?": "Candle",
            "The more you take, the more you leave behind. What am I?": "Footsteps"
        }
        # Check if the provided answer matches the correct answer
        return answer.lower() == correct_answers.get(riddle.lower(), "").lower()


class FirePit(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "Fire Pit"
        self.verbs['smoke'] = self

    def enter(self):
        announce("You stumble upon a fire pit with smoke billowing into the sky.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "smoke":
            announce("You follow the smoke signal and encounter a towering rock golem.")
            self.encounter_grill_master()

    def encounter_grill_master(self):
        announce("Before you stands the legendary Grill Master, a rock golem known for its BBQ skills.")
        announce("The Grill Master offers you free rewards for your journey.")
        kraken_egg = "Kraken Egg" in config.the_player.inventory
        diamond = "Diamond" in config.the_player.inventory

        if kraken_egg or diamond:
            announce("The Grill Master notices your special items and offers you a special reward.")
            self.reward_special()
        else:
            self.reward_normal()

    def reward_normal(self):
        announce("The Grill Master serves you a delicious BBQ feast.")
        # Provide normal rewards here

    def reward_special(self):
        announce("The Grill Master is impressed by your special items.")
        if "Kraken Egg" in config.the_player.inventory:
            announce("You present the Grill Master with the Kraken Egg.")
            announce("In return, the Grill Master grants you a special recipe for Kraken Egg BBQ.")
            # Provide special reward for Kraken Egg
        if "Diamond" in config.the_player.inventory:
            announce("You show the Grill Master the Diamond.")
            announce("The Grill Master crafts you a magical BBQ utensil.")
            # Provide special reward for Diamond


class StrangeBoulder(location.Location):
    def __init__(self, m):
        super().__init__(0, 0, m.world)
        self.name = "Strange Boulder"
        self.verbs['defeat'] = self
        self.kaptain_kragg_defeated = False

    def enter(self):
        announce("You spot a strange boulder with boots sticking out from beneath it.")
        if not self.kaptain_kragg_defeated:
            announce("As you approach, the ghostly figure of Kaptain Kragg emerges from the boulder.")

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "defeat":
            if not self.kaptain_kragg_defeated:
                self.defeat_kaptain_kragg()
            else:
                announce("You've already defeated Kaptain Kragg and claimed the treasure.")
        else:
            announce("You need to defeat Kaptain Kragg to claim the treasure.")

    def defeat_kaptain_kragg(self):
        announce("You engage in a fierce battle with the ghostly Kaptain Kragg.")
        # Perform battle logic here
        if True:  # Replace with actual battle outcome logic
            announce("You emerge victorious over Kaptain Kragg!")
            self.kaptain_kragg_defeated = True
            announce("Kaptain Kragg's treasure, phasing through the boulder, is now accessible.")
            self.reward_treasure()

    def reward_treasure(self):
        # Determine treasure reward and provide it to the crew
        announce("You obtain Kaptain Kragg's treasure.")


