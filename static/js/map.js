// Interactive Leaflet.js + OpenStreetMap scripts for Live Location Sharing and Nearby Services

document.addEventListener("DOMContentLoaded", () => {
  initLocationSharingPage();
  initNearbyServicesPage();
});

function initLocationSharingPage() {
  const mapEl = document.getElementById("locationShareMap");
  if (!mapEl || typeof L === "undefined") return;

  const startBtn = document.getElementById("startSharingBtn");
  const stopBtn = document.getElementById("stopSharingBtn");
  const statusBadge = document.getElementById("sharingStatusBadge");
  const latEl = document.getElementById("shareLat");
  const lngEl = document.getElementById("shareLng");
  const accEl = document.getElementById("shareAccuracy");
  const linkInput = document.getElementById("shareMapLink");
  const openOsmLink = document.getElementById("openOsmLink");
  const whatsappShareLink = document.getElementById("whatsappShareLink");
  const feedbackEl = document.getElementById("locationFeedback");

  const map = L.map("locationShareMap").setView([20.5937, 78.9629], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  let userMarker = null;
  let accuracyCircle = null;
  let watchId = null;

  function updateCoordinates(pos) {
    const lat = Number(pos.coords.latitude.toFixed(6));
    const lng = Number(pos.coords.longitude.toFixed(6));
    const accuracy = Number((pos.coords.accuracy || 0).toFixed(1));
    const osmUrl = SafetyGeolocation.buildOsmLink(lat, lng);

    if (latEl) latEl.textContent = lat;
    if (lngEl) lngEl.textContent = lng;
    if (accEl) accEl.textContent = `${accuracy} m`;
    if (linkInput) linkInput.value = osmUrl;
    if (openOsmLink) {
      openOsmLink.href = osmUrl;
      openOsmLink.classList.remove("disabled");
    }
    if (whatsappShareLink) {
      const msg = encodeURIComponent(`Here is my live location for safety: ${osmUrl}`);
      whatsappShareLink.href = `https://wa.me/?text=${msg}`;
      whatsappShareLink.classList.remove("disabled");
    }

    if (userMarker) {
      userMarker.setLatLng([lat, lng]);
    } else {
      userMarker = L.marker([lat, lng]).addTo(map).bindPopup("<strong>Your Current Location</strong>").openPopup();
    }

    if (accuracyCircle) {
      accuracyCircle.setLatLng([lat, lng]).setRadius(accuracy);
    } else {
      accuracyCircle = L.circle([lat, lng], {
        radius: accuracy,
        color: "#4a154b",
        fillColor: "#9333ea",
        fillOpacity: 0.15,
      }).addTo(map);
    }

    map.setView([lat, lng], 16);
  }

  function showFeedback(message, type = "info") {
    if (!feedbackEl) return;
    feedbackEl.className = `alert alert-${type} mt-3 mb-0`;
    feedbackEl.textContent = message;
    feedbackEl.classList.remove("d-none");
  }

  startBtn?.addEventListener("click", () => {
    if (!("geolocation" in navigator)) {
      showFeedback("Geolocation is not supported by your browser.", "danger");
      return;
    }

    showFeedback("Requesting location permission from your browser...", "info");
    startBtn.disabled = true;

    watchId = navigator.geolocation.watchPosition(
      (pos) => {
        updateCoordinates(pos);
        if (statusBadge) {
          statusBadge.className = "badge bg-success";
          statusBadge.textContent = "Sharing Active";
        }
        if (stopBtn) stopBtn.disabled = false;
        showFeedback("Live location sharing is active. You can stop sharing anytime.", "success");
      },
      (err) => {
        startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
        if (statusBadge) {
          statusBadge.className = "badge bg-secondary";
          statusBadge.textContent = "Inactive";
        }
        const msg =
          err.code === err.PERMISSION_DENIED
            ? "Location permission was denied. No coordinates were collected."
            : "Unable to read your current location. Please check device GPS settings.";
        showFeedback(msg, "warning");
      },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
    );
  });

  stopBtn?.addEventListener("click", () => {
    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId);
      watchId = null;
    }
    if (userMarker) {
      map.removeLayer(userMarker);
      userMarker = null;
    }
    if (accuracyCircle) {
      map.removeLayer(accuracyCircle);
      accuracyCircle = null;
    }
    if (latEl) latEl.textContent = "—";
    if (lngEl) lngEl.textContent = "—";
    if (accEl) accEl.textContent = "—";
    if (linkInput) linkInput.value = "";
    if (openOsmLink) openOsmLink.classList.add("disabled");
    if (whatsappShareLink) whatsappShareLink.classList.add("disabled");
    if (statusBadge) {
      statusBadge.className = "badge bg-secondary";
      statusBadge.textContent = "Stopped";
    }
    startBtn.disabled = false;
    stopBtn.disabled = true;
    map.setView([20.5937, 78.9629], 5);
    showFeedback("Location sharing stopped. Coordinates cleared from map.", "info");
  });
}

function initNearbyServicesPage() {
  const mapEl = document.getElementById("servicesMap");
  if (!mapEl || typeof L === "undefined") return;

  const typeSelect = document.getElementById("serviceTypeFilter");
  const citySelect = document.getElementById("serviceCityFilter");
  const useMyLocationBtn = document.getElementById("useMyLocationServicesBtn");
  const listContainer = document.getElementById("servicesListContainer");
  const servicesStatus = document.getElementById("servicesLocationStatus");

  const map = L.map("servicesMap").setView([22.5, 78.9], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  const markersLayer = L.layerGroup().addTo(map);
  let userLat = null;
  let userLng = null;

  const policeIcon = L.divIcon({
    className: "custom-pin",
    html: '<div style="background:#1d4ed8;color:#fff;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);font-weight:bold;">P</div>',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });

  const hospitalIcon = L.divIcon({
    className: "custom-pin",
    html: '<div style="background:#dc2626;color:#fff;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);font-weight:bold;">H</div>',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });

  async function loadServices() {
    const params = new URLSearchParams();
    if (typeSelect?.value) params.set("type", typeSelect.value);
    if (citySelect?.value) params.set("city", citySelect.value);
    if (userLat !== null && userLng !== null) {
      params.set("lat", userLat);
      params.set("lng", userLng);
    }

    const resp = await fetch(`/api/services?${params.toString()}`);
    const data = await resp.json();
    const services = data.services || [];

    markersLayer.clearLayers();
    const bounds = [];

    if (userLat !== null && userLng !== null) {
      L.marker([userLat, userLng])
        .addTo(markersLayer)
        .bindPopup("<strong>Your Location</strong>");
      bounds.push([userLat, userLng]);
    }

    if (listContainer) {
      if (services.length === 0) {
        listContainer.innerHTML =
          '<div class="col-12"><div class="alert alert-light border">No emergency services match your filters.</div></div>';
      } else {
        listContainer.innerHTML = services
          .map((svc) => {
            const isPolice = svc.service_type === "police";
            const badge = isPolice
              ? '<span class="badge bg-primary">Police Station</span>'
              : '<span class="badge bg-danger">Hospital</span>';
            const dist =
              svc.distance_km !== null
                ? `<span class="badge bg-light text-dark border ms-1">${svc.distance_km} km away</span>`
                : "";
            return `
              <div class="col-md-6">
                <div class="card card-safety h-100">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <div>${badge}${dist}</div>
                      <span class="small text-muted">${svc.city}</span>
                    </div>
                    <h6 class="fw-bold mb-1">${svc.name}</h6>
                    <p class="small text-muted mb-2">${svc.address}</p>
                    <div class="d-flex justify-content-between align-items-center">
                      <a href="tel:${svc.phone}" class="btn btn-sm btn-outline-danger"><i class="bi bi-telephone me-1"></i>${svc.phone}</a>
                      <a href="https://www.openstreetmap.org/?mlat=${svc.latitude}&mlon=${svc.longitude}#map=16/${svc.latitude}/${svc.longitude}" target="_blank" rel="noopener" class="btn btn-sm btn-outline-secondary">Open Map</a>
                    </div>
                  </div>
                </div>
              </div>`;
          })
          .join("");
      }
    }

    services.forEach((svc) => {
      const icon = svc.service_type === "police" ? policeIcon : hospitalIcon;
      const distText = svc.distance_km !== null ? `<br><strong>Distance:</strong> ${svc.distance_km} km` : "";
      L.marker([svc.latitude, svc.longitude], { icon })
        .addTo(markersLayer)
        .bindPopup(
          `<strong>${svc.name}</strong><br>${svc.address}<br><strong>Phone:</strong> <a href="tel:${svc.phone}">${svc.phone}</a>${distText}`
        );
      bounds.push([svc.latitude, svc.longitude]);
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [30, 30], maxZoom: 13 });
    }
  }

  typeSelect?.addEventListener("change", loadServices);
  citySelect?.addEventListener("change", loadServices);

  useMyLocationBtn?.addEventListener("click", async () => {
    useMyLocationBtn.disabled = true;
    try {
      const coords = await SafetyGeolocation.requestCurrentPosition();
      userLat = coords.latitude;
      userLng = coords.longitude;
      if (servicesStatus) {
        servicesStatus.textContent = `Sorted by distance from (${userLat}, ${userLng})`;
      }
      await loadServices();
    } catch (err) {
      if (servicesStatus) {
        servicesStatus.textContent = err.message;
      }
    } finally {
      useMyLocationBtn.disabled = false;
    }
  });

  loadServices();
}
