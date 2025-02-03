from deck import Hand

class Dealer:
    def __init__(self, hit_on_soft_17, hand):
        self.hit_on_soft_17 = hit_on_soft_17
        self.hand = hand
        self.hidden_card = hand[0]  # The dealer's first card is hidden
        self.shown_card = hand[1]   # The dealer's second card is shown

    def deal(self, deck):
        """
        Dealer's logic for hitting or standing based on the rules.
        """
        while True:
            total = self.hand.evaluate()
            is_soft = self.hand.soft  # Assuming the Hand class has a 'soft' attribute

            # Dealer stands if total is 17 or higher, unless it's a soft 17 and hit_on_soft_17 is True
            if total > 17 or (total == 17 and not (is_soft and self.hit_on_soft_17)):
                break  # Dealer stands

            # Dealer hits if total is less than 17 or it's a soft 17 and hit_on_soft_17 is True
            new_card = deck.deal()  # Draw a new card from the deck
            self.hand.add_card(new_card)  # Add the new card to the dealer's hand

            # If the new card causes the dealer to bust, break the loop
            if self.hand.evaluate() > 21:
                break