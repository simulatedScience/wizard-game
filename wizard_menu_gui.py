import tkinter as tk
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

        # set up game settings variables
        self.n_players_var = tk.IntVar(self.master_window, value=3)
        self.limit_choices_var = tk.BooleanVar(self.master_window, value=True)
        self.max_rounds_var = tk.IntVar(self.master_window, value=20)

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
            sticky="nw",
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
            sticky="nw",
            row=row_index,
            column=0,
            padx=0,
            pady=5)
        limit_choices_label = tk.Label(
            master=limit_choices_frame,
            text="Allow Bids = Tricks:")
        self.add_label_style(limit_choices_label, fontsize=15)
        limit_choices_label.grid(
            sticky="w",
            row=0,
            column=0,
            padx=0,
            pady=5)
        limit_choices_check = tk.Checkbutton(
            master=limit_choices_frame,
            bg=self.gui_colors["button"],
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
            sticky="nw",
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
            bg=self.gui_colors["button"],
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
            sticky="nw",
            row=row_index,
            column=0,
            padx=0,
            pady=5)
        row_index += 1
        # create radio buttons for choosing number of players
        radio_frame = tk.Frame(
            master=self.main_frame,
            bg=self.gui_colors["bg"])
        radio_frame.grid(
            sticky="nw",
            row=row_index,
            column=0,
            padx=10,
            pady=5)
        n_player_choices = (3, 4, 5, 6)
        col_index = 0
        for n_players in n_player_choices:
            n_players_headline_radio = tk.Radiobutton(
                master=radio_frame,
                text=str(n_players),
                variable=self.n_players_var,
                value=n_players,
                indicatoron=False,
                bg=self.gui_colors["button"],
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
                highlightthickness=0
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

        # add buttons for player modes
        self.player_modes_frame = tk.Frame(
            master=self.main_frame,
            bg=self.gui_colors["bg"])
        self.player_modes_frame.grid(
            sticky="nw",
            row=row_index,
            column=0,
            padx=10,
            pady=5)
        row_index += 1
        self.add_player_mode_choices()

        # play button
        play_button = tk.Button(
            master=self.main_frame,
            text="Start game!",
            command=self.check_menu_inputs)
        self.add_button_style(play_button)
        play_button.grid(
            sticky="w",
            row=row_index,
            column=0,
            padx=0,
            pady=5)
        row_index += 1

    def add_player_mode_choices(self):
        """
        add inputs for player modes
        """
        self.player_modes_widgets = list()
        for row_index in range(6):
            row_widgets = list()
            row_frame = tk.Frame(
                master=self.player_modes_frame,
                bg=self.gui_colors["bg"])
            row_frame.grid(
                row=row_index,
                column=0, pady=(0,5))
            row_widgets.append(row_frame)
            hint_var = tk.BooleanVar(
                master=row_frame,
                value=False)
            row_widgets.append(hint_var)
            row_widgets.append(
                tk.Checkbutton(
                    master=row_frame,
                    text="AI hints",
                    variable=hint_var,
                    bg=self.gui_colors["button"],
                    fg=self.gui_colors["button_fg"],
                    activebackground=self.gui_colors["active_button"],
                    activeforeground=self.gui_colors["active_button_fg"],
                    selectcolor=self.gui_colors["active_button"],
                    indicatoron=False,
                    border=0,
                    relief="flat"
                )
            )
            row_widgets[-1].grid(
                sticky="nw",
                row=row_index,
                column=len(row_widgets) - 1,
                padx=5,
                pady=5)

            row_widgets.append(
                tk.Label(
                    master=row_frame,
                    text="trump color choice",
                    bg=self.gui_colors["bg"],
                    fg=self.gui_colors["fg"])
            )
            row_widgets[-1].grid(
                sticky="nw",
                row=row_index,
                column=len(row_widgets) - 1,
                padx=5,
                pady=5)

            row_widgets.append(
                tk.Label(
                    master=row_frame,
                    text="bids choice",
                    bg=self.gui_colors["bg"],
                    fg=self.gui_colors["fg"])
            )
            row_widgets[-1].grid(
                sticky="nw",
                row=row_index,
                column=len(row_widgets) - 1,
                padx=5,
                pady=5)

            row_widgets.append(
                tk.Label(
                    master=row_frame,
                    text="trick play",
                    bg=self.gui_colors["bg"],
                    fg=self.gui_colors["fg"])
            )
            row_widgets[-1].grid(
                sticky="nw",
                row=row_index,
                column=len(row_widgets) - 1,
                padx=5,
                pady=5)
            self.player_modes_widgets.append(row_widgets)


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
        self.start_game(n_players, limit_choices, max_rounds)
        return True


    def start_game(self, n_players: int, limit_choices: bool, max_rounds: int) -> None:
        self.main_frame.destroy()
        game_gui = Wizard_Game_Gui(self, n_players, limit_choices, max_rounds)


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
            bg=self.gui_colors["button"],
            fg=self.gui_colors["button_fg"],
            activebackground=self.gui_colors["active_button"],
            activeforeground=self.gui_colors["active_button_fg"],
            relief="flat",
            bd=0,
            font=("", "15", ""))


    def add_entry_style(self, entry):
        entry.configure(
            bg=self.gui_colors["fg"],
            fg=self.gui_colors["bg"],
            relief="flat",
            bd=0,
            justify="center",
            font=("", "15", ""))


    def set_gui_colors(self):
        self.gui_colors = {
            "bg": "#ddcc88",  # dark yellow
            "fg": "#000000",  # black
            "button": "#885522",  # brown
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
