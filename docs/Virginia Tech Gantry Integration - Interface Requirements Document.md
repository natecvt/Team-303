# Virginia Tech Gantry Integration - Interface Requirements Document

## Executive Summary
This document defines the interface requirements for integrating the SMF Prints Dashboard with Virginia Tech's automated build plate swapping gantry system. The SMF Dashboard will provide real-time printer status events and coordinate information to enable autonomous plate removal and replacement.

## 1. System Overview

### 1.1 Current SMF Dashboard Capabilities
- **Printer Management**: 12 printers in a 2×6 grid configuration (1A-1F bottom shelf, 2A-2F top shelf)
- **Real-Time Monitoring**: MQTT connection to Bambu Lab printers with live status updates
- **Simplified Identification**: Each printer has:
  - ID: Integer matching printer name (1-12)
  - Name: String representation ("1" through "12")
  - Grid Location: Physical position (e.g., "1C" for bottom shelf position C)
- **Coordinate Storage**: Each printer profile contains:
  - Physical X, Y, Z coordinates in millimeters
  - Printer model information (P1S or X1C)
- **Event Detection**: Automatic detection of print completion (progress = 100%)
- **Status Management**: Full printer state tracking and control

### 1.2 Integration Architecture
```
[Bambu Printers] <--MQTT--> [SMF Dashboard] <--WebSocket/REST--> [VT Gantry System]
```

## 2. Communication Protocol Options

### 2.1 PRIMARY: WebSocket Event Stream (Recommended)
**Endpoint**: `wss://dashboard.smfprints.com/automation`

**Benefits**:
- Real-time bidirectional communication
- Low latency (<50ms)
- Persistent connection reduces overhead
- Event-driven architecture

**Connection Example**:
```javascript
const socket = io('wss://dashboard.smfprints.com', {
  path: '/automation',
  auth: {
    token: 'YOUR_AUTH_TOKEN'
  }
});

socket.on('print_complete', (data) => {
  // Handle print completion event
  console.log(`Print complete at position ${data.printer.grid_location}`);
});
```

### 2.2 FALLBACK: REST API with Polling
**Base URL**: `https://dashboard.smfprints.com/api/automation`

**Endpoints**:
- `GET /status` - Get all printer states
- `GET /events` - Get recent events (with timestamp filtering)
- `POST /swap-complete` - Notify swap completion
- `GET /printer/{grid_location}` - Get specific printer details by grid location (e.g., "1C")

## 3. Message Formats

### 3.1 Print Complete Event (SMF → VT)
```json
{
  "event_type": "PRINT_COMPLETE",
  "event_id": "evt_1234567890",
  "timestamp": "2025-09-06T14:30:45.123Z",
  "printer": {
    "id": 3,
    "name": "3",
    "grid_location": "1C",
    "model": "P1S",
    "coordinates": {
      "x": 600,
      "y": 0,
      "z": 850,
      "unit": "mm",
      "reference": "front_left_origin"
    }
  },
  "print_job": {
    "filename": "part_123.gcode.3mf",
    "duration_minutes": 145,
    "completion_time": "2025-09-06T14:30:45.123Z",
    "order_id": "ORD-2025-0906-001"
  },
  "required_action": {
    "type": "PLATE_SWAP",
    "priority": "normal",
    "timeout_minutes": 30
  }
}
```

### 3.2 Swap Complete Acknowledgment (VT → SMF)
```json
{
  "event_type": "SWAP_COMPLETE",
  "event_id": "evt_response_1234567890",
  "timestamp": "2025-09-06T14:32:15.456Z",
  "printer": {
    "id": 3,
    "grid_location": "1C"
  },
  "operation": {
    "status": "SUCCESS",
    "duration_seconds": 90,
    "plate_removed_id": "PLATE_007",
    "plate_installed_id": "PLATE_008",
    "errors": []
  },
  "gantry_status": {
    "position": "home",
    "ready_for_next": true
  }
}
```

### 3.3 Error Event (Bidirectional)
```json
{
  "event_type": "ERROR",
  "event_id": "evt_error_1234567890",
  "timestamp": "2025-09-06T14:33:00.789Z",
  "source": "GANTRY",
  "printer": {
    "id": 3,
    "grid_location": "1C"
  },
  "error": {
    "code": "PLATE_STUCK",
    "message": "Unable to remove build plate - magnetic force exceeded",
    "severity": "warning",
    "retry_available": true
  }
}
```

## 4. Coordinate System Specification

### 4.1 Reference Frame
- **Origin**: Front-left corner of the printer rack at floor level
- **X-Axis**: Left to right (facing the rack)
- **Y-Axis**: Front to back (depth)
- **Z-Axis**: Floor to ceiling (height)
- **Units**: Millimeters (mm)

### 4.2 Grid Layout with Coordinates
```
Bottom Shelf (Z=400mm):
┌────┬────┬────┬────┬────┬────┐
│ 1A │ 1B │ 1C │ 1D │ 1E │ 1F │
│ P1 │ P2 │ P3 │ P4 │ P5 │ P6 │
│x:0 │x:300│x:600│x:900│x:1200│x:1500│
└────┴────┴────┴────┴────┴────┘

Top Shelf (Z=850mm):
┌────┬────┬────┬────┬────┬────┐
│ 2A │ 2B │ 2C │ 2D │ 2E │ 2F │
│ P7 │ P8 │ P9 │ P10│ P11│ P12│
│x:0 │x:300│x:600│x:900│x:1200│x:1500│
└────┴────┴────┴────┴────┴────┘

All positions: Y=0 (printers accessible from front)

Printer ID Mapping:
- Bottom Shelf (1A-1F): Printers 1-6 (IDs match names)
- Top Shelf (2A-2F): Printers 7-12 (IDs match names)
- Example: Printer at position 1C has ID=3, name="3"
```

## 5. Authentication & Security

### 5.1 API Authentication
```http
Authorization: Bearer YOUR_API_TOKEN
X-Client-ID: vt-gantry-system
X-Request-ID: unique-request-id
```

### 5.2 WebSocket Authentication
```javascript
{
  "auth": {
    "token": "YOUR_API_TOKEN",
    "client_id": "vt-gantry-system"
  }
}
```

### 5.3 Security Requirements
- TLS 1.3 encryption for all communications
- API tokens with 90-day rotation
- IP whitelist for production environment
- Rate limiting: 100 requests/minute

## 6. Event Flow Sequences

### 6.1 Normal Operation Sequence
```
1. SMF Dashboard detects print completion (progress = 100%)
2. SMF sends PRINT_COMPLETE event with coordinates
3. VT Gantry acknowledges receipt (optional)
4. VT Gantry performs plate swap operation
5. VT sends SWAP_COMPLETE event
6. SMF updates printer status to "AVAILABLE"
7. SMF queues next print job (if available)
```

### 6.2 Error Recovery Sequence
```
1. VT Gantry encounters error during swap
2. VT sends ERROR event with details
3. SMF marks printer as "MAINTENANCE_REQUIRED"
4. Manual intervention resolves issue
5. Operator clears error in SMF Dashboard
6. Normal operation resumes
```

## 7. Testing & Development Support

### 7.1 Test Environment
- **URL**: `https://test.dashboard.smfprints.com`
- **Test Printers**: Simulated printers at all grid positions
- **Event Simulation**: Ability to trigger test events on demand

### 7.2 Development Tools
```bash
# Simulate print completion
curl -X POST https://test.dashboard.smfprints.com/api/automation/simulate \
  -H "Authorization: Bearer TEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "complete_print", "grid_position": "1C"}'

# Subscribe to events via WebSocket CLI
wscat -c wss://test.dashboard.smfprints.com/automation \
  -H "Authorization: Bearer TEST_TOKEN"
```

### 7.3 Test Scenarios
1. Single print completion
2. Multiple simultaneous completions
3. Network interruption recovery
4. Invalid coordinate handling
5. Authentication failure
6. Rate limit testing

## 8. Implementation Timeline

### Phase 1: Basic Integration (Week 1-2)
- REST API endpoints active
- Manual event triggering
- Basic authentication
- Test environment ready

### Phase 2: Real-Time Events (Week 3-4)
- WebSocket implementation
- Automatic event detection
- Error handling
- Coordinate validation

### Phase 3: Production Ready (Week 5-6)
- Full authentication system
- Monitoring and logging
- Performance optimization
- Documentation complete

## 9. Performance Requirements

### 9.1 Latency
- Event notification: < 100ms from detection
- API response time: < 200ms (95th percentile)
- WebSocket ping: < 50ms

### 9.2 Availability
- Uptime SLA: 99.9% 
- Planned maintenance window: Sunday 2-4 AM EST
- Automatic reconnection support required

### 9.3 Scalability
- Support for 12 concurrent printers
- 100 events per minute peak capacity
- Message queue for event reliability

## 10. Monitoring & Logging

### 10.1 Available Metrics
- Event delivery success rate
- Average swap duration by position
- Error frequency and types
- System uptime and latency

### 10.2 Log Format
```json
{
  "timestamp": "2025-09-06T14:30:45.123Z",
  "level": "INFO",
  "event": "PRINT_COMPLETE",
  "printer_position": "1C",
  "correlation_id": "evt_1234567890",
  "metadata": {
    "duration_ms": 45,
    "client_id": "vt-gantry"
  }
}
```

## 11. Contact & Support

### Technical Contact
- **Primary**: SMF Dashboard Development Team
- **Email**: api-support@smfprints.com
- **Response Time**: 4 hours (business hours)

### Documentation
- API Reference: `https://docs.smfprints.com/api/automation`
- WebSocket Guide: `https://docs.smfprints.com/websocket`
- Integration Examples: `https://github.com/smfprints/vt-integration-examples`

## Appendix A: Quick Start Code Examples

### Python WebSocket Client
```python
import socketio
import json

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to SMF Dashboard')

@sio.on('print_complete')
def on_print_complete(data):
    print(f"Print complete at {data['printer']['grid_position']}")
    # Trigger gantry movement
    move_gantry_to(data['printer']['coordinates'])
    
    # Send completion when done
    sio.emit('swap_complete', {
        'grid_position': data['printer']['grid_position'],
        'status': 'SUCCESS'
    })

sio.connect('wss://dashboard.smfprints.com',
           auth={'token': 'YOUR_TOKEN'})
```

### Node.js REST Client
```javascript
const axios = require('axios');

async function checkPrinterStatus() {
  const response = await axios.get(
    'https://dashboard.smfprints.com/api/automation/status',
    {
      headers: {
        'Authorization': 'Bearer YOUR_TOKEN'
      }
    }
  );
  
  return response.data.printers.filter(p => p.status === 'PRINT_COMPLETE');
}

async function notifySwapComplete(gridPosition) {
  await axios.post(
    'https://dashboard.smfprints.com/api/automation/swap-complete',
    {
      grid_location: gridPosition,
      status: 'SUCCESS'
    },
    {
      headers: {
        'Authorization': 'Bearer YOUR_TOKEN'
      }
    }
  );
}
```

---

## Important Update: Simplified Printer Identification (September 2025)

The SMF Dashboard has recently simplified its printer identification system:

### What Changed:
- **Removed**: The redundant `grid_position` numeric field (1-12)
- **Simplified**: Printer IDs now match printer names (ID 3 = Printer "3")
- **Retained**: Grid location strings (1A-1F, 2A-2F) for physical position reference

### API Impact:
- All API messages now include `id` field matching the printer name
- Continue using `grid_location` for position-based queries
- The `grid_position` field has been deprecated and removed

### Example:
Printer at physical position 1C:
- **ID**: 3
- **Name**: "3"
- **Grid Location**: "1C"
- **Coordinates**: x=600, y=0, z=400

---

**Document Version**: 1.1  
**Last Updated**: September 6, 2025  
**Status**: Ready for Virginia Tech Review  
**Recent Changes**: Simplified printer identification system, removed grid_position field
