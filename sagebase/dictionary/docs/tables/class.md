# class

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `class_id` | string | **PK**, required |  |
| `class_type` | string | required |  |
| `common_name` | string |  |  |
| `tax_kingdom` | string |  |  |
| `tax_phylum` | string |  |  |
| `tax_class` | string |  |  |
| `tax_order` | string |  |  |
| `tax_family` | string |  |  |
| `tax_genus` | string |  |  |
| `tax_species` | string |  |  |

## Relations

- Referenced by [`occurrence.class_id`](occurrence.md)
