# app.py
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from scipy.stats import poisson

app = Flask(__name__)

# Load and prepare your data
prem_table = pd.read_csv('C:\\Users\\raaki\\OneDrive\\Documents\\prem\\PremierLeague.csv')
prem_table = prem_table.iloc[9880:]
prem_table = prem_table.drop(prem_table.columns[10:], axis=1)
prem_table = prem_table.drop(['Time', 'Date', 'Season', 'MatchID', 'MatchWeek'], axis=1)

# Calculate average goals scored by home and away teams
home_goals = prem_table.groupby('HomeTeam')['FullTimeHomeTeamGoals']
away_goals = prem_table.groupby('AwayTeam')['FullTimeAwayTeamGoals']
average_home_goals_scored = home_goals.mean()
average_away_goals_scored = away_goals.mean()

# Calculate league average goals
league_average_home_goals = prem_table['FullTimeHomeTeamGoals'].mean()
league_average_away_goals = prem_table['FullTimeAwayTeamGoals'].mean()

# Calculate attack strengths relative to league averages
homeAttackStrength = average_home_goals_scored / league_average_home_goals
awayAttackStrength = average_away_goals_scored / league_average_away_goals

# FIFA team rankings dictionary
FIFA_team_rankings = {
    'Liverpool':84, 'West Ham': 79, 'Bournemouth': 76, 'Burnley': 73,
    'Crystal Palace': 78, 'Watford': 70, 'Tottenham': 81, 'Leicester': 76,
    'Newcastle': 81, 'Man United': 81, 'Arsenal': 83, 'Aston Villa': 80,
    'Brighton': 77, 'Everton': 76, 'Norwich': 71, 'Southampton': 75,
    'Man City': 86, 'Sheffield United': 71, 'Chelsea': 80, 'Wolves': 77,
    'Fulham': 76, 'West Brom': 71, 'Leeds': 74, 'Brentford': 76,
    "Nott'm Forest": 77, 'Luton': 73, 'Ipswich': 74
}

# Create a DataFrame containing team strengths
teamStrength_df = pd.DataFrame({
    'Team': average_home_goals_scored.index,
    'HomeAttackStrength': homeAttackStrength.values,
    'AwayAttackStrength': awayAttackStrength.values
})

# Define the simulation function
def simulate_match(home_team, away_team):
    home_attack = teamStrength_df.loc[teamStrength_df['Team'] == home_team, 'HomeAttackStrength'].values[0]
    away_attack = teamStrength_df.loc[teamStrength_df['Team'] == away_team, 'AwayAttackStrength'].values[0]
    home_expected_goals = home_attack * league_average_home_goals
    away_expected_goals = away_attack * league_average_away_goals

    home_goals = min(poisson.rvs(home_expected_goals), 6)  # cap max goals
    away_goals = min(poisson.rvs(away_expected_goals), 6)  # cap max goals

    return home_goals, away_goals

# Route for the home page
@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    teams = teamStrength_df['Team'].tolist() 
    if request.method == "POST":
        home_team = request.form.get('home_team')
        away_team = request.form.get('away_team')

        if home_team == away_team:
            error = "Please pick 2 different teams to run the simulation."
            return render_template('index.html', teams = teams, error = error)
        
        if not home_team or not away_team:
            error = "Please pick a Home Team and an Away Team"
            return render_template('index.html', teams = teams, error = error)
        
        results = []
        for _ in range(1000):
            home_goals, away_goals = simulate_match(home_team, away_team)
            results.append((home_goals, away_goals))

        # Analyze the outcomes
        home_wins = sum(1 for result in results if result[0] > result[1])
        away_wins = sum(1 for result in results if result[0] < result[1])
        draws = sum(1 for result in results if result[0] == result[1])

        return render_template('results.html', 
                               home_team=home_team, 
                               away_team=away_team, 
                               home_wins=home_wins, 
                               away_wins=away_wins, 
                               draws=draws,
                               results=results)
    
    return render_template('index.html', teams=teams, error=error)

if __name__ == '__main__':
    app.run(debug=True)
