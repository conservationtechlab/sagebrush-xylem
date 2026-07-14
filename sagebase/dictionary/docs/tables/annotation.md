# annotation

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `annotation_id` | uuid | **PK**, required |  |
| `timestamp` | timestamp | required |  |
| `annotator_id` | string | required |  |

## Relations

- References [`person.person_id`](person.md)
- Referenced by [`occurrence.annotation_id`](occurrence.md)
