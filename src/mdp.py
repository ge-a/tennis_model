import numpy as np

def get_fund_matrix(transition_mat, num_absorbing):
    """
    Get the fundamental matrix for an absorbing markov chain
    
    :param transition_mat: the transition matrix of the absorbing markov chain
    :param num_absorbing: the number of absorbing states in the markov chain
    :return: the fundamental matrix of the absoribing markov chain
    """
    Q_mat = transition_mat[:-num_absorbing, :-num_absorbing]
    R_mat = transition_mat[:-num_absorbing, -num_absorbing:]
    identity_mat = np.eye(len(transition_mat) - num_absorbing)
    N_mat = np.linalg.inv(identity_mat - Q_mat)
    fund_mat = np.dot(N_mat, R_mat)
    return fund_mat

def get_game_transition_matrix(service_pc):
    """
    Create the transition matrix with states:
    ['0-0', '15-0', '0-15', '30-0', '15-15', '0-30', '40-0', '30-15', '
    15-30','0-40', '40-15', '30-30', '15-40', '40-30', '30-40', 'Deuce', '
    Advantage Player 1', 'Advantage Player 2', 'Game Player 1', 'Game Player 2']
    
    :param service_pc: the decimal percentage that a player wins their serve
    :return: transition matrix for a game of tennis
    """
    transition_matrix = np.zeros((20, 20))
    transition_matrix[19][19] = 1
    transition_matrix[18][18] = 1
    return_pc = 1 - service_pc
    service_coords = [(0, 1), (1, 3), (2, 4), (3, 6), (4, 7), (5, 8), (6, 18), (7, 10), (8, 11), (9, 12), (10, 18), (11, 13), (12, 14), (13, 18), (14, 15), (15, 16), (16, 18), (17, 15)]
    return_coords = [(0, 2), (1, 4), (2, 5), (3, 7), (4, 8), (5, 9), (6, 10), (7, 11), (8, 12), (9, 19), (10, 13), (11, 14), (12, 19), (13, 15), (14, 19), (15, 17), (16, 15), (17, 19)]
    for (i, j) , (x, y) in zip(service_coords, return_coords):
        transition_matrix[i, j] = service_pc
        transition_matrix[x, y] = return_pc
    return transition_matrix

def write_tiebreak_transition_matrix():
    """
    Get the coordinates of transition probabilities for a tennis tiebreak with
    states outlined in the in the items list (excluding absorbing states
    Game Player 1, Game Player2)
    
    :return: the coordinates for the transition probabilities for each players serve and return
    """
    items = ["0-0", "1-0", "0-1", "2-0", "1-1", "0-2", "3-0", "2-1", "1-2", "0-3",
             "4-0", "3-1", "2-2", "1-3", "0-4", "5-0", "4-1", "3-2", "2-3", "1-4",
             "0-5", "6-0", "5-1", "4-2", "3-3", "2-4", "1-5", "0-6", "6-1", "5-2",
             "4-3", "3-4", "2-5", "1-6", "6-2", "5-3", "4-4", "3-5", "2-6", "6-3",
             "5-4", "4-5", "3-6", "6-4", "5-5", "4-6", "6-5", "5-6", "6-6", 
             "Ad Player 1", "Ad Player 2"]
    item_index_dict = {item: index for index, item in enumerate(items)}
    p1_serve_coords = []
    p2_return_coords = []
    p2_serve_coords = []
    p1_return_coords = []
    server = True
    
    for idx, item in enumerate(items):
        if item[0].isdigit():
            p1_points = int(item[0])
            p2_points = int(item[-1])
            next_item = items[idx + 1]
            if next_item[0].isdigit() and idx < len(items) - 2:
                next_point_sum = int(next_item[0]) + int(next_item[-1])
            if p1_points + 1 < 7 and p2_points + 1 < 7:
                p1_win_coords = (idx, item_index_dict[f"{p1_points + 1}-{p2_points}"])
                p2_win_coords = (idx, item_index_dict[f"{p1_points}-{p2_points + 1}"])
            elif p1_points + 1 == 7 and p2_points + 1 < 7:
                p1_win_coords = (idx, 51)
                p2_win_coords = (idx, item_index_dict[f"{p1_points}-{p2_points + 1}"])
            elif p1_points + 1 < 7 and p2_points + 1 == 7:
                p1_win_coords = (idx, item_index_dict[f"{p1_points + 1}-{p2_points}"])
                p2_win_coords = (idx, 52)
            elif p1_points + 1 == 7 and p2_points + 1 == 7:
                p1_win_coords = (idx, 49)
                p2_win_coords = (idx, 50)
        else:
            if item[-1] == "1":
                p1_win_coords = (idx, 51)
                p2_win_coords = (idx, 44)
            elif item[-1] == "2":
                p1_win_coords = (idx, 44)
                p2_win_coords = (idx, 52)
        if server:
            p1_serve_coords.append(p1_win_coords)
            p2_return_coords.append(p2_win_coords)
            if next_item[0] == "A" or next_point_sum % 4 == 1 :
                server = False
        elif not server:
            p2_serve_coords.append(p2_win_coords)
            p1_return_coords.append(p1_win_coords)
            if next_point_sum % 4 == 3:
                server = True
            
    return p1_serve_coords, p2_return_coords, p2_serve_coords, p1_return_coords

def get_tiebreak_transition_matrix(p1_service_perc, p2_service_perc):
    """
    Create the transition matrix with states:
    ["0-0", "1-0", "0-1", "2-0", "1-1", "0-2", "3-0", "2-1", "1-2", "0-3",
    "4-0", "3-1", "2-2", "1-3", "0-4", "5-0", "4-1", "3-2", "2-3", "1-4",
    "0-5", "6-0", "5-1", "4-2", "3-3", "2-4", "1-5", "0-6", "6-1", "5-2",
    "4-3", "3-4", "2-5", "1-6", "6-2", "5-3", "4-4", "3-5", "2-6", "6-3",
    "5-4", "4-5", "3-6", "6-4", "5-5", "4-6", "6-5", "5-6", "6-6", 
    "Ad Player 1", "Ad Player 2", "Game Player 1", "Game Player 2"]
    
    :param p1_service_pc: the decimal percentage that a player 1 wins their serve
    :param p1_service_pc: the decimal percentage that a player 2 wins their serve
    :return: transition matrix for a tiebreak in a tennis match
    """
    
    transition_matrix = np.zeros((53, 53))
    transition_matrix[52][52] = 1
    transition_matrix[51][51] = 1
    
    p1_serve_coords, p2_return_coords, p2_serve_coords, p1_return_coords = write_tiebreak_transition_matrix()
    
    p1_return_perc = 1 - p2_service_perc
    p2_return_perc = 1 - p1_service_perc
    
    for t in range(0, len(p2_serve_coords)):
        if t < 24:
            n, m = p1_serve_coords[t]
            o, p = p2_return_coords[t]
        i, j = p2_serve_coords[t]
        x, y = p1_return_coords[t]
        
        transition_matrix[i, j] = p2_service_perc
        transition_matrix[x, y] = p1_return_perc
        transition_matrix[n, m] = p1_service_perc
        transition_matrix[o, p] = p2_return_perc
    
    return transition_matrix

def get_set_transition_matrix(p1_service_game_perc, p2_service_game_perc):
    """
    Create the transition matrix with states:
    ["0-0", "1-0", "0-1", "2-0", "1-1", "0-2", "3-0", "2-1", "1-2", "0-3", "4-0", "3-1", 
    "2-2", "1-3", "0-4", "5-0", "4-1", "3-2", "2-3", "1-4",  "0-5", "5-1", "4-2", "3-3", 
    "2-4", "1-5", "5-2", "4-3", "3-4", "2-5", "5-3", "4-4", "3-5", "5-4", "4-5", "5-5", 
    "6-5", "5-6", "Set Player 1", "Set Player 2", "6-6"]
    
    :param p1_service_game_perc: the decimal percentage that a player 1 wins a game
    :param p2_service_game_perc: the decimal percentage that a player 2 wins a game
    :return: transition matrix for a set in a tennis match
    """
    transition_matrix = np.zeros((41, 41))
    transition_matrix[40][40] = 1
    transition_matrix[39][39] = 1
    transition_matrix[38][38] = 1
    
    p1_return_game_perc = 1 - p2_service_game_perc
    p2_return_game_perc = 1 - p1_service_game_perc
    
    p1_serve_coords = [(0, 1), (3, 6), (4, 7), (5, 8), (10, 15), (11, 16), (12, 17), (13, 18), (14, 19), (21, 38), (22, 26), (23, 27), (24, 28), (25, 29), (30, 38), (31, 33), (32, 34), (35, 36)]
    p2_return_coords = [(0, 2), (3, 7), (4, 8), (5, 9), (10, 16), (11, 17), (12, 18), (13, 19), (14, 20), (21, 26), (22, 27), (23, 28), (24, 29), (25, 39), (30, 33), (31, 34), (32, 39), (35, 37)]
    
    p2_serve_coords = [(1, 4), (2, 5), (6, 10), (7, 11), (8, 12), (9, 13), (15, 21), (16, 22), (17, 23), (18, 24), (19, 25), (20, 39), (26, 30), (27, 31), (28, 32), (29, 39), (33, 35), (34, 39), (36, 40), (37, 39)]
    p1_return_coords = [(1, 3), (2, 4), (6, 11), (7, 12), (8, 13), (9, 14), (15, 38), (16, 21), (17, 22), (18, 23), (19, 24), (20, 25), (26, 38), (27, 30), (28, 31), (29, 32), (33, 38), (34, 35), (36, 38), (37, 40)]
    
    for t in range(0, len(p1_return_coords)):
        if t < 18:
            i, j = p1_serve_coords[t]
            x, y = p2_return_coords[t]
        n, m = p2_serve_coords[t]
        o, p = p1_return_coords[t]
        
        transition_matrix[i, j] = p1_service_game_perc
        transition_matrix[x, y] = p2_return_game_perc
        transition_matrix[n, m] = p2_service_game_perc
        transition_matrix[o, p] = p1_return_game_perc
    
    return transition_matrix

def get_set_win_perc(p1_service_perc, p2_service_perc):
    """
    Get the percentage chance of each of 2 players to win a set of tennis
    given their service point win percentages
    
    :param p1_service_perc: the decimal percentage winrate of player 1 on their serve
    :param p2_service_perc: the decimal percentage winrate of player 2 on their serve
    :return: win percentages for a set of tennis for each player
    """
    p1_game_transition_matrix = get_game_transition_matrix(p1_service_perc)
    p2_game_transition_matrix = get_game_transition_matrix(p2_service_perc)
    
    p1_fund_matrix = get_fund_matrix(p1_game_transition_matrix, 2)
    p2_fund_matrix = get_fund_matrix(p2_game_transition_matrix, 2)
    
    p1_service_game_perc = p1_fund_matrix[0][0]
    p2_service_game_perc = p2_fund_matrix[0][0]
    
    set_transition_matrix = get_set_transition_matrix(p1_service_game_perc, p2_service_game_perc)
    set_fund_matrix = get_fund_matrix(set_transition_matrix, 3)
    tiebreak_perc = set_fund_matrix[0][-1]
    tiebreak_transition_matrix = get_tiebreak_transition_matrix(p1_service_perc, p2_service_perc)
    tiebreak_fund_matrix = get_fund_matrix(tiebreak_transition_matrix, 2)
    p1_tiebreak_winner = tiebreak_fund_matrix[0][0]
    p2_tiebreak_winner = tiebreak_fund_matrix[0][1]

    p1_win_perc = set_fund_matrix[0][0] + tiebreak_perc * p1_tiebreak_winner
    p2_win_perc = set_fund_matrix[0][1] + tiebreak_perc * p2_tiebreak_winner
    
    return p1_win_perc, p2_win_perc

def get_match_prob(p1_service_perc, p2_service_perc):
    """
    Get the percentage chance of each of 2 players to win a matfch of tennis 
    given their service point win percentages and how many games are in the match
    
    :param p1_service_perc: the decimal percentage winrate of player 1 on their serve
    :param p2_service_perc: the decimal percentage winrate of player 2 on their serve
    :return: win percentages for a match of tennis for each player
    """
    p1_set_win_p1_serves_first, p2_set_win_p1_serves_first = get_set_win_perc(p1_service_perc, p2_service_perc)
    p2_set_win_p2_serves_first, p1_set_win_p2_serves_first = get_set_win_perc(p2_service_perc, p1_service_perc)
    
    p1_win_serving_first = (
        # Win in straight sets
        p1_set_win_p1_serves_first * p1_set_win_p2_serves_first +
        # Win in three sets
        p1_set_win_p1_serves_first * p2_set_win_p2_serves_first * p1_set_win_p1_serves_first +
        p2_set_win_p1_serves_first * p1_set_win_p2_serves_first * p1_set_win_p1_serves_first)
    
    # Player 2 serving first scenarios
    p1_win_serving_second = (
        # Win in straight sets
        p1_set_win_p2_serves_first * p1_set_win_p1_serves_first +
        # Win in three sets
        p1_set_win_p2_serves_first * p2_set_win_p1_serves_first * p1_set_win_p2_serves_first +
        p2_set_win_p2_serves_first * p1_set_win_p1_serves_first * p1_set_win_p2_serves_first)
    
    p2_win_serving_first = (
            # Win in straight sets
            p2_set_win_p2_serves_first * p2_set_win_p1_serves_first +
            # Win in three sets
            p2_set_win_p2_serves_first * p1_set_win_p1_serves_first * p2_set_win_p2_serves_first +
            p1_set_win_p2_serves_first * p2_set_win_p1_serves_first * p2_set_win_p2_serves_first)
        
    # Player 2's scenarios when serving second
    p2_win_serving_second = (
        # Win in straight sets
        p2_set_win_p1_serves_first * p2_set_win_p2_serves_first +
        # Win in three sets
        p2_set_win_p1_serves_first * p1_set_win_p2_serves_first * p2_set_win_p1_serves_first +
        p1_set_win_p1_serves_first * p2_set_win_p2_serves_first * p2_set_win_p1_serves_first)
    
    p1_win_prob = (p1_win_serving_first + p1_win_serving_second) / 2
    p2_win_prob = (p2_win_serving_first + p2_win_serving_second) / 2
    
    return p1_win_prob, p2_win_prob