#!/bin/bash

echo "Running pi-pages..."


# List of websites to cycle through
websites=("https://news.ycombinator.com/" "https://www.coin360.com")

# Time interval to switch between tabs (in seconds)
interval=60

# Loop infinitely
while true; do
    # Loop through each website in the array
    for website in "${websites[@]}"; do
        # Open Chromium browser with the specified website in fullscreen mode
        DISPLAY=:0 chromium-browser "$website" --start-fullscreen
        
        # Sleep for the specified interval
        sleep $interval
    done
done
