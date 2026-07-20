# model

The ML model used for class identification of the occurrence record.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `model_id` | uuid | **PK**, required | Unique identifier of model |
| `name` | string | required | Name of model - e.g. 'AniML' |
| `type` | string | required | Type of model - e.g. 'transformer' |

**PK** - Primary Key  

## Relations

- [`occurrence.model_id`](occurrence.md) => model_id
