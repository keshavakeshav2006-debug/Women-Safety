// Shared UI helpers for CSRF token reading and clipboard copy

function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute("content") : "";
}

function copyTextToClipboard(text, buttonEl) {
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    if (!buttonEl) return;
    const original = buttonEl.innerHTML;
    buttonEl.innerHTML = '<i class="bi bi-check2"></i> Copied';
    setTimeout(() => {
      buttonEl.innerHTML = original;
    }, 2000);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  // Attach copy listeners
  document.querySelectorAll("[data-copy-target]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetSelector = btn.getAttribute("data-copy-target");
      const targetEl = document.querySelector(targetSelector);
      if (targetEl) {
        const value = targetEl.value !== undefined ? targetEl.value : targetEl.textContent;
        copyTextToClipboard(value.trim(), btn);
      }
    });
  });

  // Auto-dismiss non-error flash alerts after 6 seconds
  document.querySelectorAll(".alert-dismissible.auto-fade").forEach((el) => {
    setTimeout(() => {
      if (window.bootstrap && window.bootstrap.Alert) {
        const bsAlert = window.bootstrap.Alert.getOrCreateInstance(el);
        bsAlert.close();
      }
    }, 6000);
  });
});
