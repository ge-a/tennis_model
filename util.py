def convert_to_space(heading_list):
    cleaned_list = []
    for heading in heading_list:
        cleaned_str = heading.replace("\xa0", " ")
        cleaned_list.append(cleaned_str)
    return cleaned_list

### Score Reader
def score_reader(score):
    w_games_won = 0
    l_games_won = 0
    w_tiebreaks_won = 0
    l_tiebreaks_won = 0
    tiebreaks = 0
    tiebreak_points = []
    num_sets = 1

    i = 1
    for num in score[1:-1]:
        if num == '-':
            w_games_won += int(score[i-1])
            l_games_won += int(score[i+1])
        if num == '(':
            tiebreaks += 1
            if score[i-1] == '7':
                loser = 'l'
                w_tiebreaks_won += 1
            else:
                loser = 'w'
                l_tiebreaks_won += 1

            tiebreak_points.append(f"{loser} {score[i+1]}")
        if num == ' ':
            num_sets += 1
        i += 1
    total_games = w_games_won + l_games_won
    return w_games_won, l_games_won, total_games, tiebreaks, w_tiebreaks_won, l_tiebreaks_won, tiebreak_points, num_sets

def get_american_odds(win_percentage):
    # Convert decimal odds to American odds
    win_percentage = win_percentage * 100
    decimal_odds = 100 / win_percentage
    
    if win_percentage <= 50:
        # Underdog (positive odds)
        american_odds = round((decimal_odds - 1) * 100)
        return f"+{american_odds}"
    else:
        # Favorite (negative odds)
        american_odds = round(100 / (decimal_odds - 1))
        if american_odds == float('inf'):  # Handle 100% probability
            return "-10000"  # Very high negative odds for near-certain events
        return f"-{american_odds}"