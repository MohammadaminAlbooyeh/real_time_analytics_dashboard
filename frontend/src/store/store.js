import { createStore, combineReducers, applyMiddleware } from 'redux';
import { dashboardReducer } from './reducers/dashboardReducer';
import { alertReducer } from './reducers/alertReducer';
import { userReducer } from './reducers/userReducer';

const rootReducer = combineReducers({
  dashboard: dashboardReducer,
  alerts: alertReducer,
  user: userReducer,
});

const loggerMiddleware = (store) => (next) => (action) => {
  if (process.env.NODE_ENV === 'development') {
    console.log('dispatching', action.type);
  }
  return next(action);
};

export const store = createStore(
  rootReducer,
  applyMiddleware(loggerMiddleware)
);
