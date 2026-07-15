# SageBase Data Model

**SageBase** is a data model for the [SageBRUSH platform](https://github.com/conservationtechlab/sagebrush-xylem) managed by the Conservation Technology Lab at San Diego Zoo Wildlife Alliance.

## Overview


See the [Data Model Overview](data-model-overview.md) for a full entity-relationship diagram.

## Quick Start

A minimal implementation contains one CSV per primary table plus a `data.json` descriptor:

```
survey/
├── site.csv
├── deployment.csv
├── event.csv
├── occurrence.csv
├── sensor_measure.csv
```

## License

Released under [MIT](https://opensource.org/license/mit).
