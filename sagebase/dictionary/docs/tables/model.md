# model

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `model_id` | uuid | **PK**, required |  |
| `name` | string | required |  |
| `type` | string | required |  |
| `url` | string | required |  |

## Relations

- Referenced by [`occurrence.model_id`](occurrence.md)
