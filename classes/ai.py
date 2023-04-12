from .Player import Player
class SimpleAI(Player):
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