from deck import BlackjackShoe
from dealer import Dealer
from hand import Hand
from player import Player
from strategies.strategy import StrategyTable

class BlackjackRound:
    def __init__(self, shoe: BlackjackShoe, players, dealer, blackjack_payout):
        """
        Simulates a single round of blackjack with `num_players` players,
        using the provided `shoe` for card dealing.
        """
        self.shoe = shoe
        
        # Store each player's hand as a list of (rank, suit)
        self.players = players
        # Dealer's hand
        self.dealer = dealer
        self.blackjack_payout = blackjack_payout
        self.dealer_profit = 0
        # Deal initial 2 cards to each player, then 2 to the dealer
        self._deal_initial_cards()

    def _deal_initial_cards(self):
        """Deal 2 cards to each player, then 2 cards to the dealer."""
        for _ in range(2):
            for player in self.players:
                player.hands[0].add_card(self.shoe.deal_card())
            self.dealer.hand.add_card(self.shoe.deal_card())

        self.print_round()

        if self.shoe.reshuffle_needed:
            self.shoe = BlackjackShoe.create_shoe(self.num_decks)
            BlackjackShoe.shuffle_shoe(self.shoe)
            self.deal_index = 0


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
            for player in self.players:
                player.insurance_bet(0)
            if self.dealer.hand.is_blackjack():
                results = []
                for player in self.players:
                    players_hand = player.hands[0]
                    if not player.hands[0].is_blackjack():
                        players_hand.lost()
                        results.append(f"{player.name} loses, dealer has blackjack")
                    else:
                        players_hand.push()
                        results.append(f"{player.name} pushes with blackjack")
                results.extend(self._evaluate_round())
                return results
        for player in self.players:
            self._player_turn(player, dealer_upcard)

        # Dealer takes turn
        self.dealer.dealer_turn(self.shoe)
        results = self._evaluate_round()

        self.print_round()
        # Evaluate results
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
                    hand.lost()
                    break
                
                elif action == "BLACKJACK":
                    hand.blackjack_win()
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
                    hand.double_down()
                    #[TODO]: Implement the 'double' action
                    break

                elif action == "SPLIT":
                    # Handle splitting (the hand must have exactly 2 cards of same rank)
                    new_hand = hand.split()

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
        dealer_earnings = 0
        for player in self.players:
            # Each player could have multiple hands (due to splits, etc.)
            player_earnings = 0
            for j, hand in enumerate(player.hands, start=1):
                player_total = hand.evaluate()
                if hand.hand_status == "LOST":
                    outcomes.append(f"{player.name} Hand {j} lost with {player_total}. Dealer wins.")
                    player_earnings -= hand.bet
                    dealer_earnings += hand.bet
                elif hand.hand_status == "BLACKJACK WIN":
                    payout = round(hand.bet * self.blackjack_payout) # should always be an int
                    player_earnings += payout  
                    dealer_earnings -= payout
                elif hand.hand_status == "ACTIVE":
                    if dealer_bust:
                        hand.won()
                        outcomes.append(f"{player.name} Hand {j} wins with {player_total}. Dealer busts with {dealer_total}.")
                        player_earnings += hand.bet
                        dealer_earnings -= hand.bet
                    else:
                        if player_total > dealer_total:
                            hand.won()
                            outcomes.append(f"{player.name} Hand {j} wins with {player_total} > {dealer_total}.")
                            player_earnings += hand.bet
                            dealer_earnings -= hand.bet
                        elif player_total < dealer_total:
                            hand.lost()
                            outcomes.append(f"Dealer wins with {dealer_total} > {player_total}.")
                            player_earnings -= hand.bet
                            dealer_earnings += hand.bet
                        else:
                            hand.push()
                            outcomes.append(f"Push! {player.name} Hand {j} ties dealer at {player_total}.")
            outcomes.append(f"{player.name} earned ${player_earnings}.")
        outcomes.append(f"Dealer earned ${dealer_earnings}.")
                # if player_bust:
                #     outcomes.append(
                #         f"{player.name} Hand {j} busts with {player_total}. Dealer wins."
                #     )
                # elif dealer_bust:
                #     outcomes.append(
                #         f"Dealer busts with {dealer_total}. {player.name} Hand {j} wins."
                #     )
                # else:
                #     # Neither bust
                #     if player_total > dealer_total:
                #         outcomes.append(
                #             f"{player.name} Hand {j} wins with {player_total} > {dealer_total}."
                #         )
                #     elif player_total < dealer_total:
                #         outcomes.append(
                #             f"Dealer wins with {dealer_total} > {player_total}."
                #         )
                #     else:
                #         outcomes.append(
                #             f"Push! {player.name} Hand {j} ties dealer at {player_total}."
                #         )

        return outcomes

    def print_round(self):
        for player in self.players:
            print(f"\n{player.name}'s cards:")
            for hand in player.hands:
                hand.print_hand()
        print("\nDealer cards:")
        self.dealer.hand.print_hand()