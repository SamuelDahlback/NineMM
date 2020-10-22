============
Introduction
============

Hello and welcome to group J:s project for the course Software Engineering and Project Management, fall 2020. 
We have developed a CLI for a communication platform that is easily implemented and stable. 
This communication platform is built to hold a tournament for 3 to 8 people and to play 1v1 games.

The current implementation has been developed in Python 3 and has been tested.

See `GitHub <https://github.com/dahlberge/groupJ>`_ for the full repo.

Installation
************
Make sure you have `python3 <https://www.python.org/downloads/>`_ installed.

To check if you already have python3, use the following:

.. code-block:: bash

    $ python3 --version

Usages
******
Run the following command in the terminal to start the CLI menu:

.. code-block:: bash

   $ python3 source/interface.py

Run the same command in a terminals to join as a client.

At the moment the game is not implemented, to pretend that you are playing a game all moves sent should start with "MOV" + (the move) and if the game is finished "FIN" + ("WIN","LOSS" or "TIE").

.. code-block:: bash

   $ MOV[your move here] # Sends a players move to the server
   $ FINWIN   # The player that won ends the game
   $ FINLOSS  # The player that lost ends the game
   $ FINTIE   # Ends the game in a tie

Motivation
**********

The motivation for the project was to create a simple communication platform that is easy to implement. 
Because of this the focus has been to create functions that can be used in a larger project with more modules and complexity.

Limitations
***********

- Tournaments support from 3 to 8 players

- CLI interface

- Written by students
