export const SET_DASHBOARDS = 'SET_DASHBOARDS';
export const SET_CURRENT_DASHBOARD = 'SET_CURRENT_DASHBOARD';
export const ADD_DASHBOARD_ITEM = 'ADD_DASHBOARD_ITEM';
export const REMOVE_DASHBOARD_ITEM = 'REMOVE_DASHBOARD_ITEM';

export const setDashboards = (dashboards) => ({
  type: SET_DASHBOARDS,
  payload: dashboards,
});

export const setCurrentDashboard = (dashboard) => ({
  type: SET_CURRENT_DASHBOARD,
  payload: dashboard,
});

export const addDashboardItem = (item) => ({
  type: ADD_DASHBOARD_ITEM,
  payload: item,
});

export const removeDashboardItem = (itemId) => ({
  type: REMOVE_DASHBOARD_ITEM,
  payload: itemId,
});
