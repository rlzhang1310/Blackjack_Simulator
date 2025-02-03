import random

class Card:
    def __init__(self, rank, suit):
        """
        Initialize a card with a rank and suit.

        :param rank: The rank of the card (e.g., "A", "2", ..., "K").
        :param suit: The suit of the card (e.g., "Clubs", "Diamonds", "Hearts", "Spades").
        """
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        """
        Return a string representation of the card.
        """
        return f"{self.rank} of {self.suit}"

    def __eq__(self, other):
        """
        Check if two cards are equal based on rank and suit.
        """
        return self.rank == other.rank and self.suit == other.suit
        
suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", 
         "9", "10", "J", "Q", "K"]

def create_single_deck():
    """Create a list of (rank, suit) for one standard deck."""
    return [Card(rank, suit) for suit in suits for rank in ranks]
def create_shoe(num_decks=8):
    """Create a shoe composed of num_decks standard decks."""
    shoe = []
    for _ in range(num_decks):
        shoe.extend(create_single_deck())
    return shoe
def place_cut_card(shoe, penetration=0.75):
    """
    Places a cut card in the shoe. 
    `penetration` is what fraction of the shoe will be dealt before hitting the cut card.
    Example: 0.75 means 75% of the deck is dealt before cut card is reached.
    Returns (shoe, cut_index).
    """
    # The cut_index is how many cards from the 'top' you deal before you see the cut card.
    cut_index = int(len(shoe) * penetration)
    return shoe, cut_index

def shuffle_shoe(shoe):
    """Fisher-Yates (Knuth) shuffle in-place."""
    random.shuffle(shoe)
    return shoe


class BlackjackShoe:
    def __init__(self, num_decks=8, cut_penetration=0.75):
        self.num_decks = num_decks
        self.cut_penetration = cut_penetration
        # Initialize and shuffle right away
        self.shoe = create_shoe(self.num_decks)
        shuffle_shoe(self.shoe)
        # Place the cut card
        _, self.cut_index = place_cut_card(self.shoe, self.cut_penetration)
        self.deal_index = 0  # How many cards we've dealt so far

    def deal_card(self):
        """
        Deals one card from the shoe. 
        If we pass the cut card, we note that we should reshuffle soon.
        """
        if self.deal_index >= len(self.shoe):
            # Shoe is empty, definitely reshuffle
            self.reshuffle()

        card = self.shoe[self.deal_index]
        self.deal_index += 1

        # Check if we've passed the cut
        if self.deal_index > self.cut_index:
            # In a real game, you'd wait until the end of the current hand to reshuffle.
            # For simplicity, we can reshuffle right now or set a flag to do so later.
            self.reshuffle()

        return card

    def reshuffle(self):
        """
        Reshuffles the shoe and places the cut card again.
        """
        self.shoe = create_shoe(self.num_decks)
        shuffle_shoe(self.shoe)
        _, self.cut_index = place_cut_card(self.shoe, self.cut_penetration)
        self.deal_index = 0

class Hand:
    def __init__(self, cards=None):
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
        return self.value > 21

    def clear(self):
        """
        Clears the hand of all cards and resets value/soft status.
        """
        self.cards = []
        self.value = 0
        self.soft = False
