#!/bin/bash

start_date="$1"
end_date="$2"

current_date=$(date -d "$start_date" +%Y%m%d)
end_date=$(date -d "$end_date" +%Y%m%d)

while [[ "$current_date" -le "$end_date" ]]; do
    formatted_date=$(date -d "$current_date" +%Y-%m-%d)

    echo "Running $formatted_date: python3 analysis_02.py $current_date 4 0 0"
    python3 analysis_02.py "$current_date" 4 0 0

    current_date=$(date -d "$current_date + 1 day" +%Y%m%d)
done
