# Virginia Tech Gantry Automation - Implementation Guide

## Overview
This document describes the implementation of the VT Gantry automation system integrated into the SMF Prints Dashboard. The system enables automated build plate swapping for 3D printers using a robotic gantry system.

## Architecture

### Backend Components

#### 1. Automation API Routes (`/backend/api/automation_routes.py`)
- **Authentication**: Bearer token validation for secure API access
- **Endpoints**:
  - `GET /api/automation/status` - Returns all printer states with coordinates
  - `GET /api/automation/events` - Retrieves automation event history
  - `GET /api/automation/printer/{grid_position}` - Gets specific printer details
  - `POST /api/automation/swap-complete` - Handles swap completion notifications
  - `POST /api/automation/simulate` - Testing endpoint for simulating events
  - `GET /api/automation/health` - Health check endpoint

#### 2. Coordinate Mapping System
Grid positions are mapped to physical coordinates (in mm):
- **Top Shelf (Z=850mm)**: 1A-1F
- **Bottom Shelf (Z=400mm)**: 2A-2F
- **X-axis spacing**: 300mm between positions
- **Origin**: Front-left corner at floor level

### Frontend Components

#### 1. PrinterCard & PrinterCardLarge Components
- **Trigger Bed Swap Button**: Sends print completion events to VT system
- **Raw Data Viewer**: Split-view showing MQTT data and VT messages
- **Status Indicators**: Visual feedback for automation readiness

#### 2. PrinterDetailModal
- **Raw Data Tab**: 
  - Left panel: Complete MQTT/printer object data
  - Right panel: VT System communication messages
- **Automation Controls**:
  - "Trigger Bed Swap" button (orange/gray)
  - "Simulate Swap Complete" button (green)

#### 3. AutomationEvents Component
- Real-time event feed with auto-refresh
- Color-coded events by type
- Expandable raw JSON view
- Located on the Printers page

## Message Formats

### Print Complete Event (SMF → VT)
```json
{
  "event_type": "PRINT_COMPLETE",
  "event_id": "evt_1234567890",
  "timestamp": "2025-09-06T14:30:45.123Z",
  "printer": {
    "grid_position": "1C",
    "name": "Printer 3",
    "model": "P1S",
    "coordinates": {
      "x": 600,
      "y": 0,
      "z": 850
    }
  },
  "print_job": {
    "filename": "part_123.gcode.3mf",
    "duration_minutes": 145,
    "completion_time": "2025-09-06T14:30:45.123Z"
  },
  "required_action": {
    "type": "PLATE_SWAP",
    "priority": "normal",
    "timeout_minutes": 30
  }
}
```

### Swap Complete Event (VT → SMF)
```json
{
  "event_type": "SWAP_COMPLETE",
  "event_id": "evt_complete_1234567890",
  "timestamp": "2025-09-06T14:32:15.456Z",
  "printer": {
    "grid_position": "1C",
    "id": 3,
    "name": "Printer 3"
  },
  "operation": {
    "status": "SUCCESS",
    "duration_seconds": 90,
    "plate_removed_id": "PLATE_007",
    "plate_installed_id": "PLATE_008"
  },
  "gantry_status": {
    "position": "home",
    "ready_for_next": true
  }
}
```

## Testing & Simulation

### Test Authentication Token
```
Bearer test-token-vt-gantry
```

### Simulation Capabilities
1. **Trigger Print Completion**: Simulates a print finishing at 100%
2. **Trigger Bed Swap**: Sends PRINT_COMPLETE event to VT system
3. **Simulate Swap Complete**: Simulates receiving SWAP_COMPLETE from VT
4. **Update Printer Status**: Automatically updates printer to "available" after swap

### Testing Workflow
1. Open printer detail modal (click any printer card)
2. Navigate to "Raw Data" tab
3. Click "Trigger Bed Swap" to simulate print completion
4. Observe outgoing message (green) and acknowledgment (yellow)
5. Click "Simulate Swap Complete" to complete the cycle
6. Printer status updates to "available"

## API Usage Examples

### Get Automation Status
```bash
curl -X GET http://localhost:5001/api/automation/status \
  -H "Authorization: Bearer test-token-vt-gantry"
```

### Simulate Print Completion
```bash
curl -X POST http://localhost:5001/api/automation/simulate \
  -H "Authorization: Bearer test-token-vt-gantry" \
  -H "Content-Type: application/json" \
  -d '{"action": "complete_print", "grid_position": "1C"}'
```

### Send Swap Complete
```bash
curl -X POST http://localhost:5001/api/automation/swap-complete \
  -H "Authorization: Bearer test-token-vt-gantry" \
  -H "Content-Type: application/json" \
  -d '{"grid_position": "1C"}'
```

## Visual Indicators

### Color Coding
- **Orange border/status**: Print complete, ready for bed swap
- **Green button**: Simulate swap complete action
- **Blue text**: MQTT/printer data
- **Green text**: Outgoing VT messages
- **Yellow text**: Incoming VT responses

### Status Messages
- "READY FOR BED SWAP": Displayed when progress >= 100%
- "LIVE": Indicates active MQTT connection
- Directional arrows (→ ←) show message flow

## Security

### Authentication
- Bearer token required for all automation endpoints
- Token validation in `validate_token()` function
- Client ID tracking for audit trails

### Production Considerations
- Replace test tokens with secure, rotating tokens
- Implement IP whitelist for VT gantry system
- Add rate limiting (suggested: 100 requests/minute)
- Enable TLS 1.3 for all communications

## Database Updates

### Printer Model Fields
- `grid_location`: String field for grid position (e.g., "1C")
- `x_coord`, `y_coord`, `z_coord`: Physical coordinates in mm
- Temporary attributes for live data (_progress, _current_file, etc.)

### Event Storage
- Currently in-memory storage for development
- Production: Implement database table for event persistence
- Suggested fields: event_id, event_type, timestamp, printer_id, payload

### Debug Mode
Enable detailed logging in automation_routes.py:
```python
logger.setLevel(logging.DEBUG)
```

---
*Last Updated: September 2025*
*Version: 1.0.0*
