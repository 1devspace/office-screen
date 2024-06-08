#!/bin/bash

echo "Running pi-pages..."

# List of URLs to visit
urls=(
    "https://wise.com/us/currency-converter/usd-to-tnd-rate"
    "https://www.mortgagenewsdaily.com/mortgage-rates/mnd"
    "https://www.forbes.com/advisor/mortgages/mortgage-rates/"
    "https://finance.yahoo.com/most-active/"
    "https://finance.yahoo.com/quote/CNC/"
    "https://www.coindesk.com/price/bitcoin/"
    "https://www.livesport.com/soccer/world/"
    "https://live-tennis.eu/en/atp-live-scores"
    "https://forecast.weather.gov/MapClick.php?CityName=Las+Vegas&state=NV&site=VEF&textField1=36.175&textField2=-115.136&e=0"
    "https://www.weatherbug.com/weather-forecast/10-day-weather/tabarka-jundubah-ts"
    "https://tldr.tech/"
    "https://news.ycombinator.com/"
    "https://gov.nv.gov/Newsroom/PRs/news-releases/"
    "https://cityofnorthlasvegas.org/newslist.php"
    "https://www.lasvegasnevada.gov/Residents/Events#/"
    "https://www.cityofnorthlasvegas.com/things-to-do/events-calendar"
    "https://github.com/trending"
    "https://trends24.in/united-states/"
)

# Time interval to switch between tabs (in seconds)
interval=10

# Loop infinitely
while true; do
    # Loop through each URL in the array
    for url in "${urls[@]}"; do
        # Open Chromium browser with the specified website
        # --disable-gpu is used to disable GPU hardware acceleration
        # --window-size sets the initial window size
        chromium-browser "$url" --window-size=1920,1080
        
        # Sleep for the specified interval
        sleep $interval
    done
done
