<script setup>
import { ref } from 'vue';
import { Toast } from 'tdesign-mobile-vue';
import axios from 'axios';


const token = ref('');
const has_verified = ref(false)
const has_tested = ref(false)
const account_info = ref({})
const today_status = ref({})
const daka_config = ref({})
const errorMessage = ref(''); // 错误提示信息


if (localStorage.getItem('token')) {
  token.value = localStorage.getItem('token');
  has_verified.value = true;
}


const verify_input = () => {
  if (token.value.length === 36) {
    has_verified.value = true;
    errorMessage.value = ''; // 清除错误信息
  } else {
    has_verified.value = false;
    errorMessage.value = 'Token 长度应为 36 位，请检查后重新输入'; // 显示错误信息
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
      });
  } else {
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



</script>

<template>
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
      <div style="text-align: center;margin: 20px auto 0;width: 70%;">
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
    <p style="font-size: larger;font-weight: bold;text-align: center;margin: 20px auto 5px;">用户信息</p>
    <div class="card">
      <p style="">用户名称：{{ account_info.nick_name }}</p>
      <p style="">绑定手机：{{ account_info.phone }}</p>
      <p style="">团队身份：{{ account_info.team_name }} - {{ account_info.name }}</p>
      <p style="">打卡规则：{{ account_info.rule }}</p>
    </div>
    <br>
    <div v-if="today_status">
      <t-divider />
      <p style="font-size: larger;font-weight: bold;text-align: center;margin: 20px auto 5px;">今日打卡信息</p>
      <div class="card">
        <p style="font-weight: bold;text-align: center;">当前班次打卡</p>
        <div v-if="today_status.current">
          <div>
            <div v-for="(item, index) in today_status.current.details" :key="index">
              <p>{{ item.desc }}：{{ item.statusDesc }}
              <div v-if="item.currentTag" style="color: red;display: contents;">&nbsp;[当前打卡点]</div>
              </p>
            </div>
          </div>
        </div>
        <p style="font-weight: bold;text-align: center;margin-top: 10px;">其他班次打卡</p>
        <div v-if="today_status.others">
          <div v-for="(shift, shiftIndex) in today_status.others" :key="shiftIndex" class="shift">
            <div>
              <div v-for="(item, index) in shift.details" :key="index">
                <p>{{ item.desc }}：{{ item.statusDesc }}</p>
              </div>
            </div>
          </div>
        </div>
        <div style="width: 80%;text-align: center;margin: 0 auto;">
          <t-button theme="light" variant="outline" @click="refresh_today_status" block>刷新列表</t-button>
        </div>

      </div>
      <br>
      <t-divider />
      <div style="display: flex; align-items: center; justify-content: center;">
        <p style="font-size: larger; font-weight: bold; text-align: center; flex: 1;">模拟定位信息</p>
        <!-- <t-button theme="primary" variant="outline" @click="" size="smaller">修改定位信息</t-button> -->
      </div>

      <div v-if="daka_config" style="margin-left: 20px;">
        <p style="">省市街道：{{ daka_config.address }}</p>
        <p style="">打卡地址：{{ daka_config.location }}</p>
        <p style="">经度：{{ daka_config.longitude }} </p>
        <p style="">纬度：{{ daka_config.latitude }} </p>
        <p style="">Wi-Fi名称：{{ daka_config.wifi }} </p>
        <p style="">Wi-Fi Mac地址：{{ daka_config.wifi_mac }} </p>
        <p style="">定位点随机偏移：50 米</p>
      </div>
      <br>
      <div style="text-align: center;">
        <t-button theme="primary" @click="daka" style="text-align: center;width: 70%;margin: 0 20px">一键打卡</t-button>
      </div>
      <div style="text-align: left;font-size: small; color: grey;margin-top: 10px;">1.请勿连续点击按钮，防止重复打卡</div>
      <div style="text-align: left;font-size: small; color: grey;">2.本工具依赖于管理员开启“手机定位打卡”功能，若管理员关闭，则无法进行远程打卡</div>
      <div style="text-align: left;font-size: small; color: grey;">3.本工具经过严格测试，其效果等同于在小程序中直接定位打卡</div>
      <div style="text-align: left;font-size: small; color: grey;">4.本工具仅供学习交流，请合理使用</div>
    </div>
  </div>
  <t-divider />
  <!-- github开源地址 -->
  <p style="text-align: center;margin-top: 20px;">
    <a href="https://github.com/Little-King2022/HikIOT_signature" target="_blank">
      <img alt="GitHub" src="https://img.shields.io/badge/Github-%E9%A1%B9%E7%9B%AE%E5%9C%B0%E5%9D%80-blue">&nbsp;
      <img alt="GitHub last commit"
        src="https://img.shields.io/github/last-commit/Little-King2022/HikIOT_signature">&nbsp;
      <img alt="GitHub stars"
        src="https://img.shields.io/github/stars/Little-King2022/HikIOT_signature.svg?style=social">
    </a>
  </p>
</template>

<style scoped>
.home-input {
  margin: 20px auto;
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
}
</style>
