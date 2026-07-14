// Build connections between tables
(function () {
                                const CONNECTIONS = [
    { from: 'field-uom-measure_name', to: 'field-sensor_measure-masure_name' },
    { from: 'field-event-event_id', to: 'field-sensor_measure-event_id' },
    { from: 'field-person-person_id', to: 'field-occurrence-validator_id' },
    { from: 'field-deployment-deployment_id', to: 'field-event-deployment_id' },
    { from: 'field-media-media_id', to: 'field-event-media_id' },
    { from: 'field-person-person_id', to: 'field-annotation-annotator_id' },
    { from: 'field-site-site_id', to: 'field-deployment-site_id' },
    { from: 'field-device-device_id', to: 'field-deployment-device_id' },
    { from: 'field-device_type-device_type_id', to: 'field-device-device_type_id' },
    { from: 'field-device_class-device_class_id', to: 'field-device_type-device_class_id' },
    { from: 'field-event-event_id', to: 'field-occurrence-event_id' },
    { from: 'field-model-model_id', to: 'field-occurrence-model_id' },
    { from: 'field-class-class_id', to: 'field-occurrence-class_id' },
    { from: 'field-occurrence-annotation_id', to: 'field-annotation-annotation_id' },
    { from: 'field-occurrence-media_id', to: 'field-media-media_id' },
  ];

  function draw() {
    const svg = document.getElementById('connector-layer');
    const wrapper = document.getElementById('diagram-wrapper');
    if (!svg || !wrapper) return;

    svg.setAttribute('width', wrapper.offsetWidth);
    svg.setAttribute('height', wrapper.offsetHeight);

    // Clear previous connectors, keep defs
    svg.querySelectorAll('.connector').forEach(el => el.remove());

    const wr = wrapper.getBoundingClientRect();

    for (const { from, to } of CONNECTIONS) {
      const fromEl = document.getElementById(from);
      const toEl   = document.getElementById(to);
      if (!fromEl || !toEl) continue;

      const fr = fromEl.getBoundingClientRect();
      const tr = toEl.getBoundingClientRect();

      const fy = fr.top + fr.height / 2 - wr.top;
      const ty = tr.top + tr.height / 2 - wr.top;
      const fromCx = fr.left + fr.width / 2 - wr.left;
      const toCx   = tr.left + tr.width / 2 - wr.left;

      const fy2 = fy, ty2 = ty;
      let d;

      if (fromCx < toCx - 20) {
        // left → right: exit right edge, elbow at midpoint between cols, enter left edge
        const x1 = fr.right - wr.left;
        const x2 = tr.left - wr.left;
        const mx = (x1 + x2) / 2;
        d = `M${x1},${fy2} L${mx},${fy2} L${mx},${ty2} L${x2},${ty2}`;
      } else if (fromCx > toCx + 20) {
        // right → left: exit left edge, elbow at midpoint between cols, enter right edge
        // (mirrors the left→right case — vertical segment stays in the inter-column gap)
        const x1 = fr.left - wr.left;
        const x2 = tr.right - wr.left;
        const mx = (x1 + x2) / 2;
        d = `M${x1},${fy2} L${mx},${fy2} L${mx},${ty2} L${x2},${ty2}`;
      } else {
        // same column: arc out to the right far enough to clear the right→left midpoint
        const x1 = fr.right - wr.left;
        const x2 = tr.right - wr.left;
        const rx = Math.max(x1, x2) + 36;
        d = `M${x1},${fy2} L${rx},${fy2} L${rx},${ty2} L${x2},${ty2}`;
      }

      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('class', 'connector');
      path.setAttribute('d', d);
      path.dataset.from = from;
      path.dataset.to = to;
      svg.appendChild(path);
    }
  }

  function tableNameFromFieldId(fieldId) {
    // field-{tableName}-{colName} — table name is always the middle segment
    return fieldId.split('-')[1];
  }

  function buildTableLinks() {
    const links = {};
    for (const { from, to } of CONNECTIONS) {
      const a = tableNameFromFieldId(from);
      const b = tableNameFromFieldId(to);
      (links[a] = links[a] || new Set()).add(b);
      (links[b] = links[b] || new Set()).add(a);
    }
    return links;
  }

  function attachHover() {
    const tableLinks = buildTableLinks();
    const tables = document.querySelectorAll('.schema-table');

    tables.forEach(tableEl => {
      const tableName = tableEl.id.replace('table-', '');
      const connected = tableLinks[tableName] || new Set();

      tableEl.addEventListener('mouseenter', () => {
        tables.forEach(el => {
          const n = el.id.replace('table-', '');
          if (n === tableName) return;
          el.classList.toggle('schema-table--dim', !connected.has(n));
          el.classList.toggle('schema-table--highlight', connected.has(n));
        });
        document.querySelectorAll('.connector').forEach(c => {
          const a = tableNameFromFieldId(c.dataset.from || '');
          const b = tableNameFromFieldId(c.dataset.to || '');
          const related = a === tableName || b === tableName;
          c.classList.toggle('connector--dim', !related);
          c.classList.toggle('connector--active', related);
        });
      });

      tableEl.addEventListener('mouseleave', () => {
        tables.forEach(el => el.classList.remove('schema-table--dim', 'schema-table--highlight'));
        document.querySelectorAll('.connector').forEach(c => c.classList.remove('connector--dim', 'connector--active'));
      });
    });
  }

  let resizeObs = null;

  function init() {
    const svg = document.getElementById('connector-layer');
    if (!svg) return;

    requestAnimationFrame(draw);
    attachHover();

    if (resizeObs) { resizeObs.disconnect(); resizeObs = null; }

    const wrapper = document.getElementById('diagram-wrapper');
    if (wrapper && window.ResizeObserver) {
      resizeObs = new ResizeObserver(() => requestAnimationFrame(draw));
      resizeObs.observe(wrapper);
    } else {
      window.addEventListener('resize', () => requestAnimationFrame(draw));
    }
  }

  // MkDocs Material instant navigation support
  if (typeof document$ !== 'undefined') {
    document$.subscribe(init);
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
