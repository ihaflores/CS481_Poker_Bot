from pokerkit import *

# Set up the initial game state
state = NoLimitTexasHoldem.create_state(
    # Automations
    (
        Automation.ANTE_POSTING,
        Automation.BET_COLLECTION,
        Automation.BLIND_OR_STRADDLE_POSTING,
        Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        Automation.HAND_KILLING,
        Automation.CHIPS_PUSHING,
        Automation.CHIPS_PULLING,
    ),
    False,  # False for big blind ante
    0, # ante
    (200, 400), # Small and big blinds
    400, # big bet
    (10000, 10000, 10000), # Starting chips for each player
    3 # Set the number of players
)

players = [x for x in state.player_indices]
folded_players = set() # set to track what players have folded
small_blind_idx = 0 # start with first player as the small blind
big_blind_idx = small_blind_idx  + 1 # big blind is to left of small blind
starting_player_idx = big_blind_idx + 1 # starting player is player to left of big blind
curr_player_idx = starting_player_idx # current player begins as the starting player

# Deal the initial hole cards to all players in sequence, one at a time
for player in range(state.player_count * 2):
    state.deal_hole()

def is_folded(player):
    if player in folded_players:
        return True
    return False

def player_action(player):
    """Prompt player for an action."""
    hand = tuple(state.get_down_cards(player))
    print(f"Pot: {state.total_pot_amount} | Player {player}'s Stack: {tuple(state.stacks)[player]}")
    print(f"Player {player}'s turn with {tuple(state.get_down_cards(player))}")
    print(f"Board Cards: {tuple(state.get_board_cards(0))}")

    while True:
        action = input("Choose action: check, call, bet, raise, fold: ").strip().lower()
        print(f"\n")
        if action == "check":
            state.check_or_call()
        elif action == "call":
            state.check_or_call()
        elif action == "bet":
            amount = int(input("Enter bet amount: "))
            state.complete_bet_or_raise_to(amount)
        elif action == "raise":
            amount = int(input("Enter raise amount: "))
            state.complete_bet_or_raise_to(amount)
        elif action == "fold":
            folded_players.add(player)
            state.fold()
        else:
            print(f"Please input a valid action")
            continue
        break
        

def get_next_player():
    """Find the next active player in turn order."""
    global curr_player_idx
    while True:
        curr_player_idx = (curr_player_idx + 1) % len(players)
        if not is_folded(curr_player_idx):
            break
    return players[curr_player_idx]

def get_player_hand(player):
    board_cards_tuple = tuple(state.get_board_cards(0))
    player_cards_tuple = tuple(state.hole_cards[player])
    board_cards = ""
    player_cards = ""

    value_map = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    suit_map = {'h': 'h', 'd': 'd', 'c': 'c', 's': 's'}

    for card in board_cards_tuple:
        value_str = value_map.get(card.rank, str(card.rank))  # Get face card or numeric value
        suit_str = suit_map[card.suit]                        # Get suit character
        board_cards += value_str + suit_str
    for card in player_cards_tuple:
        value_str = value_map.get(card.rank, str(card.rank))  # Get face card or numeric value
        suit_str = suit_map[card.suit]                        # Get suit character
        player_cards += value_str + suit_str
    hand = StandardHighHand.from_game(player_cards, board_cards)
    return hand

def get_player_hole_cards(player):
    player_cards_tuple = tuple(state.hole_cards[player])
    player_cards = ""

    value_map = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    suit_map = {'h': 'h', 'd': 'd', 'c': 'c', 's': 's'}
    for card in player_cards_tuple:
        value_str = value_map.get(card.rank, str(card.rank))  # Get face card or numeric value
        suit_str = suit_map[card.suit]                        # Get suit character
        player_cards += value_str + suit_str
    return player_cards

def get_board_cards():
    board_cards_tuple = tuple(state.get_board_cards(0))
    board_cards = ""

    value_map = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    suit_map = {'h': 'h', 'd': 'd', 'c': 'c', 's': 's'}

    for card in board_cards_tuple:
        value_str = value_map.get(card.rank, str(card.rank))  # Get face card or numeric value
        suit_str = suit_map[card.suit]                        # Get suit character
        board_cards += value_str + suit_str
    return board_cards

def find_winner():
    # Evaluate each player's hand and determine the winner
    best_hand = None
    winning_player = None

    print("\nFinal hands:")
    print(f"Board Cards: {tuple(state.get_board_cards(0))}\n")

    for player in state.player_indices:
        if is_folded(player): # Skip folded players
            continue

        # display player's hole cards
        print(f"Player {player}: {tuple(state.get_down_cards(player))}\n")

        # Get the player's hand rank
        hand = get_player_hand(player)
        print(f"Player {player} hand rank: {hand}")

        # Determine the highest-ranked hand
        if best_hand is None or hand > best_hand:
            best_hand = hand
            winning_player = player

    print(f"The winner is Player {winning_player} with a hand rank of {best_hand}.")

# Game rounds
for stage in ["pre-flop", "flop", "turn", "river"]:
    print(f"\n{stage.capitalize()} round:")
    
    if stage == "flop":
        state.burn_card()
        state.deal_board(3)  # Deal three community cards for the flop
    elif stage == "turn" or stage == "river":
        state.burn_card()
        state.deal_board(1)  # Deal one community card for turn and river

    for _ in range(len(players) - len(folded_players)):
        current_player = players[curr_player_idx]
        if is_folded(current_player):
            current_player = get_next_player()
        
        board_cards = get_board_cards()
        player_hole_cards = get_player_hole_cards(current_player)

        hand_strength = calculate_hand_strength(
            state.player_count, # Number of players
            parse_range(player_hole_cards), # Hole cards
            Card.parse(board_cards), # Board cards
            2,
            5,
            Deck.STANDARD,
            (StandardHighHand, ),
            sample_count=1000,
        )

        print(f"Player {current_player} hand strength: {hand_strength}")

        player_action(current_player)

        # Move to the next player
        current_player = get_next_player()

# winner is remaining hand, find index of remaining hole cards
winner = -1
for player_idx in range(len(state.statuses)):
    if state.statuses[player_idx] is True:
        winner = player_idx
winning_hand = get_player_hand(winner)

print(f"The winner is Player {winner}!")
print(f"Winning Hand: {winning_hand}")