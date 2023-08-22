<template>
  <q-page class="q-pa-lg">
    <q-card class="no-shadow">
      <q-card-section class="row justify-end q-gutter-xs">
        <q-input v-model="tableProps.filter" rounded outlined dense
          clearable debounce="500">
          <template #prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </q-card-section>
    </q-card>

    <q-table class="no-shadow rounded-card" bordered
      ref="tableRef" v-bind="{ ...tableProps }"
      v-model:pagination="tableProps.pagination"
      :visible-columns="visibleColumns"
    >
      <template #body-cell-is_superuser="props">
        <q-td :props="props">
          <q-toggle v-model="props.row.is_superuser"
            @update:model-value="onSetSuperuser(props.row)" />
        </q-td>
      </template>

      <template #body-cell-action="props">
        <q-td :props="props">
          <q-btn flat dense round class="text-grey-6" icon="more_horiz">
              <q-menu>
                <q-list>
                  <q-item clickable v-close-popup @click="onRemovePassword(props.row)">
                    <q-item-section>忘记密码</q-item-section>
                  </q-item>
                </q-list>
              </q-menu>
            </q-btn>
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup lang="ts">
import {
  computed, onMounted, ref, Ref,
} from 'vue';
import { QTableProps, useQuasar } from 'quasar';
import { api } from 'src/boot/axios';
import { Pagination, UserDetail } from './schemas';

const $q = useQuasar();

const isSuperuser = computed(() => (localStorage.getItem('is_superuser') ?? '') === 'Y');

const tableRef = ref();
const tableProps: Ref<QTableProps> = ref({
  rows: [],
  columns: [{
    name: 'student_number', label: '学号', field: 'student_number', align: 'left',
  }, {
    name: 'name', label: '姓名', field: 'name', align: 'left',
  }, {
    name: 'lecture_involvements', label: '学术讲座', field: (row) => row.involvements['学术讲座'], align: 'center',
  }, {
    name: 'event_involvements', label: '研会次数', field: (row) => row.involvements['研会活动'], align: 'center',
  }, {
    name: 'is_superuser', label: '管理员', field: 'is_superuser', align: 'center',
  }, {
    name: 'action', label: '', field: '操作', align: 'right',
  }],
  loading: false,
  filter: '',
  pagination: {
    page: 1,
    rowsPerPage: 10,
    rowsNumber: 0,
  },
});

const visibleColumns = ref([
  'student_number', 'name', 'lecture_involvements', 'event_involvements',
].concat(isSuperuser.value ? ['is_superuser', 'action'] : []));

tableProps.value.rowsPerPageOptions = computed(() => {
  if ((tableProps.value.pagination?.rowsNumber ?? 0) <= 100) return [10, 0];
  return [10];
});

tableProps.value.onRequest = (requestProp) => {
  tableProps.value.loading = true;
  if ((tableProps.value.pagination?.rowsNumber ?? 0) > 100) {
    requestProp.pagination.rowsPerPage = 10;
  }
  const { filter, pagination: { page, rowsPerPage } } = requestProp;
  const limit = rowsPerPage === 0 ? 100 : rowsPerPage;
  const skip = rowsPerPage * (page - 1);
  api.get<Pagination<UserDetail>>('/users/', { params: { skip, limit, filter } })
    .then(({ data: { total, list } }) => {
      // set a unique attribute for each row
      tableProps.value.rows = list.slice();
      tableProps.value.pagination = {
        page,
        rowsPerPage,
        rowsNumber: total,
      };
      tableProps.value.loading = false;
    });
};

onMounted(() => { tableRef.value.requestServerInteraction(); });

const onSetSuperuser = (user: UserDetail) => {
  api.put(`/users/${user.student_number}/set-superuser?is_superuser=${!!user.is_superuser}`);
};

const onRemovePassword = (user: UserDetail) => {
  api.put(`/users/${user.student_number}/reset-password`)
    .then(() => {
      $q.dialog({
        message: '密码重置成功',
      });
    });
};

</script>
