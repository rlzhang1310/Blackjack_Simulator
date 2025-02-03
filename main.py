from deck import BlackjackShoe 

if __name__ == "__main__":
    bj_shoe = BlackjackShoe(num_decks=8, cut_penetration=0.75)
    # Deal a few cards:
    for _ in range(10):
        print(bj_shoe.deal_card())