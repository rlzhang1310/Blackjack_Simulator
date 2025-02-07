import random

suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", 
         "9", "10", "J", "Q", "K"]

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
        
def create_single_deck():
    """Create a list of (rank, suit) for one standard deck."""
    return [Card(rank, suit) for suit in suits for rank in ranks]
def create_shoe(num_decks=8):
    """Create a shoe composed of num_decks standard decks."""
    shoe = []
    for _ in range(num_decks):
        shoe.extend(create_single_deck())
    shuffle_shoe(shoe)
    return shoe

def shuffle_shoe(shoe):
    """Fisher-Yates (Knuth) shuffle in-place."""
    # random.shuffle(shoe)
    # return shoe
    n = len(shoe)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        shoe[i], shoe[j] = shoe[j], shoe[i]


class BlackjackShoe:
    def __init__(self, num_decks=8, cut_index=None):
        self.num_decks = num_decks
        if cut_index is None:
            leftover_decks = random.uniform(1, 2)
            self.cut_index = 416 - round(52 * leftover_decks)
        else:
            self.cut_index = cut_index   
        # Initialize and shuffle right away
        self.reshuffle_needed = False
        self.cards = create_shoe(self.num_decks)
        # self.cards = shuffle_shoe(self.cards)
        # Place the cut card
        self.deal_index = 0  # How many cards we've dealt so far

    def deal_card(self):
        """
        Deals one card from the shoe. 
        If we pass the cut card, we note that we should reshuffle soon.
        """
        if self.deal_index >= len(self.cards) or self.deal_index >= self.cut_index:
            self.reshuffle_needed = True

        card = self.cards[self.deal_index]
        self.deal_index += 1

        return card
