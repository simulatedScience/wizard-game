# Wizard card game

This project implements a digital version of the popular card game Wizard (published by Amigo) using python.

The goal is to train different AIs to play the game and allow humans to play against those AIs.

Currently the game is playable for humans with some basic AIs and the infrastructure to easily implement more AIs is in place.
It supports a very basic version of local multiplayer, but cannot properly hide information yet.

To start the game, execute `main.py`.

## future plans
- It's unlikely that I will add the option for online multiplayer.
- Support testing various AIs against each other and measure how good they are
- Allow manual input of game states or automatically reading it from images or screen captures to use the AIs either for analog or online play outside this program.
- Try to establish a software architecture that can be easily adapted to implement AIs for many different, similar (card) games.