class Hand():
    def __init__(self, num_cards, soft, hand):
        self.num_cards = num_cards
        self.soft = soft
        self.hand = hand


    def evaluate(self):
        value_map = {
            "A": 1, "J": 10, "Q": 10, "K": 10,
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
            "7": 7, "8": 8, "9": 9, "10": 10
        }

        total = 0

        for rank, suit in self.hand:
            total += value_map[rank]
            if rank == "A":
                self.soft = True

        if total > 11:
            self.soft = False

        return total