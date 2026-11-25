(function () {
    "use strict";
  
    var STORAGE_KEY = "ds-content-wide";
    var DESKTOP_QUERY = "(min-width: 76.25em)";
    var LABEL_COLLAPSE = "Navigation ausblenden";
    var LABEL_EXPAND = "Navigation einblenden";
  
    function isWideMode() {
      return document.documentElement.hasAttribute("data-ds-content-wide");
    }
  
    function setWideMode(enabled) {
      if (enabled) {
        document.documentElement.setAttribute("data-ds-content-wide", "");
        try {
          localStorage.setItem(STORAGE_KEY, "true");
        } catch (e) {}
      } else {
        document.documentElement.removeAttribute("data-ds-content-wide");
        try {
          localStorage.removeItem(STORAGE_KEY);
        } catch (e) {}
      }
    }
  
    function sidebarIsHidden(sidebar) {
      return !sidebar || sidebar.hasAttribute("hidden");
    }
  
    function hasCollapsibleSidebars() {
      var primary = document.querySelector(".md-sidebar--primary");
      return !sidebarIsHidden(primary);
    }
  
    function updateButtonState(button) {
      var wide = isWideMode();
      var collapseIcon = button.querySelector(".ds-content-width-toggle__icon--collapse");
      var expandIcon = button.querySelector(".ds-content-width-toggle__icon--expand");
  
      button.setAttribute("aria-pressed", wide ? "true" : "false");
      button.setAttribute("aria-label", wide ? LABEL_EXPAND : LABEL_COLLAPSE);
      button.setAttribute("title", wide ? LABEL_EXPAND : LABEL_COLLAPSE);
  
      if (collapseIcon) {
        collapseIcon.hidden = wide;
      }
      if (expandIcon) {
        expandIcon.hidden = !wide;
      }
    }
  
    function updateButtonVisibility(button, desktopMedia) {
      var shouldShow = desktopMedia.matches && hasCollapsibleSidebars();
      button.hidden = !shouldShow;
  
      if (!shouldShow && isWideMode()) {
        setWideMode(false);
        updateButtonState(button);
        document.dispatchEvent(new CustomEvent("ds-content-wide-change"));
      }
    }
  
    function updateButtonPosition(button) {
      if (button.hidden) {
        button.style.removeProperty("left");
        return;
      }

      // Sit just outside the relevant left boundary — the primary sidebar
      // while it's still showing (straddling the divider used to overlap
      // the nav's own links on short pages), or .md-main__inner (aligned
      // with the header grid) once the sidebar is collapsed. Never inside
      // either box, so it never covers real content.
      var wide = isWideMode();
      var anchor = document.querySelector(wide ? ".md-main__inner" : ".md-sidebar--primary");
      if (!anchor) {
        button.style.removeProperty("left");
        return;
      }

      var width = button.getBoundingClientRect().width;
      // Extra 20px breathing room from the grid edge, but only when parked
      // there in wide mode — flush against the sidebar divider otherwise.
      // Never closer than 20px to the real viewport edge either, or the
      // button ends up pinned to it on viewports with little/no margin.
      var gap = wide ? 20 : 0;
      var left = Math.max(20, anchor.getBoundingClientRect().left - width - gap);
      button.style.left = left + "px";
    }
  
    function scheduleButtonPositionUpdate(button) {
      window.requestAnimationFrame(function () {
        updateButtonPosition(button);
      });
    }
  
    function init() {
      var button = document.querySelector("[data-md-component='content-width-toggle']");
      if (!button) {
        return;
      }
  
      var desktopMedia = window.matchMedia(DESKTOP_QUERY);
  
      try {
        if (localStorage.getItem(STORAGE_KEY) === "true") {
          setWideMode(true);
        }
      } catch (e) {}
  
      function refreshButton(button, desktopMedia) {
        updateButtonVisibility(button, desktopMedia);
        updateButtonState(button);
        updateButtonPosition(button);
      }
  
      refreshButton(button, desktopMedia);

      // Everything above re-runs per navigation; everything below wires
      // listeners and must not. Material's instant navigation keeps this node
      // alive, so a second pass would double-bind the click handler.
      if (button.dataset.dsWired) {
        return;
      }
      button.dataset.dsWired = "1";

      button.addEventListener("click", function () {
        setWideMode(!isWideMode());
        refreshButton(button, desktopMedia);
        document.dispatchEvent(new CustomEvent("ds-content-wide-change"));
      });
  
      desktopMedia.addEventListener("change", function () {
        refreshButton(button, desktopMedia);
      });
  
      window.addEventListener("resize", function () {
        refreshButton(button, desktopMedia);
      });
  
      document.addEventListener("ds-toc-collapse-change", function () {
        scheduleButtonPositionUpdate(button);
      });
  
      if (typeof MutationObserver !== "undefined") {
        var layoutObserver = new MutationObserver(function () {
          scheduleButtonPositionUpdate(button);
        });
        layoutObserver.observe(document.documentElement, {
          attributes: true,
          attributeFilter: ["data-ds-toc-collapsed", "data-ds-content-wide"],
        });
      }
  
      if (typeof ResizeObserver !== "undefined") {
        var resizeObserver = new ResizeObserver(function () {
          scheduleButtonPositionUpdate(button);
        });
        var content = document.querySelector(".md-content");
        var mainInner = document.querySelector(".md-main__inner");
        if (content) {
          resizeObserver.observe(content);
        }
        if (mainInner) {
          resizeObserver.observe(mainInner);
        }
      }
    }
  
    // With navigation.instant, DOMContentLoaded fires once for the whole
    // session. Material republishes document$ on every navigation.
    if (window.document$ && typeof window.document$.subscribe === "function") {
      window.document$.subscribe(init);
    } else if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  })();