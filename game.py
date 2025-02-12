from deck import BlackjackShoe
from dealer import Dealer
from hand import Hand
from player import Player
from strategies.strategy import StrategyTable
from round import BlackjackRound
from collections import defaultdict
from counter import Counter

BLACKJACKTHREETOTWOPAYOUT = 1.5
BLACKJACKSIXTOFIVEPAYOUT = 1.2

class Game:
    def __init__(self, num_decks, num_players: int=1, strategy=StrategyTable["MULTIDECK"], hit_on_soft_17=True, resplit_till=4, blackjack_payout=BLACKJACKTHREETOTWOPAYOUT, min_bet: int=10, denominations=10, player_bankroll=0):
        # self.shoe = BlackjackShoe(num_decks)
        self.shoe = BlackjackShoe(num_decks)
        self.num_decks = num_decks  # Number of decks in the shoe
        self.num_players = num_players
        self.players = [Player(name=f"Player {i}", strategy=strategy, bankroll=player_bankroll, hands=[Hand()], min_bet=min_bet, denominations=denominations) for i in range(num_players)]
        self.dealer = Dealer(hit_on_soft_17=hit_on_soft_17, hand=Hand())
        self.resplit_till = resplit_till
        self.blackjack_payout = blackjack_payout
        self.min_bet = min_bet
        self.denominations = denominations
        self.house_bankroll = 0
        self.counter = Counter()
        # [TODO] implement total number of splits

    def play(self, games=10, print_round_results=False, print_cards=False):
        data_collector = []

        # bust = defaultdict(int) # dictionary to keep track of number of times a dealer busts
        # total = defaultdict(int) # dictionary to keep track of number of times a dealer showed a suit
        # blackjacks = 0  # Counter for number of blackjacks in the game
        for _ in range(games):
            high_low_true_count = self.get_estimated_high_low_true_count()
            five_aces_true_count = self.get_estimated_five_aces_true_count()
            for player in self.players:
                player.new_hand()
                player.put_bet_on_initial_hand(high_low_true_count, five_aces_true_count)
            self.dealer.new_hand()
            round = BlackjackRound(self.shoe, players=self.players, dealer=self.dealer, blackjack_payout=self.blackjack_payout, print_cards=print_cards ,resplit_till=self.resplit_till, counter=self.counter)
            results = round.play_round()
            self.house_bankroll += round.dealer_profit
            data_collector.append(round.dealer_profit)
            if self.shoe.reshuffle_needed:
                # print(self.counter.get_high_low_count())
                # print(self.shoe.cards[self.shoe.deal_index:])
                self.counter = Counter()                
                self.shoe = BlackjackShoe(self.num_decks) 
            if print_round_results:
                print("=== Blackjack Round Results ===")
                for outcome in results:
                    print(outcome)
            # blackjacks += round.blackjack_counter
            # for key, value in round.bust_dict.items():
            #     bust[key] += value
            # for key, value in round.total_dict.items():
            #     total[key] += value

        
        print(f"=== Results After {games} Games ===")
        for player in self.players:
            print(f"{player.name}: ${player.bankroll}")
        print(f"House Bankroll: ${self.house_bankroll}")
        print(f"Cards Left: {len(self.shoe.cards) - self.shoe.deal_index}")
        print(f"Decks Left: {self.shoe.decks_left()}")
        # print(f"Player Blackjacks: {blackjacks / games}")
        # print(f"bust percentage for each rank")
        # for rank in sorted(total.keys()):
        #     print(f"{rank}: {bust[rank] / total[rank]}")
        return data_collector
    

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