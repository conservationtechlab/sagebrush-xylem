# event

Contains multi-modality event records during survey deployment.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `event_id` | uuid | **PK**, required | Unique identifier of event record |
| `type` | string | required | Sensor class and modality |
| `start_time` | timestamp | required | Timestamp of event start |
| `end_time` | timestamp |  | Timestamp of event end |
| `duration` | number |  | Event duration in seconds |
| `deployment_id` | uuid | **FK**, required | Deployment record of device |
| `media_id` | uuid | **FK** | Media record - foreign key |

**PK** - Primary Key  
**FK** - Foreign Key

## Relations

- deployment_id => [`deployment.deployment_id`](deployment.md)
- media_id => [`media.media_id`](media.md)
- [`sensor_measure.event_id`](sensor_measure.md) => event_id
- [`occurrence.event_id`](occurrence.md) => event_id
