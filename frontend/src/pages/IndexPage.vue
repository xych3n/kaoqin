<template>
  <q-page class="q-pa-lg">
    <div class="row q-col-gutter-md">
      <div class="col-lg-8 col-sm-8 col-md-8 col-xs-12">
        <q-card class="no-shadow rounded-card" bordered>
          <q-card-section>
            <div class="text-subtitle1">统计数据</div>
          </q-card-section>
          <q-card-section class="row q-pa-none">
            <div class="col-lg-6 col-sm-6 col-md-6 col-xs-12">
              <q-card class="no-shadow rounded-card">
                <q-card-section>
                  <v-chart class="gauge-chart" :option="option1" autoresize />
                </q-card-section>
              </q-card>
            </div>
            <div class="col-lg-6 col-sm-6 col-md-6 col-xs-12">
              <q-card class="col no-shadow rounded-card">
                <q-card-section>
                  <v-chart class="gauge-chart" :option="option2" autoresize />
                </q-card-section>
              </q-card>
            </div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col-lg-4 col-sm-4 col-md-4 col-xs-12">
        <q-card class="no-shadow rounded-card" bordered>
          <q-card-section>
            <div class="text-subtitle1">最新活动</div>
          </q-card-section>
          <q-card-section>
            <div class="text-subtitle1">{{ latestActivities[0]?.title }}</div>
            <div class="text-h6">{{ latestActivities[0]?.date }}</div>
            <div class="text-caption text-grey-8">{{ latestActivities[0]?.category }}</div>
          </q-card-section>
          <q-card-section>
            <div class="text-subtitle1">{{ latestActivities[1]?.title }}</div>
            <div class="text-h6">{{ latestActivities[1]?.date }}</div>
            <div class="text-caption text-grey-8">{{ latestActivities[1]?.category }}</div>
          </q-card-section>
          <q-card-section class="q-mt-md">
            <q-btn class="full-width" no-caps outline rounded
              text-color="grey-8" label="查看全部活动" to="/activity" />
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12">
        <q-card class="no-shadow rounded-card">
          <q-card-section class="q-pl-none col-12">
            <div class="text-subtitle1 q-pl-md">
              考勤记录
              <q-btn class="float-right" flat text-color="grey-8"
                style="padding: 4px; min-width: 0px; min-height: 0px;"
                label="更多" icon-right="las la-arrow-right" to="/particip" />
            </div>
          </q-card-section>
          <q-card-section class="q-pa-none">
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
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import {
  computed, onMounted, ref, Ref,
} from 'vue';
import { QTableProps } from 'quasar';
import * as echarts from 'echarts/core';
import { GaugeChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import VChart from 'vue-echarts';

import { api } from 'boot/axios';
import {
  Activity, Particip, Pagination, UserDetail,
} from './schemas';

const maxInvolvement1 = computed(() => {
  const studentNumber = localStorage.getItem('student_number');
  if (studentNumber) {
    const code = studentNumber.substring(4, 6);
    if (code === '52') return 30;
    return 50;
  }
  return 0;
});

echarts.use([GaugeChart, CanvasRenderer]);
const involvement1 = ref(0);
const involvement2 = ref(0);
const option1 = ref({
  series: [{
    type: 'gauge',
    radius: '100%',
    data: [{
      value: involvement1,
      name: '学术讲座',
    }],
    max: maxInvolvement1,
    progress: { show: true },
    axisTick: { show: false },
    detail: { offsetCenter: [0, '50%'] },
  }],
});
const option2 = ref({
  series: [{
    type: 'gauge',
    radius: '100%',
    data: [{
      value: involvement2,
      name: '研会活动',
    }],
    max: 20,
    progress: { show: true },
    axisTick: { show: false },
    detail: { offsetCenter: [0, '50%'] },
  }],
});

const latestActivities: Ref<Activity[]> = ref([]);

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
  pagination: {
    page: 1,
    rowsPerPage: 5,
    rowsNumber: 0,
  },
  rowsPerPageOptions: [5],
});

tableProps.value.onRequest = (requestProp) => {
  tableProps.value.loading = true;
  const { filter, pagination: { page, rowsPerPage } } = requestProp;
  const limit = rowsPerPage === 0 ? 100 : rowsPerPage;
  const skip = rowsPerPage * (page - 1);
  api.get<Pagination<Particip>>('/particips/', { params: { skip, limit, filter } })
    .then(({ data: { total, list } }) => {
      // set a unique attribute for each row
      tableProps.value.rows = list.slice().map((particip) => ({
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

onMounted(() => {
  tableRef.value.requestServerInteraction();
  api.get<Pagination<Activity>>('/activities/', { params: { skip: 0, limit: 2 } })
    .then(({ data: { list } }) => {
      latestActivities.value = { ...list };
    });
  api.get<UserDetail>('/users/me').then(({ data }) => {
    involvement1.value = data.involvements['学术讲座'];
    involvement2.value = data.involvements['研会活动'];
  });
});

</script>

<style>
.gauge-chart {
  height: 277px;
  width: 100%;
}
</style>
