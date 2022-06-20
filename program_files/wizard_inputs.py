import numpy as np

from program_files.colored_text import colored_text as colored
from program_files.colored_text import print_color_index
from program_files.wizard_card import Wizard_Card
from program_files.wizard_game_state import Wizard_Game_State


def get_action_input(
        game: Wizard_Game_State) -> Wizard_Card:
    """
    get an input from player `player`
    """
    # automatically choose move if the player has only one card
    player_index = game.trick_active_player
    hand = game.players_hands[player_index]
    if len(hand) == 1:
        return hand[0]
    print("\n", "-" * 60, "\n", sep="")
    # request input until a valid action is chosen
    input(
        f"please confirm presence of player P{player_index + 1} (press any button)\n")
    action_invalid = True
    while action_invalid:
        print("choose a card to play from your hand:")
        print(hand)
        action = __action_input(hand)
        if action is None:
            continue
        action_invalid = check_action_invalid(action, hand, game.serving_color)
    return action


def __action_input(hand: list) -> Wizard_Card:
    """
    get an input from a player representing a card.
    """
    user_input = input(
        f"specify input as color ({print_color_index(0)},{print_color_index(1)},{print_color_index(2)},{print_color_index(3)}) and value (0-14) or ({colored('W', '#dddddd')}, {colored('J', '#dddddd')})\n")
    upper_input = user_input.strip(" ").upper()
    # check jester
    if upper_input in ("J", "N", "0"):
        for card in hand:
            if card.value == 0:
                return card
        print("no jester found in hand")
        return None
    # check wizard
    if upper_input in ("W", "Z", "14"):
        for card in hand:
            if card.value == 14:
                return card
        print("no wizard found in hand")
        return None
    # check other cards
    split_input = user_input.split(" ")
    if len(split_input) != 2:
        print(len(split_input))
        print("invalid input")
        return None
    color, value = split_input
    try:
        value = int(value)
    except ValueError:
        print("value should be an integer in (0,14)")
        return None
    try:
        color_to_index = {"R": 0, "Y": 1, "G": 2, "B": 3}
        color = color_to_index[color.upper()]
    except KeyError:
        print("color not understood")
        return None

    for card in hand:
        if card.color == color and card.value == value:
            return card
    print("card not found in hand")
    return None


def get_predictions(game: Wizard_Game_State, round_nbr: int, limit_choices: bool = False):
    """
    get predicted number of tricks from each player

    inputs:
    -------
        round_nbr (int): number of the current round in [1,20]
    """
    predictions = np.zeros(game.n_players, dtype=np.int8)
    for player_index in range(game.round_starting_player, game.round_starting_player + game.n_players):
        player_index = player_index % game.n_players
        # get console input from player
        print("\n", "-" * 60, "\n", sep="")
        while True:
            print(f"The trump card is: {game.trump_card}, trump color is: {print_color_index(game.trump_color)}")
            print("your hand:")
            print(game.players_hands[player_index])
            player_input = input(
                f"Player P{player_index+1}, please enter the number of tricks you expect to win.\n")
            try:
                # convert input to integer
                int_input = int(player_input.strip(" "))
                predictions[player_index] = int_input
                # check that sum of predictions is not equal to round number
                if limit_choices \
                        and player_index == (game.round_starting_player - 1) % game.n_players \
                        and np.sum(predictions) == round_nbr:
                    print(f"You cannot choose {int_input} tricks.")
                    continue
                break
            except ValueError:
                print(f"input {player_input} rejected")
                continue
    return predictions


def check_action_invalid(action, hand, serving_color):
    """
    check whether or not a given action is valid.
    """
    # check if the player had the played card
    if not action in hand:
        return True
    # check whether card is jester or wizard
    if action.value in [0, 14]:
        return False
    # check whether the color is serving color
    if action.color != serving_color:
        for card in hand:
            if card.color == serving_color:  # player had to serve
                return True
    return False


def trump_color_input(player_index: int, hand: list) -> int:
    """
    ask player `player_index` for a trump color for the current round.

    inputs:
    -------
        player_index (int) - index of the player that gave the cards for the round.
            note that player indices start at 0
    """
    input(
        f"please confirm presence of player P{player_index + 1} (press any button)\n")
    while True:
        print("your hand is:")
        print(hand)
        trump_input = input(
            f"Player P{player_index+1}: please choose a trump color\n")
        upper_input = trump_input.strip(" ").upper()
        if upper_input in ("R", "RED", "0"):
            return 0
        if upper_input in ("Y", "YELLOW", "1"):
            return 1
        if upper_input in ("G", "GREEN", "2"):
            return 2
        if upper_input in ("B", "BLUE", "3"):
            return 3
