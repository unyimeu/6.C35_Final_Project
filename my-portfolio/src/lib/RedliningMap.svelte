<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import maplibregl from 'maplibre-gl';
  import 'maplibre-gl/dist/maplibre-gl.css';

  export let expanded = false;
  export let activeStep = 0;

  const dispatch = createEventDispatcher();

  let mapContainer;
  let map;
  let geojsonData = null;

  const bostonCenter = [-71.0589, 42.3601];

  function fitToGeoJSON(data) {
    const bounds = new maplibregl.LngLatBounds();

    for (const feature of data.features) {
      const geom = feature.geometry;
      if (!geom) continue;

      if (geom.type === 'Polygon') {
        for (const ring of geom.coordinates) {
          for (const coord of ring) bounds.extend(coord);
        }
      }

      if (geom.type === 'MultiPolygon') {
        for (const polygon of geom.coordinates) {
          for (const ring of polygon) {
            for (const coord of ring) bounds.extend(coord);
          }
        }
      }
    }

    if (!bounds.isEmpty()) {
      map.fitBounds(bounds, { padding: 40, duration: 0 });
    }
  }

  function updateStepStyling() {
    if (!map || !map.getLayer('redlining-fill')) return;

    if (activeStep === 0) {
      map.setPaintProperty('redlining-fill', 'fill-opacity', 0.65);
      map.setPaintProperty('redlining-outline', 'line-opacity', 0.9);
    } else if (activeStep === 1) {
      map.setPaintProperty('redlining-fill', 'fill-opacity', 0.85);
      map.setPaintProperty('redlining-outline', 'line-opacity', 1);
    } else {
      map.setPaintProperty('redlining-fill', 'fill-opacity', 0.5);
      map.setPaintProperty('redlining-outline', 'line-opacity', 0.75);
    }
  }

  onMount(async () => {
    try {
      const response = await fetch('/data/redlining.geojson');
      if (!response.ok) {
        throw new Error(`Failed to fetch GeoJSON: ${response.status}`);
      }

      geojsonData = await response.json();
      console.log('GeoJSON loaded:', geojsonData);
      console.log('First feature:', geojsonData.features?.[0]);

      map = new maplibregl.Map({
        container: mapContainer,
        style: {
          version: 8,
          sources: {
            osm: {
              type: 'raster',
              tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
              tileSize: 256,
              attribution: '&copy; OpenStreetMap contributors'
            }
          },
          layers: [
            {
              id: 'osm',
              type: 'raster',
              source: 'osm'
            }
          ]
        },
        center: bostonCenter,
        zoom: 10
      });

      map.addControl(new maplibregl.NavigationControl(), 'top-right');

      map.on('load', () => {
        console.log('Map loaded');

        map.addSource('redlining', {
          type: 'geojson',
          data: geojsonData
        });

        map.addLayer({
          id: 'redlining-fill',
          type: 'fill',
          source: 'redlining',
          paint: {
            'fill-color': ['coalesce', ['get', 'fill'], '#999999'],
            'fill-opacity': 0.65
          }
        });

        map.addLayer({
          id: 'redlining-outline',
          type: 'line',
          source: 'redlining',
          paint: {
            'line-color': '#111111',
            'line-width': 1.5,
            'line-opacity': 0.9
          }
        });

        map.addLayer({
          id: 'redlining-highlight',
          type: 'line',
          source: 'redlining',
          paint: {
            'line-color': '#ffffff',
            'line-width': 4,
            'line-opacity': 1
          },
          filter: ['==', ['get', 'area_id'], -1]
        });

        fitToGeoJSON(geojsonData);
        updateStepStyling();

        map.on('mouseenter', 'redlining-fill', () => {
          map.getCanvas().style.cursor = 'pointer';
        });

        map.on('mouseleave', 'redlining-fill', () => {
          map.getCanvas().style.cursor = '';
        });

        map.on('click', 'redlining-fill', (e) => {
          const feature = e.features?.[0];
          if (!feature) return;

          const props = feature.properties || {};

          const district = {
            id: props.area_id,
            neighborhood: props.label || `District ${props.area_id}`,
            grade: props.grade || 'Unknown',
            description: `${props.city}, ${props.state} — ${props.category || 'No category'}`,
            city: props.city || '',
            state: props.state || '',
            raw: props
          };

          map.setFilter('redlining-highlight', [
            '==',
            ['get', 'area_id'],
            props.area_id
          ]);

          dispatch('districtSelect', district);
        });

        setTimeout(() => map.resize(), 100);
      });

      map.on('error', (e) => {
        console.error('MapLibre error:', e);
      });
    } catch (err) {
      console.error('Map setup failed:', err);
    }
  });

  $: if (map) {
    setTimeout(() => map.resize(), 0);
  }

  $: if (map && map.isStyleLoaded()) {
    updateStepStyling();
  }
</script>

<div class:expanded class="map-shell">
  <button class="expand-button" on:click={() => dispatch('toggleExpand')}>
    {expanded ? 'Close map' : 'Expand map'}
  </button>
  <div bind:this={mapContainer} class="map"></div>
</div>

<style>
  .map-shell {
    position: relative;
    width: calc(100% - 100px);
    height: 420px;
    min-height: 420px;
    border: 4px solid #111;
    background: white;
    overflow: hidden;
    margin: 1em;

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
    min-height: 420px;
  }

  .expand-button {
    position: absolute;
    top: 1rem;
    right: 1rem;
    z-index: 2;
    border: none;
    background: #001f3a;
    color: white;
    padding: 0.7rem 1rem;
    font: inherit;
    font-weight: 700;
    cursor: pointer;
  }
</style>