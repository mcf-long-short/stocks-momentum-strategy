# Implementing a momentum strategy on the stock market 

## Introduction

In his book ["Stocks on the Move: Beating the Market with Hedge Fund Momentum Strategy"](https://www.amazon.com/Stocks-Move-Beating-Momentum-Strategies/dp/1511466146), Andreas F. Clenow, presents his trading rules (chapter: "A Complete Momentum Trading Strategy", p91 in pdf): **he trades once a week, always on the same day, he ranks stocks in the S&P 500 based on momentum, and calculates the position size using the 20-day Average True Range of each stock, multiplied by 10 basis points of the portfolio value etc.**

Project goals: 

* Describing and understanding his trading algorithm in detail.  
* Implementing the algorithm in Python, using SP100 and rolling 90-day momentum.  
* How changing the momentum rolling window length affects the results? 
* Determining the drawbacks of such investment strategy and backing it up with current literature results.  
* Considering some interesting extensions and additions that the author considers for momentum strategy.  
* Summarizing the result and findings and drawing a final conclusions on such trading strategy.  

References: 
* Clenow, A. (2015). Stocks on the Move: Beating the Market with Hedge Fund Momentum Strategies. 

This repository represents group project work for course in `Quantitative Investments` for advanced degree [Masters in Computational Finance, Union University](http://mcf.raf.edu.rs/).
