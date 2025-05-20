from manip import PlayerServeReturnStats
from mdp import get_match_prob

def predict_match(player1_first, player1_last, player2_first, player2_last, current_tournament, num_weeks=-1, match_date=None):
    player1_stats = PlayerServeReturnStats(player1_first, player1_last, num_weeks, current_tournament)
    player2_stats = PlayerServeReturnStats(player2_first, player2_last, num_weeks, current_tournament)
    
    elo_table = player1_stats.get_adjusted_elo()
    player1_avg_elo = elo_table.loc[elo_table["Player"] == f"{player1_first} {player1_last}", "Average Elo"].values[0]
    player2_avg_elo = elo_table.loc[elo_table["Player"] == f"{player2_first} {player2_last}", "Average Elo"].values[0]
    elo_diff = player1_avg_elo - player2_avg_elo
    print("Player 1 elo: ", player1_avg_elo)
    print("Player 2 elo: ", player2_avg_elo)
    print("ELO diff: ", elo_diff)
    
    # Use a sigmoid function to convert ELO difference to a weight between 0.3 and 0.7
    # A positive diff means player1 is stronger, negative means player2 is stronger
    # The 400 divisor is common in ELO systems (probability of win is ~10x at 400 points difference)
    win_probability = 1 / (1 + 10 ** (-elo_diff / 400))
    
    # Scale the weights based on win probability
    # Map the win probability [0,1] to a weight range [min_weight, max_weight]
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

def main():
    p1_first = "Sebastian"
    p1_last = "Ofner"

    p2_first = "Nuno"
    p2_last = "Borges"

    current_tournament = "Geneva"

    # Assuming predict_match is defined or imported somewhere
    p1_win_perc, p2_win_perc = predict_match(
        p1_first, p1_last, p2_first, p2_last, current_tournament, num_weeks=24
    )

    print("The probability of player 1 winning the match is:", p1_win_perc)
    print("The probability of player 2 winning the match is:", p2_win_perc)

    print("The odds for player 1 winning the match are:", 1 / p1_win_perc)
    print("The odds for player 2 winning the match are:", 1 / p2_win_perc)


if __name__ == "__main__":
    main()
