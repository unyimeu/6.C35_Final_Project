<script>
  import { onMount } from "svelte";
  import RedliningMap from "$lib/RedliningMap.svelte";
  import Flashcard from "$lib/Flashcard.svelte";
  import { scenes } from "$lib/scenes.js";

  let activeScene = 1;
  let stepEls = [];
  let visibleScenes = new Set();

  onMount(() => {
    const sceneObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            activeScene = Number(entry.target.dataset.scene);
          }
        });
      },
      { threshold: 0.45 },
    );

    const animObserver = new IntersectionObserver(
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

    stepEls.forEach((el) => {
      if (el) {
        sceneObserver.observe(el);
        animObserver.observe(el);
      }
    });

    return () => {
      sceneObserver.disconnect();
      animObserver.disconnect();
    };
  });
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
        <RedliningMap {activeScene} on:districtSelect={() => {}} />
      </div>
      <div class="map-caption">HOLC Residential Security Map</div>
    </div>

    <div class="scene-indicator">
      {#each scenes as scene}
        <button
          class="indicator-dot {activeScene === scene.id ? 'active' : ''}"
          aria-label="Scene {scene.id}"
        ></button>
      {/each}
    </div>
  </div>

  <!-- Right: scrolling panels -->
  <div class="scroll-panels">
    {#each scenes as scene, i}
      <div class="panel" bind:this={stepEls[i]} data-scene={scene.id}>
        <div class="panel-inner {visibleScenes.has(scene.id) ? 'visible' : ''}">
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

          <div class="visual-placeholder">
            <div class="placeholder-inner">
              <span class="placeholder-icon">◈</span>
              <span class="placeholder-text"
                >DATA VISUALIZATION — COMING SOON</span
              >
            </div>
          </div>
        </div>
      </div>
    {/each}

    <div class="scroll-end-spacer"></div>
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
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .scene-label {
    font-family: "League Spartan", sans-serif;
    font-size: 0.63rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #c9956b;
    font-weight: 700;
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
</style>
