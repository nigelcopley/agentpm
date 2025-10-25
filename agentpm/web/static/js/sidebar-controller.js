(function() {
  const factory = function() {
    return {
      activeFilters: {
        status: null,
        type: null,
        priority: null,
        phase: null,
        document_type: null,
        tags: [],
      },
      initState: null,
      initialize(state) {
        this.initState = state;
        this.syncFromGlobal();
      },
      syncFromGlobal(filters) {
        const globalFilters = filters || (window.AIPM?.filters?.activeFilters) || {};
        this.activeFilters = {
          status: globalFilters.status ?? null,
          type: globalFilters.type ?? null,
          priority: globalFilters.priority ?? null,
          phase: globalFilters.phase ?? null,
          document_type: globalFilters.document_type ?? null,
          tags: globalFilters.tags ? [...globalFilters.tags] : [],
        };
      },
      buttonClasses(group, filter) {
        const current = this.activeFilters[group];
        const isStatusAll = group === 'status' && filter === 'all';
        const isActive = group === 'status'
          ? (current ? current === filter : isStatusAll)
          : (Array.isArray(current) ? current.includes(filter) : current === filter);
        return [
          'flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition',
          isActive
            ? 'bg-primary text-white shadow-brand'
            : 'text-gray-600 hover:bg-primary/10 hover:text-primary',
        ].join(' ');
      },
      setFilter(group, filter, event) {
        if (event) {
          event.preventDefault();
          event.stopPropagation();
          event.stopImmediatePropagation();
        }

        const filtersApi = window.AIPM?.filters;
        if (!(filtersApi && typeof filtersApi.toggleFilter === 'function')) {
          window.showToast?.(`Filter applied: ${filter}`, 'info');
          return;
        }

        const button = event?.currentTarget || document.querySelector(`.filter-btn[data-filter-group="${group}"][data-filter="${filter}"]`);
        filtersApi.toggleFilter(group, filter, button || null);
        this.syncFromGlobal(filtersApi.activeFilters);
      },
      toggleTag(tag) {
        const filtersApi = window.AIPM?.filters;
        if (!(filtersApi && typeof filtersApi.toggleFilter === 'function')) {
          window.showToast?.(`Filter applied: #${tag}`, 'info');
          return;
        }
        filtersApi.toggleFilter('tags', tag, null);
        this.syncFromGlobal(filtersApi.activeFilters);
      },
      createWorkItem() {
        window.location.assign('/work-item/create');
      },
      createTask() {
        window.location.assign('/task/create');
      },
      createProject() {
        window.location.assign('/project/create');
      },
      createIdea() {
        window.location.assign('/ideas/new');
      },
      refreshDocs() {
        window.location.reload();
      },
    };
  };

  const registerWithAlpine = () => {
    if (window.Alpine && typeof window.Alpine.data === 'function') {
      window.Alpine.data('sidebarController', factory);
    }
  };

  window.sidebarController = factory;

  if (document.readyState === 'loading') {
    document.addEventListener('alpine:init', registerWithAlpine, { once: true });
  } else if (window.Alpine) {
    registerWithAlpine();
  } else {
    document.addEventListener('alpine:init', registerWithAlpine, { once: true });
  }
})();
