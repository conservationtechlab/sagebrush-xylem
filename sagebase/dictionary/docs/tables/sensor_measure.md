# sensor_measure

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `measure_id` | uuid | **PK**, required |  |
| `recorded_time` | timestamp | required |  |
| `measure_name` | string | required |  |
| `measure_value` | number | required |  |
| `event_id` | uuid | required |  |

## Relations

- References [`uom.measure_name`](uom.md)
- References [`event.event_id`](event.md)
