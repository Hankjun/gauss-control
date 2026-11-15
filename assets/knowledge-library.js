const library = document.querySelector('.knowledge-library');
const search = library.querySelector('#library-search');
const clear = library.querySelector('.library-clear');
const count = library.querySelector('.library-count');
const empty = library.querySelector('.library-empty');

const normalize = text => text.toLocaleLowerCase().normalize('NFD').replace(/\p{M}/gu, '');
const groups = [...library.querySelectorAll('.library-topic')].map(group => ({
  group,
  jump: library.querySelector(`a[href="#${group.id}"]`),
  articles: [...group.querySelectorAll('li')].map(item => ({
    item,
    text: normalize(`${group.querySelector('h3').textContent} ${item.textContent} ${item.dataset.keywords}`),
  })),
}));
const total = groups.reduce((sum, {articles}) => sum + articles.length, 0);

function filterLibrary() {
  const query = normalize(search.value.trim());
  const terms = query ? query.split(/\s+/) : [];
  let matches = 0;
  for (const {group, jump, articles} of groups) {
    let visible = 0;
    for (const {item, text} of articles) {
      item.hidden = !terms.every(term => text.includes(term));
      visible += Number(!item.hidden);
    }
    group.hidden = visible === 0;
    jump.hidden = group.hidden;
    matches += visible;
  }
  count.textContent = count.dataset.format.replace('{count}', matches).replace('{total}', total);
  clear.disabled = !search.value;
  empty.hidden = matches !== 0;
}

search.closest('.library-search').hidden = false;
search.addEventListener('input', filterLibrary);
clear.addEventListener('click', () => {
  search.value = '';
  filterLibrary();
  search.focus();
});
filterLibrary();
