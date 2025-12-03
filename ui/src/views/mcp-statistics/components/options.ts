import * as echarts from 'echarts'

export const DATE_FORMAT = 'YYYY-MM-DD'
const colorList: Array<string> = [ '#3388FF', '#11C79B', '#FBD444', '#7F6AAD', '#F56C6C', '#53C8D1', '#59CB74', '#585247' ]

export const lineOptionConfig = {
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#FFFFFF',
    borderColor: '#E9ECF2',
    confine: true,
    textStyle: {
      color: '#223355'
    },
    axisPointer: {
      type: 'line',
      lineStyle: {
        width: 1,
        type: 'dashed',
        color: 'rgba(45,75,115,0.5)',
        shadowColor: 'transparent',
        shadowBlur: 1
      }
    }
  },
  color: colorList,
  legend: {
    y: 2,
    itemHeight: 8,
    borderColor: '#FFF',
    data: []
  },
  grid: {
    top: '10%',
    left: '3%',
    right: '3%',
    bottom: '3%',
    containLabel: true
  },
  toolbox: {
    show: false,
    feature: {
      saveAsImage: {}
    }
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: [],
    axisTick: {
      show: false,
      alignWithLabel: true
    },
    axisLine: {
      lineStyle: {
        color: 'rgba(0,0,0,0.1)'
      }
    },
    axisLabel: {
      // margin: 10,
      color: '#6B7A99',
      textStyle: {
        fontSize: 12
      }
    }
  },
  yAxis: {
    type: 'value',
    axisTick: {
      show: false,
      alignWithLabel: true
    },
    axisLine: {
      lineStyle: {
        color: 'rgba(0,0,0,0.1)'
      }
    },
    axisLabel: {
      color: '#6B7A99',
      textStyle: {
        fontSize: 12
      }
    },
    splitLine: {
      lineStyle: {
        type: 'dashed',
        color: 'rgba(233,236,242,0.85)'
      }
    }
  },
  series: []
}

export const getLineLegendData = (name: string, i: number = 0) => {
  return {
    name: name || '',
    itemStyle: {
      color: colorList[i] || '#3388FF',
      // borderColor: '#FFFFFF',
      borderWidth: 2,
      shadowColor: 'rgba(0, 0, 0, .2)',
      shadowBlur: 1
    },
    lineStyle: {
      shadowColor: 'transparent'
    },
    textStyle: {
      color: '#223355',
      textBorderColor: 'transparent',
      textShadowColor: 'transparent',
      textShadowBlur: 1
    }
  }
}

export const getLineSeriesData = (name: string, data: Array<number>, i: number = 0) => {
  return {
    name: name || '',
    type: 'line',
    smooth: true,
    data: data,
    symbol: 'circle',
    symbolSize: 5,
    itemStyle: {
      color: colorList[i],
      // borderColor: '#fff',
      borderWidth: 2,
      shadowColor: 'rgba(0, 0, 0, .2)',
      shadowBlur: 1
    }
  }
}

export const barOptionConfig: any = {
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#FFFFFF',
    borderColor: '#E9ECF2',
    confine: true,
    textStyle: {
      color: '#223355'
    },
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    top: '4%',
    left: '3%',
    right: '4%',
    bottom: '6%',
    containLabel: true
  },
  xAxis: [
    {
      type: 'category',
      data: [],
      axisTick: {
        show: false,
        alignWithLabel: true
      },
      axisLine: {
        lineStyle: {
          type: 'solid',
          color: 'rgba(233,236,242,1)'
        }
      },
      axisLabel: {
        // margin: 10,
        color: '#6B7A99',
        textStyle: {
          fontSize: 12
        }
      }
    }
  ],
  yAxis: [
    {
      type: 'value',
      axisLabel: {
        // margin: 10,
        color: '#6B7A99',
        textStyle: {
          fontSize: 12
        }
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: 'rgba(233,236,242,0.85)'
        }
      }
    }
  ],
  series: [
    {
      name: '',
      type: 'bar',
      barWidth: 32,
      data: [],
      itemStyle: {
        normal: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#188df0' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#83bff6' }
          ]),
          barBorderRadius: [ 4, 4, 0, 0 ]
        }
      }
    }
  ]
}

export const getBarSeriesData: any = (name: string, data: Array<number>) => {
  return {
    name: name || '',
    type: 'bar',
    barWidth: "15%",
    data: data,
    itemStyle: {
      normal: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#188df0' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#83bff6' }
        ]),
        barBorderRadius: [ 4, 4, 0, 0 ]
      }
    }
  }
}