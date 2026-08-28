<template>
  <section class="section container">
    <p class="eyebrow">About this site</p>
    <h1 class="section-title">Tracking every flight, in real time.</h1>
    <p class="section-lede">
      This is an informational dashboard for SpaceX missions — built to give a
      quick, at-a-glance view of what's flown, what's upcoming, and the
      vehicles behind it all.
    </p>

    <div class="about__grid">
      <article class="about__card">
        <h3>Launch feed</h3>
        <p>
          Every tracked mission, past and upcoming, with status, mission
          patch, and flight number pulled straight from the launch data.
        </p>
      </article>

      <article class="about__card">
        <h3>Vehicle roster</h3>
        <p>
          A look at the rockets flying these missions — from the workhorse
          Falcon 9 to Starship, still in active development.
        </p>
      </article>

      <article class="about__card">
        <h3>Not affiliated with SpaceX</h3>
        <p>
          This is an independent, informational project built for fans who
          want a clean way to follow the launch schedule. It is not run by or
          affiliated with SpaceX.
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
