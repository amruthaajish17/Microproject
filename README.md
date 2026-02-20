# Microproject
A Python-based MILP optimization model using PuLP and Folium to design a cost-minimizing, interactive emergency supply distribution network.

# Campus City Emergency Supply Distribution 🚚📦
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Optimization](https://img.shields.io/badge/Optimization-MILP-green)
![Libraries](https://img.shields.io/badge/Libraries-PuLP%20%7C%20Folium%20%7C%20Pandas-orange)

## 📌 Project Overview
This project focuses on designing an optimal supply distribution network for essential resources across campus facilities. Transitioning from an inefficient ad-hoc system, this computational implementation uses **Mixed-Integer Linear Programming (MILP)** to determine the optimal warehouse locations and distribution routes. 

The primary objective is to minimize total annual costs while strictly meeting all facility demands, respecting warehouse capacity constraints, and operating within a $1,500,000 annual budget.

## 📂 Repository Structure
As per the project guidelines, this repository is organized as follows:
```text
📦 campus-supply-chain-optimization
 ┣ 📂 src
 ┃ ┗ 📜 campus_logistics_optimization.ipynb  # Main executable Python notebook
 ┣ 📂 data
 ┃ ┣ 📜 demands.csv
 ┃ ┣ 📜 facilities.csv
 ┃ ┣ 📜 transportation_costs.csv
 ┃ ┗ 📜 warehouses.csv
 ┣ 📜 README.md                              # Project documentation
 ┗ 📜 Report.pdf                             # Final technical report
