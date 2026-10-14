async function runBmiComparison(casesOverride) {
  const url = 'https://www.hpa.gov.tw/Obesity/BmiCalculate.aspx';
  const cases = casesOverride || [
    ['N01', '170', '65'], ['N02', '160', '45'],
    ['N03', '180', '100'], ['N04', '150', '35'],
    ['B01', '200', '73.96'], ['B02', '200', '74'],
    ['B03', '200', '74.04'], ['B04', '200', '95.96'],
    ['B05', '200', '96'], ['B06', '200', '96.04'],
    ['B07', '200', '107.96'], ['B08', '200', '108'],
    ['B09', '200', '108.04'], ['B10', '200', '119.96'],
    ['B11', '200', '120'], ['B12', '200', '139.96'],
    ['B13', '200', '140'], ['R01', '170', '65'],
    ['R02', '170', '65'], ['R03', '170', '65'],
    ['S01', '170', '65', '0', '30'],
    ['S02', '170', '65', '1', '65'],
    ['I01', '0', '65'], ['I02', '170', '0'],
    ['I03', '-170', '65'], ['I04', '170', '-65'],
    ['I05', 'abc', '65'], ['I06', '170', 'abc'],
    ['I07', '', '65'], ['I08', '170', '']
  ];
  const state = { started: new Date().toISOString(), cases, records: [], mode: 'same-origin full-viewport iframe; native form button.click()' };
  window.bmiComparison = state;
  const frame = document.createElement('iframe');
  frame.title = 'BMI comparison measurement';
  frame.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;border:0;background:white;z-index:2147483647';
  document.body.appendChild(frame);
  const loaded = () => new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Frame navigation timeout after 15000 ms')), 15000);
    frame.addEventListener('load', () => {
      clearTimeout(timeout);
      setTimeout(resolve, 350);
    }, { once: true });
  });
  const capture = () => {
    const target = frame.contentWindow;
    return {
      timestamp: new Date().toISOString(), url: target.location.href,
      timeOrigin: target.performance.timeOrigin,
      navigation: target.performance.getEntriesByType('navigation').map(entry => entry.toJSON()),
      resources: target.performance.getEntriesByType('resource').map(entry => entry.toJSON()),
      paint: target.performance.getEntriesByType('paint').map(entry => entry.toJSON()),
      inlineScripts: [...target.document.scripts].filter(element => !element.src).map(element => element.textContent),
      text: target.document.body.innerText
    };
  };
  for (const [id, heightCm, weightKg, sex = '1', age = '30'] of cases) {
    state.current = id;
    let ready = loaded();
    frame.src = url;
    await ready;
    const target = frame.contentDocument;
    if (!target.getElementById('tbHeight')) throw new Error(`Input form missing for ${id}`);
    target.getElementById('ddlAge').value = age;
    target.getElementById(sex === '1' ? 'rdobSex_0' : 'rdobSex_1').checked = true;
    target.getElementById('tbHeight').value = heightCm;
    target.getElementById('tbWeight').value = weightKg;
    for (const name of ['ddlAge', 'tbHeight', 'tbWeight']) {
      const element = target.getElementById(name);
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));
    }
    const record = { id, heightCm, weightKg, sex, age, inputPage: capture() };
    ready = loaded();
    record.clickEpochMs = performance.timeOrigin + performance.now();
    target.getElementById('btnCal').click();
    await ready;
    record.result = capture();
    const navigation = record.result.navigation[0];
    record.result.clickToDomMs = record.result.timeOrigin + navigation.domContentLoadedEventEnd - record.clickEpochMs;
    record.result.clickToLoadMs = record.result.timeOrigin + navigation.loadEventEnd - record.clickEpochMs;
    state.records.push(record);
  }
  state.done = true;
  state.finished = new Date().toISOString();
  return state;
}
