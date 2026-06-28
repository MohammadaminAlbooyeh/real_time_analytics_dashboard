export const SET_ALERTS = 'SET_ALERTS';
export const ADD_ALERT_EVENT = 'ADD_ALERT_EVENT';
export const UPDATE_ALERT_STATUS = 'UPDATE_ALERT_STATUS';

export const setAlerts = (events) => ({
  type: SET_ALERTS,
  payload: events,
});

export const addAlertEvent = (event) => ({
  type: ADD_ALERT_EVENT,
  payload: event,
});

export const updateAlertStatus = (eventId, status) => ({
  type: UPDATE_ALERT_STATUS,
  payload: { eventId, status },
});
