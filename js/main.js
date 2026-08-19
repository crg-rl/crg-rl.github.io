(() => {
  const button = document.querySelector('[data-copy-bibtex]');
  const block = document.getElementById('bibtex-code');
  if (!button || !block || !navigator.clipboard) return;

  button.addEventListener('click', async () => {
    const original = button.textContent;
    try {
      await navigator.clipboard.writeText(block.textContent.trim());
      button.textContent = 'Copied';
      button.classList.add('copied');
    } catch (_error) {
      button.textContent = 'Select text to copy';
    }
    window.setTimeout(() => {
      button.textContent = original;
      button.classList.remove('copied');
    }, 1800);
  });
})();
