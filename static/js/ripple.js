/* Ripple UI behaviour: password reveal + auth tagline carousel. */
(function () {
  "use strict";

  // Show / hide password. Works for any button with [data-toggle-password].
  document.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-toggle-password]");
    if (!btn) return;
    var input = btn.closest(".input-wrap").querySelector("input");
    var show = input.type === "password";
    input.type = show ? "text" : "password";
    btn.setAttribute("aria-pressed", String(show));
    btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
  });

  // Tagline carousel on the login / register art panel.
  var root = document.querySelector("[data-slider]");
  if (!root) return;
  var slides = root.querySelectorAll(".slide");
  var dots = root.querySelectorAll(".dot");
  var index = 0;
  var timer = null;

  function show(i) {
    index = (i + slides.length) % slides.length;
    slides.forEach(function (s, n) { s.classList.toggle("is-active", n === index); });
    dots.forEach(function (d, n) {
      d.classList.toggle("is-active", n === index);
      d.setAttribute("aria-current", n === index ? "true" : "false");
    });
  }
  function start() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    stop();
    timer = setInterval(function () { show(index + 1); }, 5000);
  }
  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  dots.forEach(function (d, n) {
    d.addEventListener("click", function () { show(n); start(); });
  });
  show(0);
  start();
})();
