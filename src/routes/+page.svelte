<script>
  import { onMount } from 'svelte';
  import RedliningMap from '$lib/RedliningMap.svelte';
  import DistrictPanel from '$lib/DistrictPanel.svelte';

  let expanded = false;
  let selectedDistrict = null;
  let activeStep = 0;

  let stepEls = [];

  const steps = [
    {
      year: '1940s',
      text: 'HOLC maps categorized neighborhoods by perceived lending risk.'
    },
    {
      year: 'Later impacts',
      text: 'These categories shaped patterns of investment, disinvestment, and access.'
    },
    {
      year: 'Explore',
      text: 'Click the map to inspect individual districts and where they are.'
    }
  ];

  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            activeStep = Number(entry.target.dataset.step);
          }
        });
      },
      { threshold: 0.6 }
    );

    stepEls.forEach((el) => el && observer.observe(el));

    return () => observer.disconnect();
  });
</script>

<section class="hero">
  <div class="hero-content">
    <h1 class="title">
      CONTEMPORARY<br />
      EFFECTS OF<br />
      REDLINING ON MBTA<br />
      DEVELOPMENT
    </h1>

    <p class="authors">Isa de Luis, Unyi Usua, Rodrigo Gallardo</p>
    <p class="scroll-label">SCROLL TO FOLLOW THE TIMELINE ↓</p>
  </div>
</section>

<section class="timeline-section">
  <div class="year-tag">1940s</div>
  <div class="timeline-line"></div>

  <div class="grid">
    <div class="map-column">
      <RedliningMap
        {expanded}
        {activeStep}
        on:toggleExpand={() => (expanded = !expanded)}
        on:districtSelect={(e) => {
          selectedDistrict = e.detail;
          expanded = true;
        }}
      />
    </div>

    <div class="text-column">
      <DistrictPanel district={selectedDistrict} />
      <p class="source">City Survey Files, 1935–1940</p>
    </div>
  </div>
</section>

<section class="scrolly">
  {#each steps as step, i}
    <div class="step" bind:this={stepEls[i]} data-step={i}>
      <h3>{step.year}</h3>
      <p>{step.text}</p>
    </div>
  {/each}
</section>