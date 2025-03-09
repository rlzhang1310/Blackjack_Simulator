
class Hand:
    def __init__(self, cards=None, bet: int=0):
        """
        Initialize a Hand with an optional initial list of cards.
        Each card is expected to have a `.rank` attribute, e.g. "A", "K", "10", etc.
        """
        # If no initial cards are provided, start with an empty list
        self.cards = cards if cards else []

        # These will be set by self.evaluate() below
        self.value = 0
        self.soft = False  # Indicates if at least one Ace is counted as 11
        # Evaluate the hand right away if there are initial cards
        if self.cards:
            self.evaluate()

        self.bet = bet
        self.hand_status = "ACTIVE"
        self.matrix_index = set()
        self.double = False
        self.was_split = False
    def evaluate(self):
        """
        Calculates and updates:
          - self.value (the best total of the hand)
          - self.soft  (True if at least one Ace is counted as 11)
        
        Returns the computed total for convenience.
        """
        # Map card ranks to their base values.
        # Note: We'll treat Aces as 11 initially, then adjust as needed.
        value_map = {
            "A": 11, "K": 10, "Q": 10, "J": 10, "10": 10,
            "9": 9,  "8": 8,  "7": 7,  "6": 6,
            "5": 5,  "4": 4,  "3": 3,  "2": 2
        }

        total = 0
        ace_count = 0

        # First pass: Sum all card values, counting A as 11
        for card in self.cards:
            total += value_map[card.rank]
            if card.rank == "A":
                ace_count += 1

        # Adjust for Aces if we're over 21
        # Each adjustment turns one Ace from 11 down to 1 (subtract 10)
        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1

        # If we still have at least one Ace counted as 11,
        # that means we have a "soft" hand
        self.soft = (ace_count > 0)

        self.value = total
        return total

    def add_card(self, card):
        """
        Adds one card to the hand and re-evaluates the total.
        """
        self.cards.append(card)
        self.evaluate()

    def is_busted(self):
        """
        Returns True if the hand's total value exceeds 21.
        """
        if self.value > 21:
            self.hand_status = "BUST"
            return True
        return False

    def is_blackjack(self):
        """
        Returns True if the hand contains exactly two cards and has a total of 21.
        """
        if len(self.cards) == 2 and self.value == 21:
            self.hand_status = "BLACKJACK"
            return True
        return False
    
    def lost(self):
        self.hand_status = "LOST"
        
    def won(self):
        self.hand_status = "WON"
    
    def push(self):
        self.hand_status = "PUSH"

    def blackjack_win(self):
        self.hand_status = "BLACKJACK WIN"

    def clear(self):
        """
        Clears the hand of all cards and resets value/soft status.
        """
        self.cards = []
        self.value = 0
        self.soft = False
        self.insurance_bet = 0
        self.hand_status = "ACTIVE"
        self.bet = 0

    def put_initial_bet(self, bet):
        self.bet = bet

    def double_down(self):
        self.bet *= 2
        self.double = True

    def split(self):
        second_card = self.cards.pop()  # Now 'hand' has just 1 card
        # Create a new Hand with that second card
        new_hand = Hand([second_card])
        new_hand.bet = self.bet
        new_hand.hand_status = "ACTIVE"
        new_hand.matrix_index = self.matrix_index.copy()
        self.was_split = True
        new_hand.was_split = True
        return new_hand
    
    def is_pair(self):
        if len(self.cards) != 2:
            return False

        ranks = [card.rank for card in self.cards]
        # Check if both are 10/J/Q/K
        if (ranks[0] in ["10", "J", "Q", "K"] 
                and ranks[1] in ["10", "J", "Q", "K"]):
            return True
        return (ranks[0] == ranks[1])
    
    def get_player_matrix_index(self):
        value_map = {
            "A": 11, "K": 10, "Q": 10, "J": 10, "10": 10,
            "9": 9,  "8": 8,  "7": 7,  "6": 6,
            "5": 5,  "4": 4,  "3": 3,  "2": 2
        }
        list = []
        self.evaluate()
        if self.is_pair():
            list.append(int(23 + (value_map[self.cards[0].rank])))
            if self.cards[0].rank not in ["2", "A"]:
                list.append(self.value - 5)
        elif self.soft:
            list.append(int(15 + (self.value - 12)))
        else:
            list.append(self.value - 5)
        return list
        
    def record_index(self):
        self.matrix_index.update(self.get_player_matrix_index())
    def print_hand(self):
        """
        Prints the hand in a human-readable format, showing:
          - The cards in the hand
          - The total value
          - Whether it's soft or not
        """
        # Create a list of string representations of each card, e.g. ["A of Hearts", "10 of Clubs"]
        card_strings = [str(card) for card in self.cards]

        # Join them with a comma or some other separator
        cards_str = ", ".join(card_strings)

        # Indicate if the hand is soft
        soft_str = " (soft)" if self.soft else ""

        print(f"Hand: {cards_str} | Value: {self.value}{soft_str}")