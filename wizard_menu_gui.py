from doctest import master
import tkinter as tk
import tkinter.ttk as ttk

from pygments import highlight
if __name__ == "__main__":
    from wizard_game_gui import Wizard_Game_Gui


class Wizard_Menu_Gui():
    """
    A Menu for the wizard card game that allows setting all rules and starting games.
    """
    def __init__(self):
        self.set_gui_colors()
        # start menu UI
        self.master_window = tk.Tk(screenName="test")
        self.master_window.configure(bg=self.gui_colors["bg"])
        self.master_window.minsize(800, 600)
        self.master_window.state("zoomed")

        self.menu_justification = "n"
        self.ai_mode_justification = "n"

        # set up game settings variables
        self.n_players_var = tk.IntVar(self.master_window, value=3)
        self.limit_choices_var = tk.BooleanVar(self.master_window, value=True)
        self.max_rounds_var = tk.IntVar(self.master_window, value=20)

        self.init_ai_mode_variables()

        self.open_main_window()


    def open_main_window(self):
        """
        open a main menu window in `self.master_window`
        """
        self.main_frame = tk.Frame(
            master=self.master_window,
            bg=self.gui_colors["bg"])
        self.main_frame.place(
            anchor="c",
            relx=.5,
            rely=.5)
        row_index = 0

        headline_label = tk.Label(
            master=self.main_frame,
            text="Wizard Settings")
        self.add_label_style(headline_label, fontsize=20)
        headline_label.grid(
            sticky=self.menu_justification,
            row=row_index,
            column=0,
            padx=0,
            pady=10)
        row_index += 1
        # checkbutton to limit choices for predictions
        limit_choices_frame = tk.Frame(
            master=self.main_frame,
            bg=self.gui_colors["bg"])
        limit_choices_frame.grid(
            sticky=self.menu_justification,
            row=row_index,
            column=0,
            padx=0,
            pady=5)
        limit_choices_label = tk.Label(
            master=limit_choices_frame,
            text="Allow bids = tricks:")
        self.add_label_style(limit_choices_label, fontsize=15)
        limit_choices_label.grid(
            sticky="w",
            row=0,
            column=0,
            padx=0,
            pady=5)
        limit_choices_check = tk.Checkbutton(
            master=limit_choices_frame,
            bg=self.gui_colors["button_bg"],
            fg=self.gui_colors["button_fg"],
            activebackground=self.gui_colors["active_button"],
            activeforeground=self.gui_colors["active_button_fg"],
            highlightbackground=self.gui_colors["active_button"],
            highlightthickness=0,
            variable=self.limit_choices_var,
            indicatoron=False,
            relief="flat",
            borderwidth=0,
            takefocus=True,
            selectcolor=self.gui_colors["active_button"],
            padx=8,
            textvariable=self.limit_choices_var,
            font=("", "15", "")
        )
        limit_choices_check.grid(
            sticky="w",
            row=0,
            column=1,
            padx=(10, 0),
            pady=5)
        row_index += 1
        # entry for maximum number of rounds
        max_rounds_frame = tk.Frame(
            master=self.main_frame,
            bg=self.gui_colors["bg"])
        max_rounds_frame.grid(
            sticky="n",
            row=row_index,
            column=0,
            padx=0,
            pady=5)
        max_rounds_label = tk.Label(
            master=max_rounds_frame,
            text="Maximum number of rounds:")
        self.add_label_style(max_rounds_label, fontsize=15)
        max_rounds_label.grid(
            sticky="w",
            row=0,
            column=0,
            padx=0,
            pady=5)
        max_rounds_entry = tk.Entry(
            master=max_rounds_frame,
            textvariable=self.max_rounds_var,
            width=3,
            font=("", "15", ""),
            bg=self.gui_colors["button_bg"],
            fg=self.gui_colors["button_fg"],
            justify="center",
            relief="flat",
            insertbackground=self.gui_colors["button_fg"],
            selectbackground=self.gui_colors["active_button"],
            selectforeground=self.gui_colors["active_button_fg"],
            takefocus=True)
        max_rounds_entry.grid(
            sticky="w",
            row=0,
            column=1,
            padx=(10, 0),
            pady=5)
        row_index += 1
        # label for number of players
        n_players_headline_label = tk.Label(
            master=self.main_frame,
            text="Number of players:")
        self.add_label_style(n_players_headline_label, fontsize=15)
        n_players_headline_label.grid(
            sticky=self.menu_justification,
            row=row_index,
            column=0,
            padx=0,
            pady=5)
        row_index += 1
        # create radio buttons for choosing number of players
        n_players_radio_frame = tk.Frame(
            master=self.main_frame,
            bg=self.gui_colors["bg"])
        n_players_radio_frame.grid(
            sticky=self.menu_justification,
            row=row_index,
            column=0,
            padx=10,
            pady=5)
        n_player_choices = (3, 4, 5, 6)
        col_index = 0
        for n_players in n_player_choices:
            n_players_headline_radio = tk.Radiobutton(
                master=n_players_radio_frame,
                text=str(n_players),
                variable=self.n_players_var,
                value=n_players,
                indicatoron=False,
                bg=self.gui_colors["button_bg"],
                fg=self.gui_colors["button_fg"],
                activebackground=self.gui_colors["active_button"],
                activeforeground=self.gui_colors["active_button_fg"],
                relief="flat",
                borderwidth=0,
                takefocus=True,
                selectcolor=self.gui_colors["active_button"],
                padx=8,
                font=("", "15", ""),
                overrelief="flat",
                highlightthickness=0,
                command=self.update_player_modes_choices
            )

            self.add_label_style(n_players_headline_label, fontsize=15)
            n_players_headline_radio.grid(
                sticky="w",
                row=0,
                column=col_index,
                padx=5,
                pady=5)
            col_index += 1
        row_index += 1

        # add frame for player/AI modes
        self.player_modes_frame = tk.Frame(
            master=self.main_frame,
            bg=self.gui_colors["bg"])
        self.player_modes_frame.grid(
            sticky=self.menu_justification,
            row=row_index,
            column=0,
            padx=10,
            pady=5)
        row_index += 1
        # add buttons for player/AI modes
        self.add_player_mode_choices()

        # play button
        play_button = tk.Button(
            master=self.main_frame,
            text="Start game!",
            command=self.check_menu_inputs)
        self.add_button_style(play_button)
        play_button.grid(
            sticky=self.menu_justification,
            row=row_index,
            column=0,
            padx=0,
            pady=5)
        row_index += 1


    def init_ai_mode_variables(self):
        """
        Initialize variables for the AI modes for each player.
        Those variables get saved in `self.ai_mode_variables`
        """
        self.ai_mode_variables: list = list()
        for player_index in range(6):
            player_name_var = tk.StringVar(
                master=self.master_window,
                value=f"player {player_index+1}")
            ai_for_hints_var = tk.BooleanVar(
                master=self.master_window,
                value=False)
            ai_trump_color_choice = tk.StringVar(
                master=self.master_window,
                value="human input")
            ai_bids_choice = tk.StringVar(
                master=self.master_window,
                value="human input")
            ai_trick_play = tk.StringVar(
                master=self.master_window,
                value="human input")
            self.ai_mode_variables.append(
                {"player_name_var": player_name_var,
                 "hints_var": ai_for_hints_var,
                 "trump_choice_var": ai_trump_color_choice,
                 "bids_choice_var": ai_bids_choice,
                 "trick_play_var": ai_trick_play})


    def add_player_mode_choices(self):
        """
        Add the AI mode choices for the initial players.
        """
        self.player_modes_widgets = list()
        for column_index in range(self.n_players_var.get()):
            self.add_player_mode_column(column_index)


    def update_player_modes_choices(self):
        """
        add or remove player mode input columns until the number of columns matches the number of players
        """
        n_players = self.n_players_var.get()
        while n_players > len(self.player_modes_widgets):
            self.add_player_mode_column(column_index=len(self.player_modes_widgets))
        while n_players < len(self.player_modes_widgets):
            self.remove_player_mode_column(column_index=-1)


    def add_player_mode_column(self, column_index: int):
        """
        add all inputs for choosing the AI types for a player in the given column

        inputs:
        -------
            column_index (int): index of the column to be added
        """
        column_widgets = list()
        # column_frame = tk.Frame(
        #     master=self.player_modes_frame,
        #     bg=self.gui_colors["bg"])
        # column_frame.grid(
        #     row=0,
        #     column=column_index, padx=(0, 5))
        # column_widgets.append(column_frame)

        # start adding contents to each column
        column_widgets.append(
            tk.Entry(
                master=self.player_modes_frame,
                textvariable=self.ai_mode_variables[column_index]["player_name_var"],
                width=8
            )
        )
        self.add_entry_style(column_widgets[-1])
        column_widgets[-1].grid(
            sticky=self.ai_mode_justification,
            row=len(column_widgets) - 1,
            column=column_index,
            padx=5,
            pady=5)

        column_widgets.append(
            tk.Checkbutton(
                master=self.player_modes_frame,
                text="AI hints",
                width=10,
                variable=self.ai_mode_variables[column_index]["hints_var"],
                bg=self.gui_colors["button_bg"],
                fg=self.gui_colors["button_fg"],
                activebackground=self.gui_colors["active_button"],
                activeforeground=self.gui_colors["active_button_fg"],
                selectcolor=self.gui_colors["active_button"],
                indicatoron=False,
                border=0,
                relief="flat"
            )
        )
        column_widgets[-1].grid(
            sticky=self.ai_mode_justification,
            row=len(column_widgets) - 1,
            column=column_index,
            padx=5,
            pady=5)

        column_widgets.append(
            ttk.Combobox(
                master=self.player_modes_frame,
                text="trump color choice",
                textvariable=self.ai_mode_variables[column_index]["trump_choice_var"])
        )
        self.add_combobox_style(column_widgets[-1])
        column_widgets[-1].grid(
            sticky=self.ai_mode_justification,
            row=len(column_widgets) - 1,
            column=column_index,
            padx=5,
            pady=5)

        column_widgets.append(
            ttk.Combobox(
                master=self.player_modes_frame,
                text="bids choice",
                textvariable=self.ai_mode_variables[column_index]["bids_choice_var"])
        )
        self.add_combobox_style(column_widgets[-1])
        column_widgets[-1].grid(
            sticky=self.ai_mode_justification,
            row=len(column_widgets) - 1,
            column=column_index,
            padx=5,
            pady=5)

        column_widgets.append(
            ttk.Combobox(
                master=self.player_modes_frame,
                text="trick play",
                textvariable=self.ai_mode_variables[column_index]["trick_play_var"])
        )
        self.add_combobox_style(column_widgets[-1])
        column_widgets[-1].grid(
            sticky=self.ai_mode_justification,
            row=len(column_widgets) - 1,
            column=column_index,
            padx=5,
            pady=5)

        self.player_modes_widgets.append(column_widgets)


    def remove_player_mode_column(self, column_index: int = -1):
        """
        remove the given column, by default, this removes the last column

        inputs:
        -------
            column_index (int): index of the column to be added, default: `-1`
        """
        # remove widgets of given column
        for widget in self.player_modes_widgets[column_index]:
            widget.destroy()
        if column_index not in (-1, len(self.player_modes_widgets) - 1):
            # move all remaining columns to the left by one, such that all columns are filled.
            for new_column_index in range(column_index + 1, len(self.player_modes_widgets)):
                for row_index, widget in \
                        enumerate(self.player_modes_widgets[new_column_index]):
                    widget.grid(
                        row=row_index,
                        column=new_column_index - 1)
        # delete list containing the widgets in the deleted column
        del self.player_modes_widgets[column_index]


    def check_menu_inputs(self) -> bool:
        """
        Check that all inputs in the menu have valid values.
        If they do, start the game with the given settings.
        """
        try:
            max_rounds = self.max_rounds_var.get()
        except tk.TclError:
            return False
        if max_rounds < 1:
            return False  # game start not successful
        n_players = self.n_players_var.get()
        limit_choices = not self.limit_choices_var.get()
        ai_player_choices = [
            {key: var.get() for key, var in var_dict.items()}
            for var_dict in self.ai_mode_variables
        ]
        # # DEBUG:
        # for var_dict in ai_player_choices:
        #     print(var_dict)
        self.start_game(n_players, limit_choices, max_rounds, ai_player_choices)
        return True


    def start_game(self,
                   n_players: int,
                   limit_choices: bool,
                   max_rounds: int,
                   ai_player_choices: list) -> None:
        self.main_frame.destroy()
        game_gui = Wizard_Game_Gui(
            self,
            n_players,
            limit_choices,
            max_rounds,
            ai_player_choices)


    def add_label_style(self, label, fontsize=15):
        if fontsize > 15:
            bold = "bold"
        else:
            bold = ""
        label.configure(
            bg=self.gui_colors["bg"],
            fg=self.gui_colors["fg"],
            font=(bold, fontsize, ""))


    def add_button_style(self, button):
        button.configure(
            bg=self.gui_colors["button_bg"],
            fg=self.gui_colors["button_fg"],
            activebackground=self.gui_colors["active_button"],
            activeforeground=self.gui_colors["active_button_fg"],
            relief="flat",
            bd=0,
            font=("", "15", ""))


    def add_entry_style(self, entry):
        entry.configure(
            bg=self.gui_colors["bg"],
            fg=self.gui_colors["fg"],
            selectbackground=self.gui_colors["active_button"],
            selectforeground=self.gui_colors["active_button_fg"],
            relief="flat",
            bd=0,
            justify="center",
            font=("", "15", ""))


    def add_combobox_style(self, combobox, width=12):
        # self.ttk_style = ttk.Style(self.master_window)
        # self.ttk_style = ttk.Style(combobox)
        # self.ttk_style.configure(
        #     "TCombobox",
        #     fieldbackground=self.gui_colors["button_bg"],
        #     background=self.gui_colors["button_bg"],
        #     arrowsize=0)
        combobox.configure(
            background=self.gui_colors["button_bg"],
            # foreground=self.gui_colors["button_fg"],
            width=width,
            state="readonly"
            # bordercolor=self.gui_colors["button_bg"],
            # arrowsize=0,
            # arrowcolor=self.gui_colors["button_fg"],
        )


    def set_gui_colors(self):
        self.gui_colors = {
            "bg": "#ddcc88",  # dark yellow
            "fg": "#000000",  # black
            "button_bg": "#885522",  # brown
            "active_button": "#aa6633",  # light brown
            "button_fg": "#dddddd",  # almost white
            "active_button_fg": "#dddddd",  # almost white
            "red": "#ff3333",
            "yellow": "#dddd00",
            "green": "#22dd22",
            "blue": "#5588ff",
            "white": "#dddddd",
            "card_color": "#283035",
            "card_border": "#666666",
            "card_highlight_border": "#aa66aa",
        }


if __name__ == "__main__":
    wizard_gui = Wizard_Menu_Gui()
    tk.mainloop()
