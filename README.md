# Continual Online Evolutionary Planning for In-Game Build Order Adaptation in StarCraft

## Brood War Strategy Server
This project uses the Django framework to provide build order interface for StarCraft bots in Python. The bot must implement the client side API. An example of a bot implementing this is UAlbertaBot: https://github.com/njustesen/ualbertabot. 

## How to run the server
- Clone repository into some directory <coep-dir>
- Install Python 3 or later. Make sure to setup environment path for python.
- Install numpy and django. E.g. using pip.
- In a terminal goto <coep-dir>/http_server/ and run "python manage.py runserver 0.0.0.0:8000"
- You should be able to connect to the server using a browser. Try http://localhost:8000/app/probe/ - which always returns the syntax for a probe.

## Continual Online Evolutionary Planning
- To use Continual Online Evolutionary Planning (COEP) for you bot, simply start the server and point the bot client to http://localhost:8000/app/update/ and used the API described below. https://github.com/njustesen/ualbertabot already implements the API.
- To manipulate with the heuristic used by the evolution, edit the file https://github.com/njustesen/coep-starcraft/blob/master/broodwar_strategy_evolver/starcraft/data/unit_heuristics_8.csv and https://github.com/njustesen/coep-starcraft/blob/master/broodwar_strategy_evolver/starcraft/data/tech_upgrades_heuristics.csv. Details can be found in our paper. Link will appear soon.

## API
- app/update/
  - own_units: The number of each friendly unit type seperated by "-" where the index of each number corresponds to the unit type id. Example: 0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-14-2-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-1-0-3-1-0-0-2-0-0-0-1-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0
  - own_units_under_construction: "-"-seperated lists of lists, where each list contains the time left for a builds to complete where the lists index in the top-level list is the unit type id.
 Example: ----------------------------------------------------------------129--749---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  - own_techs: The number of each tech researched seperated by "-" where the index of each number corresponds to the tech type id. Note, that some techs are researched at the start of the game.
  Example: 0-0-0-0-1-0-1-0-0-0-0-0-1-0-1-0-0-0-1-0-0-0-0-1-0-0-0-0-1-1-0-0-0-0-1-0-0-0-0-0-0-0-0-0-0-1-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0
  - own_techs_under_construction: "-"-seperated lists of lists, where each list contains the time left for builds to complete where the lists index in the top-level list is the tech type id.
  - own_upgrades:  The number of each upgrade researched seperated by "-" where the index of each number corresponds to the upgrade type id. 
  Example: 0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-1-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0
  - own_upgrades_under_construction:  "-"-seperated lists of lists, where each list contains the time left for builds to complete where the lists index in the top-level list is the upgrade type id.
  Example: 0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-2354-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0
  - opp_units: The number of known enemy unit types seperated by "-" where the index of each number corresponds to the unit type id. Example: 2-0-0-0-0-0-0-12-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-1-0-0-1-1-1-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0
  - minerals: The number of minerals reseources the player has. 
  - gas: The number of gas reseources the player has.
  - own_race: protoss/terran/zerg.
  - opp_race: protoss/terran/zerg.
  - frame: The frame number.
  - new_game: Whether this is the first call to the server from this game. true/false.
