const heroVisual = document.querySelector('.hero-visual');
const slides = [...heroVisual.querySelectorAll('.hero-slide')];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const interval = 6500;
let current = 0;
let timer;
let generation = 0;

function isRunning() {
  return !document.hidden && !reducedMotion.matches && !document.body.classList.contains('paused');
}

async function showNext(cycle) {
  for (let step = 1; step < slides.length; step++) {
    const next = (current + step) % slides.length;
    const incoming = slides[next];
    if (!incoming.getAttribute('src')) {
      incoming.srcset = incoming.dataset.srcset;
      incoming.src = incoming.dataset.src;
    }
    try {
      await incoming.decode();
    } catch {
      continue;
    }
    if (cycle !== generation || !isRunning()) return;
    const outgoing = slides[current];
    incoming.classList.add('is-visible', 'is-current');
    outgoing.classList.remove('is-current', 'is-visible');
    current = next;
    break;
  }
  if (cycle === generation) schedule();
}

function schedule() {
  clearTimeout(timer);
  const cycle = ++generation;
  if (isRunning()) timer = setTimeout(() => showNext(cycle), interval);
}

document.addEventListener('visibilitychange', schedule);
reducedMotion.addEventListener('change', schedule);
new MutationObserver(schedule).observe(document.body, {attributes: true, attributeFilter: ['class']});
slides[0].decode().then(schedule, schedule);
