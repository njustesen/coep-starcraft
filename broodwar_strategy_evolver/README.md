# Brood War Strategy Evolver
This project contains an implementation of Continual Online Evolution, a build order forward model for StarCraft: Brood War (only for Protoss and Terran) and a heuristic for build order planning. This can be used as an online build order planner for UAlbertaBot using this extension https://github.com/njustesen/ualbertabot to the ProductionManager. 

## How to use as Online Planner in StarCraft: Brood War
- Read guide here: https://github.com/njustesen/broodwar_strategy_server

## Test Continual Online Evolution
- You can test COE with the file evolution/evolution_test.py. This runs the evolution once using a given game state and comes up with a candidate build order to counter the opponents units. Run it a few times to see that it does not always come up with the same strategy.

## Test forward model
- You can test the forward model with the file starcraft/forward_model_test2.py. This file contains a suite of tests for the forward model and foreach test prints out the result of performing a build order. Every ignored build is printed with an error message. 

## Test the heuristic
- You can test the heuristic with the file starcraft/adv_heuristics_test.py. It prints the heuristic of a given game state.
