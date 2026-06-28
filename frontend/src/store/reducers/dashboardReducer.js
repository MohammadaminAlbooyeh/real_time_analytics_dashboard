import {
  SET_DASHBOARDS,
  SET_CURRENT_DASHBOARD,
  ADD_DASHBOARD_ITEM,
  REMOVE_DASHBOARD_ITEM,
} from '../actions/dashboardActions';

const initialState = {
  list: [],
  current: null,
};

export function dashboardReducer(state = initialState, action) {
  switch (action.type) {
    case SET_DASHBOARDS:
      return { ...state, list: action.payload };
    case SET_CURRENT_DASHBOARD:
      return { ...state, current: action.payload };
    case ADD_DASHBOARD_ITEM:
      if (!state.current) return state;
      return {
        ...state,
        current: {
          ...state.current,
          items: [...state.current.items, action.payload],
        },
      };
    case REMOVE_DASHBOARD_ITEM:
      if (!state.current) return state;
      return {
        ...state,
        current: {
          ...state.current,
          items: state.current.items.filter((i) => i.id !== action.payload),
        },
      };
    default:
      return state;
  }
}
