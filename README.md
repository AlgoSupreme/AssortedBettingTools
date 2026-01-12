# AssortedBettingTools
An assortment of the betting tools I made. Mostly AI generated code but fixed or optimized by me. 50% AI/ 50% hand programmed

## 🥅 Goalie Performance Analyzer (v1.4)
(found under goalie folder)

A Python-based desktop application designed for visualizing and analyzing NHL goaltender statistics. This tool processes JSON data to provide interactive trend analysis and statistical distribution modeling for Shots Against, Saves, and Goals Against.
Key Features
* Interactive GUI: Built with tkinter for easy goalie selection and view toggling.
* Trend Visualization: Plot performance metrics over time with options for combined or separated trend lines.
* Gaussian Distribution Analysis: Generates histograms and normal distribution curves ($\mu, \sigma$) for performance consistency analysis.
* Reference Value Logic: Allows users to input a custom reference value (e.g., a betting line or median) to dynamically calculate the percentage of games falling Above or Below that threshold.
  
Dependencies:
* tkinter
* matplotlib
* numpy
