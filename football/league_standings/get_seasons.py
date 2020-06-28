from pathlib import Path
import re
from urllib import request

from bs4 import BeautifulSoup
import pandas as pd


cur_dir = Path(__file__).parent
data_dir = cur_dir / 'Data'
data_dir.mkdir(exist_ok=True)

# Parse RSSSF data
resp = request.urlopen(r'http://www.rsssf.com/tablese/engall.html')
soup = BeautifulSoup(resp.read(), features='html.parser')
content = soup.find_all('pre')[1].text

season_data = []

name_pattern = re.compile(r'^(?P<team>[\w\s\']+)\(')
season_pattern = re.compile(r'[\d\s]+(?P<tier>I{1,3}|IV)\s+(?P<seasons>\d+)')

for line in content.splitlines():
    name = name_pattern.search(line)
    if name:
        team_name = name.group('team').strip()
        continue
    
    seasons = season_pattern.search(line)
    if seasons:
        season_data.append(
            [team_name, seasons.group('tier'), int(seasons.group('seasons'))]
        )
        continue
    
    # print(f'Unmatched: "{line}"')

from_site = pd.DataFrame.from_records(
    season_data, columns=('Team', 'Tier', 'Seasons')
)

# Read in newer seasons, get counts per level per team
newer_seasons = pd.concat(
    pd.read_excel(cur_dir / 'Tiers_1617-1920.xlsx', sheet_name=None).values()
).groupby(['Team', 'Tier']).size().to_frame(name='Seasons').reset_index()

# Combine
df = pd.concat([from_site, newer_seasons], ignore_index=True)\
       .groupby(['Team', 'Tier'], as_index=False).agg({'Seasons': 'sum'})

df['Numeric Level'] = df['Tier'].map({
    'I': 1,
    'II': 2,
    'III': 3,
    'IV': 4
})

df['Highest Level'] = df.groupby('Team')['Numeric Level'].transform('min')
df['Total Seasons'] = df.groupby('Team')['Seasons'].transform('sum')
df.to_csv(data_dir / 'Tier Seasons.csv', index=False)
