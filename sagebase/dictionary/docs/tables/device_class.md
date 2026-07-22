# device_class

Class list of devices.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `device_class_id` | uuid | **PK**, required | Unique identifier of device class |
| `device_class` | string | required | Class of device - e.g. 'soil sensor' |

**PK** - Primary Key  

## Relations

- device_class_id => [`device_type.device_class_id`](device_type.md)
