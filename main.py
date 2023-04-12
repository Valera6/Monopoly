import random, os
from math import sqrt as sqrt
from time import sleep

starting_capital = 950
speed_dice = False
GUI = True

import pygame as p # I'd do it inside if GUI==True, but player's img is inside __init__ of Player(), so have to load those every time
p.font.init()
if GUI == True:
    BOARD_IMG = p.image.load(os.path.join('imgs', 'board.jpg'))
    BOARD_IMG = p.transform.rotate(BOARD_IMG, 270)
    HOUSE_IMG = p.image.load(os.path.join('imgs', 'house.png'))
    HOUSE_IMG = p.transform.scale(HOUSE_IMG, (30, 30))
    HOTEL_IMG = p.image.load(os.path.join('imgs', 'hotel.png'))
    HOTEL_IMG = p.transform.scale(HOTEL_IMG, (35, 35))

    red, yellow, green, blue, purple, pink = (255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (128, 0, 128), (255, 192, 203)
    white, black = (255, 255, 255), (0, 0, 0)
    WIDTH = 740
    HEIGHT = 740
    win = p.display.set_mode((WIDTH, HEIGHT), p.RESIZABLE)
    p.display.set_caption('Monopoly Game')
    background = p.transform.smoothscale(BOARD_IMG, (WIDTH, HEIGHT))
side = 100
BLUE = p.image.load(os.path.join('imgs', 'blue_ball.png'))
BLUE = p.transform.scale(BLUE, (side, side))
GREEN = p.image.load(os.path.join('imgs', 'green_ball.png'))
GREEN = p.transform.scale(GREEN, (side, side))
PINK = p.image.load(os.path.join('imgs', 'pink_ball.png'))
PINK = p.transform.scale(PINK, (side, side))
PURPLE = p.image.load(os.path.join('imgs', 'purple_ball.png'))
PURPLE = p.transform.scale(PURPLE, (side, side))
YELLOW = p.image.load(os.path.join('imgs', 'yellow_ball.png'))
YELLOW = p.transform.scale(YELLOW, (side, side))

class Player:
    def __init__(self, name, starting_capital, img, color, position_offset):
        self.name = name
        self.balance = starting_capital

        self.color = color #needed for GUI
        self.img = img #needed for GUI
        self.position_offset = position_offset #needed for GUI

        self.position = 0
        self.streets_owned = []
        self.active_railroads = 0
        self.active_utilities = 0
        self.bankrupt = False
        self.jail = 0   # if above 0, signifies the number of the day in jail: 1 to 3
        
        self.rolled = 0 # for Utilities streets
        self.pay_double = False
        self.get_out_of_jail_free_cards = 0
        self.in_action = False # stupid fix of rerouting to self.action()
        self.bot = False if self.__class__.__name__ == 'Player' else True # stupid fix to substitute rewriting the entire check_position() function in all AIs
        self.interested = [] # the streets that would complete the color complex for the player

    def rollTheDice(self): # main() calls to this function
        self.in_action = False
        self.pay_double = False
        if not self.jail:
            double_count = 0
            while True:
                dice1 = random.randint(1, 6)
                dice2 = random.randint(1, 6)
                if dice1 != dice2:
                    throw = dice1+dice2
                    print(f"{self.name} threw {throw}")
                    self.position += throw
                    self.rolled = throw
                    if self.position > 39:
                        self.position = self.position % 40
                        self.balance += 200
                    self.check_position()
                    break
                else:
                    if double_count < 2:
                        double_count += 1
                        print(f"{self.name} rolled a double. {3-double_count} more tries until jail")
                    else:
                        print(f"{self.name} rolled 3 doubles and is going to jail")
                        self.jail = 1
                        self.position = 10
                        can_act = False
                        if len(self.streets_owned):
                            for street in self.streets_owned:
                                if street.monopoly == True:
                                    can_act = True
                        if can_act:
                            self.action()
                        break
        else:
            while True:
                user_input = self.jail_choice()
                if user_input == 'd':
                    dice1 = random.randint(1, 6)
                    dice2 = random.randint(1, 6)
                    if dice1==dice2:
                        throw = dice1+dice2
                        print(f"{self.name} threw a double {dice1} and is out of jail")
                        self.position += throw
                        self.rolled = throw
                        self.jail = 0
                        self.check_position()
                        break
                    else:
                        if self.jail < 3:
                            print(f'{self.name} threw {dice1} and {dice2}, and is remaining in jail for {3-self.jail} more days')
                            self.jail += 1
                            self.action()
                            break
                        else:
                            throw = dice1+dice2
                            print(f"{self.name} threw {throw}, paid $50, and is out of jail")
                            self.position += throw
                            self.rolled = throw
                            self.balance -= 50
                            self.jail = 0
                            self.check_if_bankrupt()
                            self.check_position()
                            break
                elif user_input == 'p':
                    if self.balance >= 50:
                        self.balance -= 50
                        self.jail = 0
                        self.rollTheDice()
                        break
                    else:
                        print("You don't have enough money even for that. Throw and hope")
                elif user_input == 'c':
                    if self.get_out_of_jail_free_cards:
                        self.get_out_of_jail_free_cards -= 1
                        self.jail = 0
                        self.rollTheDice()
                        break
                    else:
                        print('You have none. Accept your faith')
                else:
                    print('Try stretching your fingers')
    def jail_choice(self):
        return input(f'{self.name}, you can throw dice ("d"), pay $50 ("p"), or use Get Out of Jail Free Card ("c"): ')
    def check_position(self):
        if GUI == True:
            draw_window()
        self.position = self.position % 40
        board_property = board[self.position]
        if board_property.price == "N/A": # this means the player cannot purchase the street

            if board_property.street_name == 'Jail/Visiting Jail':
                print(f'{self.name} is visiting jail')
                self.action()
            elif board_property.street_name == 'Luxury Tax':
                print(f'{self.name} landed on Luxury Tax and has been fined $100')
                self.balance -= 100
                self.check_if_bankrupt()
                self.action()
            elif board_property.street_name == 'Income Tax':
                print(f'{self.name} landed on Income Tax and has been fined $200')
                self.balance -= 200
                self.check_if_bankrupt()
                self.action()
            elif board_property.street_name == 'Go to Jail':
                print(f'{self.name} landed on Go to Jail and has been arrested')
                self.jail = 1
                self.position = 10
                draw_window()
                can_act = False
                if len(self.streets_owned):
                    for street in self.streets_owned:
                        if street.monopoly == True:
                            can_act = True
                if can_act:
                    self.action()
            elif board_property.street_name == 'Community Chest':
                print(f'{self.name} landed on Community Chest')
                self.community_chest()
            elif board_property.street_name == 'Chance': # chance streets
                print(f'{self.name} landed on Chance')
                self.chance()
            else:
                print(f'{self.name} landed on {board_property.street_name}')
                self.action()
        else:
            if board_property.owner == 'Bank':
                print(f'{self.name} landed on {board_property.street_name}')
                if not self.bot:
                    user_action = input(f'Do you want to buy for ${board_property.price}? (Y/n): ')
                    if user_action == 'Y':
                        board_property.purchase_street(self)
                        self.action()
                    elif user_action == 'n':
                        self.action()
                    else:
                        print('Wrong answer.')
                        self.action()
                else:
                    self.action()
            elif board_property.owner != 'Bank' and board_property.owner.name != self.name and board_property.mortgaged==False:
                if board_property.color_group != 'Utilities':
                    print(f'{self.name} landed on {board_property.street_name} and was charged ${board_property.rent} by {board_property.owner.name}')
                    self.pay_rent(board_property)
                    self.action()
                else:
                    print(f'{self.name} landed on {board_property.street_name} and was charged ${board_property.rent*self.rolled} by {board_property.owner.name}')
                    self.action()
            else: # either owned by you or mortgaged
                print(f'{self.name} landed on {board_property.street_name}')
                self.action()
    def community_chest(self):
        r = random.randint(1, 16)
        if r == 1:
            print('Advance to Go (Collect $200)')
            self.position = 0
            self.balance += 200
        elif r == 2:
            print('Bank error in your favor. Collect $200')
            self.balance += 200
        elif r == 3:
            print("Doctor's fee. Pay $50")
            self.balance -= 200
            self.check_if_bankrupt()
        elif r == 4:
            print('From sale of stock you get $50')
            self.balance += 50
        elif r == 5:
            print('Get Out of Jail Free Card')
            self.get_out_of_jail_free_cards += 1
        elif r == 6:
            print('Go to Jail. Go directly to jail, do not pass Go, do not collect $200')
            self.jail = 1
            self.position = 10
        elif r == 7:
            print('Holiday fund matures. Receive $100')
            self.balance += 100
        elif r == 8:
            print('Income tax refund. Collect $20')
            self.balance += 20
        elif r == 9:
            print('It is your birthday. Collect $10 from every player')
            for player in players:
                if player != self:
                    player.balance -= 10
                    self.balance += 10
                else:
                    pass
        elif r == 10:
            print('Life insurance matures. Collect $100')
            self.balance += 100
        elif r == 11:
            print('Pay hospital fees of $100')
            self.balance -= 100
            self.check_if_bankrupt()
        elif r == 12:
            print('Pay school fees of $50')
            self.balance -= 50
            self.check_if_bankrupt()
        elif r == 13:
            print('Receive $25 consultancy fee')
            self.balance += 25
        elif r == 14:
            print('You are assessed for street repair. $40 per house. $115 per hotel')
            for street in self.streets_owned:
                if street.houses == 5:
                    self.balance -= 115
                for house in range(street.houses):
                    self.balance -= 40
            self.check_if_bankrupt()
        elif r == 15:
            print('You have won second prize in a beauty contest. Collect $10')
            self.balance += 10
        elif r == 16:
            print('You inherit $100')
            self.balance += 100
        self.action()
    def chance(self):
        r = random.randint(1, 16)
        if r == 1:
            print('Advance to Boardwalk')
            self.position = 39
            self.check_position()
        if r == 2:
            print('Advance to Go (Collect $200)')
            self.position = 0
            self.balance += 200
        if r == 3:
            print('Advance to Illinois Avenue. If you pass Go, collect $200')
            if self.position % 40 > 24:
                self.balance += 200
            self.position = 24
            self.check_position()
        if r == 4:
            print('Advance to St. Charles Place. If you pass Go, collect $200')
            if self.position % 40 > 11:
                self.balance += 200
            self.position = 11
            self.check_position()
        if r == 5 or r == 6:
            print('Advance to the nearest Railroad. If unowned, you may buy it from the Bank.\nIf owned, pay wonder twice the rental to which they are otherwise entitled')
            up = self.position % 40
            down = up
            while True:
                up += 1
                down -= 1
                if up % 5 == 0 and up % 10 != 0:
                    self.position = up
                    break
                elif down % 5 == 0 and down % 10 != 0:
                    self.position = down
                    break
            self.pay_double = True
            self.check_position()
        if r == 7:
            print('Advance token to nearest Utility. If unowned, you may buy it from the Bank.\nIf owned, throw dice and pay owner a total ten times amount thrown.')
            up = self.position % 40
            down = up
            while True:
                up += 1
                down -= 1
                if up == 12 or up == 28:
                    self.position = up
                    break
                elif down == 12 or down == 28:
                    self.position = down
                    break
            self.pay_double = True
            self.check_position()
        if r == 8:
            print('Bank pays you dividend of $50')
            self.balance += 50
        if r == 9:
            print('Get Out of Jail Free Card')
            self.get_out_of_jail_free_cards += 1
        if r == 10:
            print('Go Back 3 Spaces')
            self.position -= 3
            self.check_position()
        if r == 11:
            print('Go to Jail. Go directly to Jail, do not pass Go, do not collect $200')
            self.jail = 1
            self.position = 10
        if r == 12:
            print('Make general repairs on all your property. For each house pay $25. For each hotel pay $100')
            for street in self.streets_owned:
                if street.houses == 5:
                    self.balance -= 100
                elif street.houses:
                    for house in range(street.houses):
                        self.balance -= 25
            self.check_if_bankrupt()
        if r == 13:
            print('Speeding fine $15')
            self.balance += 15
        if r == 14:
            print('Take a trip to Reading Railroad. If you pass Go, collect $200')
            if self.position > 5:
                self.balance += 200
            self.position = 5
            self.check_position()
        if r == 15:
            print('You have been elected Chairman of the Board. Pay each player $50')
            for player in players:
                if player != self:
                    player.balance += 50
                    self.balance -= 50
            self.check_if_bankrupt()
        if r == 16:
            print('Your building loan matures. Collect $150')
            self.balance += 150
        self.action()
    def pay_rent(self, street):
        if street.color_group == 'Utilities':
            rent_amt = street.rent * self.rolled
        else:
            rent_amt = street.rent

        if self.pay_double:
            rent_amt *= 2
            self.pay_double = False

        self.balance -= rent_amt
        if self.balance >= 0:
            street.owner.balance += rent_amt
            print(f'{self.name} has paid {street.owner.name} ${rent_amt}')
            self.action()
        else:
            self.check_if_bankrupt()
            if self.balance > 0:
                street.owner.balance += rent_amt
                print(f'{self.name} has paid {street.owner.name} ${rent_amt}')
            else:
                street.owner.balance += rent_amt + self.balance
                print(f'{self.name} has paid {street.owner.name} all he had left: ${rent_amt+self.balance}')
                self.balance = 0
    def check_if_bankrupt(self):
        while self.balance < 0:
            print(f'You need to sell or mortgage your property in order to avoid bankruptcy. Your balance is {self.balance}')
            user_choice = input('Press "m" to morgage, "s" to sell house, "a" to auction street, "b" to proclaim bankruptcy. Your action: ')
            if user_choice == 'b':
                self.declare_bankruptcy()
                break
            elif user_choice == 'm':
                while True:
                    user_choice = input('What street to mortgage (number)? (e for exit): ')
                    if user_choice == 'e':
                        break
                    elif user_choice.isnumeric() and int(user_choice) < 40:
                        board[int(user_choice)].mortgage(self)
                        break
                    else:
                        print("What's that?")
            elif user_choice == 's':
                while True:
                    user_choice = input('On what street to sell a house (number)? (e for exit): ')
                    if user_choice == 'e':
                        break
                    elif user_choice.isnumeric() and int(user_choice) < 40:
                        board[int(user_choice)].sell_house(self)
                        break
                    else:
                        print("Try aiming at the key better")
            elif user_choice == 'a':
               while True:
                    user_choice = input('What street to auction (number)? (e for exit): ')
                    if user_choice == 'e':
                        break
                    elif user_choice.isnumeric() and int(user_choice) < 40:
                        if board[int(user_choice)].owner != 'Bank' and board[int(user_choice)].owner == self:
                            try:
                                starting_price = int(input('At what starting price would you like to auction it?: '))
                            except:
                                print('Input an integer')
                                break
                            board[int(user_choice)].auction(self, starting_price)
                            break
                        else:
                            print('Moron')
                        break
                    else:
                        print("Come again")
            else:
                print(f'It would seem you are not only bad at playing, but equally so at typing, huh')
    def declare_bankruptcy(self):
        self.bankrupt = True
        print('\n-----------------------------------------------------------')
        print(f'{self.name} has declared BANKRUPTCY')
        print('-----------------------------------------------------------\n')
        for street in self.streets_owned:
            for house in range(street.houses):
                self.balance += street.house_cost/2
            street.owner = 'Bank'
            print(f'{street.street_name} has been acquired by the Bank')
            street.rent = street.rent_prices[0]
            street.houses = 0
            self.balance += street.price/2
        self.in_action = True
    def report_info(self):
        to_print = f'{self.name}, '
        if not self.jail:
            to_print += f'on the {board[self.position%40].street_name}'
        else:
            to_print += f'in jail; {3-self.jail} day left'
        print(to_print)
        to_print = f'Balance: ${self.balance}\n'
        if self.get_out_of_jail_free_cards:
            to_print += f', {self.get_out_of_jail_free_cards} Get Out Of Jail Free Cards'
        print(to_print)
        for street in self.streets_owned:
            to_print = f'{street.street_name}: ${street.price}'
            if street.houses > 0:
                to_print += f', {street.houses} houses'
            elif street.monopoly:
                to_print += f', {street.color_group} monopoly'
            elif street.mortgaged:
                to_print += f', Mortgaged; {round(street.buyback_price)} to buy back'
            print(to_print)
    def evaluate_offer(self, street, offer, player):
        while True:
            user_choice = self.evaluate_offer_choice(street, offer, player)
            if user_choice == 'Y':
                print(f'{self.name} has sold {street.street_name} to {player.name} for ${offer}')
                street.sell_all_houses()
                self.balance += offer
                for i, my_street in enumerate(self.streets_owned):
                    if my_street == street:
                        del self.streets_owned[i]
                if street.color_group == 'Railroad':
                    self.active_railroads -= 1
                if street.color_group == 'Utilities':
                    self.active_utilities -= 1

                player.balance -= offer
                street.owner = player
                self.streets_owned.remove(street)
                player.streets_owned.append(street)
                street.state_changed()
                break   
            elif user_choice == 'n':
                print(f'{self.name} has rejected offer by {player.name} of ${offer} for {street.street_name}')
                self.initiate_auction(street)
                break
            else:
                print('non existing input. Try again')
    def initiate_auction(self, street):
        pass
    def evaluate_offer_choice(self, street, offer, player):
        return input(f'{self.name}, do you wish to sell {street.street_name} for ${offer}? (Y/n): ')
    def evaluate_price(self, street, price):
        return input(f'{self.name}, how much are you betting?: ')
    def action(self):
        if not self.in_action:
            self.in_action = True
            draw_window()
            while True:
                user_choice = input("What do you want to do? (h for help): ")
                if user_choice == 'e':
                    break
                elif user_choice == 'i':
                    print('.......')
                    self.report_info()
                    print('.......')
                elif user_choice == 'oi':
                    print('.......')
                    for player in players:
                        if player != self:
                            player.report_info()
                            print('\n')
                    print('.......')
                elif user_choice == 'p':
                    street = board[self.position % 40]
                    street.purchase_street(self)
                elif user_choice == 'm':
                    while True:
                        user_choice = input('What street to mortgage (number)? (e for exit): ')
                        if user_choice == 'e':
                            break
                        elif user_choice.isnumeric() and int(user_choice) < 40:
                            board[int(user_choice)].mortgage(self)
                            break
                        else:
                            print("What's that?")
                elif user_choice == 's':
                    while True:
                        user_choice = input('On what street to sell a house (number)? (e for exit): ')
                        if user_choice == 'e':
                            break
                        elif user_choice.isnumeric() and int(user_choice) < 40:
                            board[int(user_choice)].sell_house(self)
                            break
                        else:
                            print("Try aiming at the key better")
                elif user_choice == 'a':
                    while True:
                        user_choice = input('What street to auction (number)? (e for exit): ')
                        if user_choice == 'e':
                            break
                        elif user_choice.isnumeric() and int(user_choice) < 40:
                            if board[int(user_choice)].owner != 'Bank' and board[int(user_choice)].owner == self:
                                try:
                                    starting_price = int(input('At what starting price would you like to auction it?: '))
                                except:
                                    print('Input an integer')
                                    break
                                board[int(user_choice)].auction(self, starting_price)
                                break
                            else:
                                print('Moron')
                            break
                        else:
                            print("Come again")
                elif user_choice == 'c':
                    while True:
                        user_choice = input('On what street to buy a house (number)? (e for exit): ')
                        if user_choice == 'e':
                            break
                        elif user_choice.isnumeric() and int(user_choice) < 40:
                            board[int(user_choice)].construct_house(self)
                            break
                        else:
                            print("Open those eyes nice and wide and try again")
                elif user_choice == 'b':
                    while True:
                        user_choice = input('What street to buy back (number)? (e for exit): ')
                        if user_choice == 'e':
                            break
                        elif user_choice.isnumeric() and int(user_choice) < 40:
                            board[int(user_choice)].unmortgage(self)
                            break
                        else:
                            print("Try wiping your glasses")
                elif user_choice == 't':
                    while True:
                        user_choice = input('What street to place an offer on (number)? (e for exit): ')
                        if user_choice == 'e':
                            break
                        elif user_choice.isnumeric() and int(user_choice) < 40:
                            offer = input('What is your offer (number)?: ')
                            if offer.isnumeric() and self.balance >= int(offer):
                                if board[int(user_choice)].owner != 'Bank' and board[int(user_choice)].owner != self:
                                    board[int(user_choice)].owner.evaluate_offer(board[int(user_choice)], int(offer), self)
                                else:
                                    print('Invalid option')
                                break
                            else:
                                print('Nope. Not having this here. Come back tomorrow.')
                                break
                        else:
                            print("Your fingers have gotten fat")
                            break
                elif user_choice == 'h':
                    help()
                else:
                    print('...')
        else:
            pass

class SimpleAI(Player):
    def jail_choice(self):
        return 'c' if self.get_out_of_jail_free_cards else 'd'
    def check_if_bankrupt(self):
        tried_to_auction = [] # keeping score of the streets the bot tried to auction so it doesn't repeat
        streets_owned = len(self.streets_owned)
        while self.balance < 0:
            did_something = False
            houses = 0
            def unwanted_street(street):
                if street.mortgaged == False:
                    did_something = True
                    street.mortgage(self)
                elif not street in tried_to_auction:
                    did_something = True
                    tried_to_auction.append(street)

                    starting_price = (street.price)/2 - street.buyback_price*0.7 -1  #AI decision
                    starting_price = max(starting_price, street.price/4)
                    street.auction(self, starting_price)
            for street in self.streets_owned:
                houses += street.houses
                if not street.monopoly and not street.houses:
                    unwanted_street(street)
                    if self.balance >= 0:
                        break
            if houses:
                for street in self.streets_owned:
                    did_something = True
                    street.sell_house(self)
                    if self.balance >= 0:
                        break
            
            if not did_something:
                if len(self.streets_owned):
                    unwanted_street(self.streets_owned[0])
                    if self.balance >= 0:
                        break
            if not did_something:
                self.declare_bankruptcy()
                break
#TODO: rewrite the bots in terms of estimating ev+ bid/ask diapason in a single function later and just call it for all decisions
    def initiate_auction(self, street):
        reasonable = street.price*2
        if street.house_cost != 'N/A':
            reasonable += street.houses*3*street.house_cost
        if street.mortgaged:
            reasonable += street.buyback_price
        street.auction(self, reasonable)
    def evaluate_offer_choice(self, street, offer, player):
        reasonable = street.price*2
        if street.house_cost != 'N/A':
            reasonable += street.houses*3*street.house_cost
        if street.mortgaged:
            reasonable += street.buyback_price
        return 'Y' if offer >= reasonable else 'n'

    def evaluate_price(self, street, price):
        reasonable = street.price * 0.85 +1
        if street.house_cost != 'N/A':
            reasonable += street.houses*3*street.house_cost/2
        if street.mortgaged:
            reasonable -= street.buyback_price * 0.7 # saying we'd rather pay a bank than another player

        streets_bought = 0 # max is 27
        for s in board:
            if s.owner != 'Bank':
                streets_bought += 1
        streets_bought_function = ((streets_bought-14)/13)**2 if (streets_bought-14)>0 else 0 # goes to 1 when all streets are bought
        reasonable += streets_bought_function * 1/3 * (self.balance-reasonable) * street.price/400 if self.balance>reasonable else 0# going from the idea that you should be willing to give third your balance for Broadwalk normally, ratio all others from it
        if street in self.interested:
            if street.house_cost != 'N/A':
                reasonable = self.balance * (1-0.1*(street.house_cost/50))
            else:
                reasonable = min(reasonable*2, self.balance*0.5)

        if price+5 < reasonable and price+5 <= self.balance:
            return price+5
        else:
            return 0
    def action(self):
        if not self.in_action:
            self.in_action = True
            draw_window()
            done_everything = False
            made_an_offer = []
            while not done_everything:
                done_everything = True
                need_money = False
                self.interested = []
                if board[self.position % 40].price != 'N/A':
                    if self.balance >= board[self.position % 40].price and board[self.position % 40].owner == 'Bank':   # p
                        board[self.position % 40].purchase_street(self)
                        if board[self.position % 40].owner != self:
                            need_money = True

                constructed = True                             # c
                while constructed:
                    constructed = False
                    for street in self.streets_owned:
                        if street.monopoly and street.houses < 5:
                            if self.balance >= street.house_cost:
                                street.construct_house(self)
                                constructed = True
                            else:
                                need_money = True

                for street in self.streets_owned:              # b
                    color_group = []
                    for s in board:
                        if s.color_group == street.color_group:
                            color_group.append(s)
                    monopoly = 1
                    potential_interest = street
                    for s in color_group:
                        if s.owner != self:
                            monopoly -= 1
                            potential_interest = s
                    if monopoly == 1:
                        for s in color_group:
                            if s.mortgaged == True:
                                if self.balance >= s.buyback_price:
                                    s.unmortgage(self)
                                else:
                                    need_money = True
                    elif monopoly == 0: # meaning there is only one street the player needs for a monopoly
                        self.interested.append(potential_interest)

                if not need_money:
                    for s in self.interested:
                        if self.balance >= s.price * 1.5 and s.owner != 'Bank' and not s in made_an_offer:
                            s.owner.evaluate_offer(s, s.price*1.5, self)
                            made_an_offer.append(s)
                else:                         # m
                    for street in self.streets_owned:
                        color_group = []
                        for s in board:
                            if s.color_group == street.color_group:
                                color_group.append(street)
                        monopoly_possible = True
                        for s in color_group:
                            if s.owner != street.owner and s.owner != 'Bank' and s.color_group != 'Railroad' and s.color_group != 'Utilities':
                                monopoly_possible = False
                        for s in color_group:
                            if not s.mortgaged and not monopoly_possible:
                                s.mortgage(self)
                                done_everything = False
        else:
            pass

class Street:
    def __init__(self, street_name, color_group, price, house_cost, rent_prices):
        self.street_name = street_name
        self.color_group = color_group
        self.price = price
        self.house_cost = house_cost
        self.rent_prices = rent_prices

        self.rent = rent_prices[0]
        self.houses = 0
        self.owner = "Bank"
        self.mortgaged = False
        self.monopoly = False
        self.buyback_price = round(1.1*(price/2)) if type(price)==int else 'N/A'
    def mortgage(self, player):
        if self.price != 'N/A':
            if self.mortgaged == False:
                if self.owner == player:
                    houses = 0
                    for s in board:
                        if s.color_group == self.color_group:
                            houses += s.houses
                    if not houses:
                        player.balance += self.price/2
                        self.mortgaged = True
                        print(f'{player.name} has mortgaged {self.street_name} for ${self.price/2}')
                        self.state_changed()
                    else:
                        print(f"First, dispose of all the houses of the color sector. On this street you have {self.houses}")
                else:
                    print("You don't even own the street, bozo")
            else:
                print('The street is already mortgaged')
        else:
            print("Can't morgage that, you dumb-dumb")
    def unmortgage(self, player):
        if self.mortgaged == True:
            if self.owner == player:
                price = round(1.1 * self.price/2)
                if player.balance >= price:
                    player.balance -= price
                    self.mortgaged = False
                    self.state_changed()
                    print(f'{player.name} bought back {self.street_name} for ${price}')
                else:
                    print("Kindly leave the bank's premises, you are too poor for us")
            else:
                print("You don't even own the street, bozo")
        else:
            print("The street isn't even mortgaged.")
    def auction(self, seller, starting_price):
        if seller == self.owner:
            print(f'{seller.name} is auctioning {self.street_name} at ${starting_price}')
            ended = False
            standing_offer = (starting_price-5, seller) # format: (amount, player)
            while not ended:
                ended = True
                for player in players:
                    if player != seller and player != standing_offer[1]:
                        if player.bot != True:
                            user_action = input(f'{player.name}, are you willing to bet? (Y/n): ')
                        else:
                            user_action = 'Y'
                        if user_action == 'Y':
                            offer = player.evaluate_price(self, standing_offer[0]) # for test purposes
                            try:
                                offer = int(offer)
                                if player.balance >= offer:
                                    if offer >= standing_offer[0] + 5:
                                        print(f'New standing offer of ${offer} on {self.street_name} by {player.name}')
                                        standing_offer = (offer, player)
                                        ended = False
                                        break
                                    elif offer > standing_offer[0]:
                                        print(f"{player.name} tried to make an offer, but doesn't know the minimum step is 5")
                                else:
                                    print(f"{player.name} tried to make an offer, but doesn't have enough money")
                            except:
                                print('not an integer')
                                break
                        else:
                            print(f'{player.name} passes')
            if standing_offer[0] >= starting_price:
                self.sell_all_houses()
                print(f'{seller.name} has auctioned {self.street_name} off to {standing_offer[1].name} at ${standing_offer[0]}')
                seller.balance += standing_offer[0]
                standing_offer[1].balance -= standing_offer[0]
                standing_offer[1].streets_owned.append(self)
                seller.streets_owned.remove(self)
                self.owner = standing_offer[1]
                self.state_changed()
            else:
                print(f'Nobody wanted {self.street_name} at the price of ${starting_price}')
        else:
            print(f"{seller.name} tried to auction off {self.owner.name}'s street")
    def state_changed(self):
        if self.color_group == 'Railroad':
            self.owner.active_railroads = 0
            for street in self.owner.streets_owned:
                if street.color_group == 'Railroad' and not street.mortgaged:
                    self.owner.active_railroads += 1
            for street in self.owner.streets_owned:
                if street.color_group == 'Railroad' and not street.mortgaged:
                    street.rent = street.rent_prices[self.owner.active_railroads-1]
        elif self.color_group == 'Utilities':
            self.owner.active_utilities = 0
            for street in self.owner.streets_owned:
                if street.color_group == 'Utilities' and not street.mortgaged:
                    self.owner.active_utilities += 1
            for street in self.owner.streets_owned:
                if street.color_group == 'Utilities' and not street.mortgaged:
                    street.rent = street.rent_prices[self.owner.active_utilities]
        elif self.house_cost != 'N/A':
            color_group = []
            for s in board:
                if s.color_group == self.color_group:
                    color_group.append(s)
            monopoly = True
            for s in color_group:
                if s.color_group == self.color_group and s.owner != self.owner:
                    monopoly = False
            if monopoly:
                to_print = False
                for s in color_group:
                    if not s.monopoly:
                        s.monopoly = True
                        to_print = True
                    if not s.houses:
                        s.rent = s.rent_prices[0] * 2
                if to_print:
                    print(f'{player.name} now has an active {self.color_group} monopoly')
            else:
                for s in color_group:
                    s.monopoly = False
                    s.rent = s.rent_prices[0]
        draw_window()
    def sell_all_houses(self):
        if self.houses:
            house_counter = 0
            color_group = []
            for s in board:
                if s.color_group == self.color_group:
                    color_group.append(s)
                    house_counter += s.houses
            print(f'{s.owner.name} has sold {house_counter} houses on {self.street_name} for ${house_counter * self.house_cost/2}')

            sold_any = True
            while sold_any:
                sold_any = False

                houses_on_color_group = []
                for s in color_group:
                    houses_on_color_group.append(s.houses)
                for s in color_group: 
                    if s.houses == max(houses_on_color_group):
                        s.sell_house(s.owner)
    def purchase_street(self, player):
        if self.owner == 'Bank' and self.price != 'N/A':
            if player.balance >= self.price:
                player.balance -= self.price
                player.streets_owned.append(self)
                self.owner = player
                print(f'{player.name} has purchased {self.street_name} for ${self.price}')
                self.state_changed()
            else:
                print('Too poor.')
        else:
            print('Cannot purchase the street')
    def construct_house(self, player):
        if player == self.owner:
            if self.monopoly == True:
                if player.balance >= self.house_cost:
                    houses_on_color_group = []
                    for street in board:
                        if street.color_group == self.color_group:
                            houses_on_color_group.append(street.houses)
                    sequential_construction = True if min(houses_on_color_group) == self.houses else False
                    if sequential_construction == True:
                        if self.houses < 5:
                            player.balance -= self.house_cost
                            self.houses += 1
                            self.rent = self.rent_prices[self.houses]
                            if self.houses == 5:
                                print(f'{player.name} has build a hotel on {self.street_name}! Rent is now ${self.rent}')
                            else:
                                print(f'{player.name} has built a house on {self.street_name}. Rent is now ${self.rent}')
                            draw_window()
                        else:
                            print('You have already build the hotel')
                    else:
                        print('You have to build houses sequentially. Check that all of your streets of\nthis color complex have the same number of houses on them')
                else:
                    print('Get out of here, you have no money')
            else:
                print('How do you expect to build houses not owning a monopoly?!')
        else:
            print('Dumbass')
    def sell_house(self, player):
        if player == self.owner:
            if self.houses:
                houses_on_color_group = []
                for street in board:
                    if street.color_group == self.color_group:
                        houses_on_color_group.append(street.houses)
                sequential_destruction = True if max(houses_on_color_group) == self.houses else False
                if sequential_destruction == True:
                    self.houses -= 1
                    self.rent = self.rent_prices[self.houses]
                    player.balance += self.house_cost/2
                    print(f'{player.name} has sold a house on {self.street_name}. Rent is now ${self.rent}')
                    draw_window()
                else:
                    if not player.bot:
                        print(f'First sell houses from other streets of the {self.color_group} Color')
            else:
                if not player.bot:
                    print('No houses on the street')
        else:
            if not self.bot:
                print('Good try, but police now has its eyes on you')

def initialize_streets_and_board():
    """
    Creates all the needed street objects and adds them in the correct order to the board variable.
    The board represents the order of streets in the original Monopoly game board.
    :return: board: a list of streets.
    """
    go = Street("Go", "N/A", "N/A", "N/A", "N/A")
    med_ave = Street("Mediterranean Avenue", "Brown", 60, 50, {0: 2,
                                                                        1: 10,
                                                                        2: 30,
                                                                        3: 90,
                                                                        4: 160,
                                                                        5: 250})
    comm_chest = Street("Community Chest", "N/A", "N/A", "N/A", "N/A")
    baltic_ave = Street("Baltic Avenue", "Brown", 60, 50, {0: 4,
                                                                    1: 20,
                                                                    2: 60,
                                                                    3: 180,
                                                                    4: 320,
                                                                    5: 450})
    income_tax = Street("Income Tax", "N/A", "N/A", "N/A", "N/A")
    reading_rr = Street("Reading Railroad", "Railroad", 200, "N/A", {0: 25,
                                                                     1: 50,
                                                                     2: 100,
                                                                     3: 200})
    oriental_ave = Street("Oriental Avenue", "Light Blue", 100, 50, {0: 6,
                                                                            1: 30,
                                                                            2: 90,
                                                                            3: 270,
                                                                            4: 400,
                                                                            5: 550})
    chance = Street("Chance", "N/A", "N/A", "N/A", "N/A")
    vermont_ave = Street("Vermont Avenue", "Light Blue", 100, 50, {0: 6,
                                                                            1: 30,
                                                                            2: 90,
                                                                            3: 270,
                                                                            4: 400,
                                                                            5: 550})
    conn_ave = Street("Connecticut Avenue", "Light Blue", 120, 50, {0: 8,
                                                                            1: 40,
                                                                            2: 100,
                                                                            3: 300,
                                                                            4: 450,
                                                                            5: 600})
    # new row
    jail = Street("Jail/Visiting Jail", "N/A", "N/A", "N/A", "N/A")
    st_charles_place = Street("St. Charles Place", "Pink", 140, 100, {0: 10,
                                                                                1: 50,
                                                                                2: 150,
                                                                                3: 450,
                                                                                4: 625,
                                                                                5: 750})
    electric_company = Street("Electric Company", "Utilities", 150, "N/A", {0: 4, 1: 4, 2: 10})
    states_ave = Street("States Avenue", "Pink", 140, 100, {0: 10,
                                                                    1: 50,
                                                                    2: 150,
                                                                    3: 450,
                                                                    4: 625,
                                                                    5: 750})
    virginia_ave = Street("Virginia Avenue", "Pink", 160, 100, {0: 12,
                                                                        1: 60,
                                                                        2: 180,
                                                                        3: 500,
                                                                        4: 700,
                                                                        5: 900})
    penn_rr = Street("Pennsylvania Railroad", "Railroad", 200, "N/A", {0: 25,
                                                                       1: 50,
                                                                       2: 100,
                                                                       3: 200})
    st_james_place = Street("St. James Place", "Orange", 180, 100, {0: 14,
                                                                            1: 70,
                                                                            2: 200,
                                                                            3: 550,
                                                                            4: 750,
                                                                            5: 950})
    # comm chest
    ten_ave = Street("Tennessee Avenue", "Orange", 180, 100, {0: 14,
                                                                        1: 70,
                                                                        2: 200,
                                                                        3: 550,
                                                                        4: 750,
                                                                        5: 950})
    ny_ave = Street("New York Avenue", "Orange", 200, 100, {0: 16,
                                                                    1: 80,
                                                                    2: 220,
                                                                    3: 600,
                                                                    4: 800,
                                                                    5: 1000})
    free_parking = Street("Free Parking", "N/A", "N/A", "N/A", "N/A")
    # rotate
    kentucky_ave = Street("Kentucky Avenue", "Red", 220, 150, {0: 18,
                                                                        1: 90,
                                                                        2: 250,
                                                                        3: 700,
                                                                        4: 875,
                                                                        5: 1050})
    # chance
    indiana_ave = Street("Indiana Avenue", "Red", 220, 150, {0: 18,
                                                                    1: 90,
                                                                    2: 250,
                                                                    3: 700,
                                                                    4: 875,
                                                                    5: 1050})
    illinois_ave = Street("Illinois Avenue", "Red", 240, 150, {0: 20,
                                                                        1: 100,
                                                                        2: 300,
                                                                        3: 750,
                                                                        4: 925,
                                                                        5: 1100})
    bno_rr = Street("B. & O. Railroad", "Railroad", 200, "N/A", {0: 25,
                                                                  1: 50,
                                                                  2: 100,
                                                                  3: 200})
    atlantic_ave = Street("Atlantic Avenue", "Yellow", 260, 150, {0: 22,
                                                                            1: 110,
                                                                            2: 330,
                                                                            3: 800,
                                                                            4: 975,
                                                                            5: 1150})
    ventnor_ave = Street("Ventnor Avenue", "Yellow", 260, 150, {0: 22,
                                                                        1: 110,
                                                                        2: 330,
                                                                        3: 800,
                                                                        4: 975,
                                                                        5: 1150})
    water_works = Street("Water Works", "Utilities", 150, 'N/A', {0: 4, 1: 4, 2: 10})
    marvin_gardens = Street("Marvin Gardens", "Yellow", 280, 150, {0: 24,
                                                                            1: 120,
                                                                            2: 360,
                                                                            3: 850,
                                                                            4: 1025,
                                                                            5: 1200})
    # rotateh
    go_to_jail = Street("Go to Jail", "N/A", "N/A", "N/A", "N/A")
    pacific_ave = Street("Pacific Avenue", "Green", 300, 200, {0: 26,
                                                                        1: 130,
                                                                        2: 390,
                                                                        3: 900,
                                                                        4: 1100,
                                                                        5: 1275})
    nc_ave = Street("North Carolina Avenue", "Green", 300, 200, {0: 26,
                                                                        1: 130,
                                                                        2: 390,
                                                                        3: 900,
                                                                        4: 1100,
                                                                        5: 1275})
    # comm chest
    penn_ave = Street("Pennsylvania Avenue", "Green", 320, 200, {0: 28,
                                                                        1: 150,
                                                                        2: 450,
                                                                        3: 1000,
                                                                        4: 1200,
                                                                        5: 1400})
    short_line_rr = Street("Short Line", "Railroad", 200, "N/A", {0: 25,
                                                                  1: 50,
                                                                  2: 100,
                                                                  3: 200})
    # chance
    park_place = Street("Park Place", "Blue", 350, 200, {0: 35,
                                                                1: 175,
                                                                2: 500,
                                                                3: 1100,
                                                                4: 1300,
                                                                5: 1500})
    luxury_tax = Street("Luxury Tax", "N/A", "N/A", "N/A", "N/A")
    boardwalk = Street("Boardwalk", "Blue", 400, 200, {0: 50,
                                                                1: 200,
                                                                2: 600,
                                                                3: 1400,
                                                                4: 1700,
                                                                5: 2000})
    # end
    board = [
        go,
        med_ave,
        comm_chest,
        baltic_ave,
        income_tax,
        reading_rr,
        oriental_ave,
        chance,
        vermont_ave,
        conn_ave,
        jail,
        st_charles_place,
        electric_company,
        states_ave,
        virginia_ave,
        penn_rr,
        st_james_place,
        comm_chest,
        ten_ave,
        ny_ave,
        free_parking,
        kentucky_ave,
        chance,
        indiana_ave,
        illinois_ave,
        bno_rr,
        atlantic_ave,
        ventnor_ave,
        water_works,
        marvin_gardens,
        go_to_jail,
        pacific_ave,
        nc_ave,
        comm_chest,
        penn_ave,
        short_line_rr,
        chance,
        park_place,
        luxury_tax,
        boardwalk
    ]

    return board

def draw_window():
    if GUI == True:
        win.blit(background, (0,0))
        #TODO: add update of all the resources on the board here
        for player in players:
            def move_player():
                player.position = player.position%40
                x, y = 0, 0
                if 0 <= player.position < 10:
                    x = 55
                    y = 685 - player.position * 63
                elif 10 <= player.position < 20:
                    x = 55 + (player.position-10) * 63
                    y = 55
                elif 20 <= player.position < 30:
                    x = 685
                    y = 55 + (player.position-20) * 63
                elif 30 <= player.position < 40:
                    x = 685 - (player.position-30) * 63
                    y = 685
                if player.position == 10 and player.jail == 0: #meaning we're visiting
                    x = 15
                    y = 15

                x += player.position_offset
                y -= player.position_offset/2
                width, height = player.img.get_size()
                x -= width/2
                y -= height/2

                win.blit(player.img, (x, y))
            def draw_street_properties():
                hs_width, hs_height = HOUSE_IMG.get_size()
                hl_width, hl_height = HOTEL_IMG.get_size()
                for street in player.streets_owned:
                    if street.houses > 0:
                        x, y = 0, 0
                        if 0 <= board.index(street) < 10:
                            x = 25
                            y = 685 - board.index(street) * 63
                        elif 10 <= board.index(street) < 20:
                            x = 55 + (board.index(street)-10) * 63
                            y = 25
                        elif 20 <= board.index(street) < 30:
                            x = 715
                            y = 55 + (board.index(street)-20) * 63
                        elif 30 <= board.index(street) < 40:
                            x = 685 - (board.index(street)-30) * 63
                            y = 715

                        shift = 15
                        if street.houses == 5:
                            win.blit(HOTEL_IMG, (x - hl_width/2, y - hl_height/2))
                        else:
                            for i in range(street.houses):
                                house = i+1
                                if house == 1:
                                    win.blit(HOUSE_IMG, (x-shift - hs_width/2, y-shift/2 - hs_height/2))
                                if house == 2:
                                    win.blit(HOUSE_IMG, (x-shift/2 - hs_width/2, y+shift/2 - hs_height/2))
                                if house == 3:
                                    win.blit(HOUSE_IMG, (x - hs_width/2, y-shift/2 - hs_height/2))
                                if house == 4:
                                    win.blit(HOUSE_IMG, (x+shift/2 - hs_width/2, y+shift/2 - hs_height/2))

                    x, y = 0, 0
                    if 0 <= board.index(street) < 10:
                        x = 100
                        y = 660 - board.index(street) * 60
                    elif 10 <= board.index(street) < 20:
                        x = 55 + (board.index(street)-10) * 60
                        y = 100
                    elif 20 <= board.index(street) < 30:
                        x = 612
                        y = 55 + (board.index(street)-20) * 60
                    elif 30 <= board.index(street) < 40:
                        x = 660 - (board.index(street)-30) * 60
                        y = 612

                    rect = p.Rect(x, y, 30, 30)
                    p.draw.rect(win, player.color, rect)
                    if street.mortgaged == True:
                        semitransparent_rect = p.Rect(x, y, 25, 25)
                        p.draw.rect(win, p.Color(255, 0, 0, 128), semitransparent_rect) # Draws see-through red square on top # also it's not see through for some reason, so I just made it a bit smaller
            def draw_stats():
                player.balance = round(player.balance)
                stat_font = p.font.SysFont('comicsans', 15)
                name_text = stat_font.render(f'{player.name}', True, player.color)
                text = f':  ${player.balance}'
                if player.get_out_of_jail_free_cards > 0:
                    text += f', {player.get_out_of_jail_free_cards} Jail Free Card'
                    if player.get_out_of_jail_free_cards > 1:
                        text += 's'
                balance_text = stat_font.render(text, True, black)

                name_rect = name_text.get_rect()
                balance_rect = balance_text.get_rect()

                x, y = 280, 135
                position = player.position_offset/6 + 1
                name_rect.topleft = (x, y + position*15)
                balance_rect.topleft = (name_rect.right + 4, y + position*15)

                win.blit(name_text, name_rect)
                win.blit(balance_text, balance_rect)
            move_player()
            draw_street_properties()
            draw_stats()
        p.display.update()
    else:
        pass

def help() -> None:
    """
    Displays possible options for players.
    :return: None
    """
    print("Instruction.......................................Command")
    print("End the turn........................................e")
    print("View your info......................................i")
    print("View info of others................................oi")
    print("Purchase the street.................................p")
    print("Mortgage property...................................m")
    print("Sell house..........................................s")
    print("Auction a street off................................a")
    print("Construct house.....................................c")
    print("Buy back a mortgaged street.........................b")
    print("Trade...............................................t")

board = initialize_streets_and_board()

player1 = SimpleAI("Alice", starting_capital, PURPLE, purple, -6)
player2 = SimpleAI("Bob", starting_capital, YELLOW, yellow, 0)
player3 = SimpleAI("Clyde", starting_capital, GREEN, green, 6)
player4 = SimpleAI("Dodo the Bird", starting_capital, BLUE, blue, 12)
players = [player1, player2, player3, player4]

if __name__ == "__main__":
    print("The Game is Started\n")
    help()
    while len(players)>1:
        for player in players:
            print('\n')
            player.rollTheDice()
            for player in players:
                if player.bankrupt:
                    players.remove(player)

    print('\n\n\n\n=========================================================\n')
    print(f'The GAME is OVER! {players[0].name} has WON!')
    print('\n=========================================================\n\n')

end_screen = input('press Enter to exit  .  .  .')
