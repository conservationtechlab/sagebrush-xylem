# person

Person table.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `person_id` | uuid | **PK**, required | Unique identifier of person |
| `name` | string | required | Name of person |
| `email` | string |  | email of person |

**PK** - Primary Key  

## Relations

- [`annotation.annotator_id`](annotation.md) => person_id
- [`occurrence.validator_id`](occurrence.md) => person_id
