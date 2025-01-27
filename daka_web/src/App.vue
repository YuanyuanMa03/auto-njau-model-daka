<script setup>
import { ref } from 'vue';
import { Toast } from 'tdesign-mobile-vue';
import axios from 'axios';
import { h } from 'vue';
import { IconFont } from 'tdesign-icons-vue-next';
import { CloseIcon, CheckIcon } from 'tdesign-icons-vue-next';

const icons = [h(CheckIcon, { size: '20px' }), h(CloseIcon, { size: '20px' })];

const overlay_visible = ref(false); // 控制遮罩层显示状态
const token = ref('');
const auto_login = ref(false);
const has_verified = ref(false)
const has_tested = ref(false)
const account_info = ref({})
const today_status = ref({})
const daka_config = ref({})
const errorMessage = ref(''); // 错误提示信息

// 卡片折叠状态控制
const isCollapsed1 = ref(true);
const isCollapsed2 = ref(true);
isCollapsed1.value = localStorage.getItem('isCollapsed1') === 'true' ? true : false;
isCollapsed2.value = localStorage.getItem('isCollapsed2') === 'true' ? true : false;


const verify_input = () => {
  if (token.value.length === 36) {
    has_verified.value = true;
    errorMessage.value = '';
  } else {
    has_verified.value = false;
    errorMessage.value = 'Token 长度应为 36 位，请检查后重新输入';
  }
};

const test_token = () => {
  if (token.value.length === 36) {
    // 使用axios将token.value发送到后端进行验证
    axios.post('/api/test_token', { token: token.value })
      .then(response => {
        if (response.data.message === 'success') {
          has_tested.value = true;
          account_info.value = response.data;
          // 将token保存到本地存储
          localStorage.setItem('token', token.value);
          localStorage.setItem('token_time', new Date().getTime());
          overlay_visible.value = false;
          Toast({
            duration: 3000,
            theme: 'success',
            direction: 'column',
            message: '登录成功',
          });
          get_today_status();
        } else {
          Toast(response.data.message);
        }
      })
      .catch(error => {
        console.error(error);
        Toast('网络异常，请稍后再试');
      })
      .finally(() => {
        overlay_visible.value = false;
      });
  } else {
    overlay_visible.value = false;
    Toast('Token长度为36位 请检查后重新输入');
  }
}

const get_today_status = async () => {
  try {
    const response = await axios.post('/api/get_today_status', { token: token.value });
    if (response.data) {
      today_status.value = response.data;
      get_daka_config();
      return true;
    } else {
      Toast(response.data.message);
      return false;
    }
  } catch (error) {
    Toast('网络异常，请稍后再试');
    return false;
  }
}

const daka = async () => {
  try {
    const response = await axios.post('/api/daka', { token: token.value });
    if (response.data.message === 'success') {
      const statusResponse = await axios.post('/api/get_today_status', { token: token.value });
      if (statusResponse.data) {
        today_status.value = statusResponse.data;
        Toast({
          duration: 3000,
          theme: 'success',
          direction: 'column',
          message: '打卡成功',
        });
      } else {
        Toast(statusResponse.data.message);
      }

    } else {
      Toast(response.data.message);
    }
  } catch (error) {
    Toast('网络异常，请稍后再试');
  }
}


const refresh_today_status = async () => {
  const success = await get_today_status();  // 使用 await 等待异步函数完成
  if (success) {
    Toast('刷新成功');
  }
}
const get_daka_config = async () => {
  axios.get('/api/get_daka_config')
    .then(response => {
      if (response.data) {
        daka_config.value = response.data;
      } else {
        Toast(response.data.message);
      }
    })
    .catch(error => {
      Toast('网络异常，请稍后再试');
    });
}

const toggleCard = (index) => {
  if (index === 1) {
    isCollapsed1.value = !isCollapsed1.value;
    localStorage.setItem('isCollapsed1', isCollapsed1.value);
  } else if (index === 2) {
    isCollapsed2.value = !isCollapsed2.value;
    localStorage.setItem('isCollapsed2', isCollapsed2.value);
  }
}

const save_auto_login = () => {
  localStorage.setItem('auto_login', auto_login.value);
}

if (localStorage.getItem('auto_login')) {
  auto_login.value = localStorage.getItem('auto_login') === 'true' ? true : false;
}

if (localStorage.getItem('token')) {
  token.value = localStorage.getItem('token');
  has_verified.value = true;
  if (localStorage.getItem('auto_login') == "true") {
    overlay_visible.value = true;
    test_token();
  }
}

</script>

<template>
  <t-overlay :visible="overlay_visible" />
  <div v-if="!has_tested">
    <h1 style="text-align: center;">远程打卡小工具</h1>
    <t-divider />
  </div>

  <!-- token未提交测试 -->
  <div v-if="!has_tested">
    <p style="font-size: larger;font-weight: bold;text-align: center;margin: 20px auto 20px;">获取"海康物联"Token操作步骤</p>
    <p style="font-size: large;">1. 在电脑浏览器中打开"海康物联"工作台:<br><a href="https://www.hikiot.com/tenant/workBench"
        target="_blank">https://www.hikiot.com/tenant/workBench</a></p>
    <p style="font-size: large;">2. 使用短信验证码登录账号，请确保手机号和微信小程序中的一致</p>
    <p style="font-size: large;">3. 登录成功后，按“F12”打开开发者工具(或右击页面，点击“检查”)</p>
    <p style="font-size: large;">4. 按照下图引导，复制“www_token”的值到下面的文本框中</p>
    <img src="./assets/instruction.png" alt="token" style="display: block;margin: 0 auto;width: 100%;">
    <t-divider />
    <p style="font-size: larger;font-weight: bold;text-align: center;margin: 20px auto 20px;">请在下方粘贴www_token</p>
    <t-input v-model="token" placeholder="请输入www_token" class="home-input" @change="verify_input"
      :tips="errorMessage"></t-input>
    <div v-if="has_verified" style="text-align: center;">
      <div style="text-align: center;margin: 0 auto 0;width: 70%;">
        <t-button theme="primary" variant="light" @click="test_token" block>登录账号</t-button>

      </div>
      <div style="text-align: left;font-size: small; color: grey;margin-top: 10px;">1.登录成功后，Token将保存在浏览器本地，方便下次快速登录
      </div>
      <div style="text-align: left;font-size: small; color: grey;">2.服务器不会存储你的任何信息</div>
      <div style="text-align: left;font-size: small; color: grey;">3.Token有效期为30天，有效期内可重复使用，超出时间后需要重新获取</div>
    </div>
  </div>
  <!-- token已提交测试 -->
  <div v-if="has_tested">
    <!-- 用户信息卡片 -->
    <div class="card">
      <div @click="toggleCard(1)">
        <p style="font-size: larger;font-weight: bold;text-align: center;"
          :style="{ color: isCollapsed1 ? '#c1c1c1' : '#333' }">用户信息</p>
        <icon-font class="toggle-icon" :name="isCollapsed1 ? 'expand-down' : 'expand-up'"></icon-font>
      </div>
      <div class="card-content" style="margin: 0 auto 5px;" v-show="!isCollapsed1">
        <p style="">用户名称：{{ account_info.nick_name }}</p>
        <p style="">绑定手机：{{ account_info.phone }}</p>
        <p style="">团队身份：{{ account_info.team_name }} - {{ account_info.name }}</p>
        <p style="">打卡规则：{{ account_info.rule }}</p>
      </div>
    </div>
    <br>
    <!-- 模拟位置信息卡片 -->
    <div v-if="daka_config" class="card">
      <div @click="toggleCard(2)">
        <p style="font-size: larger; font-weight: bold; text-align: center;"
          :style="{ color: isCollapsed2 ? '#c1c1c1' : '#333' }">位置模拟</p>
        <icon-font class="toggle-icon" :name="isCollapsed2 ? 'expand-down' : 'expand-up'"></icon-font>
      </div>
      <div class="card-content" style="margin-left: 20px;" v-show="!isCollapsed2">
        <p style="">省市街道：{{ daka_config.address }}</p>
        <p style="">打卡地址：{{ daka_config.location }}</p>
        <p style="">经度：{{ daka_config.longitude }} </p>
        <p style="">纬度：{{ daka_config.latitude }} </p>
        <p style="">Wi-Fi名称：{{ daka_config.wifi }} </p>
        <p style="">Wi-Fi Mac地址：{{ daka_config.wifi_mac }} </p>
        <p style="">定位点随机偏移：50 米</p>
      </div>
    </div>

    <br>

    <!-- 今日打卡信息卡片 -->
    <div v-if="today_status">
      <!-- <t-divider /> -->
      <p style="font-size: larger;font-weight: bold;text-align: center;margin: 1% auto 5px;">今日打卡信息</p>
      <div class="card">
        <p style="font-weight: bold;text-align: center;">当前班次打卡</p>
        <div v-if="today_status.current">
          <div>
            <div v-for="(item, index) in today_status.current.details" :key="index" style="margin-left: 20px;">
              <p>{{ item.desc }}：{{ item.statusDesc }}
              <div v-if="item.currentTag" style="color: red;display: contents;">&nbsp;[当前打卡点]</div>
              </p>
            </div>
          </div>
        </div>
        <p style="font-weight: bold;text-align: center;margin-top: 10px;">其他班次打卡</p>
        <div v-if="today_status.others">
          <div v-for="(shift, shiftIndex) in today_status.others" :key="shiftIndex" class="shift"
            style="margin-left: 20px;">
            <div>
              <div v-for="(item, index) in shift.details" :key="index">
                <p>{{ item.desc }}：{{ item.statusDesc }}</p>
              </div>
            </div>
          </div>
        </div>
        <div style="width: 50%;text-align: center;margin: 0 auto;">
          <t-button theme="light" variant="outline" @click="refresh_today_status" block>刷新列表</t-button>
        </div>
      </div>
      <br>


      <br>
      <div style="text-align: center;">
        <t-button theme="primary" @click="daka"
          style="font-size: 20px;letter-spacing: 3px;text-align: center;width: 70%;height: 60px;margin: 0 20px;box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">一键打卡</t-button>
      </div>
      <div style="text-align: center;font-size: small; color: grey;margin-top: 10px;">请勿连续点击按钮，防止重复打卡</div>
      <div style="text-align: center;font-size: small; color: grey;">仅供学习交流，请合理使用</div>
    </div>
  </div>
  <t-divider />
  <div
    style="text-align: center;font-size: small; color: grey;display: flex;align-items: center;justify-content: center;margin-top: 30px;">
    <div>下次自动登录&nbsp;</div>
    <t-switch size="small" :default-value="true" :icon="icons" v-model="auto_login"
      @change="save_auto_login"></t-switch>
  </div>
  <!-- github开源地址 -->
  <p style="text-align: center;margin-top: 5px;">
    <a href="https://github.com/Little-King2022/HikIOT_signature" target="_blank">
      <img alt="GitHub" src="https://img.shields.io/badge/Github-%E9%A1%B9%E7%9B%AE%E5%9C%B0%E5%9D%80-blue">&nbsp;
      <img alt="GitHub stars"
        src="https://img.shields.io/github/stars/Little-King2022/HikIOT_signature.svg?style=social">
    </a>
  </p>
</template>

<style scoped>
.home-input {
  margin: 20px auto 10px;
  display: block;
  width: 90%;
  border: 1px solid rgba(220, 220, 220, 1);
  border-radius: 6px;
}

/* 蓝色卡片 */
.card {
  margin: 0px 10px;
  background-color: rgba(232, 244, 255, 0.524);
  padding: 10px 20px;
  border-radius: 10px;
  --td-input-bg-color: aliceblue;
  --td-input-suffix-text-color: rgba(142, 142, 142, 0.5);
  --td-input-vertical-padding: 10px;
  border-radius: 8px;
  box-shadow: 6px 6px 8px rgba(0, 0, 0, 0.3);
  animation: fade-in 0.2s;
  position: relative;
  overflow: hidden;
  transition: height 1s ease;
}

.card-content {
  transition: max-height 0.3s ease-in-out;
}

.toggle-icon {
  position: absolute;
  top: 12px;
  right: 10px;
  cursor: pointer;
  font-size: 20px;
  transition: transform 1s ease;
}



.card.collapsed .toggle-icon {
  transform: rotate(180deg);
  /* 旋转图标，表示折叠状态 */
}

/* switch开关 */
t-switch {
  height: 1px;
}
</style>
