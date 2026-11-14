(() => {
  const form = document.querySelector('.contact-form[data-enquiry]');
  if (!form) return;
  const button = form.querySelector('button[type="submit"]');
  const status = form.querySelector('#form-status');
  const language = document.documentElement.lang.split('-')[0];
  const copy = {
    en: ['Sending your enquiry…', 'Your enquiry was submitted. Thank you.', 'We could not confirm submission. Your details are still here; try again or contact us by email.'],
    zh: ['正在提交询盘…', '询盘已提交，谢谢。', '暂未确认提交成功。填写的信息已保留，请重试或直接发邮件联系我们。'],
    es: ['Enviando su consulta…', 'Su consulta se ha enviado. Gracias.', 'No pudimos confirmar el envío. Sus datos se conservan; inténtelo de nuevo o contacte por correo.']
  }[language] || [];
  let pending = false;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (pending) return;
    pending = true;
    button.disabled = true;
    form.setAttribute('aria-busy', 'true');
    status.textContent = copy[0];
    try {
      const data = new FormData(form);
      const topic = form.elements.process.selectedOptions[0]?.textContent;
      if (topic) data.set('process', topic);
      const response = await fetch(form.action, {
        method: 'POST',
        headers: { Accept: 'application/json' },
        body: data,
        signal: AbortSignal.timeout(15000)
      });
      const result = await response.json();
      if (!response.ok || result?.ok !== true) throw new Error('Submission not confirmed');
      form.reset();
      status.textContent = copy[1];
    } catch {
      status.textContent = copy[2];
    } finally {
      form.removeAttribute('aria-busy');
      button.disabled = false;
      pending = false;
    }
  });
})();
