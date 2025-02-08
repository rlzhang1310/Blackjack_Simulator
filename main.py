from deck import BlackjackShoe
from dealer import Dealer
from round import BlackjackRound
from hand import Hand
from game import Game, BLACKJACKSIXTOFIVEPAYOUT, BLACKJACKTHREETOTWOPAYOUT
from strategies.strategy import StrategyTable
import seaborn as sns
import numpy as np

if __name__ == "__main__":
    # game = Game(8, num_players=1, strategy=StrategyTable["MULTIDECK"], hit_on_soft_17=True, blackjack_payout=BLACKJACKTHREETOTWOPAYOUT, min_bet=10, denominations=10, player_bankroll=0)
    # data = game.play(100000, print_cards=False)

    # print(sns.displot(data, kind="kde"))

    rounds = []
    games = []  
    num_players = 5
    num_games = 1
    bet_size = 100
    num_rounds = 500
    for _ in range(num_games):
        game = Game(8, num_players=num_players, strategy=StrategyTable["MULTIDECK"], hit_on_soft_17=False, blackjack_payout=BLACKJACKTHREETOTWOPAYOUT, min_bet=bet_size, denominations=10, player_bankroll=0)
        round_data = game.play(num_rounds, print_cards=False, print_round_results=False)
        rounds.extend(round_data)
        games.append(game.house_bankroll)

    sum = 0
    for g in games:
        sum += g
    print(sum)

    print(sum / num_players / num_games / num_rounds)