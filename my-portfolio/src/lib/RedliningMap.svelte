<script>
  import { onMount, createEventDispatcher } from "svelte";
  import { base } from "$app/paths";
  import { geoIdentity, geoPath } from "d3-geo";
  import { interpolate } from "d3-interpolate";

  export let expanded = false;
  export let activeScene = 1;

  const dispatch = createEventDispatcher();

  const VIEW_W = 1000;
  const VIEW_H = 1000;

  const ROXBURY_BBOX = {
    minLng: -71.1,
    maxLng: -71.07,
    minLat: 42.31,
    maxLat: 42.34,
  };

  let geojsonData = null;
  let projection = null;
  let pathGenerator = null;
  let selectedId = null;
  let hoveredId = null;

  let dGradeIds = new Set();
  let abGradeIds = new Set();
  let roxburyIds = new Set();


  const fullViewBox = [0, 0, VIEW_W, VIEW_H];
  let currentViewBox = fullViewBox;
  let roxburyViewBox = fullViewBox;
  let viewBoxStr = `0 0 ${VIEW_W} ${VIEW_H}`;


  let rafId = null;

  function featureCentroidLngLat(feature) {
    const geom = feature.geometry;
    if (!geom) return null;

    let coords = null;
    if (geom.type === "Polygon") {
      coords = geom.coordinates[0];
    } else if (geom.type === "MultiPolygon") {
      coords = geom.coordinates[0][0];
    }
    if (!coords || coords.length === 0) return null;

    let sumLng = 0;
    let sumLat = 0;
    for (const [lng, lat] of coords) {
      sumLng += lng;
      sumLat += lat;
    }
    return [sumLng / coords.length, sumLat / coords.length];
  }

  function isInRoxbury(feature) {
    if (feature.properties.city !== "Boston") return false;
    const centroid = featureCentroidLngLat(feature);
    if (!centroid) return false;
    const [lng, lat] = centroid;
    return (
      lng >= ROXBURY_BBOX.minLng &&
      lng <= ROXBURY_BBOX.maxLng &&
      lat >= ROXBURY_BBOX.minLat &&
      lat <= ROXBURY_BBOX.maxLat
    );
  }

  function viewBoxFor(features, pad = 40) {
    if (!features.length || !pathGenerator) return fullViewBox;

    const fc = { type: "FeatureCollection", features };
    const [[x0, y0], [x1, y1]] = pathGenerator.bounds(fc);

    const w = x1 - x0 + pad * 2;
    const h = y1 - y0 + pad * 2;
    const size = Math.max(w, h);
    const cx = (x0 + x1) / 2;
    const cy = (y0 + y1) / 2;
    return [cx - size / 2, cy - size / 2, size, size];
  }

  const DIM = 0.15;
  function sceneOpacity(feature, scene) {
    const id = feature.properties.area_id;

    if (scene === 1) return 1;
    if (scene === 2 || scene === 4) return dGradeIds.has(id) ? 1 : DIM;
    if (scene === 3) return abGradeIds.has(id) ? 1 : DIM;
    if (scene === 5) return roxburyIds.has(id) ? 1 : DIM;
    return 1;
  }

  function sceneHighlightIds(scene) {
    if (scene === 2 || scene === 4) return dGradeIds;
    if (scene === 3) return abGradeIds;
    if (scene === 5) return roxburyIds;
    return new Set();
  }

  // Animated viewBox tween using d3-interpolate + requestAnimationFrame.
  function animateViewBox(target, duration = 1200) {
    if (rafId != null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }

    const start = currentViewBox;
    const end = target;
    const interp = interpolate(start, end);
    const startTime = performance.now();

    const ease = (t) =>
      t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

    function frame(now) {
      const elapsed = now - startTime;
      const t = Math.min(1, elapsed / duration);
      const v = interp(ease(t));
      currentViewBox = v;
      viewBoxStr = `${v[0]} ${v[1]} ${v[2]} ${v[3]}`;
      if (t < 1) {
        rafId = requestAnimationFrame(frame);
      } else {
        rafId = null;
      }
    }

    rafId = requestAnimationFrame(frame);
  }

  onMount(async () => {
    try {
      const response = await fetch(`${base}/data/redlining.geojson`);
      if (!response.ok) {
        throw new Error(`Failed to fetch GeoJSON: ${response.status}`);
      }
      geojsonData = await response.json();

      projection = geoIdentity()
        .reflectY(true)
        .fitSize([VIEW_W, VIEW_H], geojsonData);
      pathGenerator = geoPath(projection);

      for (const feature of geojsonData.features) {
        const id = feature.properties.area_id;
        const grade = feature.properties.grade;
        if (grade === "D") dGradeIds.add(id);
        if (grade === "A" || grade === "B") abGradeIds.add(id);
        if (isInRoxbury(feature)) roxburyIds.add(id);
      }

      const roxburyFeatures = geojsonData.features.filter((f) =>
        roxburyIds.has(f.properties.area_id),
      );
      roxburyViewBox = viewBoxFor(roxburyFeatures, 60);
      currentViewBox = fullViewBox;
      viewBoxStr = `${fullViewBox[0]} ${fullViewBox[1]} ${fullViewBox[2]} ${fullViewBox[3]}`;
    } catch (err) {
      console.error("Map setup failed:", err);
    }

    return () => {
      if (rafId != null) cancelAnimationFrame(rafId);
    };
  });
  $: if (pathGenerator) {
    const target = activeScene === 5 ? roxburyViewBox : fullViewBox;
    animateViewBox(target);
  }

  $: highlightIds = sceneHighlightIds(activeScene);

  function handleDistrictClick(feature) {
    const props = feature.properties || {};

    const district = {
      id: props.area_id,
      neighborhood: props.label || `District ${props.area_id}`,
      grade: props.grade || "Unknown",
      description: `${props.city}, ${props.state} — ${props.category || "No category"}`,
      city: props.city || "",
      state: props.state || "",
      raw: props,
    };

    selectedId = props.area_id;
    dispatch("districtSelect", district);
  }
</script>

<div class:expanded class="map-shell">
  {#if geojsonData && pathGenerator}
    <svg
      class="map"
      viewBox={viewBoxStr}
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="HOLC redlining map of Greater Boston"
    >
      <!-- Base layer -->
      <g class="districts">
        {#each geojsonData.features as feature (feature.properties.area_id)}
          <path
            d={pathGenerator(feature)}
            fill={feature.properties.fill || "#999999"}
            fill-opacity={sceneOpacity(feature, activeScene)}
            stroke="#111111"
            stroke-width="0.6"
            class="district"
            class:hovered={hoveredId === feature.properties.area_id}
            on:click={() => handleDistrictClick(feature)}
            on:mouseenter={() => (hoveredId = feature.properties.area_id)}
            on:mouseleave={() => (hoveredId = null)}
            on:keydown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                handleDistrictClick(feature);
              }
            }}
            role="button"
            tabindex="0"
            aria-label="District {feature.properties.label} in {feature
              .properties.city}, grade {feature.properties.grade}"
          />
        {/each}
      </g>

      <g class="scene-highlights" pointer-events="none">
        {#each geojsonData.features.filter( (f) => highlightIds.has(f.properties.area_id), ) as feature (feature.properties.area_id)}
          <path
            d={pathGenerator(feature)}
            fill="none"
            stroke="#1a2e3b"
            stroke-width="2"
            stroke-linejoin="round"
            class="scene-highlight-path"
          />
        {/each}
      </g>

      {#if selectedId != null}
        {#each geojsonData.features.filter((f) => f.properties.area_id === selectedId) as feature}
          <path
            d={pathGenerator(feature)}
            fill="none"
            stroke="#ffffff"
            stroke-width="2.5"
            stroke-linejoin="round"
            pointer-events="none"
          />
        {/each}
      {/if}
    </svg>
  {/if}
</div>

<style>
  .map-shell {
    position: relative;
    width: 100%;
    height: 100%;
    background: #f5f0e8;
    overflow: hidden;
  }

  .map-shell.expanded {
    position: fixed;
    inset: 2rem;
    z-index: 1000;
    height: auto;
    min-height: 80vh;
    border-width: 6px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
  }

  .map {
    width: 100%;
    height: 100%;
    display: block;
  }

  .district {
    cursor: pointer;
    transition:
      fill-opacity 0.6s ease,
      stroke-width 0.2s ease;
  }

  .district.hovered {
    stroke-width: 1.4;
    stroke: #ffffff;
  }

  .district:focus {
    outline: none;
    stroke-width: 1.4;
    stroke: #ffffff;
  }

  .scene-highlight-path {
    transition: opacity 0.6s ease;
  }
</style>
