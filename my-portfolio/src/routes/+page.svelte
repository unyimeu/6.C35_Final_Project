<script>
  import { onMount, tick } from "svelte";
  import RedliningMap from "$lib/RedliningMap.svelte";
  import Flashcard from "$lib/Flashcard.svelte";
  import { scenes } from "$lib/scenes.js";
  import { base } from "$app/paths";

  let activeScene = 1;
  let stepEls = [];
  let visibleScenes = new Set();

  let districtStats = {};
  let selectedDistrict = null;
  let comparisonDistrict = null;
  let compareMode = false;
  let savedScrollY = 0;

  const demographicFields = [
    { key: "pct_non_hispanic_white", label: "Non-Hispanic White" },
    { key: "pct_non_hispanic_black", label: "Non-Hispanic Black" },
    { key: "pct_non_hispanic_asian", label: "Non-Hispanic Asian" },
    { key: "pct_hispanic", label: "Hispanic" },
    { key: "pct_other_combined", label: "Other / multiracial" },
  ];

  function pct(value) {
    if (value == null) return "—";
    return `${(value * 100).toFixed(1)}%`;
  }

  function comma(value) {
    if (value == null) return "—";
    return value.toLocaleString();
  }
  function resetComparison() {
    selectedDistrict = null;
    comparisonDistrict = null;
    compareMode = false;
  }
  let sceneObserver;
  let animObserver;

  onMount(async () => {
    try {
      const statsRes = await fetch(`${base}/data/districtStats.json`);
      if (!statsRes.ok) {
        throw new Error(
          `Failed to load districtStats.json: ${statsRes.status}`,
        );
      }
      const statsJson = await statsRes.json();
      districtStats = Object.fromEntries(
        statsJson.map((d) => [String(d.area_id), d]),
      );
    } catch (err) {
      console.error("Could not load district stats:", err);
      districtStats = {};
    }

    sceneObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            activeScene = Number(entry.target.dataset.scene);
          }
        });
      },
      { threshold: 0.45 },
    );

    animObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const id = Number(entry.target.dataset.scene);
          if (entry.isIntersecting) {
            visibleScenes = new Set([...visibleScenes, id]);
          } else {
            visibleScenes.delete(id);
            visibleScenes = new Set(visibleScenes);
          }
        });
      },
      { threshold: 0.15 },
    );

    return () => {
      sceneObserver?.disconnect();
      animObserver?.disconnect();
    };
  });

  // we want to re-observe the
  // samme panels whenever they get (re)mounted after returning to timeline
  $: if (sceneObserver && animObserver && !selectedDistrict) {
    tick().then(() => {
      stepEls.forEach((el) => {
        if (el) {
          sceneObserver.observe(el);
          animObserver.observe(el);
        }
      });
      if (savedScrollY > 0) {
        window.scrollTo({ top: savedScrollY, behavior: "instant" });
        savedScrollY = 0;
      }
    });
  }
</script>

<!-- HERO -->
<section class="hero">
  <div class="hero-content">
    <p class="hero-eyebrow">A VISUAL HISTORY</p>
    <h1 class="title">
      CONTEMPORARY<br />
      EFFECTS OF<br />
      REDLINING ON<br />
      MBTA DEVELOPMENT
    </h1>
    <p class="authors">
      Isa de Luis &nbsp;&nbsp; Unyi Usua &nbsp;&nbsp; Rodrigo Gallardo
    </p>
    <p class="scroll-label">SCROLL TO FOLLOW THE TIMELINE ↓</p>
  </div>
  <div class="hero-deco"></div>
</section>

<!-- FLASHCARD -->
<Flashcard />

<!-- TIMELINE -->
<section class="timeline-section">
  <!-- Left: sticky map -->
  <div class="map-sticky-wrapper">
    <div class="map-frame">
      <div class="map-label">BOSTON, 1938</div>
      <div class="map-container">
        <RedliningMap
          {activeScene}
          on:districtSelect={(e) => {
            // save scroll position before swapping views (only when entering from timeline)
            if (!selectedDistrict) {
              savedScrollY = window.scrollY;
            }

            const district = e.detail;
            const statsRecord = districtStats[String(district.id)] ?? null;

            const hydratedDistrict = {
              ...district,
              stats: statsRecord?.stats ?? null,
            };

            // normal mode: one selected district only
            if (!compareMode) {
              selectedDistrict = hydratedDistrict;
              comparisonDistrict = null;
              return;
            }

            // compare mode: fill first slot if empty
            if (!selectedDistrict) {
              selectedDistrict = hydratedDistrict;
              return;
            }

            // ignore clicking the same district again
            if (selectedDistrict.id === hydratedDistrict.id) {
              return;
            }

            // fill second slot if empty
            if (!comparisonDistrict) {
              comparisonDistrict = hydratedDistrict;
              return;
            }

            // if both already filled, replace only the second district
            comparisonDistrict = hydratedDistrict;
          }}
        />
      </div>
      <div class="map-caption">HOLC Residential Security Map</div>
    </div>

    <div class="scene-indicator">
      {#each scenes as scene}
        <button
          class="indicator-dot {activeScene === scene.id ? 'active' : ''}"
          aria-label="Scene {scene.id}"
        ></button>
        <span class="scene-year-dot {activeScene === scene.id ? 'active' : ''}"
          >{scene.year}</span
        >
      {/each}
    </div>
  </div>

  <!-- Right: scrolling panels OR district details -->
  <div class="scroll-panels">
    {#if compareMode && selectedDistrict}
      <div class="panel district-panel-live">
        <div class="panel-inner visible">
          <div class="panel-header">
            <span class="scene-label">DISTRICT COMPARISON</span>
            <span class="scene-divider"></span>
            <span class="scene-year">
              {#if comparisonDistrict}
                2 DISTRICTS SELECTED
              {:else}
                SELECT ONE MORE DISTRICT
              {/if}
            </span>
          </div>

          <div class="policy-tag">INTERACTIVE COMPARISON</div>

          <h2 class="panel-title">Compare Demographics</h2>

          <div class="compare-district-headings">
            <div class="compare-district-card">
              <h3>{selectedDistrict.neighborhood}</h3>
              <p>{selectedDistrict.city}, {selectedDistrict.state}</p>
              <p><strong>HOLC Grade:</strong> {selectedDistrict.grade}</p>
            </div>

            <div class="compare-district-card">
              {#if comparisonDistrict}
                <h3>{comparisonDistrict.neighborhood}</h3>
                <p>{comparisonDistrict.city}, {comparisonDistrict.state}</p>
                <p><strong>HOLC Grade:</strong> {comparisonDistrict.grade}</p>
              {:else}
                <h3>Waiting for second district</h3>
                <p>Click another district on the map.</p>
              {/if}
            </div>
          </div>

          {#if selectedDistrict.stats && comparisonDistrict?.stats}
            <div class="compare-bars">
              {#each demographicFields as field}
                <div class="compare-row">
                  <div class="compare-label">{field.label}</div>

                  <div class="compare-bar-pair">
                    <div class="compare-bar-block">
                      <div class="compare-bar-track">
                        <div
                          class="compare-bar-fill first"
                          style={`width: ${(selectedDistrict.stats[field.key] ?? 0) * 100}%`}
                        ></div>
                      </div>
                      <div class="compare-bar-value">
                        {pct(selectedDistrict.stats[field.key])}
                      </div>
                    </div>

                    <div class="compare-bar-block">
                      <div class="compare-bar-track">
                        <div
                          class="compare-bar-fill second"
                          style={`width: ${(comparisonDistrict.stats[field.key] ?? 0) * 100}%`}
                        ></div>
                      </div>
                      <div class="compare-bar-value">
                        {pct(comparisonDistrict.stats[field.key])}
                      </div>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {/if}

          <div class="panel-actions">
            <button
              class="compare-toggle active"
              on:click={() => {
                compareMode = false;
                comparisonDistrict = null;
              }}
            >
              Exit compare mode
            </button>

            <button
              class="back-to-timeline"
              on:click={() => {
                selectedDistrict = null;
                comparisonDistrict = null;
                compareMode = false;
              }}
            >
              Return to timeline
            </button>
          </div>
        </div>
      </div>
    {:else if selectedDistrict}
      <div class="panel district-panel-live">
        <div class="panel-inner visible">
          <div class="panel-header">
            <span class="scene-label">SELECTED DISTRICT</span>
            <span class="scene-divider"></span>
            <span class="scene-year"
              >{selectedDistrict.city}, {selectedDistrict.state}</span
            >
          </div>

          <div class="policy-tag">HOLC INTERACTIVE VIEW</div>

          <h2 class="panel-title">{selectedDistrict.neighborhood}</h2>

          <p class="panel-body">
            <strong>HOLC Grade:</strong>
            {selectedDistrict.grade}
          </p>

          {#if selectedDistrict.stats}
            <div class="single-bars">
              {#if selectedDistrict.stats.total_population_2020 != null}
                <p class="panel-body">
                  <strong>Total population:</strong>
                  {comma(selectedDistrict.stats.total_population_2020)}
                </p>
              {/if}

              {#each demographicFields as field}
                <div class="single-bar-row">
                  <div class="single-bar-header">
                    <span>{field.label}</span>
                    <span>{pct(selectedDistrict.stats[field.key])}</span>
                  </div>
                  <div class="single-bar-track">
                    <div
                      class="single-bar-fill"
                      style={`width: ${(selectedDistrict.stats[field.key] ?? 0) * 100}%`}
                    ></div>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <p class="panel-body">
              No demographic summary found for this district.
            </p>
          {/if}

          <div class="panel-actions">
            <button
              class="compare-toggle"
              on:click={() => {
                compareMode = true;
                comparisonDistrict = null;
              }}
            >
              Compare two districts
            </button>

            <button
              class="back-to-timeline"
              on:click={() => {
                selectedDistrict = null;
                comparisonDistrict = null;
                compareMode = false;
              }}
            >
              Return to timeline
            </button>
          </div>
        </div>
      </div>
    {:else}
      {#each scenes as scene, i}
        <div class="panel" bind:this={stepEls[i]} data-scene={scene.id}>
          <div
            class="panel-inner {visibleScenes.has(scene.id) ? 'visible' : ''}"
          >
            <div class="panel-header">
              <span class="scene-label">{scene.label}</span>
              <span class="scene-divider"></span>
              <span class="scene-year">{scene.year}</span>
            </div>

            <div class="policy-tag">{scene.policy}</div>
            <h2 class="panel-title">{scene.title}</h2>
            <p class="panel-body">{scene.body}</p>

            <blockquote class="panel-quote">
              <p>{scene.quote}</p>
              <footer>
                <a
                  href={scene.sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {scene.source} ↗
                </a>
              </footer>
            </blockquote>

            {#if scene.stat}
              <div class="stat-callout">
                <span class="stat-bar"></span>
                <div class="stat-content">
                  <p class="stat-text">{scene.stat}</p>
                  <a
                    href={scene.statSourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="stat-source"
                  >
                    {scene.statSource} ↗
                  </a>
                </div>
              </div>
            {/if}

            <figure class="scene-visual">
              <img src="{base}{scene.visual.src}" alt={scene.visual.alt} />
              {#if scene.visual.caption}
                <figcaption>{scene.visual.caption}</figcaption>
              {/if}
            </figure>
          </div>
        </div>
      {/each}

      <div class="scroll-end-spacer"></div>
    {/if}
  </div>
</section>

<style>
  :global(body) {
    background: #f5f0e8;
    margin: 0;
  }

  /* HERO */
  .hero {
    min-height: 100vh;
    display: flex;
    align-items: flex-end;
    background: #f5f0e8;
    padding: 5rem 5rem 4rem;
    position: relative;
    overflow: hidden;
    border-bottom: 3px solid #1a2e3b;
  }

  .hero-deco {
    position: absolute;
    top: -6rem;
    right: -6rem;
    width: 480px;
    height: 480px;
    background: #c9956b;
    opacity: 0.1;
    border-radius: 50%;
    pointer-events: none;
  }

  .hero-content {
    max-width: 780px;
    position: relative;
    z-index: 1;
  }

  .hero-eyebrow {
    font-family: "League Spartan", sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: #c9956b;
    margin: 0 0 1.5rem 0;
    font-weight: 700;
  }

  .title {
    font-family: "League Spartan", sans-serif;
    font-weight: 900;
    font-size: clamp(2.6rem, 5.5vw, 5.5rem);
    line-height: 0.92;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    color: #1a2e3b;
    margin: 0 0 2.5rem 0;
  }

  .authors {
    font-family: "League Spartan", sans-serif;
    font-size: 0.78rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #8a9ba8;
    margin: 0 0 3rem 0;
  }

  .scroll-label {
    font-family: "League Spartan", sans-serif;
    font-size: 0.73rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: #c9956b;
    margin: 0;
    animation: pulse 2.2s ease-in-out infinite;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.3;
    }
  }

  /* TIMELINE LAYOUT */
  .timeline-section {
    display: flex;
    align-items: flex-start;
    background: #f5f0e8;
  }

  /* STICKY MAP */
  .map-sticky-wrapper {
    width: 50%;
    position: sticky;
    top: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 2.5rem 3rem 4rem;
    gap: 1.5rem;
    border-right: 1px solid #ddd5c8;
  }

  .map-frame {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
  }

  .map-label {
    font-family: "League Spartan", sans-serif;
    font-size: 0.62rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #8a9ba8;
    font-weight: 700;
  }

  .map-container {
    width: 100%;
    aspect-ratio: 1 / 1;
    max-height: 62vh;
    border-radius: 14px;
    overflow: hidden;
    border: 2px solid #c8bfb4;
    box-shadow:
      0 4px 0 #c8bfb4,
      0 10px 36px rgba(26, 46, 59, 0.1),
      0 28px 64px rgba(26, 46, 59, 0.07);
    transition: box-shadow 0.4s ease;
  }

  .map-container:hover {
    box-shadow:
      0 4px 0 #c8bfb4,
      0 14px 44px rgba(26, 46, 59, 0.15),
      0 36px 72px rgba(26, 46, 59, 0.1);
  }

  .map-caption {
    font-family: "League Spartan", sans-serif;
    font-size: 0.6rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #b0a898;
  }

  .scene-indicator {
    display: flex;
    gap: 0.55rem;
    align-items: center;
  }

  .indicator-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #d4cbbf;
    border: none;
    padding: 0;
    cursor: pointer;
    transition:
      background 0.3s ease,
      transform 0.3s ease;
  }

  .indicator-dot.active {
    background: #c9956b;
    transform: scale(1.5);
  }

  .scene-year-dot.active {
    color: #c9956b;
    font-weight: 700;
  }

  /* SCROLL PANELS */
  .scroll-panels {
    width: 50%;
  }

  .panel {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 5rem 4rem 5rem 3.5rem;
    border-bottom: 1px solid #ddd5c8;
    position: relative;
  }

  .panel:last-of-type {
    border-bottom: none;
  }

  /* STAGGER ANIMATION SYSTEM */
  .panel-inner {
    display: flex;
    flex-direction: column;
  }

  /* All direct children start invisible and shifted down */
  .panel-inner > * {
    opacity: 0;
    transform: translateY(30px);
  }
  .scroll-panels .panel:first-of-type .panel-inner > * {
    opacity: 1;
    transform: translateY(0);
  }
  /* When visible class added, animate each child with staggered delay */
  .panel-inner.visible .panel-header {
    animation: floatIn 0.55s ease forwards 0s;
  }
  .panel-inner.visible .policy-tag {
    animation: floatIn 0.55s ease forwards 0.1s;
  }
  .panel-inner.visible .panel-title {
    animation: floatIn 0.6s ease forwards 0.18s;
  }
  .panel-inner.visible .panel-body {
    animation: floatIn 0.6s ease forwards 0.27s;
  }
  .panel-inner.visible .panel-quote {
    animation: floatIn 0.6s ease forwards 0.36s;
  }
  .panel-inner.visible .stat-callout {
    animation: floatIn 0.6s ease forwards 0.45s;
  }
  .panel-inner.visible .visual-placeholder {
    animation: floatIn 0.6s ease forwards 0.54s;
  }

  @keyframes floatIn {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* PANEL CONTENT */
  .panel-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .scene-label {
    font-family: "League Spartan", sans-serif;
    font-size: 2rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #c9956b;
    font-weight: 700;
  }

  .scene-year-dot {
    font-family: "League Spartan", sans-serif;
    font-size: 1rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #8a9ba8;

    transition: color 0.3s ease;
  }

  .scene-divider {
    display: block;
    width: 22px;
    height: 1px;
    background: #c8bfb4;
    flex-shrink: 0;
  }

  .scene-year {
    font-family: "League Spartan", sans-serif;
    font-size: 0.63rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #8a9ba8;
  }

  .policy-tag {
    display: inline-block;
    font-family: "League Spartan", sans-serif;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #f5f0e8;
    background: #1a2e3b;
    padding: 0.28rem 0.65rem;
    margin-bottom: 1rem;
    font-weight: 700;
    align-self: flex-start;
  }

  .panel-title {
    font-family: "League Spartan", sans-serif;
    font-weight: 900;
    font-size: clamp(1.8rem, 2.8vw, 2.6rem);
    line-height: 0.95;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    color: #1a2e3b;
    margin: 0 0 1.25rem 0;
  }

  .panel-body {
    font-family: system-ui, sans-serif;
    font-size: 0.965rem;
    line-height: 1.68;
    color: #4a5560;
    margin: 0 0 1.5rem 0;
    max-width: 460px;
  }

  .panel-quote {
    border-left: 3px solid #c9956b;
    margin: 0 0 1.25rem 0;
    padding: 0.65rem 0 0.65rem 1.1rem;
    background: rgba(201, 149, 107, 0.06);
  }

  .panel-quote p {
    font-family: "Georgia", serif;
    font-size: 0.88rem;
    line-height: 1.68;
    color: #3a4a54;
    font-style: italic;
    margin: 0 0 0.5rem 0;
    max-width: 460px;
  }

  .panel-quote footer a {
    font-family: "League Spartan", sans-serif;
    font-size: 0.6rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #8a9ba8;
    text-decoration: none;
    transition: color 0.2s;
  }

  .panel-quote footer a:hover {
    color: #c9956b;
  }

  .stat-callout {
    display: flex;
    gap: 0.85rem;
    align-items: stretch;
    background: #ede7dc;
    border: 1px solid #d4cbbf;
    padding: 0.9rem 1rem;
    margin-bottom: 1.25rem;
    max-width: 460px;
  }

  .stat-bar {
    display: block;
    width: 3px;
    background: #1a2e3b;
    flex-shrink: 0;
  }

  .stat-content {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .stat-text {
    font-family: "League Spartan", sans-serif;
    font-size: 0.86rem;
    font-weight: 700;
    color: #1a2e3b;
    margin: 0;
    line-height: 1.4;
  }

  .stat-source {
    font-family: "League Spartan", sans-serif;
    font-size: 0.58rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #8a9ba8;
    text-decoration: none;
    transition: color 0.2s;
  }

  .stat-source:hover {
    color: #c9956b;
  }

  .visual-placeholder {
    margin-top: 0.5rem;
    border: 1.5px dashed #c8bfb4;
    max-width: 460px;
  }

  .placeholder-inner {
    padding: 2.5rem 1.25rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
  }

  .placeholder-icon {
    font-size: 1.4rem;
    color: #c8bfb4;
  }

  .placeholder-text {
    font-family: "League Spartan", sans-serif;
    font-size: 0.58rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #c8bfb4;
  }

  .scroll-end-spacer {
    height: 40vh;
  }

  /* RESPONSIVE */
  @media (max-width: 900px) {
    .timeline-section {
      flex-direction: column;
    }

    .map-sticky-wrapper {
      width: 100%;
      height: 50vh;
      padding: 1.5rem;
      border-right: none;
      border-bottom: 1px solid #ddd5c8;
    }

    .map-container {
      max-height: 38vh;
    }

    .scroll-panels {
      width: 100%;
    }

    .panel {
      padding: 3rem 2rem;
      min-height: auto;
    }

    .hero {
      padding: 3rem 2rem;
    }
  }

  .district-panel-live {
    min-height: 100vh;
  }

  .district-stats-card {
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
    background: #ede7dc;
    border: 1px solid #d4cbbf;
    padding: 1rem 1rem 0.8rem;
    max-width: 460px;
    margin-bottom: 1.5rem;
  }

  .district-stat-row {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #d8cfc2;
    font-family: system-ui, sans-serif;
    font-size: 0.95rem;
    color: #1a2e3b;
  }

  .district-stat-row span:last-child {
    font-weight: 700;
  }

  .back-to-timeline {
    border: 1px solid #c9956b;
    background: transparent;
    color: #1a2e3b;
    padding: 0.55rem 0.8rem;
    font: inherit;
    cursor: pointer;
    align-self: flex-start;
  }

  .back-to-timeline:hover {
    background: rgba(201, 149, 107, 0.08);
  }

  .district-panel-live .panel-inner > * {
    opacity: 1;
    transform: translateY(0);
  }

  .panel-actions {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    flex-wrap: wrap;
    margin-top: 1rem;
  }

  .compare-toggle,
  .back-to-timeline {
    border: 1px solid #c9956b;
    background: transparent;
    color: #1a2e3b;
    padding: 0.55rem 0.8rem;
    font: inherit;
    cursor: pointer;
  }

  .compare-toggle.active {
    background: #1a2e3b;
    color: #f5f0e8;
  }

  .compare-toggle:hover,
  .back-to-timeline:hover {
    background: rgba(201, 149, 107, 0.08);
  }

  .single-bars,
  .compare-bars {
    max-width: 520px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .single-bar-row,
  .compare-row {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .single-bar-header,
  .compare-label {
    font-family: "League Spartan", sans-serif;
    font-size: 0.8rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #1a2e3b;
  }

  .single-bar-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }

  .single-bar-track,
  .compare-bar-track {
    width: 100%;
    height: 12px;
    background: #ddd5c8;
    overflow: hidden;
  }

  .single-bar-fill,
  .compare-bar-fill {
    height: 100%;
  }

  .single-bar-fill,
  .compare-bar-fill.first {
    background: #1a2e3b;
  }

  .compare-bar-fill.second {
    background: #c9956b;
  }

  .compare-district-headings {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    max-width: 520px;
    margin-bottom: 1.5rem;
  }

  .compare-district-card {
    background: #ede7dc;
    border: 1px solid #d4cbbf;
    padding: 0.9rem;
  }

  .compare-district-card h3 {
    margin: 0 0 0.5rem 0;
    font-family: "League Spartan", sans-serif;
    color: #1a2e3b;
  }

  .compare-district-card p {
    margin: 0.2rem 0;
    color: #4a5560;
  }

  .compare-bar-pair {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .compare-bar-block {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .compare-bar-value {
    font-size: 0.85rem;
    color: #4a5560;
  }

  .panel-inner.visible .scene-visual {
    animation: floatIn 0.6s ease forwards 0.54s;
  }

  .scene-visual {
    margin: 0.5rem 0 0 0;
    max-width: 360px;
  }

  .scene-visual img {
    width: 100%;
    height: auto;
    display: block;
    border: 1px solid #c8bfb4;
  }

  .scene-visual figcaption {
    font-family: "League Spartan", sans-serif;
    font-size: 0.58rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #8a9ba8;
    margin-top: 0.5rem;
  }
</style>
