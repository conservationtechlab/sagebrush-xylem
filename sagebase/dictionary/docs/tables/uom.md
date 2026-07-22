# uom

Unit of Measure table.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `measure_name` | string | **PK**, required | Unique name of measure |
| `unit_of_measure` | string | required | Units recorded - e.g. 'uS/cm' |

**PK** - Primary Key  

## Relations

- [`sensor_measure.measure_name`](sensor_measure.md) => measure_name
