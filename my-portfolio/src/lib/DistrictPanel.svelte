<script>
  export let district = null;
</script>

<div class="panel">
  {#if district}
    <h2>{district.neighborhood}</h2>
    <p><strong>HOLC Grade:</strong> {district.grade}</p>
    <p>{district.description}</p>

    {#if district.city || district.state}
      <p><strong>Location:</strong> {district.city}{district.city && district.state ? ', ' : ''}{district.state}</p>
    {/if}
  {:else}
    <p>Click a district on the map to inspect it.</p>
  {/if}
</div>

<style>
  .panel {
    background: #001f3a;
    color: #f7f3ee;
    padding: 2rem;
    border-left: 14px solid #e3a37b;
    /* min-height: 220px; */
    height: 100%;
  }

  h2 {
    margin: 0 0 1rem;
    font-size: 2rem;
  }

  p {
    margin: 0 0 1rem;
    line-height: 1.4;
  }
</style>