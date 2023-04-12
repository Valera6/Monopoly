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
    def mortgage(self, player):
        if self.price != 'N/A':
            if self.mortgaged == False:
                if self.owner == player:
                    if self.houses == 0:
                        player.balance += self.price/2
                        self.mortgaged = True
                        draw_window()
                        print(f'{player.name} has mortgaged {self.street_name} for ${self.price/2}')
                        for street in board:
                            if street.color_group == self.color_group:
                                street.monopoly = False
                    else:
                        print("First, dispose of all the houses of the color sector. On this street you have {self.houses}")
                else:
                    print("You don't even own the street, bozo")
            else:
                print('The street is already mortgaged')
        else:
            print("Can't morgage that, you dumb-dumb")
    def unmortgage(self, player):
        if self.mortgaged == True:
            if self.owner == player:
                price = 1.1 * self.price/2
                if player.balance >= price:
                    player.balance -= price
                    self.mortgaged = False
                    draw_window()
                    print(f'{player.name} bought back {self.street_name} for ${price}')
                else:
                    print("Kindly leave the bank's premises, you are too poor for us")
            else:
                print("You don't even own the street, bozo")
        else:
            print("The street isn't even mortgaged.")
    def auction(self, starting_price):
        houses_sold = True
        for street in board:
            if street.color_group == self.color_group:
                if street.houses > 0:
                    houses_sold = False
        if houses_sold:
            ended = False
            standing_offer = (0, self.owner) # format: (amount, player)
            while not ended:
                ended = True
                for player in players:
                    if player != self.owner and player != standing_offer[1]:
                        user_action = input(f'{player.name}, are you willing to bet? (Y/n): ')
                        if user_action == 'Y':
                            try:
                                offer = int(input(f'{player.name}, how much are you betting?: '))
                            except:
                                print('not an integer')
                                break
                            if offer > standing_offer[0] and offer >= starting_price and player.balance >= offer:
                                print(f'New standing offer of ${offer} on {self.street_name} by {player.name}')
                                standing_offer = (offer, player)
                                ended = False
                                break
                        else:
                            print(f'{player.name} passes')
            if standing_offer[0] >= starting_price:
                print(f'{self.owner.name} has auctioned {self.street_name} off to {standing_offer[1].name} at ${standing_offer[0]}')
                standing_offer[1].balance -= standing_offer[0]
                standing_offer[1].streets_owned.append(self)
                self.owner.balance += standing_offer[0]
                draw_window()
                for i, my_street in enumerate(self.owner.streets_owned):
                    if my_street == self:
                        del self.owner.streets_owned[i]
                self.owner = standing_offer[1]
                if self.monopoly:
                    for street in board:
                        if street.color_group == self.color_group:
                            street.monopoly = False
            else:
                print(f'Nobody wanted {self.street_name} at the price of ${starting_price}')
        else:
            print('first, sell all the houses on the color complex')
    def purchase_street(self, player):
        if self.owner == 'Bank' and self.price != 'N/A':
            if player.balance >= self.price:
                player.balance -= self.price
                player.streets_owned.append(self)
                self.owner = player
                print(f'{player.name} has purchased {self.street_name} for ${self.price}')
                draw_window()
                if self.color_group == 'Railroad':
                    player.railroads_owned += 1
                    for street in player.streets_owned:
                        if street.color_group == 'Railroad':
                            street.rent = street.rent_prices[player.railroads_owned-1]
                if self.color_group == 'Utilities':
                    if player.utilities_owned == 2:
                        self.rent = 10
                # check if it makes a monopoly
                elif self.house_cost != 'N/A':
                    color_group = []
                    for street in board:
                        if street.color_group == self.color_group:
                            color_group.append(street)
                    monopoly = True
                    for street in color_group:
                        if street.owner != self.owner:
                            monopoly = False
                    if monopoly == True:
                        for street in color_group:
                            street.monopoly = True
                            street.rent = street.rent_prices[0] * 2
                        print(f'{player.name} has acquired a {self.color_group} monopoly')
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
                    print(f'First sell houses from other streets of the {self.color_group} Color')
            else:
                print('No houses on the street')
        else:
            print('Good try, but police now has its eyes on you')
