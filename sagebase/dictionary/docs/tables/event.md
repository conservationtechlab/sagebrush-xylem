# event

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `event_id` | uuid | **PK**, required |  |
| `type` | string | required |  |
| `start_time` | timestamp | required |  |
| `end_time` | timestamp |  |  |
| `duration` | number |  |  |
| `deployment_id` | uuid | required |  |
| `media_id` | uuid |  |  |

## Relations

- References [`deployment.deployment_id`](deployment.md)
- References [`media.media_id`](media.md)
- Referenced by [`sensor_measure.event_id`](sensor_measure.md)
- Referenced by [`occurrence.event_id`](occurrence.md)
