import requests
import time
import os

# ASCII corner and line symbols:
# https://textkool.com/en/symbols/corner-symbols
# https://textkool.com/en/symbols/line-symbols

# ASCII card symbols:
# https://textkool.com/en/symbols/card-symbols

# I wanted to practice using APIs, so the game uses this deck of cards API:
# https://www.deckofcardsapi.com/

class Deck:
    
    def __init__(self, deck_id):
        self.deck_id = deck_id
        self.base_url = f"https://www.deckofcardsapi.com/api/deck/{self.deck_id}/"
        
    def _get(self, action):
        """ Returns the requested stuff from the API. 'action' can be:
                draw = draw a card from the deck (without replacement)
                return = return all cards to the deck (might DELETE THIS later) """
        res = requests.get(f"{self.base_url}/{action}/")
        if res.ok:
            return res.json()
        else:
            print(f"There was an error {action}ing the card(s).")
    
    def evaluate_card(self, card):
        """ Takes in an API card and returns the int value of that card.
                2-9 will return that value.
                JACK, QUEEN, and KING will return 10.
                ACE will return 11. """
        card_id = card['cards'][0]['value']
        if card_id.lower() in {'jack','queen','king'}:
            card_val = 10
        elif card_id.lower() == 'ace':
            card_val = 11
        elif int(card_id) <= 10:
            card_val = int(card_id)
#         print(f"Card: {card_id} has value {card_val}.")
        return card_val
    
    def card_suit(self, card):
        """ Takes in an API card and returns the suit icon of that card. """
        card_suit = card['cards'][0]['suit'].lower()
        if card_suit == "clubs":
            return '♣'
        
        elif card_suit == "diamonds":
            return '♦'
        
        elif card_suit == "spades":
            return '♠'
        
        elif card_suit == "hearts":
            return '♥'



class Player:
    hand = []
    formatted_hand = []
    hand_val = 0
    has_blackjack = False
    insurance = 0
    
    def __init__(self, deck, money, bet):
        self.deck = deck
        self.money = money
        self.original_money = money
        self.bet = bet
        self.has_blackjack = False
#         reset the class attributes
        self.hand = []
        self.hand_val = 0
#         MAYBE LATER: Add a bool for card counting.

    def append_formatted_hand(self, card):
        """ Accepts an API card object and appends the formatted_hand attribute
            with the card as a formatted object."""
        suit = self.deck.card_suit(card)
    
        if card['cards'][0]['value'].lower() == 'jack':
            self.formatted_hand.append(['╭─────╮',f'│  J  │', '│     │', f'│  {suit}  │','╰─────╯'])
        elif card['cards'][0]['value'].lower() == 'queen':
            self.formatted_hand.append(['╭─────╮',f'│  Q  │', '│     │', f'│  {suit}  │','╰─────╯'])
        elif card['cards'][0]['value'].lower() == 'king':
            self.formatted_hand.append(['╭─────╮',f'│  K  │', '│     │', f'│  {suit}  │','╰─────╯'])
        elif card['cards'][0]['value'].lower() == 'ace':
            self.formatted_hand.append(['╭─────╮',f'│  A  │', '│     │', f'│  {suit}  │','╰─────╯'])
        elif card['cards'][0]['value'] == '10':
            self.formatted_hand.append(['╭─────╮',f'│ 1 0 │', '│     │', f'│  {suit}  │','╰─────╯'])
        else:
            num = card['cards'][0]['value']
            self.formatted_hand.append(['╭─────╮',f'│  {num}  │', '│     │', f'│  {suit}  │','╰─────╯'])
    
    def print_hand(self, insurance):
        """ Prints the player's hand, 
            including if they have a blackjack, 
            their current bet,
            and their current wallet total. """
        
        print(f"\n\n----- MY HAND -----")
        for item in self.formatted_hand:
            print(item[0], end=' ')
        print("")
        for item in self.formatted_hand:
            print(item[1], end=' ')
        print("")
        for item in self.formatted_hand:
            print(item[2], end=' ')
        print("")
        for item in self.formatted_hand:
            print(item[3], end=' ')
        print("")
        for item in self.formatted_hand:
            print(item[4], end=' ')
                
        if self.has_blackjack:
            print("\n\tBLACKJACK!")
        print(f"\nMY BET: ${self.bet:.2f}")
        if insurance:
            print(f"\nINSURANCE: ${self.insurance:.2f}")
        print(f"MY WALLET: ${self.money:.2f}")

    
    def take_turn(self, dealer):
        """ Allows the player to choose to hit or stand.
                if hit, calls self.hit()
                if stand, calls dealer.take_turn() """
        # os.system('cls')
        # dealer.print_hand(False)
        # self.print_hand()
        choice = input("\nWhat would you like to do? (H)IT / (S)TAND / (D)OUBLE DOWN: ").lower().strip()
        while choice not in {'hit', 'stand','double down','h','s','d'}:
            choice = input("That didn't work." +
                "\nWhat would you like to do? (H)IT / (S)TAND / (D)OUBLE DOWN: ").lower().strip()
        while (choice == 'd' or choice == 'double down') and self.bet * 2 > self.money:
            choice = input(f"You don't have enough money to double down. You only have ${self.money:.2f}" +
                "\nWhat would you like to do? (H)IT / (S)TAND / (D)OUBLE DOWN: ").lower().strip()
        if choice == 'hit' or choice == 'h':
            self.hit(dealer)
        elif choice == 'stand' or choice == 's':
            dealer.take_turn(insurance=False)
        elif choice == 'double down' or choice == 'd':
            self.bet *= 2
            self.hit(dealer, doubledown=True)
        
#         MAYBE LATER: If the two cards on the first move are the same, option to SPLIT.
#         MAYBE LATER: Option to DOUBLE DOWN (2x bet and only draw 1 card).
    
    
    def hit(self, dealer, **doubledown):
        """ Draws a new API card and puts it in the player's hand.
            Evaluates the player's hand's value after the draw to see if they lost """
#         print("You have decided to HIT.")
        card = self.deck._get('draw')
        self.hand.append(card)
        self.append_formatted_hand(card)
        os.system('cls')
        dealer.print_hand(False)
        self.print_hand(insurance=False)
        self.hand_val += self.deck.evaluate_card(card)

        ace_count = 0
        for card in self.hand:
            if card['cards'][0]['value'].lower() == 'ace':
                ace_count += 1
        while self.hand_val > 21 and ace_count > 0:
#                 if the dealer total is >21 and they have an ace, subtract 10.
#                 if they have more aces and the total is still >21, continue to subtract 10.
            self.hand_val -= 10
            ace_count -= 1
        if self.hand_val > 21:
            print("===============")
            print("Your total is over 21. You lost.")
            self.money -= self.bet
            print(f"WALLET: ${self.money:.2f}")
            self.play_again(dealer)
        else:
            if doubledown:
                dealer.take_turn(insurance=False)
            else:
                self.take_turn(dealer)

    
    def quit(self):
        """ Prints out the player's money information and quits game. """
        print("\n=============== THANKS FOR PLAYING ===============")
        print(f"STARTING WALLET: ${self.original_money:.2f}.")
        print(f"CURRENT WALLET: ${self.money:.2f}")
        if self.money < self.original_money:
            print(f"You lost ${self.original_money-self.money:.2f}.")
        elif self.money >= self.original_money:
            print(f"You gained ${self.money-self.original_money:.2f}.")
        print("\nPlay again! I'm sure you'll win big!")
        
    
    def play_again(self, dealer):
        """ Asks the player if they want to play again.
                if so, resets the player's betting information and hand, and starts new game.
                if not, quit. """
        while True:
            again = input("Would you like to play again? (Y/N): ").lower()
            if again not in {"y",'n'}:
                print("That didn't work.")
            elif again == 'y':
                print("YOU'VE CHOSEN PLAY AGAIN")
                # reset all class attributes
                self.bet = 0
                self.hand = []
                self.formatted_hand = []
                self.hand_val = 0
                self.has_blackjack = False
                self.insurance = 0
                dealer.hand = []
                dealer.formatted_hand = []
                dealer.hand_val = 0
                dealer.has_blackjack = False
                dealer.opt_insurance = False
                
                start(dealer, self)
                break
            elif again == 'n':
                self.quit()
                break



class Dealer():
    
    hand = []
    formatted_hand = []
    hand_val = 0
    has_blackjack = False
    opt_insurance = False
    
    def __init__(self, deck, player):
        self.deck = deck
        self.player = player
#         reset the class attributes
        self.hand = []
        self.hand_val = 0
        self.has_blackjack = False
    
    
    def print_hand(self, dealer_turn):
        """ Prints the player's hand, 
            including if they have a blackjack """
        if dealer_turn == True:
            print(f"--- DEALER HAND ---")
            for item in self.formatted_hand:
                print(item[0], end=' ')
            print("")
            for item in self.formatted_hand:
                print(item[1], end=' ')
            print("")
            for item in self.formatted_hand:
                print(item[2], end=' ')
            print("")
            for item in self.formatted_hand:
                print(item[3], end=' ')
            print("")
            for item in self.formatted_hand:
                print(item[4], end=' ')
                
            if self.has_blackjack:
                print("\n\tBLACKJACK!")
                
        elif dealer_turn == False:
            print(f"--- DEALER HAND ---")            
            print(self.formatted_hand[0][0], end=" ")
            if len(self.hand) == 2:
                print('╭┬┬┬┬┬╮')
            else:
                print('')
            print(self.formatted_hand[0][1], end=' ')
            if len(self.hand) == 2:
                print('├╳╳╳╳╳┤')
            else:
                print('')
            print(self.formatted_hand[0][2], end=' ')
            if len(self.hand) == 2:
                print('├╳╳╳╳╳┤')
            else:
                print('')
            print(self.formatted_hand[0][3], end=' ')
            if len(self.hand) == 2:
                print('├╳╳╳╳╳┤')
            else:
                print('')
            print(self.formatted_hand[0][4], end=' ')
            if len(self.hand) == 2:
                print('╰┴┴┴┴┴╯')
            else:
                print('')
        
    def append_formatted_hand(self, card):
        """ Accepts an API card object and appends the formatted_hand attribute
            with the card as a formatted object."""
        suit = self.deck.card_suit(card)
    
        if card['cards'][0]['value'].lower() == 'jack':
            self.formatted_hand.append(['╭─────╮',f'│  J  │', '│     │', f'│  {suit}  │','╰─────╯'])
        elif card['cards'][0]['value'].lower() == 'queen':
            self.formatted_hand.append(['╭─────╮',f'│  Q  │', '│     │', f'│  {suit}  │','╰─────╯'])
        elif card['cards'][0]['value'].lower() == 'king':
            self.formatted_hand.append(['╭─────╮',f'│  K  │', '│     │', f'│  {suit}  │','╰─────╯'])
        elif card['cards'][0]['value'].lower() == 'ace':
            self.formatted_hand.append(['╭─────╮',f'│  A  │', '│     │', f'│  {suit}  │','╰─────╯'])
        elif card['cards'][0]['value'] == '10':
            self.formatted_hand.append(['╭─────╮',f'│ 1 0 │', '│     │', f'│  {suit}  │','╰─────╯'])
        else:
            num = card['cards'][0]['value']
            self.formatted_hand.append(['╭─────╮',f'│  {num}  │', '│     │', f'│  {suit}  │','╰─────╯'])
            
    
    def deal(self):
        """ Simulates dealing the cards. """
#         1. To me
        card = self.deck._get('draw')
        self.player.hand.append(card)
        self.player.append_formatted_hand(card)
        print("--- DEALER HAND ---")
        print("")
        print("")
        print("")
        print("")
        print("")
        self.player.print_hand(insurance=False)
#         add the value of the current card to player's hand
        self.player.hand_val += self.deck.evaluate_card(card)
        
#         2. To Dealer (face up)
        time.sleep(1)
        os.system('cls')
        card = self.deck._get('draw')
        self.hand.append(card)
        self.append_formatted_hand(card)
#         add the value of the current card to dealer's hand
        self.hand_val += self.deck.evaluate_card(card)
        # BOOKMARK - uncomment the line below to force an insurance query
        # self.hand_val = 11
        if self.hand_val == 11:
            self.opt_insurance = True
        self.print_hand(False)
        self.player.print_hand(insurance=False) # for the ambiance, printing my hand below the dealer's
        
#         3. To me
        time.sleep(1)
        os.system('cls')
        card = self.deck._get('draw')
        self.player.hand.append(card)
        self.player.append_formatted_hand(card)
        self.print_hand(False)
#         add the value of the current card to player's hand
        self.player.hand_val += self.deck.evaluate_card(card)
#         If it's a blackjack, let me know. 
        if self.player.hand_val == 21:
            self.player.has_blackjack = True
        self.player.print_hand(insurance=False)
#         print(f"HAND VALUE: {self.player.hand_val}")

#         4. To Dealer (face down)
        time.sleep(1)
        os.system('cls')
        card = self.deck._get('draw')
        self.hand.append(card)
        self.append_formatted_hand(card)
        self.hand_val += self.deck.evaluate_card(card)
        if self.hand_val == 21:
            self.has_blackjack = True
        self.print_hand(False)
        self.player.print_hand(insurance=False)
#         AFTER DEALER'S TURN: add the value of the current hand to dealer's hand
#         If you have a blackjack, check if dealer also has a potential Blackjack
#             if dealer does not have Ace or 10, you automatically win.
#             if dealer has Ace or 10, do dealer's turn first.
#         If you don't have blackjack, take your turn.
        time.sleep(1)
        if self.opt_insurance:
            ins = self.take_insurance()
            if self.has_blackjack:
                os.system('cls')
                self.print_hand(True)
                self.player.print_hand(ins)
                print("Dealer has a Blackjack!")
                if ins:
                    self.player.money += (self.player.insurance*2)
                    self.player.money -= self.player.bet
                
                if self.player.has_blackjack:
                        print("===============")
                        print("TIE!")
                        print(f"WALLET: ${self.player.money:.2f}")
                        self.player.play_again(self)
                else:
                    self.player.take_turn(self)

            else:
                self.print_hand(False)
                if ins:
                    self.player.money -= self.player.insurance
                self.player.print_hand(False)
                print("Dealer does not have a Blackjack.")
                # play continues as usual.

        if self.player.has_blackjack:
                print("===============")
                print("You win!")
                self.player.money += (self.player.bet*1.5)
                print(f"WALLET: ${self.player.money:.2f}")
                self.player.play_again(self)
        else:
            self.player.take_turn(self)


    def take_insurance(self):
        opt_in = input("Would you like to buy insurance? (Y/N): ").lower()
        while opt_in not in {'y','n'}:
            opt_in = input("That didn't work.\nWould you like to buy insurance? (Y/N): ").lower()
        else:
            amt = input(f"You can insure up to ${self.player.bet/2:.2f}. \nHow much would you like to insure? $")
            while True:
                try:
                    if isinstance(float(amt),float): # if it works, continue; if it throws an error, ask again.
                        while float(amt) > self.player.bet / 2:
                            amt = input(f"That didn't work. You can only insure up to ${self.player.bet/2:.2f}."+ 
                                "\nHow much would you like to insure? $")
                        else:
                            print(f"INSURANCE: ${float(amt):.2f}")
                            self.player.insurance = float(amt)
                            break
                except:
                    amt = input("That didn't work. Please enter a number. \nHow much would you like to insure? $")
        return True if opt_in == 'y' else False


        
    def take_turn(self, insurance):
        """ Dealer decides how to take turn """
        os.system('cls')
        self.print_hand(True)
        self.player.print_hand(insurance)
        if self.player.has_blackjack:
            if self.has_blackjack:
                print("===============")
                print("You both have a Blackjack. TIE!")
                print(f"WALLET: ${self.player.money:.2f}")
                self.player.play_again(self)
            else:
                print("===============")
                print("You win!")
                self.player.money += (self.player.bet*1.5)
                print(f"WALLET: ${self.player.money:.2f}")
                self.player.play_again(self)
        else:
            ace_count = 0
            for card in self.hand:
                if card['cards'][0]['value'].lower() == 'ace':
                    ace_count += 1
            while self.hand_val > 21 and ace_count > 0:
#                 if the dealer total is >21 and they have an ace, subtract 10.
#                 if they have more aces and the total is still >21, continue to subtract 10.
                self.hand_val -= 10
                ace_count -= 1
            if self.hand_val > 21:
                print("===============")
                print("Dealer total is over 21. You win!")
                self.player.money += self.player.bet
                print(f"WALLET: ${self.player.money:.2f}")
                self.player.play_again(self)
            elif self.hand_val < 17:
                self.hit()
            elif self.hand_val >= 17 and self.hand_val <= 21:
                self.compare_hands(insurance)
        
    
    def hit(self):
        time.sleep(1)
        os.system('cls')
#         print("Dealer has chosen to HIT.")
        card = self.deck._get("draw")
        self.hand.append(card)
        self.append_formatted_hand(card)
        self.print_hand(True)
        self.player.print_hand(insurance=False)
        self.hand_val += self.deck.evaluate_card(card)
        self.take_turn(insurance=False)
    
    def compare_hands(self, insurance):
        time.sleep(1)
        print("===============")
        if self.hand_val > self.player.hand_val:
            print("Dealer's hand is higher. You lose.")
            self.player.money -= self.player.bet
            print(f"WALLET: ${self.player.money:.2f}")
            self.player.play_again(self)
        elif self.hand_val < self.player.hand_val:
            print("Your hand is higher. You win!")
            self.player.money += self.player.bet
            print(f"WALLET: ${self.player.money:.2f}")
            self.player.play_again(self)
        elif self.hand_val == self.player.hand_val:
            if self.has_blackjack and self.player.has_blackjack:
                print("You both have a Blackjack. TIE!")
                print(f"WALLET: ${self.player.money:.2f}")
                self.player.play_again(self)
            elif self.has_blackjack:
                print("Dealer has Blackjack. You lose.")
                if insurance:
                    print("Subtracting Insurance.")
                    self.player.money -= self.player.insurance
                else:
                    self.player.money -= self.player.bet
                print(f"WALLET: ${self.player.money:.2f}")
                self.player.play_again(self)
            else:
                print("TIE!")
                print(f"WALLET: ${self.player.money:.2f}")
                self.player.play_again(self)



def get_new_deck_id():
    new_deck = requests.get("https://www.deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
    if new_deck.ok:
        deck = new_deck.json()
    else:
        print("Error making new deck.")
    return deck["deck_id"]
    
def start(dealer, player):
    os.system('cls')
    deck = Deck(get_new_deck_id())
    player.deck = deck
    dealer.deck = deck
    print("=============== WELCOME TO BLACKJACK ===============")
    print("PLACE YOUR BETS. Minimum: $5.")
    print("-----")
    print(f"WALLET: ${player.money:.2f}.")

    while True:
        amt = input("MY BET: $")
        if amt.isdigit():
            if amt == '' or int(amt) < 5:
                print("TOO LOW. Minimum bet is $5.")
            elif int(amt) > player.money:
                print(f"TOO HIGH. You only have ${player.money} in your wallet.")
            else:
                player.bet = int(amt)
                os.system('cls')
                dealer.deal()
                break
        else:
            print("Please enter a whole number.")


me = Player(None, 100, 0)
dealer = Dealer(None, me)
start(dealer, me)