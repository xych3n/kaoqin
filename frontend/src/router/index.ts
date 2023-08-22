import { route } from 'quasar/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';

import { api } from 'boot/axios';
import { User } from 'src/pages/schemas';
import routes from './routes';

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route((/* { store, ssrContext } */) => {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory);

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  Router.beforeEach(async (to, from, next) => {
    const token = localStorage.getItem('access-token');
    if (!token) {
      if (to.path !== '/login') return next('/login');
      return next();
    }
    try {
      const { data } = await api.post<User>('/login/test-token');
      localStorage.setItem('student_number', data.student_number);
      localStorage.setItem('name', data.name);
      localStorage.setItem('is_superuser', data.is_superuser ? 'Y' : 'N');
    } catch (error) {
      localStorage.removeItem('access-token');
      return next('/login');
    }
    if (to.path === '/login') return next('/');
    return next();
  });

  return Router;
});
