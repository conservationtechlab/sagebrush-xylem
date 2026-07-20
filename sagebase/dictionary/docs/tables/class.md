# class

Class list, e.g. species/sound

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `class_id` | string | **PK**, required | Unique identifier of class |
| `class_type` | string | required | Type of class record - e.g. 'Animal' |
| `common_name` | string |  | Taxonomy - common name |
| `tax_kingdom` | string |  | Taxonomy - Kingdom |
| `tax_phylum` | string |  | Taxonomy - Phylum |
| `tax_class` | string |  | Taxonomy - Class |
| `tax_order` | string |  | Taxonomy - Order |
| `tax_family` | string |  | Taxonomy - Family |
| `tax_genus` | string |  | Taxonomy - Genus |
| `tax_species` | string |  | Taxonomy - species |

**PK** - Primary Key

## Relations

- [`occurrence.class_id`](occurrence.md) => class_id
