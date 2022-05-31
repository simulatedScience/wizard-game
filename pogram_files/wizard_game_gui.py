import tkinter as tk
import time

import numpy as np

from pogram_files.wizard_card import Wizard_Card
from pogram_files.wizard_game_state import Wizard_Game_State
# from pogram_files.wizard_menu_gui import Wizard_Menu_Gui # only imported for type hints
from pogram_files.wizard_functions import get_hands, check_action_invalid
# imports for AI
from pogram_files.wizard_ais.wizard_ai_classes import ai_classes, ai_trump_chooser_methods, ai_bids_chooser_methods, ai_trick_play_methods


class Wizard_Game_Gui():
  def __init__(self,
               wizard_menu: "Wizard_Menu_Gui",
               n_players: int,
               limit_choices: bool,
               max_rounds: int,
               ai_player_types: list,
               sleep_times: dict = {
                   "end_of_trick_delay": 0.2,
                   "end_of_round_delay": 0.8}):
    """
    create a gui that handles playing a game of wizard with the given settings

    inputs:
    -------
      wizard_menu (Wizard_Menu_Gui): The menu gui object provides the frame where the game is displayed and style settings from the menu gui are used.
      n_players (int): number of players in the game
      limit_choices (bool): whether or not to allow the number of bids can equal the number of tricks
      max_rounds (int): number of rounds to be played
      ai_player_choices (list) of (dict): settings for player names and whether to use AI to calculate actions during the game.
      sleep_times (dict): setting for delays before moving on to the next section of the game.
        should contain two keys: `'end_of_trick_delay'` and `'end_of_round_delay'`.
        values are sleeptimes in seconds.
    """
    self.wizard_menu = wizard_menu
    self.n_players = n_players
    self.limit_choices = limit_choices
    self.n_rounds = min(max_rounds, 60 // self.n_players) + 1
    self.ai_player_types = ai_player_types

    self.end_of_trick_delay = sleep_times["end_of_trick_delay"]  # in seconds
    self.end_of_round_delay = sleep_times["end_of_round_delay"]  # in seconds
    self.card_width = 160
    self.card_height = 240

    self.master_window = self.wizard_menu.master_window
    self.gui_colors = self.wizard_menu.gui_colors

    self.card_color_to_str = {
        0: "red",
        1: "yellow",
        2: "green",
        3: "blue",
        -1: "white"}

    self._open_game_window()


  def _open_game_window(self):
    """
    create all Tkinter widgets on the game window to enable play.
    """
    self.main_game_frame = tk.Frame(
        master=self.master_window,
        bg=self.gui_colors["bg"])
    self.main_game_frame.place(
        anchor="c",
        relx=.5,
        rely=.5)
    self.main_game_frame.grid_columnconfigure(0, weight=1)
    self.main_game_frame.grid_rowconfigure(0, weight=1)

    def close_game(_):
      """
      close game frame and reopen the menu.
      """
      self.main_game_frame.destroy()
      self.wizard_menu.open_main_window()
      self.master_window.unbind("<Escape>")
    self.master_window.bind("<Escape>", close_game)
    row_index = 0
    # `played_cards_frame` shows which card each player played in a trick and highlights the winning card. Also shows player names and how many tricks they predicted as well as how many they already won
    self.played_cards_frame = tk.Frame(
        master=self.main_game_frame,
        bg=self.gui_colors["bg"])
    # bg="#ff00ff")
    self.played_cards_frame.grid(
        sticky="nsew",
        row=row_index,
        column=0,
        rowspan=2,
        padx=(0, 20),
        pady=(0, 20))
    # `trump_frame` shows the current trump card and color
    self.trump_frame = tk.Frame(
        master=self.main_game_frame,
        bg=self.gui_colors["bg"])
    self.trump_frame.grid(
        sticky="se",
        row=row_index,
        column=1,
        padx=20,
        pady=(0, 20))
    # `round_info_frame` shows how many tricks are available, how many were predicted and the current round_number
    self.round_info_frame = tk.Frame(
        master=self.main_game_frame,
        bg=self.gui_colors["bg"])
    self.round_info_frame.grid(
        sticky="nw",
        row=row_index + 1,
        column=1,
        padx=20,
        pady=20)
    # `players_points_frame` shows intermediate and final scores for each player
    self.players_points_frame = tk.Frame(
        master=self.main_game_frame,
        bg=self.gui_colors["card_color"])
    self.players_points_frame.grid(
        sticky="nw",
        row=row_index,
        column=2,
        rowspan=3,
        padx=20,
        pady=(0, 20))
    row_index += 2

    self.players_hand_frame = tk.Frame(
        master=self.main_game_frame,
        bg=self.gui_colors["bg"])
    self.players_hand_frame.grid(
        sticky="nw",
        row=row_index,
        column=0,
        columnspan=2,
        padx=(0, 20),
        pady=(20, 0))

    # # planned feature: log everything that happens in the game
    # self.event_log_frame = tk.Frame(
    #     master=self.main_game_frame,
    #     bg=self.gui_colors["bg"])
    # self.event_log_frame.grid(
    #     sticky = "nw",
    #     row = row_index,
    #     column = 0,
    #     columnspan = 2,
    #     padx = (0, 20),
    #     pady = (20, 0))

    self._fill_trump_frame()
    self._fill_round_info_frame()
    self._fill_players_points_frame()
    self.master_window.update()
    self._start_game()


  def _fill_trump_frame(self):
    """
    create required frames and labels inside `self.trump_frame`
    """
    trump_color_label = tk.Label(
        master=self.trump_frame,
        text="Trump\ncolor:")
    self.wizard_menu.add_label_style(trump_color_label)
    trump_color_label.grid(
        sticky="sw",
        row=0,
        column=0,
        padx=(0, 5),
        pady=0)

    self.trump_color_frame = tk.Frame(
        master=self.trump_frame,
        bg=self.gui_colors["white"],
        highlightbackground=self.gui_colors["card_color"],
        highlightthickness=5,
        width=56,
        height=87)
    self.trump_color_frame.grid(
        sticky="sw",
        row=1,
        column=0,
        padx=5,
        pady=10)

    self.trump_card_frame = tk.Frame(
        master=self.trump_frame,
        bg=self.gui_colors["card_color"],
        highlightbackground=self.gui_colors["card_border"],
        highlightthickness=5,
        width=self.card_width,
        height=self.card_height)
    self.trump_card_frame.grid_propagate(False)
    self.trump_card_frame.grid(
        sticky="sw",
        row=0,
        rowspan=2,
        column=1,
        padx=(0, 10),
        pady=(0, 10))


  def _fill_round_info_frame(self):
    """
    create required labels and variables inside `self.round_info_frame`
    """
    bids_tricks_label = tk.Label(
        master=self.round_info_frame,
        text="Bids / Tricks:")
    self.wizard_menu.add_label_style(bids_tricks_label)
    bids_tricks_label.grid(
        sticky="sw",
        row=0,
        column=0,
        padx=(0, 5),
        pady=(0, 5))

    self.n_bids = tk.IntVar(self.round_info_frame, value=0)
    bids_indicator_label = tk.Label(
        master=self.round_info_frame,
        textvariable=self.n_bids)
    self.wizard_menu.add_label_style(bids_indicator_label)
    bids_indicator_label.grid(
        sticky="sw",
        row=0,
        column=1,
        padx=5,
        pady=(0, 5))

    bids_tricks_seperator_label = tk.Label(
        master=self.round_info_frame,
        text="/")
    self.wizard_menu.add_label_style(bids_tricks_seperator_label)
    bids_tricks_seperator_label.grid(
        sticky="sw",
        row=0,
        column=2,
        padx=5,
        pady=(0, 5))

    self.n_tricks = tk.IntVar(self.round_info_frame, value=1)
    tricks_indicator_label = tk.Label(
        master=self.round_info_frame,
        textvariable=self.n_tricks)
    self.wizard_menu.add_label_style(tricks_indicator_label)
    tricks_indicator_label.grid(
        sticky="sw",
        row=0,
        column=3,
        padx=(5, 0),
        pady=(0, 5))

    round_label = tk.Label(
        master=self.round_info_frame,
        text="Round number:")
    self.wizard_menu.add_label_style(round_label)
    round_label.grid(
        sticky="sw",
        row=1,
        column=0,
        padx=(0, 5),
        pady=(5, 0))

    self.round_nbr = tk.IntVar(self.round_info_frame, value=1)
    round_indicator_label = tk.Label(
        master=self.round_info_frame,
        textvariable=self.round_nbr)
    self.wizard_menu.add_label_style(round_indicator_label)
    round_indicator_label.grid(
        sticky="sw",
        row=1,
        column=1,
        padx=(5, 0),
        pady=(5, 0))


  def _fill_players_points_frame(self):
    """
    create labels to show player points
    """
    # create player indicators as headline
    for player_index in range(self.n_players):
      player_label = tk.Label(
          master=self.players_points_frame,
          width=7,
          bg=self.gui_colors["card_color"],
          fg=self.gui_colors["white"],
          text=self.ai_player_types[player_index]["player_name_var"],
          font=("bold", "12", ""))
      player_label.grid(
          sticky="s",
          row=0,
          column=2 * player_index + 1,
          columnspan=2,
          padx=5,
          pady=(10, 5))
    # create labels for all predictions (bids) during the game
    self.bids_label_matrix = [
        [tk.Label(
            master=self.players_points_frame,
            width=2,
            bg=self.gui_colors["white"],
            font=("", "12", ""))
            for _ in range(self.n_players)
         ] for _ in range(1, self.n_rounds)
    ]
    for round_nbr, labels in enumerate(self.bids_label_matrix):
      round_nbr_label = tk.Label(
          master=self.players_points_frame,
          width=2,
          bg=self.gui_colors["card_color"],
          fg=self.gui_colors["white"],
          justify="right",
          text=str(round_nbr + 1),
          font=("bold", "12", ""))
      round_nbr_label.grid(
          sticky="ne",
          row=round_nbr + 1,
          column=0,
          padx=(10, 0),
          pady=2)
      if round_nbr == self.n_rounds - 2:
        pady = (2, 15)
      else:
        pady = 2
      for player_index, label in enumerate(labels):
        label.grid(
            sticky="s",
            row=round_nbr + 1,
            column=2 * player_index + 1,
            padx=(5, 2),
            pady=pady)

    self.points_label_matrix = [
        [tk.Label(
            master=self.players_points_frame,
            width=5,
            bg=self.gui_colors["white"],
            font=("", "12", ""))
            for _ in range(self.n_players)
         ] for _ in range(1, self.n_rounds)
    ]
    for round_nbr, labels in enumerate(self.points_label_matrix):
      if round_nbr == self.n_rounds - 2:
        pady = (2, 15)
      else:
        pady = 2
      for player_index, label in enumerate(labels):
        if player_index == self.n_players - 1:
          padx = (2, 15)
        else:
          padx = (2, 5)
        label.grid(
            sticky="s",
            row=round_nbr + 1,
            column=2 * player_index + 2,
            padx=padx,
            pady=pady)


  def _start_game(self):
    """
    create a `Wizard_Game_State` object and start the game by allowing player action inputs.
    """
    self.game_obj = Wizard_Game_State(self.n_players, verbosity=0)
    # for round_nbr in range(1, self.n_rounds):
    round_nbr = self.game_obj.round_number
    self._initialize_round(self.game_obj, round_nbr)


  def _initialize_round(self,
                        game: Wizard_Game_State,
                        round_nbr: int):
    """
    play round `round_nbr` with the rules saved in `self`

    inputs:
    -------
      game (Wizard_Game_State): object containing the current game state
      round_nbr (int): round number = number of tricks in the round
    """
    self.n_bids.set(0)
    self.n_tricks.set(round_nbr)
    self.round_nbr.set(round_nbr)
    clear_frame(self.trump_card_frame)
    # generate hands and determine trump
    hands, trump_card = get_hands(game.n_players, round_nbr)
    # hands, trump_card = get_hands(game.n_players, 9)
    self._determine_trump(game, hands, trump_card)


  def _determine_trump(self,
                       game: Wizard_Game_State,
                       hands: list,
                       trump_card: Wizard_Card):
    # show trump card
    self._show_card(self.trump_card_frame, trump_card)
    # determine trump color
    if trump_card is None:  # no trump card
      trump_color = None
      self._start_round(game, hands, trump_card, trump_color)
    elif trump_card.value != 14:  # trump card determines trump color (including jester -> no trump)
      trump_color = trump_card.color
      self._start_round(game, hands, trump_card, trump_color)
    else:  # trump card is a wizard -> dealer determines trump
      active_player = game.round_starting_player
      clear_frame(self.played_cards_frame)
      self._show_hand(hands[active_player], active_player)
      choose_trump_label = tk.Label(
          master=self.played_cards_frame,
          text="Choose a trump color for this round:"
      )
      self.wizard_menu.add_label_style(choose_trump_label)
      choose_trump_label.grid(
          sticky="s",
          row=0,
          column=0,
          columnspan=6)
      self.played_cards_frame.columnconfigure(0, weight=1)
      self.played_cards_frame.columnconfigure(5, weight=1)

      def set_trump(color_index: int):
        """
        start a round with the given color as trump

        inputs:
        -------
          color_index (int: - index of the chosen trump color
        """
        clear_frame(self.players_hand_frame)
        # reset column weights
        self.played_cards_frame.columnconfigure(0, weight=0)
        self.played_cards_frame.columnconfigure(5, weight=0)
        # start round
        self._start_round(game, hands, trump_card, int(color_index))

      player_mode = self.ai_player_types[active_player]["trump_choice_var"]
      if player_mode != "human input":
        ai_trump_choice = ai_trump_chooser_methods[player_mode](
            hands=hands,
            active_player=active_player,
            game_state=game)
        if self.ai_player_types[active_player]["hints_var"] is False:
          self.master_window.after(10, lambda: set_trump(color_index=ai_trump_choice))
        else:
          print(f"{ai_trump_choice=}")  # TODO: show ai trump hint in GUI
      if self.ai_player_types[active_player]["hints_var"] or player_mode == "human input":
        # create buttons to choose trump color
        for color_index in range(4):
          color_button_frame = tk.Frame(
              master=self.played_cards_frame,
              bg=self.gui_colors[self.card_color_to_str[color_index]],
              height=174,
              width=112,
              highlightbackground=self.gui_colors["card_color"],
              highlightthickness=5)
          color_button_frame.grid(
              sticky="n",
              row=1,
              column=color_index + 1,
              padx=5,
              pady=5)
          color_button_frame.bind("<Button-1>", lambda _, i=color_index: set_trump(i))


  def _start_round(self,
                   game: Wizard_Game_State,
                   hands: list,
                   trump_card: Wizard_Card,
                   trump_color: int):
    """
    show trump color and start playing the round

    inputs:
    -------
      game (Wizard_Game_State: - game state encoded in an object
      hands (list: - hands of each player
      trump_card (Wizard_Card: - trump card
      trump_color (int: - trump color (important if trump card is a wizard)
    """
    # show trump color
    if trump_card is None:
      trump_color = -1
    bg_color = self.gui_colors[self.card_color_to_str[trump_color]]
    self.trump_color_frame.config(
        bg=bg_color)
    # start round in `game`
    game.start_round(hands, trump_card, trump_color)
    # get predictions from each player
    self.predictions = np.zeros(game.n_players, dtype=np.int8)
    self._get_player_prediction(game, game.round_number, game.round_starting_player)


  def _get_player_prediction(self,
                             game: Wizard_Game_State,
                             round_nbr: int,
                             player_index: int):
    clear_frame(self.played_cards_frame)
    choose_predictions_label = tk.Label(
        master=self.played_cards_frame,
        text="How many tricks do you plan to win this round?")
    self.wizard_menu.add_label_style(choose_predictions_label)
    choose_predictions_label.grid(
        sticky="sew",
        row=0,
        column=0,
        columnspan=13)
    self.played_cards_frame.columnconfigure(0, weight=1)
    self.played_cards_frame.columnconfigure(12, weight=1)

    def set_bids(n_bids: int, player_index: int):
      """
      save the given number of predicted tricks and progress the game state (get prediction from next player or start tricks)

      inputs:
      -------
        n_bids (int) - number of predicted won tricks
      """
      self.predictions[player_index] = n_bids
      clear_frame(self.players_hand_frame)
      self.bids_label_matrix[round_nbr - 1][player_index].config(text=n_bids)
      player_index = (player_index + 1) % game.n_players
      self.n_bids.set(self.n_bids.get() + n_bids)
      if player_index != game.round_starting_player:
        self._get_player_prediction(game, round_nbr, player_index)
      else:
        game.set_predictions(self.predictions)
        clear_frame(self.played_cards_frame)
        # show how many tricks each player bid and won this round
        self.player_bids_labels = [0] * game.n_players
        for player_index in range(game.n_players):
          player_name_label = tk.Label(
              master=self.played_cards_frame,
              text=self.ai_player_types[player_index]["player_name_var"])
          self.wizard_menu.add_label_style(player_name_label)
          player_name_label.grid(
              row=0,
              column=player_index + 1,
              padx=5,
              pady=(0, 5))

          player_bids_label = tk.Label(
              master=self.played_cards_frame,
              text=f"0 / {self.predictions[player_index]}")
          self.wizard_menu.add_label_style(player_bids_label)
          player_bids_label.grid(
              row=1,
              column=player_index + 1,
              padx=5,
              pady=(0, 15))
          self.player_bids_labels[player_index] = player_bids_label
          card_width_frame = tk.Frame(
              master=self.played_cards_frame,
              width=self.card_width,
              height=1,
              bg=self.gui_colors["bg"])
          card_width_frame.grid(
              row=2,
              column=player_index + 1,
              padx=5)
        self._initialize_trick(game)

    player_mode = self.ai_player_types[player_index]["bids_choice_var"]
    if player_mode != "human input":
      ai_bid = ai_bids_chooser_methods[player_mode](
          player_index=player_index,
          game_state=game)
      if self.ai_player_types[player_index]["hints_var"] is False:
        self.master_window.after(10, lambda: set_bids(n_bids=ai_bid, player_index=player_index))
      else:
        print(f"{ai_bid=}")  # TODO: show ai bid hint in GUI
    if self.ai_player_types[player_index]["hints_var"] or player_mode == "human input":
      self._show_hand(game.players_hands[player_index], player_index)
      # create buttons to place bitds
      for n_bids in range(round_nbr + 1):
        # implement special rule `n_bids != n_tricks`
        if self.limit_choices \
                and player_index == (game.round_starting_player - 1) % game.n_players \
                and np.sum(self.predictions) + n_bids == round_nbr:
          continue
        bid_button = tk.Button(
            master=self.played_cards_frame,
            command=lambda i=n_bids: set_bids(i, player_index),
            text=n_bids,
            width=2)
        self.wizard_menu.add_button_style(bid_button)
        bid_button.grid(
            sticky="nw",
            row=n_bids // 11 + 1,
            column=n_bids % 11 + 1,
            padx=5,
            pady=5
        )



  def _initialize_trick(self, game: Wizard_Game_State):
    """
    set up everything for playing a trick

    inputs:
    -------
      game (Wizard_Game_State): game state object
    """
    if game.tricks_to_be_played != game.round_number:
      for frame in self.played_cards:
        frame.destroy()
    # print("init trick")
    self.played_cards_frame.columnconfigure(game.n_players + 1, weight=1)  # TODO undo this after each round
    self.played_cards = [0] * game.n_players
    for player_index in range(game.n_players):
      played_card_frame = tk.Frame(
          master=self.played_cards_frame,
          bg=self.gui_colors["card_color"],
          highlightbackground=self.gui_colors["card_border"],
          highlightthickness=5,
          width=self.card_width,
          height=self.card_height)
      played_card_frame.grid_propagate(False)
      played_card_frame.grid(
          sticky="nw",
          row=3,
          column=player_index + 1,
          padx=5,
          pady=0)
      self.played_cards[player_index] = played_card_frame

    game.start_trick()
    self._play_trick(game)


  def _play_trick(self, game: Wizard_Game_State):
    """
    start playing a trick

    inputs:
    -------
      game (Wizard_Game_State) - game state object
    """
    player_index = game.trick_active_player

    player_mode = self.ai_player_types[player_index]["trick_play_var"]
    if player_mode != "human input":
      ai_action = ai_trick_play_methods[player_mode](
          game_state=game)
      if self.ai_player_types[player_index]["hints_var"] is False:
        self.master_window.after(10, lambda: self._perform_action(action=ai_action))
      else:
        print(f"{ai_action=}")  # TODO: show ai action hint in GUI
    if self.ai_player_types[player_index]["hints_var"] or player_mode == "human input":

      self._show_hand(game.players_hands[player_index], player_index, clickable=True)


  def _check_action(self, action: Wizard_Card):
    hand = self.game_obj.players_hands[self.game_obj.trick_active_player]
    if not check_action_invalid(action, hand, self.game_obj.serving_color):
      # action was valid
      self._perform_action(action)


  def _perform_action(self, action: Wizard_Card):
    clear_frame(self.players_hand_frame)

    print(f"player {self.game_obj.trick_active_player+1} action: {action}")

    active_player = self.game_obj.trick_active_player
    played_card_frame = self.played_cards[active_player]
    self._show_card(played_card_frame, action)

    old_winner = self.game_obj.trick_winner_index
    self.played_cards[old_winner].config(
        highlightbackground=self.gui_colors["card_border"])

    game_state = self.game_obj.perform_action(action)

    winner = self.game_obj.trick_winner_index
    self.played_cards[winner].config(
        highlightbackground=self.gui_colors["card_highlight_border"])

    if game_state == 1:  # trick done
      self._end_trick(start_new_trick=True)
    elif game_state == 2:  # round done
      self._end_trick(start_new_trick=False)
      self._end_round()
    else:
      self._play_trick(self.game_obj)


  def _end_trick(self, start_new_trick=True):
    # update won trick counter of the trick winner
    winner_label = self.player_bids_labels[self.game_obj.trick_winner_index]
    print(f"winner of trick {self.game_obj.round_number-self.game_obj.tricks_to_be_played} in round {self.game_obj.round_number} is: player {self.game_obj.trick_winner_index+1}")
    old_text = winner_label["text"].split(" / ")
    new_won_tricks = 1 + int(old_text[0])
    winner_label.config(text=f"{new_won_tricks} / {old_text[1]}")
    self.played_cards_frame.update()
    time.sleep(self.end_of_trick_delay)
    if start_new_trick:
      self._initialize_trick(self.game_obj)


  def _end_round(self):
    # update total scores
    game = self.game_obj
    gained_points = game.players_gained_points_history[game.round_number - 2]
    self.played_cards_frame.columnconfigure(game.n_players + 1, weight=0)
    for player_index, pair in enumerate(zip(gained_points, game.players_total_points)):
      # round nuber has already been increased at this point
      player_points_label = self.points_label_matrix[game.round_number - 2][player_index]
      sign, value = pair
      if sign < 0:
        player_points_label.config(
            fg=self.gui_colors["red"])
      player_points_label.config(text=value)
    time.sleep(self.end_of_round_delay)
    if game.round_number < self.n_rounds:
      self._initialize_round(game, game.round_number)
    else:
      self._show_winner()


  def _show_winner(self):
    for label, points in zip(self.player_bids_labels, self.game_obj.players_total_points):
      label.config(
          text=f"{points} points")
    for frame in self.played_cards:
      frame.destroy()

    winner_index = np.argmax(self.game_obj.players_total_points)
    winner_label = tk.Label(
        master=self.played_cards_frame,
        text=f"{self.ai_player_types[winner_index]['player_name_var']} won!\nCongratulations!")
    self.wizard_menu.add_label_style(winner_label, fontsize=24)
    winner_label.grid(
        sticky="n",
        row=2,
        column=1,
        columnspan=self.game_obj.n_players,
        padx=0,
        pady=(50, 0))


  def _show_hand(self,
                 hand: list,
                 player_index: int,
                 clickable: bool = False):
    """show the given hand of a player

    inputs:
    -------
      hand (list) of (Wizard_Card) - list of wizard cards in the hand of the current player
      player_infex (int) - index of the player to label the hand
      clickable (bool) - whether or not clicking the cards triggers an action # TODO
    """
    clear_frame(self.players_hand_frame)
    player_name = f"Hand of Player {player_index+1}:"
    player_name_label = tk.Label(
        master=self.players_hand_frame,
        text=player_name)
    self.wizard_menu.add_label_style(player_name_label)
    player_name_label.place(
        anchor="nw",
        x=0,
        y=0)
    # player_name_label.grid(
    #     sticky="sw",
    #     row=0,
    #     column=0,
    #     padx=0,
    #     pady=10)

    frame_width = self.master_window.winfo_width() - self.players_points_frame.winfo_width() - 100
    if len(hand) > 1:
      card_x_shift = (frame_width - self.card_width) // (len(hand) - 1)
      card_x_shift = min(card_x_shift, self.card_width)
    else:
      card_x_shift = 0

    self.players_hand_frame.config(width=frame_width, height=self.card_height + 50),
    x_position = 0
    for i, card in enumerate(hand):
      card_frame = tk.Frame(
          master=self.players_hand_frame,
          bg=self.gui_colors["card_color"],
          highlightbackground=self.gui_colors["card_border"],
          highlightthickness=5,
          width=self.card_width,
          height=self.card_height)
      card_frame.grid_propagate(False)
      card_frame.place(
          anchor="nw",
          x=x_position,
          y=50)
      self._show_card(card_frame, card)
      if clickable:
        self._make_clickable(card_frame, card)
      x_position += card_x_shift


  def _make_clickable(self, frame: tk.Frame, card: Wizard_Card):
    """
    Make a wizard card frame clickable as well as highlight it when the mouse hovers over it.

    inputs:
    -------
      frame (tk.Frame: - the frame that should be clickable
      card (Wizard_Card: - the card that is represented by the frame. When clicked, `self.check_action()` will be executed with this card as the argument.
    """
    def on_enter_card(_):
      frame.place(
          anchor="nw",
          x=frame.winfo_x(),
          y=frame.winfo_y() - 40)
      frame.config(highlightbackground=self.gui_colors["card_highlight_border"])

    def on_leave_card(_):
      frame.place(
          anchor="nw",
          x=frame.winfo_x(),
          y=frame.winfo_y() + 40)
      frame.config(highlightbackground=self.gui_colors["card_border"])

    def on_click_card(_):
      # print(card)
      self._check_action(card)

    frame.bind("<Enter>", on_enter_card)
    frame.bind("<Leave>", on_leave_card)
    frame.bind("<Button-1>", on_click_card)


  def _show_card(self, frame: tk.Frame, card: Wizard_Card):
    """
    show a wizard card

    inputs:
    -------
      frame (tk.Frame: - the tkinter frame where the card is to be shown
      card (Wizard_Card: - the card to be displayed
    """
    if card is None:
      return
    card_font = "cooper black"
    if card.value == 0:
      card_text = "J"
    elif card.value == 14:
      card_text = "W"
    else:
      card_text = card.value
    card_value_labels = [tk.Label(
        master=frame,
        text=card_text,
        width=2,
        bg=self.gui_colors["card_color"],
        fg=self.gui_colors[self.card_color_to_str[card.color]],
        font=(card_font, "15", "")) for _ in range(4)]

    card_value_labels[0].grid(
        sticky="nw",
        row=0,
        column=0,
        padx=(5, 0),
        pady=(5, 0))
    card_value_labels[1].grid(
        sticky="ne",
        row=0,
        column=2,
        padx=(0, 5),
        pady=(5, 0))
    card_value_labels[2].grid(
        sticky="sw",
        row=2,
        column=0,
        padx=(5, 0),
        pady=(5, 0))
    card_value_labels[3].grid(
        sticky="se",
        row=2,
        column=2,
        padx=(5, 0),
        pady=(5, 0))

    card_big_value_label = tk.Label(
        master=frame,
        text=card_text,
        width=2,
        bg=self.gui_colors["card_color"],
        fg=self.gui_colors[self.card_color_to_str[card.color]],
        font=(card_font, "25", ""))
    card_big_value_label.grid(
        sticky="se",
        row=1,
        column=1,
        padx=10,
        pady=55)


def clear_frame(frame: tk.Frame):
  """cleaer all contents of a frame

  inputs:
  -------
    frame (tk.Frame) - any tkinter frame or canvas
  """
  for child_widget in frame.winfo_children():
    child_widget.destroy()
