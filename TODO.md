### TODO

## General Running Quality of Life
1. Figure out why in certain instances pulling a player's data requries multiple runs
2. Write a method of batch running match predictions - perhaps by a group string input or by tournament from an external api
3. Write a function to automatically convert the percentages from decimal to +/- odds and get our expected EV
4. Streamline the command line output of the data - perhaps output our information in group runs as a CSV file

## Model Improvements
1. If we do not have the surface speed for a tournament then we use the average speed of the surface for calculations
2. Add weights for more recent matches vs older ones, perhaps weight current tournament form more than previous form as well
3. Take into account player's historical preferences by surface speed ranges to adjust odds
4. Write toggles for different new features to allow for ease in backtesting

## Backtesting
1. Take stock of the point I previously reached in backtesting development
2. Write a try catch loop that runs a match 3? times before it gives up and moves onto the next line in case of errors
3. Output expected EV calculations into a df containing historical match and odds data 
4. Write a function placing wagers with unit sizes corresponding to odds in order to calculate our net gain

## Priorities
1. General QOL 2 + 4 - DONE
2. General QOL 3 - DONE
3. General QOL 1
4. Backtesting
5. Model Improvements 1
6. Model Improvemnets 3