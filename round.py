from deck import BlackjackShoe
from dealer import Dealer
from hand import Hand

class BlackjackRound:
    def __init__(self, shoe: BlackjackShoe, num_players: int = 1):
        """
        Simulates a single round of blackjack with `num_players` players,
        using the provided `shoe` for card dealing.
        """
        self.shoe = shoe
        self.num_players = num_players
        
        # Store each player's hand as a list of (rank, suit)
        self.players = [Hand() for _ in range(num_players)]
        # Dealer's hand
        self.dealer = Dealer(hit_on_soft_17=True, hand=Hand())

        # Deal initial 2 cards to each player, then 2 to the dealer
        self._deal_initial_cards()

    def _deal_initial_cards(self):
        """Deal 2 cards to each player, then 2 cards to the dealer."""
        for _ in range(2):
            for i in range(self.num_players):
                self.players[i].add_card(self.shoe.deal_card())
            self.dealer.hand.add_card(self.shoe.deal_card())

        self.print_round()

        if self.shoe.reshuffle_needed:
            self.shoe = BlackjackShoe.create_shoe(self.num_decks)
            BlackjackShoe.shuffle_shoe(self.shoe)
            self.deal_index = 0
    def print_round(self):
        for i in range(self.num_players):
            print(f"\nPlayer {i+1} cards:")
            self.players[i].print_hand()
        print("\nDealer cards:")
        self.dealer.hand.print_hand()
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
        self.dealer.dealer_turn(self.shoe)
        self.print_round()
        # Evaluate results
        results = self._evaluate_round()
        return results

    def _player_turn(self, player_index):
        """
        Simple (naive) strategy for the player:
        - Keep hitting until hand value >= 17
        """
        while self.players[player_index].evaluate() < 17:
            self.players[player_index].add_card(self.shoe.deal_card())

    def _evaluate_round(self):
        """
        Compare each player's final hand to the dealer's hand
        and return a summary of outcomes.
        """
        dealer_total = self.dealer.hand.evaluate()
        dealer_bust = dealer_total > 21

        outcomes = []
        for i, hand in enumerate(self.players):
            player_total = hand.evaluate()
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
