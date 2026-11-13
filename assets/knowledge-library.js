const library = document.querySelector('.knowledge-library');
const search = library.querySelector('.library-search input');
const groups = [...library.querySelectorAll('.library-topic')].map(group => ({
  group,
  jump: library.querySelector(`a[href="#${group.id}"]`),
  articles: [...group.querySelectorAll('li')].map(item => ({
    item,
    text: `${group.querySelector('h3').textContent} ${item.textContent} ${item.dataset.keywords}`.toLowerCase(),
  })),
}));

function filterLibrary() {
  const terms = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
  let hasResults = false;
  for (const {group, jump, articles} of groups) {
    for (const {item, text} of articles) {
      item.hidden = !terms.every(term => text.includes(term));
    }
    group.hidden = articles.every(({item}) => item.hidden);
    jump.hidden = group.hidden;
    hasResults ||= !group.hidden;
  }
  library.querySelector('.library-empty').hidden = hasResults;
}

search.closest('.library-search').hidden = false;
search.addEventListener('input', filterLibrary);
filterLibrary();
