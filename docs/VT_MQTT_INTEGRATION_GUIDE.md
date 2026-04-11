# VT Bed Swap MQTT Integration Guide

Last updated: 2026-04-09

## Connection Details

| Setting | Value |
|---|---|
| Broker | Mosquitto on iMac (`localhost:1883`) |
| Protocol | MQTT 3.1.1 (standard, no TLS) |
| Base Topic | `vt_bed_swap` (configurable via `VT_MQTT_BASE_TOPIC`) |
| QoS | 1 for all messages |

---

## Messages: Dashboard to VT Pi

### 1. BED SWAP COMMAND

Sent when a print finishes and the printer needs a fresh plate.

**Topic:** `vt_bed_swap/{printer_id}/command`

```json
{
  "event_type": "SWAP_BED",
  "printer_id": "2",
  "grid_location": "2E",
  "timestamp": "2026-04-09T14:32:15.123456-04:00"
}
```

| Field | Type | Description |
|---|---|---|
| `action` | string | Always `"swap_bed"` |
| `printer_id` | string | Database printer ID |
| `grid_location` | string | Physical grid position (e.g., `1A` through `2F`) |
| `timestamp` | string | ISO 8601, Eastern Time |

**Triggered by:** Print completing at 100%, or manual trigger from dashboard UI.

**Expected response:** `received` message within 30 seconds, then `complete` within 7 minutes.

If the VT Pi is offline (heartbeat stale), the command is queued (up to 20 commands). Queued commands are flushed when the Pi sends its next heartbeat.

---

### 2. STORAGE RESET

Sent when the operator loads clean plates into the dispenser and enters the count.

**Topic:** `vt_bed_swap/plates/all_processed`

```json
{
  "event_type": "STORAGE_RESET",
  "timestamp": "2026-04-09T18:32:15.123456+00:00",
  "plate_amount": 34
}
```

| Field | Type | Description |
|---|---|---|
| `event_type` | string | Always `"STORAGE_RESET"` |
| `timestamp` | string | ISO 8601, UTC |
| `plate_amount` | integer | Number of clean plates loaded (absolute count) |

**Triggered by:** Operator clicking "All Dirty Plates Processed" button on Printer Fleet page after entering the plate count.

---

## Messages: VT Pi to Dashboard

### 1. HEARTBEAT

The dashboard expects a heartbeat every 30 seconds. After 3 missed beats (90 seconds of silence), the Pi is considered offline and new commands are queued instead of published.

**Topic:** `vt_bed_swap/heartbeat`

```json
{
  "event_type": "HEARTBEAT",
  "status": "online",
  "timestamp": "2026-04-09T14:32:15.123456-04:00"
}
```

Payload is flexible -- any valid JSON (or empty) will reset the heartbeat timer.

---

### 2. ACKNOWLEDGMENT (RECEIVED)

Sent after the Pi receives a bed swap command. Must arrive within **30 seconds** or the dashboard cancels the swap and returns the printer to available status.

**Topic:** `vt_bed_swap/{printer_id}/received`

```json
{
  "status": "received",
  "message": "Command received, starting bed swap",
  "printer_name": "2",
  "grid_location": "2E",
  "timestamp": "2026-04-09T14:32:16.500000-04:00"
}
```

| Field | Type | Description |
|---|---|---|
| `status` | string | `"received"` |
| `message` | string | Human-readable status |
| `printer_name` | string | Printer ID (should match command) |
| `grid_location` | string | Grid position (should match command) |
| `timestamp` | string | ISO 8601 |

**Dashboard behavior on receive:** Printer status changes to `bed_swap_in_progress`. Completion timer starts (420 seconds).

---

### 3. COMPLETION

Sent when the physical bed swap is finished. Must arrive within **420 seconds (7 minutes)** of the acknowledgment, or the dashboard marks the printer as offline.

**Topic:** `vt_bed_swap/{printer_id}/complete`

```json
{
  "event_type": "SWAP_COMPLETE",
  "status": "completed",
  "printer_id": "2",
  "grid_location": "2E",
  "timestamp": "2026-04-09T14:37:45.200000-04:00"
}
```

| Field | Type | Description |
|---|---|---|
| `status` | string | `"completed"` |
| `printer_name` | string | Printer ID |
| `grid_location` | string | Grid position |
| `timestamp` | string | ISO 8601 |

**Dashboard behavior on receive:**
1. Printer status set to `AVAILABLE`
2. Printer MQTT connection health-checked (auto-reconnects if needed)
3. Next print job from batch queue auto-assigned if available
4. 120-second status override prevents stale MQTT data from reverting status

---

### 4. ERROR

Sent when the Pi encounters a problem during a bed swap.

**Topic:** `vt_bed_swap/{printer_id}/error`

```json
{
  "event_type": "ERROR",
  "error_code": 32,
  "timestamp": "2025-09-06T14:33:00.789Z",
  "source": "GANTRY",
  "at": {
    "statep": "Printer",
    "statem": "Full",
    "location": {"x": 32.40, "y": 442.0}
  },
  "message": "Clean storage full",
  "severity": "WARNING"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `error` | string | yes | Human-readable error description |
| `code` | string | no | Machine-readable error code |
| `severity` | string | no | `"warning"`, `"error"`, or `"critical"` |
| `printer_name` | string | yes | Printer ID |
| `timestamp` | string | yes | ISO 8601 |

**Dashboard behavior on receive:** Printer set to `OFFLINE`. All timers cancelled. Manual intervention required to retry.

---

## Timeouts

| Timer | Duration | Trigger | On Timeout |
|---|---|---|---|
| ACK | 30 seconds | After command sent | Swap cancelled, printer back to available |
| Completion | 420 seconds (7 min) | After ACK received | Printer set to offline, manual retry needed |
| Heartbeat | 90 seconds (3 x 30s) | No heartbeat received | Pi marked offline, commands queued |

All timeout values are configurable via environment variables:
- `VT_MQTT_ACK_TIMEOUT_SECONDS` (default: 30)
- `VT_MQTT_COMPLETION_TIMEOUT_SECONDS` (default: 420)
- `VT_MQTT_HEARTBEAT_INTERVAL_SECONDS` (default: 30)
- `VT_MQTT_HEARTBEAT_MISSED_THRESHOLD` (default: 3)

---

## Topic Summary

| Direction | Topic | Purpose |
|---|---|---|
| Dashboard -> Pi | `vt_bed_swap/{printer_id}/command` | Request bed swap |
| Dashboard -> Pi | `vt_bed_swap/plates/all_processed` | Storage reset with plate count |
| Pi -> Dashboard | `vt_bed_swap/{printer_id}/received` | Acknowledge command |
| Pi -> Dashboard | `vt_bed_swap/{printer_id}/complete` | Swap finished |
| Pi -> Dashboard | `vt_bed_swap/{printer_id}/error` | Error during swap |
| Pi -> Dashboard | `vt_bed_swap/heartbeat` | Pi is alive |

---

## Printer Grid Reference

The `printer_id` in topics and the `grid_location` in payloads refer to physical printer positions:

| Grid | Row 1 | Row 2 |
|---|---|---|
| A | 1A | 2A |
| B | 1B | 2B |
| C | 1C | 2C |
| D | 1D | 2D |
| E | 1E | 2E |
| F | 1F | 2F |

---

## Offline Queueing

When the Pi is offline (heartbeat stale):
- New bed swap commands are queued in memory (max 20)
- When the next heartbeat arrives, all queued commands are published in order
- If the queue fills, the oldest command is dropped
