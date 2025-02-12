from deck import BlackjackShoe
from hand import Hand
from counter import Counter

class Dealer:
    def __init__(self, hit_on_soft_17, hand):
        self.hit_on_soft_17 = hit_on_soft_17
        self.hand = hand

    def dealer_turn(self, shoedeck: BlackjackShoe, counter) -> int:
        """
        Dealer's logic for hitting or standing based on the rules.
        """
        while True:
            total = self.hand.evaluate()

            # Dealer stands if total is 17 or higher, unless it's a soft 17 and hit_on_soft_17 is True
            if total > 17 or (total == 17 and not (self.hand.soft and self.hit_on_soft_17)):
                break  # Dealer stands
            # Dealer hits if total is less than 17 or it's a soft 17 and hit_on_soft_17 is True
            new_card = shoedeck.deal_card()  # Draw a new card from the deck
            self.hand.add_card(new_card)  # Add the new card to the dealer's hand
            counter.update_count(new_card)
            # If the new card causes the dealer to bust, break the loop
            if self.hand.evaluate() > 21:
                break

        return
    
    def new_hand(self):
        self.hand = Hand()