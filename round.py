from deck import BlackjackShoe
from dealer import Dealer
from hand import Hand
from player import Player
from strategies.strategy import StrategyTable
from collections import defaultdict
from counter import Counter
import numpy as np

class BlackjackRound:
    def __init__(self, shoe: BlackjackShoe, players, dealer, blackjack_payout, print_cards=False, resplit_till=4, counter: Counter=None):
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
        self.resplit_till = resplit_till
        self.dealer_profit = 0
        self._print_cards = print_cards
        self.counter = counter
        self.win_count_matrix = np.zeros((10, 35))
        self.profit_count_matrix = np.zeros((10, 35))
        self.total_count_matrix = np.zeros((10, 35))
        ########################################################################
        # BUSTING DEBUGGING VARIABLES
        # self.blackjack_counter = 0
        # self.bust_dict = defaultdict(int)
        # self.total_dict = defaultdict(int)

        self._deal_initial_cards()

    def _deal_initial_cards(self):
        """Deal 2 cards to each player, then 2 cards to the dealer."""
        for i in range(2):
            for player in self.players:
                card = self.shoe.deal_card()
                player.hands[0].add_card(card)
                self.counter.update_count(card)
            card = self.shoe.deal_card()
            self.dealer.hand.add_card(card)
        if self._print_cards:
            self.print_cards()


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
        self.counter.update_count(dealer_upcard)
        if self._print_cards:
            print("=== Dealer Card ===")
            print(dealer_upcard)
        results = []
        # offer insurance if the dealer has potential for blackjack
        if dealer_upcard.rank == "A":
            high_low_true_count = self.get_estimated_high_low_true_count()
            # five_ace_true_count = self.get_estimated_five_aces_true_count()
            for player in self.players:
                player.insurance_bet(high_low_true_count)
            self.dealer.hand.evaluate()
            if self.dealer.hand.is_blackjack():
                self.counter.update_count(self.dealer.hand.cards[0])
                for player in self.players:
                    players_hand = player.hands[0]
                    players_hand.record_index()
                    if not player.hands[0].is_blackjack():
                        players_hand.lost()
                        results.append(f"{player.name} loses, dealer has blackjack")
                    else:
                        players_hand.push()
                        # self.blackjack_counter += 1
                        results.append(f"{player.name} pushes with blackjack")
                # results.extend(self._evaluate_insurance())
                results.extend(self._evaluate_round())
                return results
        for player in self.players:
            self._player_turn(player, dealer_upcard)

        # Dealer takes turn
        self.counter.update_count(self.dealer.hand.cards[0])
        self.dealer.dealer_turn(self.shoe, self.counter)
        # results.extend(self._evaluate_insurance())
        results.extend(self._evaluate_round())

        ########################################################################
        # BUSTING DEBUGGING CODE
        # bust_rank = dealer_upcard.rank
        # if bust_rank in ["10", "J", "Q", "K"]:
        #     bust_rank = "10"
        # self.total_dict[bust_rank] += 1
        # if self.dealer.hand.evaluate() > 21:
        #     self.bust_dict[bust_rank] += 1

        if self._print_cards:
            self.print_cards()
            print("=== Dealer's Cards ===")
            self.dealer.hand.print_hand()
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
            if self._print_cards:
                print(f"\n{player.name}'s actions for hand {hand_index+1}:")
            hand.record_index()
            # Continue acting on this hand until the player stands, busts, or doubles
            while True:

                # Ask the player's strategy for an action
                action = player.get_action(hand, dealer_upcard, self.resplit_till, self.get_estimated_high_low_true_count())
                if self._print_cards:
                    print(action)
                if action == "BUST":
                    hand.lost()
                    break
                
                elif action == "BLACKJACK":
                    # self.blackjack_counter += 1
                    hand.blackjack_win()
                    break

                elif action == "HIT":
                    # Deal one card to the current hand
                    card = self.shoe.deal_card()
                    hand.add_card(card)
                    # hand.record_index()
                    self.counter.update_count(card)

                elif action == "STAND":
                    # Player stops acting on this hand
                    break

                elif action == "DOUBLE":
                    # Deal exactly one more card, then the hand is done
                    card = self.shoe.deal_card()
                    hand.add_card(card)
                    self.counter.update_count(card)
                    hand.double_down()
                    break

                elif action == "SPLIT":
                    # Handle splitting (the hand must have exactly 2 cards of same rank)
                    new_hand = hand.split()

                    # Deal one new card to each split hand
                    card_1 = self.shoe.deal_card()
                    card_2 = self.shoe.deal_card()
                    hand.add_card(card_1)
                    new_hand.add_card(card_2)
                    new_hand.record_index()
                    self.counter.update_count(card_1)
                    self.counter.update_count(card_2)

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

        dealer_upcard_rank = self.dealer.hand.cards[1].rank
        if dealer_upcard_rank == 'A':
            dealer_matrix_index = 9
        elif dealer_upcard_rank in ['J', 'Q', 'K']:
            dealer_matrix_index = 8
        else:
            dealer_matrix_index = int(dealer_upcard_rank) - 2
        outcomes = []
        # Iterate through each player
        dealer_earnings = 0
        for player in self.players:
            player_earnings = 0
            if player.hands[0].insurance_bet > 0:
                if self.dealer.hand.is_blackjack():
                    player_earnings += player.hands[0].insurance_bet * 2
                    dealer_earnings -= player.hands[0].insurance_bet * 2
                    outcomes.append(f"{player.name} wins insurance bet")
                else:
                    player_earnings -= player.hands[0].insurance_bet
                    dealer_earnings += player.hands[0].insurance_bet
                    outcomes.append(f"{player.name} loses insurance bet")

            # Each player could have multiple hands (due to splits, etc.)            
            for j, hand in enumerate(player.hands, start=1):
                for matrix_idx in hand.matrix_index:
                    # hand.print_hand()
                    # print(matrix_idx)
                    self.total_count_matrix[dealer_matrix_index, matrix_idx] += 1
                player_total = hand.evaluate()
                if hand.hand_status == "LOST":
                    outcomes.append(f"{player.name} Hand {j} lost with {player_total}. Dealer wins.")
                    player_earnings -= hand.bet
                    dealer_earnings += hand.bet
                elif hand.hand_status == "BLACKJACK WIN":
                    # Player does not win blackjack bonus for split hands
                    if len(player.hands) > 1:
                        outcomes.append(f"{player.name} Hand {j} has BLACKJACK with split hands")
                        player_earnings += hand.bet  
                        dealer_earnings -= hand.bet
                        for matrix_idx in hand.matrix_index:
                            # if matrix_idx == 24:
                            #     continue
                            self.win_count_matrix[dealer_matrix_index, matrix_idx] += 1
                            # self.total_profit_matrix[dealer_matrix_index, matrix_idx] += 1
                    else:
                        outcomes.append(f"{player.name} Hand {j} has BLACKJACK")
                        payout = round(hand.bet * self.blackjack_payout) # should always be an int
                        player_earnings += payout  
                        dealer_earnings -= payout
                        for matrix_idx in hand.matrix_index:
                            self.win_count_matrix[dealer_matrix_index, matrix_idx] += 1
                            # self.total_profit_matrix[dealer_matrix_index, matrix_idx] += self.blackjack_payout
                elif hand.hand_status == "ACTIVE":
                    if player_total > 21:
                        hand.lost()
                        outcomes.append(f"{player.name} Hand {j} busts with {player_total}. Dealer wins.")
                        player_earnings -= hand.bet
                        dealer_earnings += hand.bet
                    elif dealer_bust:
                        hand.won()
                        outcomes.append(f"{player.name} Hand {j} wins with {player_total}. Dealer busts with {dealer_total}.")
                        player_earnings += hand.bet
                        dealer_earnings -= hand.bet
                        for matrix_idx in hand.matrix_index:
                            self.win_count_matrix[dealer_matrix_index, matrix_idx] += 1
                            # profit = 2 if hand.double else 1
                            # self.total_profit_matrix[dealer_matrix_index, matrix_idx] += profit
                    else:
                        if player_total > dealer_total:
                            hand.won()
                            outcomes.append(f"{player.name} Hand {j} wins with {player_total} > {dealer_total}.")
                            player_earnings += hand.bet
                            dealer_earnings -= hand.bet
                            for matrix_idx in hand.matrix_index:
                                self.win_count_matrix[dealer_matrix_index, matrix_idx] += 1
                                # profit = 2 if hand.double else 1
                                # self.total_profit_matrix[dealer_matrix_index, matrix_idx] += profit
                        elif player_total < dealer_total:
                            hand.lost()
                            outcomes.append(f"Dealer wins with {dealer_total} > {player_total}.")
                            player_earnings -= hand.bet
                            dealer_earnings += hand.bet
                        else:
                            hand.push()
                            outcomes.append(f"Push! {player.name} Hand {j} ties dealer at {player_total}.")
                            for matrix_idx in hand.matrix_index:
                                self.win_count_matrix[dealer_matrix_index, matrix_idx] += 0.5
                                # self.total_profit_matrix[dealer_matrix_index, matrix_idx] += 0.5
                elif hand.hand_status == "PUSH":
                    outcomes.append(f"Push! {player.name} Hand {j} ties dealer at {player_total}.")
                    for matrix_idx in hand.matrix_index:
                        self.win_count_matrix[dealer_matrix_index, matrix_idx] += 0.5
                        # self.total_profit_matrix[dealer_matrix_index, matrix_idx] += 0.5
                else:
                    ## DEBUGGING
                    print(f"Unexpected hand status: {hand.hand_status}")
                    i = 1 / 0
                    return i
            outcomes.append(f"{player.name} earned ${player_earnings}.")
            player.bankroll += player_earnings
        outcomes.append(f"Dealer earned ${dealer_earnings}.")
        self.dealer_profit += dealer_earnings  # Update the dealer's profit after the round ends
        return outcomes

    def get_estimated_high_low_true_count(self):
        """Implement high low count"""
        decks_left = self.shoe.decks_left()
        true_count = self.counter.get_high_low_count() / decks_left
        return true_count
    
    def get_estimated_five_aces_true_count(self):
        """Implement high low count"""
        decks_left = self.shoe.decks_left()
        true_count = self.counter.get_five_aces_count() / decks_left
        return true_count
    
    def print_cards(self):
        for player in self.players:
            print(f"\n{player.name}'s cards:")
            for hand in player.hands:
                hand.print_hand()