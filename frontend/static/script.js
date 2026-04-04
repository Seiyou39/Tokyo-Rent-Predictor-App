const API_URL = '';

let clickCount = 0;
let clickTimer = null;

const translations = {
    en: {
        title: "Tokyo Rent Predictor",
        subtitle: "Estimate monthly rent for apartments across Tokyo using machine learning.",
        area: "Area (m²)", walk: "Walk to station (min)", age: "Building age (years)",
        floor: "Floor", total_floors: "Total floors", ward: "Ward", layout: "Layout",
        predict: "Predict rent", result: "Estimated monthly rent",
        select_ward: "Select ward", select_layout: "Select layout",
        fill_all: "Please fill in all fields",
        floor_error: "Floor cannot exceed total floors",
        connecting: "Predicting...",
        server_error: "Failed to connect to server. Make sure the API is running.",
        area_error: "Area must be between 10-200 m²",
        walk_error: "Walk time must be between 1-30 min",
        age_error: "Building age must be between 0-30 years",
        floor_error_range: "Floor must be between 1-50",
        total_floors_error_range: "Total floors must be between 1-50",
        description: "This project uses a linear regression model trained on 18,236 rental listings collected from SUUMO. The model estimates monthly rent based on features including ward, area, building age, walk time to station, floor, and layout type. Prediction error is typically within ±30,000 yen, with an R² of 0.81, explaining approximately 81% of rent variation.",
    },
    ja: {
        title: "東京家賃予測",
        subtitle: "機械学習を使って東京の賃貸物件の月額家賃を予測します。",
        area: "面積（m²）", walk: "駅徒歩（分）", age: "築年数",
        floor: "階数", total_floors: "総階数", ward: "地域", layout: "間取り",
        predict: "家賃を予測", result: "予測月額家賃",
        select_ward: "地域を選択", select_layout: "間取りを選択",
        fill_all: "すべての項目を入力してください",
        floor_error: "階数は総階数を超えられません",
        connecting: "予測中...",
        server_error: "サーバーに接続できません。APIが起動しているか確認してください。",
        area_error: "面積は10〜200m²の範囲で入力してください",
        walk_error: "徒歩時間は1〜30分の範囲で入力してください",
        age_error: "築年数は0〜30年の範囲で入力してください",
        floor_error_range: "階数は1〜50の範囲で入力してください",
        total_floors_error_range: "総階数は1〜50の範囲で入力してください",
        description: "本プロジェクトは線形回帰アルゴリズムに基づき、本人と同僚が収集したSUUMOの18,236件の物件データを用いて東京の家賃予測モデルを構築しました。エリア、面積、築年数、徒歩時間、階数、間取りなどの特徴量を組み合わせて家賃を推定します。予測誤差は概ね±3万円程度、モデルのR²は0.81で、家賃変動の約81%を説明できます。",
    },
    zh: {
        title: "东京房租预测",
        subtitle: "使用机器学习预测东京公寓的月租金。",
        area: "面积（m²）", walk: "步行到车站（分钟）", age: "房龄（年）",
        floor: "楼层", total_floors: "总楼层", ward: "地区", layout: "户型",
        predict: "预测房租", result: "预测月租金",
        select_ward: "选择地区", select_layout: "选择户型",
        fill_all: "请填写所有字段",
        floor_error: "楼层不能超过总楼层",
        connecting: "预测中...",
        server_error: "无法连接服务器，请确认API已启动。",
        area_error: "面积必须在10-200 m²之间",
        walk_error: "步行时间必须在1-30分钟之间",
        age_error: "房龄必须在0-30年之间",
        floor_error_range: "楼层必须在1-50之间",
        total_floors_error_range: "总楼层必须在1-50之间",
        description: "本项目基于线性回归算法，使用本人和好友们采集的 18,236 条 SUUMO 房源数据训练东京租金预测模型。模型结合区域、面积、房龄、步行时间、楼层和户型等特征，对房租进行估计，当前预测结果与实际房价的误差通常在 ±3 万日元左右。模型 R² 为 0.81，可解释约 81% 的租金变化。",
    }
};

let currentLang = 'ja';

function setLang(lang, e) {
    currentLang = lang;
    document.querySelectorAll('[data-key]').forEach(el => {
        el.textContent = translations[lang][el.dataset.key];
    });
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');
    const errorMsg = document.getElementById('errorMsg');
    if (errorMsg.style.display === 'block' && errorMsg.dataset.errorKey) {
        errorMsg.textContent = translations[lang][errorMsg.dataset.errorKey];
    }
}
 
async function predict() {

clickCount++;
clearTimeout(clickTimer);
clickTimer = setTimeout(() => { clickCount = 0; }, 3000);

if (clickCount >= 3) {
    clickCount = 0;
    const errorMsg = document.getElementById('errorMsg');
    const messages = {
        en: "Stop playing with the system! 😤",
        ja: "本システムで遊ばないでください！😤",
        zh: "不要再玩弄本系统啦！😤"
    };
    errorMsg.textContent = messages[currentLang];
    errorMsg.dataset.errorKey = '';
    errorMsg.style.display = 'block';
    return;
}


  const btn = document.getElementById('predictBtn');
  const errorMsg = document.getElementById('errorMsg');
  const resultCard = document.getElementById('resultCard');
  const resultValue = document.getElementById('resultValue');
 
  errorMsg.style.display = 'none';
  resultCard.classList.remove('visible');
 
  const area = document.getElementById('area').value;
  const walk = document.getElementById('walk').value;
  const age = document.getElementById('age').value;
  const floor = document.getElementById('floor').value;
  const total_floors = document.getElementById('total_floors').value;
  const location = document.getElementById('location').value;
  const layout = document.getElementById('layout').value;
 
  if (!area || !walk || !age || !floor || !total_floors || !location || !layout) {
    errorMsg.textContent = translations[currentLang].fill_all;
    errorMsg.dataset.errorKey = 'fill_all';
    errorMsg.style.display = 'block';
    return;
  }

  if (Number(area) < 10 || Number(area) > 200) {
    errorMsg.textContent = translations[currentLang].area_error;
    errorMsg.dataset.errorKey = 'area_error';
    errorMsg.style.display = 'block';
    return;
}
if (Number(walk) < 1 || Number(walk) > 30) {
    errorMsg.textContent = translations[currentLang].walk_error;
    errorMsg.dataset.errorKey = 'walk_error';
    errorMsg.style.display = 'block';
    return;
}
if (Number(age) < 0 || Number(age) > 30) {
    errorMsg.textContent = translations[currentLang].age_error;
    errorMsg.dataset.errorKey = 'age_error';
    errorMsg.style.display = 'block';
    return;
}
if (Number(total_floors) < 1 || Number(total_floors) > 50) {
    errorMsg.textContent = translations[currentLang].total_floors_error_range;
    errorMsg.dataset.errorKey = 'total_floors_error_range';
    errorMsg.style.display = 'block';
    return;
}
if (Number(floor) < 1 || Number(floor) > 50) {
    errorMsg.textContent = translations[currentLang].floor_error_range;
    errorMsg.dataset.errorKey = 'floor_error_range';
    errorMsg.style.display = 'block';
    return;
}
if (Number(floor) > Number(total_floors)) {
    errorMsg.textContent = translations[currentLang].floor_error;
    errorMsg.dataset.errorKey = 'floor_error';
    errorMsg.style.display = 'block';
    return;
}
 
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span>${translations[currentLang].connecting}`;
 
  try {
    const delay = new Promise(resolve => setTimeout(resolve, 500));
    const fetchPromise = fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        area: parseFloat(area),
        walk: parseFloat(walk),
        age: parseFloat(age),
        floor: parseFloat(floor),
        total_floors: parseFloat(total_floors),
        location: location,
        layout: layout
      })
    });
    const [response] = await Promise.all([fetchPromise, delay]);
    if (!response.ok) throw new Error('Prediction failed');
 
    const data = await response.json();
    const rent = Math.round(data.predicted_rent);
    resultValue.innerHTML = `¥${rent.toLocaleString()}<span class="result-unit">/month</span>`;
    resultCard.classList.add('visible');
  } catch (err) {
    errorMsg.textContent = translations[currentLang].server_error;
    errorMsg.dataset.errorKey = 'server_error';
    errorMsg.style.display = 'block';
    resultCard.classList.remove('visible');
  } finally {
    btn.disabled = false;
    btn.innerHTML = translations[currentLang].predict;
  }
}
 
document.querySelectorAll('input').forEach(input => {
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') predict();
  });
});


function sanitizeDecimalInput(raw, maxDecimals = 2) {
  let v = (raw ?? '').toString().normalize('NFKC');
  v = v.replace(/[。．，,]/g, '.'); 
  v = v.replace(/[^0-9.]/g, '');

  const firstDot = v.indexOf('.');
  if (firstDot !== -1) {
    v = v.slice(0, firstDot + 1) + v.slice(firstDot + 1).replace(/\./g, '');
  }

  const re = new RegExp(`^\\d*(?:\\.\\d{0,${maxDecimals}})?`);
  const m = v.match(re);
  return m ? m[0] : '';
}

function sanitizeIntegerInput(raw) {
  let v = (raw ?? '').toString().normalize('NFKC');
  v = v.replace(/[。．，,]/g, '.');
  v = v.split('.')[0];
  v = v.replace(/[^0-9]/g, '');
  return v;
}


const areaEl = document.getElementById('area');
if (areaEl) {
  areaEl.addEventListener('input', function () {
    this.value = sanitizeDecimalInput(this.value, 2);
  });
  areaEl.addEventListener('keydown', function (e) {

    if (['e', 'E', '-', '+'].includes(e.key)) e.preventDefault();
  });
}


['walk', 'age', 'floor', 'total_floors'].forEach((id) => {
  const el = document.getElementById(id);
  if (!el) return;

  el.addEventListener('keydown', (e) => {
    if (['.', ',', '。', '．', 'e', 'E', '-', '+'].includes(e.key)) {
      e.preventDefault();
    }
  });

  el.addEventListener('input', function () {
    this.value = sanitizeIntegerInput(this.value);
  });
});