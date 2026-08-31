// hedron-extras composition helpers
export function mountComposition(el) {
  el.dataset.hedronComposition = 'ready';
  const groups = el.querySelectorAll('[data-hedron-choice="cards"][data-hedron-required="true"]');
  groups.forEach((group) => {
    const inputs = group.querySelectorAll('input[type="checkbox"]');
    if (!inputs.length) return;
    const validate = () => {
      const valid = Array.from(inputs).some((input) => input.checked);
      inputs[0].setCustomValidity(valid ? '' : 'Select at least one option.');
    };
    inputs.forEach((input) => input.addEventListener('change', validate));
    const form = group.closest('form');
    if (form) form.addEventListener('submit', (event) => {
      validate();
      if (!form.checkValidity()) event.preventDefault();
    });
    validate();
  });
}
