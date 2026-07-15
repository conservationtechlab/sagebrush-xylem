# Data Model Overview

The diagram shows all five tables, their columns, and foreign-key relationships. Click a table name to open its full documentation.

<div class="schema-diagram-root">
  <div id="diagram-wrapper">
    <div id="tables-grid">

      <div class="schema-column">

        <div class="schema-table schema-table--project schema-table--deployment" id="table-deployment">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/deployment/">deployment</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-deployment-deployment_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>deployment_id</span></div>
            <div class="schema-field" id="field-deployment-site_id"><span class="schema-field-content">site_id</span></div>
            <div class="schema-field" id="field-deployment-device_id"><span class="schema-field-content">device_id</span></div>
            <div class="schema-field" id="field-deployment-start_date"><span class="schema-field-content">start_date</span></div>
            <div class="schema-field" id="field-deployment-end_date"><span class="schema-field-content">end_date</span></div>
            <div class="schema-field" id="field-deployment-deployed_by"><span class="schema-field-content">deployed_by</span></div>
            <div class="schema-field" id="field-deployment-note"><span class="schema-field-content">note</span></div>
            <div class="schema-field" id="field-deployment-lat"><span class="schema-field-content">lat</span></div>
            <div class="schema-field" id="field-deployment-long"><span class="schema-field-content">long</span></div>
            <div class="schema-field" id="field-deployment-geom"><span class="schema-field-content">geom</span></div>
            <div class="schema-field" id="field-deployment-elevation"><span class="schema-field-content">elevation</span></div>
          </div>
        </div>

        <div class="schema-table schema-table--project schema-table--site" id="table-site">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/site/">site</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-site-site_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>site_id</span></div>
            <div class="schema-field" id="field-site-site_code"><span class="schema-field-content">site_code</span></div>
            <div class="schema-field" id="field-site-geom"><span class="schema-field-content">geom</span></div>
          </div>
        </div>
        
        <div class="schema-table schema-table--infrastructure schema-table--device" id="table-device">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/device/">device</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-device-device_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>device_id</span></div>
            <div class="schema-field" id="field-device-serial_number"><span class="schema-field-content">serial_number</span></div>
            <div class="schema-field" id="field-device-device_type_id"><span class="schema-field-content">device_type_id</span></div>
          </div>
        </div>

        <div class="schema-table schema-table--infrastructure schema-table--device_type" id="table-device_type">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/device_type/">device_type</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-device_type-device_type_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>device_type_id</span></div>
            <div class="schema-field" id="field-device_type-brand"><span class="schema-field-content">brand</span></div>
            <div class="schema-field" id="field-device_type-model"><span class="schema-field-content">model</span></div>
            <div class="schema-field" id="field-device_type-code"><span class="schema-field-content">code</span></div>
            <div class="schema-field" id="field-device_type-device_class_id"><span class="schema-field-content">device_class_id</span></div>
          </div>
        </div>
        
        <div class="schema-table schema-table--infrastructure schema-table--device_class" id="table-device_class">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/device_class/">device_class</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-device_class-device_class_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>device_class_id</span></div>
            <div class="schema-field" id="field-device_class-device_class"><span class="schema-field-content">device_class</span></div>
          </div>
        </div>


      </div>

      <div class="schema-column">

        <div class="schema-table schema-table--primary schema-table--event" id="table-event">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/event/">event</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-event-event_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>event_id</span></div>
            <div class="schema-field" id="field-event-type"><span class="schema-field-content">type</span></div>
            <div class="schema-field" id="field-event-start_time"><span class="schema-field-content">start_time</span></div>
            <div class="schema-field" id="field-event-end_time"><span class="schema-field-content">end_time</span></div>
            <div class="schema-field" id="field-event-duration"><span class="schema-field-content">duration</span></div>
            <div class="schema-field" id="field-event-deployment_id"><span class="schema-field-content">deployment_id</span></div>
            <div class="schema-field" id="field-event-media_id"><span class="schema-field-content">media_id</span></div>
          </div>
        </div>

        
        <div class="schema-table schema-table--event schema-table--occurrence" id="table-occurrence">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/occurrence/">occurrence</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-occurrence-occurrence_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>occurrence_id</span></div>
            <div class="schema-field" id="field-occurrence-event_id"><span class="schema-field-content">event_id</span></div>
            <div class="schema-field" id="field-occurrence-model_id"><span class="schema-field-content">model_id</span></div>
            <div class="schema-field" id="field-occurrence-class_id"><span class="schema-field-content">class_id</span></div>
            <div class="schema-field" id="field-occurrence-confidence"><span class="schema-field-content">confidence</span></div>
            <div class="schema-field" id="field-occurrence-validator_id"><span class="schema-field-content">validator_id</span></div>
            <div class="schema-field" id="field-occurrence-annotation_id"><span class="schema-field-content">annotation_id</span></div>
            <div class="schema-field" id="field-occurrence-occurrence_time"><span class="schema-field-content">occurrence_time</span></div>
            <div class="schema-field" id="field-occurrence-media_id"><span class="schema-field-content">media_id</span></div>
          </div>
        </div>

        <div class="schema-table schema-table--event schema-table--media" id="table-media">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/media/">media</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-media-media_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>media_id</span></div>
            <div class="schema-field" id="field-media-media_type"><span class="schema-field-content">media_type</span></div>
            <div class="schema-field" id="field-media-bitrate"><span class="schema-field-content">bitrate</span></div>
            <div class="schema-field" id="field-media-samplerate"><span class="schema-field-content">samplerate</span></div>
            <div class="schema-field" id="field-media-uri"><span class="schema-field-content">uri</span></div>
          </div>
        </div>


         <div class="schema-table schema-table--event schema-table--sensor_measure" id="table-sensor_measure">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/sensor_measure/">sensor_measure</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-sensor_measure-measure_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>measure_id</span></div>
            <div class="schema-field" id="field-sensor_measure-recorded_time"><span class="schema-field-content">recorded_time</span></div>
            <div class="schema-field" id="field-sensor_measure-masure_name"><span class="schema-field-content">masure_name</span></div>
            <div class="schema-field" id="field-sensor_measure-measure_value"><span class="schema-field-content">measure_value</span></div>
            <div class="schema-field" id="field-sensor_measure-event_id"><span class="schema-field-content">event_id</span></div>
          </div>
        </div>
       
        
      </div>


      <div class="schema-column">

        
        <div class="schema-table schema-table--context schema-table--class" id="table-class">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/class/">class</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-class-class_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>class_id</span></div>
            <div class="schema-field" id="field-class-class_type"><span class="schema-field-content">class_type</span></div>
            <div class="schema-field" id="field-class-common_name"><span class="schema-field-content">common_name</span></div>
            <div class="schema-field" id="field-class-kingdom"><span class="schema-field-content">tax_kingdom</span></div>
            <div class="schema-field" id="field-class-phylum"><span class="schema-field-content">tax_phylum</span></div>
            <div class="schema-field" id="field-class-class"><span class="schema-field-content">tax_class</span></div>
            <div class="schema-field" id="field-class-order"><span class="schema-field-content">tax_order</span></div>
            <div class="schema-field" id="field-class-family"><span class="schema-field-content">tax_family</span></div>
            <div class="schema-field" id="field-class-genus"><span class="schema-field-content">tax_genus</span></div>
            <div class="schema-field" id="field-class-species"><span class="schema-field-content">tax_species</span></div>
          </div>
        </div>
        
        <div class="schema-table schema-table--context schema-table--person" id="table-person">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/person/">person</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-person-person_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>person_id</span></div>
            <div class="schema-field" id="field-person-name"><span class="schema-field-content">name</span></div>
            <div class="schema-field" id="field-person-email"><span class="schema-field-content">email</span></div>
          </div>
        </div>

        <div class="schema-table schema-table--context schema-table--model" id="table-model">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/model/">model</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-model-model_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>model_id</span></div>
            <div class="schema-field" id="field-model-name"><span class="schema-field-content">name</span></div>
            <div class="schema-field" id="field-model-type"><span class="schema-field-content">type</span></div>
            <div class="schema-field" id="field-model-url"><span class="schema-field-content">url</span></div>
          </div>
        </div>


        <div class="schema-table schema-table--context schema-table--annotation" id="table-annotation">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/annotation/">annotation</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-annotation-annotation_id"><span class="schema-field-content"><span class="schema-pk-icon"></span>annotation_id</span></div>
            <div class="schema-field" id="field-annotation-timestamp"><span class="schema-field-content">timestamp</span></div>
            <div class="schema-field" id="field-annotation-annotator_id"><span class="schema-field-content">annotator_id</span></div>
          </div>
        </div>

         <div class="schema-table schema-table--context schema-table--uom" id="table-uom">
          <h3 class="schema-title">
            <a class="schema-title-content" href="../tables/uom/">uom</a>
          </h3>
          <div class="schema-fields">
            <div class="schema-field" id="field-uom-measure_name"><span class="schema-field-content"><span class="schema-pk-icon"></span>measure_name</span></div>
            <div class="schema-field" id="field-uom-unit_of_measure"><span class="schema-field-content">unit_of_measure</span></div>
          </div>

        </div>
       
      </div>

      
    </div><!-- #tables-grid -->
    <svg id="connector-layer" xmlns="http://www.w3.org/2000/svg"></svg>
  </div><!-- #diagram-wrapper -->

  <div class="legend-box">
    <p class="legend-title">Legend</p>
    <div class="legend-items">
    <span class="legend-item">
        <span class="legend-swatch legend-swatch--project"></span>
        <span class="legend-label">Project</span>
      </span>
      <span class="legend-item">
        <span class="legend-swatch legend-swatch--infrastructure"></span>
        <span class="legend-label">Infrastructure</span>
      </span>
      <span class="legend-item">
        <span class="legend-swatch legend-swatch--event"></span>
        <span class="legend-label">Event</span>
      </span>
      <span class="legend-item">
        <span class="legend-swatch legend-swatch--context"></span>
        <span class="legend-label">Context</span>
      </span>
      <span class="legend-item">
        <span class="legend-token legend-token--pk">
          <svg class="legend-key-icon" viewBox="0 0 16 16" fill="currentColor">
            <path d="M3.5 11.5a3.5 3.5 0 1 1 3.163-5H14L15.5 8 14 9.5l-1-1-1 1-1-1-1 1-1-1-1.837 1.837A3.5 3.5 0 0 1 3.5 11.5zm-1-4a1 1 0 1 0 2 0 1 1 0 0 0-2 0z"/>
          </svg>
        </span>
        <span class="legend-label">Primary key</span>
      </span>
      <span class="legend-item">
        <span style="display:inline-block;width:44px;border-top:2.5px solid var(--line-color)"></span>
        <span class="legend-label">Foreign key relationship</span>
      </span>
      
    </div>
  </div>
</div>


## Relationships

| FK Table | FK Column | References Table | PK Column |
|----------|-----------|------------------|-----------|
| `sensor_measure` | `masure_name` | `uom` | `measure_name` |
| `sensor_measure` | `event_id` | `event` | `event_id` |
| `occurrence` | `validator_id` | `person` | `person_id` |
| `event` | `deployment_id` | `deployment` | `deployment_id` |
| `event` | `media_id` | `media` | `media_id` |
| `annotation` | `annotator_id` | `person` | `person_id` |
| `deployment` | `site_id` | `site` | `site_id` |
| `deployment` | `device_id` | `device` | `device_id` |
| `device` | `device_type_id` | `device_type` | `device_type_id` |
| `device_type` | `device_class_id` | `device_class` | `device_class_id` |
| `occurrence` | `event_id` | `event` | `event_id` |
| `occurrence` | `model_id` | `model` | `model_id` |
| `occurrence` | `class_id` | `class` | `class_id` |
| `annotation` | `annotation_id` | `occurrence` | `annotation_id` |
| `media` | `media_id` | `occurrence` | `media_id` |
## Table Pages

| Table | Columns | Description |
|-------|---------|-------------|
| [annotation](tables/annotation.md) | 3 |  |
| [class](tables/class.md) | 10 |  |
| [deployment](tables/deployment.md) | 10 |  |
| [device](tables/device.md) | 3 |  |
| [device_class](tables/device_class.md) | 2 |  |
| [device_type](tables/device_type.md) | 5 |  |
| [event](tables/event.md) | 7 |  |
| [media](tables/media.md) | 5 |  |
| [model](tables/model.md) | 4 |  |
| [occurrence](tables/occurrence.md) | 9 |  |
| [person](tables/person.md) | 3 |  |
| [sensor_measure](tables/sensor_measure.md) | 5 |  |
| [site](tables/site.md) | 3 |  |
| [uom](tables/uom.md) | 2 |  |
