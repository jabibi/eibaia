const STORAGE_KEY = "elosue:sidebar-collapsed";

export function useSidebar() {
  const collapsed = useState<boolean>("sidebar-collapsed", () => true);
  const mobileOpen = useState<boolean>("sidebar-mobile-open", () => false);

  function persist() {
    if (import.meta.client) {
      localStorage.setItem(STORAGE_KEY, collapsed.value ? "1" : "0");
    }
  }

  function restoreFromStorage() {
    if (import.meta.client) {
      const stored = localStorage.getItem(STORAGE_KEY);
      collapsed.value = stored === null ? true : stored === "1";
    }
  }

  function toggleCollapsed() {
    collapsed.value = !collapsed.value;
    persist();
  }

  function expand() {
    if (collapsed.value) {
      collapsed.value = false;
      persist();
    }
  }

  function collapse() {
    if (!collapsed.value) {
      collapsed.value = true;
      persist();
    }
  }

  function openMobile() {
    mobileOpen.value = true;
  }

  function closeMobile() {
    mobileOpen.value = false;
  }

  /** Header toggle button: closes the mobile drawer if it's open, otherwise
   * behaves as the desktop collapse/expand toggle. */
  function handleHeaderToggle() {
    if (mobileOpen.value) {
      closeMobile();
    } else {
      toggleCollapsed();
    }
  }

  return {
    collapsed,
    mobileOpen,
    restoreFromStorage,
    toggleCollapsed,
    expand,
    collapse,
    openMobile,
    closeMobile,
    handleHeaderToggle,
  };
}
