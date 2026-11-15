(() => {
  if (location.hostname !== 'www.gauss-control.net') return;

  const measurementId = 'G-1VFTC3BXHR';
  const pageUrl = new URL(location.pathname, location.origin);
  const query = new URLSearchParams(location.search);
  for (const name of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'utm_id']) {
    const value = query.get(name);
    if (value && /^[a-z0-9._~-]{1,100}$/i.test(value)) pageUrl.searchParams.set(name, value);
  }

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  gtag('js', new Date());
  gtag('config', measurementId, {
    page_location: pageUrl.href,
    allow_google_signals: false,
    allow_ad_personalization_signals: false
  });

  document.addEventListener('gauss:enquiry-submitted', () => {
    gtag('event', 'generate_lead');
  });

  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
  document.head.append(tag);
})();
