<template>
  <section class="section container">
    <h1 class="section-title">Tracking Missions</h1>
    <p class="section-lede">This is an informational site about different space missions</p>

    <div class="about__grid">
      <article class="about__card">
        <h3>Mission Types</h3>
        <p>
          There are several types of space missions, including cargo resupply missions, satellite
          deployments, and crewed spaceflights.
        </p>
      </article>

      <article class="about__card">
        <h3>History</h3>
        <p>The purpose of this site is to show different space launches.</p>
      </article>

      <article class="about__card">
        <h3>No affiliation</h3>
        <p>
          This site is not affiliated with any space company and is intended for informational
          purposes only.
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
