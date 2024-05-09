from game.display import announce, menu
from game.context import Context
from game.combat import Combat
# from game.player import Player 
from game.crewmate import CrewMate  
import random

class Kraken:
    def __init__(self):
        # Constructor for Kraken class
        self.health = 100

    def take_damage(self, damage):
        self.health -= damage

class KrakenEncounter(Context):
    def __init__(self, player):
        super().__init__()
        self.name = "kraken"
        self.kraken = Kraken()
        self.alive = True
        self.player = player
        self.combat = Combat([CrewMate() for _ in range(random.randint(3, 6))])

    def encounter(self):
        announce("You encounter a massive kraken in the depths of the sea.")
        while self.alive and self.player.gameInProgress and self.kraken.health > 0:
            self.player_action()

    def player_action(self):
        action = menu(["Attack with cannons", "Attack with harpoons", "Defend", "Sail away", "Befriend"])
        if action == 1:
            self.attack_with_cannons()
        elif action == 2:
            self.attack_with_harpoons()
        elif action == 3:
            self.defend()
        elif action == 4:
            self.sail_away()
        elif action == 5:
            self.befriend()

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
        announce("The crew braces for the kraken's attack, preparing to defend themselves.")
        # Perform defensive actions using Combat module
        self.combat.defend()
        announce("The crew successfully defends against the kraken's attack!")
        self.kraken_attack()  # Proceed with the kraken's attack

    def sail_away(self):
        announce("You manage to narrowly escape the kraken's grasp and continue your journey.")
        self.alive = False
    
    def befriend(self):
        if random.choice([True, False]):  # 50/50 chance of success
            announce("You successfully befriend the kraken!")
            # reward logic here
            food_reward = random.randint(50, 100)  # Random food supply between 50 and 100 units
            self.player.get_ship().add_food(food_reward)  # Add food reward to the ship
            announce("The kraken chirps happily and gives your crew some supplies before swimming away.")
            announce(f"You received {food_reward} units of food.")
            self.alive = False
        else:
            announce("Your attempt to befriend the kraken fails. It seems unwilling to cooperate.")
            self.kraken_attack()

    def kraken_attack(self):
        kraken_attack_power = random.randint(15, 25)
        # Select a crew member to get injured
        injured_crew_member = random.choice(self.player.get_pirates())
        injured_crew_member.health -= kraken_attack_power
        announce(f"The kraken attacks {injured_crew_member.get_name()}, dealing {kraken_attack_power} damage!")
        # Check if the crew member is killed
        if injured_crew_member.health <= 0:
            announce(f"{injured_crew_member.get_name()} has been killed by the kraken!")
            self.player.cleanup_pirates()  # Clean up the crew members
        else:
            announce(f"{injured_crew_member.get_name()} survives the kraken's attack with {injured_crew_member.health} health remaining.")
            announce(f"Kraken's health: {self.kraken.health}.")
