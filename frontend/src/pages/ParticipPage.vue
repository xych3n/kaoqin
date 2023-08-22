<template>
  <q-page class="q-pa-lg">
    <q-card class="no-shadow">
      <q-card-section class="row justify-end q-gutter-xs">
        <q-input v-model="tableProps.filter" rounded outlined dense clearable debounce="500">
          <template #prepend>
            <q-icon name="search" />
          </template>
        </q-input>
        <q-btn outline rounded label="导出" icon="las la-cloud-download-alt"
          @click="onDownloadFile" :loading="downloadLoading"  />
        <q-btn outline rounded label="上传" icon="las la-cloud-upload-alt"
          @click="onUploadFile" v-show="isSuperuser" />
        <q-btn outline rounded label="添加" icon="las la-plus"
          @click="onCreateItem" v-show="isSuperuser" />
        <q-btn outline rounded label="删除" icon="las la-trash-alt"
          @click="onDeleteItems" v-show="isSuperuser" :disable="deleteDisabled" />
      </q-card-section>
    </q-card>

    <q-table class="no-shadow rounded-card" bordered
      ref="tableRef" v-bind="{ ...tableProps }"
      v-model:pagination="tableProps.pagination"
      v-model:selected="tableProps.selected"
    >
      <template v-slot:body-cell-participant="props">
        <q-td :props="props">
          <q-item dense class="q-pl-none q-py-sm">
            <q-item-section>
              <q-item-label>{{ props.row.participant.name }}</q-item-label>
              <q-item-label>{{ props.row.participant.student_number }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-td>
      </template>
      <template v-slot:body-cell-category="props">
        <q-td :props="props">
          <q-chip outline :color="props.row.activity.category === '研会活动' ? 'red' : 'teal'">
            {{ props.row.activity.category }}
          </q-chip>
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="uploadItemsDialog">
      <q-card style="min-width: 360px;">
        <q-card-section>
          <q-form>
            <q-item>
              <q-item-section>
                <q-item-label class="q-mb-sm">活动名称</q-item-label>
                <q-input v-model="participUploadItem!.title" filled
                  hide-bottom-space :rules="[(val) => !!val || '活动名称不可为空']"/>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label class="q-mb-sm">活动日期</q-item-label>
                <q-input v-model="participUploadItem!.date" filled>
                  <template #append>
                    <q-icon name="event" class="cursor-pointer">
                      <q-popup-proxy>
                        <q-date v-model="participUploadItem!.date"
                          mask="YYYY-MM-DD" today-btn/>
                      </q-popup-proxy>
                    </q-icon>
                  </template>
                </q-input>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label class="q-mb-sm">活动类型</q-item-label>
                <q-select v-model="participUploadItem!.category"
                  filled :options="['学术讲座', '研会活动']" />
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label class="q-mb-sm">人员名单</q-item-label>
                <q-file v-model="participUploadItem!.file" filled>
                  <template #prepend>
                    <q-icon name="attach_file" />
                  </template>
                </q-file>
              </q-item-section>
            </q-item>
            <q-item>
              文件格式要求：<br>
              学号 | 姓名 | 计入次数
            </q-item>
            <q-item class="q-mt-lg">
              <q-item-section>
                <q-btn outline rounded label="取消" @click="uploadItemsDialog = false;" />
              </q-item-section>
              <q-item-section>
                <q-btn outline rounded label="上传" type="submit"
                  @click="uploadParticip"/>
              </q-item-section>
            </q-item>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <q-dialog v-model="createItemDialog">
      <q-card style="min-width: 300px;">
        <q-card-section>
          <q-form>
            <q-item>
              <q-item-section>
                <q-item-label class="q-mb-sm">用户</q-item-label>
                <q-select v-model="participCreateItem!.user" filled style="width: 300px"
                  use-input :options="userOptions" @filter="filterUsers">
                </q-select>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label class="q-mb-sm">活动</q-item-label>
                <q-select v-model="participCreateItem!.activity" filled style="width: 300px"
                  use-input :options="activityOptions" @filter="filterActivities">
                </q-select>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section>
                <q-item-label class="q-mb-sm">计入次数</q-item-label>
                <q-input v-model="participCreateItem!.involvement" filled type="number"/>
              </q-item-section>
            </q-item>
            <q-item class="q-mt-lg">
              <q-item-section>
                <q-btn outline rounded label="取消" @click="createItemDialog = false;" />
              </q-item-section>
              <q-item-section>
                <q-btn outline rounded label="添加" @click="createItem" />
              </q-item-section>
            </q-item>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import {
  computed, onMounted, ref, Ref,
} from 'vue';
import {
  useQuasar, QTableProps, date, exportFile,
} from 'quasar';
import { api } from 'src/boot/axios';
import {
  Activity, Particip, Pagination, ParticipCreate, ParticipUpload, User,
} from './schemas';

const $q = useQuasar();

const isSuperuser = computed(() => (localStorage.getItem('is_superuser') ?? '') === 'Y');

const tableRef = ref();
const tableProps: Ref<QTableProps> = ref({
  rows: [],
  columns: [{
    name: 'participant', label: '用户', field: 'participant', align: 'left',
  }, {
    name: 'activity', label: '活动', field: (row) => row.activity.title, align: 'left',
  }, {
    name: 'date', label: '日期', field: (row) => row.activity.date, align: 'left',
  }, {
    name: 'involvement', label: '计入次数', field: 'involvement', align: 'center',
  }, {
    name: 'category', label: '类别', field: (row) => row.activity.category, align: 'center',
  }],
  loading: false,
  filter: '',
  pagination: {
    page: 1,
    rowsPerPage: 10,
    rowsNumber: 0,
  },
  selection: isSuperuser.value ? 'single' : 'none',
});

tableProps.value.rowsPerPageOptions = computed(() => {
  if (tableProps.value.pagination?.rowsNumber ?? 0 <= 100) return [10, 0];
  return [10];
});

tableProps.value.onRequest = (requestProp) => {
  tableProps.value.loading = true;
  if (tableProps.value.pagination?.rowsNumber ?? 0 > 100) {
    requestProp.pagination.rowsPerPage = 10;
  }
  const { filter, pagination: { page, rowsPerPage } } = requestProp;
  const limit = rowsPerPage === 0 ? 100 : rowsPerPage;
  const skip = rowsPerPage * (page - 1);
  api.get<Pagination<Particip>>('/particips/', { params: { skip, limit, filter } })
    .then(({ data: { total, list } }) => {
      // set a unique attribute for each row
      tableProps.value.rows = list.slice().map((particip: Particip) => ({
        ...particip,
        id: `${particip.participant.id}${particip.activity.id}`,
      }));
      tableProps.value.pagination = {
        page,
        rowsPerPage,
        rowsNumber: total,
      };
      tableProps.value.loading = false;
    });
};

onMounted(() => { tableRef.value.requestServerInteraction(); });
const deleteDisabled = computed(() => tableProps.value.selected?.length === 0);
type Options = { label: string, value: unknown }[];
const userOptions: Ref<Options> = ref([]);
const activityOptions: Ref<Options> = ref([]);
const filterUsers = (val: string, update: (callbackFn: () => void) => void, abort: () => void) => {
  if (val.length === 0) {
    abort();
    return;
  }
  update(() => {
    api.get<Pagination<User>>('/users/', { params: { filter: val } })
      .then(({ data: { list } }) => {
        userOptions.value = list.map(
          (item) => ({
            label: `${item.name}(${item.student_number})`,
            value: item.id,
          }),
        );
      });
  });
};

const filterActivities = (
  val: string,
  update: (callbackFn: () => void) => void,
  abort: () => void,
) => {
  if (val.length === 0) {
    abort();
    return;
  }
  update(() => {
    api.get<Pagination<Activity>>('/activities/', { params: { filter: val } })
      .then(({ data: { list } }) => {
        activityOptions.value = list.map(
          (item) => ({
            label: `${item.title}(${item.date})`,
            value: item.id,
          }),
        );
      });
  });
};

const uploadItemsDialog: Ref<boolean> = ref(false);
const createItemDialog: Ref<boolean> = ref(false);
const participUploadItem: Ref<ParticipUpload | undefined> = ref();
const participCreateItem: Ref<ParticipCreate | undefined> = ref();

const onCreateItem = () => {
  participCreateItem.value = {
    user: {
      label: '',
      value: 0,
    },
    activity: {
      label: '',
      value: 0,
    },
    involvement: 0,
    is_stuff: false,
  };
  createItemDialog.value = true;
};

const createItem = () => {
  api.post('/particips/', {
    user_id: participCreateItem.value?.user.value,
    activity_id: participCreateItem.value?.activity.value,
    involvement: participCreateItem.value?.involvement,
    is_stuff: participCreateItem.value?.is_stuff,
  })
    .then(() => {
      $q.dialog({
        message: '添加成功',
      }).onOk(() => {
        createItemDialog.value = false;
        tableRef.value.requestServerInteraction();
      });
    });
};

const downloadLoading = ref(false);

const onDownloadFile = () => {
  downloadLoading.value = true;
  api.get('/particips/download', { responseType: 'blob' })
    .then(({ data }) => {
      downloadLoading.value = false;
      exportFile(`考勤记录-${localStorage.getItem('student_number')}.xlsx`, data);
    });
};

const onUploadFile = () => {
  participUploadItem.value = {
    title: '',
    date: date.formatDate(Date.now(), 'YYYY-MM-DD'),
    category: '学术讲座',
  };
  uploadItemsDialog.value = true;
};

const uploadParticip = () => {
  api.post(
    '/particips/upload',
    { ...participUploadItem.value },
    { headers: { 'content-type': 'multipart/form-data' } },
  ).then(() => {
    uploadItemsDialog.value = false;
    tableRef.value.requestServerInteraction();
  });
};

const onDeleteItems = () => {
  $q.dialog({
    message: '确定删除已选中的记录吗？',
    ok: '确定',
    cancel: '取消',
    noBackdropDismiss: true,
  }).onOk(() => {
    if (tableProps.value.selected) {
      const particip = tableProps.value.selected[0];
      api.delete(`/particips/?activity_id=${particip.activity_id}&user_id=${particip.user_id}`)
        .then(() => {
          $q.dialog({
            message: '删除成功',
          }).onOk(() => {
            tableProps.value.selected?.pop();
            tableRef.value.requestServerInteraction();
          });
        });
    }
  });
};

</script>
