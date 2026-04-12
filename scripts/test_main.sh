echo "main.py should be running in a different terminal"

mosquitto_sub -h "$BROKER" -t "$TOPIC" | jq .

mosquitto_sub -h "localhost" -t "test/#" | while read -r payload; do
        if echo "$payload" | jq -e . >/dev/null 2>&1; then
            echo "--- New Message ---"
            echo "$payload" | jq .
        else
            echo "Non-JSON message received: $payload"
        fi
    done