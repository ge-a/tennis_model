import numpy as np
import pandas as pd
import re
from scrape import DataScraper, PlayerDataScraper

class TennisDataScraper:
    """Base class for tennis data scraping with common datasets"""
    
    # Shared data storage - will be initialized only once
    _shared_data = {
        'surface_data': None,
        'elo_data': None,
        'y_elo_data': None,
        'initialized': False
    }
    
    def __init__(self):
        # Initialize common datasets only if they haven't been loaded yet
        self._ensure_data_initialized()
    
    @classmethod
    def _ensure_data_initialized(cls):
        """Ensure the shared data is initialized"""
        if not cls._shared_data['initialized']:
            print("Initializing shared tennis data (surface speeds and ELO ratings)...")
            temp_scraper = DataScraper()
            cls._shared_data['surface_data'] = temp_scraper.get_surface_speed()
            cls._shared_data['elo_data'], cls._shared_data['y_elo_data'] = temp_scraper.get_elo_data()
            cls._shared_data['initialized'] = True
    
    @property
    def surface_data(self):
        """Access the shared surface data"""
        self._ensure_data_initialized()
        return self._shared_data['surface_data']
    
    @property
    def elo_data(self):
        """Access the shared ELO data"""
        self._ensure_data_initialized()
        return self._shared_data['elo_data']
    
    @property
    def y_elo_data(self):
        """Access the shared yearly ELO data"""
        self._ensure_data_initialized()
        return self._shared_data['y_elo_data']
    
    def get_adjusted_elo(self):
        """Calculate adjusted ELO ratings by combining regular and yearly ELO data"""
        combined_elo = pd.merge(
            self.elo_data[['Elo Rank', 'Player', 'Elo', 'Log diff']],
            self.y_elo_data[['Rank', 'Player', 'yElo']],
            on='Player',
            how='left')

        # Modify Player names to remove all spaces after the first
        def compress_name(name):
            parts = name.split()
            if len(parts) > 2:
                return parts[0] + ' ' + ''.join(parts[1:])
            return name

        combined_elo['Player'] = combined_elo['Player'].apply(compress_name)

        combined_elo['Average Elo'] = combined_elo.apply(
            lambda row: (float(row['Elo']) + float(row['yElo'])) / 2 if pd.notnull(row['yElo']) else float(row['Elo']),
            axis=1)

        return combined_elo

class PlayerServeReturnStats(TennisDataScraper):
    """Class for analyzing player's serve and return statistics"""
    
    def __init__(self, first_name, last_name, num_weeks, current_tournament, career=False):
        # Call parent class's __init__ to ensure common data is initialized
        super().__init__()
        
        self.first_name = first_name
        self.last_name = last_name
        # Initialize player-specific data
        player_scraper = PlayerDataScraper(first_name, last_name)
        if career:
            self.all_results = player_scraper.get_all_results()
        else:
            self.recent_results = player_scraper.get_recent_results()
        self.num_weeks = num_weeks
        self.current_tournament = current_tournament
        
    def gather_last_x_weeks(self, num_weeks=-1):
        abbreviated_data = self.recent_results[["Match", "Date", "Scoreline", "vRk", "SPW", "RPW"]]
        abbreviated_data = abbreviated_data[~abbreviated_data["Match"].str.contains("Davis Cup", na=False)]
        abbreviated_data = abbreviated_data[~abbreviated_data["Match"].str.contains("Laver Cup", na=False)]
        if num_weeks == -1:
            return abbreviated_data
        most_recent_date = self.recent_results["Date"].max()
        cutoff_date = most_recent_date - pd.Timedelta(weeks=num_weeks)
        return abbreviated_data[abbreviated_data["Date"] >= cutoff_date]
    
    def gather_from_match_date(self, match_date):
        all_results = self.all_results[["Match", "Date", "Scoreline", "vRk", "SPW", "RPW"]]
        all_results = all_results[~all_results["Match"].str.contains("Davis Cup", na=False)]
        all_results = all_results[~all_results["Match"].str.contains("Laver Cup", na=False)]
        lower_bound = match_date - pd.Timedelta(days=7 * self.num_weeks)
        results_from_match_date = all_results[(all_results["Date"] > lower_bound) & (all_results["Date"] <= match_date)]
        return results_from_match_date
    
    def normalize_data(self, match_date=None):
        abbreviated_data = self.gather_last_x_weeks(num_weeks=self.num_weeks) if match_date is None else self.gather_from_match_date(match_date)
        
        for index, row in abbreviated_data.iterrows():
            tournament = row["Match"]
            match = re.search(r"\d{4}\s+(.+?)\s+\S+$", tournament)
            if match:
                tournament_name = match.group(1)
            surface_speed = self.surface_data.loc[self.surface_data["Tournament"].str.contains(tournament_name, case=False), "Surface Speed"]
            
            if not surface_speed.empty:
                surface_speed = surface_speed.iloc[0]
            else:
                print("No Surface Speed Found for: ", tournament_name)
                surface_speed = 1  # TODO: get an average surface speed based on surface type

            spw_num = float(row["SPW"][:-1])
            rpw_num = float(row["RPW"][:-1])

            spw = spw_num / float(surface_speed)
            rpw = rpw_num * float(surface_speed)
            
            abbreviated_data.at[index, "SPW"] = spw
            abbreviated_data.at[index, "RPW"] = rpw
        return abbreviated_data
    
    def estimate_spw_rpw(self, match_date=None):
        """
        Estimate service and return points won percentages adjusted for both surface speed
        and the quality of opponents faced.
        """
        normalized_data = self.normalize_data(match_date=match_date)
        
        # Get all players' ELO data
        all_players_elo = self.get_adjusted_elo()
        
        # Calculate average tour ELO for reference
        avg_tour_elo = all_players_elo['Average Elo'].sort_values(ascending=False).head(300).mean()
        # Extract opponent ELOs and calculate average
        opponent_elos = []
        
        # TODO: Add a weighting difference based on whether or not they won or lost against the opponent
        for index, row in normalized_data.iterrows():
            # Extract opponent information from the match description
            match_info = row["Scoreline"]
            pattern = r"(?:\(?\d+\)?\s*)?([A-Za-z]+(?:\s[A-Za-z]+)?)\s*\[[A-Z]+\]"
            opponent_match = re.search(pattern, match_info)
            if opponent_match:
                def normalize_name(name):
                    parts = name.split()
                    if len(parts) > 2:
                        return parts[0] + ' ' + ''.join(parts[1:])
                    return name
                opponent_name = normalize_name(opponent_match.group(1).strip())

                # Look up opponent's ELO
                opponent_elo_row = all_players_elo[all_players_elo['Player'] == opponent_name]
                if not opponent_elo_row.empty:
                    opponent_elo = float(opponent_elo_row['Average Elo'].iloc[0])
                    opponent_elos.append(opponent_elo)
                    
                    # Store opponent ELO for potential debugging
                    normalized_data.at[index, "Opp_ELO"] = opponent_elo
        
        # Calculate average opponent ELO
        avg_opponent_elo = np.mean(opponent_elos) if opponent_elos else avg_tour_elo
        
        # Calculate opponent quality adjustment factor
        # For every 100 ELO points above average, scale performance down by 5%
        # For every 100 ELO points below average, scale performance up by 5%
        opponent_quality_factor = 1 - ((avg_tour_elo - avg_opponent_elo) / 100) * 0.05
        
        # Limit adjustment factor to reasonable range (0.6 to 1.4)
        opponent_quality_factor = max(0.8, min(1.2, opponent_quality_factor))
        
        # Calculate raw averages
        spw = np.average(normalized_data["SPW"])
        rpw = np.average(normalized_data["RPW"])
        print("avg opp elo: ", avg_opponent_elo)
        print("qual factor: ", opponent_quality_factor)
        # Apply opponent quality adjustment
        adjusted_spw = spw * opponent_quality_factor
        adjusted_rpw = rpw * opponent_quality_factor
        
        # Apply current surface adjustment
        current_surface_speed = self.surface_data.loc[self.surface_data["Tournament"] == self.current_tournament, "Surface Speed"]
        if current_surface_speed.empty:
            current_surface_speed = 1
        else:
            current_surface_speed = float(current_surface_speed.iloc[0])
        
        # Return surface-adjusted values
        return adjusted_spw * current_surface_speed, adjusted_rpw / current_surface_speed