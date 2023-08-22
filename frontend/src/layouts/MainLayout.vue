<template>
  <q-layout view="lHh Lpr lFf">
    <q-header v-model="showHeader" reveal bordered class="bg-white text-black">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu"
          @click="toggleLeftDrawer" />
        <q-toolbar-title class="text-subtitle2 text-weight-bolder text-grey-9">
          考勤管理系统
        </q-toolbar-title>
        <div>Powered by Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered class="full-height bg-grey-1"
      @update:model-value="showHeader = !leftDrawerOpen">
      <q-toolbar>
        <q-item class="q-mt-lg q-px-lg">
          <q-item-section avatar>
            <q-avatar class="cursor-pointer">
              <img src="Soochow_University1.svg">
            </q-avatar>
          </q-item-section>
          <q-item-section class="text-grey-9 text-subtitle2 text-weight-bolder">
            计算机学院考勤管理系统
          </q-item-section>
        </q-item>
      </q-toolbar>
      <q-list class="q-mt-lg q-px-lg" v-for="menu in menusList" :key="menu.title">
        <q-item :to="menu.link" active-class="q-item-no-link-highlighting">
          <q-item-section avatar>
            <q-icon :name="menu.icon"/>
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-weight-medium text-grey-9">
              {{ menu.title }}
            </q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
      <div class="absolute-bottom">
        <q-separator />
        <q-item class="q-my-md q-px-lg">
          <q-item-section side>
            <q-avatar color="grey-8" text-color="white">
              {{ username.slice(-1) }}
            </q-avatar>
          </q-item-section>
          <q-item-section class="text-subtitle1 text-weight-medium">
            <q-item-label>{{ username }}</q-item-label>
            <q-item-label caption>{{ studentNumber }}</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-btn flat dense round icon="more_horiz">
              <q-menu>
                <q-list>
                  <q-item clickable v-close-popup @click="onChangePassword">
                    <q-item-section>修改密码</q-item-section>
                  </q-item>
                  <q-item clickable v-close-popup @click="onLogout">
                    <q-item-section>退出</q-item-section>
                  </q-item>
                </q-list>
              </q-menu>
            </q-btn>
          </q-item-section>
        </q-item>
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>

  <q-dialog v-model="passwordDialogOpen">
    <q-card>
      <q-card-section>
        <q-form>
          <q-item>
            <q-item-section>
              <q-item-label class="q-mb-sm">修改密码</q-item-label>
              <q-input v-model="passwordForm.new_password" filled type="password"
                :rules="[(val) => !!val || '此项为必填项']" />
            </q-item-section>
          </q-item>
          <q-item>
            <q-item-section>
              <q-item-label class="q-mb-sm">确认密码</q-item-label>
              <q-input v-model="passwordForm.confirm_password" filled type="password"
                :rules="[(val) => !!val || '此项为必填项',
                         (val) => val === passwordForm.new_password || '与输入的新密码不一致']" />
            </q-item-section>
          </q-item>
          <q-item class="q-mt-lg">
            <q-item-section>
              <q-btn outline rounded label="取消" @click="passwordDialogOpen = false" />
            </q-item-section>
            <q-item-section>
              <q-btn outline rounded label="确定" type="submit" @click="changePassword" />
            </q-item-section>
          </q-item>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';

const $q = useQuasar();
const $router = useRouter();

const menusList = [
  {
    title: '首页',
    icon: 'la la-home',
    link: '/',
  },
  {
    title: '活动',
    icon: 'lar la-star',
    link: '/activity',
  },
  {
    title: '记录',
    icon: 'las la-archive',
    link: '/particip',
  },
  {
    title: '用户',
    icon: 'las la-users',
    link: '/user',
  },
];

const showHeader = ref(true);
const leftDrawerOpen = ref(false);
const toggleLeftDrawer = () => {
  leftDrawerOpen.value = !leftDrawerOpen.value;
};

const username = computed(() => localStorage.getItem('name') ?? '');
const studentNumber = computed(() => localStorage.getItem('student_number'));

const onLogout = () => {
  localStorage.removeItem('access-token');
  $router.push('/login');
};

const passwordDialogOpen = ref(false);
const defaultPasswordForm = {
  new_password: '',
  confirm_password: '',
};
const passwordForm = ref();
const onChangePassword = () => {
  passwordForm.value = { ...defaultPasswordForm };
  passwordDialogOpen.value = true;
};
const changePassword = () => {
  api.put(`/users/${studentNumber.value}/reset-password?new_password=${passwordForm.value.new_password}`)
    .then(() => {
      $q.dialog({
        message: '修改成功',
      }).onOk(() => {
        localStorage.removeItem('access-token');
        $router.push('/login');
      });
    });
};

</script>
