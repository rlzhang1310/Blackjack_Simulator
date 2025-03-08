from hand import Hand
import copy

class Player:
    """
    A Blackjack Player with a specific strategy.
    """
    def __init__(self, name, strategy, bankroll, hands, min_bet=10, denominations=10, high_low_counting=False, ace_five_counting=False):
        """
        :param name: A string to identify this player
        :param strategy: An object implementing .get_action(hand, dealer_card)
        """
        self.name = name
        self.hands = hands
        self.pair_strategy = strategy["PAIR"]
        self.soft_strategy = strategy["SOFT"]
        self.hard_strategy = strategy["HARD"]
        self.high_low_counting = high_low_counting
        self.ace_five_counting = ace_five_counting
        self.bankroll = bankroll
        self.min_bet = min_bet
        self.denominations = denominations

    def play_another_hand(self):
        name = self.name + "_" + "+TC"
        second_hand_player = copy.deepcopy(self)
        second_hand_player.name = name
        return second_hand_player

    def get_action(self, hand, dealer_card, resplit_till, true_count):
        """
        Determine whether to HIT, STAND, DOUBLE, or SPLIT using the strategy tables.
        :param hand: Hand object (with hand.value, hand.soft, hand.cards).
        :param dealer_card: A Card object representing the dealer's upcard.
        :return: A string in ["HIT", "STAND", "DOUBLE", "SPLIT", "BUST", "BLACKJACK"  ]
        """
        # Quick checks
        if hand.is_busted():
            return "BUST" 
        
        if hand.is_blackjack():
            return "BLACKJACK"
        
        # Dealer upcard as integer (2..11)
        up_val = dealer_upcard_value(dealer_card)

        if self.high_low_counting:
            action = self._deviations(hand, up_val, resplit_till, true_count)
            if action:
                return action
        # If 2 cards and pair
        if len(hand.cards) == 2 and self._is_pair(hand) and len(self.hands) < resplit_till:
            action = self._pair_action(hand, up_val)
            if action:
                return action  # if the strategy says "Split" or "Stand" or something

        # If hand is soft
        if hand.soft:
            return self._soft_action(hand.value, up_val, can_double=(len(hand.cards)==2))

        # Otherwise, hard
        return self._hard_action(hand.value, up_val, can_double=(len(hand.cards)==2))

    def _is_pair(self, hand):
        """Check if a 2-card hand is a pair or '10-value pair' (like K, Q)."""
        if len(hand.cards) != 2:
            return False

        ranks = [card.rank for card in hand.cards]
        # Check if both are 10/J/Q/K
        if (ranks[0] in ["10", "J", "Q", "K"] 
                and ranks[1] in ["10", "J", "Q", "K"]):
            return True
        return (ranks[0] == ranks[1])

    def _pair_action(self, hand, dealer_up_val):
        """
        Use PAIR_ACTIONS table for the 2-card pair.
        :return: "HIT", "STAND", "DOUBLE", "SPLIT", or None
        """
        c1, c2 = hand.cards
        # Normalize 'T' for 10/J/Q/K
        def normalize_rank(r):
            if r in ["10", "J", "Q", "K"]:
                return 'T'
            elif r == "A":
                return 'A'
            else:
                return r

        r1, r2 = normalize_rank(c1.rank), normalize_rank(c2.rank)
        # Ensure a consistent tuple order
        pair_tuple = tuple(sorted((r1, r2)))

        pair_rule = self.pair_strategy.get(pair_tuple)
        if not pair_rule:
            return None  # no special rule, revert to normal logic

        # Some pairs map to { 'ANY': 'P' } => always do that
        if 'ANY' in pair_rule:
            action = pair_rule['ANY']
            if action == 'P':
                return "SPLIT"
            elif action == 'S':
                return "STAND"
            # etc. or None
            return None

        # Otherwise, we have a dictionary keyed by up_val or 'DEFAULT'
        # Try exact match
        action = pair_rule.get(dealer_up_val)
        if action is None:
            # fallback to 'DEFAULT' or do nothing
            action = pair_rule.get('DEFAULT')
        if action is None:
            return None

        # Convert short code to a full action
        if action == 'P':
            return "SPLIT"
        elif action == 'S':
            return "STAND"
        elif action == 'H':
            return "HIT"
        elif action == 'D':
            # doubling doesn't make sense with pairs => ignoring
            return "HIT"
        # or fallback
        return None

    def _soft_action(self, total, dealer_up_val, can_double):
        """Use the SOFT_ACTIONS table for a soft total."""
        # If total > 21 => stand? (shouldn’t happen in 'soft' logic but just in case)
        if total >= 21:
            return "STAND"

        rule = self.soft_strategy.get(total)
        if not rule:
            # If total < 13 or > 21, default to 'HIT'? 
            return "HIT"

        # Some entries have 'ALL' = 'H' or 'S'
        if 'ALL' in rule:
            action_code = rule['ALL']
            return self._interpret_action_code(action_code, can_double)

        # If there's no single 'ALL' rule, we check up_val
        action_code = rule.get(dealer_up_val)
        if action_code is None:
            action_code = rule.get('DEFAULT', 'H')  # fallback

        return self._interpret_action_code(action_code, can_double)

    def _hard_action(self, total, dealer_up_val, can_double):
        """Use the HARD_ACTIONS table for a hard total."""
        if total < 5:
            return "HIT"  # minimal edge case
        if total > 17:
            # 18 or more => stand
            return "STAND"

        rule = self.hard_strategy.get(total)
        if not rule:
            # e.g. total 18 or 19 if needed
            if total >= 17:
                return "STAND"
            return "HIT"

        if 'ALL' in rule:
            return self._interpret_action_code(rule['ALL'], can_double)

        # Look up the dealer_up_val or fallback
        action_code = rule.get(dealer_up_val)
        if action_code is None:
            action_code = rule.get('DEFAULT', 'H')
        return self._interpret_action_code(action_code, can_double)

    def _interpret_action_code(self, code, can_double):
        """
        Convert single-letter code into full action,
        respecting the 'can_double' flag (2-card only).
        """
        if code == 'H':
            return "HIT"
        elif code == 'S':
            return "STAND"
        elif code == 'D':
            # If we can double, do so; else default to HIT
            return "DOUBLE" if can_double else "HIT"
        elif code == 'P':
            return "SPLIT"
        return "HIT"  # fallback

    def _deviations(self, hand, dealer_up_val, resplit_till, true_count):
        if len(hand.cards) == 2 and self._is_pair(hand) and len(self.hands) < resplit_till and hand.value == 20:
            if true_count >= 4 and dealer_up_val == 6:
                return "SPLIT"
            if true_count >= 5 and dealer_up_val == 5:
                return "SPLIT"
            if true_count >= 6 and dealer_up_val == 4:
                return "SPLIT"
        elif len(hand.cards) == 2 and self._is_pair(hand) and len(self.hands) < resplit_till and hand.value == 18:
            if true_count >= 3 and dealer_up_val == 7:
                return "SPLIT"
        elif hand.value == 16:
            if true_count > 0 and dealer_up_val == 10:
                return "STAND"
            if true_count >= 4 and dealer_up_val == 9:
                return "STAND"
            if true_count >= 3 and dealer_up_val == 11:
                return "STAND"
        elif hand.value == 15:
            if true_count >= 4 and dealer_up_val == 10:
                return "STAND"
        elif hand.value == 13:
            if true_count <= -1 and dealer_up_val == 2:
                return "HIT"
            if true_count <= -2 and dealer_up_val == 3:
                return "HIT"
        elif hand.value == 12:
            if true_count >= 3 and dealer_up_val == 2:
                return "STAND"
            if true_count >= 2 and dealer_up_val == 3:
                return "STAND"
            if true_count < 0 and dealer_up_val == 4:
                return "HIT"
        elif hand.value == 11:
            if true_count > 0 and dealer_up_val == 11:
                return "DOUBLE"
        elif hand.value == 10:
            if true_count >= 4 and dealer_up_val == 10:
                return "DOUBLE"
            if true_count >= 3 and dealer_up_val == 11:
                return "DOUBLE"
        elif hand.soft and hand.value == 20:
            if true_count >= 4 and dealer_up_val == 6:
                return "DOUBLE"
            if true_count >= 5 and dealer_up_val == 5:
                return "DOUBLE"
            if true_count >= 6 and dealer_up_val == 4:
                return "DOUBLE"
        elif hand.soft and hand.value == 19:
            if true_count >= 0 and dealer_up_val == 6:
                return "DOUBLE"
            if true_count >= 1 and dealer_up_val == 5:
                return "DOUBLE"
            if true_count >= 3 and dealer_up_val == 4:
                return "DOUBLE"
            if true_count >= 5 and dealer_up_val == 3:
                return "DOUBLE"
        elif hand.soft and hand.value == 17:
            if true_count >= 1 and dealer_up_val == 2:
                return "DOUBLE"
        elif hand.soft and hand.value == 15:
            if true_count < 0 and dealer_up_val == 4:
                return "HIT"
        else:
            return None

 
    def insurance_bet(self, true_count):
        if true_count >= 3.2:
            bet = self.hands[0].bet / 2
            self.hands[0].put_insurance_bet(bet)
        return
    
    def put_bet_on_initial_hand(self, high_low_true_count, five_aces_true_count):
        if self.high_low_counting:
            bet = self.min_bet * 2
            if high_low_true_count <= -1:
                bet -= self.denominations
            elif high_low_true_count >= 2:
                bet += 2 * self.denominations
            elif high_low_true_count >= 3:
                bet += 4 * self.denominations
            elif high_low_true_count >= 4:
                bet += 6 * self.denominations
            self.hands[0].put_initial_bet(bet)
        elif self.ace_five_counting:
            bet = self.min_bet
            if five_aces_true_count >= 2:
                bet *= 2
            elif five_aces_true_count >= 3:
                bet *= 4
            elif five_aces_true_count >= 4:
                bet *= 8
            elif five_aces_true_count >= 5:
                bet *= 16
            elif five_aces_true_count >= 6:
                bet *= 32
            self.hands[0].put_initial_bet(bet)
        else:
            bet = self.min_bet
            self.hands[0].put_initial_bet(bet)
        return bet

    def new_hand(self):
        self.hands = [Hand()]

    def print_hands(self):
        print("--------------------")
        for hand in self.hands:
            print(hand.print_hand())
        print("--------------------")


def dealer_upcard_value(card):
    """Convert the dealer's upcard rank into a numeric value for strategy lookup."""
    rank = card.rank
    if rank in ["10", "J", "Q", "K"]:
        return 10
    elif rank == "A":
        return 11
    else:
        return int(rank)  # e.g., "2" -> 2, "7" -> 7, etc.
