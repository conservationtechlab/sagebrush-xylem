# device

Record of device to be deployed during survey.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `device_id` | string | **PK**, required | Unique identifier of device record |
| `serial_number` | string |  | Serial number of hardware |
| `device_type_id` | string | **FK** | Record of device type |

**PK** - Primary Key  
**FK** - Foreign Key  

## Relations

- device_type_id => [`device_type.device_type_id`](device_type.md)
- [`deployment.device_id`](deployment.md) => device_id
