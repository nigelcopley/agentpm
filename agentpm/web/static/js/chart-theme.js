(function (global) {
  const palette = {
    primary: '#667eea',
    purple: '#764ba2',
    sky: '#4facfe',
    green: '#43e97b',
    greenDark: '#2dd36f',
    pink: '#fa709a',
    gold: '#ffc107',
    goldDark: '#d97706',
    teal: '#30cfd0',
    amber: '#fee140',
    magenta: '#f093fb',
    success: '#28a745',
    danger: '#dc3545',
    slate: '#94a3b8',
    navy: '#1a1d29',
    midnight: '#2d3748',
    textLight: '#e2e8f0',
    gray: '#6c757d'
  };

  const statusColorMap = {
    proposed: palette.primary,
    validated: palette.purple,
    accepted: palette.sky,
    in_progress: palette.green,
    review: palette.pink,
    completed: palette.success,
    blocked: palette.gold,
    cancelled: palette.danger,
    archived: palette.gray
  };

  const taskTypeColorMap = {
    implementation: palette.primary,
    testing: palette.green,
    design: palette.purple,
    documentation: palette.sky,
    bugfix: palette.danger,
    refactoring: palette.pink,
    deployment: palette.amber,
    review: palette.teal,
    analysis: palette.magenta,
    simple: palette.slate
  };

  const entityColors = [
    palette.primary,
    palette.purple,
    palette.green,
    palette.pink,
    palette.gold,
    palette.sky
  ];

  function withAlpha(color, alpha) {
    const sanitized = (color || '').replace('#', '');
    if (sanitized.length !== 6) {
      return color;
    }
    const bigint = parseInt(sanitized, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  function getStatusColors(labels) {
    return (labels || []).map((label) => statusColorMap[label] || palette.gray);
  }

  function getTaskTypeColors(labels) {
    return (labels || []).map((label) => {
      const key = (label || '').toString().toLowerCase();
      return taskTypeColorMap[key] || palette.gray;
    });
  }

  function getComplianceColor(rate) {
    if (rate >= 90) {
      return palette.success;
    }
    if (rate >= 70) {
      return palette.gold;
    }
    return palette.danger;
  }

  function getTimelineSeriesConfig() {
    return {
      borderColor: palette.green,
      backgroundColor: withAlpha(palette.green, 0.1),
      pointBackgroundColor: palette.green,
      pointBorderColor: palette.navy
    };
  }

  global.AIPM_CHART_THEME = {
    palette,
    statusColorMap,
    taskTypeColorMap,
    entityColors,
    getStatusColors,
    getTaskTypeColors,
    getComplianceColor,
    getTimelineSeriesConfig,
    withAlpha
  };
}(window));
