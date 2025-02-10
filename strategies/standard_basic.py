# Actions: H=Hit, S=Stand, D=Double, P=Split
# We’ll interpret them in code so that "D" might become "DOUBLE" 
# only if the player can indeed double (2 cards, etc.). Otherwise we fallback to "HIT".

# 2.1.1 Pair Actions
PAIR_ACTIONS = {
    # Format: (rank, rank) or ('T','T') for 10-value
    ('A','A'): { 'ANY': 'P' },  # Always split
    ('8','8'): { 'ANY': 'P' },  # Always split
    ('9','9'): { 2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 8: 'P', 9: 'P', 'DEFAULT': 'S' },
    ('7','7'): { 2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 'DEFAULT': 'H' },
    ('6','6'): { 2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 'DEFAULT': 'H' },
    ('5','5'): { 'ANY': None },  # We'll handle 5,5 in HARD totals
    ('4','4'): { 'ANY': None },  # Rarely split in multi-deck
    ('3','3'): { 2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 'DEFAULT': 'H' },
    ('2','2'): { 2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 'DEFAULT': 'H' },
    ('T','T'): { 'ANY': 'S' },  # 10/J/Q/K => never split
}

# 2.1.2 Soft Totals (A = 11 included)
# Key = player total (13 to 20)
# Value = dictionary of dealer upcard => action
SOFT_ACTIONS = {
    13: { 'ALL': 'H' },  # Soft 13 => always HIT
    14: { 'ALL': 'H' },  # Soft 14 => always HIT
    15: { 'ALL': 'H' },  # Soft 15 => always HIT
    16: { 4: 'D', 5: 'D', 6: 'D', 'DEFAULT': 'H' },  # Soft 16 => double vs 4-6, else HIT
    17: { 3: 'D', 4: 'D', 5: 'D', 6: 'D', 'DEFAULT': 'H' },
    18: { 2: 'S', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'S', 8: 'S', 'DEFAULT': 'H' },
    19: { 6: 'D', 'DEFAULT': 'S' },
    20: { 'ALL': 'S' },  # Soft 20 => always STAND
    21: { 'ALL': 'S' },  # Soft 21 => always STAND
}

# 2.1.3 Hard Totals
# Key = total (5..17+)
HARD_ACTIONS = {
    5:  { 'ALL': 'H' },
    6:  { 'ALL': 'H' },
    7:  { 'ALL': 'H' },
    8:  { 'ALL': 'H' },
    9:  { 3: 'D', 4: 'D', 5: 'D', 6: 'D', 'DEFAULT': 'H' },
    10: { 2: 'D', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'D', 8: 'D', 9: 'D', 'DEFAULT': 'H' },
    11: { 11: 'H', 'DEFAULT': 'D' },
    12: { 4: 'S', 5: 'S', 6: 'S', 'DEFAULT': 'H' },
    13: { 2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 'DEFAULT': 'H' },
    14: { 2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 'DEFAULT': 'H' },
    15: { 2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 'DEFAULT': 'H' },
    16: { 2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S', 'DEFAULT': 'H' },
    17: { 'ALL': 'S' },  # 17+ => always stand
}

STRATEGY_DICT = {"PAIR": PAIR_ACTIONS, "SOFT": SOFT_ACTIONS, "HARD": HARD_ACTIONS}