# Blackjack_Simulator
Simulation for Blackjack to find EV

To use, go to main.py and input the parameters to simulate the number of rounds you wanted to simulate
Currently, only Ace-Five and standard High-Low counting is implemented

Ideas to implement:
- Data visualization
    - Visualization of winrates per hand state
    - Graphs that show the risk of ruin throughout number of hands
    - Graphs that show the chances of positive profit throughout rounds
    - Graphs that visualize the variance throughout rounds
- Parallel Processing for multiple games at the same time
- Function to find mathematically correct action given cards left in the deck (has to be efficient for simulation performance)
- Front End website
- Functioning interactive player added, as well as showing the count and correct action afterwards
- Figure out counting way to incorporate side bets like 777s