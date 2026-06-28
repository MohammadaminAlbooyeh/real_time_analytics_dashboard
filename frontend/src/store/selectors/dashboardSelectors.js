export const selectDashboards = (state) => state.dashboard.list;
export const selectCurrentDashboard = (state) => state.dashboard.current;
export const selectAlertEvents = (state) => state.alerts.events;
export const selectCurrentUser = (state) => state.user.current;
export const selectIsAuthenticated = (state) => state.user.isAuthenticated;
