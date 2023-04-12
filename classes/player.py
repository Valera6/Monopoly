import random
GUI = False
board = [0]

class Player:
    def __init__(self, name, starting_capital, img, color, position_offset):
        self.name = name
        self.balance = starting_capital

        self.color = color #needed for GUI
        self.img = img #needed for GUI
        self.position_offset = position_offset #needed for GUI

        self.position = 0
        self.streets_owned = []
        self.railroads_owned = 0
        self.utilities_owned = 0
        self.bankrupt = False
        self.jail = 0   # if above 0, signifies the number of the day in jail: 1 to 3
        
        self.rolled = 0 # for Utilities streets
        self.pay_double = False
        self.get_out_of_jail_free_cards = 0
        self.in_action = False # stupid fix of rerouting to self.action()

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
                user_input = input(f'{self.name}, you can throw dice ("d"), pay $50 ("p"), or use Get Out of Jail Free Card ("c"): ')
                if user_input == 'd':
                    dice1 = random.randint(1, 6)
                    dice2 = random.randint(1, 6)
                    if dice1==dice2:
                        throw = dice1+dice2
                        print(f"{self.name} threw a double {dice1} and is out of jail")
                        self.position += throw
                        self.rolled = throw
                        self.check_position()
                        break
                    else:
                        if self.jail < 3:
                            print(f'{self.name} threw {dice1} and {dice2}, and is remaining in jail for {3-self.jail} more days')
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
                print(f'{self.name} landed on Luxury Tax and has been fined $75')
                self.balance -= 75
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
                user_action = input(f'Do you want to buy for ${board_property.price}? (Y/n): ')
                if user_action == 'Y':
                    board_property.purchase_street(self)
                    self.action()
                elif user_action == 'n':
                    self.action()
                else:
                    print('Wrong answer.')
                    self.action()
            elif board_property.owner != 'Bank' and board_property.owner.name != self.name and board_property.mortgaged==False:
                if board_property.color_group != 'Utilities':
                    print(f'{self.name} landed on {board_property.street_name} and was charged ${board_property.rent} by {board_property.owner.name}')
                    self.pay_rent(board_property)
                    self.action()
                else:
                    print(f'{self.name} landed on {board_property.street_name} and was charged ${board_property.rent*self.rolled} by {board_property.owner.name}')
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
                elif len(street.houses):
                    for house in street.houses:
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
                    for house in street.houses:
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
                print(f'{self.name} has paid {street.owner.name} all he had left - ${rent_amt+self.balance}')
                self.balance = 0
    def check_if_bankrupt(self):
        while self.balance < 0:
            print(f'You need to sell or mortgage your property in order to avoid bankruptcy. Your balance is {self.balance}')
            user_choice = input('Press "m" to morgage, "s" to sell house, "a" to auction street, "b" to proclaim bankruptcy. Your action: ')
            if user_choice == 'b':
                self.bankrupt = True
                print('\n-----------------------------------------------------------')
                print(f'{self.name} has declared BANKRUPTCY')
                print('\n-----------------------------------------------------------')
                if len(self.streets_owned):
                    for street in range(self.streets_owned):
                        if len(street.houses):
                            for house in range(street.houses):
                                balance += street.house_cost/2
                        street.owner = 'Bank'
                        balance += street.price/2
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
                            board[int(user_choice)].auction(starting_price)
                            break
                        else:
                            print('Moron')
                        break
                    else:
                        print("Come again")
            else:
                print(f'It would seem you are not only bad at playing, but equally so at typing, huh')         
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
                to_print += f', Mortgaged; {round(1.1*street.price/2)} to buy back'
            print(to_print)
    def evaluate_offer(self, street, offer, player):
        while True:
            user_choice = input(f'{self.name}, do you wish to sell {street.street_name} for ${offer}? (Y/n): ')
            if user_choice == 'Y':
                print(f'{self.name} has sold {street.street_name} to {player.name} for ${offer}')
                self.balance += offer
                for i, my_street in enumerate(self.streets_owned):
                    if my_street == street:
                        del self.streets_owned[i]
                player.balance -= offer
                street.owner = player
                player.streets_owned.append(street)
                if street.monopoly:
                    for street in board:
                        if street.color_group == self.color_group:
                            street.monopoly = False
                house_counter = 0
                for some_street in board:
                    if some_street.color_group == street.color_group:
                        for house in range(some_street.houses):
                            self.balance += street.house_cost/2
                        some_street.houses = 0
                if house_counter:
                    print(f'{self.name} also sold {house_counter} houses for {house_counter * street.house_cost/2} to proceed with the deal')
                break   
            elif user_choice == 'n':
                print(f'{self.name} has rejected offer by {player.name} of ${offer} for {street.street_name}')
                break
            else:
                print('non existing input. Try again')
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
                                board[int(user_choice)].auction(starting_price)
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
                            print("Your fingers have gotten fats")
                            break
                elif user_choice == 'h':
                    help()
                else:
                    print('...')
        else:
            pass
