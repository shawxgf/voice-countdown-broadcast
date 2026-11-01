# 语音倒计时播报器

支持「分:秒:百分秒」精度的语音倒计时工具，为 OPPO（ColorOS）手机设计，可添加到桌面当独立 App 使用。

## 一、功能

| 项目 | 说明 |
| --- | --- |
| 时间格式 | `00:00:00`，前两位为分、中间两位为秒、末两位为百分秒（1 秒 = 100 份） |
| 可设置部分 | 前四位（分与秒），末两位固定从 `00` 起倒计 |
| 播报规则 | 剩余 **> 10 秒**：每跨过一个 10 秒节点播报（50、40、30…）；剩余 **≤ 10 秒**：每整秒播报（10、9、8…1）；归零播报结束提示 |
| 播报人声 | 下拉切换系统全部 TTS 人声（按中文/其他分组），可调语速、音调、音量，支持试听 |
| 其他 | 屏幕常亮锁、结束蜂鸣、最后 10 秒振动、快捷时长、离线可用（PWA） |

播报节点按「整十节点」对齐而非「从起点每 10 秒」：例如设定 1:25，播报序列为 `1:25 → 20 → 10 → 9 → 8 … 1 → 时间到`，与体育计时习惯一致。

## 二、目录结构

```
计时播报器/
├─ index.html              应用主体（单文件，含样式与逻辑）
├─ manifest.json           PWA 清单（名称、图标、全屏启动）
├─ sw.js                   离线缓存
├─ assets/icons/           logo：icon.svg、icon-512/192.png、icon-maskable-512.png 等
├─ tools/make_icons.py     logo 绘制脚本（改配色/几何后重跑即可出新图标）
├─ tools/simulate.js       无浏览器仿真，校验各时长下的播报时序
└─ README.md
```

## 三、本地预览

```bash
cd 计时播报器
python -m http.server 8123
# 手机与电脑同一 Wi-Fi 时，用 OPPO 浏览器访问 http://<电脑IP>:8123 即可试听
```

> 直接双击用 `file://` 打开也能跑，但系统语音列表可能读不出来，建议用 http 方式打开。

## 四、部署与在 OPPO 上安装

1. **部署到 HTTPS 静态托管**（PWA 安装必须 HTTPS）：任意静态托管均可，例如 GitHub Pages、腾讯云 COS、Cloudflare Pages、Netlify。
2. **OPPO 手机安装**（ColorOS 11 及以上，Chrome / OPPO 浏览器均可）：
   - 浏览器打开站点 → 右上角菜单 → **添加到主屏幕** 或 **安装应用**
   - 桌面出现本项目的秒表图标，点开即以全屏独立窗口运行，无地址栏
3. **首页「安装到桌面」按钮**：Chrome 触发安装条件时会显示，点击即可直接安装。

## 五、常见问题

| 现象 | 处理 |
| --- | --- |
| 人声列表为空 / 只有一项 | 手机「设置 → 系统 → 语言和输入法 → 文字转语音（TTS）」中确认已启用 TTS 引擎；OPPO 建议同时安装「Google 文字转语音」，可选人声会明显增多。装好后回应用点「刷新」 |
| 播报到一半停了 | ColorOS 会杀后台：设置 → 电池 → 应用耗电管理 → 找到浏览器 → 允许后台运行、关闭自动优化；同时开启应用内「保持屏幕常亮」并把页面留在前台 |
| 完全没声音 | 检查媒体音量；确认已联网（部分云端人声需联网）；点「试听」验证 |
| 想当独立 APK 分发 | 见下节 |

## 六、打包成独立 APK（可选）

如需脱离浏览器、以真 APK 分发，推荐用 Capacitor 包壳（WebView 内仍是同一套页面，语音能力由系统 WebView 提供）：

```bash
npm i -D @capacitor/cli @capacitor/core @capacitor/android
npx cap init "语音倒计时播报器" "cn.xxx.countdown" --web-dir=.
npx cap add android
npx cap copy android
npx cap open android     # 在 Android Studio 里 Build → Generate Signed APK
```

要点：

- `minSdkVersion` 建议 ≥ 26（OPPO 现役机型均满足）。
- 需要 `android.permission.VIBRATE`；Wake Lock 与 TTS 无需额外权限。
- 图标用 `assets/icons/` 下 PNG，通过 Android Studio 的 Image Asset 导入即可自动生成各分辨率。

Alternative：也可用 HBuilderX 直接「打包 → 原生 App 云打包」，把本项目文件作为本地 HTML 资源放入即可。
