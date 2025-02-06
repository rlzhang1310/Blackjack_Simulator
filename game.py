from deck import BlackjackShoe
from dealer import Dealer
from hand import Hand
from player import Player
from strategies.strategy import StrategyTable
from round import BlackjackRound

BLACKJACKTHREETOTWOPAYOUT = 1.5
BLACKJACKSIXTOFIVEPAYOUT = 1.2

class Game:
    def __init__(self, num_decks, num_players: int=1, strategy=StrategyTable["MULTIDECK"], hit_on_soft_17=True, blackjack_payout=BLACKJACKTHREETOTWOPAYOUT, min_bet: int=10, denominations=10, player_bankroll=0):
        self.shoe = BlackjackShoe(num_decks)
        self.num_decks = num_decks  # Number of decks in the shoe
        self.num_players = num_players
        self.players = [Player(name=f"Player {i}", strategy=strategy, bankroll=player_bankroll, hands=[Hand()]) for i in range(num_players)]
        self.dealer = Dealer(hit_on_soft_17=hit_on_soft_17, hand=Hand())
        self.blackjack_payout = blackjack_payout
        self.min_bet = min_bet
        self.denominations = denominations
        self.house_bankroll = min_bet * 10000

    def play(self, games=10, print_round_results=False, print_cards=False):
        data_collector = []
        for _ in range(games):
            for player in self.players:
                player.new_hand()
                player.put_bet_on_initial_hand(self.min_bet)
            self.dealer.new_hand()
            round = BlackjackRound(self.shoe, players=self.players, dealer=self.dealer, blackjack_payout=self.blackjack_payout, print_cards=print_cards)
            results = round.play_round()
            self.house_bankroll += round.dealer_profit
            data_collector.append(round.dealer_profit)
            if self.shoe.reshuffle_needed:
                self.shoe = BlackjackShoe(self.num_decks) 
            if print_round_results:
                print("=== Blackjack Round Results ===")
                for outcome in results:
                    print(outcome)
        
        print(f"=== Results After {games} Games ===")
        for player in self.players:
            print(f"{player.name}: ${player.bankroll}")
        print(f"House Bankroll: ${self.house_bankroll}")
        print(f"Cards Left: {self.shoe.cut_index - self.shoe.deal_index}")
        return data_collector