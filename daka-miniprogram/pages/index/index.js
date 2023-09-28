const app = getApp();

Page({
  nfc: null,

  data: {
    records: [],
  },

  onLoad() {
    const that = this;

    function getCurrentTime() {
      const timestamp = Math.floor(new Date().getTime() / 1000);
      const date = new Date(timestamp * 1000);
      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      const seconds = date.getSeconds().toString().padStart(2, '0');
      const time = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
      return time;
    }

    function discoverHandler(res) {
      const uidUint8Array = new Uint8Array(res.id);
      if (uidUint8Array.length !== 4) {
        return;
      }
      const uidDigits = [];
      for (const byte of uidUint8Array) {
        uidDigits.push(byte.toString(16));
      }
      uidDigits.reverse();
      const uid = Number('0x' + uidDigits.join(''));
      const records = that.data.records;
      records.unshift({
        uid,
        time: getCurrentTime(),
      });
      wx.setStorage({
        key: 'records',
        data: records,
        encrypt: true,
      });
      that.setData({ records });
      wx.showToast({
        title: '打卡成功',
      });
      wx.vibrateShort({
        type: 'heavy',
      });
    }

    const nfc = wx.getNFCAdapter();
    this.nfc = nfc;
    nfc.onDiscovered(discoverHandler);
    nfc.startDiscovery({
      fail(err) {
        wx.showToast({
          title: '该机型不支持NFC！',
          icon: 'error',
        });
        console.log(err);
      }
    });

    wx.showLoading({
      title: '加载数据...',
    });
    wx.getStorage({
      key: 'records',
      encrypt: true,
      success (res) {
        that.setData({ records: res.data });
        wx.hideLoading();
      }
    });
  },

  clear() {
    const that = this;
    wx.showModal({
      content: '确定要清空数据吗？',
      complete: (res) => {
        if (res.confirm) {
          that.setData({ records: [] });
          wx.setStorage({
            key: 'records',
            data: [],
            encrypt: true,
          });
          wx.showToast({
            title: '已清空',
          });
        }
      }
    });
  },

  save() {
    const clipboardText = this.data.records.map(item => `${item.uid}\t${item.time}`).join('\n');
    wx.setClipboardData({
      data: clipboardText,
      success: function (res) {
        wx.showToast({
          title: '已复制到剪贴板',
        });
      },
      fail: function (err) {
        wx.showToast({
          title: '复制失败',
          icon: 'error',
        });
        console.log(err);
      },
    });
  },
})