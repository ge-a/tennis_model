import pandas as pd
from src.util import score_reader

players = pd.read_csv('data/atp_players.csv')

def get_all_player_names(player_ids):
    first_names = pd.Series([players.loc[players['player_id'] == pid, 'name_first'].values[0] if not players.loc[players['player_id'] == pid, 'name_first'].empty else None for pid in player_ids])
    last_names = pd.Series([players.loc[players['player_id'] == pid, 'name_last'].values[0] if not players.loc[players['player_id'] == pid, 'name_last'].empty else None for pid in player_ids])
    
    return first_names, last_names

def get_player_name(player_id):
    player = players[players['player_id'] == player_id]
    first_name = player['name_first'].iloc[0]
    last_name = player['name_last'].iloc[0]
    return first_name, last_name

### Filter out the stats of the opposing player
def filter_results(df, player_name):
    player_stats = []

    for index, row in df.iterrows():
        if row['winner_name'] == player_name:
            player_stat = {
                'tourney_id': row['tourney_id'],
                'tourney_name': row['tourney_name'], 
                'surface': row['surface'], 
                'tourney_date': row['tourney_date'], 
                'player': row['winner_name'], 
                'opponent': row['loser_name'],
                'score' : row['score'],
                'result': 'win',
                'ace_percentage' : row['w_ace_perc'],
                'df_percentage': row['w_df_perc'],
                'first_in': row['w_first_in'],
                'first_win_perc': row['w_first_win_perc'],
                'second_in': row['w_second_in'],
                'second_win_perc': row['w_second_win_perc'],
                'bp_hold_perc': row['w_bp_hold_perc'],
                'bp_win_perc': row['w_bp_win_perc'],
                'opp_first_in': row['l_first_in'],
                'first_return_win_perc' : row['w_first_return_win_perc'],
                'second_return_win_perc' : row['w_second_return_win_perc'],
                'return_win_perc': row['w_return_win_perc'],
            }
        elif row['loser_name'] == player_name:
            player_stat = {
                'tourney_id': row['tourney_id'],
                'tourney_name': row['tourney_name'], 
                'surface': row['surface'], 
                'tourney_date': row['tourney_date'], 
                'player': row['loser_name'], 
                'opponent': row['winner_name'],
                'score' : row['score'],
                'result': 'loss',
                'ace_percentage' : row['l_ace_perc'],
                'df_percentage': row['l_df_perc'],
                'first_in': row['l_first_in'],
                'first_win_perc': row['l_first_win_perc'],
                'second_in': row['l_second_in'],
                'second_win_perc': row['l_second_win_perc'],
                'bp_hold_perc': row['l_bp_hold_perc'],
                'bp_win_perc': row['l_bp_win_perc'],
                'opp_first_in': row['w_first_in'],
                'first_return_win_perc' : row['l_first_return_win_perc'],
                'second_return_win_perc' : row['l_second_return_win_perc'],
                'return_win_perc': row['l_return_win_perc'],
            }
        player_stats.append(player_stat)

    player_stats_df = pd.DataFrame(player_stats)
    
    return player_stats_df

### Convert to Percentages
def get_percentages(orig_df):
    percentages = {}
    
    percentages['tourney_id'] = orig_df['tourney_id']
    percentages['tourney_name'] = orig_df['tourney_name']
    percentages['surface'] = orig_df['surface']
    percentages['draw_size'] = orig_df['draw_size']
    percentages['tourney_date'] = orig_df['tourney_date']
    percentages['match_num'] = orig_df['match_num']
    percentages['score'] = orig_df['score']
    percentages['winner_id'] = orig_df['winner_id']
    winner_first, winner_last = get_all_player_names(orig_df['winner_id'])
    percentages['winner_name'] = winner_first + ' ' + winner_last
    percentages['winner_seed'] = orig_df['winner_seed']
    percentages['winner_hand'] = orig_df['winner_hand']
    percentages['winner_ht'] = orig_df['winner_ht']
    percentages['winner_age'] = orig_df['winner_age']
    percentages['winner_rank'] = orig_df['winner_rank']
    percentages['winner_rank_points'] = orig_df['winner_rank_points']
    percentages['loser_id'] = orig_df['loser_id']
    loser_first, loser_last = get_all_player_names(orig_df['loser_id'])
    percentages['loser_name'] = loser_first + ' ' + loser_last
    percentages['loser_seed'] = orig_df['loser_seed']
    percentages['loser_hand'] = orig_df['loser_hand']
    percentages['loser_ht'] = orig_df['loser_ht']
    percentages['loser_age'] = orig_df['loser_age']
    percentages['loser_rank'] = orig_df['loser_rank']
    percentages['loser_rank_points'] = orig_df['loser_rank_points']

    percentages['w_ace_perc'] = orig_df['w_ace'] / orig_df['w_svpt']
    percentages['w_df_perc'] = orig_df['w_df'] / (orig_df['w_svpt'] - orig_df['w_1stIn'])
    percentages['w_first_in'] = orig_df['w_1stIn'] / orig_df['w_svpt']
    percentages['w_first_win_perc'] = orig_df['w_1stWon'] / orig_df['w_1stIn']
    percentages['w_second_in'] = 1 - percentages['w_df_perc']
    percentages['w_second_win_perc'] = orig_df['w_2ndWon'] / (orig_df['w_svpt'] - orig_df['w_1stIn'])
    percentages['w_bp_hold_perc'] = orig_df['w_bpSaved'] / orig_df['w_bpFaced']
    percentages['w_bp_win_perc'] = 1 - (orig_df['l_bpSaved'] / orig_df['l_bpFaced'])
    percentages['w_first_return_win_perc'] = 1 - orig_df['l_1stWon'] / orig_df['l_1stIn']
    percentages['w_second_return_win_perc'] = 1 - orig_df['l_2ndWon'] / (orig_df['l_svpt'] - orig_df['l_1stIn'])
    percentages['w_return_win_perc'] = (orig_df['l_bpFaced'] - orig_df['l_bpSaved']) / orig_df['l_SvGms']

    percentages['l_ace_perc'] = orig_df['l_ace'] / orig_df['l_svpt']
    percentages['l_df_perc'] = orig_df['l_df'] / (orig_df['l_svpt'] - orig_df['l_1stIn'])
    percentages['l_first_in'] = orig_df['l_1stIn'] / orig_df['l_svpt']
    percentages['l_first_win_perc'] = orig_df['l_1stWon'] / orig_df['l_1stIn']
    percentages['l_second_in'] = 1 - percentages['l_df_perc']
    percentages['l_second_win_perc'] = orig_df['l_2ndWon'] / (orig_df['l_svpt'] - orig_df['l_1stIn'])
    percentages['l_bp_hold_perc'] = orig_df['l_bpSaved'] / orig_df['l_bpFaced']
    percentages['l_bp_win_perc'] = 1 - percentages['w_bp_hold_perc']
    percentages['l_first_return_win_perc'] = 1 - orig_df['w_1stWon'] / orig_df['w_1stIn']
    percentages['l_second_return_win_perc'] = 1 - orig_df['w_2ndWon'] / (orig_df['w_svpt'] - orig_df['w_1stIn'])
    percentages['l_return_win_perc'] = (orig_df['w_bpFaced'] - orig_df['w_bpSaved']) / orig_df['w_SvGms']
    
    return pd.DataFrame(percentages)

# Player Data Search
def search_player(first_name, last_name, year="2024"):
    atp_data = pd.read_csv(f'data/atp_singles/atp_matches_{year}.csv')
    atp_data['tourney_date'] = pd.to_datetime(atp_data['tourney_date'], format='%Y%m%d')
    df = get_percentages(atp_data)
    player_id = players.loc[(players['name_first'] == first_name) & (players['name_last'] == last_name), 'player_id'].iloc[0]
    data = df[(df['winner_id'] == player_id) | (df['loser_id'] == player_id)]
    data = data.sort_values(by='tourney_date', ascending=False)
    return data

def get_tiebreak_win_percentage(filtered_player_df):
    scores = filtered_player_df['score']
    results = filtered_player_df['result']
    tiebreaks_total = 0
    tiebreaks_won = 0
    for score, result in zip(scores, results):
        print("SCORE: ", score)
        w_games_won, l_games_won, total_games, tiebreaks, w_tiebreaks_won, l_tiebreaks_won, tiebreak_points, num_sets = score_reader(score)
        if result == 'win':
            tiebreaks_won += w_tiebreaks_won
        if result == 'loss':
            tiebreaks_won += l_tiebreaks_won
        print(tiebreaks_won)
        tiebreaks_total += tiebreaks
    return tiebreaks_won / tiebreaks_total

def serve_return_win_perc(first_name, last_name):
    stat_df = filter_results(search_player(first_name, last_name), f"{first_name} {last_name}")
    serve_df = stat_df[['first_in', 'first_win_perc', 'second_win_perc']].dropna()
    serve_df['service_point_win_perc'] = (serve_df['first_in'] * serve_df['first_win_perc']) + ((1 - serve_df['first_in']) * serve_df['second_win_perc'])
    avg_service_point_win_perc = serve_df['service_point_win_perc'].mean()
    
    return_df = stat_df[['opp_first_in', 'first_return_win_perc' ,'second_return_win_perc']].dropna()
    return_df['return_point_win_perc'] = (return_df['opp_first_in'] * return_df['first_return_win_perc']) + ((1 - return_df['opp_first_in']) * return_df['second_return_win_perc'])
    avg_return_point_win_perc = return_df['return_point_win_perc'].mean()
    
    return avg_service_point_win_perc, avg_return_point_win_perc