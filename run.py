import pandas as pd
from tqdm import tqdm
from datetime import date
from manip import PlayerServeReturnStats
from mdp import get_match_prob
from util import get_american_odds

def predict_match(player1_first, player1_last, player2_first, player2_last, current_tournament, num_weeks=-1, match_date=None):
    player1_stats = PlayerServeReturnStats(player1_first, player1_last, num_weeks, current_tournament)
    player2_stats = PlayerServeReturnStats(player2_first, player2_last, num_weeks, current_tournament)
    
    elo_table = player1_stats.get_adjusted_elo()
    player1_avg_elo = elo_table.loc[elo_table["Player"] == f"{player1_first} {player1_last}", "Average Elo"].values[0]
    player2_avg_elo = elo_table.loc[elo_table["Player"] == f"{player2_first} {player2_last}", "Average Elo"].values[0]
    elo_diff = player1_avg_elo - player2_avg_elo
    
    win_probability = 1 / (1 + 10 ** (-elo_diff / 400))
    
    min_weight = 0.25
    max_weight = 0.75
    weight_range = max_weight - min_weight
    
    # Player 1's weight is higher when they have higher win probability
    player1_weight = min_weight + (win_probability * weight_range)
    player2_weight = 1 - player1_weight

    player1_spw, player1_rpw = player1_stats.estimate_spw_rpw(match_date=match_date)
    player2_spw, player2_rpw = player2_stats.estimate_spw_rpw(match_date=match_date)
    
    # maybe adjust the way combined spw is calculated to take into account ranking difference
    player1_combined_spw = (player1_weight * player1_spw) + ((1 - player1_weight) * (100 - player2_rpw))
    player2_combined_spw = (player2_weight * player2_spw) + ((1 - player2_weight) * (100 - player1_rpw))
    
    return get_match_prob(player1_combined_spw / 100, player2_combined_spw / 100)

def batch_predeiction(match_data, num_weeks=-1):
    """
    Batch process multiple matches through the predict_match function
    
    Parameters:
    -----------
    matches_data : list of tuples
        Tuples of format (player1_first, player1_last, player2_first, player2_last, current_tournament, match_date or None)
        
    num_weeks : int, default=-1
        Number of weeks of data to use
        
    Returns:
    --------
    pandas DataFrame with match predictions and player information
    """
    if all(len(entry) == 5 for entry in match_data):
        columns = ['player1_first', 'player1_last', 'player2_first', 'player2_last', 'current_tournament']
        match_df = pd.DataFrame(match_data, columns=columns)
        match_df['match_date'] = None
    elif all(len(entry) == 6 for entry in match_data):
        columns = ['player1_first', 'player1_last', 'player2_first', 'player2_last', 'current_tournament', 'match_date']
        match_df = pd.DataFrame(match_data, columns=columns)
    else:
        raise ValueError("Each entry in match_data must be a tuple of length 5 or 6.")
    
    match_df['p1_win_prob'] = None
    match_df['p2_win_prob'] = None
    
    def process_match(row):
        p1_first, p1_last = row[0], row[1]
        p2_first, p2_last = row[2], row[3]
        current_tournament = row[4]
        if len(row) > 5:
            match_date = row[5]
        
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            try:
                result = predict_match(
                    p1_first, p1_last, 
                    p2_first, p2_last, 
                    current_tournament, 
                    num_weeks, 
                    match_date)
                p1_win_prob = result[0]
                p2_win_prob = result[1]
                
                return p1_win_prob, p2_win_prob
            except Exception as e:
                if attempts == max_attempts:
                    print(f"FAILED AFTER {max_attempts} ATTEMPTS: {p1_first} {p1_last} vs {p2_first} {p2_last}: {str(e)}")
                    return None, None
                else:
                    print(f"Attempt {attempts} failed for {p1_first} {p1_last} vs {p2_first} {p2_last}: {str(e)} - Retrying...")
                    attempts += 1
    
    results = []
    for idx, row in tqdm(match_df.iterrows(), total=match_df.shape[0], desc="Processing matches"):
        result = process_match(row)
        results.append(result)
    
    # Concurrent processing 
    """
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(tqdm(
            executor.map(process_match, [row for _, row in df.iterrows()]),
            total=len(df),
            desc="Processing matches"
        ))
    """
    for i, (p1_win_prob, p2_win_prob) in enumerate(results):
        match_df.loc[i, 'p1_win_prob'] = p1_win_prob
        match_df.loc[i, 'p2_win_prob'] = p2_win_prob
        match_df.loc[i, 'p1_odds'] = get_american_odds(p1_win_prob)
        match_df.loc[i, 'p2_odds'] = get_american_odds(p2_win_prob)
    
    return match_df

def main():
    tourney = "Hamburg"
    matches = [
        ("Flavio", "Cobolli", "Roberto", "BautistaAgut", tourney),
        ("Tomas", "MartinEtcheverry", "Jiri", "Lehecka", tourney),]
    
    today = date.today().isoformat()
    
    results_df = batch_predeiction(
        match_data=matches,
        num_weeks=24)
    
    results_df.to_csv(f"match_data/match_predictions_{today}.csv", index=False)

if __name__ == "__main__":
    main()
