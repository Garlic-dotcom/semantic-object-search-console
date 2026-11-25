'use strict';

(() => {
  const el = (id) => document.getElementById(id);
  const labels = {
    starting: '启动中', booting: '启动中', preflight: '启动检查', checking: '启动检查', simulation: '启动仿真',
    waiting_simulation: '等待传感器', navigation: '启动导航', waiting_navigation: '等待定位导航',
    perception: '启动感知', safety: '启动防碰撞', waiting_perception: '等待视觉数据', ready: '系统就绪', switching: '正在切换模式',
    running: '执行中', canceling: '正在停止', completed: '已完成', succeeded: '已完成',
    found: '已找到', passed: '检查通过', partial: '部分完成', failed: '失败', error: '异常',
    canceled: '已取消', stopped: '已停止', stopping: '正在关闭', shutdown: '已关闭',
    not_found: '未找到', no_sensor_data: '缺少感知数据', localization_failed: '定位失败',
    navigation_failed: '导航失败', navigation_rejected: '导航未就绪', timeout: '执行超时',
    idle: '空闲', pending: '等待启动', exited: '已退出', disabled: '未启用',
  };
  const componentLabels = {simulation: 'Gazebo', navigation: '导航', detector: '视觉检测', search: '搜索服务', rviz: 'RViz', slam: '实时建图', motion: '运动保护', safety: '防碰撞'};
  const categories = {cup: '杯子', bottle: '瓶子', chair: '椅子'};
  const rooms = {};
  let roomSignature = '';
  let catalogSignature = '';
  let memoryData = null;
  let memoryRequest = 0;
  let selectedMemoryId = null;
  let mapView = 'semantic';
  let memoryHitTargets = [];
  const objectColors = {cup:'#087f8c',bottle:'#346fca',chair:'#7972ab',bowl:'#bc6c25',
    apple:'#cd4d58',book:'#815bc0','sports ball':'#bc7a0c','cell phone':'#516473',
    orange:'#d77828',banana:'#9c861a',vase:'#a65f93'};
  const categoryColor = (category) => objectColors[category] || '#557684';
  const busyStates = new Set(['starting', 'running', 'canceling', 'queued', 'pending']);
  let state = null;
  let online = false;
  let mutationPending = false;
  let recording = null;
  let lastTranscriptId = null;
  const canRecord = Boolean(navigator.mediaDevices?.getUserMedia && window.MediaRecorder);
  let selectedHistoryId = null;
  let lastNotice = '';
  let mapData = null;
  let mapRaster = null;
  let mapUnavailable = false;
  let costmapData=null,costmapRaster=null,costmapReceived=0,costmapBusy=false,costmapSession=null;
  let mapExportSession=null;
  let zoom = 1;
  let historyKey = '';
  let taskKey = '';
  let logBusy = false;
  const canvas = el('map');
  const ctx = canvas.getContext('2d');

  const text = (id, value) => { el(id).textContent = value; };
  const finite = (n) => typeof n === 'number' && Number.isFinite(n);
  const statusLabel = (value) => labels[value] || value || '等待数据';
  const statusClass = (value) => {
    if (['ready', 'found', 'completed', 'succeeded', 'passed'].includes(value)) return 'good';
    if (['failed', 'error', 'no_sensor_data', 'localization_failed', 'navigation_failed', 'timeout'].includes(value)) return 'bad';
    if (['partial', 'canceling', 'starting', 'booting', 'running'].includes(value)) return 'warn';
    return 'neutral';
  };
  function badge(id, value, label) {
    const node = el(id);
    node.className = 'badge ' + statusClass(value);
    node.textContent = label || statusLabel(value);
  }
  function announce(message, error = false) {
    lastNotice = message;
    const node = el('notice');
    node.textContent = message;
    node.className = 'notice' + (error ? ' error' : '');
    node.hidden = !message;
  }
  async function api(path, body) {
    const options = {cache: 'no-store', signal: AbortSignal.timeout(12000)};
    if (body instanceof Blob) Object.assign(options, {method: 'POST', headers: {'Content-Type': 'application/octet-stream'}, body});
    else if (body !== undefined) Object.assign(options, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
    const response = await fetch(path, options);
    const value = await response.json();
    if (!response.ok) throw new Error(typeof value.error === 'string' ? value.error : value.message || `请求失败 (${response.status})`);
    return value;
  }
  function formatElapsed(seconds) {
    if (!finite(seconds)) return '—';
    seconds = Math.max(0, Math.floor(seconds));
    return seconds < 60 ? `${seconds} 秒` : `${Math.floor(seconds / 60)} 分 ${seconds % 60} 秒`;
  }
  function requestId() {
    if (crypto.randomUUID) return crypto.randomUUID();
    return Array.from(crypto.getRandomValues(new Uint8Array(16)), (x) => x.toString(16).padStart(2, '0')).join('');
  }
  function taskBusy() { return Boolean(state && (state.busy || state.task && busyStates.has(state.task.state))); }
  function taskCommand(task) {
    if (task.kind === 'validation') return '传感器检查';
    if (task.kind === 'return') return task.command || '返回充电处';
    const command = task.command;
    let structured = command;
    if (typeof command === 'string') {
      try { structured = JSON.parse(command); } catch { return command || '机器人任务'; }
    }
    if (structured?.mode === 'clean' && rooms[structured.room]) return `清扫${rooms[structured.room]}`;
    if (structured && typeof structured === 'object' && rooms[structured.room] && categories[structured.category] && ['find', 'count'].includes(structured.mode)) {
      return `去${rooms[structured.room]}${structured.mode === 'count' ? '统计' : '寻找'}${categories[structured.category]}`;
    }
    return typeof command === 'string' ? command : '机器人任务';
  }
  function refreshButtons() {
    const allowed = Boolean(online && state && state.ready && !taskBusy() && !mutationPending && !recording);
    const mapping = state?.mode === 'mapping';
    el('export-costmap').hidden = mapping || !state?.map_export_available;
    el('export-view-control').hidden=mapping || !state?.map_export_views;
    el('export-costmap').textContent=state?.map_export_views?'保存所选地图':'保存导航代价快照';
    if (mapExportSession && mapExportSession!==state?.session_id) {
      el('costmap-exports').replaceChildren();mapExportSession=null;
    }
    const motion = state?.telemetry?.mapping_motion;
    const cleaning = el('mode').value === 'clean';
    el('search-fields').hidden = mapping;
    el('mapping-fields').hidden = !mapping;
    el('category-field').hidden = cleaning;
    el('switch-mode').disabled = !allowed;
    text('switch-mode', mapping ? '返回导航' : '进入建图');
    text('robot-mode', mapping ? '建图模式' : '导航模式');
    text('map-title', mapping ? '实时建图' : '家庭地图');
    el('command').placeholder = mapping ? '例如：请前进' :
      cleaning ? '例如：请去健身区扫地' : '例如：去厨房找杯子';
    el('open-nearby-door').hidden = !state?.room_doors;
    el('save-mapping').disabled = !allowed || motion?.status==='moving';
    text('motion-status', motion?.message || '');
    document.querySelector('.region-controls').hidden = mapping;
    el('task-fields').disabled = !allowed;
    el('submit-task').disabled = !allowed;
    text('submit-task', mutationPending ? '正在提交…' : taskBusy() ? '任务执行中' : allowed ? '开始任务' : '等待系统就绪');
    el('cancel-task').disabled = !online || mutationPending;
    el('stop-from-page').disabled = el('cancel-task').disabled;
    el('stop-from-page').hidden = !(taskBusy() || recording || motion?.status === 'moving');
    el('validate').disabled = !allowed;
    el('return-to-dock').hidden = mapping || !state?.charging_station;
    el('return-to-dock').disabled = !allowed;
    el('dock-legend').hidden = mapping || !state?.charging_station;
    el('record-voice').disabled = recording ? !recording.recorder : !allowed || !canRecord || !state?.voice_available;
    text('record-voice', recording ? recording.recorder ? '结束录音' : '等待麦克风授权…' : '录音转写');
    text('task-help', recording ? '录音最长 8 秒。说完可提前结束。' : !online ? '连接已断开，无法提交任务。' :
      taskBusy() ? '完成或停止当前任务后，可开始下一条。' : allowed ?
        mapping ? '可用箭头键、按钮或语音短时移动。空格停车。' :
          canRecord && state.voice_available ? '可输入文字或录音，确认指令后开始任务。' : '语音不可用，可输入文字或选择目标。'
        : '正在等待当前模式就绪。');
  }
  function progressLabel(progress) {
    if (!progress) return '等待搜索节点接收任务。';
    if (progress.viewpoint_source === 'memory_safe_approach') {
      return progress.stage === 'navigating' ? '正在根据历史位置优先前往核验，物品尚未现场确认。' :
        progress.stage === 'observing' ? '正在现场核验历史线索，确认数量只来自本次观测。' : '正在核验历史线索。';
    }
    const position = progress.viewpoint_index ? `观察点 ${progress.viewpoint_index} / ${progress.viewpoints_total}` : '';
    const room = rooms[progress.room] || progress.room;
    if (progress.inspection_area) {
      if (progress.stage === 'navigating') return `正在前往${room}的${progress.inspection_area}巡视（${position}）。`;
      if (progress.stage === 'observing') return `正在巡视${room}的${progress.inspection_area}（${position}）。`;
    }
    if (progress.viewpoint_source === 'tentative_object_recheck') {
      if (progress.stage === 'navigating') return `发现待确认目标，正在${room}寻找更清晰的观察位置（${position}）。`;
      if (progress.stage === 'observing') return `正在${room}近距离核验目标（${position}）。`;
    }
    if (progress.viewpoint_source === 'measured_support_surface') {
      if (progress.stage === 'navigating') return `正在${room}靠近已观察到的桌面，检查小物品（${position}）。`;
      if (progress.stage === 'observing') return `正在${room}检查桌面细节（${position}）。`;
    }
    switch (progress.stage) {
      case 'navigating': return `正在前往${room}的${position}。`;
      case 'observing': return `正在${room}扫描（${position}）。`;
      case 'waiting_for_data': return `正在${room}等待相机与深度数据（${position}）。`;
      case 'canceling': return '正在取消导航，等待机器人停止。';
      case 'saving': return '正在保存任务结果和地图。';
      case 'finished': return '搜索已结束，正在核对结果文件。';
      default: return '正在执行搜索。';
    }
  }
  function cleaningProgress(progress) {
    switch (progress?.stage) {
      case 'entering': return `正在前往${rooms[progress.room] || progress.room}。`;
      case 'sweeping': return `正在清扫。已处理 ${progress.goals_finished} / ${progress.goals_total} 个路线点。`;
      case 'supplementing': return '正在补扫遗漏区域。';
      case 'returning': return state?.charging_station ? '正在返回充电处。' : '正在返回本次任务的起点。';
      default: return '正在核对起点、地面和清扫路线。';
    }
  }
  function healthRow(label, value, tone) {
    const li = document.createElement('li');
    const left = document.createElement('span'); left.textContent = label;
    const right = document.createElement('span'); right.textContent = value; right.className = 'status-label ' + tone;
    li.append(left, right);
    return li;
  }
  function renderHealth() {
    const telemetry = state.telemetry || {};
    const list = el('health'); list.replaceChildren();
    const mapping = state.mode === 'mapping';
    const checks = mapping ? [['建图与运动保护', telemetry.mapping_ready]] :
      [['定位与导航', telemetry.navigation_ready], ['视觉数据', telemetry.perception_ready]];
    for (const [name, ready] of [['仿真数据', telemetry.simulation_ready], ...checks]) {
      list.append(healthRow(name, ready ? '就绪' : '等待数据', ready ? 'good' : 'warn'));
    }
    if (state.components?.safety?.state !== 'disabled' && state.components?.safety) {
      const safety = telemetry.safety || {};
      const reasons = {scan_stale: '雷达数据过期', depth_stale: '深度数据过期', cloud_stale: '障碍数据过期',
        odom_stale: '里程计过期', odometry_tf_stale: '里程计变换过期', clock_stale: '仿真时钟停止',
        collision_monitor_inactive: '防碰撞未就绪'};
      const blocked = (safety.reasons || []).filter((name) => name !== 'command_stale');
      const label = safety.ready ? '就绪' : !safety.fresh ? '等待防护数据' :
        `已停车 · ${blocked.slice(0, 2).map((name) => reasons[name] || '等待数据').join('、')}`;
      list.append(healthRow('运动防护', label, safety.ready ? 'good' : 'warn'));
    }
    for (const [name, component] of Object.entries(state.components || {})) {
      if (!Object.hasOwn(componentLabels, name)) continue;
      if (state.phase === 'ready' && (mapping ? ['navigation', 'search'].includes(name) :
        ['slam', 'motion'].includes(name))) continue;
      const current = component.state || (component.returncode != null ? 'exited' : component.pid ? 'running' : 'pending');
      list.append(healthRow(componentLabels[name] || name, current === 'running' ? '运行中' : statusLabel(current), current === 'running' ? 'good' : ['failed', 'exited'].includes(current) && component.returncode ? 'bad' : 'neutral'));
    }
    el('system-dot').className = 'dot ' + (state.error ? 'bad' : state.ready ? 'good' : 'warn');
    el('system-dot').setAttribute('aria-label', state.error ? '系统异常' : state.ready ? '系统就绪' : '等待就绪');
    const topics = el('topics'); topics.replaceChildren();
    for (const [name, info] of Object.entries(telemetry.topics || {})) {
      const row = document.createElement('li');
      const topic = document.createElement('code'); topic.textContent = name;
      const status = document.createElement('span');
      status.className = 'status-label ' + (info.fresh ? 'good' : 'warn');
      status.textContent = info.messages ? info.fresh ? `已收 ${info.messages} 条` : finite(info.age_seconds) ? `${info.age_seconds.toFixed(1)} 秒前` : '数据过期' : '尚无数据';
      row.append(topic, status); topics.append(row);
    }
    if (!topics.children.length) topics.append(healthRow('传感器', '等待数据', 'neutral'));
  }
  function appendArtifacts(container, artifacts) {
    container.replaceChildren();
    for (const artifact of Array.isArray(artifacts) ? artifacts : []) {
      if (!artifact || typeof artifact.url !== 'string') continue;
      let url;
      try { url = new URL(artifact.url, location.href); } catch { continue; }
      if (url.origin !== location.origin || url.pathname !== '/api/artifact') continue;
      const link = document.createElement('a');
      link.href = url.href;
      link.textContent = artifact.name || artifact.kind || '查看文件';
      link.target = '_blank'; link.rel = 'noopener';
      container.append(link);
    }
  }
  function selectedTask() {
    return selectedHistoryId ? (state.history || []).find((row) => row.id === selectedHistoryId) || state.task : state.task;
  }
  function renderTask() {
    const task = selectedTask();
    const historical = Boolean(selectedHistoryId && task && task.id === selectedHistoryId);
    text('task-title', historical ? '历史任务' : '当前任务');
    el('show-current').hidden = !historical;
    const result = task && task.result;
    const validation = task && task.kind === 'validation';
    const voice = task && task.kind === 'voice';
    const cleaning = task?.kind === 'clean';
    const current = task ? task.state || 'running' : 'idle';
    badge('task-badge', current);
    text('active-command', task ? taskCommand(task) : '等待你的第一条指令');
    text('elapsed', task ? formatElapsed(task.elapsed_seconds) : '—');
    const progress = task && task.progress;
    const count = result?.count ?? progress?.count;
    const cleanCoverage = (result || progress)?.coverage;
    const fraction = cleanCoverage?.coverage_fraction;
    text('task-metric', cleaning ? '可清扫区域覆盖率' : '确认数量');
    text('count', cleaning ? finite(fraction) ? `${(fraction*100).toFixed(1)}%` : '—' :
      finite(count) ? String(count) : '—');
    const key = JSON.stringify([task && task.id, current, result, progress, task?.door_progress, task?.return, task && task.error, task && task.save_status, task && task.artifacts, historical]);
    if (taskKey === key) return;
    taskKey = key;
    let feedback = '选择房间和物品，系统就绪后即可开始。';
    if (task) {
      if (task.error) feedback = String(task.error);
      else if (current === 'canceling') feedback = '已请求停止，正在等待机器人确认。';
      else if (busyStates.has(current) && task.door_progress) {
        feedback = {approaching_door:'正在前往门口。', opening_door:'正在开门并等待关节反馈。',
          closing_door:'正在关门。', crossing_door:'门已打开，正在通过门洞。'}[task.door_progress.stage] || '正在准备门口通行。';
      }
      else if (busyStates.has(current) && task.return?.state==='running') feedback = '任务结果已保存，正在返回充电处。';
      else if (busyStates.has(current) && task.kind==='return') feedback = '正在返回充电处。';
      else if (busyStates.has(current)) feedback = validation ? '正在检查实际传感器数据和坐标变换。' :
        voice ? '正在离线转写录音。' :
        task.kind === 'motion' ? '正在执行运动指令。' :
        task.kind === 'map_save' ? '正在保存当前地图。' :
        cleaning ? cleaningProgress(progress) : progressLabel(progress);
      else if (validation) feedback = result ? result.passed ? '传感器检查通过。详细数据已记录在报告中。' : '传感器检查未通过，请查看报告与日志。' : statusLabel(current);
      else if (voice) feedback = result?.text ? `识别文本\n${result.text}` : statusLabel(current);
      else if (task.kind === 'motion' || task.kind === 'map_save' || task.kind==='door' || task.kind==='return' || cleaning) feedback = result?.message || statusLabel(current);
      else if (result) {
        const resultLabel = statusLabel(result.status || current);
        feedback = `${resultLabel}${finite(result.count) ? `，已确认 ${result.count} 个${categories[result.category] || result.category || '目标'}。` : '。'}`;
      } else feedback = statusLabel(current);
      if (!busyStates.has(current) && task.kind==='search' && !task.error && task.return?.return_state==='simulated_charging') {
        feedback += '\n已返回充电处并进入模拟充电。';
      }
      if (task.save_status === 'partial') feedback += '\n部分结果文件尚未完整保存，请查看日志。';
      if (task.save_status === 'missing') feedback += '\n未找到结果文件，请查看日志。';
      if (historical) feedback += '\n正在查看本次运行中的历史记录。';
    }
    if (task?.memory?.status === 'failed') feedback += ` ${task.memory.message}`;
    if (result?.memory_guidance?.used) feedback += '\n已参考历史位置安排现场核验，确认数量仅来自本次观测。';
    text('task-feedback', feedback);
    const coverage = cleaning ? cleanCoverage : result && result.coverage;
    el('coverage').hidden = !coverage;
    if (coverage && cleaning) {
      const target = result?.coverage_target;
      const spatial = (result || progress).spatial_coverage;
      const returnStatus = {simulated_charging:'模拟充电', return_incomplete:'停靠未达标', returning:'返航中',
        return_canceled:'已取消返航', not_attempted:'尚未返航'}[(result || progress).return_state];
      text('coverage', `已扫 ${coverage.covered_area_m2.toFixed(2)} m²，剩余 ${coverage.uncovered_cells} 格。` +
        (finite(target) ? `覆盖目标 ${Math.round(target*100)}%。` : '') +
        (spatial ? ` 已实扫条带 ${spatial.covered_lanes}/${spatial.planned_lanes}。` : '') +
        (returnStatus ? ` ${returnStatus}。` : ''));
    } else if (coverage) {
      const observed = coverage.viewpoints_observed;
      const total = result.viewpoints_total;
      const geometry = result.geometric_coverage;
      const detail = finite(geometry?.observed_fraction) ? `实测可见采样 ${(100*geometry.observed_fraction).toFixed(1)}%，补充 ${geometry.additional_views} 个观察点。` : '';
      const inspection = result.inspection_coverage;
      const areas = inspection?.required ? inspection.groups.map(group => `${group.name}：${group.completed ? '已巡视' : '未完成'}`).join('；') + '。' : '';
      text('coverage', `${areas}${finite(observed) && finite(total) ? `已完成观察 ${observed} / ${total}。` : ''}${detail}${coverage.full_room_coverage_verified === true ? '房间覆盖已验证。' : '数量来自已完成的有效观察，未确认全房覆盖。'}`);
    }
    const objects = el('objects'); objects.replaceChildren();
    for (const object of !validation && result && Array.isArray(result.objects) ? result.objects : []) {
      const row = document.createElement('div'); row.className = 'object-item';
      const id = object.id ?? object.object_id ?? '?';
      const xyz = ['x', 'y', 'z'].map((name) => finite(object[name]) ? object[name].toFixed(2) : '—').join(', ');
      row.textContent = `#${id} ${categories[object.category || result.category] || object.category || result.category || '物品'} · (${xyz}) m`;
      objects.append(row);
    }
    appendArtifacts(el('artifacts'), task && task.artifacts);
    el('result-details').hidden = !result;
    text('result-json', result ? JSON.stringify(result, null, 2) : '');
    drawMap();
  }
  function renderHistory() {
    const history = Array.isArray(state.history) ? state.history : [];
    text('history-count', `${history.length} 条`);
    const key = JSON.stringify(history.map((row) => [row.id, row.state, row.command, row.result && row.result.count]));
    if (key === historyKey) return;
    historyKey = key;
    const list = el('history'); list.replaceChildren();
    if (!history.length) {
      const row = document.createElement('li'); row.className = 'empty-row'; row.textContent = '完成的任务会显示在这里。'; list.append(row); return;
    }
    for (const task of history.slice(0, 20)) {
      const row = document.createElement('li'); const button = document.createElement('button');
      button.type = 'button'; button.className = 'history-item';
      const title = document.createElement('strong'); title.textContent = taskCommand(task);
      const meta = document.createElement('span'); meta.className = 'history-meta';
      meta.textContent = `${statusLabel(task.state)} · ${formatElapsed(task.elapsed_seconds)}${task.result && finite(task.result.count) ? ` · ${task.result.count} 个` : ''}`;
      button.append(title, meta);
      button.addEventListener('click', () => { selectedHistoryId = task.id; taskKey = ''; renderTask(); });
      row.append(button); list.append(row);
    }
  }
  function renderValidation() {
    const value = state.validation;
    if (!value) return;
    text('validation-state', busyStates.has(value.state) ? '正在检查传感器…' : value.error || (value.result && value.result.passed === true ? '最近一次传感器检查通过。' : value.result && value.result.passed === false ? '最近一次检查未通过，请查看报告。' : statusLabel(value.state)));
    appendArtifacts(el('validation-artifacts'), value.artifacts);
  }
  function renderRooms() {
    const definitions = state.rooms || {};
    const signature = JSON.stringify(definitions);
    if (signature === roomSignature) return;
    roomSignature = signature;
    const selected = el('room').value;
    const memoryRoom = el('memory-room').value;
    el('memory-room').replaceChildren(new Option('全部房间', ''));
    el('room').replaceChildren();
    for (const key of Object.keys(rooms)) delete rooms[key];
    for (const [id, room] of Object.entries(definitions)) {
      rooms[id] = room.display_name || (room.aliases || [id])[0];
      el('memory-room').append(new Option(rooms[id], id));
      const option = document.createElement('option'); option.value = id; option.textContent = rooms[id];
      el('room').append(option);
    }
    if (definitions[selected]) el('room').value = selected;
    if (definitions[memoryRoom]) el('memory-room').value = memoryRoom;
    taskKey = ''; historyKey = '';
  }
  function renderState() {
    renderCatalog();
    renderRooms();
    badge('connection', 'ready', '已连接');
    text('phase', statusLabel(state.phase));
    text('session', `会话 ${state.session_id || '—'}`);
    if (state.error && state.error !== lastNotice) announce(String(state.error), true);
    const task = state.task;
    if (task?.kind === 'voice' && task.state === 'completed' && task.id !== lastTranscriptId) {
      lastTranscriptId = task.id;
      el('command').value = task.result.text;
      announce('已填写识别文本。请检查或修改文字，再点击开始任务。');
    }
    renderHealth(); renderTask(); renderHistory(); renderValidation(); refreshButtons(); drawMap();
  }

  function renderCatalog() {
    const catalog = state.object_catalog;
    if (!Array.isArray(catalog)) return;
    const signature = JSON.stringify(catalog);
    if (signature === catalogSignature) return;
    catalogSignature = signature;
    const selected = el('category').value;
    const memoryCategory = el('memory-category').value;
    el('category').replaceChildren();
    el('memory-category').replaceChildren(new Option('全部物品', ''));
    for (const item of catalog) {
      categories[item.category] = item.name;
      const enabled = item.admitted || item.validation_enabled;
      const option = new Option(item.name + (item.admitted ? '' : item.validation_enabled ? '（验证中）' : '（待验证）'), item.category);
      option.disabled = !enabled;
      el('category').append(option);
      el('memory-category').append(new Option(item.name, item.category));
    }
    if (catalog.some((item) => item.category === selected && (item.admitted || item.validation_enabled))) el('category').value = selected;
    if (categories[memoryCategory]) el('memory-category').value = memoryCategory;
  }

  function renderMemory() {
    const items = el('memory-objects');
    const opened = new Set([...items.querySelectorAll('details[open]')].map(item => item.dataset.memoryId));
    items.replaceChildren();
    if (!memoryData?.objects?.some(item => item.id === selectedMemoryId)) selectedMemoryId = null;
    text('memory-status', memoryData?.message || '等待物品记忆。');
    text('memory-count', memoryData?.available ? `${memoryData.total} 条记录` : '暂不可用');
    el('memory-graph').hidden = !memoryData?.graph_available;
    if (!memoryData?.available) return;
    if (!memoryData.objects.length) {
      const empty = document.createElement('p'); empty.className = 'small muted';
      empty.textContent = '该范围还没有物品记忆。实际任务确认物品后会自动保存。'; items.append(empty);
    }
    for (const item of memoryData.objects) {
      const detail = document.createElement('details'); detail.className = 'object-item';
      detail.dataset.memoryId = item.id;
      detail.open = opened.has(item.id) || item.id === selectedMemoryId;
      detail.classList.toggle('memory-selected', item.id === selectedMemoryId);
      const summary = document.createElement('summary');
      const status = item.classification_conflict ? '类别或物品变化待核验' : item.state === 'needs_verification' ? '后续盘点未再确认' : '最后观测位置';
      const stamp = new Date(item.last_seen).toLocaleString('zh-CN',{hour12:false});
      const title=document.createElement('strong');title.textContent=categories[item.category] || item.category;
      const badge=document.createElement('span');badge.className='memory-state';badge.textContent=item.classification_conflict || item.state==='needs_verification' ? '待核验' : '历史观测';
      const subtitle=document.createElement('span');subtitle.className='memory-subtitle';
      subtitle.textContent=`${rooms[item.room] || item.room} · M-${item.id.slice(0,6)}${item.category_admitted === false ? ' · 类别验证中' : ''}`;
      summary.append(title,badge,subtitle);detail.style.borderLeftColor=categoryColor(item.category);
      const info = document.createElement('p'); info.className = 'small';
      info.textContent = `(${item.x.toFixed(2)}, ${item.y.toFixed(2)}, ${item.z.toFixed(2)}) m · ${stamp} · ${item.observation_tasks} 次任务观测。`;
      const evidence = document.createElement('p'); evidence.className = 'small muted';
      evidence.textContent = `任务 ${item.task_id}；证据 ${item.evidence}。` +
        (item.classification_conflict ? '同一历史位置出现不同类别；可能是误识或物品替换，尚未确定。' : '') +
        (item.association === 'ambiguous' ? '空间关联有歧义，记录身份待核验。' : '记录按空间位置关联，移动后的物理身份待核验。');
      const locate = document.createElement('button'); locate.type = 'button'; locate.className = 'text-button';
      locate.textContent = item.id === selectedMemoryId ? '已在地图选中' : '在地图查看最后位置';
      locate.setAttribute('aria-pressed', String(item.id === selectedMemoryId));
      locate.setAttribute('aria-controls', 'map');
      locate.disabled = !online || state?.mode === 'mapping' || !mapData ||
        memoryData.namespace !== mapData.memory_namespace || ![item.x, item.y].every(finite);
      locate.addEventListener('click', () => {
        selectedMemoryId = item.id; zoom = 1; el('show-memory').checked = true;
        renderMemory(); drawMap(); el('map-stage').scrollIntoView({block: 'nearest'});
      });
      const provenance=document.createElement('details');provenance.className='memory-provenance';
      const provenanceTitle=document.createElement('summary');provenanceTitle.textContent='观测依据与关联说明';
      provenance.append(provenanceTitle,evidence);
      detail.append(summary, info, locate, provenance); items.append(detail);
    }
    if (memoryData.truncated) {
      const note = document.createElement('p'); note.className = 'small muted';
      note.textContent = `已显示最近 ${memoryData.objects.length} 条，请按房间或类别缩小查询范围。`; items.append(note);
    }
  }

  function renderSemanticSummary() {
    const items=memoryData?.objects || [];
    const pending=items.filter(item => item.state==='needs_verification' || item.classification_conflict).length;
    const selected=state && selectedTask();
    const confirmed=selected?.kind==='search' ? selected.result?.count || 0 : 0;
    const box=el('semantic-summary');box.replaceChildren();box.hidden=mapView==='operation';
    for (const [number,label] of [[items.length,'历史观测记录'],[pending,'待核验记录'],[confirmed,'所选任务确认']]) {
      const item=document.createElement('div');const strong=document.createElement('strong');strong.textContent=number;
      const text=document.createElement('span');text.textContent=label;item.append(strong,text);box.append(item);
    }
  }

  function renderSemanticRelations() {
    const container=el('semantic-relations');container.replaceChildren();
    const note=document.createElement('p');note.className='relation-note';
    note.textContent='家庭 → 房间 → 物品记录 · 连线表示房间归属；历史位置需要现场核验。';container.append(note);
    if (!memoryData?.available) { note.textContent='等待同版地图与物品观测记录。';return; }
    const definitions=state?.rooms || {};const shown=(memoryData.objects || []).slice(0,40);
    const keys=Object.keys(definitions).filter(key => !el('memory-room').value || key===el('memory-room').value);
    const ns='http://www.w3.org/2000/svg';
    const svg=document.createElementNS(ns,'svg');
    const height=Math.max(410,keys.reduce((n,key)=>n+Math.max(76,shown.filter(item=>item.room===key).length*48),30));
    svg.setAttribute('viewBox',`0 0 860 ${height}`);svg.setAttribute('role','img');svg.setAttribute('aria-label','按实际观测记录生成的家庭、房间和物品关系');
    function element(tag,attributes,text) {
      const node=document.createElementNS(ns,tag);
      for (const [key,value] of Object.entries(attributes)) node.setAttribute(key,value);
      if (text!==undefined) node.textContent=text;svg.append(node);return node;
    }
    function edge(x1,y1,x2,y2,color) {
      element('path',{d:`M${x1},${y1} C${(x1+x2)/2},${y1} ${(x1+x2)/2},${y2} ${x2},${y2}`,fill:'none',stroke:color,'stroke-width':1.5});
    }
    const rootY=height/2;let top=24;
    for (const key of keys) {
      const items=shown.filter(item=>item.room===key);const block=Math.max(76,items.length*48);const y=top+block/2;
      const color=/^#[0-9a-f]{6}$/i.test(definitions[key].color || '') ? definitions[key].color : '#557684';
      edge(124,rootY,274,y,'#c7d6dc');
      element('rect',{x:274,y:y-22,width:158,height:44,rx:12,fill:color+'14',stroke:color});
      element('text',{x:290,y:y-2,fill:color,'font-size':14,'font-weight':600},rooms[key] || key);
      element('text',{x:290,y:y+14,fill:'#68808c','font-size':10},`${items.length} 条历史记录`);
      items.forEach((item,index)=>{
        const iy=top+24+index*48;const selected=item.id===selectedMemoryId;
        const pending=item.state==='needs_verification' || item.classification_conflict;
        edge(432,y,505,iy,pending ? '#c2a66e' : '#cbd9df');
        const rect=element('rect',{x:505,y:iy-19,width:308,height:38,rx:9,fill:selected ? '#e9f3f7' : '#fff',stroke:selected ? '#225d82' : '#dbe5e9','stroke-width':selected ? 2 : 1,tabindex:0,role:'button','aria-label':`查看${categories[item.category] || item.category}历史位置`});
        element('circle',{cx:522,cy:iy,r:5,fill:categoryColor(item.category)});
        const label=element('text',{x:537,y:iy+5,fill:'#294b5b','font-size':13},`${categories[item.category] || item.category} · M-${item.id.slice(0,6)}${pending ? ' · 待核验' : ''}`);
        label.style.pointerEvents='none';
        function select() { selectedMemoryId=item.id;renderMemory();renderSemanticRelations(); }
        rect.addEventListener('click',select);rect.addEventListener('keydown',event=>{if (['Enter',' '].includes(event.key)) {event.preventDefault();select();}});
      });
      top+=block;
    }
    element('rect',{x:18,y:rootY-30,width:106,height:60,rx:16,fill:'#153c4c'});
    element('text',{x:71,y:rootY+6,fill:'#fff','font-size':18,'text-anchor':'middle','font-weight':600},'家庭');
    container.append(svg);
    if ((memoryData.objects || []).length>shown.length) {
      const limit=document.createElement('p');limit.className='relation-note';limit.textContent='当前展示前40条记录，请按房间或类别筛选查看其余记录。';container.append(limit);
    }
  }

  async function refreshMemory() {
    const request = ++memoryRequest;
    const query = new URLSearchParams();
    if (el('memory-room').value) query.set('room', el('memory-room').value);
    if (el('memory-category').value) query.set('category', el('memory-category').value);
    try {
      const value = await api('/api/memory?' + query);
      if (request !== memoryRequest) return;
      memoryData = value;
    } catch (error) {
      if (request !== memoryRequest) return;
      memoryData = {available: false, objects: [], message: `物品记忆读取失败：${error.message}`};
    }
    renderMemory(); drawMap();
  }

  async function pollMemory() {
    await refreshMemory();
    setTimeout(pollMemory, 5000);
  }

  function setMap(value) {
    if (!value || !value.available) { mapUnavailable = true; drawMap(); return; }
    const {width, height, resolution, data} = value;
    if (!Number.isInteger(width) || !Number.isInteger(height) || width < 1 || height < 1 || width * height > 16000000 || !finite(resolution) || resolution <= 0 || !Array.isArray(data) || data.length !== width * height) return;
    const origin = value.origin || {};
    if (![origin.x, origin.y, origin.yaw].every(finite)) return;
    mapUnavailable = false;
    mapData = value;
    mapRaster = document.createElement('canvas'); mapRaster.width = width; mapRaster.height = height;
    const rasterContext = mapRaster.getContext('2d');
    const pixels = rasterContext.createImageData(width, height);
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const occupancy = data[y * width + x];
        const index = ((height - 1 - y) * width + x) * 4;
        const color = occupancy < 0 ? [219, 228, 231] : occupancy >= 65 ? [61, 82, 94] : occupancy === 0 ? [250, 252, 252] : [250 - Math.round(occupancy * 1.6), 252 - Math.round(occupancy * 1.5), 252 - Math.round(occupancy * 1.4)];
        pixels.data[index] = color[0]; pixels.data[index + 1] = color[1]; pixels.data[index + 2] = color[2]; pixels.data[index + 3] = 255;
      }
    }
    rasterContext.putImageData(pixels, 0, 0);
    el('map-empty').hidden = true;
    text('map-meta', `${value.frame_id || 'map'} · ${resolution.toFixed(2)} m / 栅格 · ${(width * resolution).toFixed(1)} × ${(height * resolution).toFixed(1)} m`);
    drawMap();
  }
  function renderObstacle() {
    const observation=state?.telemetry?.obstacle;
    const fresh=online && observation?.fresh && observation?.motion_fresh;
    const labels={near_moving:'近障 · 正在移动',near_stopped:'近障 · 速度接近零',moving:'正在移动',stationary:'当前静止',stale:'数据过期'};
    const near=fresh && observation.state.startsWith('near_');
    document.querySelector('.avoidance-panel').dataset.state=!fresh?'stale':near?'near':'observing';
    text('obstacle-heading',!fresh?'等待有效观测':near?'检测到近距离障碍':observation.state==='moving'?'机器人正在行进':'机器人当前静止');
    text('obstacle-symbol',near?'!':'⌖');
    badge('obstacle-badge',!fresh?'neutral':near?'partial':'ready',!fresh?'等待有效数据':labels[observation.state]);
    const closest=fresh && observation.nearest;
    text('obstacle-sector',fresh?`${observation.sector}最近障碍`:'当前方向最近障碍');
    text('obstacle-distance',closest?`${closest.distance_m.toFixed(2)} m`:'— m');
    text('obstacle-bearing',closest?`方位 ${closest.bearing_degrees.toFixed(0)}°`:'方位 —');
    text('obstacle-speed',fresh && observation.velocity?`${Math.abs(observation.velocity[0]).toFixed(2)} m/s`:'— m/s');
    text('obstacle-turn',fresh && observation.velocity?`转速 ${Math.abs(observation.velocity[1]).toFixed(2)} rad/s`:'转速 — rad/s');
    text('obstacle-note',!fresh?'观测不可用或已过期；不据此判断安全。':near?'检测到近距离障碍。请结合规划路径、实际运动和任务结果判断避障完成情况。':'距离从机器人中心计算；激光只反映当前可见障碍，低矮/悬空障碍还依赖深度与导航。');
    const list=el('obstacle-events');list.replaceChildren();
    const events=observation?.events || [];
    for (const event of events.slice(-5).reverse()) {
      const item=document.createElement('li');
      item.textContent=`${event.stamp_seconds?.toFixed(1) || '—'}s · ${labels[event.state] || event.state}${finite(event.distance_m)?` · ${event.sector} ${event.distance_m.toFixed(2)}m / ${event.bearing_degrees.toFixed(0)}°`:''}`;
      list.append(item);
    }
    if (!events.length){const item=document.createElement('li');item.textContent='暂无近障变化记录';list.append(item);}
  }
  function drawMap() {
    memoryHitTargets=[];
    renderObstacle();
    if (el('map-card').closest('[data-console-page]').hidden) return;
    renderSemanticSummary();
    const relations=mapView==='relations';canvas.hidden=relations;el('semantic-relations').hidden=!relations;
    el('zoom-in').disabled=relations;el('zoom-out').disabled=relations;el('fit-map').disabled=relations;
    if (relations) {el('map-empty').hidden=true;renderSemanticRelations();return;}
    const bounds = canvas.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    if (canvas.width !== Math.floor(bounds.width * ratio) || canvas.height !== Math.floor(bounds.height * ratio)) {
      canvas.width = Math.floor(bounds.width * ratio); canvas.height = Math.floor(bounds.height * ratio);
    }
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0); ctx.clearRect(0, 0, bounds.width, bounds.height);
    if (!mapData || !mapRaster) return;
    const scale = Math.min((bounds.width - 40) / mapData.width, (bounds.height - 40) / mapData.height) * zoom;
    const offsetX = (bounds.width - mapData.width * scale) / 2;
    const offsetY = (bounds.height - mapData.height * scale) / 2;
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(mapRaster, offsetX, offsetY, mapData.width * scale, mapData.height * scale);
    const origin = mapData.origin;
    const c = Math.cos(origin.yaw), s = Math.sin(origin.yaw);
    function project(x, y) {
      const dx = x - origin.x, dy = y - origin.y;
      return [offsetX + (c * dx + s * dy) / mapData.resolution * scale, offsetY + (mapData.height - (-s * dx + c * dy) / mapData.resolution) * scale];
    }
    const showCost=el('map-layer').value==='cost';el('costmap-legend').hidden=!showCost;
    if (costmapSession && costmapSession!==state?.session_id) {costmapData=null;costmapRaster=null;}
    // 1Hz native update/publication plus 1Hz HTTP polling can legitimately
    // exceed 2.5s between paints. This is a display lease, not navigation safety.
    const costFresh=online && costmapData?.fresh && Date.now()-costmapReceived<4000 &&
      finite(state?.telemetry?.clock_seconds) && state.telemetry.clock_seconds-costmapData.stamp_seconds<=4 &&
      state.telemetry.clock_seconds-costmapData.stamp_seconds>=-.1;
    if (showCost && state?.mode!=='mapping' && costmapRaster && costmapData.frame_id===mapData.frame_id) {
      const layer=costmapData,zero=project(layer.origin.x,layer.origin.y);
      const angle=layer.origin.yaw-origin.yaw;
      const layerScale=layer.resolution/mapData.resolution*scale;
      ctx.save();ctx.globalAlpha=costFresh?1:.35;ctx.translate(...zero);ctx.rotate(-angle);
      ctx.drawImage(costmapRaster,0,-layer.height*layerScale,layer.width*layerScale,layer.height*layerScale);ctx.restore();
      text('costmap-state',costFresh?'全局导航代价 · 实时更新':'上次导航代价（已过期）');
    } else text('costmap-state',showCost?'代价图不可用或已过期，当前仅显示底图':'共用同一张栅格底图');
    if (state && state.rooms_frame_id === mapData.frame_id) {
      const definitions = state.rooms || {};
      if (state.mode!=='mapping' && el('show-regions').checked) for (const [id, room] of Object.entries(definitions)) {
        if (!Array.isArray(room.polygon) || room.polygon.length < 3) continue;
        const color = /^#[0-9a-f]{6}$/i.test(room.color || '') ? room.color : '#147d76';
        ctx.save(); ctx.beginPath();
        room.polygon.forEach((point, index) => {
          const p = project(point[0], point[1]);
          if (index === 0) ctx.moveTo(...p); else ctx.lineTo(...p);
        });
        ctx.closePath(); ctx.fillStyle = color; ctx.globalAlpha = .08; ctx.fill();
        ctx.globalAlpha = .9; ctx.strokeStyle = color; ctx.lineWidth = id === el('room').value ? 2.5 : 1.4; ctx.stroke();
        const label = room.label_position;
        if (Array.isArray(label) && label.every(finite)) {
          const p = project(...label); const name = rooms[id] || id;
          ctx.font = 'bold 13px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          const width = ctx.measureText(name).width + 12;
          ctx.globalAlpha = .94; ctx.fillStyle = '#ffffff'; ctx.fillRect(p[0]-width/2,p[1]-11,width,22);
          ctx.globalAlpha = 1; ctx.fillStyle = color; ctx.fillText(name,...p);
        }
        ctx.restore();
      }
      const currentTask=state.task;
      const taskData=currentTask?.kind==='search'?(currentTask.progress?.room ? currentTask.progress : currentTask.result):null;
      const roomId=state.busy && taskData?.room ? taskData.room:el('room').value;
      const category=state.busy && taskData?.category ? taskData.category:el('category').value;
      const room = definitions[roomId];
      el('view-note').hidden=!el('show-views').checked;
      if (state.mode!=='mapping' && room && el('show-views').checked) {
        const route=[...Object.values(room.inspection_views || {}).flat(),...((room.category_views || {})[category] || room.views || [])];
        const seen=new Set();const views=route.filter(p=>{const key=JSON.stringify(p);if(seen.has(key))return false;seen.add(key);return true;});
        const relevant=taskData?.room===roomId && taskData?.category===category;
        const diagnostics=relevant ? currentTask.result?.viewpoint_diagnostics || []:[];
        const progress=relevant && currentTask.progress?.kind==='search' ? currentTask.progress:null;
        const current=progress && ['navigating','observing'].includes(progress.stage)?views[(progress.viewpoint_index || 1)-1]:null;
        const same=(a,b)=>a && b && Math.hypot(a[0]-b[0],a[1]-b[1])<.001 && Math.abs(Math.atan2(Math.sin(a[2]-b[2]),Math.cos(a[2]-b[2])))<.00001;
        text('view-note',`${rooms[roomId] || roomId} · ${categories[category] || category}：预设巡视点，非实时检测位置；绿=已观察，橙=当前目标，灰=预设。`);
        const positions = new Map();
        views.forEach((view, index) => {
          const key = `${view[0].toFixed(3)},${view[1].toFixed(3)}`;
          if (!positions.has(key)) positions.set(key, []);
          positions.get(key).push({view,index});
        });
        canvas.dataset.observationPositions=String(positions.size);
        canvas.dataset.observationTargets=String(views.length);
        positions.forEach((directions) => {
          const {view,index} = directions[0];
          const [x,y] = project(view[0],view[1]);
          const completed=p=>diagnostics.some(d=>d.reached && d.dwell_completed && same(d.pose,p)) ||
            (progress?.viewpoints_failed===0 && views.findIndex(v=>same(v,p))>=0 &&
             views.findIndex(v=>same(v,p))<(progress.viewpoint_index || 1)-1);
          const active=directions.some(d=>same(d.view,current));
          const color=active?'#d47a19':directions.every(d=>completed(d.view))?'#16847d':'#5c7180';
          ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = '#ffffff'; ctx.lineWidth = active?2.5:1.5;
          ctx.beginPath(); ctx.arc(x,y,7,0,2*Math.PI); ctx.fill(); ctx.stroke();
          directions.forEach(({view: pose}) => {
            ctx.strokeStyle=same(pose,current)?'#d47a19':completed(pose)?'#16847d':'#5c7180';
            const angle = -(pose[2]-origin.yaw);
            ctx.beginPath(); ctx.moveTo(x,y); ctx.lineTo(x+17*Math.cos(angle),y+17*Math.sin(angle)); ctx.stroke();
          });
          ctx.font='bold 11px sans-serif'; ctx.fillStyle=color;
          const observedCount=directions.filter(d=>completed(d.view)).length;
          ctx.fillText(`P${index+1}${directions.length>1?' · '+observedCount+'/'+directions.length+'朝向':observedCount?' ✓':''}`,x+9,y-18); ctx.restore();
        });
      }
    }
    const task = state && selectedTask();
    const clean = state?.mode!=='mapping' && (task?.kind==='clean' ? (task.result || task.progress) :
      task?.kind==='return' ? (task.result || task.progress) : task?.return ? (task.progress || task.return) : null);
    if (clean?.frame_id === mapData.frame_id && clean.trace_preview?.length) {
      ctx.save();
      ctx.lineWidth = 2.8;
      ctx.lineCap = 'round';
      let previous = null;
      for (const [x,y,stage,connected] of clean.trace_preview) {
        const point = project(x,y);
        if (previous && connected) {
          ctx.beginPath();
          ctx.strokeStyle = stage === 'returning' ? '#6366a2' :
            ['sweeping','supplementing'].includes(stage) ? '#16847d' : '#738a98';
          ctx.moveTo(...previous);
          ctx.lineTo(...point);
          ctx.stroke();
        }
        previous = point;
      }
      ctx.restore();
    }
    const dock = state?.mode!=='mapping' && state?.charging_station;
    if (dock?.frame_id===mapData.frame_id && Array.isArray(dock.map_pose)) {
      const [x,y]=project(dock.map_pose[0],dock.map_pose[1]);
      ctx.save();ctx.fillStyle='#7755a2';ctx.strokeStyle='#fff';ctx.lineWidth=2;
      ctx.fillRect(x-8,y-8,16,16);ctx.strokeRect(x-8,y-8,16,16);
      ctx.fillStyle='#513872';ctx.font='bold 12px sans-serif';ctx.fillText('充电处',x+12,y-9);ctx.restore();
    }
    if (online && el('show-obstacles').checked) {
      const obstacle=state?.telemetry?.obstacle;
      const path=state?.telemetry?.navigation_path;
      ctx.save();
      if (state?.busy && path?.fresh && path.frame_id===mapData.frame_id && path.points?.length>1) {
        ctx.beginPath();ctx.strokeStyle='#3282c4';ctx.lineWidth=2;ctx.setLineDash([6,4]);
        path.points.forEach(([x,y],i)=>{const point=project(x,y);if(i===0)ctx.moveTo(...point);else ctx.lineTo(...point);});ctx.stroke();ctx.setLineDash([]);
      }
      if (obstacle?.fresh && obstacle.frame_id===mapData.frame_id) {
        ctx.fillStyle='#df8b28';ctx.globalAlpha=.8;
        for (const point of obstacle.points || []) {const [x,y]=project(...point);ctx.beginPath();ctx.arc(x,y,2,0,2*Math.PI);ctx.fill();}
        const near=obstacle.nearest;
        if (near?.map_xy && near.distance_m<=obstacle.near_threshold_m) {
          const [x,y]=project(...near.map_xy);ctx.globalAlpha=1;ctx.strokeStyle='#c86315';ctx.lineWidth=2;
          ctx.beginPath();ctx.arc(x,y,8,0,2*Math.PI);ctx.stroke();ctx.fillStyle='#a54c09';ctx.font='bold 12px sans-serif';ctx.fillText(`${near.distance_m.toFixed(2)}m`,x+11,y-10);
        }
      }
      ctx.restore();
    }
    const pose = state && state.telemetry && state.telemetry.pose;
    const poseFresh = online && pose && pose.fresh !== false && state.telemetry.pose_fresh !== false;
    if (pose && finite(pose.x) && finite(pose.y) && finite(pose.yaw) && (!pose.frame_id || pose.frame_id === mapData.frame_id)) {
      const [x, y] = project(pose.x, pose.y);
      const heading = -(pose.yaw - origin.yaw);
      ctx.save(); ctx.translate(x, y); ctx.rotate(heading);
      ctx.fillStyle = poseFresh ? '#147d76' : '#81969c'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(0, 0, 10, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(7, 0); ctx.lineTo(-3, -4); ctx.lineTo(-3, 4); ctx.closePath(); ctx.fill(); ctx.restore();
      text('pose', `${poseFresh ? '' : '上次位置 · '}x ${pose.x.toFixed(2)} / y ${pose.y.toFixed(2)} m`);
    } else text('pose', '位置等待定位');
    const semantic=mapView==='semantic';
    const result = state?.mode!=='mapping' && task && task.kind === 'search' && task.result;
    const objects = result && Array.isArray(result.objects) ? result.objects : [];
    const labelBoxes=[];
    function semanticLabel(label,x,y,color,force=false) {
      ctx.font='600 11px system-ui';const width=ctx.measureText(label).width+12;const height=19;
      let box=null;
      for (const [dx,dy] of [[13,-25],[13,9],[-width-13,-25],[-width-13,9],[13,-50],[13,34],[-width/2,-70]]) {
        const b={x:x+dx,y:y+dy,w:width,h:height};
        if (b.x<2 || b.y<2 || b.x+b.w>bounds.width-2 || b.y+b.h>bounds.height-2) continue;
        if (labelBoxes.every(a=>b.x>a.x+a.w+4 || b.x+b.w+4<a.x || b.y>a.y+a.h+4 || b.y+b.h+4<a.y)) {box=b;break;}
      }
      if (!box && !force) return;
      box ||= {x:x-width/2,y:y+17,w:width,h:height};labelBoxes.push(box);
      ctx.strokeStyle=color;ctx.lineWidth=.7;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(box.x+box.w/2,box.y+box.h/2);ctx.stroke();
      ctx.fillStyle='#ffffffed';ctx.fillRect(box.x,box.y,box.w,box.h);ctx.fillStyle=color;ctx.textAlign='left';ctx.fillText(label,box.x+6,box.y+13);
    }
    if (semantic && online && state?.mode !== 'mapping' && el('show-memory').checked && memoryData?.available &&
        memoryData.namespace === mapData.memory_namespace) for (const item of [...memoryData.objects].sort((a,b)=>Number(b.id===selectedMemoryId)-Number(a.id===selectedMemoryId))) {
      if (result && item.task_id===result.task_id && item.category===result.category) continue;
      const [x, y] = project(item.x, item.y);
      const selected = item.id === selectedMemoryId;
      memoryHitTargets.push({x,y,id:item.id});
      ctx.strokeStyle = item.classification_conflict || item.state === 'needs_verification' ? '#986b20' : categoryColor(item.category);
      ctx.lineWidth = selected ? 3 : 1.8; ctx.setLineDash([3, 2]);
      ctx.beginPath(); ctx.arc(x, y, selected ? 14 : 9, 0, Math.PI * 2); ctx.stroke(); ctx.setLineDash([]);
      semanticLabel(`${categories[item.category] || item.category} · M-${item.id.slice(0,4)}`,x,y,ctx.strokeStyle,selected);
    }
    for (const object of objects) {
      if (!finite(object.x) || !finite(object.y)) continue;
      if (result.frame_id && result.frame_id !== mapData.frame_id) continue;
      const [x, y] = project(object.x, object.y);
      const id = String(object.id ?? object.object_id ?? '?');
      ctx.fillStyle = semantic ? categoryColor(result.category) : '#d38b23'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(x, y, 7, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.font = '600 11px system-ui'; ctx.textAlign = 'center';
      const label = `#${id}`;
      const width = ctx.measureText(label).width + 12;
      ctx.fillStyle = '#fff'; ctx.fillRect(x - width / 2, y - 29, width, 18);
      ctx.fillStyle = '#8b601b'; ctx.fillText(label, x, y - 16);
    }
    text('map-result-context', clean ? '实际轨迹 · 灰色前往房间 · 绿色清扫 · 紫色返航' :
      result ? `${selectedHistoryId ? '历史' : '当前'}任务结果：${objects.length} 个已确认物品标记。机器人图标为最新可用定位。` : '物品标记将在任务结果返回后显示。');
    el('map-stale').hidden = online && !mapData.stale && !mapUnavailable;
    text('map-stale', !online ? '连接中断 · 显示最后收到的地图' : mapUnavailable ? '地图暂不可用 · 显示最后收到的地图' : '地图数据已过期');
  }

  async function pollState() {
    try { state = await api('/api/state'); online = true; renderState(); }
    catch (error) {
      online = false; badge('connection', 'error', '连接中断'); text('phase', '检查启动终端与服务状态');
      el('system-dot').className = 'dot bad'; refreshButtons(); drawMap();
    }
    setTimeout(pollState, 1000);
  }
  async function pollMap() {
    try { setMap(await api('/api/map')); } catch { mapUnavailable = true; drawMap(); }
    setTimeout(pollMap, 3000);
  }
  async function pollCostmap() {
    if (costmapBusy) return;
    if (el('map-layer').value!=='cost' || state?.mode==='mapping') {setTimeout(pollCostmap,1000);return;}
    costmapBusy=true;
    try {
      const value=await api('/api/costmap');
      if (value.available && value.fresh && Number.isInteger(value.width) && value.width>0 && Number.isInteger(value.height) && value.height>0 &&
          value.width*value.height<=16000000 && finite(value.resolution) && value.resolution>0 &&
          [value.origin?.x,value.origin?.y,value.origin?.yaw].every(finite) && Array.isArray(value.data) && value.data.length===value.width*value.height) {
        const raster=document.createElement('canvas');raster.width=value.width;raster.height=value.height;
        const context=raster.getContext('2d'),pixels=context.createImageData(value.width,value.height);
        for(let y=0;y<value.height;y++)for(let x=0;x<value.width;x++) {
          const cost=value.data[y*value.width+x],i=((value.height-1-y)*value.width+x)*4;
          const color=cost<0?[111,125,139,100]:cost===100?[207,47,52,220]:cost===99?[229,115,32,200]:cost>0?[245,177,50,Math.round(35+cost*1.1)]:[0,0,0,0];
          pixels.data.set(color,i);
        }
        context.putImageData(pixels,0,0);
        costmapData=value;costmapReceived=Date.now();costmapRaster=raster;costmapSession=state?.session_id;
      }
    } catch { /* Keep last valid frame, visibly stale when its display lease expires. */ }
    finally {costmapBusy=false;drawMap();setTimeout(pollCostmap,1000);}
  }
  async function refreshLog() {
    if (logBusy) return;
    logBusy = true;
    try {
      const output = await api(`/api/log?component=${encodeURIComponent(el('log-component').value)}`);
      const target = el('log-output');
      const nearEnd = target.scrollHeight - target.scrollTop - target.clientHeight < 35;
      target.textContent = output.text || '该组件暂时没有日志。';
      if (nearEnd) target.scrollTop = target.scrollHeight;
    } catch (error) { text('log-output', `日志读取失败：${error.message}`); }
    finally { logBusy = false; }
  }
  async function mutate(path, body, message) {
    if (mutationPending) return;
    mutationPending = true; refreshButtons();
    try {
      await api(path, body);
      selectedHistoryId = null; taskKey = ''; announce(message);
      state = await api('/api/state'); online = true; renderState();
    } catch (error) { announce(error.message, true); }
    finally { mutationPending = false; refreshButtons(); }
  }
  function stopRecording(discard = false) {
    const active = recording;
    if (!active) return;
    active.discard ||= discard;
    clearTimeout(active.timer);
    if (active.recorder?.state === 'recording') active.recorder.stop();
    else if (!active.recorder) {
      recording = null;
      refreshButtons();
    }
  }
  async function recordVoice() {
    if (recording) { stopRecording(); return; }
    if (!canRecord || !state?.voice_available || !state.ready || mutationPending || !online) return;
    const active = {discard: false};
    recording = active;
    refreshButtons();
    try {
      active.stream = await navigator.mediaDevices.getUserMedia({audio: true});
      if (active.discard) { active.stream.getTracks().forEach((track) => track.stop()); return; }
      const recorder = new MediaRecorder(active.stream, {audioBitsPerSecond: 32000});
      active.recorder = recorder;
      const chunks = [];
      recorder.addEventListener('dataavailable', (event) => chunks.push(event.data));
      recorder.addEventListener('error', () => {
        active.discard = true;
        announce('录音失败，请检查麦克风。', true);
      });
      recorder.addEventListener('stop', async () => {
        clearTimeout(active.timer);
        active.stream.getTracks().forEach((track) => track.stop());
        recording = null;
        if (!active.discard) {
          const audio = new Blob(chunks);
          if (audio.size) await mutate('/api/transcribe', audio, '已提交录音，正在离线转写。');
          else announce('录音为空，请重试。', true);
        }
        refreshButtons();
      }, {once: true});
      recorder.start();
      active.timer = setTimeout(() => stopRecording(), 8000);
      refreshButtons();
    } catch (error) {
      active.stream?.getTracks().forEach((track) => track.stop());
      if (recording === active) {
        recording = null;
        announce('无法录音，请检查浏览器权限和麦克风。', true);
        refreshButtons();
      }
    }
  }
  el('task-form').addEventListener('submit', (event) => {
    event.preventDefault();
    if (!state || !state.ready || taskBusy() || mutationPending || !online || recording) return;
    const command = el('command').value.trim();
    if (state.mode==='mapping' && !command) {
      announce('请输入运动指令，或点击方向按钮。', true);
      return;
    }
    const body = command ? {command, request_id: requestId()} :
      {mode: el('mode').value, room: el('room').value, request_id: requestId()};
    if (!command && body.mode !== 'clean') body.category = el('category').value;
    mutate('/api/task', body, '任务已提交，执行状态将在右侧更新。');
  });
  el('mode').addEventListener('change', refreshButtons);
  el('switch-mode').addEventListener('click', () => {
    const mode = state?.mode==='mapping' ? 'navigation' : 'mapping';
    el('command').value = '';
    mutate('/api/mode', {mode}, '正在切换模式。');
  });
  function motionCommand(command) {
    if (state?.mode==='mapping' && state.ready && online && !recording && !mutationPending) {
      mutate('/api/task', {command, request_id:requestId()}, '已提交运动指令。');
    }
  }
  document.querySelectorAll('[data-motion]').forEach((button) => {
    button.addEventListener('click', () => motionCommand(button.dataset.motion));
  });
  el('save-mapping').addEventListener('click', () => mutate('/api/mapping/save', {}, '已开始保存地图。'));
  const motionKeys = {
    ArrowUp: ['forward','前进'], KeyW: ['forward','前进'],
    ArrowDown: ['backward','后退'], KeyS: ['backward','后退'],
    ArrowLeft: ['left','左转'], KeyA: ['left','左转'],
    ArrowRight: ['right','右转'], KeyD: ['right','右转'],
  };
  let heldKey = null;
  let keyTimer = null;
  let keySending = false;
  let stopQueued = false;

  async function sendHeldKey() {
    if (keySending || (!heldKey && !stopQueued)) return;
    const command = stopQueued ? 'stop' : motionKeys[heldKey][0];
    stopQueued = false;
    keySending = true;
    try {
      const response = await fetch('/api/mapping/keyboard', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({command}), keepalive: command === 'stop',
        signal: AbortSignal.timeout(1500),
      });
      if (!response.ok && command !== 'stop') releaseKey();
    } catch {
      if (command !== 'stop') releaseKey();
    } finally {
      keySending = false;
      if (stopQueued) sendHeldKey();
    }
  }

  function releaseKey() {
    if (!heldKey) return;
    heldKey = null;
    clearInterval(keyTimer);
    keyTimer = null;
    stopQueued = true;
    sendHeldKey();
  }

  document.addEventListener('keydown', (event) => {
    if (state?.mode!=='mapping' || event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey ||
        event.target.closest('.topbar, .page-arrows') || activePage === 'diagnostics' ||
        event.target.isContentEditable || ['INPUT','TEXTAREA','SELECT'].includes(event.target.tagName)) return;
    if (event.code==='Space' && !event.repeat && !event.target.closest('button, a, summary')) {
      event.preventDefault();
      releaseKey();
      if (!state.keyboard_hold || state.busy) el('cancel-task').click();
      return;
    }
    const action = motionKeys[event.code];
    if (!action) return;
    event.preventDefault();
    if (event.repeat) return;
    if (!state.keyboard_hold) { motionCommand(action[1]); return; }
    if (!state.ready || !online || recording || mutationPending) return;
    heldKey = event.code;
    if (!keyTimer) keyTimer = setInterval(sendHeldKey,160);
    sendHeldKey();
  });
  window.addEventListener('keyup', (event) => {
    if (event.code === heldKey) releaseKey();
  });
  window.addEventListener('blur', releaseKey);
  document.addEventListener('visibilitychange', () => { if (document.hidden) releaseKey(); });
  el('record-voice').addEventListener('click', recordVoice);
  el('return-to-dock').addEventListener('click', () =>
    mutate('/api/task',{mode:'return',request_id:requestId()},'已开始返回充电处。'));
  el('cancel-task').addEventListener('click', () => {
    releaseKey();
    if (recording) {
      stopRecording(true);
      announce('已取消录音。');
    } else mutate('/api/cancel', {}, '已提交停止请求，请等待执行状态更新。');
  });
  el('stop-from-page').addEventListener('click', () => el('cancel-task').click());
  el('validate').addEventListener('click', () => mutate('/api/validate', {}, '开始传感器检查，报告将保存在本次会话中。'));
  el('show-current').addEventListener('click', () => { selectedHistoryId = null; taskKey = ''; renderTask(); });
  el('log-component').addEventListener('change', refreshLog);
  el('refresh-log').addEventListener('click', refreshLog);
  el('zoom-in').addEventListener('click', () => { zoom = Math.min(4, zoom * 1.2); drawMap(); });
  el('zoom-out').addEventListener('click', () => { zoom = Math.max(.5, zoom / 1.2); drawMap(); });
  el('fit-map').addEventListener('click', () => { zoom = 1; drawMap(); });
  el('map-layer').addEventListener('change',drawMap);
  el('export-costmap').addEventListener('click',async () => {
    const button=el('export-costmap');button.disabled=true;
    try {
      const view=state?.map_export_views ? el('map-export-view').value:'cost';
      const body={view};
      if (view==='observations' || view.startsWith('clean_')) {
        const task=selectedTask();
        if (!task) throw new Error('请先选择本次运行中已保存的相应任务。');
        body.task_id=task.id;
      }
      if (view==='semantic' && selectedTask()?.kind==='search')body.task_id=selectedTask().id;
      if (['semantic','relations'].includes(view)) {
        if(el('memory-room').value)body.room=el('memory-room').value;
        if(el('memory-category').value)body.category=el('memory-category').value;
      }
      const result=await api('/api/map/export',body),links=el('costmap-exports');links.replaceChildren();
      mapExportSession=result.session_id;
      for(const item of result.artifacts) {
        const a=document.createElement('a');a.href=item.url;a.textContent=item.name;
        a.target='_blank';a.rel='noopener';a.className='text-button';links.append(a,document.createTextNode(' · '));
      }
      announce('已保存所选视图PNG、SVG和原始数据；快照不自动更新。');
    } catch(error) {announce(error.message,true);}
    finally {button.disabled=false;}
  });
  ['room','category','show-regions','show-views','show-memory','show-obstacles'].forEach((id) => el(id).addEventListener('change', drawMap));
  ['memory-room','memory-category'].forEach((id) => el(id).addEventListener('change', refreshMemory));
  document.querySelectorAll('[data-map-view]').forEach(button=>button.addEventListener('click',()=>{
    mapView=button.dataset.mapView;
    document.querySelectorAll('[data-map-view]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    drawMap();
  }));
  function memoryHit(event) {
    const bounds=canvas.getBoundingClientRect();const x=event.clientX-bounds.left,y=event.clientY-bounds.top;
    return memoryHitTargets.filter(item=>Math.hypot(item.x-x,item.y-y)<=15)
      .sort((a,b)=>Math.hypot(a.x-x,a.y-y)-Math.hypot(b.x-x,b.y-y))[0];
  }
  canvas.addEventListener('mousemove',event=>{canvas.style.cursor=memoryHit(event) ? 'pointer' : 'default';});
  canvas.addEventListener('click',event=>{
    const item=memoryHit(event);if (!item) return;
    selectedMemoryId=item.id;renderMemory();drawMap();
  });
  const simulationImage = el('simulation-image');
  const simulationPlaceholder = el('simulation-empty');
  const cameraButtons = [...document.querySelectorAll('[data-camera]')];
  let cameraView = null;
  let cameraUrl = null;
  let displayedCamera = null;
  let simulationVisible = true;

  new IntersectionObserver(([entry]) => {
    simulationVisible = entry.isIntersecting;
  }).observe(el('simulation-view'));

  function updateCameraButtons(view, overview) {
    for (const button of cameraButtons) {
      button.disabled = button.dataset.camera === 'overview' && !overview;
      button.setAttribute('aria-pressed', String(button.dataset.camera === view));
    }
  }

  for (const button of cameraButtons) {
    button.addEventListener('click', () => {
      cameraView = button.dataset.camera;
      updateCameraButtons(cameraView, state?.gazebo_preview);
      if (simulationImage.hidden) {
        simulationPlaceholder.hidden = false;
        simulationPlaceholder.querySelector('p').textContent = '正在切换视角';
      }
      text('simulation-status', '正在切换视角');
    });
  }

  async function pollCamera() {
    let delay = 900;
    try {
      if (document.hidden || activePage !== 'simulation' || !simulationVisible || !state) return;
      const overview = Boolean(state.gazebo_preview);
      const view = cameraView || (overview ? 'overview' : 'robot');
      updateCameraButtons(view, overview);
      const reply = await fetch('/api/simulator/frame?view=' + view, {
        cache: 'no-store', signal: AbortSignal.timeout(1800)
      });
      if (!reply.ok) throw new Error(reply.status === 404 ? '重启项目后可接收实时画面' : '正在等待 Gazebo 画面');
      const frame = await reply.blob();
      if (cameraView && view !== cameraView) return;
      if (frame.type !== 'image/jpeg') throw new Error('仿真画面暂不可用');
      const nextUrl = URL.createObjectURL(frame);
      const nextImage = new Image();
      nextImage.src = nextUrl;
      try {
        await nextImage.decode();
      } catch (error) {
        URL.revokeObjectURL(nextUrl);
        throw error;
      }
      if (cameraView && view !== cameraView) {
        URL.revokeObjectURL(nextUrl);
        return;
      }
      const previousUrl = cameraUrl;
      cameraUrl = nextUrl;
      delay = 250;
      simulationImage.src = nextUrl;
      simulationImage.hidden = false;
      if (displayedCamera !== view && !reducedMotion.matches) {
        simulationImage.animate([{opacity: .65}, {opacity: 1}], {duration: 200, easing: 'ease-out'});
      }
      displayedCamera = view;
      simulationPlaceholder.hidden = true;
      if (previousUrl) URL.revokeObjectURL(previousUrl);
      text('simulation-status', view === 'overview' ? '全屋俯视 · 实时' : '机器人相机 · 实时');
    } catch (error) {
      if (simulationImage.hidden) {
        simulationPlaceholder.hidden = false;
        simulationPlaceholder.querySelector('p').textContent =
          error.name === 'TimeoutError' ? 'Gazebo 画面连接超时' : error.message;
        text('simulation-status', '画面暂不可用');
      } else {
        text('simulation-status', '画面暂缓更新 · 保留上一帧');
      }
    } finally {
      setTimeout(pollCamera, delay);
    }
  }

  const pages = [...document.querySelectorAll('[data-console-page]')];
  const pageIds = pages.map(page => page.dataset.consolePage);
  const pageTitles = ['仿真工作台', '任务管理', '地图与物品', '系统诊断'];
  const pageLinks = [...document.querySelectorAll('.top-nav [data-page-link]')];
  const pageSurface = el('console-pages');
  const pageNav = document.querySelector('.top-nav');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let activePage = 'simulation';
  let activeTransition = null;
  let requestedNavigation = 0;

  function positionPageMarker() {
    const link = pageLinks[pageIds.indexOf(activePage)];
    pageNav.style.setProperty('--selection-x', link.offsetLeft + 'px');
    pageNav.style.setProperty('--selection-width', link.offsetWidth + 'px');
    pageNav.dataset.positioned = '';
  }

  function switchPage(target, {history = true, animate = true, focus = false} = {}) {
    const pageId = target === 'task-history' ? 'tasks' : target;
    const index = pageIds.indexOf(pageId);
    if (index < 0) return;
    const request = ++requestedNavigation;
    const previous = pageIds.indexOf(activePage);
    const changed = index !== previous;
    if (changed) releaseKey();
    if (activeTransition) {
      activeTransition.skipTransition();
      activeTransition = null;
    }
    const direction = index < previous ? 'previous' : 'next';
    const motion = animate && changed && !reducedMotion.matches;
    const canTransition = motion && typeof document.startViewTransition === 'function'
      && window.scrollY < 48 && !document.hidden;
    function showPage() {
      if (request !== requestedNavigation) return;
      activePage = pageId;
      pages.forEach((page, i) => {
        page.hidden = i !== index;
        delete page.dataset.direction;
      });
      pageLinks.forEach((link, i) => {
        if (i === index) link.setAttribute('aria-current', 'page');
        else link.removeAttribute('aria-current');
      });
      text('page-title', pageTitles[index]);
      positionPageMarker();
      if (focus) pageLinks[index].focus({preventScroll: true});
      el('previous-page').disabled = index === 0;
      el('next-page').disabled = index === pages.length - 1;
      if (history && location.hash !== '#' + pageId) window.history.pushState(null, '', '#' + pageId);
      if (changed) window.scrollTo({top: 0, behavior: 'instant'});
      if (pageId === 'diagnostics') refreshLog();
      if (pageId === 'map-card') drawMap();
    }
    delete document.documentElement.dataset.consoleMotion;
    if (canTransition) {
      document.documentElement.dataset.consoleMotion = direction;
      const transition = document.startViewTransition(showPage);
      activeTransition = transition;
      // Rapid navigation can skip a transition before its snapshots are ready.
      transition.ready.catch(() => {});
      const cleanup = () => {
        if (activeTransition === transition) {
          delete document.documentElement.dataset.consoleMotion;
          activeTransition = null;
        }
      };
      transition.finished.then(cleanup, cleanup);
    } else {
      showPage();
      if (motion) pages[index].dataset.direction = direction;
    }
  }

  function stepPage(offset, focus = false) {
    const next = pageIds[pageIds.indexOf(activePage) + offset];
    if (next) switchPage(next, {focus});
  }

  function restorePage(event) {
    const id = location.hash.slice(1);
    if (event?.type === 'hashchange' && activeTransition) return;
    switchPage(pageIds.includes(id) || id === 'task-history' ? id : 'simulation',
      {history: false, animate: event?.type === 'popstate'});
  }

  document.querySelectorAll('[data-page-link]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      switchPage(link.hash.slice(1));
    });
  });
  el('previous-page').addEventListener('click', () => stepPage(-1, true));
  el('next-page').addEventListener('click', () => stepPage(1, true));
  pageNav.addEventListener('keydown', event => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    stepPage(event.key === 'ArrowLeft' ? -1 : 1, true);
  });
  window.addEventListener('popstate', restorePage);
  window.addEventListener('hashchange', restorePage);

  const ownGesture = 'input, select, textarea, button, a, summary, canvas, pre, #semantic-relations, .memory-list, .history-list';
  let touchStart = null;
  pageSurface.addEventListener('touchstart', event => {
    resetSwipe();
    if (event.touches.length !== 1 || event.target.closest(ownGesture)) return;
    const finger = event.touches[0];
    touchStart = {id: finger.identifier, x: finger.clientX, y: finger.clientY};
  }, {passive: true});
  function resetSwipe() {
    touchStart = null;
    delete pageSurface.dataset.dragging;
    pageSurface.style.removeProperty('--page-drag');
  }
  pageSurface.addEventListener('touchmove', event => {
    if (event.touches.length !== 1) { resetSwipe(); return; }
    if (!touchStart || reducedMotion.matches) return;
    const finger = event.touches[0];
    const dx = finger.clientX - touchStart.x;
    const dy = finger.clientY - touchStart.y;
    if (Math.abs(dx) < 12 || Math.abs(dx) < 1.4 * Math.abs(dy)) return;
    const towardPage = pageIds[pageIds.indexOf(activePage) + (dx < 0 ? 1 : -1)];
    pageSurface.dataset.dragging = '';
    const shift = Math.max(-28, Math.min(28, dx * (towardPage ? .24 : .10)));
    pageSurface.style.setProperty('--page-drag', shift + 'px');
  }, {passive: true});
  pageSurface.addEventListener('touchcancel', resetSwipe, {passive: true});
  pageSurface.addEventListener('touchend', event => {
    if (!touchStart) return;
    const finger = [...event.changedTouches].find(touch => touch.identifier === touchStart.id);
    const start = touchStart;
    resetSwipe();
    if (!finger) return;
    const dx = finger.clientX - start.x;
    const dy = finger.clientY - start.y;
    if (Math.abs(dx) > 55 && Math.abs(dx) > 1.4 * Math.abs(dy)) stepPage(dx < 0 ? 1 : -1);
  }, {passive: true});

  let trackpadDistance = 0;
  let lastWheel = -Infinity;
  let wheelChanged = false;
  pageSurface.addEventListener('wheel', event => {
    if (event.ctrlKey || event.target.closest(ownGesture)
        || Math.abs(event.deltaX) <= 1.4 * Math.abs(event.deltaY)) return;
    event.preventDefault();
    if (event.timeStamp - lastWheel > 180) {
      trackpadDistance = 0;
      wheelChanged = false;
    }
    lastWheel = event.timeStamp;
    if (wheelChanged) return;
    trackpadDistance += event.deltaX * (event.deltaMode === 1 ? 16 : 1);
    if (Math.abs(trackpadDistance) >= 65) {
      wheelChanged = true;
      stepPage(trackpadDistance > 0 ? 1 : -1);
    }
  }, {passive: false});

  restorePage();
  new ResizeObserver(positionPageMarker).observe(pageNav);
  new ResizeObserver(drawMap).observe(el('map-stage'));
  pollState(); pollCamera(); pollMap(); pollCostmap(); pollMemory(); refreshLog();
  setInterval(() => { if (activePage === 'diagnostics') refreshLog(); }, 5000);
})();
