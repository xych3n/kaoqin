<template>
  <q-page class="q-pa-lg">
    <q-card class="no-shadow">
      <q-card-section class="row justify-end q-gutter-xs">
        <q-input v-model="tableProps.filter" rounded outlined dense clearable debounce="500">
          <template #prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </q-card-section>
    </q-card>

    <q-table class="no-shadow rounded-card" bordered ref="tableRef" v-bind="{ ...tableProps }"
      v-model:pagination="tableProps.pagination">
      <template #body="props">
        <q-tr
          :class="isSuperuser ? 'cursor-pointer' : ''"
          :props="props" @click="onRowClick(props.row)"
        >
          <q-td
            v-for="col in props.cols.filter((col: any) => col.name !== 'category')"
            :key="col.name"
          >
            {{ col.value }}
          </q-td>
          <q-td key="category" :props="props">
            <q-chip outline :color="props.row.category === '研会活动' ? 'red' : 'teal'">
              {{ props.row.category }}
            </q-chip>
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-dialog v-model="sideDialog" position="right" :maximized="true">
      <q-card class="full-height" style="width: 450px;">
        <q-card-section class="col-12">
          <q-btn flat icon="close" @click="sideDialog = false" />
        </q-card-section>
        <q-card-section class="col-12">
          <q-item class="full-width">
            <q-item-section>
              <q-item-label class="q-mb-sm text-grey-7">活动名称</q-item-label>
              <q-input v-model="activityItem!.title" filled />
            </q-item-section>
          </q-item>
          <q-item class="full-width">
            <q-item-section>
              <q-item-label class="q-mb-sm text-grey-7">活动日期</q-item-label>
              <q-input v-model="activityItem!.date" filled>
                <template #append>
                  <q-icon class="cursor-pointer" name="event">
                    <q-popup-proxy>
                      <q-date v-model="activityItem!.date" mask="YYYY-MM-DD" today-btn />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </q-item-section>
          </q-item>
          <q-item class="full-width">
            <q-item-section>
              <q-item-label class="q-mb-sm text-grey-7">活动类型</q-item-label>
              <q-select v-model="activityItem!.category" filled :options="['研会活动', '学术讲座']" />
            </q-item-section>
          </q-item>
          <q-item class="full-width">
            <q-item-section>
              <q-item-label class="q-mb-sm text-grey-7">参与人数</q-item-label>
              <q-input v-model="activityItem!.headcount" filled disable />
            </q-item-section>
          </q-item>
          <q-item class="full-width q-mt-lg">
            <q-item-section>
              <q-btn class="q-py-sm" outline rounded label="删除活动" @click="onDelete" />
            </q-item-section>
          </q-item>
          <q-item class="full-width q-mt-sm">
            <q-item-section>
              <q-btn class="q-py-sm" outline rounded :disable="saveDisabled" label="保存"
                @click="onSave" />
            </q-item-section>
          </q-item>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import {
  computed, onMounted, ref, Ref,
} from 'vue';
import { useQuasar, QTableProps } from 'quasar';
import { api } from 'src/boot/axios';
import {
  ActivityDetail, Pagination,
} from './schemas';

const $q = useQuasar();

const isSuperuser = computed(() => (localStorage.getItem('is_superuser') ?? '') === 'Y');

const tableRef = ref();
const tableProps: Ref<QTableProps> = ref({
  rows: [],
  columns: [{
    name: 'title', label: '活动名称', field: 'title', align: 'left',
  }, {
    name: 'date', label: '活动日期', field: 'date', align: 'left',
  }, {
    name: 'headcount', label: '参与人数', field: 'headcount', align: 'left',
  }, {
    name: 'category', label: '活动类别', field: 'category', align: 'center',
  }],
  loading: false,
  filter: '',
  pagination: {
    page: 1,
    rowsPerPage: 10,
    rowsNumber: 0,
  },
});

tableProps.value.rowsPerPageOptions = computed(() => {
  if ((tableProps.value.pagination?.rowsNumber ?? 0) <= 100) return [10, 0];
  return [10];
});

tableProps.value.onRequest = (requestProp) => {
  tableProps.value.loading = true;
  const { filter, pagination: { page, rowsPerPage } } = requestProp;
  const limit = rowsPerPage === 0 ? 100 : rowsPerPage;
  const skip = rowsPerPage * (page - 1);
  api.get<Pagination<ActivityDetail>>('/activities/', { params: { skip, limit, filter } })
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

const sideDialog = ref(false);
const activityItem: Ref<ActivityDetail | undefined> = ref();
const rawActivityItem: Ref<ActivityDetail | undefined> = ref();

const saveDisabled = computed(() => {
  if (!!activityItem.value && !!rawActivityItem.value) {
    if (activityItem.value.title !== rawActivityItem.value.title
      || activityItem.value.date !== rawActivityItem.value.date
      || activityItem.value.category !== rawActivityItem.value.category) {
      return false;
    }
  }
  return true;
});

const onRowClick = (row: ActivityDetail) => {
  if (!isSuperuser.value) return;
  activityItem.value = { ...row };
  rawActivityItem.value = { ...row };
  sideDialog.value = true;
};

const onDelete = () => {
  $q.dialog({ message: '删除活动将导致相关考勤记录也被删除，确定删除吗？', cancel: true }).onOk(() => {
    api.delete(`/activities/${activityItem?.value?.id}`)
      .then(() => {
        sideDialog.value = false;
        tableRef.value.requestServerInteraction();
      });
  });
};

const onSave = () => {
  api.put(
    `/activities/${activityItem.value?.id}`,
    {
      id: activityItem.value?.id,
      title: activityItem.value?.title,
      date: activityItem.value?.date,
      category: activityItem.value?.category,
    },
  )
    .then(() => {
      sideDialog.value = false;
      tableRef.value.requestServerInteraction();
    });
};

</script>
