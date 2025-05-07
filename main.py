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
    rounds_count = []
    games = []
    num_players = 1
    num_games = 1
    bet_size = 25
    num_rounds = 100
    win_count_matrix = np.zeros((10, 35))
    profit_count_matrix = np.zeros((10, 35))
    total_count_matrix = np.zeros((10, 35))
    total_profit_matrix = np.zeros((10, 35))

    for _ in range(num_games):
        game = Game(num_decks=6, num_players=num_players, strategy=StrategyTable["MULTIDECK"], hit_on_soft_17=True, blackjack_payout=BLACKJACKTHREETOTWOPAYOUT, min_bet=bet_size, denominations=100, player_bankroll=0, resplit_till=4)
        for player in game.players:
            player.ace_five_counting = True
            player.high_low_counting = False
        round_data, round_count_data = game.play(num_rounds, print_cards=False, print_round_results=False)
        rounds_count.extend(round_count_data)
        rounds.extend(round_data)
        games.append(game.house_bankroll)
        win_count_matrix += game.win_count_matrix
        profit_count_matrix += game.profit_count_matrix
        total_count_matrix += game.total_count_matrix
        total_profit_matrix += game.total_profit_matrix

    # win_percentage_matrix = np.divide(win_count_matrix, total_count_matrix, out=np.zeros_like(win_count_matrix), where=total_count_matrix != 0)
    # print(win_percentage_matrix[:, 17:25])
    # print("total_profit_matrix")
    # for row in total_profit_matrix:
    #     print(" ".join(f"{value:2.0f}" for value in row))
    # print(total_profit_matrix[:, 24])
    # print("profit_count_matrix")
    # for row in profit_count_matrix:
    #     print(" ".join(f"{value:2.0f}" for value in row))
    # print(profit_count_matrix[:, 24])

    sum = 0
    wins = 0
    losses = 0
    pushes = 0
    for g in rounds:
        print(rounds_count)
        if g > 0:
            wins += 1
        elif g < 0:
            losses += 1
        else:
            pushes += 1
        sum += g
    print(sum)

    print(sum / num_players / num_games / num_rounds)
    print(f"Wins: {wins / num_rounds}, Losses: {losses / num_rounds}, Pushes: {pushes / num_rounds}")
    print()