<template>
  <section class="section container">
    <h1 class="section-title">Tracking Missions</h1>
    <p class="section-lede">This is an informational site about SpaceX's missions</p>

    <div class="about__grid">
      <article class="about__card">
        <h3>Mission Types</h3>
        <p>
          SpaceX conducts a variety of missions, including satellite launches, cargo resupply
          missions, and crewed spaceflights.
        </p>
      </article>

      <article class="about__card">
        <h3>History</h3>
        <p>The purpose of this site is to give a historical lens of SpaceX's launches.</p>
      </article>

      <article class="about__card">
        <h3>Not affiliated with SpaceX</h3>
        <p>
          This site is not affiliated with SpaceX and is intended for informational purposes only.
        </p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.about__grid {
  margin-top: 40px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.about__card {
  background: var(--color-bg-raised);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 22px;
}

.about__card h3 {
  font-size: 17px;
  font-weight: 600;
}

.about__card p {
  margin-top: 10px;
  color: var(--color-text-dim);
  font-size: 14px;
  line-height: 1.6;
}
</style>
