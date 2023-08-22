<template>
  <q-layout>
    <q-page-container class="bg-grey-2">
      <q-page class="flex flex-center">
        <q-form style="width: 300px;" ref="formRef" @submit="login">
          <q-card bordered class="no-shadow" style="border-radius: 12px;">
            <q-card-section class="q-pa-md text-center text-h6">
              计算机学院考勤管理系统
            </q-card-section>
            <q-card-section class="text-center text-body1 text-weight-bolder">
              登录
            </q-card-section>
            <q-card-section class="q-mx-sm">
              <q-item>
                <q-item-section>
                  <q-item-label class="q-mb-sm text-grey-7">学号</q-item-label>
                  <q-input v-model="username" name="username" dense outlined
                    :rules="[(val) => !!val || '学号不能为空']"/>
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label class="q-mb-sm text-grey-7">密码</q-item-label>
                  <q-input v-model="password" name="password" dense outlined type="password"
                    :rules="[(val) => !!val || '密码不能为空']" />
                </q-item-section>
              </q-item>
            </q-card-section>
            <q-card-section class="text-center q-pa-none text-grey-8">
              <a>
                忘记密码
                <q-tooltip anchor="center right" self="center left">
                  初始密码为身份证后六位，若忘记密码，请联系管理员重置
                </q-tooltip>
              </a>
            </q-card-section>
            <q-card-section class="q-mx-sm q-mb-md">
              <q-btn class="bg-dark text-white full-width" rounded
                label="登录" type="submit" />
            </q-card-section>
          </q-card>
        </q-form>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { Ref, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from 'boot/axios';
import { BearerToken } from './schemas';

const $q = useQuasar();
const $router = useRouter();

const formRef = ref();
const username: Ref<string> = ref('');
const password: Ref<string> = ref('');

const login = () => {
  formRef.value.validate().then((success: boolean) => {
    if (success) {
      api.post<BearerToken>(
        '/login/access-token',
        { username: username.value, password: password.value },
        { headers: { 'content-type': 'multipart/form-data' } },
      ).then(({ data }) => {
        localStorage.setItem('access-token', data.access_token);
        $router.push('/');
      }).catch(() => {
        $q.dialog({ message: '账号或密码错误！' });
      });
    }
  });
};
</script>
