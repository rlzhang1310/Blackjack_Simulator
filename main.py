from deck import BlackjackShoe
from dealer import Dealer
from round import BlackjackRound
from hand import Hand
from game import Game, BLACKJACKSIXTOFIVEPAYOUT, BLACKJACKTHREETOTWOPAYOUT
from strategies.strategy import StrategyTable

if __name__ == "__main__":
    game = Game(8, num_players=3, strategy=StrategyTable["MULTIDECK"], hit_on_soft_17=True, blackjack_payout=BLACKJACKTHREETOTWOPAYOUT, min_bet=10, denominations=10)
    game.play_one_round()
    # Create a BlackjackRound with 3 players, as an example

    # # Play the round and capture the results
    # results = round_game.play_round()

    # # Print the outcomes
    # print("=== Blackjack Round Results ===")
    # for outcome in results:
    #     print(outcome)