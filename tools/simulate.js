/**
 * 无浏览器环境下仿真 index.html 的倒计时逻辑，校验播报时序。
 * 用法：node tools/simulate.js [总秒数]
 * 例：node tools/simulate.js 60
 */
const fs = require("fs");
const path = require("path");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("未找到内联脚本"); process.exit(1); }

/* ---------- DOM / BOM 桩 ---------- */
const spoken = [];
let tickFn = null;

function El(id) {
  const h = {};
  return {
    id, value: "", textContent: "", innerHTML: "", checked: false, disabled: false,
    dataset: {},
    style: {},
    classList: { add() {}, remove() {} },
    addEventListener(ev, fn) { (h[ev] = h[ev] || []).push(fn); },
    _fire(ev) { (h[ev] || []).forEach((f) => f.call(this, { preventDefault() {} })); },
    appendChild() {}, focus() {}, select() {},
    querySelector() { return null; },
    get _h() { return h; }
  };
}
const els = {};
["cmm","css","ccc","bar","sub","board","btnMain","btnReset","toast",
 "d0","d1","d2","d3","voice","btnTest","btnRefresh","rate","pitch","vol",
 "rateV","pitchV","volV","mode","endText","swStart","swBeep","swVib","swWake","installBtn"]
  .forEach((id) => (els[id] = El(id)));

global.window = global;
global.addEventListener = () => {};
global.document = {
  getElementById: (id) => els[id] || El(id),
  querySelectorAll: () => [],
  createElement: () => El("el"),
  addEventListener() {}
};
global.Option = function (text, value) { this.text = text; this.value = value; };
global.navigator = { vibrate() {} };
global.location = { protocol: "file:" };
global.localStorage = {
  _d: {},
  getItem(k) { return k in this._d ? this._d[k] : null; },
  setItem(k, v) { this._d[k] = String(v); }
};
global.speechSynthesis = {
  paused: false,
  getVoices: () => [],
  cancel() {}, resume() {}, speak(u) { spoken.push(u.text); }
};
global.SpeechSynthesisUtterance = function (t) { this.text = t; };
global.setInterval = (fn) => { tickFn = fn; return 1; };
global.clearInterval = () => { tickFn = null; };

let now = 1_000_000;
Date.now = () => now;

/* ---------- 载入应用 ---------- */
eval(m[1]);

/* ---------- 场景 ---------- */
const totalSec = parseInt(process.argv[2] || "60", 10);
els.d0.value = String(Math.floor(totalSec / 60 / 10) % 10);
els.d1.value = String(Math.floor(totalSec / 60) % 10);
els.d2.value = String(Math.floor((totalSec % 60) / 10));
els.d3.value = String((totalSec % 60) % 10);

els.btnMain._fire("click");                       // 开始
const step = 25;
for (let i = 0; i < (totalSec * 1000) / step + 20 && tickFn; i++) {
  now += step;
  tickFn();
}

console.log("设定总时长：", totalSec, "秒");
console.log("播报序列：", spoken.join(" → "));

/* ---------- 期望值校验 ---------- */
const expect = [];
expect.push(totalSec + "秒");                                   // 开始时播报一次（可关）
for (let t = Math.floor((totalSec - 1) / 10) * 10; t >= 10; t -= 10) expect.push(t + "秒");  // 10 秒节点
for (let t = (totalSec > 10 ? 9 : totalSec - 1); t >= 1; t--) expect.push(t + "秒");         // 整秒
expect.push("时间到");

const ok = spoken.length === expect.length && spoken.every((v, i) => v === expect[i]);
console.log("期望序列：", expect.join(" → "));
console.log(ok ? "✔ 时序一致" : "✘ 时序不一致");
process.exit(ok ? 0 : 1);
