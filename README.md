# AssortedBettingTools
An assortment of the betting tools I made. 

## 🥅 Goalie Performance Analyzer (v1.4)
(found under nhl_goalie folder)

A Python-based desktop application designed for visualizing and analyzing NHL goaltender statistics. This tool processes JSON data to provide interactive trend analysis and statistical distribution modeling for Shots Against, Saves, and Goals Against.
Key Features
* Interactive GUI: Built with tkinter for easy goalie selection and view toggling.
* Trend Visualization: Plot performance metrics over time with options for combined or separated trend lines.
* Gaussian Distribution Analysis: Generates histograms and normal distribution curves ($\mu, \sigma$) for performance consistency analysis.
* Reference Value Logic: Allows users to input a custom reference value (e.g., a betting line or median) to dynamically calculate the percentage of games falling Above or Below that threshold.
  
### Dependencies:
* tkinter
* matplotlib
* numpy

### Use Cases:
* Goalie Props
* Goals totals (By team of goaltender)

## Quickstart
```
run 'goalie_dump.bat' to generate the goalie data required for the program to run. [Takes a few minutes]

run 'goalie_view.bat' to run the data viewer.
```

## 🏒 Player Performance Analyzer (v1.3)

(found under nhl_player folder)

A Python-based desktop application designed for visualizing and analyzing NHL player statistics on a game-by-game basis. This tool processes JSON data to provide interactive statistical distribution modeling for Points, Goals, Assists, and Shots.
Key Features
* Interactive GUI: Built with tkinter for seamless player selection and metric switching.
* Game-by-Game Distribution: Generates histograms and normal distribution curves ($\mu, \sigma$) to visualize a player's consistency and frequency of performance per game.
* Standard Deviation Analysis: Automatically plots and calculates $\pm 1\sigma$ and $\pm 2\sigma$ ranges to identify statistical outliers.
* Probability Calculator: Includes a user input field to set a custom reference value (e.g., a betting line of "0.5 goals"), dynamically calculating the percentage likelihood of the player performing Above or Below that number based on their season history.

## Dependencies:
* tkinter
* matplotlib
* numpy
* scipy

## Use Cases:
* Player Props (Shots on Goal, Points, Goal Scorer)
* Fantasy Hockey
* Consistency Analysis
  
## Quickstart
```
Run 'data_dump.bat'
Run 'player_view.bat' to launch the analyzer.
```
