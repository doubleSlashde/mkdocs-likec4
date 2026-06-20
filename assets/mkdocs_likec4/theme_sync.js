(function () {
  function resolve() {
    var attr = document.body && document.body.getAttribute("data-md-color-scheme");
    if (attr) return attr === "slate" ? "dark" : "light";
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function apply() {
    var scheme = resolve();
    var els = document.querySelectorAll("[data-likec4-auto-scheme]");
    for (var i = 0; i < els.length; i++) {
      if (els[i].getAttribute("color-scheme") !== scheme) {
        els[i].setAttribute("color-scheme", scheme);
      }
    }
  }

  function init() {
    apply();

    new MutationObserver(apply).observe(document.body, {
      attributes: true,
      attributeFilter: ["data-md-color-scheme"],
    });

    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    if (mq.addEventListener) mq.addEventListener("change", apply);
    else if (mq.addListener) mq.addListener(apply);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
