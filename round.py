from deck import BlackjackShoe
from dealer import Dealer
from hand import Hand
from player import Player
from strategies.strategy import StrategyTable

class BlackjackRound:
    def __init__(self, shoe: BlackjackShoe, num_players: int = 1):
        """
        Simulates a single round of blackjack with `num_players` players,
        using the provided `shoe` for card dealing.
        """
        self.shoe = shoe
        self.num_players = num_players
        
        # Store each player's hand as a list of (rank, suit)
        self.players = [Player(name=f"Player {i}", strategy=StrategyTable["MULTIDECK"], bankroll=1000, hands=[Hand()]) for i in range(num_players)]
        # Dealer's hand
        self.dealer = Dealer(hit_on_soft_17=True, hand=Hand())

        # Deal initial 2 cards to each player, then 2 to the dealer
        self._deal_initial_cards()

    def _deal_initial_cards(self):
        """Deal 2 cards to each player, then 2 cards to the dealer."""
        for _ in range(2):
            for i in range(self.num_players):
                self.players[i].hands[0].add_card(self.shoe.deal_card())
            self.dealer.hand.add_card(self.shoe.deal_card())

        self.print_round()

        if self.shoe.reshuffle_needed:
            self.shoe = BlackjackShoe.create_shoe(self.num_decks)
            BlackjackShoe.shuffle_shoe(self.shoe)
            self.deal_index = 0

    def print_round(self):
        for i in range(self.num_players):
            print(f"\n{self.players[i].name}'s cards:")
            for hand in self.players[i].hands:
                hand.print_hand()
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
        dealer_upcard = self.dealer.hand.cards[1]

        # offer insurance if the dealer has potential for blackjack
        if dealer_upcard.rank in ["A", "10", "J", "Q", "K"]:
            for i in range(self.num_players):
                self.players[i].insurance_bet(0)
            if self.dealer.hand.is_blackjack():
                results = []
                for i in range(self.num_players):
                    if not self.players[i].hands[0].is_blackjack():
                        results.append(f"Player {i} loses, dealer has blackjack")
                    else:
                        results.append(f"Player {i} pushes with blackjack")
                return results
        for i in range(self.num_players):
            self._player_turn(self.players[i], dealer_upcard)

        # Dealer takes turn
        self.dealer.dealer_turn(self.shoe)
        self.print_round()
        # Evaluate results
        results = self._evaluate_round()
        return results

    def _player_turn(self, player, dealer_upcard, hand_index=0):
        """
        Allow the player to act on each of their hands in sequence (handling splits).
        'player.hands' is a list of Hand objects. 
        """
        # We'll process each hand in the player's list of hands
        while hand_index < len(player.hands):
            hand = player.hands[hand_index]
            print(f"\n{player.name}'s actions for hand {hand_index+1}:")
            # Continue acting on this hand until the player stands, busts, or doubles
            while True:

                # Ask the player's strategy for an action
                action = player.get_action(hand, dealer_upcard)
                print(action)
                if action == "BUST":
                    break
                
                elif action == "BLACKJACK":
                    break

                elif action == "HIT":
                    # Deal one card to the current hand
                    hand.add_card(self.shoe.deal_card())

                elif action == "STAND":
                    # Player stops acting on this hand
                    break

                elif action == "DOUBLE":
                    # Deal exactly one more card, then the hand is done
                    hand.add_card(self.shoe.deal_card())
                    #[TODO]: Implement the 'double' action
                    break

                elif action == "SPLIT":
                    # Handle splitting (the hand must have exactly 2 cards of same rank)
                    second_card = hand.cards.pop()  # Now 'hand' has just 1 card

                    # Create a new Hand with that second card
                    new_hand = Hand([second_card])

                    # Deal one new card to each split hand
                    hand.add_card(self.shoe.deal_card())
                    new_hand.add_card(self.shoe.deal_card())

                    # Append the new hand to the player's list
                    player.hands.append(new_hand)
                    continue

                else:
                    # Fallback if no recognized action
                    break

            # Move to the next hand in the list
            hand_index += 1

    def _evaluate_round(self):
        """
        Compare each player's final hands to the dealer's hand
        and return a summary of outcomes.
        """
        # Evaluate the dealer's final total
        dealer_total = self.dealer.hand.evaluate()
        dealer_bust = dealer_total > 21

        outcomes = []
        # Iterate through each player
        for i, player in enumerate(self.players, start=1):
            # Each player could have multiple hands (due to splits, etc.)
            for j, hand in enumerate(player.hands, start=1):
                player_total = hand.evaluate()
                player_bust = player_total > 21

                if player_bust:
                    outcomes.append(
                        f"Player {i} Hand {j} busts with {player_total}. Dealer wins."
                    )
                elif dealer_bust:
                    outcomes.append(
                        f"Dealer busts with {dealer_total}. Player {i} Hand {j} wins."
                    )
                else:
                    # Neither bust
                    if player_total > dealer_total:
                        outcomes.append(
                            f"Player {i} Hand {j} wins with {player_total} > {dealer_total}."
                        )
                    elif player_total < dealer_total:
                        outcomes.append(
                            f"Dealer wins with {dealer_total} > {player_total}."
                        )
                    else:
                        outcomes.append(
                            f"Push! Player {i} Hand {j} ties dealer at {player_total}."
                        )

        return outcomes

