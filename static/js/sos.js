// SOS Emergency Alert workflow with confirmation modal and honest notification status

document.addEventListener("DOMContentLoaded", () => {
  const openModalBtn = document.getElementById("openSosConfirmBtn");
  const confirmSendBtn = document.getElementById("confirmSendSosBtn");
  const sosModalEl = document.getElementById("sosConfirmModal");
  const includeLocationCheckbox = document.getElementById("includeLocationCheck");
  const sosMessageInput = document.getElementById("sosMessageInput");
  const sosResultBox = document.getElementById("sosResultBox");
  const sosLocationPreview = document.getElementById("sosLocationPreview");

  if (!openModalBtn || !confirmSendBtn || !sosModalEl) return;

  const sosModal = new bootstrap.Modal(sosModalEl);

  openModalBtn.addEventListener("click", () => {
    if (sosLocationPreview) {
      sosLocationPreview.textContent =
        "Location will only be requested after you confirm sending the SOS alert (if checked below).";
    }
    sosModal.show();
  });

  confirmSendBtn.addEventListener("click", async () => {
    confirmSendBtn.disabled = true;
    confirmSendBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm me-2"></span>Processing SOS...';

    let latitude = null;
    let longitude = null;
    let accuracy = null;
    let locationStatus = "not_shared";

    if (includeLocationCheckbox && includeLocationCheckbox.checked) {
      try {
        if (sosLocationPreview) {
          sosLocationPreview.textContent = "Requesting browser location permission...";
        }
        const coords = await SafetyGeolocation.requestCurrentPosition();
        latitude = coords.latitude;
        longitude = coords.longitude;
        accuracy = coords.accuracy;
        locationStatus = "captured";
      } catch (err) {
        locationStatus = err.code === "DENIED" ? "denied" : "unavailable";
      }
    }

    const selectedContactIds = Array.from(
      document.querySelectorAll('input[name="sos_contact_ids"]:checked')
    ).map((el) => Number(el.value));

    try {
      const response = await fetch("/api/sos", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          latitude,
          longitude,
          accuracy,
          location_status: locationStatus,
          message: sosMessageInput ? sosMessageInput.value.trim() : "",
          contact_ids: selectedContactIds,
        }),
      });

      const data = await response.json();
      sosModal.hide();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Failed to create SOS alert.");
      }

      renderSosResult(data);
    } catch (error) {
      if (sosResultBox) {
        sosResultBox.classList.remove("d-none");
        sosResultBox.innerHTML = `
          <div class="alert alert-danger mb-0">
            <strong>Error:</strong> ${error.message}. If you are in immediate danger, please call <a href="tel:112" class="fw-bold text-danger">112</a> directly.
          </div>`;
      }
    } finally {
      confirmSendBtn.disabled = false;
      confirmSendBtn.innerHTML = '<i class="bi bi-exclamation-triangle-fill me-1"></i> Confirm & Send SOS';
    }
  });

  function renderSosResult(data) {
    if (!sosResultBox) return;
    const alert = data.alert;
    const notifications = data.notifications || [];

    const notifRows =
      notifications.length > 0
        ? notifications
            .map((n) => {
              let badgeClass = "bg-secondary";
              let statusLabel = n.status;
              if (n.status === "sent") {
                badgeClass = "bg-success";
                statusLabel = "Confirmed Sent";
              } else if (n.status === "simulated") {
                badgeClass = "bg-warning text-dark";
                statusLabel = "Simulated (Dev Mode)";
              } else if (n.status === "failed") {
                badgeClass = "bg-danger";
                statusLabel = "Delivery Failed";
              }
              return `
                <li class="list-group-item d-flex justify-content-between align-items-start flex-wrap gap-2">
                  <div>
                    <strong>${escapeHtml(n.contact_name)}</strong>
                    <span class="text-muted small">(${escapeHtml(n.recipient)} • ${escapeHtml(n.channel.toUpperCase())})</span>
                    <div class="small text-muted">${escapeHtml(n.provider_message || "")}</div>
                  </div>
                  <span class="badge ${badgeClass}">${statusLabel}</span>
                </li>`;
            })
            .join("")
        : `<li class="list-group-item text-muted">No trusted contacts were selected. Add contacts to notify them during an SOS.</li>`;

    const locText = alert.map_link
      ? `Lat ${alert.latitude}, Lng ${alert.longitude} — <a href="${alert.map_link}" target="_blank" rel="noopener">View on OpenStreetMap</a>`
      : `Location not captured (${escapeHtml(alert.location_status)})`;

    sosResultBox.classList.remove("d-none");
    sosResultBox.innerHTML = `
      <div class="card card-safety border-danger">
        <div class="card-header bg-danger text-white d-flex justify-content-between align-items-center">
          <span><i class="bi bi-broadcast me-2"></i>SOS Alert #${alert.id} Recorded (${escapeHtml(alert.status.toUpperCase())})</span>
          <a href="tel:112" class="btn btn-light btn-sm fw-bold text-danger"><i class="bi bi-telephone-fill me-1"></i>Call 112</a>
        </div>
        <div class="card-body">
          <p class="mb-2"><strong>Time:</strong> ${escapeHtml(alert.created_at)}</p>
          <p class="mb-3"><strong>Location:</strong> ${locText}</p>
          <h6 class="fw-bold mb-2">Notification Dispatch Status</h6>
          <ul class="list-group list-group-flush mb-3">${notifRows}</ul>
          <a href="/sos/history" class="btn btn-outline-secondary btn-sm">View Full SOS History</a>
        </div>
      </div>`;
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
