# Virginia Tech Bed Swap MQTT Integration Guide

**For:** Virginia Tech Team
**Purpose:** Connect your Raspberry Pi bed swap system to the SMF Dashboard via MQTT
**Last Updated:** October 2025

---

## Overview

The SMF Dashboard will send you MQTT messages when a printer finishes a job and needs its bed swapped. Your Raspberry Pi will:
1. **Receive** bed swap command messages from the SMF Dashboard
2. **Execute** the physical bed swap using your gantry system
3. **Send back** completion or error messages to confirm the swap

**You do NOT need to set up an MQTT broker** - the SMF Dashboard is already running one that you'll connect to.

---

## System Architecture

```
SMF Dashboard (Mac)                  Your Raspberry Pi
┌──────────────────┐                ┌──────────────────┐
│  Flask App with  │                │  Your Python     │
│  Embedded MQTT   │                │  Client Code     │
│  Broker          │◄───────────────│  (paho-mqtt)     │
│  (Port 1883)     │                │                  │
│                  │                │                  │
│  Sends Commands  │─────────────►  │  Executes Swap   │
│  ◄────────────────  Receives ACK  │                  │
└──────────────────┘                └──────────────────┘
     localhost:1883                      Gantry Robot
     or 192.168.1.XXX:1883
```

**Note**: The MQTT broker runs inside the SMF Dashboard Flask application (embedded broker). When the SMF Dashboard starts, the broker starts automatically. You don't need to install or configure any broker software - just connect to the SMF Dashboard Mac's IP address on port 1883.

---

## 1. Connection Information

### MQTT Broker Details

You will receive these connection details from SMF:

- **Broker Host**: `192.168.1.XXX` (SMF Dashboard Mac IP address)
- **Broker Port**: `1883` (standard MQTT port)
- **Authentication**: None required (local network only)
- **Protocol**: MQTT v3.1.1

### Network Requirements

- Your Raspberry Pi must be on the **same local network** as the SMF Dashboard
- Firewall on SMF Dashboard Mac must allow incoming connections on port 1883
- Test connectivity from your Pi:

```bash
# Test network connectivity
ping 192.168.1.XXX

# Test MQTT broker (install mosquitto clients first)
sudo apt-get install mosquitto-clients
mosquitto_sub -h 192.168.1.XXX -t vt_bed_swap/# -v
```

---

## 2. MQTT Topics

### Topics You SUBSCRIBE To (Receive Commands)

**Topic Pattern**: `vt_bed_swap/{printer_id}/command`

Examples:
- `vt_bed_swap/3/command` - Commands for printer ID 3
- `vt_bed_swap/4/command` - Commands for printer ID 4

**Subscribe to all printers**: `vt_bed_swap/+/command` (+ is wildcard)

### Topics You PUBLISH To (Send Responses)

**Acknowledgment Topic**: `vt_bed_swap/{printer_id}/received` (send immediately)
**Completion Topic**: `vt_bed_swap/{printer_id}/complete`
**Error Topic**: `vt_bed_swap/{printer_id}/error`

**Message Flow:**
1. Receive command → Immediately send acknowledgment
2. Execute bed swap (30-60 seconds)
3. Send completion or error when finished

---

## 3. Message Protocols

### 3.1 Incoming Command Message (SMF → You)

**Topic**: `vt_bed_swap/{printer_id}/command`

**JSON Payload**:
```json
{
  "action": "swap_bed",
  "printer_id": "3",
  "grid_location": "2E",
  "timestamp": "2025-10-24T15:30:45.123456"
}
```

**Field Descriptions**:
- `action`: Always "swap_bed" for now
- `printer_id`: Database ID of the printer (use this in your response topics)
- `grid_location`: Physical grid location (e.g., "2E" means Row 2, Column E)
- `timestamp`: ISO 8601 timestamp when command was sent

### 3.2 Outgoing Acknowledgment Message (You → SMF)

**Topic**: `vt_bed_swap/{printer_id}/received`

**JSON Payload**:
```json
{
  "printer_id": "3",
  "grid_location": "2E",
  "status": "received",
  "timestamp": "2025-10-24T15:30:45.500000",
  "message": "Bed swap command received, starting execution"
}
```

**Required Fields**:
- `printer_id`: Same ID from the command message
- `grid_location`: Same location from command message
- `status`: Always `"received"` for acknowledgment messages
- `timestamp`: ISO 8601 timestamp when command was received

**Purpose**: Send this **immediately** when you receive a command, before starting the physical swap. This confirms that your Pi is online and received the message.

---

### 3.3 Outgoing Completion Message (You → SMF)

**Topic**: `vt_bed_swap/{printer_id}/complete`

**JSON Payload**:
```json
{
  "printer_id": "3",
  "grid_location": "2E",
  "success": true,
  "duration_seconds": 45.2,
  "timestamp": "2025-10-24T15:31:30.500000",
  "message": "Bed swap completed successfully"
}
```

**Required Fields**:
- `printer_id`: Same ID from the command message
- `grid_location`: Same location from command message
- `success`: Always `true` for completion messages
- `timestamp`: ISO 8601 timestamp when swap finished

**Optional Fields**:
- `duration_seconds`: How long the swap took
- `message`: Human-readable success message

### 3.4 Outgoing Error Message (You → SMF)

**Topic**: `vt_bed_swap/{printer_id}/error`

**JSON Payload**:
```json
{
  "printer_id": "3",
  "grid_location": "2E",
  "error": "Gantry failed to reach position",
  "error_code": "GANTRY_POSITION_TIMEOUT",
  "timestamp": "2025-10-24T15:31:15.200000"
}
```

**Required Fields**:
- `printer_id`: Same ID from the command message
- `grid_location`: Same location from command message
- `error`: Human-readable error description
- `timestamp`: ISO 8601 timestamp when error occurred

**Optional Fields**:
- `error_code`: Machine-readable error code
- `details`: Additional error context

---

## 4. Python Client Implementation

### 4.1 Installation

Install the MQTT library on your Raspberry Pi:

```bash
pip3 install paho-mqtt>=2.0.0
```

### 4.2 Complete Working Example

Save this as `bed_swap_client.py` on your Raspberry Pi:

```python
#!/usr/bin/env python3
"""
Virginia Tech Bed Swap MQTT Client
Connects to SMF Dashboard MQTT broker and handles bed swap commands
"""

import json
import time
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# ============================================================================
# CONFIGURATION - Update these values
# ============================================================================

MQTT_BROKER_HOST = "192.168.1.XXX"  # Get this from SMF
MQTT_BROKER_PORT = 1883
BASE_TOPIC = "vt_bed_swap"

# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Bed Swap Robot Control (YOU IMPLEMENT THIS)
# ============================================================================

def execute_bed_swap(printer_id: str, grid_location: str) -> dict:
    """
    Execute the physical bed swap operation.

    Args:
        printer_id: Database ID of the printer
        grid_location: Physical grid location (e.g., "2E")

    Returns:
        dict with 'success', 'duration', 'error' (if failed)
    """
    logger.info(f"Starting bed swap for printer {printer_id} at {grid_location}")

    start_time = time.time()

    try:
        # ============================================================
        # TODO: IMPLEMENT YOUR GANTRY CONTROL HERE
        # ============================================================

        # Example steps you might implement:
        # 1. Move gantry to printer location based on grid_location
        # 2. Activate bed gripper
        # 3. Lift bed from printer
        # 4. Move to bed storage/swap area
        # 5. Release old bed
        # 6. Pick up new bed
        # 7. Move back to printer
        # 8. Place new bed on printer
        # 9. Home gantry

        # For now, simulate the swap
        time.sleep(5)  # Replace this with your actual robot control code

        # ============================================================
        # END TODO
        # ============================================================

        duration = time.time() - start_time

        logger.info(f"Bed swap completed in {duration:.2f} seconds")
        return {
            'success': True,
            'duration': duration,
            'message': 'Bed swap completed successfully'
        }

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Bed swap failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_code': 'SWAP_EXECUTION_FAILED',
            'duration': duration
        }


# ============================================================================
# MQTT Client
# ============================================================================

class BedSwapMQTTClient:
    """MQTT client for bed swap automation."""

    def __init__(self, broker_host: str, broker_port: int):
        """Initialize the MQTT client."""
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id="vt_bed_swap_pi"
        )

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        logger.info(f"MQTT client initialized for {broker_host}:{broker_port}")

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """Callback when client connects to broker (paho-mqtt 2.x signature)."""
        if reason_code.value == 0:
            logger.info("✅ Connected to SMF Dashboard MQTT broker")

            # Subscribe to all bed swap commands
            subscribe_topic = f"{BASE_TOPIC}/+/command"
            client.subscribe(subscribe_topic)
            logger.info(f"📥 Subscribed to: {subscribe_topic}")
        else:
            logger.error(f"❌ Connection failed with reason code: {reason_code}")

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        """Callback when client disconnects from broker (paho-mqtt 2.x signature)."""
        if reason_code.value != 0:
            logger.warning(f"⚠️  Unexpected disconnect from MQTT broker (code: {reason_code})")
            logger.info("Will attempt to reconnect automatically...")
        else:
            logger.info("Disconnected from MQTT broker")

    def _on_message(self, client, userdata, msg):
        """Callback when message is received."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')

            logger.info(f"📨 Received message on topic: {topic}")
            logger.debug(f"Payload: {payload}")

            # Parse the command
            try:
                command = json.loads(payload)
            except json.JSONDecodeError:
                logger.error(f"❌ Invalid JSON payload: {payload}")
                return

            # Extract printer info
            printer_id = command.get('printer_id')
            grid_location = command.get('grid_location')
            action = command.get('action')

            if not all([printer_id, grid_location, action]):
                logger.error(f"❌ Missing required fields in command: {command}")
                return

            if action != 'swap_bed':
                logger.warning(f"⚠️  Unknown action: {action}")
                return

            logger.info(f"🤖 Executing bed swap for printer {printer_id} ({grid_location})")

            # Send acknowledgment immediately
            self._send_acknowledgment(printer_id, grid_location)

            # Execute the bed swap
            result = execute_bed_swap(printer_id, grid_location)

            # Send response back to SMF Dashboard
            if result['success']:
                self._send_completion(printer_id, grid_location, result)
            else:
                self._send_error(printer_id, grid_location, result)

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}", exc_info=True)

    def _send_acknowledgment(self, printer_id: str, grid_location: str):
        """Send acknowledgment message to SMF Dashboard."""
        topic = f"{BASE_TOPIC}/{printer_id}/received"

        message = {
            'printer_id': printer_id,
            'grid_location': grid_location,
            'status': 'received',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Bed swap command received, starting execution'
        }

        payload = json.dumps(message)
        self.client.publish(topic, payload, qos=1)

        logger.info(f"✅ Sent acknowledgment to: {topic}")
        logger.debug(f"Acknowledgment payload: {payload}")

    def _send_completion(self, printer_id: str, grid_location: str, result: dict):
        """Send completion message to SMF Dashboard."""
        topic = f"{BASE_TOPIC}/{printer_id}/complete"

        message = {
            'printer_id': printer_id,
            'grid_location': grid_location,
            'success': True,
            'duration_seconds': result.get('duration', 0),
            'timestamp': datetime.utcnow().isoformat(),
            'message': result.get('message', 'Bed swap completed')
        }

        payload = json.dumps(message)
        self.client.publish(topic, payload, qos=1)

        logger.info(f"✅ Sent completion message to: {topic}")
        logger.debug(f"Completion payload: {payload}")

    def _send_error(self, printer_id: str, grid_location: str, result: dict):
        """Send error message to SMF Dashboard."""
        topic = f"{BASE_TOPIC}/{printer_id}/error"

        message = {
            'printer_id': printer_id,
            'grid_location': grid_location,
            'error': result.get('error', 'Unknown error'),
            'error_code': result.get('error_code', 'UNKNOWN_ERROR'),
            'timestamp': datetime.utcnow().isoformat()
        }

        payload = json.dumps(message)
        self.client.publish(topic, payload, qos=1)

        logger.error(f"❌ Sent error message to: {topic}")
        logger.debug(f"Error payload: {payload}")

    def connect(self):
        """Connect to the MQTT broker."""
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            logger.info("MQTT client loop started")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT client stopped")


# ============================================================================
# Main Program
# ============================================================================

def main():
    """Main program entry point."""
    logger.info("="*60)
    logger.info("Virginia Tech Bed Swap MQTT Client Starting")
    logger.info("="*60)

    # Create and connect the MQTT client
    client = BedSwapMQTTClient(MQTT_BROKER_HOST, MQTT_BROKER_PORT)

    try:
        client.connect()

        logger.info("✅ Client running. Waiting for bed swap commands...")
        logger.info("Press Ctrl+C to stop")

        # Keep the program running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\n⚠️  Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
    finally:
        client.disconnect()
        logger.info("👋 Bed swap client stopped")


if __name__ == "__main__":
    main()
```

### 4.3 Running the Client

```bash
# Make the script executable
chmod +x bed_swap_client.py

# Run the client
python3 bed_swap_client.py
```

**Expected Output**:
```
2025-10-24 15:30:00 - INFO - ============================================================
2025-10-24 15:30:00 - INFO - Virginia Tech Bed Swap MQTT Client Starting
2025-10-24 15:30:00 - INFO - ============================================================
2025-10-24 15:30:00 - INFO - MQTT client initialized for 192.168.1.XXX:1883
2025-10-24 15:30:00 - INFO - Connecting to MQTT broker at 192.168.1.XXX:1883...
2025-10-24 15:30:01 - INFO - ✅ Connected to SMF Dashboard MQTT broker
2025-10-24 15:30:01 - INFO - 📥 Subscribed to: vt_bed_swap/+/command
2025-10-24 15:30:01 - INFO - ✅ Client running. Waiting for bed swap commands...
2025-10-24 15:30:01 - INFO - Press Ctrl+C to stop
```

---

## 5. Testing Your Integration

### 5.1 Test Receiving Messages

Use `mosquitto_sub` to verify you can receive test messages:

```bash
# Subscribe to all VT bed swap topics
mosquitto_sub -h 192.168.1.XXX -t vt_bed_swap/# -v
```

Ask SMF to trigger a test bed swap command and you should see it appear.

### 5.2 Test Sending Messages

Send a test completion message manually:

```bash
# Test completion message for printer ID 3
mosquitto_pub -h 192.168.1.XXX -t vt_bed_swap/3/complete -m '{
  "printer_id": "3",
  "grid_location": "2E",
  "success": true,
  "duration_seconds": 42.5,
  "timestamp": "2025-10-24T15:30:00.000000",
  "message": "Test completion from VT team"
}'
```

This should appear in the SMF Dashboard's MQTT Message Log in the Operations Center.

### 5.3 Full Integration Test

1. **Start your client**: `python3 bed_swap_client.py`
2. **SMF triggers a bed swap** from the dashboard (or via manual test)
3. **Your client receives the command** and executes the swap
4. **Your client sends back a completion/error message**
5. **SMF Dashboard displays the result** in the MQTT Message Log

---

## 6. Error Handling & Recovery

### Common Issues

**Connection Refused**:
```
❌ Connection failed with reason code: 1
```
- Check that the MQTT broker IP is correct
- Verify the SMF Dashboard is running
- Check firewall settings on the Mac

**No Messages Received**:
- Verify you're subscribed to the correct topic (`vt_bed_swap/+/command`)
- Check that the SMF Dashboard is publishing to `vt_bed_swap/{printer_id}/command`
- Use `mosquitto_sub` to debug

**Messages Not Reaching SMF Dashboard**:
- Verify your response topics are correct:
  - Completion: `vt_bed_swap/{printer_id}/complete`
  - Error: `vt_bed_swap/{printer_id}/error`
- Check JSON formatting (use `json.dumps()`)
- Verify QoS is set to 1 for reliable delivery

### Automatic Reconnection

The provided client code automatically reconnects if the connection drops. The MQTT library handles this internally.

### Timeout Handling

If your bed swap takes longer than expected, the SMF Dashboard has a timeout (default: 5 minutes). If no response is received within this time:
- The printer status will show an error
- SMF staff will be notified to check the robot manually

**Recommended**: Send progress updates or extend the timeout if your swaps take longer.

---

## 7. Production Deployment

### Run as a System Service

Create `/etc/systemd/system/vt-bed-swap.service`:

```ini
[Unit]
Description=VT Bed Swap MQTT Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/bed-swap
ExecStart=/usr/bin/python3 /home/pi/bed-swap/bed_swap_client.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable vt-bed-swap
sudo systemctl start vt-bed-swap
sudo systemctl status vt-bed-swap
```

### View Logs

```bash
# View real-time logs
sudo journalctl -u vt-bed-swap -f

# View recent logs
sudo journalctl -u vt-bed-swap -n 100
```

---

## 8. Contact & Support

**For connection details, IP addresses, or testing assistance**:
- Contact: SMF Dashboard Administrator
- They will provide you with the correct `MQTT_BROKER_HOST` IP address

**For MQTT protocol questions**:
- See this integration guide
- Check the MQTT Message Log in the SMF Dashboard Operations Center

---

## Quick Start Checklist

- [ ] Install `paho-mqtt` on your Raspberry Pi
- [ ] Get the MQTT broker IP address from SMF
- [ ] Update `MQTT_BROKER_HOST` in the Python code
- [ ] Test connectivity with `mosquitto_sub`
- [ ] Run the client: `python3 bed_swap_client.py`
- [ ] Implement your gantry control logic in `execute_bed_swap()`
- [ ] Test receiving commands from SMF Dashboard
- [ ] Test sending completion messages back
- [ ] Set up as a systemd service for production
- [ ] Monitor logs to verify operation

---

**End of Integration Guide**
