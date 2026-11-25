(function () {
    "use strict";
  
    var STORAGE_KEY = "ds-toc-collapsed";
    var DESKTOP_QUERY = "(min-width: 76.25em)";
    var TOOLTIP_DURATION_MS = 3000;
    var LABEL_COLLAPSE = "Inhaltsverzeichnis ausblenden";
    var LABEL_EXPAND = "Inhaltsverzeichnis einblenden";
    var TOOLTIP_PREFIX = "Hier können Sie das ";
    var TOP_GAP = 12;

    // bindTooltipInteractions() attaches listeners, so it must run exactly
    // once even though init() re-runs on every instant navigation.
    var tooltipControlCache = null;
  
    function isTocCollapsed() {
      return document.documentElement.hasAttribute("data-ds-toc-collapsed");
    }
  
    function setTocCollapsed(enabled) {
      if (enabled) {
        document.documentElement.setAttribute("data-ds-toc-collapsed", "");
        try {
          localStorage.setItem(STORAGE_KEY, "true");
        } catch (e) {}
      } else {
        document.documentElement.removeAttribute("data-ds-toc-collapsed");
        try {
          localStorage.removeItem(STORAGE_KEY);
        } catch (e) {}
      }
    }
  
    function tocIsUnavailable() {
      var secondary = document.querySelector(".md-sidebar--secondary");
      if (!secondary || secondary.hasAttribute("hidden")) {
        return true;
      }
      // Material hides the secondary sidebar on small screens (display: none),
      // where the ToC is folded into the navigation drawer instead. offsetParent
      // is null when the element (or an ancestor) is display:none, so this covers
      // the responsive case without hardcoding a breakpoint. A collapsed sidebar
      // uses visibility:hidden (not display:none), so it still keeps a layout box
      // and the button stays available to expand it again.
      if (secondary.offsetParent === null) {
        return true;
      }
      // Material renders the secondary sidebar even for pages without headings,
      // leaving an empty ToC. Treat an empty ToC as hidden so the toggle button
      // is only shown when there is an actual table of contents to collapse.
      return !secondary.querySelector(".md-nav--secondary .md-nav__item");
    }
  
    function updateButtonState(button, tooltip) {
      var collapsed = isTocCollapsed();
      var collapseIcon = button.querySelector(".ds-toc-toggle__icon--collapse");
      var expandIcon = button.querySelector(".ds-toc-toggle__icon--expand");
      var label = collapsed ? LABEL_EXPAND : LABEL_COLLAPSE;

      button.setAttribute("aria-pressed", collapsed ? "true" : "false");
      button.setAttribute("aria-label", label);

      if (tooltip) {
        // The button carries its own tooltip element. A `title` on top of it
        // makes the browser render its native tooltip alongside, so the label
        // shows up twice. aria-label plus aria-describedby keep assistive
        // technology covered without it.
        button.removeAttribute("title");
        tooltip.textContent = TOOLTIP_PREFIX + label;
      } else {
        button.setAttribute("title", label);
      }

      if (collapseIcon) {
        collapseIcon.hidden = collapsed;
      }
      if (expandIcon) {
        expandIcon.hidden = !collapsed;
      }
    }
  
    function shouldKeepTooltipVisible(button, isHovered) {
      return document.activeElement === button || isHovered;
    }
  
    function showTooltip(tooltip) {
      if (!tooltip) {
        return;
      }
      tooltip.classList.add("ds-toc-toggle__tooltip--visible");
    }
  
    function hideTooltip(tooltip, button, isHovered, force) {
      if (!tooltip || !tooltip.classList.contains("ds-toc-toggle__tooltip--visible")) {
        return;
      }
      if (!force && button && shouldKeepTooltipVisible(button, isHovered)) {
        return;
      }
      tooltip.classList.remove("ds-toc-toggle__tooltip--visible");
    }
  
    function bindTooltipInteractions(button, tooltip) {
      var isHovered = false;
      var autoHideTimer = null;
  
      function clearAutoHideTimer() {
        if (autoHideTimer !== null) {
          window.clearTimeout(autoHideTimer);
          autoHideTimer = null;
        }
      }
  
      function hideIfUnpinned(force) {
        hideTooltip(tooltip, button, isHovered, force);
      }
  
      function scheduleAutoHide() {
        clearAutoHideTimer();
        autoHideTimer = window.setTimeout(function () {
          hideIfUnpinned(false);
        }, TOOLTIP_DURATION_MS);
      }
  
      button.addEventListener("focus", function () {
        clearAutoHideTimer();
        showTooltip(tooltip);
      });
  
      button.addEventListener("blur", function () {
        hideIfUnpinned(false);
      });
  
      button.addEventListener("mouseenter", function () {
        isHovered = true;
        clearAutoHideTimer();
        showTooltip(tooltip);
      });
  
      button.addEventListener("mouseleave", function () {
        isHovered = false;
        hideIfUnpinned(false);
      });
  
      return {
        scheduleAutoHide: scheduleAutoHide,
        clearAutoHideTimer: clearAutoHideTimer,
        hideIfUnpinned: hideIfUnpinned,
      };
    }
  
    function updateWrapperTop(wrapper) {
      // The CSS parks the wrapper at a fixed `top: 6rem`, which only clears a
      // single-row header. With navigation.tabs.sticky there is a second row
      // and the icon lands on top of it. Derive the offset from whatever
      // chrome is actually rendered instead. Read at the current scroll
      // position only — sticky tabs slide away while scrolling, and following
      // them would make the button jitter, so it stays parked below their
      // full height.
      var chrome = [
        document.querySelector(".md-header"),
        document.querySelector(".md-tabs"),
      ];
      var bottom = 0;
      for (var i = 0; i < chrome.length; i++) {
        var el = chrome[i];
        if (el && el.offsetParent !== null) {
          bottom = Math.max(bottom, el.getBoundingClientRect().bottom);
        }
      }
      if (bottom > 0) {
        wrapper.style.top = Math.round(bottom + TOP_GAP) + "px";
      }
    }

    function updateWrapperPosition(wrapper) {
      if (!wrapper) {
        return;
      }

      updateWrapperTop(wrapper);

      // Sit just outside the relevant right boundary — the secondary
      // sidebar while it's still showing (touching the ToC's own right
      // edge, not the divider — sitting on the divider used to overlap
      // both the "edit this page" icon in content and the ToC's own nav
      // links on short pages), or .md-main__inner (aligned with the header
      // grid) once it's collapsed. Never inside either box.
      var collapsed = isTocCollapsed();
      var anchor = document.querySelector(collapsed ? ".md-main__inner" : ".md-sidebar--secondary");
      if (!anchor) {
        wrapper.style.removeProperty("right");
        return;
      }

      var width = wrapper.getBoundingClientRect().width;
      // Extra 20px breathing room from the grid edge when parked there in
      // the collapsed state; a smaller 8px gap otherwise so the button
      // doesn't sit flush against the sidebar's scrollbar. Never closer
      // than 20px to the real viewport edge either, or the wrapper ends up
      // pinned to it on viewports with little margin.
      var gap = collapsed ? 20 : 18;
      // position:fixed's `right` is relative to the document's clientWidth
      // (viewport minus scrollbar), not window.innerWidth (which includes
      // it) — using innerWidth here pushed the button left by the
      // scrollbar's own width, into the sidebar.
      var viewportWidth = document.documentElement.clientWidth;
      var right = Math.max(20, viewportWidth - anchor.getBoundingClientRect().right - width - gap);
      wrapper.style.right = right + "px";
    }

    function scheduleWrapperPositionUpdate(wrapper) {
      window.requestAnimationFrame(function () {
        updateWrapperPosition(wrapper);
      });
    }

    function updateButtonVisibility(button, tooltip, tooltipControl) {
      var wasVisible = !button.hidden;
      var shouldShow = !tocIsUnavailable();
      button.hidden = !shouldShow;
  
      if (!shouldShow) {
        if (wasVisible) {
          tooltipControl.clearAutoHideTimer();
          tooltipControl.hideIfUnpinned(true);
        }
        if (isTocCollapsed()) {
          setTocCollapsed(false);
          updateButtonState(button, tooltip);
        }
      }
    }

    function init() {
      var button = document.querySelector("[data-md-component='toc-collapse-toggle']");
      var tooltip = document.querySelector("[data-md-component='toc-collapse-tooltip']");
      var wrapper = document.querySelector(".ds-toc-toggle-wrapper");
      if (!button) {
        return;
      }

      if (!tooltipControlCache) {
        tooltipControlCache = bindTooltipInteractions(button, tooltip);
      }
      var tooltipControl = tooltipControlCache;
      var desktopMedia = window.matchMedia(DESKTOP_QUERY);

      try {
        if (localStorage.getItem(STORAGE_KEY) === "true") {
          setTocCollapsed(true);
        }
      } catch (e) {}

      updateButtonState(button, tooltip);
      updateButtonVisibility(button, tooltip, tooltipControl);
      updateWrapperPosition(wrapper);

      // Everything above re-runs per navigation; everything below wires
      // listeners and must not. Material's instant navigation keeps these
      // nodes alive, so a second pass would double-bind the click handler
      // and every click would toggle twice.
      if (button.dataset.dsWired) {
        return;
      }
      button.dataset.dsWired = "1";

      button.addEventListener("click", function () {
        setTocCollapsed(!isTocCollapsed());
        updateButtonState(button, tooltip);
        updateWrapperPosition(wrapper);
        tooltipControl.clearAutoHideTimer();
        tooltipControl.hideIfUnpinned(true);
        // A mouse click also focuses the button, and the focus handler
        // below shows the tooltip again with no auto-hide — blur so the
        // click's force-hide actually sticks.
        button.blur();
        document.dispatchEvent(new CustomEvent("ds-toc-collapse-change"));
      });

      desktopMedia.addEventListener("change", function () {
        updateButtonVisibility(button, tooltip, tooltipControl);
        updateButtonState(button, tooltip);
        updateWrapperPosition(wrapper);
      });

      window.addEventListener("resize", function () {
        updateButtonVisibility(button, tooltip, tooltipControl);
        updateWrapperPosition(wrapper);
      });

      document.addEventListener("ds-content-wide-change", function () {
        scheduleWrapperPositionUpdate(wrapper);
      });

      if (typeof ResizeObserver !== "undefined") {
        var resizeObserver = new ResizeObserver(function () {
          scheduleWrapperPositionUpdate(wrapper);
        });
        var content = document.querySelector(".md-content");
        if (content) {
          resizeObserver.observe(content);
        }
      }
    }
  
    // With navigation.instant, DOMContentLoaded fires once for the whole
    // session, so the button keeps whatever state the previous page left it
    // in. Material republishes document$ on every navigation.
    if (window.document$ && typeof window.document$.subscribe === "function") {
      window.document$.subscribe(init);
    } else if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  })();