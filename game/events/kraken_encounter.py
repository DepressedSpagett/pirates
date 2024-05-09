from game.display import announce, menu
import game.superclasses as superclasses
import game.items as items 
from game.context import Context
import game.config as config
import random

class Kraken:
    def __init__(self):
        # Constructor for Kraken class
        pass  # Placeholder for actual implementation

class KrakenEncounter(Context):
    def __init__(self):
        super().__init__()
        self.alive = True
        self.player_health = 100
        self.crew = [CrewMate() for _ in range(4)]  # Assuming there are 4 crew members
        self.kraken = Kraken()

    def encounter(self):
        announce("You encounter a massive kraken in the depths of the sea.")
        while self.alive and self.player_health > 0 and self.kraken.health > 0:
            self.player_action()

    def player_action(self):
        action = menu(["Attack with cannons", "Attack with harpoons", "Defend", "Sail away"])
        if action == 1:
            self.attack_with_cannons()
        elif action == 2:
            self.attack_with_harpoons()
        elif action == 3:
            self.defend()
        elif action == 4:
            self.sail_away()

    def attack_with_cannons(self):
        announce("You fire the ship's cannons at the kraken!")
        total_damage = sum(random.randint(20, 40) for _ in range(3))  # Assuming 3 cannons fired
        self.kraken.take_damage(total_damage)
        announce(f"You deal {total_damage} damage to the kraken!")
        if self.kraken.health <= 0:
            announce("You have defeated the kraken!")
            self.alive = False
        else:
            self.kraken_attack()

    def attack_with_harpoons(self):
        announce("You throw harpoons at the kraken!")
        total_damage = sum(random.randint(10, 20) for _ in range(4))  # Assuming 4 harpoons thrown
        self.kraken.take_damage(total_damage)
        announce(f"You deal {total_damage} damage to the kraken!")
        if self.kraken.health <= 0:
            announce("You have defeated the kraken!")
            self.alive = False
        else:
            self.kraken_attack()

    def defend(self):
        announce("You take a defensive stance, preparing for the kraken's next move.")
        self.kraken_attack()

    def sail_away(self):
        announce("You manage to narrowly escape the kraken's grasp and continue your journey.")
        self.alive = False

    def kraken_attack(self):
        kraken_attack_power = random.randint(15, 25)
        self.player_health -= kraken_attack_power
        announce(f"The kraken attacks you, dealing {kraken_attack_power} damage!")
        if self.player_health <= 0:
            announce("The kraken overwhelms you. You have been defeated.")
            self.alive = False
        else:
            announce(f"Your health: {self.player_health}. Kraken's health: {self.kraken.health}.")

class CrewMate(superclasses.CombatCritter):
    def __init__(self):
        super().__init__(random.choice(['Anne', 'Bartholomew', 'Benjamin', 'Po', 'Eliza', 'Edward', 'Grace', 'Henry', 'Mary', 'Paulsgrave', 'Jack', 'Turgut', 'William', 'Sayyida', 'Emanuel', 'Peter', 'Richard', 'Yang']), 100, 100 + random.randrange(-20, 21))
        self.skills = {
            "brawling": random.randrange(10, 101),
            "swords": random.randrange(10, 101),
            "melee": random.randrange(10, 101),
            "guns": random.randrange(10, 101),
            "cannons": random.randrange(10, 101),
            "swimming": random.randrange(10, 101)
        }
        self.items = [items.Cutlass(), items.Flintlock()]
        self.powder = 32
        self.sick = False
        self.lucky = False

    def start_day(self, ship):
        ship.take_food(self.get_hunger())
        if self.sick:
            self.inflict_damage(1, "Died of their illness")
            if self.health <= 0:
                announce(f"{self.name} has died of their illness!")
        elif self.hurtToday:
            self.hurtToday = False
        elif self.health < 100:
            if self.health >= 75:
                self.health += random.randint(1, 10)
            elif self.health >= 50:
                self.health += random.randint(1, 6)
            elif self.health >= 25:
                self.health += random.randint(1, 4)
            else:
                self.health += 1
            if self.health > 100:
                self.health = 100
        self.start_turn()

    def start_turn(self):
        self.reload()

    def end_day(self):
        if self.sick:
            if self.isLucky() or random.randint(1, 10) == 1:
                self.sick = False
        self.lucky = False

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "equip":
            if len(cmd_list) > 1:
                for i, item in enumerate(config.the_player.inventory):
                    if item.name == cmd_list[1]:
                        found = config.the_player.inventory.pop(i)
                        self.items.append(found)
                        self.items.sort()
                        break
            else:
                announce("Equip what?")
        elif verb == "unequip":
            if len(cmd_list) > 1:
                for i, item in enumerate(self.items):
                    if item.name == cmd_list[1]:
                        found = self.items.pop(i)
                        config.the_player.inventory.append(found)
                        config.the_player.inventory.sort()
                        break
            else:
                announce("Unequip what?")
        elif verb == "inventory":
            self.print_inventory()
        elif verb == "restock":
            if config.the_player.location != config.the_player.ship:
                announce("Powder and shot can only be restocked on the ship!")
            else:
                self.restock()
        elif verb == "skills":
            self.print_skills()
        else:
            print(f"{self.name} doesn't know how to {verb}")

    def print_inventory(self):
            for item in self.items:
                print(item)
            print()

    def restock(self):
        restock_needed = 32 - self.powder
        if config.the_player.powder > restock_needed:
            self.powder += restock_needed
            config.the_player.powder -= restock_needed
        else:
            self.powder += config.the_player.powder
            config.the_player.powder = 0
        if restock_needed == 0:
            announce(f"{self.name} doesn't need a restock!")
        elif config.the_player.powder == 0:
            if restock_needed < (32 - self.powder):
                announce(f"{self.name} takes the last powder!")
            else:
                announce(f"{self.name} reports that the ship is out of powder!")
        else:
            announce(f"{self.name} restocks their powder and shot!")

    def reload(self):
        for item in self.items:
            item.recharge(self)

    def getAttacks(self):
        for defendee in self.defendees:
            defendee.removeDefender(self)
        self.defendees = []
        options = []
        for item in self.items:
            attack_list = item.getAttacks(self)
            if len(attack_list) > 0:
                for putative_attack in attack_list:
                    if putative_attack not in options:
                        options.append(putative_attack)
        if "brawling" in self.skills.keys():
            options.append(superclasses.CombatAction("punch", superclasses.Attack("punch", "punches", self.skills["brawling"], (1, 11), False), self))
        options.append(superclasses.CombatAction("defend", superclasses.Defend("defend", "defends"), self))
        return options
# Main code
if __name__ == "__main__":
    kraken_encounter = KrakenEncounter()
    kraken_encounter.encounter()