# sensor_measure

Data table of environmental sensor measurements.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `measure_id` | uuid | **PK**, required | Unique identifier of measure record |
| `recorded_time` | timestamp | required | Timestamp of when measure was recorded |
| `measure_name` | string | required | What measure is recorded - e.g. 'ext_temperature' |
| `measure_value` | number | **FK**, required | Raw data value of captured measure |
| `event_id` | uuid | **FK**, required | Linked event record |

**PK** => Primary Key  
**FK** => Foreign Key  

## Relations

- measure_name => [`uom.measure_name`](uom.md)
- event_id => [`event.event_id`](event.md)
