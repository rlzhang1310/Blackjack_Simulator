from deck import BlackjackShoe, Hand
from dealer import Dealer

class BlackjackRound:
    def __init__(self, shoe: BlackjackShoe, num_players: int = 1):
        """
        Simulates a single round of blackjack with `num_players` players,
        using the provided `shoe` for card dealing.
        """
        self.shoe = shoe
        self.num_players = num_players
        
        # Store each player's hand as a list of (rank, suit)
        self.player_hands = [[] for _ in range(num_players)]
        # Dealer's hand
        self.dealer_hand = []

        # Deal initial 2 cards to each player, then 2 to the dealer
        self._deal_initial_cards()

    def _deal_initial_cards(self):
        """Deal 2 cards to each player, then 2 cards to the dealer."""
        for _ in range(2):
            for i in range(self.num_players):
                self.player_hands[i].append(self.shoe.deal_card())
            self.dealer_hand.append(self.shoe.deal_card())

    def play_round(self):
        """
        Plays out the round:
        1) Each player acts with a simple strategy
        2) Dealer acts
        3) Determine results
        Returns a list of outcome strings or any data structure you prefer.
        """
        # Players take their turns
        for i in range(self.num_players):
            self._player_turn(i)

        # Dealer takes turn
        self._dealer_turn()

        # Evaluate results
        results = self._evaluate_round()
        return results

    def _player_turn(self, player_index):
        """
        Simple (naive) strategy for the player:
        - Keep hitting until hand value >= 17
        """
        while self._hand_value(self.player_hands[player_index]) < 17:
            self.player_hands[player_index].append(self.shoe.deal_card())

    def _dealer_turn(self):
        """Dealer must hit until total >= 17 (typical blackjack rule)."""
        while self._hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.shoe.deal_card())

    def _evaluate_round(self):
        """
        Compare each player's final hand to the dealer's hand
        and return a summary of outcomes.
        """
        dealer_total = self._hand_value(self.dealer_hand)
        dealer_bust = dealer_total > 21

        outcomes = []
        for i, hand in enumerate(self.player_hands):
            player_total = self._hand_value(hand)
            player_bust = player_total > 21

            if player_bust:
                outcomes.append(f"Player {i+1} busts with {player_total}. Dealer wins.")
            elif dealer_bust:
                outcomes.append(f"Dealer busts with {dealer_total}. Player {i+1} wins.")
            else:
                # Neither bust
                if player_total > dealer_total:
                    outcomes.append(f"Player {i+1} wins with {player_total} > {dealer_total}.")
                elif player_total < dealer_total:
                    outcomes.append(f"Dealer wins with {dealer_total} > {player_total}.")
                else:
                    outcomes.append(f"Push! Player {i+1} ties dealer at {player_total}.")

        return outcomes
