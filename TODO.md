### TODO

## General Running Quality of Life
1. Figure out why in certain instances pulling a player's data requries multiple runs

## Model Improvements
1. If we do not have the surface speed for a tournament then we use the average speed of the surface for calculations
2. Add weights for more recent matches vs older ones, perhaps weight current tournament form more than previous form as well
3. Take into account player's historical preferences by surface speed ranges to adjust odds
4. Write toggles for different new features to allow for ease in backtesting

## Additional Lines
1. Get the percentage and odds for a singular game
2. Get the percentage and oods for a singular set
3. Get the odds distribution for different game spreads and total games

## Backtesting
1. Take stock of the point I previously reached in backtesting development
2. Write a try catch loop that runs a match 3? times before it gives up and moves onto the next line in case of errors
3. Output expected EV calculations into a df containing historical match and odds data 
4. Write a function placing wagers with unit sizes corresponding to odds in order to calculate our net gain

## Priorities
1. Add BO5
2. General QOL 1
3. Backtesting
4. Model Improvements 1
5. Model Improvemnets 3