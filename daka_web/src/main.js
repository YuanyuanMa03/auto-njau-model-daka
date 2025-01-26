import './assets/main.css'
import 'tdesign-mobile-vue/es/style/index.css';

import { createApp } from 'vue'
import TDesign from 'tdesign-mobile-vue';
import App from './App.vue'

const app = createApp(App)
app.use(TDesign)
app.mount('#app')
