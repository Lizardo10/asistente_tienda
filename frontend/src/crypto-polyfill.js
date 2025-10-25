// Polyfill para crypto en el navegador
if (typeof global === 'undefined') {
  window.global = window;
}

if (typeof process === 'undefined') {
  window.process = { env: {} };
}

// Polyfill para crypto.hash
if (typeof crypto !== 'undefined' && !crypto.hash) {
  crypto.hash = function(algorithm) {
    return {
      update: function(data) {
        this.data = data;
        return this;
      },
      digest: function(encoding) {
        // Implementación simple para desarrollo
        return 'mock-hash-' + Math.random().toString(36).substr(2, 9);
      }
    };
  };
}






