// Permission-based Browser Geolocation helper (never collects coordinates automatically)

const SafetyGeolocation = {
  requestCurrentPosition(options = {}) {
    return new Promise((resolve, reject) => {
      if (!("geolocation" in navigator)) {
        reject({
          code: "UNAVAILABLE",
          message: "Geolocation is not supported by your browser.",
        });
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          resolve({
            latitude: Number(pos.coords.latitude.toFixed(6)),
            longitude: Number(pos.coords.longitude.toFixed(6)),
            accuracy: Number((pos.coords.accuracy || 0).toFixed(1)),
            timestamp: new Date(pos.timestamp).toLocaleString(),
          });
        },
        (err) => {
          let message = "Unable to retrieve your location.";
          let code = "UNAVAILABLE";
          if (err.code === err.PERMISSION_DENIED) {
            code = "DENIED";
            message = "Location permission was denied. Enable browser location permission to share GPS coordinates.";
          } else if (err.code === err.POSITION_UNAVAILABLE) {
            message = "Location signal is currently unavailable.";
          } else if (err.code === err.TIMEOUT) {
            message = "Location request timed out. Please try again.";
          }
          reject({ code, message });
        },
        {
          enableHighAccuracy: true,
          timeout: options.timeout || 10000,
          maximumAge: options.maximumAge || 0,
        }
      );
    });
  },

  buildOsmLink(lat, lng) {
    return `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=17/${lat}/${lng}`;
  },
};
