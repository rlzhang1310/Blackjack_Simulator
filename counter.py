class Counter:
    def __init__(self):
        self.high_low_count = 0
        self.five_aces_count = 0

    def update_count(self, card):
        if card.rank in ["10", "J", "Q", "K", "A"]:
            self.high_low_count -= 1
        elif card.rank in ["2", "3", "4", "5", "6"]:
            self.high_low_count += 1

        if card.rank == "5":
            self.five_aces_count += 1
        elif card.rank == "A":
            self.five_aces_count -= 1

    def get_high_low_count(self):
        return self.high_low_count
    
    def get_five_aces_count(self):
        return self.five_aces_count
    
    def reset(self):
        self.high_low_count = 0
        self.five_aces_count = 0
        return