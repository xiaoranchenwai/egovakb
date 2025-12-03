<template>
  <div class="mcp-stats-overview">
    <div class="item resource">
      <div class="item-title">
        <div class="icon"></div>
        <div class="text">资源数量</div>
      </div>
      <div class="item-content">
        <div class="chunk">
          <div class="chunk-title">MCP模板分类数</div>
          <div class="chunk-count">
            <span class="chunk-count-text">{{ serviceInfo.total_template_groups }}</span>
            <span class="chunk-count-unit">个</span>
          </div>
          <div class="chunk-trend">
            <div>
              <span class="chunk-trend-text">今日新增</span>
              <span class="chunk-trend-num">{{ serviceInfo.today_new_template_groups }}</span>
            </div>

          </div>
        </div>
        <div class="chunk">
          <div class="chunk-title">MCP模板数</div>
          <div class="chunk-count">
            <span class="chunk-count-text">{{ serviceInfo.total_templates }}</span>
            <span class="chunk-count-unit">个</span>
          </div>
          <div class="chunk-trend">
            <div>
              <span class="chunk-trend-text">今日新增</span>
              <span class="chunk-trend-num">{{ serviceInfo.today_new_templates }}</span>
            </div>
          </div>
        </div>

      </div>
    </div>
    <div class="item use">
      <div class="item-title">
        <div class="icon"></div>
        <div class="text">调用次数</div>
      </div>
      <div class="item-content">
        <div class="chunk">
          <div class="chunk-title">MCP服务调用总数</div>
          <div class="chunk-count">
            <span class="chunk-count-text">{{ serviceInfo.total_service_calls }}</span>
            <span class="chunk-count-unit">个</span>
          </div>
          <div class="chunk-trend">
            <div>
              <span class="chunk-trend-text">今日调用</span>
              <span class="chunk-trend-num">{{ serviceInfo.today_new_service_calls }}</span>
            </div>

          </div>
        </div>
        <div class="chunk">
          <div class="chunk-title">MCP工具调用次数</div>
          <div class="chunk-count">
            <span class="chunk-count-text">{{ serviceInfo.total_tools_calls }}</span>
            <span class="chunk-count-unit">个</span>
          </div>
          <div class="chunk-trend">
            <div>
              <span class="chunk-trend-text">今日调用</span>
              <span class="chunk-trend-num">{{ serviceInfo.today_new_tools_calls }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="item server">
      <div class="item-title">
        <div class="icon"></div>
        <div class="text">服务数量</div>
      </div>
      <div class="item-content">
        <div class="chunk">
          <div class="chunk-title">MCP服务总数</div>
          <div class="chunk-count">
            <span class="chunk-count-text">{{ serviceInfo.total_services || 0 }}</span>
            <span class="chunk-count-unit">个</span>
          </div>
          <div class="chunk-trend">
            <div>
              <span class="chunk-trend-text">运行中</span>
              <span class="chunk-trend-num">{{ serviceInfo.running_services || 0 }}</span>
            </div>

            <div>
              <span class="chunk-trend-text">已停止</span>
              <span class="chunk-trend-num">{{ serviceInfo.stopped_services || 0 }}</span>
            </div>

            <div>
              <span class="chunk-trend-text">异常</span>
              <span class="chunk-trend-num">{{ serviceInfo.error_services || 0 }}</span>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import mcpStatisticsApi from '@/api/mcp-statistics'

const {
  getServiceStats,
  getModuleRankings,
  getToolRankings,
  getServiceRankings,
  getToolExecutions,
  refreshStatistics
} = mcpStatisticsApi
// 服务数量
const serviceInfo = ref<any>({
  total_services: 0,
  running_services: 0,
  stopped_services: 0,
  error_services: 0
})
const getServiceInfos = async () => {
  const res = await getServiceStats()

  if (res.code === 200) {
    serviceInfo.value = res.data || {}
  }
}
onMounted(() => {
  getServiceInfos()
})
</script>

<style lang="scss">
.mcp-stats-overview {
  width: 100%;
  height: 100%;
  position: relative;
  padding: 0 20px 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  .item {
    width: 100%;
    height: 125px;
    position: relative;
    border-radius: 8px;
    display: flex;
    flex-direction: row;
    justify-content: flex-start;

    .item-title {
      width: 80px;
      height: 100%;
      position: relative;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;

      .icon {
        width: 39px;
        height: 39px;
        position: relative;
        margin-bottom: 10px;
        background-size: 100% 100%;
      }

      .text {
        font-size: 14px;
        color: #FFFFFF;
        font-weight: 400;
      }
    }

    .item-content {
      flex: 1;
      height: 100%;
      position: relative;
      padding: 8px;
      display: grid;
      column-gap: 8px;

      .chunk {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 8px;
        padding: 8px 12px 0;
        display: flex;
        flex-direction: column;
        justify-content: space-around;

        .chunk-title {
          font-size: 14px;
          color: #6B7A99;
          height: 22px;
          line-height: 22px;
        }

        .chunk-count {
          height: 36px;

          .chunk-count-text {
            font-size: 24px;
            color: #223355;
            font-weight: 600;
          }

          .chunk-count-unit {
            font-size: 14px;
            color: #6B7A99;
            margin-left: 4px;
          }
        }

        .chunk-trend {
          width: 100%;
          height: 32px;
          line-height: 32px;
          position: relative;
          border-top: 1px dashed #E9ECF2;
          display: flex;
          flex-direction: row;
          justify-content: space-between;

          .chunk-trend-text {
            font-size: 14px;
            color: #6B7A99;
          }

          .chunk-trend-num {
            font-size: 16px;
            font-weight: 600;
            color: #11C79B;
            margin-left: 12px;
          }
        }
      }
    }
  }

  .resource {
    background-color: #B6FAE0;

    .item-title {
      background-image: linear-gradient(0deg, #87EDC9 0%, #11C79B 100%);

      .icon {
        background-image: url('../../../assets/mcp/resource.png');
      }
    }

    .item-content {
      grid-template-columns: repeat(2, 1fr);

      .chunk {

      }
    }
  }

  .use {
    background-color: #D6F7FF;

    .item-title {
      background-image: linear-gradient(0deg, #ADECFF 0%, #33BBFF 100%);

      .icon {
        background-image: url('../../../assets/mcp/num.png');
      }
    }

    .item-content {
      grid-template-columns: repeat(2, 1fr);

      .chunk-trend-num {
        color: #33BBFF !important;
      }
    }
  }

  .server {
    background-color: #FFEDA3;

    .item-title {
      background-image: linear-gradient(0deg, #FFE07A 0%, #FFAA00 100%);

      .icon {
        background-image: url('../../../assets/mcp/server.png');
      }
    }

    .item-content {
      .chunk-trend {
        > div {
          &:nth-child(1) {
            .chunk-trend-num {
              color: #FFAA00 !important;
            }
          }

          &:nth-child(2) {
            .chunk-trend-num {
              color: #A8B4C8 !important;
            }
          }

          &:nth-child(3) {
            .chunk-trend-num {
              color: #FF4433 !important;
            }
          }
        }
      }

      .chunk-trend-num {
        color: #FFAA00 !important;
      }
    }
  }
}
</style>