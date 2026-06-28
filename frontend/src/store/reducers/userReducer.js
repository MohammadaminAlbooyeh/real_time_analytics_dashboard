import { SET_USER, CLEAR_USER } from '../actions/userActions';

const initialState = {
  current: null,
  isAuthenticated: false,
};

export function userReducer(state = initialState, action) {
  switch (action.type) {
    case SET_USER:
      return { ...state, current: action.payload, isAuthenticated: true };
    case CLEAR_USER:
      return { ...state, current: null, isAuthenticated: false };
    default:
      return state;
  }
}
