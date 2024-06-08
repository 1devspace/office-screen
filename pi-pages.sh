#!/bin/bash

# Function to close Chromium browser
close_chromium() {
    killall chromium-browser
}

echo "Running pi-pages..."
export DISPLAY=:0

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
interval=90

# Trap interrupts and exit signal to close Chromium browser
trap close_chromium INT TERM

# Open Chromium browser initially
chromium-browser &

# Sleep for a while to allow Chromium browser to open
sleep 15

# Loop infinitely
while true; do
    # Loop through each URL in the array
    for url in "${urls[@]}"; do
        # Switch to Chromium window
        wmctrl -a "Chromium"

        # Open the URL in a new tab
        xdotool key ctrl+t
        sleep 5
        xdotool type "$url"
        xdotool key Return

        # Sleep for the specified interval
        sleep $interval

        # Close the tab
        xdotool key ctrl+w
    done
done