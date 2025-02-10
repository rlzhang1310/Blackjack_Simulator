import unittest
from deck import BlackjackShoe, Card, create_single_deck, create_shoe, shuffle_shoe
from dealer import Dealer
from hand import Hand
from player import Player
from strategies.strategy import StrategyTable
from round import BlackjackRound
from game import Game
from counter import Counter

class TestBlackjackGame(unittest.TestCase):

    def setUp(self):
        """
        Initialize the basic game setup for all tests.
        """
        # Create a 2-deck shoe for testing (or any number of decks you like)
        self.shoe = BlackjackShoe(num_decks=2)

        # Create a dealer with the standard hit-on-soft-17 rule
        self.dealer = Dealer(hit_on_soft_17=True, hand=Hand())

        # Create a strategy for testing (simple strategy or basic strategy)
        self.strategy = StrategyTable["MULTIDECK"]  # Assuming this is a valid strategy

        # Create a player with an empty bankroll
        self.player = Player(name="Test Player", strategy=self.strategy, bankroll=1000, hands=[Hand()])

        # Initialize round instance
        self.round = BlackjackRound(shoe=self.shoe, players=[self.player], dealer=self.dealer, blackjack_payout=1.5, print_cards=True, counter=Counter(), resplit_till=4)

    def test_split(self):
        """
        Test the case where the player is dealt a pair and chooses to split.
        """
        # Player receives a pair of 8s
        self.player.hands[0] = Hand()  # Create a new hand for the player
        self.player.hands[0].put_initial_bet(10)  # Player bets 10
        self.player.hands[0].add_card(Card("8", "Hearts"))
        self.player.hands[0].add_card(Card("8", "Spades"))
        self.player.hands[0].evaluate() 
        # Player decides to split
        self.round._player_turn(self.player, self.dealer.hand.cards[1])  # Dealer upcard
        
        # Check if player now has two hands
        self.assertEqual(len(self.player.hands), 2)

        # Check if both hands got a new card
        self.assertGreaterEqual(len(self.player.hands[0].cards), 2)
        self.assertGreaterEqual(len(self.player.hands[1].cards), 2)

    def test_dealer_hits_on_soft_17(self):
        """
        Test the dealer's behavior when they have a soft 17 and hit_on_soft_17 is True.
        """
        # Dealer gets A + 6 (soft 17)
        self.dealer.hand = Hand()  # Create a new hand for the player
        self.dealer.hand.add_card(Card("A", "Clubs"))
        self.dealer.hand.add_card(Card("6", "Diamonds"))
        self.dealer.hand.evaluate() 

        # Simulate the dealer's turn
        self.dealer.dealer_turn(self.shoe, self.round.counter)

        # Assert the dealer hits until they have 17 or more
        self.assertGreaterEqual(self.dealer.hand.value, 17)
        self.assertNotEqual(self.dealer.hand.value, 18)  # Because it's a soft 17, they should hit

    def test_blackjack_payout(self):
        """
        Test the blackjack payout logic for both the dealer and the player.
        """
        # Player gets A + 10 (Blackjack)
        self.player.hands[0] = Hand()  # Create a new hand for the player
        self.player.hands[0].put_initial_bet(10)  # Player bets 10
        self.player.hands[0].add_card(Card("A", "Clubs"))
        self.player.hands[0].add_card(Card("10", "Diamonds"))
        self.player.hands[0].evaluate() 

        # Dealer gets A + 9 (not Blackjack)
        self.dealer.hand = Hand()
        self.dealer.hand.add_card(Card("A", "Hearts"))
        self.dealer.hand.add_card(Card("9", "Spades"))
        self.dealer.hand.evaluate() 

        # Simulate the round (dealer and player will act based on their hand)
        results = self.round.play_round()

        # Check if the player gets the correct payout
        self.assertIn('Test Player Hand 1 has BLACKJACK', results[0])  # Player should win with blackjack
        self.assertEqual(-15, self.round.dealer_profit)

    def test_bust(self):
        """
        Test the case where the player busts and the dealer busts.
        """
        # Player's hand: 10, 10, 10 (bust)
        self.player.hands[0] = Hand()  # Create a new hand for the player
        self.player.hands[0].put_initial_bet(10)
        self.player.hands[0].add_card(Card("10", "Hearts"))
        self.player.hands[0].add_card(Card("10", "Clubs"))
        self.player.hands[0].add_card(Card("10", "Diamonds"))
        self.player.hands[0].evaluate() 
        # Dealer's hand: 10, 10, 5 (bust)
        self.dealer.hand = Hand()
        self.dealer.hand.add_card(Card("10", "Spades"))
        self.dealer.hand.add_card(Card("10", "Hearts"))
        self.dealer.hand.add_card(Card("5", "Diamonds"))
        self.dealer.hand.evaluate() 

        # Simulate the round (dealer and player will act based on their hand)
        results = self.round.play_round()

        # Check that the player loses and the dealer wins
        self.assertIn(f"{self.player.name} Hand 1 lost", results[0])
        self.assertIn("Dealer wins", results[0])

    def test_max_splits(self):
        """
        Test that a player can split up to 3 times (4 total hands) and no further.
        """
        # Override the shoe to force splits (pre-load with 8s to allow repeated splits)
        eight_of_hearts = Card("8", "Hearts")
        eight_of_spades = Card("8", "Spades")

        
        # Rig the shoe to deal 8s for splits (enough for 3 splits)
        self.round.shoe.shoe = [
            Card("8", "Hearts"), Card("8", "Spades"),  # Initial player hand
            Card("8", "Clubs"), Card("8", "Diamonds"),  # First split cards
            Card("8", "Hearts"), Card("8", "Spades"),  # Initial player hand
            Card("8", "Clubs"), Card("8", "Diamonds"),  # First split cards
            Card("8", "Hearts"), Card("8", "Spades"),  # Initial player hand
            Card("8", "Clubs"), Card("8", "Diamonds"),  # First split cards
            Card("8", "Hearts"), Card("8", "Spades"),  # Initial player hand
            # Add non-8 cards afterward to avoid infinite splits
            Card("2", "Hearts"), Card("3", "Hearts")
        ]
        self.shoe.deal_index = 0
        # for card in self.shoe.shoe:
        #     print(card)


        # Set dealer's upcard to 6 (to encourage splitting)
        dealer_upcard = Card("6", "Diamonds")
        self.dealer.hand.add_card(dealer_upcard)

        # Player starts with two 8s (splittable hand)
        self.player.hands[0] = Hand()
        self.player.hands[0].put_initial_bet(10)
        self.player.hands[0].add_card(eight_of_hearts)
        self.player.hands[0].add_card(eight_of_spades)
        self.player.hands[0].evaluate()

        # Player's turn: split as many times as allowed (3 splits → 4 hands)
        self.round._player_turn(self.player, dealer_upcard)

        # Assert 4 hands exist after 3 splits
        self.assertEqual(len(self.player.hands), 4, "Player should have 4 hands after 3 splits")

        # Verify each hand has exactly 2 cards
        for hand in self.player.hands:
            self.assertEqual(len(hand.cards), 2, "Each split hand should have 2 cards")

    def test_count(self):
        counter = Counter()
        shoe = create_shoe()
        shuffle_shoe(shoe)
        for card in shoe:
            counter.update_count(card)

        self.assertEqual(counter.get_high_low_count(), 0)

if __name__ == "__main__":
    unittest.main()
