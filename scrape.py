import numpy as np
import pandas as pd
import time
import re
from typing import Literal
from selenium import webdriver
from bs4 import BeautifulSoup
from util import convert_to_space

class DataScraper:
    def scrape_html(self, url):
        driver = webdriver.Chrome()
        driver.get(url)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        driver.quit()
        return soup
    
    def get_url_tables(self, stat_url):
        stat_html = self.scrape_html(stat_url)
        stat_all_tables = stat_html.find_all("table")
        stat_table = stat_all_tables[-1]
        stat_headers = convert_to_space([th.text.strip() for th in stat_table.find_all("th")])
        stat_rows = []
        for tr in stat_table.find_all("tr"):
            cells = [td.text.strip() for td in tr.find_all("td")]
            if cells:
                stat_rows.append(cells)
                
        return stat_rows, stat_headers
    
    def get_surface_speed(self):
        serve_url = "https://tennisabstract.com/reports/atp_surface_speed.html"
        surface_rows, surface_headers = self.get_url_tables(serve_url)
        surface_cols = [f"{col}_{i}" if surface_headers.count(col) > 1 else col for i, col in enumerate(surface_headers)]
        surface_df = pd.DataFrame(surface_rows, columns=surface_cols)
        surface_df = surface_df.dropna()
        surface_df = surface_df.replace(["", " ", None], np.nan)
        return surface_df
    
    def get_elo_data(self):
        elo_url = "https://tennisabstract.com/reports/atp_elo_ratings.html"
        y_elo_url = "https://tennisabstract.com/reports/atp_season_yelo_ratings.html"
        elo_rows, elo_headers = self.get_url_tables(elo_url)
        elo_cols = [f"{col}_{i}" if elo_headers.count(col) > 1 else col for i, col in enumerate(elo_headers)]
        elo_df = pd.DataFrame(elo_rows, columns=elo_cols)
        elo_df = elo_df.dropna()
        elo_df = elo_df.replace(["", " ", None], np.nan)
        y_elo_rows, y_elo_headers = self.get_url_tables(y_elo_url)
        y_elo_cols = [f"{col}_{i}" if y_elo_headers.count(col) > 1 else col for i, col in enumerate(y_elo_headers)]
        y_elo_df = pd.DataFrame(y_elo_rows, columns=y_elo_cols)
        y_elo_df = y_elo_df.dropna()
        y_elo_df = y_elo_df.replace(["", " ", None], np.nan)
        elo_df['Player'] = elo_df['Player'].str.replace('\xa0', ' ', regex=False)
        y_elo_df['Player'] = y_elo_df['Player'].str.replace('\xa0', ' ', regex=False)
        return elo_df, y_elo_df


class PlayerDataScraper(DataScraper):
    table_options = Literal["recent_results_serve", "recent_results_return", "winners_ues", "serve_speed", "key_points", "key_games", "point_by_point", 
                            "charting_serve", "charting_return", "charting_rally", "charting_tactics"]
    
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.general_url = f"https://www.tennisabstract.com/cgi-bin/player.cgi?p={first_name}{last_name}"
        self.pid = None # gets set when its needed
        self.player_stats_url = self.PlayerStatUrls(self)
    
    def get_pid(self):
        profile_html = self.scrape_html(url=self.general_url)
        key_games = profile_html.find(string="Key Games")
        key_games_url = str(key_games.parent)
        pid = re.search(r'p=(\d+)/', key_games_url).group(1)
        return str(pid)
    
    def get_table_df(self, table_name: table_options):
        ### Gonna need to edit this so that it gets basic return stats from the recent matches table
        def add_duplicate_suffix(series):
            counts = series.value_counts()
            return series.where(counts == 1, series + '_' + series.groupby(series).cumcount().add(1).astype(str))
        
        if table_name not in ['recent_results_serve', 'recent_results_return', 'all_results_serve', 'all_results_return']:
            self.pid = self.get_pid()
        
        stat_url = self.player_stats_url.get_url(table_name)
        stat_html = self.scrape_html(stat_url)
        stat_all_tables = stat_html.find_all("table")
        stat_table = stat_all_tables[-1]
        stat_headers = convert_to_space([th.text.strip() for th in stat_table.find_all("th")])
        stat_rows = []
        for tr in stat_table.find_all("tr"):
            cells = [td.text.strip() for td in tr.find_all("td")]
            if cells:
                stat_rows.append(cells)
        if table_name == 'charting_serve':
            stat_headers[14] = '2nd ' + stat_headers[14]
            stat_headers[15] = '2nd ' + stat_headers[15]
        
        stat_columns = [f"{col}_{i}" if stat_headers.count(col) > 1 else col for i, col in enumerate(stat_headers)]
        
        stat_df = pd.DataFrame(stat_rows, columns=stat_columns)
        if table_name == 'recent_results_serve' or table_name == 'all_results_serve':
            stat_df = stat_df.drop("More", axis=1)
            stat_df = stat_df.replace(["", " ", None], np.nan)
            stat_df = stat_df.dropna()
            match = match = stat_df.apply(lambda row: f"{row['Date'][-4:]} {row['Tournament']} {row['Rd']}".replace("Masters ", ""), axis=1)
            stat_df.insert(0, 'Match', match)
            spw = stat_df.apply(lambda row: f"{((float(row['1stIn'][:-1])) * float(row['1st%'][:-1]) + (100 - float(row['1stIn'][:-1])) * float(row['2nd%'][:-1])) * 0.01}%", axis=1)
            stat_df.insert(len(stat_df.columns) - 2, 'SPW', spw)
            # Write function to pull player name and then categorize them into a playstyle either by statistics or external api
            # Write function to pull opponent player name and add as a col
            stat_df['Match'] = add_duplicate_suffix(stat_df['Match'])
            return stat_df
        if table_name == 'recent_results_return' or table_name == 'all_results_return':
            stat_df = stat_df.drop("More", axis=1)
            stat_df = stat_df.replace(["", " ", None], np.nan)
            stat_df = stat_df.dropna()
            match = match = stat_df.apply(lambda row: f"{row['Date'][-4:]} {row['Tournament']} {row['Rd']}".replace("Masters ", ""), axis=1)
            stat_df.insert(0, 'Match', match)
            stat_df['Match'] = add_duplicate_suffix(stat_df['Match'])
            return stat_df
        
        stat_df = stat_df.dropna()
        stat_df['Match'] = add_duplicate_suffix(stat_df['Match'])
        stat_df['Match'] = stat_df['Match'].str.replace('\xa0', ' ', regex=False)
        return stat_df
    
    def get_all_tables(self, delay=5):
        all_tables = {}
        self.pid = self.get_pid()
        for table_option in self.table_options.__args__:
            try:
                table_df = self.get_table_df(table_option)
                all_tables[table_option] = table_df
                time.sleep(delay)
            except Exception as e:
                print(f"Error retrieving {table_option}: {e}")
        return all_tables
    
    def get_recent_results(self, delay=5):
        recent_results = {}
        for table_option in ["recent_results_serve", "recent_results_return"]:
            try:
                table_df = self.get_table_df(table_option)
                recent_results[table_option] = table_df
                time.sleep(delay)
            except Exception as e:
                print(f"Error retrieving {table_option}: {e}")
        recent_results_serve = recent_results["recent_results_serve"]
        recent_results_return = recent_results["recent_results_return"]
        merged_df = recent_results_serve[["Match", "", "Date", "Surface", "vRk", "A%", "DF%", "1stIn", "1st%", "2nd%", "SPW"]].merge(
            recent_results_return[["Match", "vA%", "v1st%", "v2nd%", "RPW"]], on="Match", how="outer")
        merged_df.rename(columns={'': 'Scoreline'}, inplace=True)
        merged_df["Date"] = merged_df["Date"].str.replace(r"[^\x00-\x7F]+", "-", regex=True)  # Normalize hyphens
        merged_df["Date"] = pd.to_datetime(merged_df["Date"], format="%d-%b-%Y")
        return merged_df.sort_values(by="Date", ascending=False)
    
    def get_all_results(self, delay=5):
        all_results = {}
        for table_option in ["all_results_serve", "all_results_return"]:
            try:
                table_df = self.get_table_df(table_option)
                all_results[table_option] = table_df
                time.sleep(delay)
            except Exception as e:
                print(f"Error retrieving {table_option}: {e}")
        all_results_serve = all_results["all_results_serve"]
        all_results_return = all_results["all_results_return"]
        merged_df = all_results_serve[["Match", "", "Date", "Surface", "vRk", "A%", "DF%", "1stIn", "1st%", "2nd%", "SPW"]].merge(
            all_results_return[["Match", "vA%", "v1st%", "v2nd%", "RPW"]], on="Match", how="outer")
        merged_df.rename(columns={'': 'Scoreline'}, inplace=True)
        merged_df["Date"] = merged_df["Date"].str.replace(r"[^\x00-\x7F]+", "-", regex=True)
        merged_df["Date"] = pd.to_datetime(merged_df["Date"], format="%d-%b-%Y")
        return merged_df.sort_values(by="Date", ascending=False)
    
    def get_merged_data(self, all_df_dict):
        recent_results_serve = all_df_dict["recent_results_serve"]
        recent_results_return = all_df_dict["recent_results_return"]
        merged_df = recent_results_serve[["Match", "Date", "Surface", "vRk", "A%", "DF%", "1stIn", "1st%", "2nd%", "SPW"]] # Add player playstyle col, add opponent name col
        merged_df = merged_df.merge(recent_results_return[["Match", "vA%", "v1st%", "v2nd%", "RPW"]], on="Match", how="outer")
        merged_df["Date"] = merged_df["Date"].str.replace(r"[^\x00-\x7F]+", "-", regex=True)  # Normalize hyphens
        merged_df["Date"] = pd.to_datetime(merged_df["Date"], format="%d-%b-%Y")
        
        table_to_cols = {
            "winners_ues": ["Match", "Ratio", "Wnr/Pt", "UFE/Pt", "RallyRatio", "Rally Wnr/Pt", "Rally UFE/Pt", "vs Ratio", "vs Wnr/Pt", "vs UFE/Pt"],
            "serve_speed": ["Match", "Avg Speed", "1st Avg", "2nd Avg"],
            "key_points": ["Match", "TB SPW", "TB RPW"],
            "key_games": ["Match", "BP Games", "BP Conv/BPG", "BPF Games", "Hold/BPFG", ],
            "point_by_point": ["Match"],
            "charting_serve": ["Match", "SvImpact_5", "Unret%", "<=3 W%_3", "RiP W%_4", "1st: Unret%", "<=3 W%_7", "RiP W%_8", "2nd: Unret%", "2nd <=3 W%", "2nd RiP W%"],
            "charting_return": ["Match", "RiP%", "RiP W%_3", "1st: RiP%", "RiP W%_9", "2nd: RiP%", "RiP W%_14"],
            "charting_rally": ["Match", "1-3 W%", "4-6 W%", "7-9 W%", "10+ W%"],
            "charting_tactics": ["Match", "Net Freq", "Net W%", "FH: Wnr%", "DTL Wnr%_7", "IO Wnr%", "BH: Wnr%", "DTL Wnr%_10"],
        }
        
        for table, df in all_df_dict.items():
            if table == "recent_results_serve":
                continue
            if table == "recent_results_return":
                continue
            selected_rows = df[table_to_cols[table]]
            merged_df = pd.merge(merged_df, selected_rows, on="Match", how="outer")
        
        return merged_df
    
    class PlayerStatUrls:
        TABLES = {
            "recent_results_serve": "recent_results_serve",
            "recent_results_return" : "recent_results_return",
            "all_results_serve" : "all_results_serve",
            "all_results_return" : "all_results_return",
            "winners_ues": "winners-errors",
            "serve_speed": "serve-speed",
            "key_points": "pbp-points",
            "key_games": "pbp-games",
            "point_by_point": "pbp-stats",
            "charting_serve": "mcp-serve",
            "charting_return": "mcp-return",
            "charting_rally": "mcp-rally",
            "charting_tactics": "mcp-tactics",
        }

        def __init__(self, scraper):
            self.scraper = scraper

        def get_url(self, table_name):
            if table_name not in self.TABLES:
                raise ValueError(f"Unknown table name: {table_name}")
            table = self.TABLES[table_name]
            if table == "recent_results_serve":
                return f"https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={self.scraper.first_name}{self.scraper.last_name}"
            elif table == "recent_results_return":
                return f"https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={self.scraper.first_name}{self.scraper.last_name}&f=r1"
            elif table == "all_results_serve":
                return f"https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={self.scraper.first_name}{self.scraper.last_name}&f=ACareerqq"
            elif table == "all_results_return":
                return f"https://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={self.scraper.first_name}{self.scraper.last_name}&f=ACareerqqr1"
            return f"https://www.tennisabstract.com/cgi-bin/player-more.cgi?p={self.scraper.pid}/{self.scraper.first_name}-{self.scraper.last_name}&table={table}"

        def __getattr__(self, item):
            if item in self.TABLES:
                return self.get_url(item)
            raise AttributeError(f"'PlayerStats' object has no attribute '{item}'")