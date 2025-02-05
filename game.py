from deck import BlackjackShoe
from dealer import Dealer
from hand import Hand
from player import Player
from strategies.strategy import StrategyTable
from round import BlackjackRound

BLACKJACKTHREETOTWOPAYOUT = 1.5
BLACKJACKSIXTOFIVEPAYOUT = 1.2

class Game:
    def __init__(self, num_decks, num_players: int = 1, strategy=StrategyTable["MULTIDECK"], hit_on_soft_17=True, blackjack_payout=BLACKJACKTHREETOTWOPAYOUT, min_bet: int = 5, denominations=10):
        self.shoe = BlackjackShoe(num_decks)
        self.num_players = num_players
        self.players = [Player(name=f"Player {i}", strategy=strategy, bankroll=1000, hands=[Hand()]) for i in range(num_players)]
        # Dealer's hand
        self.dealer = Dealer(hit_on_soft_17=hit_on_soft_17, hand=Hand())
        self.blackjack_payout = blackjack_payout
        self.min_bet = min_bet
        self.denominations = denominations
        self.house_bankroll = min_bet * 10000

    def play_round(self):
        round = BlackjackRound(self.shoe, num_players=self.num_players)