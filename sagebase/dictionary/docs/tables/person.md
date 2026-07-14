# person

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `person_id` | uuid | **PK**, required |  |
| `name` | string | required |  |
| `email` | string |  |  |

## Relations

- Referenced by [`annotation.annotator_id`](annotation.md)
- Referenced by [`occurrence.validator_id`](occurrence.md)
