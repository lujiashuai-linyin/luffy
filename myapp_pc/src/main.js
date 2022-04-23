// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import settings from './settings';

Vue.config.productionTip = false;
Vue.prototype.$settings = settings;

// element-ui配置
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
// 调用插件
Vue.use(ElementUI);

// 导入css初始化样式
import "../static/css/reset.css";

import axios from "axios"
axios.defaults.withCredentials = false; // false表示阻止ajax附带cookie
Vue.prototype.$axios = axios; // 把对象挂载vue中


/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
