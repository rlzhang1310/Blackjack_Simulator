
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