from deck import BlackjackShoe
from dealer import Dealer
from round import BlackjackRound
from hand import Hand

if __name__ == "__main__":
    shoe = BlackjackShoe(num_decks=8)

    # Create a BlackjackRound with 3 players, as an example
    round_game = BlackjackRound(shoe=shoe, num_players=3)

    # Play the round and capture the results
    results = round_game.play_round()

    # Print the outcomes
    print("=== Blackjack Round Results ===")
    for outcome in results:
        print(outcome)