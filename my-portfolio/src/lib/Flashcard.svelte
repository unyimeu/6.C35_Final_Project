<script>
  let flipped = false;
</script>

<section class="flashcard-section">
  <button
    class="flashcard {flipped ? 'flipped' : ''}"
    on:click={() => (flipped = !flipped)}
    aria-label="Flip redlining flashcard"
  >
    <div class="flashcard-inner">
      <div class="flashcard-face flashcard-front">
        <h2>WHAT IS<br />REDLINING?</h2>
      </div>
      <div class="flashcard-face flashcard-back">
        <p>
          Redlining is the systematic denial of financial services to residents
          of certain areas, based on their race or ethnicity.
        </p>
      </div>
    </div>
  </button>
</section>

<style>
  .flashcard-section {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #e8e0d5;
    padding: 2rem;
    border-bottom: 3px solid #1a2e3b;
  }

  .flashcard {
    width: min(1100px, 90vw);
    height: min(620px, 75vh);
    perspective: 1400px;
    border: none;
    background: transparent;
    padding: 0;
    cursor: pointer;
  }

  .flashcard-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.7s ease;
    transform-style: preserve-3d;
  }

  .flashcard.flipped .flashcard-inner {
    transform: rotateY(180deg);
  }

  .flashcard-face {
    position: absolute;
    inset: 0;
    backface-visibility: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2.5rem 3rem;
    background: #1a2e3b;
    box-shadow: 0 20px 45px rgba(26, 46, 59, 0.2);
  }

  .flashcard-front {
    transform: rotate(-3deg);
  }

  .flashcard-back {
    transform: rotateY(180deg) rotate(-3deg);
  }

  .flashcard-front h2 {
    margin: 0;
    font-family: 'League Spartan', sans-serif;
    font-weight: 900;
    font-size: clamp(3.5rem, 9vw, 8rem);
    line-height: 0.88;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: #f7f3ee;
    text-align: left;
    width: 100%;
  }

  .flashcard-back p {
    margin: 0;
    max-width: 820px;
    font-family: system-ui, sans-serif;
    font-size: clamp(1.4rem, 2.4vw, 2.3rem);
    line-height: 1.35;
    color: #f7f3ee;
    text-align: center;
  }

  .flashcard:hover .flashcard-inner {
    transform: scale(1.01);
  }

  .flashcard.flipped:hover .flashcard-inner {
    transform: rotateY(180deg) scale(1.01);
  }

  .flashcard:focus-visible {
    outline: 3px solid #c9956b;
    outline-offset: 8px;
  }

  @media (max-width: 700px) {
    .flashcard { height: min(500px, 70vh); }
    .flashcard-face { padding: 1.5rem; }
    .flashcard-front h2 { font-size: clamp(2.8rem, 12vw, 5rem); }
    .flashcard-back p { font-size: clamp(1.1rem, 4vw, 1.5rem); }
  }
</style>
