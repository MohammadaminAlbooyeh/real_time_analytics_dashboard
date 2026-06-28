import {
  SET_ALERTS,
  ADD_ALERT_EVENT,
  UPDATE_ALERT_STATUS,
} from '../actions/alertActions';

const initialState = {
  events: [],
};

export function alertReducer(state = initialState, action) {
  switch (action.type) {
    case SET_ALERTS:
      return { ...state, events: action.payload };
    case ADD_ALERT_EVENT:
      return { ...state, events: [action.payload, ...state.events].slice(0, 100) };
    case UPDATE_ALERT_STATUS:
      return {
        ...state,
        events: state.events.map((e) =>
          e.id === action.payload.eventId
            ? { ...e, status: action.payload.status }
            : e
        ),
      };
    default:
      return state;
  }
}
