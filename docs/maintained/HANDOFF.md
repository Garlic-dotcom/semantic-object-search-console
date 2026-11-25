# 当前项目交接

## 分页与仿真回归测试（2026-11-25）

- 恢复资源锁所指定的手机模型 v9，核对归档与模型 SHA-256，资源锁未变。完整 Python 测试 538 通过、38 跳过，原生 C++ 测试 3 通过。
- Edge 实测转场、快速切页、触摸、触控板、键盘、减少动态效果及 320–1440 px 布局。额外 19 项浏览器功能检查通过。当前会话读取实时相机、地图和日志，提交、停止、地图导出等写操作通过浏览器测试拦截，未发给原会话。
- 隔离会话 `20261125T055213_883412Z_558d62be` 同时启用电动门、A* 和俯视相机，验证两路相机、代价图、建图模式键盘前进 0.183 m 并松键停车、保存并下载 YAML/PGM，以及恢复导航和模拟回充。证据在 Windows 工作区 `results/console_regression_20261125`。

## 控制台分页（2026-11-25）

- 分页切换增加分方向的新旧页面转场、连续移动的导航标记和触摸跟随。支持系统减少动态效果。Gazebo 切换相机时保留上一帧，下一视角完成解码后更新。

- 仿真、任务、地图和诊断使用独立页面。顶部导航、左右按钮、触摸横滑、触控板和浏览器前进后退都可切换；任务表单保留输入，建图方向键在切页时释放，任务运行时可用顶部停止按钮。
- 现有 8768 会话实测四页、实时 Gazebo、地图与语义关系、日志读取、任务草稿保留。320、390、768、1024、1440 px 无横向溢出。浏览器预览放在 Windows 工作区 `results/console_pages`。

## Gazebo 网页实时视图（2026-11-25）

- 工作台首屏新增 Gazebo 画面，下面保留原地图与图层，任务与结果集中在右栏。网页可展示已有机器人相机，启动增加 `--gazebo-preview` 时还可切换独立的全屋俯视。
- 两次隔离仿真会话 `20261125T024835_059948Z_8e18130c` 和 `20261125T025405_977367Z_609aa14c` 验证导航就绪、Gazebo 俯视 JPEG 800×480、机器人相机 JPEG 640×480和浏览器切换刷新。115 项控制台与运行时测试通过。网页以同源图片请求获取实帧，限定到屏幕可见时刷新。界面和实帧保存在 Windows 工作区 `results/console_gazebo`。

## 控制台界面更新（2026-11-25）

- `ui/index.html`、`ui/style.css` 更新工作台视觉和分区。实时地图在桌面首屏，图层与导出可展开，系统状态与日志集中在系统诊断。沿用现有网页控件标识和任务接口。
- 在现有 8768 仿真会话读取真实地图与任务结果。浏览器验证 1440、1024、768、390、320 px 无横向溢出，三种地图视图、图层展开和地图适应可用，浏览器无脚本异常。桌面与手机效果图在 Windows 工作区 `results/console_ui`。

## A* 全局规划候选（2026-11-25）

- 当前项目已具备任务一至四及语义地图，优化阶段先验证全局路径规划。启动显式选择 `--astar`，用 `CellCenteredNavfn` 优先运行 A*，无法取得目标路径时回退 Dijkstra 与容差目标。启动时保存生效参数及哈希。
- 固定静态代价图、相同坐标插件和 7 组起终点，每策略每条路线预热 5 次后计时 50 次。各路线规划中位耗时下降 15.9% 至 74.7%，路径长度变化 -0.82% 至 +1.35%，采样点最高代价均持平。数据及复现用网格生成脚本在 Windows 工作区 `results/semantic_astar_20261125`。
- 带门仿真会话 `20261125T015322_306271Z_42c7cfda` 确认实际 Nav2 插件加载及客厅、杂物间门前两次规划成功。三项 C++ 测试及 117 项 Python 测试通过。尚未做同条件完整任务耗时对照，A* 保持显式启用。

## 单机键盘建图与电动门（166ada0 本地改动）

- 新增网页按住方向键连续运动、松键和空格停车。沿用语音转写、关键词消息、激光避障与地图保存，隔离实测键盘前进约 0.247 m 后松键停车，合成语音“请前进”转写并执行，以及保存 YAML/PGM。
- 使用 `--room-doors` 进入隔离场景。厨房、卧室、杂物间和健身区通过带碰撞体的电动推拉门与客厅相连。搜索、清扫、返航按房间入口通行，建图时在门旁停稳后可手动发“开门”“关门”。单次仿真已验证四门的开门及通行，并验证关闭门扇后各房间在地图连通性检查中与客厅隔断。
- 网页“去厨房找杯子”实测经厨房门进入，找到 1 个杯子，经同门退出，并回到模拟充电处。杂物间墙端让出门扇间隙后，重新启动实测关门、再开门，键盘跨门前进约 1.09 m 并保存局部地图。三包构建、网页脚本语法检查及 120 项相关测试通过。
- 日常导航仍用与场景匹配的校准底图。新保存的 SLAM 地图需单独校准房间、观测点及充电坐标后用于任务。机械臂抓取留在最后阶段。

## 当前可续接摘要（2026-11-24）

**当前工作（用户最新四项，原自动目标已清除）：** 暂停制作PPT与答辩资料，先完善项目。①杂物间三静置球主扫后前往漏扫块、现场局部重规划并补扫；用户确认允许最多额外3分钟、含返航总预算最多15分钟，不改覆盖/实际条带/安全门槛；②新增客厅香蕉寻找计数，资产已在本地，旧厨房find XY .05746m与S模型离线旁证支持优先选择，客厅两香蕉首轮find/count已通过，尚无多布局稳定性验收；③同条件语义记忆引导查找正确性/耗时路程对照，再移动核验更新；④有平移、转弯、重访的局部建图路线，保存/重载/恢复导航回充，用户确认本轮不要求整屋重建。grill-me与grilling已读，三项关键取舍已获明确回答（有限补扫、局部建图、安全记忆核验点），新物体由用户授权自主选择。原暂缓的三球/语义优化现按新指令恢复，未通过不升级。保存摘要不是宿主原生上下文压缩。

证据简称：`D=results/development/demo_two_rooms_20261123`；`C=results/development/cloud_continuity_20261122/depth_image_candidate_20261124`。详细旧状态已原文移入本文件历史，以下为当前可执行事实。

### 当前现场与下一小步

**当前优先任务：** 用户要求快速收尾、检查并更新远程仓库，保证他人可本地部署；发布后继续开发，不是项目结束。不制作新PPT。此前四项开发安排保留，发布检查期间不启动新的机器人任务。

- **现场已收尾：** be7bb4a8串行driver已failed退出，清扫已终态/停稳，后续建图未派发。中断后8767拒绝连接、控制台PID不存在，未见shutdown收据；按唯一UID/token/start_ticks核对所属残留为空，未盲重启。公开副本`docs/evidence/development_20261124/runtime_cleanup.json`，完整本机证据保留。
- **三球补扫最新：** `D/cleaning_followup/ball_trial/local_replan/utility_priority/`，主扫6792格/605.27秒，补扫净增696格/180.07秒；总7488/9336=80.2057%、15/23条、847.73秒，cleaning_budget_exhausted/partial。原刷盘重画、动作停稳/接触0、431638源检查0通过；地图停靠4.79cm但独立仿真16.0787cm>.15，整项未过。原首轮80.69%/20of27、补扫274格保留；初始条带/现场状态不同，不称严格因果或稳定改善。
- **客厅香蕉首轮：** 双香蕉find1/count2、最大XY14.76cm、完整原2方向计数、源0/接触0/地图回充过；仅所选布局，不升级正式默认类别。
- **语义变化核验通过、提速未过：** be7冷根同香蕉移60cm后find1/count1、XY10.31/8.03cm，旧位置待核验、新位置来自现场，SQLite/API与真实Spark-DSG重载一致；独立回充10.39/8.69cm、源0/接触0。夹具已ack恢复原冻结布局，未用真值改记忆或声称恢复后当前确认。新增安全点ABBA四次正确但两组慢18.56/24.90秒、多走约2.8m，新增点均0投影；`--memory-safe-approach`已隔离默认关闭，原显式memory_guidance排序保留。
- **局部建图：** 原f52实测平移2.147m、转弯6.549rad、重访9.02cm，另存/独立map_server重载82806格完全一致、原地图哈希/导航恢复过；独立停靠18.03cm失败。be7相关返航复测因前置清扫独立停靠失败未派发，不能称补测已过。
- **源码和工程：** 分阶段有限补扫/v16、真实失败快照选择测试、客厅香蕉布局、记忆安全点显式试验、精确回充最终朝向候选均已实现。536通过/38条件跳过18.90秒，三包2.03秒，diff/py_compile过。精确回充候选三次短任务独立位置过，但长清扫仍超15cm，尚不升级默认；不得放宽门槛。原参数别名启动失败/首版朝向停滞/UI终态不新鲜/DDS验证器发现等待失败均保留。
- **发布检查已完成：** main开发快照将按用户授权提交并推送，Git HEAD/远程状态以本轮发布收据为准。隔离源码536过/38跳过15.36秒、原生3过、全新三包build/install9.59秒，CPU网页/导航/感知就绪及10秒传感器检查过，未执行移动任务；临时根已stopped/残留空。复用锁定资源缓存及现有依赖，完整CPU依赖重装因官方轮下载超时/重试过慢未完成，未称换机验收。已补依赖清单、下载超时/重试、移除验证脚本本机固定路径，精选收据在`docs/evidence/deployment_20261124/audit.json`。没有修改原失败结果或删除本地成果，发布后继续开发。

- **发布后下一步：** 保留现有唯一总计划与三项已确认取舍（补扫≤180秒/总≤900秒、局部建图闭环、安全核验点可实验）；先排查长任务定位/物理停靠偏差，再补建图返航相关复测。记忆新增点先解决实际可观测性再谈收益，不机械重跑；三球完整条带仍欠缺。真人麦克风、更多布局稳定性仍未完成，16类/全屋不是交付前提。

### 此前已完成与可交付内容

**四项当前配方代表任务：** `D/delivery_preflight/daily_regression/combined_audit.json`为`representative_task_cases_passed_whole_runtime_pending`。同一856d根、固定配置，分批验证，**不是一次连续四任务或全运行时稳定性通过**。

| 项目 | 本轮证据与范围 |
|---|---|
| 静置箱 | 原生检出、实际最近中心距.8506m、绕行后杂物间原10点/现场0杯正确/回充；完整首观察窗146164检查源0超界 |
| 移动物体 | 新鲜实际已发布路径上横穿，原生0→占据，.34秒提前近停、续行/卧室杯1、XY.11593m/回充；完整相关窗76919检查源0。机身/夹具接触校准、心跳、清理通过 |
| 普通门口 | 实测距配置门口.559m、两处必巡/杯XY.08743m/回充；自身完整53391检查源0 |
| 持续堵路 | 实测改走替代通道，原生odom过阻挡面y=-.590/-.594，原10点/0杯/回充；完整任务首末各外扩.5秒，102119检查源0。不是全封门停车 |

**保留失败与统计修复：** 第一移动例只在观察点自然停车，仍拒绝作为让行。相关复测旧1.5m筛选又漏计更早停车，原两个failed保留。新增`scripts/validation/audit_moving_yield.py`保留.05m/s/.2s/.45s，核对新鲜实际已发布路径、原生占据转变、排除观察目标/当前原生目标到点停车；不要求靠近障碍才算成功。有充分旁证的连续近停.34秒、名义穿越点距1.669m、距观察目标>6m；另.74秒缺足够新鲜占据旁证，不额外计入，**勿误称入口到点停车**。同目标原生路径在有效停车前已改变（旧对当时夹具距离0、新名义表面余量.2787m），见related_followup/moving/native_response_audit.json。

新`tests/test_moving_yield_audit.py`和83KB真实采样夹具，5项正反/缺证据/过期旁证回归通过。只修验收器，不改机器人或数据。门口＋堵路合并观察器原failed7次均静止夹具准备期，原failed保留，按既有回调时钟包围法核对完整堵路任务；.4/-.1门槛未放宽。三批driver均0但原audit均failed，不能说原批次全过。只按combined_audit的明确范围表述，接触不覆盖轮/脚轮/地面。

**热态切换复核：** 同856d根后续一次短转/停止/SLAM另存/原导航恢复回充通过、33532次源检查0，180秒watch无断流、未触发GDB。旧cbd热根切建图时clock/odom/scan停而RGB仍更新，150秒验证超时、180秒整栈保护关闭，独立5秒探针确认，原failed13634超界保留。冷根与本轮后续热态成功不证明旧间歇故障已修，无证据不改QoS。证据`D/delivery_preflight/transition_diagnosis/`；本机Fast DDS2.6.12、rmw_fastrtps6.2.10，勿混称。

**交付文件：**

- **本轮新增可编辑演示稿：** `D/delivery_preflight/defense_deck_styled/defense_presentation.{pptx,pdf}`，13页/325段原生可编辑文字，串联统一系统/四任务/两区/北侧绕行/现场计数/变化核验/地图/共享深度/验证限制。真实Office重新打开、总览13页与修正页核对、文本/16:9/字体/输入SHA检查通过。两原始4倍UI视频另附、未嵌入PPT。完整`defense_deck.zip`23,507,848B，522项文件SHA全部核对，SHA c904d4ebd920d909fbf7078425ee575464daeee8dfc9f8eb6455608916ee570c；审计`defense_deck_archive_audit.json`。原8页包与报告均保留；只清理本轮被替换的初稿重复目录，保留字体导入/前缀误判/换行修正证据。所有未通过与人名待填均在演示稿，未最终提交。

- `D/delivery_materials/index.html`及同名ZIP：8张1920×1080 PNG页、原图/两段真实4倍UI片段、审计和5个原会话配置/源码快照，430文件SHA通过；ZIP SHA78efcc92cf3f8be392ca58a8a791ffcac52fae27554ed77306c2a5a4d22e5587。搬移后Firefox离线8页/500px、两视频2270/1186帧完整解码、无运动、临时浏览器清理通过。不同原会话不拼成连续验收。
- `D/delivery_preflight/presentation_materials.{pptx,pdf}`：8页16:9图片素材，LibreOffice真实打开/导出/预览通过，不是可编辑图表或最终答辩叙事稿。
- `D/delivery_preflight/report_draft/project_report_draft.{docx,pdf}`：按老师原四章模板的10页A4可编辑证据草稿，含实际系统框图/真实图/来源/范围/未完成项、成员实际贡献占位；真实Office打开/PDF文本与封面、系统、结果页栅格已核对。`assets/system_architecture.png`可复用；audit.json附输入/原件/当前配置源码/验收器散列，generator.py为生成源码。姓名学号实际分工待填、真人未测、未提交。图/材料先前工具错误与原失败保留，不影响实际机器人结果。
- 第5项总收据仍`D/delivery_preflight/system_precheck.json`，不可另立计划或交接。最新工程仅验收器5项/py_compile/diff通过，未重跑前轮完整513通过/38条件跳过21.09秒/三包2.73秒，不冒充本轮构建。

### 已有基础、展示素材与仍未完成

- **普通两区清扫合格素材：** b1根杂物间8658/9336=92.7378%/26of26/629.44秒，卧室6767/7975=84.8527%/19of19/511.33秒，冻结刷盘/接触0/源0/回充单次过；`D/cleaning_followup/repair/{utility,bedroom}/presentation.png`。旧90.23%后碰门失败保留。cbd当前配方复测8502/9336=91.0668%/26of27/659.18秒仍partial，lane19九格漏1格；源336428检查0/刷盘/停车/回充过，但接触观察线程提前关闭、完整性未证，`delivery_preflight/cleaning/audit.json`not_accepted。不重跑此优化。
- **三静置球：** 旧79.50%/19of28、新79.68%/16of25均partial；新补扫实际增111/121/1格、最后恢复预算不足。残余1897中末观测潜力内1070/外827只是上界，不能全归球；142秒4倍UI片段从任务中途开始且保留partial。已暂缓，不当完整清扫通过。
- **厨房/卧室物品：** 普通书碗布局保留原9杯瓶，两厨房支撑面各1碗、卧室书桌/床头柜各1书；S1280/书辅助/v14所选8项寻找计数及杯回归首轮过，正式默认仍杯/瓶/椅。更多布局/5重复暂缓。cbd配方连续书find1/count2、121.15/158.78秒、XY.11062/.10028/.04269m、两处/保存/现场记忆/回充/接触与源0过；非真人。厨房v15第5冷启漏1/2、碗源失败、瓶目标回复丢失保护关闭均保留，用户暂缓。
- **综合北侧绕行素材：** `D/route_pair/actual_pair.png`为同根两次实际路线，途中箱后自主走靠近健身区一侧，不要求进入gym、无强制北侧航点；原厨房11点/2杯/回充过。原无箱49任务内源超界失败保留；唯一重试通过、放箱准备5失败/任务窗0另审计，不称全运行时稳定。
- **语义变化与地图：** Kitchen杯移动单次find1/count2、≤20cm/全11点/源0/回充、SQLite与真实Spark-DSG重载/显式变体冷加载一致通过，`D/semantic_followup/movement_cup_diagnostic/memory_change.png`及74秒4倍UI片段可用；首次.313m失败保留。不是厨房提速或物理身份重识别。7类空间图＋真实DSG关系PNG/SVG/原始JSON已实现且同底图核对，`D/map_exports/shared_views_verified/gallery.png`；实际浏览器5种即时视图/15下载及新partial清扫真实HTTP导出通过。局部odom代价图/全房视觉覆盖仍未做，各源戳独立。
- **合格记忆收益仍未过且追加优化暂缓：** find已修为完整配置4秒驻留再结束，min_hits2/20cm/必巡不变。原云4次ABBA数量/位置/回充过但169源超界（121在首任务）；image ABBA首无记忆XY.11778过、有记忆.25278失败即停，两次均32投影/源0。原观察与包围TF证明map跨任务差.137058m、诊断反算odom差.0000528m，是这两例定位变换差，不推广全部历史唯一原因、不用odom替代运行map。只读核对alpha1–5=.2/原生50Hz里程计，**未新增AMCL候选**。同Gym球移动count2/真实1失败保留；不能拼Kitchen变化与Gym收益当同物品闭环。
- **共享点云候选已实现：** 显式image每启动3对不同同戳原云/深度/内参独立校准≤.002m后输出，固定内参/帧签名/时效；native默认保留。正Inf仅经验证清除不mark、NaN/零/负Inf不当自由；输入.25/运动.4不放宽。1280stride8（640stride4）均160×120；原云29.49MB/帧→既有深度4.92MB，只是载荷不是6倍任务提速。YAML lazy确停原云，静态箱0→100→0、几何差约1微米及两实际find/返航全窗源0通过，见C；源与四任务全运行稳定性不能等同。

**剩余与约束：** 真人四功能、当前合成链路预检、报告实际成员贡献/答辩素材最终取舍、间歇热态断流/准备期源时效风险仍未完。原P1–P3三类100分批案例/57异常、G0/G1合成自动验收为历史冻结证据；最近旧合成找杯XY.206539m失败不能当通过。保持一份逻辑底图、历史/兼容地图/失败；真值仅布置和事后评估，不进感知/路线/补数；物品位置用真实map观测，历史不当库存，任务编号/M-ID/物理身份区分。保护大量既有未提交改动，不commit/push/reset/清理旧成果；仅清理本轮临时进程/夹具。关键取舍先grill-me+grilling，每轮≤3问；目前两个待答是人工可用性与报告事实，不是新验收取舍。

## 续接摘要历史（原文保留，运行状态与下一步以上节为准）

### 2026-11-24：发布收尾前的开发现场摘要（历史）

### 当前现场与下一小步

- **当前be7bb4a8/domain67/8767/Gazebo+RViz，root exec92633；后续串行driver exec77518正在清扫，不能重发任务。** `D/semantic_followup/living_banana/heading_fix_audit.json`passed：冷根原位完整count1、移.6m后find1/count1均数量/.20m/独立停靠/接触0/全源0通过，独立停靠.10412/.10387/.08689m；移动后find/count XY.10308/.08035m。SQLite/API与真实Spark-DSG重载全字段/修订一致。物理夹具已ack恢复原布局，恢复后未重新核验当前位置，不把历史当当前。默认关闭新点，显式memory_guidance保留，precision_docking最终朝向修复本根已加载。
- **本根当前清扫复测：** `D/cleaning_followup/ball_trial/local_replan/utility_priority/current.json`，实际约445秒/53.38%，尚在主扫；父driver接下来仅在动作/停稳/接触/源和独立停靠过后派发`D/mapping_loop/run.py --expected-session ...be7bb4a8 --output-name heading_fix`。原三球完整覆盖仍未过，不提前称当前达标。最新工程536过/38跳过18.90秒、三包2.03秒，diff/py_compile过，日志`full_tests_heading_fix.log/build_heading_fix.log`。


- **880ba12a最新实测：** 首单香蕉count1/XY.12377m、独立停靠.10532m和全源49998检查0通过，但终态一次UI障碍fresh=false使原整项failed；8次只读后续已恢复，不覆盖失败。ABBA首工具在DDS里程计未发现前退出且未运动；加有界15秒发现等待后四次功能/≤.20m/接触/原生里程计/独立停靠通过，177876源检查0。两组有记忆反而慢18.56/24.90秒、多走2.84/2.81m，新点均0投影后回退固定点；不能宣称提速，`D/semantic_followup/living_banana/abba2_audit.json`保留failed。新增点现隔离为`--memory-safe-approach`默认关闭，既有显式memory_guidance排序保留。
- **移动测试新失败：** 同香蕉移.6m后find已现场正确1/XY约.094m，但精确停靠近目标.10m、朝向误差约2.55rad停滞，含有界重试后partial；源0/接触0/停稳过，fixture已ack恢复原位，count未派发。原`movement/audit.json`failed保留。实际载入参数读取两次回空/CLI发现不完整，不能称已核实完整参数；已记录。新候选只为停靠启用官方rotation shim的最终朝向控制、SimpleGoalChecker达5cm后保留位置阶段，最终独立验收仍15cm/.15rad，不把机制线索当已证明根因。回归/构建后冷启复测；目前旧根idle，无本轮运动在跑。


- **最新确认Q3：** 允许从真实历史坐标＋当前已观测地图生成一个安全优先核验点；必巡与所有固定回退点保留，计数完整巡视/现场观测。有无记忆使用同一正常基线，预测收益不当实测收益。
- **f52b173a根当前ready/idle/无uncertain**（domain67/8767、console PID6927，root exec34224）。已完成本轮三项实跑，未启动下一运动；下述源码候选尚未加载，需核对退出收据后单次冷启。当前冻结S1280/image/书球辅助/v16/两香蕉三球布局，不要把工作区新源码当已运行。
- **补扫第一次实跑仍partial：** `D/cleaning_followup/ball_trial/local_replan/utility/audit.json`，7533/9336=80.6877%，20/27条，796.51秒；主扫7259格/552.64秒，独立补扫净增274格/160.71秒，最终recovery_budget_insufficient。原刷盘重画/动作顺序/停稳、接触0、406650次源检查0通过；独立仿真停靠.16427m>.15失败保留。残余1803中当前规划潜力内1031/外772只是上界。新选择候选仅在显式补扫阶段允许≥80%后按既有1.25倍收益/秒选更高效片区；真实失败夹具普通选21格、补扫选75格，尚未实跑。
- **新客厅香蕉首轮通过：** `D/living_banana/audit.json`，find1/1、XY.14757m、74.10秒；count2/2、XY.13576/.10842m、98.14秒，原2方向/现场观测/保存/地图回充/接触0/完整源检查0。真实RGB-D/TF已采集；仅所选布局，不升级正式类别或稳定验收。该旧验证器未加独立物理停靠门槛，不补称通过。
- **局部建图链路通过，整体未过：** `D/mapping_loop/trial/audit.json`，实际平移2.147m、转弯6.549rad、重访差.0902m；另存373×222栅格与独立map_server重载完全一致、原地图哈希不变、导航恢复，61194源检查0/接触0；独立仿真停靠.18032m>.15，整体failed保留。
- **待加载的语义与回充候选：** `memory_approach.py`复用RoomSweep/SciPy，在当前新鲜costmap可用、已知自由/≥.35m间距/同连通区生成一个历史核验点，完整回退保留、计数不变；记录实际地图供独立重算。新增单香蕉原位/移动显式布局只作设计和事后评估，同一物理目标做ABBA与变化。显式`--precision-docking`以5cm执行目标和完整朝向收敛，独立验收仍15cm/.15rad；原默认充电配置保留。工程日志在`D/semantic_followup/living_banana/`，新完整回归/构建待核对，未宣称实测收益。
- **下一步：** 完成当前候选回归与构建、按所属根停旧栈并核对shutdown，再单次冷加载；先现场验证精确停靠/单香蕉，然后同条件ABBA及移动核验，针对性补扫与建图返航复测。保护全部原失败/历史地图/未提交改动，不制作PPT；UI语音选择同步仅定位，未修改。

- **前根`20261123T225544_901710Z_343f2dfe`的历史结果（当前状态以上为准）。** 已核实旧856d根关闭收据后按同配方仅冷恢复一次，root exec41229；旧退出事实及收据仍在`D/delivery_preflight/runtime_exit_after_trials.json`，不据此称运行崩溃。独立合成椅子计数预检exec78238已收到停止信号并exit1，来源未记录；脚本取消、任务canceled/停稳/ready无uncertain已确认。随后公共返航地图完成但独立仿真.16463m>.15，failed保留。本轮有信号记录的独立计数exec74984已exit1：完整18/18方向但2/4，已匹配两把XY.08357/.04770m，独立停靠.155946m>.15，完整207899源检查0/接触0/停稳.96秒，ready/idle/无uncertain。`synth_voice_count_followup/audit.json`为最新终态；无本轮运动验证在跑，root仍运行。
- 最近冻结配方：普通`layout_service_bowl_book_v1`、rooms v14、S1280/1280×960、候选bowl/book/sports ball、辅助YOLOE book+sports ball、显式memory_guidance和**depth-cloud-source=image**，NavFn Dijkstra+DWB/default圆形nav2_depth，body/safety均未启用。默认n640/v6/native仍保留，image未升级默认。配置与源码以该根session.json/configuration/sources的SHA为准；本轮没改ROS产品、AMCL、速度、半径或安全门槛。
- **下一小步：** 先实现有独立补扫预算的漏扫块就近处理与现场重规划，并用原失败快照验证、实跑三球场景；随后客厅香蕉与同物体语义对照、局部建图。新证据入口`D/cleaning_followup/ball_trial/local_replan/`已保存决策及源码前像，候选已实现、回归过、现场清扫在跑，未验收。旧候选找杯24.46cm/椅2of4/独立停靠15.59cm失败保留，不降门槛。UI语音表单同步问题仅只读定位，**尚未修改代码**，本轮不插入为主任务。
- **最新现场核对：** 8767拒绝连接，旧343f根记录控制台PID302008已不存在，根目录未见shutdown收据；不能沿用上方旧ready/idle。启动前继续核对组件所属残留，勿只因端口拒绝重复起栈；尚未重启或停止组件。
- **语音预检工具修复：** 原`D/delivery_preflight/synth_voice`在原始Marionette上下文未提交；改标准Geckodriver后`synth_voice_webdriver`明确捕获fetch未绑定Window的验证器错误，录音16727B但未送转写/未移动。新`synth_voice_bound_fetch`绑定原生fetch后实际转写“请去厨房找一个杯子。”，未编辑文字，只通过原UI确认；实际136.70秒、两处/3of11、1杯，.244603m定位失败保留。完整76405检查源0、独立仿真绝对停靠.14302m/.10531rad/停稳、接触0/心跳/浏览器及profile清理过；不是完整整机或真人通过。立即截取的result_ui.png仍显示上次轮询的返航中，仅作过程截图，终态以final_state/evaluation为准。
- **独立计数中断：** `synth_voice_count/audit.json`记录正确转写与原文UI提交；143秒附近完成6/18方向、现场暂确认1把时验证进程收到SIGINT或SIGTERM（旧处理器未记具体信号/发送者），随后finally取消真实任务，API确认canceled/ready/无uncertain。完整79591次源检查0超界、浏览器/profile清理过，不据此当计数通过或归因为导航失败；不盲重跑。`after_interrupt_state.json`保留完整原结果。
- **计数有界复核：** `synth_voice_count_followup/`增加SIGINT/TERM具体信号记录与strace来源记录，先用自身SIGTERM探针证实仍处理停止，再按原UI合成椅子指令完整实跑393.90秒。未收到停止信号，旧中断来源仍未知、不能称已修。18/18配置驻留/观测数据完整、现场2/评估4，计数未过；源207899次0超界、接触0/心跳/地图回充/浏览器profile清理过，原生仿真停靠.155946m略超.15、停车.96秒。实际UI终态截图已等到“已完成”，不把该徽标当独立数量通过。只改验证器：连续原生停稳样本保持原速度/.45秒门槛，失败正确exit1，未改机器人/感知或安全参数。
- **文档一致性：** TARGET_CATALOG与RESOURCE_PREPARATION已移除16类/8类/12类当前硬门槛、过时85%设施备注，更新7类图/碗书所选布局/变化核验与收益区别；正式三类和定位门槛未改。更改前原TARGET_CATALOG完整SHA冻结在`D/delivery_preflight/synth_voice/target_catalog_snapshot.md`供.20/.30门槛追溯。S权重/资源只读check通过，不作功能验收。
- 真人可用性、报告成员姓名/学号/实际分工已分别异步询问，尚无回复；不要把预选项或超时当回答。暂无需重复询问的关键决策，不重开暂缓优化。



### 2026-11-24：第5项日常代表复核与报告收尾前的摘要原文

整理前摘要原文（当前状态以上方为准）

**活动目标仍进行中：**“今晚的目标：完成计划，对答辩展示的部分进行优化”。唯一总计划为DEPLOYMENT_PLAN.md。用户最新明确“这部分暂时还行，进行后续计划”，本轮停止追加定位/语义对照调参，转第5项预检与交付；碗/书更多布局与重复、厨房v15和新增球清扫仍暂缓。未通过保持未通过，保存此摘要不等于宿主原生上下文压缩。

**本轮最新进展（先看此段）：** 856d470e后续热态SLAM短转/停止/另存/原导航恢复回充通过，33532次源检查0超界，180秒watch无断流；旧cbd长时故障仍未定因，没改QoS。接着同一冻结配置做四日常回归，最终`D/delivery_preflight/daily_regression/combined_audit.json`为`representative_task_cases_passed_whole_runtime_pending`：静置箱绕行、移动物体短停续行、普通门口、持续堵路实际替代通道的代表任务通过。不是一次连续四任务或全运行时稳定性认证。

移动首例只有观察点停车不采信；相关复测原1.5m筛选误排提前停车，原两个failed均保留。新增`scripts/validation/audit_moving_yield.py`按新鲜实际已发布路径、原生0→占据、排除观察目标/当前原生目标到点停车核对，保持.05m/s/.2s/.45s，采信.34秒提前近停（名义穿越点距1.669m、观察目标距>6m）。另一段.74秒近停因占据旁证源戳不够新鲜，不额外计入，**不能误称入口到点停车**。同目标原生路径在有效停车前已改变：旧对当时夹具表面距离0、新路径名义余量.2787m，native_response_audit.json旁证。只修验证统计，机器人参数/位姿/真值未改。新`tests/test_moving_yield_audit.py`及83KB真实采样夹具，5项正反/缺证据/过期旁证回归通过；未冒充重跑前轮513/38或构建。

当前回归时效：静置/移动完整窗146164/76919检查0；门口自身完整窗53391检查0。门口＋堵路全观察窗原failed7次均静止夹具准备期；保留原failed，堵路原生首末各扩.5秒、回调时钟上下界包围、102119检查0超界，阈值.4/-.1不变。堵路原生odom过阻挡面y=-.590/-.594，原10点/现场0杯正确/回充，确有替代路，不称全封门停车。实际夹具落球校准、机身/夹具无记录接触、心跳、模型清理均核对。三批driver均0退出但各原audit状态failed，不能写成原批次全部通过；合格代表范围与原failed由combined_audit显式汇合。

**报告交付：** `D/delivery_preflight/report_draft/project_report_draft.{docx,pdf}`按老师原四章模板生成，10页A4，含真实系统框图/图/上游来源、成员实际分工占位、所有合格范围与未完成项；LibreOffice真实打开导出/PDF文本检查、封面及系统/结果页栅格已查看。audit.json附原件SHA、输入审计/当前冻结配置源码与验证器/夹具散列，generator.py为本稿实际生成源码；不是最终提交。可复用框图在该目录assets/system_architecture.png。只有验收器/实验工具/文档改动，无ROS产品修改、无新构建。

**当前现场状态与既定下一步：** 856d470e root exec13136现exit0；控制台在任务全部结束、离线整理期间收到SIGINT/SIGTERM关闭信号（发起者未记录），shutdown 22:39:33 UTC为stopped/残留[]，PID已无、8767拒绝连接。`D/delivery_preflight/runtime_exit_after_trials.json`与shutdown副本为据，**当前没有运行中的机器人根**，不能沿用下段旧ready状态。后续先按同配方正常冷恢复（不要因旧API拒绝重复起栈），再做当前配方合成音频→同UI→实际任务→20cm/保存/回充预检；不以合成替代真人。已异步询问真人是否方便、报告姓名学号实际分工，尚无回复，不等人工继续可做的预检。活动目标未完成，AMCL/球清扫/类别矩阵仍不重开。

**第5项最新执行：** `D/delivery_preflight/audit.json`所选卧室书本连续文字find/count通过，分别121.15/158.78秒，find1/XY .11062m，count2/2、XY .10028/.04269m，两处必巡、保存/记忆/现场计数/回充、接触0、完整各自观察窗源检查60636/79999次均0超界。不是真人麦克风、冷启重复或四功能完整通过。同根一次普通杂物间完整清扫已结束：8502/9336=91.0668%、26of27、659.18秒、预算结束partial；原lane19九格中八格实刷、缺一格，原条带门槛仍失败。冻结刷盘/停车/回充(.09443m/.09621rad/.46秒)及336428次源检查0超界通过。parent接触观察线程出现ExternalShutdownException、具体开始时刻未知，不能用空列表称全窗无接触；上层`D/delivery_preflight/cleaning/audit.json`明确not_accepted，旧原审计与异常收据保留。exec67811已0退出/两子观察器0；不再重跑或调参。随后热根建图切换失败：独立5秒仅RGB11帧，clock/odom/scan零帧；mapping尚未就绪、未发运动/保存，150秒验证超时，实际控制台180秒超时整栈保护关闭。`D/delivery_preflight/mapping/audit.json`保留13634次源超界，failed_state与shutdown/独立探针已保存。旧cbd根shutdown stopped/残留[]后控制台按所属PID正常关闭。同配方冷根856d470e仅一次有界复核已通过：短转.79573rad/停止/SLAM另存YAML+PGM/恢复原导航/回充(.06819m/.09136rad/.46秒)，主YAML/PGM未变，接触观察心跳完整、记录接触0，34155次源检查0超界；独立90秒窗口未复现断流、未触发GDB。`mapping_cold/audit.json`与热失败分开，不称故障已修；不是全屋重建或真人验收。原book runner exec92143已0退出。

**可交付素材包：** 新`scripts/package_demo_materials.py`只从原审计导出事实，生成`D/delivery_materials/index.html`、8张1920×1080 PNG页、原图/两段真实UI视频、原审计和5会话配置/源码快照，430文件散列已核验；ZIP SHA `78efcc92cf3f8be392ca58a8a791ffcac52fae27554ed77306c2a5a4d22e5587`，约18MB。独立搬移ZIP后实际Firefox离线8页/500px、partial说明、两视频2270/1186帧全解码通过，浏览前后机器人任务不变、浏览器0退出/临时profile删除，收据`D/delivery_preflight/materials_browser/audit.json`。三球partial仅附录，记忆变化不称提速；各不同原会话明确标注。另有`D/delivery_preflight/presentation_materials.{pptx,pdf}`8页16:9图片素材页，实际LibreOffice打开/导出/栅格预览已核对，`presentation_audit.json`通过；不是最终叙事稿/可编辑图表。首次母版标签与随后单位取整的比例失败保留，最终标准化页面及全页图片为12192000×6858000 EMU，原比例门槛通过。初打包同名snapshot.json被散列守卫拒绝后改保留子目录；浏览工具首次Snap不能访问/tmp、第二次缺ffprobe，改工作区隔离路径＋已有PyAV后通过，原工具失败记录保留。仅打包/验证工具与文档改动，无新AMCL参数或产品源码修改；py_compile/diff通过，沿用前轮513/38与构建，不称本轮重跑。

**本轮开始时的会话（现已关闭，以上段为准）：** `20261123T220246_841985Z_856d470e`，同配方/domain67/8767/Gazebo+RViz，root exec13136；开始时曾ready=true/busy=false/mode=navigation/control_uncertain=false，模拟充电。mapping_cold exec51069和90秒transition_watch exec8216均0退出，cloud0。冷启动不是热态故障修复证据。`mapping.py`显式关闭rclpy默认信号处理并记录executor心跳；旧清扫接触监测空缺不能补成通过。第5项汇总仍同`D/delivery_preflight/system_precheck.json`；当前关闭与下一步以本轮最新段为准。

**上一会话（已关闭）：** `20261123T210413_273482Z_cbd3ce16`，domain67/8767/Gazebo+RViz，普通`layout_service_bowl_book_v1`、rooms v14、S1280、1280×960、辅助book+sports ball、显式memory_guidance、**显式depth-cloud-source=image**。root exec89863收尾exit143，shutdown stopped/残留[]为关闭依据；新ABBA exec7877已因定位断言exit1，TF/AMCL exec69923与独立cloud均0收尾，原memory_guidance=true已恢复。后续预检与关闭见上段；书本任务结束时曾ready/idle/回充。核对同一handle/API再行动，不以观察超时当作任务停止。上一原云根4a1e6841已正常关闭（shutdown stopped/残留[]）。静态箱探针已结束且models_restored=true，无临时夹具。当前实际参数/源码以会话session.json、configuration及source_snapshots为准。

证据简称：`D=results/development/demo_two_rooms_20261123`；`C=results/development/cloud_continuity_20261122/depth_image_candidate_20261124`。以下路径均相对项目根，不是另立计划。

**本轮代码与工程验证：**

- `search_node.py`修正find在2投影时跳过已配置4秒驻留：检测callback继续采样，完成本点驻留及必巡后再found；count路线、min_hits2、20cm、TF、球拟合/导航/停止不变。前像`D/semantic_followup/counterbalanced/dwell_candidate/search_node.py.before`。相关3项新回归及当时完整504/38、三包1.29秒通过。
- `cloud_projection.py`新增Fortress X-forward/半像素深度投影；`cloud_adapter.py`显式image模式，每次启动必须取得3个不同、严格同源戳的原云/深度/CameraInfo，独立核对XYZ最大差≤.002m、有限及正Inf掩膜才输出。之后锁定内参/尺寸/帧/编码且核对新鲜度；销毁校准订阅。NaN/零/负Inf不成自由射线，每帧仍需≥8有限锚点才补正Inf至实际far，仅clearing不marking。输入.25秒/运动.4秒不放宽。
- `development.launch.py`在image模式用同版ros_gz_bridge0.244.26的**YAML lazy=true**；该版CLI读取lazy但未赋给BridgeConfig，不能仅加CLI参数。适配器退订后原云停止大载荷桥接，ROS发布者仍可被发现。Runtime/Console新增`--depth-cloud-source image`并冻结模式/新源码；**默认native原云基线保留**，image是显式候选。native逐帧原云校验与image“启动独立校准＋固定签名”是不同机制，不能声称完全相同。
- 最新完整**513通过/38条件跳过21.09秒、三包构建2.73秒**。新夹具`tests/fixtures/depth_native_fortress.*`为真实采样，核对原标障/清除一致性、三不同帧、错误内参拒绝、无回波、端序/行padding。曾有测试把Inf加.01未改变输入，修正选择真实有限点后通过，失败日志保留。原生C++未改；未因本轮声称其全部专项重跑。前像集中C/sources_before/，官方Apache2上游代码/URL/blob SHA在C/upstream/。

**已证实的传输线索与候选子项：** 原云1280×960/point_step24，每帧29,491,200B，深度图4,915,200B。当前1280实际stride8（640为4），都保留160×120采样，不误写为1280仍stride4。三对同戳实测投影最大差<1微米，有限/正Inf掩膜一致；这只是几何证据，不等于导航通过。C/loaded.json已核对新根实际SHA/原生3帧校准/XYZ12B camera_link输出、Lazy1日志与原云消费者0；Gazebo查询仅发布端，无大流订阅。首次只读加载探针误用RELIABLE订阅BEST_EFFORT输出，QoS修正后通过，产品QoS未改，旧失败日志保留。

C/stationary_probe已实际加入/移除箱体：native代价0→100→0、模型全部恢复；独立完整静态观察窗19760检查/过期0，cloud最大gap.27891秒、到达源龄最大.080秒，cleanup均0。**新候选两次实际find/返航全观察窗134235检查/过期0，cloud最大gap.186314秒、源龄最大.126秒，接触/odom/回充通过；源连续性子项通过，但不是四项日常避障或全部配置稳定性。记忆组定位仍失败，见下。** UI/RViz已正常就绪，导航仍NavFn Dijkstra+DWB、nav2_depth local/behavior=odom/local static=false，半径/速度等未因这轮改变。

**当前语义对照的真实完成程度：**

| 组别 | 证据与结论 |
|---|---|
| 原8168585d基线 | `D/semantic_followup/counterbalanced/audit.json`：首find1但XY .247651m>.20即停，没派发guided；回充/接触/里程计/66804次源检查0超界通过，原失败保留 |
| 同根仅一次几何诊断 | `.../geometry_diagnostic/geometry_analysis.json`：XY .081916m，但16次源超界，仍fullfailed；该帧球拟合确成功，odom约3.29530/4.22731、map3.24797/4.15897。首失败无同戳TF，唯一原因未定，未用odom纠正运行位置 |
| 驻留修复、原云4a1e6841 ABBA | `D/semantic_followup/counterbalanced/dwell_candidate/audit.json`：4任务数量/≤.20m/回充/接触/独立odom均过；两组省46.52/51.41秒与.9295/.4206m，3→2点。**全窗169次源超界、一次.57948秒cloud断档，121次确在首任务，故not_accepted**。不能全归准备期。新增近朝向仍0投影，不称新视角提升识别 |
| 当前image候选 ABBA | `C/memory_abba/audit.json`仍not_accepted：无记忆XY .117779m通过，有记忆XY .252782m失败即停，均find1/32投影/完整驻留/接触0/odom/回充过；全窗源0超界。未补派第3/4次，原参数已恢复。保留只读初始DB和每轮历史，未人工删选旧5条。正面renderer因门槛未过没有执行 |

**保留定位证据（第4项追加优化暂缓）：** `C/memory_abba/position_frame_audit.json`精确读取两任务各32个原始observations与包围检测时戳的真实TF（包围变换相同，无回溯插值）。同静止案例map点相差.137058m，诊断反算到odom后仅差.0000528m；各任务观察窗内点和TF均不变。最后AMCL后验σx约.155–.194m、σy约.243–.261m、σyaw约.186–.189rad。**这两例的跨任务坐标差已由map/odom定位变换解释，不能再归为球深度抖动或点云重建误差；也不能推广为所有历史失败唯一原因。** 未读目标真值、未用odom替换运行map坐标，原25.3cm失败不改。

定位追加优化现按用户安排暂缓；已只读核对AMCL alpha1–5=.2与仿真50Hz原生OdometryPublisher配置，证据`D/semantic_followup/localization_calibration/{baseline_loaded_parameters,sim_odometry_source}.json`。**没有新增定位候选、改AMCL参数/初始置信度或map/odom值，也未盲重跑ABBA。** 后续若恢复此项，保持Dijkstra/DWB、安全边界、20cm和源龄门槛；同一Gym球收益＋变化仍欠完整通过，不能拿Kitchen变化与Gym收益拼成同物品闭环。已有`layout_service_memory_ball_moved_v1.json`及`D/semantic_followup/movement_design.json`，使用前核对源/hash/姿态；旧Gym移动count2/实际1失败保留，不删条或补数。临时物理移动失败须恢复ack，成功须显式变体冷重载或恢复再验。当前下一步为上段第5项预检、真人联调准备和交付收尾。

**已有答辩素材与保留缺口：** 入口在DEVELOPMENT_VALIDATION.md顶部。

- 无新增球：杂物间92.7378%/26of26/629.44秒，卧室84.8527%/19of19/511.33秒，接触/时效/原刷盘重画/回充单次过。图在D/cleaning_followup/repair/{utility,bedroom}/presentation.png。旧90.23%后碰门失败保留。
- 三静置球：旧79.50%/19of28，新79.68%/16of25均partial；新分支3次实刷111/121/1格，最后恢复预算不足而返航。新漏扫1897格中，末次观测规划掩膜潜力内1070/外827；只是上界，不能全部归球或证明永久不可达。`D/cleaning_followup/ball_trial/repair_followup/`有审计、漏扫图及142秒4倍UI片段（从任务中途开始，非相机/全任务录制，末帧partial）；不再立即重跑此项。
- 综合避障：D/route_pair同根无箱实走＋途中放箱自主北侧实走，原厨房11点/2杯/回充通过，actual_pair.png。北侧是靠近健身区一侧，不要求进入；未强塞北侧航点。首无箱49次任务内源超界保留，放箱5次准备期超界与任务窗0另审计；不推广为所有配置稳定。
- 碗/书：厨房餐桌与L形操作台各1碗、卧室书桌与床头柜各1书，原9杯瓶保留。显式S1280/书辅助/v14所选布局8项寻物计数与杯回归单轮过，后续变化布局/5重复由用户暂缓。杯/瓶/椅仍正式默认；16类全面准入/全屋清扫不作答辩前提。
- 厨房v15四既有点/4朝向候选：首根4杯计数+find过，第5冷启及诊断漏1/2，碗回归源时效fail、瓶返航send_goal回复丢失后整栈保护关闭，均未验收。用户已暂缓，不再补五次。rmw_fastrtps6.2.10上游定位到回复reader匹配超时（本机Fast DDS为2.6.12，二者不可混称），仅是机制线索，未改RPC等待/未知终态保护，不宣称本次点云优化已解决RPC。
- 记忆变化：Kitchen杯移动单轮find1/count2、≤.20m/两处/全11点/源0/回充/SQLite与真实Spark-DSG重载通过，memory_change.png和74秒4倍UI片段在D/semantic_followup/movement_cup_diagnostic及recording_cup_diagnostic。首次.313m失败保留；厨房必巡前缀未变化，不能当提速或物理重识别。
- 地图：D/map_exports统一导出7类空间视图＋真实DSG关系PNG/SVG/JSON，共用同一逻辑底图；shared_views_verified/gallery.png。实际Firefox5种即时视图三文件下载/500px通过；新三球partial清扫两图真实HTTP导出与原result/plan/全trace/格数完全一致。局部odom代价图/全房视觉覆盖仍未实现，源戳分别保留，不称同步图；历史M-ID、任务#与物理身份不同。

**仍未完成：** 同物品合格记忆收益＋变化闭环、当前最终配置四项日常避障相关回归、四功能连续预检/真人麦克风、固定配置与PPT/报告收尾。原P1–P3三类基线100例/57异常、G0/G1合成语音自动验收是历史冻结配置证据；最近合成找杯执行/回充通过但独立定位.206539m失败，不能当真人通过。语音“找”仍找一个，需要全部用统计/清点/有多少；本轮只修观察窗口，不改指令数量含义。

**不可丢约束：** 一份逻辑栅格底图，各图层派生；历史/兼容地图及失败保留。真值只用于场景生成/事后评估，不进感知/路线/补数。历史不当现场库存，不确认移动物理身份。保护大量既有未提交改动，无commit/push/reset/清理旧成果；仅清理本轮临时进程与夹具。需要关键目标/验收取舍再grill-me+grilling，每轮≤3问；当前无待用户回答的关键决策。



### 2026-11-24：深度图投影候选接入前的续接原文

当前运行：新4a1e6841/domain67/8767/Gazebo+RViz，普通书碗布局/v14/S1280/书球辅助/显式记忆，冷加载find完成4秒驻留修复，当前ABBA对照中。旧8168585d已按所属控制台SIGINT关闭，shutdown stopped/残留[]，root exec39481返回143如实保留。用户暂缓v15与碗书追加优化，保留未验收和失败；不重跑球清扫。

**当前语义驻留修复候选（先看此段）：** 已证实原普通Gym find在2有效投影即提前finish，最后点dwell_completed=false、配置却4秒，基线与诊断均如此。search_node.py删除检测callback立即结束，next_view在本点完整驻留且必巡完成后found，无必巡房间也按这一检查结束，不多走下一点；计数路线/min_hits2/球拟合/TF/导航/20cm门槛不变。3项新增回归覆盖继续采样、驻留终止不多导航、不得跳另一必巡区域；完整504通过/38跳过13.32s、三包1.29s。新增测试首两次缺夹具字段/第一次路径猜错失败日志保留，修正夹具后全过，无产品断言改松。

唯一候选收据`semantic_followup/counterbalanced/dwell_candidate/audit.json`，原源前像search_node.py.before。新4a1e6841根普通书碗布局与旧三球根不同，不与原失败当严格单变量因果；本候选内部ABBA配置一致、每轮history_before保留，初始SQLite只读备份未改原数据库。exec45458 root、86340 ABBA、88872纯TF/AMCL小流观察（无图像，终态自动结束）。当前首个冷启动无记忆case通过：find1/3点/116.5635秒搜索/14.8590m独立里程计、XY .138348m/回充/接触与odom质量通过，第三点完整驻留33投影；source全窗等收尾独立审计，未先称提效或定位根因解决。随后guided执行中。

原counterbalanced基线.24765m失败不替代，geometry_diagnostic同原816根暖态重跑XY .081916m但16次源时效超界，仍fullfailed。geometry_analysis.json逐项精确复现原深度/掩膜，球心拟合确实成功、map点3.24797/4.15897、odom3.29530/4.22731；只证该帧TF贡献，未捕获首轮同戳TF，不能认定其唯一因或用odom修正运行位置。旧诊断observer/task均0收尾。下一步核对本候选四任务/ABBA/真实历史使用、数量/20cm/回充/接触/odom/全观察窗源时效，全部通过后才判断收益；若失败保留，不用后续诊断补成四次通过。

**当前执行原计划第4项语义闭环：** 同8168585d根无临时物理改动，先尝试Gym球ABBA两组（关→开、开→关），未人工删选5条原历史/误检/待核验记录，初始SQLite只读备份与每次history_before均保留。`semantic_followup/counterbalanced/audit.json`原基线首例即停：find1/实际1、3点、95.855秒搜索、134.45秒含回充，定位.247651m>.20；回充/接触0/里程计979样本无跳/源66804检查0超界均过，不能接受记忆收益，也未派发guided。runner59530已exit1，cloud0、trials1为正确性断言，memory_guidance原false已恢复，旧失败未改。诊断前APIready/idle已确认。

原有界几何诊断`counterbalanced/geometry_diagnostic`，exec92758已收尾，公共find+独立接触/cloud观察器，辅助只读observe_ball.py从原杯采集器适配真实球掩膜/同戳map与odom TF/RGB-D，未改产品或参数、未读真值下发任务。假设为球拟合失败后表面中心回退或TF偏差，尚未证实；先看实际同步数据，不能根据.247m就认定唯一原因或放宽门槛。该次不是补足ABBA通过。新收据/工具集中同semantic_followup子目录，不建新计划。

**后续清扫小阶段已收尾（原计划第2项，完整清扫仍未通过）：** 用户要求不长期困在一项，v15/碗书追加优化均暂缓。run_cleaning.py只改seed完成后、覆盖不足80%的补扫选择：预计新扫格/秒至少高25%且时间够时先补附近可达片，再重算原条带；原分母/刷盘/原条带/停车/回充/预算不变。真实旧失败快照11.9KB在tests/fixtures/cleaning_ball_remaining.*，3项新增＋相关54过，完整501通过/38跳过12.23秒、三包1.12秒，diff/py_compile过。首次pytest误收集results历史测试副本报ImportMismatch，full_tests.log保留，限定正式tests后通过。

唯一新阶段收据`cleaning_followup/ball_trial/repair_followup/audit.json`。8168585d冷根实际7439/9336=79.6808%、16/25、645.79秒，recovery_budget_insufficient，partial保留；地图回充.10427m/.09434rad/.46s、接触0、源时效0、冻结刷盘重画/原生动作顺序与停稳均过。新分支3次实际派发，覆盖增量111/121/1格，末次failed；不称整房已修好。remaining_snapshot图/JSON：未扫1897格，末次观测规划掩膜刷盘潜力内1070、掩膜外827；只是该帧潜力上界，不证明身体可执行/永久阻塞，不把外部全部归球。native三处球周围占据462/552/604帧，绕行/继续/回充子项过，独立encounter_audit另存。

对照限制：本轮原始25条、旧球场景28条；布局/rooms/nav2冻结文件逐字相同，但本轮辅助book+sports ball，旧book-only，comparison_conditions逐项记录；**不作同负载严格因果提速或同配方稳定性**。无额外临时夹具，显式三球布局与当前物理状态一致。driver3169/cost17300/录制78908、cloud/motion均0收尾，无本轮profile残留；root39481仍运行，最终API已核对ready/idle，无未知控制状态。真实UI录制后半段568.469秒/2270帧，4倍H.264片段与逐帧映射在recording/，非相机视频/非全任务录制，末帧明确partial。原WebM保留。

本轮额外补齐真实新清扫HTTP导出：统一接口clean_trace/clean_coverage各PNG/SVG/rawJSON，原result/plan/全trace/eligible/covered逐项完全一致、partial保留、无动作，exports/audit通过，map_exports总收据新增live_cleaning_http_phase；此前仅旧源离线/API隔离的限制现补为本轮实际HTTP子项，不升级清扫验收。答辩素材入口整合在DEVELOPMENT_VALIDATION顶部，卧室/杂物间无新增球通过素材仍为84.85/92.74；本轮三球只展示避障/部分完成。**下一步转原计划第4项合格语义记忆收益闭环，不再立即重跑球清扫或v15五次计数。** 当前导航配置的动态让行全回归、真人四功能仍未完成。保存摘要不是宿主原生压缩。

**当前厨房互补候选结果（原计划第1项，尚未验收）：** 独立v15仅改厨房必巡顺序/餐桌加入原互补点及cup/bottle/bowl category_views，南侧两个操作台原点→餐桌原点→原互补点，共4既有位置/4方向（杯原11方向），两处物理区域不变，餐桌2方向均有效停留后find才返回。其他房间、原v14、布局/score/.30关联/2hits/.20m门槛/NavFn+DWB不变；没有新增算法/位姿或真值指令。椅等通用回退保留，但共享前缀变化，不称所有类别已回归。

唯一阶段收据`count_diagnosis/compact_route/audit.json`，replay_compact原同步投影逐帧精确复现后保留4点，双杯/双碗/原杯3例仍2/2，仅离线保留。原39a03a7e根cold1：4次杯完整计数+1次find全部数量/≤.20m/4of4/两处/接触0/时效0/回充通过，杯计数145.27/157.65/150.85/147.03秒含回充，最大XY .11868m；find177.89秒/.09184m，不能声称所有任务提速。几何观察器0，所有cloud观察器0收尾，精确工具快照各子目录保留。

两个相关单次回归如实失败：related_bowl数量2/2、XY .06255/.05216m/4点/无接触/回充正确，但任务中55次时效超界（observer109.2039–109.4017，cloud源1077.626→1077.75→1078.0，晚到帧age.314，不能只看max_gap.285<.4），不通过完整检查。当前launch已明确min_period=.1，未盲改为更快。related_bottle数量2/2、XY .04409/.03126m正确，但返航12秒/移动0，初始2秒暖机后send_goal响应等待8秒＋追等2秒仍无handle，stop_confirmed=false；原return_result/statusfailed、return.log“导航响应或定位数据超时”及navigation.log1244行“Failed to send goal response ... client will not receive response”保留。系统按未知终态规则停止本栈并禁新任务，shutdown无所属残留。末尾73次source无效集中源停止后的关闭阶段，不据此说成返航前因，也不升级原failed。

查阅GitHub官方rmw_fastrtps **6.2.10**源码，与本机rmw_fastrtps_cpp/shared_cpp6.2.10一致：该message来自service response writer等回复reader匹配超时（MAYBE分支），不等于已证实底层网络原因。当前只定位/研究，**没有改ActionClient超时、停车/感知门槛或DDS配置**；后续可考察仅目标回复writer的有界匹配等待，并保留同源未知终态关闭防护，尚未实现/验证。

第二冷根a7540a65的cold2第五杯计数失败：1/真实2，全部4点/两处/无接触/时效0/正常回充通过，但餐桌两点valid_projections均0，clipped/size/TF/invalid_depth拒绝均0，只有操作台32投影。故4轮绿不能称稳定通过；**不得把随后诊断成功补成第5轮**。旧geometry观察器仅有cup≥.35才留图，漏检点无图；已给observe.py加--capture-all-views与all-class标签摘要，compact_trial --diagnostic只在诊断启用，精确原工具快照仍在原目录。原同配置diagnose_miss --counts1 --no-find --diagnostic已结束1/2失败，用户已暂缓，不再追加，exec95196原cold1已exit0、exec17332在碗fail后assert停批、exec93768瓶结束、exec17150 cold2已exit0，原诊断exec51337已收尾；该项恢复时再看实际餐桌RGB/标签，区分未见目标/误分类/视角，不能先假定唯一原因；如需新视点须从已观测自由栅格和实际图像校准，不用资产真值位置当运行答案，不放宽门槛。

工具/文件集中count_diagnosis：v15 JSON、replay_compact.py、compact_trial.py、observe.py、compare_compact.py（比较图尚未执行，应标候选首轮而非稳定）；当前未改产品算法，未为配置/验证工具重跑全量构建，validate_rooms/精确重放已过，上一产品工程498/38/三包2.40s仍为上轮证据。顺便只读汇总旧球清扫action时长于cleaning_followup/ball_trial/time_audit.json：15次adjusted_goal_unreached耗127.515秒，对照无球9次77.652秒；仅定位重复连接开销线索，未改算法/预算或宣称漏扫解决。活动目标继续，5次杯稳定/瓶返航/时效、散落球可达残余及完整语义收益等均未完成。

**本轮地图导出阶段已收尾，整机目标仍进行中：** 用户目标保持“今晚的目标：完成计划，对答辩展示的部分进行优化”，上一目标轮次为实质进展。按原计划第5项新增`semantic_search/view_export.py`，统一POST /api/map/export的view参数/UI下拉，{}仍为cost。7类空间视图＋真实Spark-DSG关系输出PNG/SVG/原始JSON，代码含本会话task_id文件allowlist、frame/namespace/revision与原floor/eligible/covered格数核对，观察实测到达/预设分开，完整清扫轨迹按阶段/起终点/定位断点绘制。语义M-记录和#任务编号分开、R源位置仅新鲜map位姿；关系核对真实家庭—房间及房间—物品边。导出时间与原源戳分开，cost界面采样轨迹也修为不跨断点连线。没有改导航/感知参数或真值隔离。

文件还改robot_console.py/robot_runtime.py、UI三文件、tests/test_view_export.py/test_map_export.py/test_robot_console.py；完整498通过/38跳过20.00s，三包2.40s，JS/py_compile/diff检查通过。原生源码未改，未重新跑原生专项。总收据仍`results/development/demo_two_rooms_20261123/map_exports/audit.json`，新shared_views_phase；真实8图同逻辑底图SHA一致，源会话分别保留，不称连续执行，最终图/原始数据/精确渲染源快照在shared_views_verified/。首版非目标房间地面错误灰化图标failed保留于shared_views/，修复为原room归属并核对floor_cells；断点测试曾误把图例线算实轨迹，失败日志保留，修正断言后全过。仅本轮中间成功出图临时副本已清理，摘要存总收据，原失败/原任务会话/最终素材都保留。

`ui_verified/report.json`是最终冷根真实Firefox五种即时视图（cost/occupancy/rooms/semantic/relations）15个下载、500px无溢出通过，runtime_verified.json核对最终代码SHA；隔离profile和浏览器均清理。清扫导出用真实旧刷盘/轨迹离线与隔离HTTP检查，**没有为导出重跑整房，不称当前本会话清扫HTTP全程实跑通过**；局部odom代价及全房视觉覆盖仍未实现。新增工具export_views.py/verify_ui.py/check_task_export.py复用原map_exports，未另立计划或交接。

**自动预检新失败及下一步：** 原Piper WAV正确转写“请去厨房找一个杯子。”，公共文本链路实跑find1/两必巡/3of11/132.49秒含回充、接触0/过期0/回充通过，原客户端passed；独立定位.206539m>.20，task_export/audit.json整体failed，原结果不改、不四舍五入放过。观察HTTP导出与全部原diagnostics一致、临时音频删除；这不是真人麦克风验收。新任务写入历史，当前46条记录/revision110，不是46个现场物品。自动任务/几何cloud均收尾，当前新根空闲。下一小步回原计划第1项：先查find提前结束条件和厨房首4个互补点的已保存同步数据，评估减少同点8方向及补足find互补核验；在独立配置复测数量/≤.20m/两处/回充与冷热启动，不动门槛，不把导出通过说成整机通过。活动目标仍未完成，清扫新增球可达残余、完整语义收益与真人功能联调仍保留。

**当前活动目标与本轮阶段结果（进行中）：** 用户暂缓碗书额外布局/重复验收，继续后续计划；活动目标“今晚的目标：完成计划，对答辩展示的部分进行优化”仍未完成。收据`results/development/demo_two_rooms_20261123/cleaning_followup/audit.json`。旧e5899ede杂物间8424/9336=90.23%、25/26，返航base_collision—FoldingDoor_01_002真实接触564事件，被独立观察器取消/停稳、未回充，卧室未派发；旧根已正常关闭，失败原件保留。

修复候选已构建并在冷根`20261123T161729_423600Z_b1c2928b`/domain67/8767/Gazebo+RViz实跑（两区已结束、该根正常关闭无残留）。沿用S1280/1280×960、仅book辅助、v14、新书碗布局，**nav2_depth只改local/behavior的global_frame为odom、local static_layer.enabled=false**，global map/.25半径/速度/NavFn+DWB不变。`repair/loaded_parameters.json`已核实现场参数。接触前map→odom曾大幅变化，源间隔与接触相隔45秒，不能称唯一碰撞根因；不用truth引导导航。前像`nav2_before_odom.yaml`保留，若回退须用确切前像，勿覆写其余脏改动。

产品新增`cleaning_repairs.py:offset_lane_repairs`，通过RoomSweep及run_cleaning在原条带直接修补无候选时尝试安全侧向短段；只用原漏格、实际cost与刷盘几何，候选拒绝禁行中心格、不改分母、预测不记覆盖、有限重试。冻结真实缺口夹具新增4项＋原补扫3项通过；完整回归469通过/38跳过、三包构建通过。**本轮杂物间单次独立审计已通过：8658/9336=92.7378%、26/26，629.44秒，回充误差.10018m/.09564rad/.46秒，真实接触0、过期检查0，精确刷盘重画一致。** 冻结计划证明offset分支4次实际执行，前像原条带缺4格、末态全部实际刷到；部分原生Follow失败仍如实保存，不能推广全场景稳定。卧室同根随后6767/7975=84.8527%、19/19、511.33秒也独立通过，回充.11170m/.09620rad/.46秒、接触0/过期0。本轮19条不可误写旧18条；两区观察子进程均0/无残留，驱动保存两终态审计后退出143，未宣称编排退出0。lane_probe只读跟踪原缺口，证据另存`repair/lane_cost_trace.json`。

杂物间三新增静置球布局已生成`layout_service_cleaning_three_balls_v1.json`，保留原13目标/家具/原球，另加3个.31m半径球；设计间距检查通过。上一根`20261123T164222_374641Z_1bd0ec80`/67/8767/Gazebo+RViz已在配对结束后正常关闭，显式候选bowl/book/sports ball，新增球清扫`followup_utility_clean_01`已结束：7422/9336=79.4987%、19/28、673.95秒，预算结束/partial，回充.10723m/.09684rad/.46秒；接触0/过期0/精确重画和动作停稳通过，原清扫失败门槛不改。`ball_trial/audit.json`仅避障子项通过：三处native100、原普通条带与各球相交、原生odom最近中心距.579/.588/.643m、检出后又实刷5491格。可达补扫未完成，末native刷盘潜力上界约94.72%，不能把1914未扫格全算球占据。45秒球检测同步相机抓帧超时，不当语义球验收；通用相机实帧及真实cost快照保存。观察器已无残留，驱动及cost观察退出143、原因未明，cloud/motion子退出0。球XY仅评估器使用，不进导航/感知。**当时启动同根厨房无箱/放箱实际计数对照，现已收尾见下段**：`.../route_pair/run_pair.py`（先baseline再blocked，错误即停）与只读`capture_cost_pair.py`；收据`route_pair/audit.json`。不强制北侧航点，须核对两次真实轨迹方向；语义正确案例随后。两区普通清扫PPT图片为`repair/utility/presentation.png`、`repair/bedroom/presentation.png`，原栅格/完整房间范围/实际分阶段轨迹未改。地图输出并行补了`map_export.py`、`POST /api/map/export`及UI快照按钮：带图例/源戳/会话/机器人/有效原生计划/界面采样实际清扫轨迹的PNG/SVG＋原始JSON，只接受同map的新鲜原生全局代价图。真实运行直接导出已查看；新冷根1bd0ec80实际Firefox快照按钮/三文件下载/500px无溢出通过，隔离profile/进程已收尾（能力标志保护旧后台）。含此功能的最新完整回归**476通过/38跳过20.49s**、三包构建2.82s，JS语法通过；首次全量未加载ROS导致收集错误保留，不计产品失败。证据集中`.../map_exports/`。未提交/推送，继续保护既有改动；按context-compression增量维护此摘要，非宿主原生压缩。

厨房配对收尾：同1bd0ec80根，原baseline计数2/2、XY≤.07672m、11/11/回充/接触0，但49次时效超界确在任务内，原failed保留；唯一一次同配置baseline_retry全部通过。随后放箱：原客厅已发布路径(1.09879,-3.74713)，约2m前方，真实检出后自主走家具北侧，原11点/两处必巡、两杯XY≤.13874m/无接触/回充通过。全观察窗原failed5次，均夹具准备期1768.794–1768.804、早于任务首样1771.46；task_window_audit用相邻callback包围并外扩首末任务各.5秒，完整任务132937检查/超界0，原.4/-.1门槛不变、原失败保留。两份实际首段中位y=-3.75575→.00722，北移3.76297m，不要求进gym、无强制北侧航点。证据route_pair/audit.json、actual_pair.png；系统全运行时效稳定性仍待处理，不能说首次失败已修。线程假设实测不支持，未修改线程参数。箱夹具/桥接恢复，旧根正常关闭。

**语义后续当前执行（优先看此段）：** 产品memory_guidance.py显式find最多补1个.8–2.2m现有点位朝向，历史方位仅作观察线索，必巡前缀/全部配置回退保留、count不启用。全480通过/38跳过19.14s、三包2.48s；随后验收器修正“find早停实际已访列表≠完整计划”，新增真实3访/11计划回归（相关12通过）；完整计划仍须在diagnostics存在。首次pair参数读取超时无任务，持久Get/Set客户端探针通过后重测；各实际外部工具自冻结，不能混用启动快照。唯一总收据semantic_followup/audit.json。

旧5cfd13e6原书碗布局、辅助book+sports ball、显式记忆：无记忆/有记忆Gym找球数量1、XY .13497/.17588m、接触/回充/odom质量均过，搜索122.60→71.13秒、3→2访点、实测少.80464m；仅一次先无后有，未抵消热态/初始运动影响。新增近朝向0有效投影，不能宣称其提高识别。baseline7次任务内源超界，guided86次均准备期/任务0，**全时效验收仍未通过**，单次正确性/耗时子项见benefit_audit.json；旧错误报告保留baseline_reaudit修正旁证。

随后原生Gym球移动(3.2955,4.2257)→(1.5,3.6)：find1/XY .11638m正确，但完整11点count2/真实1失败；多余位置(2.4764,3.1932)有31帧，误分类/投影污染/关联成因尚未确定，不做真值删条或宽门限。movement/audit.json保留原failed及source超界；finally已用原生set_pose恢复原球、ack true，旧根随后正常关闭。recording/ui_telemetry.webm为此失败过程真实UI遥测，不能当通过素材。

按不长期卡一类的安排，该阶段冷根20261123T181616_669356Z_86a6f7ca恢复主展示S1280/1280×960、v14/书碗原布局、仅book辅助，候选bowl/book、记忆显式true；球辅助未开，不将跨配置结果合并为稳定通过。当时movement_cup实跑：只将kitchen_yellow_mug从(6.4,.95)移到(7.1,.95)，其他12目标/家具/观察点不变，支撑/无重叠检查通过；独立变体layout_service_memory_cup_moved_v1.json和movement_cup_design.json声明。**86a6f7ca核验期间物理姿态为已声明临时移动，启动冻结仍原布局；下述冷加载后已一致**；truth仅setter及事后评估副本使用、不给公共任务，失败自动恢复，成功须冷重载变体或恢复再核验，不能留不一致。movement_cup首轮find1、两必巡/无接触/回充/62768次源检查0超界，但XY .31338m>.20失败，count未派发，原杯已恢复ack true；recording_cup为此失败的UI遥测、不可当通过素材。原工具精确快照保留。同根仅一次有界movement_cup_diagnostic复测通过：find1/XY .11687m/3of11/133.62秒含回充，count2/2、XY .17744/.09113m、11of11/227.75秒、两必巡/无接触/两任务源超界0/回充通过；memory_checks全true，旧位置待核验、新位现场记录，数量不来自历史。几何观察器0退出。独立SQLite/API完全一致，真实Spark-DSG重载52节点51边/46历史记录、全部位置/状态/证据/task/revision一致。厨房实际必巡前缀未变化，不当厨房提速收益。同步几何count首点map误差.242m而odom约.039，互补点后最终.177m，支持定位变换影响；首轮缺同帧TF，唯一成因未定，不使用odom/真值纠正运行位置。movement_cup_diagnostic/memory_change.png是实际记录前后对照，recording_cup_diagnostic为真实UI片段；旧failed原样保留。公共任务ID加随机尾防幂等旧请求，不改产品门槛/参数。86a6f7ca已正常关闭/无所属残留，该阶段后续冷根20261123T183001_627207Z_e575625b显式加载layout_service_memory_cup_moved_v1，保持同配方/显式记忆，无临时夹具；cold_reload_audit核对显式布局/生成hash/目标姿态、46记录/修订/图完整一致，ready/idle；此为重载审计，不是冷启动动作重复。新增真实记忆对照PNG及74.333秒4倍UI遥测MP4，原297.134秒/1186帧逐帧保留、无插帧/无音频/非相机片，已解码核对，原WebM保留；三个隔离浏览器profile/进程及几何观察器全部收尾。最新工程481通过/38条件跳过17.49s，三包2.48s沿用此前产品构建（之后仅验证工具/文档改动），py_compile与diff检查通过。下一步整理现有答辩素材入口并做所选配置四功能预检；不再立即扩大类别矩阵或持续调球。活动目标未完成：单次变化核验已有，合格完整收益对照、间歇源时效及首轮定位风险仍留待完善，不把球count2/1或旧失败改通过。

**当前新增碗书收尾（最新）：** 用户“继续，把新增的两个物品放进去”已落实为厨房餐桌/操作台各1碗、卧室书桌/床头柜各1书，原9杯瓶实例逐项保留。唯一收据results/development/demo_two_rooms_20261123/bowl_book/audit.json，s1280_near_bowl_book_and_cup_single_layout_passed。新布局scenes/aws_house/layout_service_bowl_book_v1.json；v13观察配置保留失败，当前显式v14_bowl_book_near保留全部两处必巡，只将卧室杯/书原两个远距离补充点收敛为原近处互补点（6→4目标/3位置），瓶及厨房路线未因此缩减。适用于所选支撑面布局，不保证任意全房摆放；垃圾桶误识未做通用分类修复。

该阶段最终根20261123T150622_424709Z_4e904695/domain67/8767/Gazebo+RViz（已于后续清扫阶段关闭），**S1280/1280×960＋仅book的YOLOE辅助**，bowl/book显式候选，记忆引导关闭；该阶段结束时已回充、ready/idle；当前运行见摘要顶部。原n640/v6默认与三类准入不改。near_mixed8项（厨房碗/卧室书/两房原杯，均find+count）全部数量、≤.20m定位、必巡、保存/记忆和回充通过：双碗/双书/两房双杯均2/2；碗count最大.07016m、书count最大.11648m，8项最大.18721m。45秒负载抽查20170次过期0，点云/scan最大间隔.19503/.26863秒，非全任务无过期认证。UI桌面/手机及档案联动通过；实际Spark-DSG独立重载46节点45边/40条历史记录与API逐字段位置/状态一致，当前2书2碗last_observed，其他旧记录可待核验，历史总数不当现场库存。

原失败保留：2a494570/S1280-v13新增碗书4项通过，但原卧室杯3/2，实际垃圾桶false cup（score.736、extent约.117/.200/.200m）；随后n640＋book辅助-v13两房杯回归通过，但双碗/双书均count1/2，均非正式准入。低分辨率漏检与高分辨率误识不能混写为单一通过。最终同S配方v14近视点8项通过，仅单布局首轮，3布局/5重复和历史map坐标分裂仍未闭环。没有改分数/尺寸/关联门限、没有移动原家具/照片规避错误。旧b027在本轮开始前已未就绪，正常关闭；本轮两旧根正常关闭，所有观察器/隔离浏览器收尾，无临时障碍残留。原资产哈希、目标间AABB/支撑高度检查及实际RGB-D留证；首次离线设计JSON bool_序列化错误修正，未充当感知失败。仅新增布局/观察JSON和本轮工具，产品算法未改，未重跑全量工程/重建ROS；配置校验/py_compile/diff检查通过。运行命令已加入RUNNING，TARGET_CATALOG/验证/总计划增量更新。下一步按原计划补所选碗书变化布局与重复、继续核对观察范围/跨视点关联，再交替清扫与语义案例；未提交/推送，保护既有脏改动。

**当前执行收尾：厨房计数首阶段（最新，用户已授权按计划逐项执行）：** 唯一收据results/development/demo_two_rooms_20261123/count_diagnosis/audit.json，selected_count_case_5_passed_historical_split_pending。旧892根仿真在本轮前正常退出/未就绪，已正常关闭残余控制台；新诊断cc4根两次计数2/2通过、3/2失败后正常关闭。只读observe.py采同戳detections/depth/info、map/odom/optical TF及视点RGB-D；本次多余实例为灶台旋钮33帧、extent最大.02713m，与旧餐桌杯ID分裂不同。首轮桌杯两视点map差.132m/odom约.023m，支持定位修正风险但非旧失败唯一根因证明。

产品仅depth.py杯尺寸校验补最大片段≥.04m，测试tests/test_depth.py；原score.35/2hits/.30关联、默认路线/导航不变。冻结同步帧回放失败3→2、正常2→2，真实杯最大片段≥.079m保留；小/遮挡杯可能拒绝，须其他充分视点。冷根20261123T114131_359953Z_b027d8ec/domain67/8767/Gazebo+RViz当前就绪空闲/已回充，完整厨房杯计数5次（首轮冷启）均2/2、11目标/两处必巡、XY最大.16562m、结果/记忆/回充/停车/接触记录0/源时效通过。**5轮新尺寸拒绝均0**，拒绝分支仅冻结失败验证，不能说旧分裂已解决。465测试通过/38条件跳过、三包构建通过，初次收集缺scripts路径错误保留；原生未改未重跑。所有本轮只读观察器结束、无新增夹具，未提交/推送、保护原脏改动。

文件/证据集中原demo目录的count_diagnosis：observe.py/audit.py/repeat_fixed.py、sync_01和sync_fixed、原count_01/02、fixed_count_01—05、frozen_geometry_replay.json、diagnosis.png、工程/构建日志、final_state.json。原历史failed未改。计划/接口/验证本次增量更新。下一步继续计划第1项跨视点坐标关联核对与两房互补点位/朝向，当前厨房仍8方向原路线；随后交替两区清扫、综合避障和语义核验，不提升扩展类别/全系统完成状态。


**最新六点计划整合（用户明确，优先于下方旧范围）：** 当前交付为完整四功能系统＋两三个有证据亮点；16类全面验收和全屋清扫转后续。已直接更新唯一DEPLOYMENT_PLAN.md，保留P0—P6分项/框图/UI/地图结构，删除旧85%、健身区主线、多轮执行安排、C系列流水和全量工时估算。两区清扫明确卧室和杂物间均优化；厨房餐桌/L形操作台、卧室书桌/床头柜为计数主场景，杯瓶椅基线、优先碗书，重点实际视野、互补点位/必要朝向与正确计数，厨房同点8朝向尚待优化。所选正式案例5重复含冷启、扩展3变化布局保留，其他类别不展开。

用户本轮两次确认：①杂物间3–4球静置散落；现有AWS球碰撞直径.62m，先3球校准净空再考虑4球。②杂物间用两组证据：无新增球按≥80%和原可达条带完成；有球另验真实检出/绕行/可达残余处理/回充，球占据受阻单列，原分母和partial保留，不把避障子例通过说成整房完整。综合避障仍客厅短路受阻后自主走靠近健身区的北侧，无需进入gym、无强制航点。语义补一个正确的记忆查找＋移动后现场核验更新；收益须先通过数量/定位，必巡前缀可能限制提效，不删必巡制造收益。地图清单新增导航代价为第7类空间视图，另附关系图；全局代价UI/清扫NPZ已有，带图例PNG/SVG导出待完善，局部图未接UI。本轮只核对源码/既有证据和更新计划/摘要，无新任务或验收，原失败/配置/进程未动。下一步按计划第5节，先重复计数与两房观察策略，再交替两区清扫/综合避障/语义核验和地图素材。

**最新避障素材构想及用户澄清：** 用户指无障碍走客厅较短一侧、途中受阻后自主改走靠近健身区的北侧通路，到厨房执行任务；**无需进入健身区、不要求越过y=1边界**。此前将进入gym作为条件属理解过严，已修正唯一总计划。旧living_kitchen_count_01/no_return/route_count_01实走中部家具北侧，方向符合构想；已有原计划对照，但若称无障碍/有障碍两次实走，需对应两份实际轨迹，不能把计划线冒充实走。原厨房点不变，由真实感知重规划，不强加北侧航点。本轮只核对既有JSON/轨迹图并改文档，未启动任务、未改产品或原证据。

**最新用户取舍与本轮审视（优先于下方全量扩展安排）：** 答辩不做现场演示，提前整理素材进PPT，长任务可加速/截取关键片段；本轮仅核对可展示功能与成果，不启动新任务。16类全部验收、全屋完整清扫不再作为答辩前置；四功能统一系统、真实结果及失败保留。选材建议已写回唯一总计划顶部：卧室为清扫主例、杂物间为补充；厨房餐桌/操作台为寻物计数主候选，卧室书桌/床头柜为补充，客厅用于途中避障；这些是评估建议，不伪称用户已经最终选定。卧室85.81%/18条单次完整，杂物间旧88.60%/26条完整但最新90.08%/25条partial，厨房最新重复杯3/2失败，均须注明版本与限制。

重点拓展核查：SQLite、真实Spark-DSG、语义/运行/房间关系三视图和档案联动已有实测，计划旧“关系图待实现”已校正；历史待核验/新现场记录有子例，跨移动物理身份没有。记忆引导默认关闭，101.88→30.05秒对照因定位.2254>.20未过，主动补点没有有效手机投影增益；不能当已验证提效。建议集中补一个正确的记忆查找/更新案例，协同清扫、续作/低电量、组合任务、导航比较及其余类别列后续。本轮核对老师原始docx、源码、实际收据和语义截图；原件未规定16类/覆盖数字。四项日常避障矩阵改为约定代表检查通过，保留完全封门子例未测。HEAD737aadb、检查时181项既有Git脏条目，未动产品源码/运行进程/历史结果。仅更新现有计划、要求对照、物品清单和本摘要；本次未新做验收。三个集中证据目录有图片/数据、未找到mp4/webm/mkv成片，不把日志称为已有视频。保存本摘要不是宿主原生上下文压缩。

**唯一总计划为 [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md)。P1–P3 三类目标的原冻结基线通过，P4/G0 和 P4a/G1 自动验证通过。P4b 已接入清扫，短程及完整预算返航已有通过，完整覆盖仍待验收。** 已确认至少16类按常用区域验收，日常避障收敛为4项；语义地图和自主补充观察为首轮重点。先整体打通，再逐步完善，增加局部避障测试。物品验收维护在 [清单](TARGET_CATALOG.md#5-物品验收清单)，真人麦克风安排已由下方11月22日用户决定提前。C019 的持久记忆与开源场景图接入子任务已实测通过，默认正式可调用仍三类，其余类别需显式开启验证，C020 已修复多模型材质并完成六项候选初探，C021 主动观察已完成首轮实测，C022 清扫仍未达标，C023 已有专项通过、最终配置待验收；尚未达到新增类别准入。

### 当前目标与已确定方案

**用户恢复后本轮收尾（2026-11-23）：旧占据清除与UI修复通过，计数重复稳定性仍失败。** 唯一当前[修复收据](../../results/development/demo_two_rooms_20261123/clearing/audit.json)，clearing_fix_validated_count_repeat_failed；当前根20261123T080640_573935Z_892635c1/domain67/8767/Gazebo+RViz保持就绪空闲供查看，三次任务结束、所有临时箱/校准球/桥接/观察器均收尾，无清图或任务间重启，未提交/推送。原4c失败及暂停记录均保留，原暂停已由用户明确解除。保存摘要不是宿主原生压缩。

- 归因与实现：真实原始云/深度图均62476个正Inf且逐像素匹配，NaN/零/负Inf为0；像素中心+.5与有限XYZ匹配中位误差1.72e-7m。原生冻结射线覆盖重放表明只改3→4m仍留高处潜在体素，需保留无回波自由射线。默认适配器新增独立/rgbd/clearing，有限实际返回＋经新鲜无畸变内参验证的正Inf量程射线；NaN/零/负Inf不生成自由空间，少于8有限点或几何不匹配不补射线。仅仿真launch从实际传感器clip/far=8m显式启用，默认max_depth0关闭；源旧/rgbd/obstacles有限点标障/.08–1.1m/2.5m不变。原生depth_clear仅清除、不标障，端点高度过滤-8..8后由原生VoxelLayer裁剪、raytrace4m、expected_update_rate .4s，NavFn/DWB/轮廓/未知和静态地图规则不变。产品文件clouds.py/cloud_adapter.py/development.launch.py/nav2_depth.yaml，未改body/安全候选；SDF读取仅传感器标定，不读目标真值。
- 完整实跑：no_return/route_count_01箱始终保留到任务结束，杯2/2、11/11及两必巡区、定位误差.02872/.04198m、回充(.10498m/.09747rad/.46s)通过；传感检查137438次过期0，mark云max gap.29044/scan.35636秒，清除流在独立观察器中同样要求≤.4秒。物理箱清理后同根cost85→0→0，无清图/重启。第二次完整计数实际沿旧箱通道通过，原位置map中心最小实走.02249m/原生计划.02161m，11/11/必巡、停稳与回充/接触记录0/过期0通过，证明旧禁行已解除；但其数量3/实际2，原failed及followup断言失败保留，不把连续完整计数改成通过。字段/证据分别在no_return/route_count_01/audit.json、post_route_clearance.json、repeat_count_02/report.json、repeat_count_diagnosis.json。
- 相关移动障碍回归no_return/moving_regression通过：连续低速2.12秒，障碍清开后继续任务/回充，实际箱接触源落球校准、机身/箱体接触记录0、全部夹具恢复。464项Python通过/38条件跳过12.47秒，原生3项通过，三包构建通过。单次冻结覆盖诊断工具移入clearing/frozen_ray_replay.cpp，不作为产品构建目标；原生地面清除回归depth_clearing.cpp保留。UI真实24次绘制0缺层、隔离6秒HTTP失败保留并标过期后恢复；no_return/ui_stability/ui_report.json，桌面/500px通过。巡视点含4位置/11目标，返回阶段沿用感知结果状态；各方向按实时进度/最终诊断变绿，底层8朝向路线没有改。
- 剩余与下一小任务：第二次餐桌视点0确认ID1(6.11365,.95868)，视点3确认ID3(6.42397,.92338)，各32hit、相距约.312m，超过原.30关联门限，疑同杯因坐标/观测误差分裂；原任务没有map→odom时间史，尚未证明唯一原因，不能加大合并半径、改真值或只升min_hits掩盖。下步有界采集同步detections/depth/odom/map→odom并核对物理实例，接续原物品/语义地图质量任务；16类/多布局/重复计数及杂物间短条带状态不提升。只有实际重新观察到自由空间才能清除；被遮挡/超出有效视距的历史占据仍保留，不按时间或仿真删除真值擦除。

**此前地面清除阶段（已由上方无回波修复接续）：** 基线131根静止箱体在(0,-4)实测0→100→100，移出18秒仍占据；raw已有约8888地面点/帧，原生清除端点minz约.0991m。默认nav2_depth的local/global已分离depth标障(.08–1.1，markTrue/clearFalse)和depth_clear真实地面清除(-.05–1.1，markFalse/clearTrue)，同/rgbd/obstacles、原范围3m，其他规划/DWB/半径不改，body/安全候选未改。旧默认完整YAML保留clearing/baseline/nav2_depth.yaml及根冻结副本。4c根同会话两次静止移入/移出0→100→0，通过；真实障碍/遮挡/未知/静态/重新出现的原生测试3项通过、工程461通过/38跳过10.71s。旧原生测试夹具射线未交体素失败、初次Python旧配置断言2失败均留日志，已修正夹具和明确新默认/历史body差异，不掩盖产品实跑失败。

**此前4c根失败（本轮修复已复测，原件保留）：** 修复后完整route_count_01实跑餐区计数与回充通过，但物理箱清理后点(1.09985,-3.73983)在同根45秒仍99；continuous_clearing_followup.py据失败门槛停止，第二轮计数未派发。现场静止只读冻结retained_diagnostic.json/npz保存原生lethal列、实际raw地面点（旧箱附近655点）和clearing_endpoints；旧列分布约x.715/.765与1.165–1.315，尚需把真实射线、3m距离/离散采样与map→odom历史投影逐一核对，不能仅据minZ认定唯一原因，不能用真值擦格/放宽轮廓或重启充当修复。根在用户暂停时关闭，失败原结果未改。恢复后从这些冻结证据做有界归因，再复测完整路线→移除→同根再次计数及相关回归。

**UI追加工作与验证：** /api/costmap独立返回原生global栅格（不塞/api/state），同一底图可切“底图＋导航代价”，红100障碍/橙99禁行膨胀/黄1–98代价/灰未知。后续按用户反馈修显示闪动：实测API源龄可近2s，加1Hz网页轮询会触碰原2.5秒逐帧隐藏；UI显示租约改4s、只替换有效新帧，断流保留上一帧并明确“已过期”且淡化，不改导航.4s保护或真实地图。真实Firefox在ui_diagnosis/ui_report.json记录24次绘制缺层0、隔离浏览器模拟6秒HTTP失败正确过期/保留/恢复，桌面/500px通过。前两次页面测试因隔离脚本环境记录不到主页面原型，后一次初始等待不足，均保留，最终在页面上下文通过。当前root启动快照UI是热修前版本，后续审计按当前三UI文件另取SHA。

“所选物品观察点”已改为“预设巡视点与朝向”：渲染与后端同顺序合并inspection_views和category_views并去重，实际厨房杯为4位置/11目标（包含餐桌、操作台2处、另一视点），当前目标橙/完成观察绿/预设灰；去掉重复方向造成的“9次观察”标签，显示P号及真实朝向数。它是预设路线图，不是实时物品检测点；任务运行时跟随实际房间/类别。底层v6同位置8朝向路线本轮没有优化，不能声称改显示就提升巡视效率。产品文件scripts/robot_monitor.py/robot_console.py、nav2_depth.yaml、ui三文件；回归tests/test_robot_monitor.py/test_development.py/test_body_footprint.py及service_navfn/test/depth_clearing.cpp/CMakeLists.txt；验证脚本/数据集中原demo目录，不新建平行计划。

**追加用户场景已实跑（客厅→餐区计数，2026-11-23）：** 用户要求在实际餐区计数途中遇杂物后绕行，按固定点观察完成并回充。原1a9f7587/default根通过公开API执行daily_9b9f86d55c6b_task/kitchen/cup/count，.5×.5×.8m箱经场外落球校准后，移入已发布客厅路径(.94898,-3.80388)，距当时机器人map中心2.351m；约1.119秒后原生global该点由40→99，实际最近odom中心距箱中心1.529m。机器人改走另一侧绕过中部家具，保留全部原目标；餐桌/拐角操作台必巡和11/11观察、计数2/预期2、编号定位XY误差.06393/.06067m、回充(.12245m/.09571rad/停稳.46s)均通过，总265.86秒。箱一直保留到完整任务结束，无中途挪走/改目标/真值补数/清图；机身及经校准箱体接触记录0、独立点云/扫描过期检查0、观察器退出0。此为额外集成代表实跑，不变更原清扫或多类别稳定准入。统一子证据[living_kitchen_count_01/audit.json](../../results/development/demo_two_rooms_20261123/living_kitchen_count_01/audit.json)、actual_route.png及ui_final/obstacle_ui_desktop.png；encounter_trial.py新增route_count分支，audit_living_kitchen_count.py独立事后评估，原历史三分支行为保留。本轮无产品源码/导航参数改动，验证工具py_compile通过。

**此前1a9收尾（历史，已由本轮修复接续）：** 移除物理箱后，旧会话原生global该点仍99（post_cleanup_cost.json），不能认定自动清除已通过，也未证明是哪一感知层/新自由观测是否覆盖；不能用场景真值擦格。保留原任务通过及此独立缺口，正常关闭1a9f7587（shutdown stopped、所属残留[]），同默认配置冷恢复20261123T050136_911553Z_131a176e/domain67/8767/Gazebo+RViz，原点cost两次0，已就绪空闲在充电处。恢复只用于测试环境收尾，不当作旧占据清除修复。新根冻结的UI已含突出卡片；旧任务证据/完成页面仍保留于原会话/上述ui_final，当前新会话无正在执行任务/临时箱/观察器。下一有界任务应核对旧占据的新自由观测及分层清除，再继续杂物间短条带与原物品/语义工作，不扩大矩阵或开启Smac。

**11月23日最新用户决定与实测（优先于下方健身区安排）：** 展示分区为卧室/杂物间，先测试两区清扫完成与既定4项日常避障；另要求在统一UI直观呈现。固定当前默认n640/v6/service_surfaces_v2/NavFn+DWB，未启用body/安全候选/aux/记忆引导，未启用Smac、P5不开始。唯一[阶段收据](../../results/development/demo_two_rooms_20261123/audit.json)，test_stage_completed_with_followups；主开发仍in_progress。

- 本轮完整清扫：卧室6843/7975=85.8056%、18/18原条带、603.94秒、map回充(.09045m/.09522rad/.46s)，单次通过；杂物间8410/9336=90.0814%、25/26、657.03秒，预算结束/回充(.10455m/.09628rad/.46s)，仍partial。两区冻结源码独立重画一致、动作顺序/停车通过、接触记录/过期检查0，观察器退出0。杂物间18号短条带4个未刷中心格末次live cost均99，不缩分母、不因面积高就改为完成；utility/remaining_diagnosis.json留证。历史88.60%/82.92%不混作本轮成绩。
- 4项代表实跑通过：杂物间现有家具绕行到原目标、两区普通门口进出；卧室临时移动箱接近时减速（连续低速1.76秒），障碍移开后继续寻找/回充；杂物间持续门口障碍被原生地图检出，实际经另一通道完成10/10巡视并回充，未宣称完全封门后的停车用例。夹具接触源落球校准通过，机身/夹具接触记录0，全部临时模型/桥接清理，无清空代价图/传入真值答案。routes_audit.json、encounters_audit.json及实际轨迹图集中同目录。
- 新增UI只读避障呈现：scripts/robot_monitor.py按真实/scan+同戳TF/odom和原生/plan提供telemetry.obstacle/navigation_path，地图橙色实测点/近障圈及蓝色规划路径，显示距离/方位/v/w、近障运动/速度接近零/过期、最近观察事件；终端打印[避障观察]。.70m为中心距离提示阈值，不改导航/安全边界；激光/odom>.4s过期不展示有效观测，path>2.5s隐藏，激光图层不冒充全部深度障碍。改动ui/index.html/app.js/style.css、tests/test_robot_monitor.py；同一逻辑底图，无新地图副本。实际Firefox桌面及500px宽检查通过，未宣称390px；obstacle_ui_near_live.png为真实近障截图。109相关/460全量通过、38条件跳过13.29秒，JS语法通过，无需重建ROS包。
- 用户随后要求UI更突出：仅静态UI热更新，大状态标题21px、距离/速度27px独立卡片、近障整卡橙黄/粗左边、最近事件默认显示（保留5条、可滚动），观测说明折叠。真实桌面/500px页面与JS语法检查通过；ui_emphasis/ui_report.json及obstacle_ui_desktop.png留证。近障配色只做CSS状态检查，本轮未新增机器人运动/避障试验，不改上方四项单次验收。当次根1a9f7587启动冻结UI副本为改前版本，集中audit.ui.emphasis_followup另存改后且与HTTP实发字节一致的三文件SHA，避免混淆源码证据。
- 夹具清理后关键路线demo_final_bedroom_find_01：找到1杯，书桌/床头柜必巡完成、自动回充(.09598m/.09468rad/.46s)、停稳/接触记录0/过期检查0通过，key_route/report.json。第一个根b8465695已正常shutdown/无所属残留；该次根20261123T042934_498721Z_1a9f7587随后完成上述餐区集成试验并正常关闭；最新运行根见顶部收尾状态。代码737aadb及既有大量脏改动保留，未提交/推送。
- 下一小任务为杂物间短条带禁行格的有界核对与补扫，不重开健身区/Smac优化；保持卧室展示结果，随后沿原物品扩充与语义收益顺序继续。四项为两区代表单次实跑，不扩为复杂矩阵、不据此宣称全部场景/实体停靠精度验收完成。

**C041当前要求（2026-11-22，优先于C040）：** 清扫≥80%且全部可达原规划条带实际覆盖，不触80%提前退出，重点卧室/健身区；扩展碗/苹果（餐桌+操作台）、书（书桌+床头柜）、杂物间/健身区球。≥3独立变化布局、选定完整计数案例5重复含冷启，寻找同步检查变化布局，数量梯度合并布局、不展开机械矩阵。语义优先查找提效/移动现场更新，计数完整现场巡视。当前展示沿用NavFn，健身区轮廓规划候选暂缓；其余已定要求不重复询问。Git仍737aadb，既有大量改动保留，未提交/推送。详细事实/文件/证据统一[阶段收据](../../results/development/integrated_expansion_20261122/stage_summary.json)，in_progress；保存摘要不称宿主原生压缩。

**此前用户安排（已由本轮两区展示安排接续）：** 先处理健身区漏扫，随后汇报物品扩充/语义地图/日常避障/真人语音等其余任务实际状态；客厅与厨房的完整清扫验收暂缓，不继续串行执行这两房。本轮已做默认与显式body的完整核对，健身区仍未通过；当前进度与待确认选择以下方最新状态为准，客厅/厨房不派清扫。

**健身区当前修整（2026-11-23，尚未80%验收）：** 默认本轮最高76.27%；唯一集中证据[footprint_trial/audit.json](../../results/development/gym_completion_20261122/footprint_trial/audit.json)，上层默认审计不覆盖。保留80%+全部可达原条带实扫、11156参考可扫格/.50刷宽/.35pitch/.35m/s/720秒；客厅/厨房清扫暂缓，之后汇报其余任务。默认圆形nav2_depth/v6/布局/原地图字节保留，Git737aadb及既有大量脏改动保护，未提交/推送。

**健身区上一轮显式配置（本轮未启动）：** `--body-footprint --rooms-file src/semantic_search/config/rooms_aws_house_v12_body_transit.json`，n640/service_surfaces_v2/auxNone/guidanceFalse/三类准入。nav2_body_footprint：local为含全部碰撞体的8点外包、padding **.03**、**6×6m/odom**，local static_layer.enabled=false（实时激光/深度保留），global为同样包含全碰撞体的.40×.36m矩形、padding .01/map；behavior_server配套odom。Footprint.scale=.4（Humble乘.05后才是原有效.02，41评分确认）；NavFn仍非SE2保证，DWB完整边缘硬碰撞检查保留。v12仅gym连接筛选.22/附加0，参考中心仍.32+半格/eligible11156不变。深度minheight.02/原160×120/.1周期/时效门槛不变，两个depth关闭footprint_clearing；共同三BT以Wait1秒观察重试替代清整图，保留原生重规划/Spin/BackUp。新padding .03≥半格.025，依据左趾拒绝与背面解除的冻结交集校准，非已测误差上界，须验证背面可通行，不能盲放宽。

**失败与局部通过分开：** body初版3ca完整52.46%椅002接触、f838低高度完整36.43%支架—杠铃接触均取消/停稳未回充。原生清局部图后续接触有日志顺序；无重置时盲区杆仍保留5秒，不能把盲区当自然丢图的已证根因。ea50权重校正后背面161格/回充与4接近+5绕行局部通过，但完整25.41%/3/24且回充失败，旧格持续拒绝全部候选。局部改odom的94b2完整25.38%/3/23、211.99秒，尚余451.09秒因恢复实际落global99而提前结束，map回充.10786m/.09597rad/.46通过；旧恢复目标距禁行区不足.12到点容差。已新增恢复端点整个.12圆盘验证，必要时取最近30秒连续实走.4–.85m有余量锚点，原实际停车/安全复核不变。测试真实夹具tests/fixtures/cleaning_recovery_arrival.*；补丁arrival_margin.patch。后续4c67完整61.38%/7/23、320.99秒又遇base—椅001接触47事件，观察器取消/停稳、未回充；这些原结果不改，上述根均正常shutdown无所属残留。

**最新低趾事实与修复依据：** left_chair_sensor_audit.json已核实本根完整world与001网格SHA；接触片约2.7–13.7mm，低于.02过滤线，历史5113低脚点离本次片最近.0686m，未证实接触趾曾被擦。末次低脚观测时该片可能仍在原3m局部窗外；扩大到6m以纳入全部2.5m源范围和相机偏置。后时冻结图重放接触姿态padding≥.03会硬拒绝，但非接触前证明。保留minheight，不直接改.025×16细体素（1m传感原点会越界失去raytrace），没有新增传感器或换规划算法。真实低云/voxel后时快照/接触/完整world均在arrival_margin_full；94b2还保存422帧低点/TF，同一3598点按末TF重投差中位.1282m/max.18685，证明投影变化但非原生格子出生唯一因。

**当前健身区状态（2026-11-23，本段为最新）：** 尚未完成80%验收，原正式默认未替换。当前无运行根/任务：最后5e0c102d gym_turn_room_01实际6316/11156=56.615%、8/23原条带、612.03秒；验证器因90.417秒无新增覆盖且净移<.10m调用取消，原生结果canceled、停稳确认、未返航，不能改写为自主恢复失败或回充成功。机身/支架接触记录0、点云/扫描过期检查0，四观察器退出均0，根已正常shutdown无所属残留；完整独立重画/实际world诊断见turn_full/audit.json，实际图actual_coverage.png。历史默认最高76.27%、body旧配置78.89%/15/23且返航失败仍保留，不算本轮达标；客厅/厨房完整清扫继续暂缓。

**本阶段源码与实际配置：** 新src/service_navfn包的CellCenteredNavfn复用安装NavFn求解器/生命周期/容差，仅统一floor索引/格心输出；冻结3个请求点实际88/88/93被旧round读到相邻99，cell_coordinate_audit.json有实证。OdomObstacleLayer/OdomVoxelLayer复用原生感知缓冲/MessageFilter/raytrace/持久体素存odom，每轮投真实lethal回原map，不以free/unknown擦静态或开放未知；TF/范围错误令native current=false。额外4m缓存仅射线存储，不扩大逻辑底图。显式body实际local6m/odom/真实8点/.03/staticFalse、global map/完整矩形.40×.36/.01/staticTrue及原生odom感知投影，其他源和DWB硬碰撞保留。body清扫checker .04、general .12、dock独立.15；NavigationRun的lane_start成功还须原请求≤.12，否则adjusted_goal_unreached保留原生action_status=4与停车证据。NavFn仍是点栅格规划，不宣称SE2路径保证。默认圆形nav2_depth/v6、原地图和service_surfaces_v2字节均未改。

**清扫小缺口与掉头点适配：** RoomSweep.required_lane_repairs在默认主遍历之后优先补原中心线实际缺口，不受普通.04m²面积门槛忽略，每段≥.14m、近似段最多2试，动态障碍/未知/原分母不变；fixture cleaning_required_stripe.*来自旧完整冻结实跑，99.991%/22of23为单独保留一个实际漏格的测试构造，不是真实新成绩。execution_segment仅v12 gym turning_radius .321启用，按真实占据/未知整格方块检查转向圆（实8点padding.03最大半径≤.281+.04原生误差），沿原条带内收0/.05/.10/.15m；大幅入口转向差>.4rad且接近距离>.35时主动预留最多.15m，仍须现场free/转向检查。短段可只到安全中点，但须实际完整原段已刷且停车才算完成；原路线/11156/80%/全原条带/720/.50刷宽/.35pitch/.35速度不改、不授计划覆盖。source run_cleaning item记录execution_segment/original_lane_id/required_centerline_cells，未扫原尾仍入队。新增3项漏格及4项掉头回归；最新457通过/38条件跳过10.96秒，原生2项通过、独立停车协议27项47.66秒通过，最新三包1.56秒（仅补装原生包LICENSE，不改控制代码）。这些改动尚未证明整房收益，不宣称成功优化。

**真实局部与失败分开：** 7e12ca76同Native坐标/全局odom记忆配置，south_odom_projection全部7目标/原请求≤.12，rear_odom_projection三接近+后方.5m实际175格=.4375m²均通过，map回充分别.11494m/.09759rad、.10891m/.08490rad/停稳.46；接触/过期0。双椅原南侧直接接近65秒超时/回充通过保留，改经已验北侧后both_chairs_odom_north 5接近+原8目标/.35全部通过、回充.07499m/.10518rad/.46、接触/过期0。随后3056aa2c整房4.53%/0/23/134.78秒，尚余525.71秒在第一条带原起点转向受阻而恢复失败，map回充.06362m/.09743rad/.46通过，接触/过期0；projection_full/audit.json保留。994e两次first_stripe_turn没有执行目标段：首次工具错误预期baseline也应通过，启动前断言失败/零移动；恢复原baselineFalse/candidateTrue判据后重试，入房后实际地图已分割旧整段，安全拒绝发approach/strip，回充通过，不作内收通行成功或失败。上述根均正常shutdown。更早c311精确接入/返航失败，7f原工具passed但请求点.37449m独立审计False，均在对应文件保留，不升级验收。

**最新停滞证据与限制：** turn_full/footprint_replay.json及terminal_footprint.png以最后654.88秒原生local voxel及同戳odom机身姿态重放，单用真实marked列便使本机完整padding.03轮廓得254；原始body或padding.01得0，而.02/.025/.026/.03均254。机器人中心点与完整安全轮廓不能混为同一可行判断，不能靠改速度、抬高度、擦格或直接减padding复用此回放当解决。回放缺激光/未知/膨胀，是正命中下界、非控制器内同步快照；也没保存最后原完整NavFn路径，不能把NavFn当唯一已证根因。原生BackUp同样检查t=0的完整轮廓，已有占据重叠并不能保证用原生倒车脱困。未启用倒车或Smac。

**健身区候选准备（本轮暂缓）：** 已按grill-me/grilling要求读两SKILL并委派fresh-context只读事实审查；shape_lattice_candidate_review.json与nav2_body_lattice_candidate.yaml/lattice_candidate_preparation.json已准备、YAML/差异/控制集SHA/全局包含局部外包核对通过，没有节点/规划器/动作启动，也没加入产品启动开关。候选为安装Nav2 1.1.20 Smac Lattice的5cm diff原语（112含32原地转向、16heading含所有cardinal），只前进/原地、无平滑/倒车；global矩形保持、padding仅.01→.03，使其包含local padded外包，可能更保守拒绝窄路。tolerance .12、原请求位置复核保留。任意yaw量化最大约.232rad及转动中间采样/本地姿态跟踪有缺口；DWB硬保护仍须保留，不能保证整房成功。已有异步单题询问是否允许这一次候选短测，尚未答复：总计划固定NavFn，P5比较仍暂缓，不把沉默当授权。确认后才在同一启动/UI入口显式接入，先静态路径/转向/后方/返航短测再整房，不做算法矩阵、不自动提升默认；若用户坚持NavFn则沿原算法继续调查。其余任务真实状态在stage_summary.other_tasks_review，之后按用户要求汇报。Git737aadb、既有大量脏改动保留，无提交/推送；保存本摘要不是宿主原生压缩。

**C041定向补扫/其他房间子阶段（2026-11-22，已收尾）：** 用户确认完整主条带后对未扫地面换方向补扫。cleaning.route新增网格横/竖方向筛选，uncovered_only按有增益的连续区间拆短段，不再从首个漏扫格连至最后一个跨过大片已扫地面；remaining_lanes优先垂直于原主条带的方向，无有效安全候选时回退，仍用原实时可通行/连通/尝试去重。run_cleaning仅在默认原条带队列之后接新补扫，并保存orientation/preferred_orientation；预算调度实验仍关闭。原eligible/.50刷宽/.35pitch/80%且全原条带/.35速度/720秒/附加1格保留，不强行全房第二遍。3项新增回归修前失败，最终397通过/29条件跳过9.89秒、两包1.16秒。五房冻结主路线及分母完全一致；隔离残余块旧2.95m连接改两段各.70m，3份真实冻结残余掩码安全/覆盖不增加核对通过（这些快照新旧最优候选相同，不当收益）。证据统一[本轮审计](../../results/development/cross_supplement_20261122/audit.json)及changes.patch/replay，接回原C041阶段与清扫收据。

**新杂物间实跑结果：** 冷根db55cffc默认n640/v6/service_surfaces_v2（aux关闭/guidanceFalse），公开API cross_utility_full_01，8272/9336=88.60%、26/26原条带实际覆盖、588.82秒（控制台590.10）、completed/saved，map回充.09312m/.09573rad/停稳.46秒通过。仍1064可扫格=2.66m²未扫，不能说100%；冻结源逐格重画与原报告/空间检查一致。51个已接受动作全部确认停车，最短终态后等待.461秒、动作顺序通过；4个原Follow失败保留，最终物理刷盘仍补全原条带。此次remaining_floor尝试0，主遍历即达标，未实跑新垂向补扫、不宣称其节时/覆盖收益。全任务点云4700份、最大间隔.18175秒/源龄.106，扫描最大.23974秒，300156次时效检查过期0；未新增独立world停靠精度/全程接触/4项日常避障通过结论。实际覆盖图results/development/cross_supplement_20261122/actual_coverage.png。

**各房间与当前运行：** 卧室历史单次82.92%/19条及回充通过，最终当前配置仍需回归；杂物间本轮单次88.60%/26条通过；健身区本轮默认最高76.27%仍不达标，主遍历/器械后方受阻保留；客厅和厨房/餐区均共用清扫实现，但未找到完整清扫结果，不能据寻物/返航代替。db55cffc及准备根e8010a52均已关闭；实际活动根/任务以上方最新段为准。新任务前先查实时API；Git737aadb、大量既有脏改动保护，无提交/推送。下一小步按既定优先级有界处理健身区主遍历/后方接近，客厅/厨房清扫按用户要求暂缓，随后汇报其他任务并继续既定类别/语义项；继续交替类别/语义任务，不能把单次新房通过说成五区稳定验收。

**C041最新点云链路修复（用户要求修复后已实测，2026-11-22）：** 普通开发启动原来将控制/图像/大点云共用桥，adapter以best_effort收原云、.25秒降采样且保留多余字段；现复用既有候选的四独立桥（控制、RGB-D、原云、接触），原云RELIABLE/depth1、周期.1、紧凑XYZ，原160×120采样密度、源stamp、最大输入年龄.25和诊断.4秒门槛不变。只改development.launch.py与新增只读validation/cloud_continuity.py；Nav2/半径/速度/默认三类/aux关闭/房间v6/附加1格不变，原fortress基线保留，未启用CollisionMonitor默认。实际GetParameters确认生效。属于链路组合修复，未孤立证明UDP/内核机制。证据统一[本轮审计](../../results/development/cloud_continuity_20261122/audit.json)，接回C041既有阶段与清扫收据。

同场景轻量无GUI各45秒：修复前点云最长1.35084秒/35次间隔>.4，修后.16798秒/0次；移动120秒最大.23344秒，轻量GUI180秒.16663秒，高分辨率1280×960/S1280 GUI静止45秒.21300秒，修后四窗扫描/点云过期检查均0。高分辨率未启用辅助YOLOE，未证明所有未来负载。GUI公开API“去厨房找杯子”140.31秒completed/saved，实际找到1杯、餐桌和操作台必巡3/3完成，map回充误差.05333m/.09564rad、停稳.46秒通过；未独立验world停靠精度或4项日常避障。全套394通过/29条件跳过10.15秒，两包1.18秒；早期测试误收third_party/缺ROS环境、GUI观察器误用任务ID字段均保留并修正，机器人原产物未改。

**此前点云修复收尾（当前运行见上方）：** 器械背面局部复测已实走25.939m，全程无诊断过期中止，但.12m/s接近动作180秒超时，未到.5m待测段；确认停车后map回充.09498m/.09507rad/.46秒通过。不能将数据修复算窄区/整房覆盖通过，默认附加1格保留。四个本轮实例2a186b2a、3ebdb855、d648816e、dc6e6a35均正常shutdown、无所属残留，观察器均已结束。Git仍737aadb、既有脏改动保护、无提交/推送。下一小步有界复核接近路线的实时连通/分段接入与超时原因；传感只读观察保持，随后交替接续类别0/5与5重复、语义查找/更新收益，避免持续盲跑整房。

**清扫与刚修复缺陷：** .50刷宽/.35pitch/720秒/.35速度及安全/停车门槛保留。dccfcf2c卧室6613/7975=82.92%、19/19条、572.05秒、回充通过，仍1362格未扫、仅单次子检查；同根gym8363/11156=74.96%、18/22条、回充通过但覆盖失败。最新6970同v10/v3_C显式候选gym6114/11156=54.80%、7/25条、409.56秒及回充.10354m/.09042rad/.46通过，原因remaining_lanes_exhausted，非预算耗尽；附加独立world里程计核对充电点位置误差.18646m>.15，map停靠虽通过，不能称实际世界停靠精度通过，原结果不改；初始实时掩码/场景/模型与前根不同，不当孤立提速对照。冻结源码逐格重放一致。最终实测当前位置的connected_center_cells=0，next_lanes却破坏性清空pending；用同一实跑末掩码回放，旧队列25→0，新逻辑25→25。已修run_cleaning.next_lanes在该状态保留队列，sweep_remaining最多2次复用已有安全锚点恢复；失败明确终止，不虚报扫完、不放宽掩码/分母。新增3项修复前失败、修后全套386通过/29条件跳过；本轮semantic_search目标包构建通过（首次目录发现/脚本导入错误均保留），此前两包构建证据保留。新完整实跑见下方活动根，尚不宣称覆盖收益。

**末端评分事实：** 新dwb_scores只读工具65秒普通导航202样本通过，6970全清扫有真实评分/独立motion；73个靠近终点的零线速样本，均有完整评分的前进候选与原地转动同分。官方DWB严格更小才替换best，支持离散代价同分停滞线索。原Goal/PathAlign/障碍评分均保留；原生Twirling scale.1仅离线对保留候选重评分有更低前进解，候选放results/.../candidates；已完成单项YAML差异校验及实际参数Twirling=.1/.35速度/.12容差，单次实跑71.77%/15/25条，未证明整房收益，已关闭根并恢复原YAML与测试断言，不当实际节时。采样工具已修正all-illegal时best_index=0并非真实选中命令的标识。原.133m末端失败/截止取消全部保留。

**新增类别实际结果：** v1_A仅碗2/2通过，苹果0/2、书1/2、两房球0/1失败；v2_A+S/免提示E的碗2、苹果2、书2、杂物球1通过，gym0失败（完整可见报balloon）。B旧免提示8任务5通过3失败；改显式S1280+提示E仅书/球及v9视点后B10/10通过（碗1、苹果1、竖书1、杂物球0、gym2，均find/count）。v2_C10任务7通过3失败：书find/count3、gym find/count1通过；碗count2/3、苹果count4/3、杂物球count1/3失败，全部回充。FCL确认操作台碗/苹果源网格相交；v3_C只移碗，保留原C和数量；v10只增杂物间较远点、保留旧3点，静态净空.9m连通。6970相关6项复测4通过2失败：碗find/count3通过、苹果find通过/count3正确但餐桌XY .248/.259>.20失败、杂物球find通过/count1/3失败。新增点未提升完整数量；9点RGB-D完整。球仍有裁切/balloon误分类，不做balloon别名。v2_empty碗/苹果/书0例已预定义未实跑；数量5梯度、正式5重复和稳定准入未完成。正式默认仍杯瓶椅。

**定位诊断：** 修正C苹果62个餐桌投影map误差中位.24847m；依据C031已核实的Fortress world里程计和本图恒定绑定，事后扣同期实测map/odom变换后剩.01652m（max.01951），证据apple_localization_contribution。只用于评估，未把world/真值坐标送回感知。6970随后仅在实际停稳时调用官方AMCL无运动激光更新5次，服务均返回，但完整苹果计2/3失败，已确认两点定位.080/.033m；没有证明刷新解决问题，**不接默认**。须保留定位与识别两类失败，不把位置通过说成数量通过。

**当前候选/语义：** 默认n640/v6/service_surfaces_v2、auxNone、guidanceFalse不改；显式S1280/native1280×960、高1/pitch.25、19通用词冻结37KB NPZ（SHA c198c497e1d0a351bbcf832b74d54860534fe9cbf7c0cb27a051f6ee7f0e67e0）只补书/球，IoU≥.5 primary优先、score.35/2hits/.20位置/≤.4s源龄/2Hz保留。球心拟合仅实际深度、无资产半径。权重/recipe/锁校验，600MB编码器仅离线、临时源码已清；120秒235样本检测年龄p95 .266s，非整任务避障结论。UI语义/运行/房间关系三视图、分类颜色/标签避让/状态/档案联动，Firefox桌面/390px通过；ConceptGraphs/Canopy只作设计参考，真实Spark-DSG B20/C26记录独立重载与API坐标/状态/任务/证据/revision一致。跨任务仅空间ID，非移动物理身份；semantic_update_audit保留书旧位置复核、旧球待核验等实际变化。新排序精确关联历史观测ID，仅重排find可选点，必巡/回退和count完整现场数量不变。旧椅A/B85.62→93.38秒无收益；新gym首对101.88→30.05秒、14.19→6.86m，但引导位置.22543>.20失败，第二对停测，两次回充/odom质量通过，不能称提效验收。

**此前局部诊断运行（最新状态见上方点云修复）：** 本轮三个局部诊断根ff52f98b、1fc673f7、3590cd42均正常shutdown、无所属残留，所有探针结束；未重跑整房。此前38b6aae9的8007/11156=71.77%、15/25条/Twirling未证实收益，原YAML与critic断言已恢复；本轮再次按dcbccdec冻结件核对nav2_depth字节一致。当前工程394通过/29条件跳过，两包构建1.18秒；默认仍n640/v6/service_surfaces_v2、auxNone、guidanceFalse、三类准入与附加1格。Git737aadb，原有大量脏改动保留，无提交/推送。

用户最新追问器械后/周围漏扫及安全间距。已完成最新最终任务的事后空间审计：FitnessEquipment_01_001周边第21/22/23条有原规划但无实际清扫尝试，第24条仅两段；图示靠墙背面ROI可扫243格=.6075m²、实扫0，其中177格=.4425m²无原条带刷盘覆盖，66格=.165m²规划可刷但未扫；另76格=.19m²自由地面被当前安全模型排除，不能把整片空白都称不可达。Nav2机器人半径.25m，但RoomSweep.CENTER_CLEARANCE_M=.32，再加半格.025与跟踪膨胀1格.05，沿轴规划净空约.395m，确实偏保守；附加1格把该ROI可规划中心47压到25，潜在刷盘243→160格，路布置/执行也有独立缺口。原参数未全局放宽，未缩机器人半径/覆盖分母。证据gym_equipment_audit.json/png、equipment_margin_audit.json；精选docs/evidence/gym_equipment_clearance_20261122.png。物体网格只用于任务结束后的图示定位，不进入感知/搜索。

**用户确认后的局部子阶段：** 已实现房间级`cleaning_tracking_margin_cells`整数0/1，默认1；显式v11_margin0只在v10的gym加0，保留基础.32m、Nav2半径.25m、原eligible11156/刷宽/80%及逐格实时检查。新增6项检查通过（含0格不误用SciPy侵蚀到空、原分母/基本中心不变、动态禁行仍拒绝）；报告写实际采用值。冻结图选出器械背面.5m段，候选可规划/原余量拒绝，159格仅预测而非实扫。新增`validation/cleaning_clearance_probe.py`复用原生动作/限速.12、共用停车与回充，独立线程监视扫描/障碍点云和机身接触，外部UI任务抢占时取消。Fortress接触仅有事件、无心跳，已查原生实现/端点，不能将静止零消息当无碰撞通过。

实跑3次接近动作均因.4秒数据新鲜度中止并确认停车，最大实测里程仅.00209m，未驶出充电处；高分辨率点云12秒采样最大间隔1.399秒，轻量GUI原周期最大.738秒。另15秒`.1`周期读回采样中原云6次间隔>.4、最大.883秒，输出最大1.027秒；该采样多订阅原云会增负载，不能当隔离频率收益对照。无GUI同导航复测与随后仅准备诊断均未发目标；最后一份确认地图/动作服务/停车/接触发布/速度限制订阅均已就绪，但连续2秒新鲜窗口最长1.128秒（46次重置）。2秒为新增局部诊断准备条件，不改默认任务标准。早期工具在收到停止后未等待恢复参数回执，保留原false标记；随后实查周期.25。现已修清理阶段在确认停车后有界等待恢复、准确记状态，最后两份均确认周期.25和解除临时限速。

**修复前局部结论/当时下一步（已由上方接续）：** 附加余量候选已实现，实际窄区通行/无接触及覆盖收益均未验收，默认不切0格。证据统一[局部审计](../../results/development/clearance_probe_20261122/audit.json)并接回既有阶段收据，5份原探针和3根shutdown保留。下一小步只对现有独立桥接/传感链路做有界连续新鲜度定位，数据准备通过后再回到这.5m通行段；不盲跑整房、不降低.4门槛、不全局缩轮廓。随后仍交替推进类别0/1/2/3/5布局与5重复、语义查找/移动更新及4项避障和真人联调。

**文件轨迹：** 本局部阶段修改cleaning.py、run_cleaning报告、tests/test_cleaning_reference.py，新v11_margin0/validation/cleaning_clearance_probe.py与集中证据；INTERFACES/RUNNING/SOURCES/DEVELOPMENT_VALIDATION及本摘要增量同步。此前关键新修复scripts/run_cleaning.py、tests/test_cleaning_remaining.py；新validation/dwb_scores.py、localization_refresh_trial.py仅诊断，及此前target_stability/memory_guidance_trials；v10 rooms/v3_C layout独立保存。其他C041 cleaning/navigation_client/connector、memory_guidance/semantic_memory/search_node、ball_geometry/detection_fusion/detector/depth、Runtime/Console/UI、prepare_runtime和提示资源的原件/失败在before、before_aux、before_prompt与各会话冻结源。地图/原世界/权重基线保留。现有长期文档与三份既有收据增量同步，详细路径见stage_summary，勿另立计划/交接。

**C040最新收尾（2026-11-22）：** 用户要求均匀路线/提速与床头柜复测，本轮已完成一次整房实跑及床头柜子项验收，仍有清扫欠账。当前默认已切到rooms_aws_house_v6.json + layout_service_surfaces_v2.json，厨房两区不变、卧室书桌/床头柜必巡；默认开发nav2_depth线速度.35m/s，原nav2.yaml/nav2_safety.yaml及旧v5/布局保留。冷启动会话20261122T090623_391875Z_a6a541fe、域67、http://127.0.0.1:8767，ready/不忙碌，Gazebo/RViz相机显示运行，留给用户真人麦克风联调；先查API再操作，不假设该状态永久有效。原试验7d7419c5已正常关闭、shutdown无所属残留。Git仍737aadb，未提交/推送。

**C040清扫事实：** 原同底图/7975分母、.50扫幅、720秒和停车/轮廓门槛不变；采用相邻.35m条带，实际规划20条（含分段），未启用隔条。原5997/7975=75.20%、core661.08秒；本轮6390/7975=80.13%、core635.48秒/console636.67秒、重复面积7.2325→6.8175m²，整任务面积效率1.3607→1.5083m²/分钟约+10.85%。一次配置对照、初始实时掩码/前序观察不同，不当作隔离速度因果或重复稳定性。实际Follow阶段1862样本横向误差中位.0211m/p95 .05675m，沿线跟踪更具体地可核对；两次确认安全停稳后续原队列，未插入全局补扫。回充.09058m/.09586rad/.46秒通过。原partial/budget_exhausted保留，西侧诊断带仅239/908=26.32%，最左两条仍未完整扫完，85%与左侧完整覆盖仍未验收。40动作中failed5/timed_out1；lane_start累计326.345秒、follow_path229.797秒，端部等待/换道仍是下一步重点，不盲目加速或连续重跑整房。

**C040提速/床头柜：** 控制器与平滑器实查.35上限，转速/加速度不改；短程运动取消停车两次检查，补测peak .34751m/s、取消2秒后新鲜odom停稳、回充通过并增量保存原始采样。床头柜修复仅对杯/瓶掩膜内深度做NumPy IQR异常值过滤，原尺寸先验/2hits/.20m定位标准未变，椅等大物体估计不变；10张旧图回放保留书桌/厨房杯瓶，历史垃圾桶误识仍拒绝。新冷会话实际卧室计数2/预期2，XY误差.13242/.04297m、书桌/床头柜必巡6/6、6份RGB-D/TF完整，床头柜32帧投影0尺寸拒绝，总168.75秒，回充.08543m/.09541rad/.46秒通过。当前namespace共8物品，新增床头柜杯独立记录；SQLite重开与API一致、真实Spark-DSG14节点13边重载一致。只属新范围单次功能子项，不是16类/变化布局正式重复或记忆收益/物理身份验收。

**C040证据与限制：** results/development/cleaning_efficiency_20261122/stage_summary.json集中源码/配置/结果与下一步，clean_audit.json和cleaning_comparison.png区分蓝色计划/绿色实际覆盖，stop_recheck保留原始odom，memory_audit和depth_regression可复查。外部汇总器在最终收尾意外退出143、原因未知；控制台清扫本体正常partial并回充，原结果/轨迹/掩码完整、组件仍健康。保留report_interrupted.json后从final_trial_state/会话原产物恢复汇总；全程接触采样/末尾原始motion文件未落盘，不宣称整房无碰撞采样通过；随后短程重测停车/回充保存原始数据，不重复整房。工程368通过/29条件跳过、两包构建1.13秒；默认选择改后33项针对性检查通过，12份原地图与C035指纹一致。清扫/物品/记忆既有收据增量记录C040。下一步先有界复现条带端部等待和最左残余，保持已有验收门槛；用户可继续真人麦克风四功能联调，16类/85%不阻塞首次联调。

**此前C039收尾（由C040接续）：** 用户指出卧室候选轨迹不均匀，隔条遍历候选不接受、不升级默认。825cedf9与独立床头柜复测309f603b均已正常关闭，shutdown无所属残留，当前没有本轮运行任务/采集器。Git仍737aadb，未提交/推送。Runtime默认保持v5/厨房两区布局，床头柜v6/新布局尚未升级。证据统一results/development/bedroom_nightstand_20261122/stage_summary.json，以及清扫/物品既有收据新增C039字段。

**C039清扫结论：** 原用户任务5997/7975=75.20%、西侧x<-8.2的908格0覆盖；末3条原计划未执行，初/末掩码西侧规划中心连通，系预算尾部遗漏。隔条候选实际5954/7975=74.66%、西侧675/908=74.34%，重复面积7.655m²较原7.2325m²增大，回充.11479m/.09625rad/.46秒通过；两次均partial。隔条首遍中心间距.70m而刷宽.50m，填间隔前预算耗尽；另两次条带末端失败后插入全局横向补扫，再回到原下一条，相关4动作132.398秒。v6已撤下coarse_then_infill，恢复adjacent；实验函数/冻结失败会话保留。run_cleaning现仅在settled+stop_confirmed且实际位置通过静态/实时安全检查、还有原条带队列时继续原队列，残余补扫后置；原失败回执不改，不安全或未停稳仍走恢复。工程最终367通过/29条件跳过，两包构建1.15秒；实际失败掩码离线回放下一原条带连接约.96/.72m，不改覆盖。修复尚无整房实跑收益，左侧尾部遗漏与均匀性仍未验收。详见clean_audit/audit.json、uniformity_audit.json及uniformity_diagnosis.png，不把132秒当作实测节时。

**C039床头柜结论：** NightStand_01_001书桌侧台面约.68691m。新v6卧室书桌/床头柜必巡，总6姿态/5位置、单点最多2朝向，静态连通且间距至少.47m。service_surfaces_v1新增杯被原相框遮挡，完整6点只计书桌杯1/预期2，失败保留。独立v2只移新增杯到空角落(-7.48,2.72)，原相框/其余目标/数量2/.20m标准不变：真实6/6观察/数据、6份实际RGB-D/TF完整，图中杯可见且YOLO检出；仍计1/2、失败。床头柜32帧投影中31帧被原尺寸先验拒绝，仅1次可用不足2hits，离线同帧几何extent(.10106,.24834,.09122)、水平对角约.268m超原.25m；未放宽阈值，不简单归为YOLO漏检或仍遮挡。总180.13秒，回充.08331m/.08894rad/.46秒通过。SQLite/真实Spark保存本次1条，无新增独立重载收益结论。首被动采集器域错误空记录保留，改域67后完整采6点；沙盒构建缓存写入失败后经宿主正常构建通过，原失败均保留。

**C039当时下一步（已由C040实跑接续）：** 对相邻条带失败续接做有界实跑，核对实际连接耗时、均匀性、覆盖与回充；不继续叠加控制参数或恢复隔条默认。利用已采RGB-D核对床头柜前景深度/尺寸混入，不放宽先验掩盖误投影，修复前不升级新范围；之后继续用户真人麦克风四功能联调，16类/85%仍不阻塞首次联调。

**C038点位效率复核（用户建议分散点位、每点少量方向）：** 当前厨房实际为11个不同XY位置、18个观察姿态，同一(6.6,-.4)占8个方向。历史椅子任务末尾7个原地朝向从到达到最后停留约68.75仿真秒，均无有效椅子投影；不是只有一个观察点。用原始投影按原LandmarkMap/.30m/2hits离线重放，完整重放精确复现4把；选保留必巡餐桌/操作台的6个互补位置[0,1,2,3,5,7]也保留4个确认实例。建议少量互补空间点、每点先1个必要朝向，确有盲区才补第2个，并优化顺路次序；这是当前布局的离线候选，尚无实跑节时/新转场/其他布局证明。证据results/development/microphone_intent_20261122/route_efficiency_replay.json。本轮未改默认路线或导航参数，未移动机器人；后续实跑应同时核对数量、位置、两区巡视、回充和耗时，不能因旧帧重放就宣称新的完整盘点通过。

**C038真人联调进行中（优先于下方静态ready状态）：** 用户实际说“去厨房找椅子。”，首转写“去厨房找意识。”、第二次为正确的“去厨房找椅子。”；请求531884b9-8416-4181-8fc2-5a9f14696c59/任务a7250ff1-2867-4f41-b29c-52a153247f67按find1完成并回充，用户期望厨房全部椅子，因此本次用户验收是意图约定不符，不能称整机真人验收通过。保留原completed/found1及用户反馈；事后最近ChairA_01_002模型原点XY偏差.08303m，不把该点当作实际统计全部的证据。用户随后询问可用指令，尚未要求全局把裸“找”改成count；当前以“统计/清点”全量，未指定数量的find保持原行为，UI/运行指南补充说明。

公开API补做human_all_kitchen_chairs_01（count kitchen chair）已完成：18/18观察/数据完整、4把椅子，事后匹配4个场景椅位置XY误差.104/.138/.071/.041m（原.30m标准内），回充.08929m/.09705rad/.46秒通过。这是用户澄清后的API全量补测，不是新增真人“统计”语音验收；当前已空闲供用户继续测试。原受管RViz已正常关闭returncode0；RGB配置原为关闭，已开启/Reliable并重开辅助RViz，窗口已移到屏幕右下且置前，真实RGB画面已核对。辅助窗口携带本栈SEMANTIC_RUNTIME_OWNER及role=rviz_camera_reopen，整机清理可识别；Console组件行仍记录原RViz退出，不等于当前窗口未打开。证据results/development/microphone_intent_20261122/（state_before、summary、rviz_camera.png）；旧配置/网页文案均有备份。

**2026-11-22最新用户决定：先完成再完善，降低当前阶段验收标准，整体链路预检后由用户进行真人麦克风全功能验收。** 本阶段使用已准入杯/瓶/椅；清扫不以85%作为联调门槛，但真实覆盖/partial和剩余原因保留，须能执行、保存并回充；语义地图先保证写入/查询/重载。16类、3布局/5重复、85%、记忆收益和完整视图列入后续完善，均不再阻塞首次真人联调。数量正确、停车、避障保护、公共回充与无控制冲突仍需满足；未指定新比例，运行目标/分母/停靠容差不擅改。覆盖此前“高指标完成后才真人联调”的顺序，唯一总计划已同步。

**同轮新增要求：厨房餐桌和L形灶台拐角操作台均作为物品摆放/巡视区域。** 现有category_views以餐桌及原地环视为主，不能据旧找杯/计数记录宣称已覆盖操作台。正在核对两侧观察点与独立摆放案例；现运行C036仍为冻结的旧布局/路线，后续须单独记录厨房新增范围的验证，再交给用户麦克风联调。

**当前C037厨房两区巡视已完成子项验证，控制台保持运行供用户真人麦克风联调。** 活动会话`20261122T072416_913300Z_5804f937`，域67，网页http://127.0.0.1:8767，ready且不忙碌。当前默认已选rooms_aws_house_v5.json + layout_kitchen_two_surfaces_v1.json（仍杯/瓶/椅三类）。餐桌与操作台两区实拍、find必巡3点及回充通过；独立冷计数2、位置误差.13173/.03949m和回充.07580m/.09569rad/.46秒通过。工程359项通过/29条件跳过，两包构建；旧v4/原布局/12份地图保留。首次计数时整机退出来源未知，原失败保留，不能称连续稳定性已验收。语音资源就绪，真人输入、操作台瓶子完整计数等仍未测。新厨房几何使用独立namespace，旧22条记忆不变，新namespace两条杯记录及Spark-DSG8节点/7边重载一致。证据`results/development/kitchen_two_surfaces_20261122/stage_summary.json`；查看本节C037细节。

**C036功能阶段预检已通过：** 会话`20261122T065856_764386Z_264ead9d`使用原v4/yellow冻结配置，建图运动/停止/保存恢复、厨房杯find1/count1及各自回充通过；清扫636.99秒，原任务partial、7854/11156=70.40%，回充.10413m/.09443rad/.46秒。34份HTTP产物字节匹配；SQLite22条、真实Spark-DSG28节点/27边、revision88核对通过。此为用户降低门槛后的功能预检，原85%未通过状态保留，不代表新厨房操作台已验证。正常shutdown无所属残留，已切换至C037新会话`20261122T071811_302236Z_4c732f89`验证中，暂未交出真人联调。证据`results/development/integration_handoff_20261122/stage_summary.json`及原P4/G0收据新增字段。

**此前C035收尾（已由C036/C037接续）：共用文件底图入口与新版本保存已完成子项验证，两个C035会话均已关闭、无所属残留。** 冷启动完成建图另存/恢复原图、厨房找杯及自动回充，SQLite与Spark-DSG独立重载一致。工程352项通过/29条件跳过、两包构建。首次集成返航响应超时的失败保留；新增2秒发现预备窗口后单次冷复测通过，尚不证明所有通信超时已解决。原12份PGM/YAML、导航参数、接受门槛及既有工作区改动保留；Git仍737aadb，未提交/推送。C034覆盖61.35%/85%和原连接完整朝向限制不变，其后执行顺序已由上方11月22日用户决定更新。

**三项修整的真实结果：** C031固定充电处/出生(-1.8,-4)与各正常任务公共回充已实现；深度积压修复在同重载短程单次对照中有收益，.26m/s上限不变。历史最高C032为8122/11156=72.80%且回充通过，属于旧配置；C033收益候选70.32%且回充失败，默认关闭。C034同区域短程已录到支架底板—原场景哑铃实体接触，修正代价层/实体外接圆并复用普通转向适配，整房6844/11156=61.35%、回充.08062m/.09648rad/.46通过，无机身接触记录，85%仍失败。原连接专项实测位置误差.10440m，但朝向未完成、40秒超时，不算完整通过；四邻预算在该点不可达而用欧氏后备，实际延长收益未证实。已停止叠加导航参数，接续厨房杯子现场找到1个及自动回充，SQLite独立重开和Spark-DSG28节点/27边/22历史记录核对通过；没有新增类别或记忆引导收益结论。当前主要未决仍是覆盖收益、原连接完整朝向/预算后备、最终4项日常避障、16类稳定准入与语义现场核验收益；真人麦克风最后联调。

**此前开发收尾（C026–C029）：** 已连续推进C026–C029，全部测试实例已关闭，Git基线仍`737aadb`，未提交/推送。 工程270项通过/17条件跳过，Spark-DSG独立3项已有通过；C028额外28项配置测试通过。清扫近程恢复和局部静态层试验未解决卡点，前者默认关闭、后者恢复上一候选；新增实测锚点校验已触发拒绝。语义记忆空盘点修复已现场验证，手机跨卧室/客厅更新与冷重载通过子检查；但客厅计数2/预期1，已定位原AWS平板误识，不新增类别准入。冷会话异常退出143后已按身份外部清理，原因仍待跟踪。下一步继续清扫末端/TF与受阻根因，交替打磨类别负例和语义核验；全部门槛沿用唯一总计划。详见C029–C025及现有收据。

**上轮暂停记录（由本轮恢复指令接续）：** 最近子任务为桌面线索补充观察接入、手机寻找/完整计数及早期取消保存修复。会话 `20261121T040718_113508Z_1de0819e` 已正常关闭，shutdown无所属残留，被动观测器与临时浏览器已退出。手机找到1个/47.31秒、完整计数1个/271.12秒，16/16到点审计通过；不代表新增类别正式准入。证据集中在 [物品收据](../evidence/target_expansion_20261121.json) 的support_surface_probe。当时没有运行中的批次；随后仅按用户要求更新验收范围、地图方案并核对长期文档，暂停至本轮恢复。 Git基线仍为`737aadb`，本轮修改保留在工作区，尚未提交或推送。

### 可视化显式演示（2026-11-21）

- 用户要求直接看效果；打开统一UI、Gazebo和RViz，使用C029手机移位布局、原rooms_objects_v1、s/1280 GPU、1280×960/1.4rad、1.2m/.15rad及原`.30m`安全候选，显式开启cell phone。两项清扫实验关闭，未改运行源码、地图、模型阈值或类别准入。
- 会话`20261121T091504_795614Z_d88cce53`，请求`visible_phone_find_20261121_01`，任务`c406a69c-750e-4718-90a6-aaefb3a1bbc1`，以统一文字入口提交“去客厅找手机”。真实found 1，10.89墙钟秒（控制台13.87秒），首点2帧有效投影，TF/深度失败0，结果/观测/SVG保存。寻找提前返回，原观察计划未完整执行，不作为全房盘点或平板误识已解决。
- 结果在`results/development/visible_phone_demo/report.json`及对应会话，窗口布局调整为网页左侧、Gazebo右上、RViz右下。演示后曾保持运行供用户查看；随后用户提交卧室清扫并在C030后要求停止，现已正常shutdown。继承C029开发限制，Git仍未提交/推送。

### 阶段复盘（2026-11-22）

- 本轮按用户要求只做复盘，核对Git、源码指纹及C031–C035原证据，未启动任务、未改运行源码/控制参数/验收标准。C035的16项源码指纹仍一致，宿主无项目控制台、8767释放；Git仍737aadb，121项状态条目含大量既有改动，未提交/推送。
- 已有成果：固定充电/出生与公共回充；深度积压在一次同重载短程对照中明显缓解卡顿；地图统一载入/独立保存；感知记忆及SQLite/Spark-DSG重载。流畅性对照并非同路线完整任务，尚不能推为整任务稳定提速。
- 核心欠账：当前C034清扫61.35%/85%，历史C032最高72.80%属于旧配置；四项日常避障、至少16类变化布局及正式重复未完成。原冻结杯/瓶/椅基线通过，扩展类别仍候选。语义地图已能存取/更新，但记忆引导收益、物理身份和主动补点识别增益未证实。
- 故障分开归因：C033实测进入被当前掩码排除的99格；C034同区域录到实体接触，修整后专项无机身接触记录但完整朝向仍差约1.74rad、40秒超时；其预算因掩码不可达退回欧氏40秒，实际延长收益未证实。C035另有返航响应发送超时，2秒预备窗口后仅一次冷复测通过。上述证据尚不足以归为一个规划/执行单因。
- 开发方式需修正：C034同时改变障碍层、轮廓和普通转向，覆盖比历史最好低约11.5个百分点，缺少逐项因果对照；不能凭这两次结果断言某参数导致下降，也不能将新配置评价为整体优化成功。工程352项通过、产物一致性和反复找杯回归各有价值，业务验收仍以覆盖/回充/避障和类别正确率为准。后续固定配置、先补证据、每次单项改动，未证实收益的候选保留原失败，不自动提升验收状态。
- 下一步沿唯一总计划：先按C034有界核对原连接的实际NavFn路径/目标可达性、odom/TF与终点朝向，再选择单项修复；穿插P6现场核验/更新和清单约定布局，保持已有3布局/5重复、4项日常避障与真人麦克风最后的安排。避免长期停留在同一连接调参或仅重复找杯。总计划顺序1已修正滞留的C032“当前默认”表述，明确当前导航候选与历史最高成绩，不新增平行计划。
- 证据沿用[清扫收据](../evidence/cleaning_coverage_20261121.json)、[记忆收据](../evidence/semantic_memory_20261121.json)、[类别收据](../evidence/target_expansion_20261121.json)和各C031–C035原路径；本轮不产生新的运行验收成绩。

### C038：真人意图澄清、RViz恢复与原地反复调整诊断（2026-11-22）

- 用户说“去厨房找椅子”，转写最终正确，系统执行find1/返回；用户期望找齐全部，记录为意图约定不符，原completed/found1不改写。用户随后询问可用指令，尚未要求改裸“找”的全局默认；运行指南和网页提示明确“找”单个、“统计/清点”完成计划巡视并报告数量。原语音两次文本、任务/证据与用户失败反馈保留。
- 同一会话5804f937通过公开API补做厨房chair count，18/18完整观察确认4把、位置核对与回充通过。机器人来回调整的明确流程原因：同一(6.6,-.4)有8个不同方向，全部逐次发NavigateToPose；最后7次arrival从sim1688.012到1752.760秒，另含此前必巡餐桌。该8点本次有效椅子投影均0，不能据单次结果推断它们对所有布局均无用。没有摆动当时连续cmd_vel/odom，尚未量化控制振荡或归因所有抖动。未改导航参数或到达容差；后续优先核对/合并同地点的转向采样，保留两区必巡及数量正确。
- 原受管RViz已退出且RGB显示关闭；已备份rviz配置、开启RGB/Reliable，移除旧隐藏窗口布局，重开窗口置前并核对实时画面。辅助RViz持有当前栈所有权标记/rviz_camera_reopen角色，整机关闭可清理，Console旧rviz组件行仍显示旧实例退出；后续停止需同时留意辅助窗口，勿启动重复RViz。原栅格、感知结果和导航配置不改。
- 证据results/development/microphone_intent_20261122/summary.json、state_before/all_chairs_state/oscillation_state、rviz_camera.png、command_checks.json；本轮仅验证指令例子/显示配置/HTML模式和实跑产物，工程359/29为C037版本历史记录、未重复全套。当前控制台与RViz留给用户继续真人验收；动作/数量/部分转写通过不代表所有真人功能和连续稳定性通过。

### C037：厨房餐桌与L形操作台巡视（2026-11-22，子项通过、真人待验）

- 依用户图片补充两处摆放/巡视范围。旧v4厨房多边形排除了操作台，两处新增目标原先room_at=None；v5纳入完整厨房语义范围，旧v4/布局保留。原栅格不改、健身区分母11156不改；实际/map+新房间几何生成新namespace，旧22条记录逐字段保留，不混入新任务数量。
- 新布局在餐桌杯瓶外各加操作台杯/瓶，仍三类准入；场景设计/评估用几何不进入搜索。通用inspection_views将餐桌及操作台两方向置于计划前部、去重；只有实际到达/完整停留/有效同步帧才完成分区巡视，find确认后也先完成必巡区域。未完成一侧保留partial，UI显示区域及已巡视/未完成。
- 首冷会话4c732f89找杯147.76秒、必巡3点、回充.04663m/.09548rad/.46通过。独立被动采集3份RGB-D/TF，实拍已核对餐桌、炉灶侧及水槽侧；寻找提前返回不表示全房全目标检查。开始计数约10秒时控制台关闭，HTTP ConnectionReset，原report保持failed，shutdown无所属残留；仅凭清理时RCLError不能归为节点先崩溃，退出来源未明。
- 同配置独立进程组冷补计数会话5804f937通过：count2/251.43秒，两个感知位置分别匹配餐桌与操作台目标，XY误差.13173/.03949m，原.20m门槛不改；回充.07580m/.09569rad/.46通过。新scope旧find记录冷重载后更新，SQLite2条与真实Spark-DSG8节点/7边的位置/证据一致，旧scope22条不变。strace信号跟踪受宿主ptrace权限限制未能附加，未改系统设置；独立进程组重启不能宣称已消除首次退出原因。
- 359项工程通过/29条件跳过，两包构建；源码轨迹在sources_before/after.json。实测通过后只将Runtime默认选择及相关测试预期改为已测v5/新布局，活动会话此前已显式选用完全相同的一对配置；该选择调整未改导航/动作客户端，未重复整套实跑。原v4/yellow可用原有--rooms-file/--layout-file回归。
- 精选[物品收据](../evidence/target_expansion_20261121.json)的kitchen_two_surfaces，含原失败、冷补测、静态检查/实际采集、产物/SQLite/图重载审计和原件散列。C036与首C037已正常关闭，当前5804f937刻意保持运行供用户测试，观察器/验证器已退出。未验收真人麦克风、操作台瓶子完整计数、连续稳定性、16类/85%和最终4项避障；下一步用户按RUNNING逐项录音联调，修阻断问题，再完善指标。

### C035：共用底图载入与新版本保存（2026-11-22，子项验证通过）

- 按唯一总计划“共用底图与统一视图”子项推进，避免继续反复调导航参数。新增map_resources.json两组资源及map_resources.py公共选择/校验入口；AWS同版三份YAML/PGM实测一致，baseline单独保留。注册路径指向同一主图，现存兼容副本几何或图像不同即拒绝混用，不覆盖/删除原件；显式未注册新版本不按像素相同自动合并。
- 场景选择、两种导航脚本、Runtime配置/快照、充电绑定及三种离线地图读取工具使用公共入口；保留Humble所需ASCII工作区别名。充电双SHA继续校验请求原文件，并核对实际选用地图一致。保存默认写独立results/maps版本，显式前缀也拒绝注册图或已保存输出；控制台原会话map_output仍按原流程保存，不自动替换现行底图。新底图仍须重新核对房间/观察点和充电标定。
- 首冷会话`20261122T025030_136345Z_1bfab54b`完成实际MapServer路径、建图另存/恢复及找杯/记忆写入，但找杯后的返航目标响应发送超时，客户端未获接受回执，正确触发停机保护；`report.json`保持failed。日志只证实响应超时，发现匹配竞态为待验证解释。`run_return.py`增加至少2秒消息处理与发现等待，仍需新鲜位姿/停稳/服务就绪；原25秒启动、8秒目标接受、终态/停车屏障与任务截止不变，不放宽停靠。
- 独立冷复测`20261122T030047_676399Z_d83639ed`通过：实际MapServer前后均为ASCII路径的主图，短程静止建图另存到会话新版本，恢复后实际/map和记忆namespace/revision不变；厨房杯现场found1，任务含回充107.05秒，回充.10311m/.09629rad/.46秒通过。记忆revision85→86、22条历史记录独立SQLite重开逐字段一致；真实Spark-DSG重载28节点/27边，位置、证据、任务ID和未核验物理身份标志一致。find提前确认不是完整盘点或记忆引导收益验收。
- 工程352项通过/29条件跳过，两包构建；另实跑旧PNG工具，主图/兼容入口与修改前逐像素一致；空间检查前后报告一致、8项通过，但原.22m静态检查不代表当前.25m导航验收。原12份地图散列不变，Nav2参数/原布局/共用动作客户端与C034快照相同。独立审计最初误读query返回封装、残留检查最初匹配自身shell，均修正记录，不是产品故障。
- 证据集中`results/development/map_loading_20261122/`，摘要`stage_summary.json`、失败`report.json`、复测`retry/report.json`、`semantic_audit.json`、`offline_tools_audit.json`、`cleanup.json`；精选入口为[记忆收据](../evidence/semantic_memory_20261121.json)的map_loading。两个shutdown均stopped，宿主复核无所属进程且8767释放。总计划开头滞留的“尚无公共回充”已按C031实测修正；只完成资源载入子项，六类视图/统一导出、85%、4项日常避障、16类稳定准入和真人麦克风仍待完成。下一步保持C034有界连接回归及原总计划顺序，不继续叠加控制参数。

### C034：连接实体接触与转向/预算修整（2026-11-22，阶段收尾；部分验收未通过）

- 依用户要求限定连接排查，再继续唯一总计划。首短程从固定充电处实际导航至原连接起点请求，再去(2.865,2.595)，旧混合层/.22配置40秒超时。在停稳位置补录支架mount_plate与Dumbbell_01_001实体接触69份；仅证明该复现区域实际接触，不倒推C033首次碰撞时刻或唯一成因。首次诊断topic误放sensor而非Fortress读取的contact子项，无消息不能判无碰撞；发现实际话题后补录并修正，原件保留。
- 默认开发候选复用已有独立激光ObstacleLayer/深度VoxelLayer最大融合，.22→.25m包住实体后角约.237m；普通FollowPath外复用原生RotationShim/.6rad/s，底层DWB全部critics和general完整朝向门槛保留。原.30m安全候选、.26m/s和物品/地图不变。分层、加普通转向的两次短程均因40秒上限结束，后者推进至绕行另一侧，不能记到达通过。
- 清扫lane_start新增当前全局二值掩码四邻距离的40–180秒估计，受原720秒及回充预留限制，写入connector_budget；不可达用原欧氏后备，不等于加权NavFn实际路径长度。最终全跑14份预算均40秒，冻结掩码逐份重算一致，仅组件用例证明长绕行会延长。后续原连接专项距离为空、后备40秒，实际位置误差.10440m、无机身接触，但完整朝向未完成，原动作超时保留，实际延长收益尚未证实。
- 最终冷会话`20261121T173842_396879Z_54246dea`/`connector_gym_full_01`：638.49秒，6844/11156=61.35%，预算截止，回充.08062m/.09648rad/.46秒通过。接触系统/共享桥已用独立夹具校准，夹具移除，全程无机身/支架接触记录；不覆盖轮子/脚轮，也不把通道校准当完整避障通过。源/原栅格/轨迹/odom/SVG/参考/动作停车及14份预算审计均通过，85%仍失败。相机/布局/推理默认n/640不变，配置耦合且实测起步有误差，不作单因素速度收益结论。
- 随后统一UI厨房找杯`connector_memory_cup_01`：现场found1/全任务101.67秒，自动回充.07385m/.09459rad/.46通过。记忆revision83→84，独立进程重开SQLite的22条记录逐字段与UI一致，导航变更前后地图namespace相同；真实Spark-DSG重载28节点/27边/22历史物品记录，位置、任务ID、证据和未验证物理身份标志一致。本次现场确认只有1个，不把历史记录补成当前数量；不证明记忆引导收益或新增类别准入。
- 最终取消清扫后45份独立新鲜odom跨.88秒停稳、无自动回充，六项HTTP产物字节一致，取消覆盖/轨迹/停车审计通过。组合观察器在后续手动回充阶段出现rclpy上下文失效，来源未定位，原failed报告及被工具取消的回充保持。确认取消停稳后仅补手动回充，.08823m/.09549rad/.46通过；不把初始组合观察器改记通过。
- 工程335项通过/29条件跳过，两包构建；独立Spark-DSG3项通过，共用动作客户端字节未改，18项隔离协议历史证据保留、未重复。初期诊断配置与两项测试工具错误原输出保留。文件为run_cleaning.py、cleaning.py的预算；development.py/launch的低流量机身接触；nav2_depth.yaml分层/.25/普通转向及三组相关测试。原碰撞几何、nav2.yaml、全部地图、spatial_v4和真值不改。
- 集中证据`results/development/connector_contact_20261122/`；精选[清扫收据](../evidence/cleaning_coverage_20261121.json)的connector_contact、[记忆收据](../evidence/semantic_memory_20261121.json)的connector_regression和[两次失败连接图](../evidence/cleaning_connector_contact_20261122.png)。a8dd8076、974cd059、79e56a85、54246dea四会话正常shutdown，无所属残留；宿主复核无本轮观察器/控制台、8767释放，校准模型移除。
- 下一步沿原计划推进覆盖与语义地图，保留原连接完整朝向/预算后备为有界回归项；再改控制器前先补实际NavFn路径长度与目标可达性证据。当前默认开发配置与.30安全候选都尚欠最终4项日常避障，不扩大矩阵；16类、记忆收益和真人麦克风门槛不变。观察器上下文异常继续留证待查，保存本摘要不是宿主原生上下文压缩。

### C033：清扫预算与提前补扫（2026-11-22，收尾；候选不采用为默认）

- 沿用既定下一步，默认n/640、原yellow/v4、nav2_depth/.22m及C032一格静态余量/恢复/停车约束不改。试验联合评估主条带和未扫条带，预计单位时间新扫面积高25%才提前选择，保留未选工作，估计不适合剩余窗口的段不选。工程初328项通过/29跳过、两包构建通过，冻结旧掩码探针只作为组件结果。
- 统一UI全预算实跑`20261121T165308_993555Z_e6b3c717`/`budget_gym_full_01`：490.52秒，7845/11156=70.32%，回充失败7.65444m/.30302rad，停车.46秒确认；85%与回充均失败。10次条带尝试中2次保持顺序、8次主路线重排，没有执行到remaining_floor。选路、原栅格/轨迹/SVG/odom/动作停车审计均一致，不能把审计通过当任务通过。
- 最后一段估计11.53秒，实际连接29.80秒失败；实测map位姿(2.32960,2.44409)未通过可通行检查，连接开始前对应全局格已99，失败快照全局/局部均99、419候选被BaseObstacle拒绝；旧锚点恢复、出房及回充均失败。转返航时清扫窗口还剩117.57秒，主要阻碍是连接执行/控制安全性，非总预算耗尽。原结果、源码和失败不改。
- 已将候选改为`--cleaning-budget-selection`显式启动（客户端`--budget-selection`），默认关闭并恢复原主路线顺序和原补扫评分；会话与报告记录开关，候选产物仍可下载。增加默认隔离、开关传递/保存回归，最终333项通过/29条件跳过、两包构建通过。初次无路径pytest误收集历史备份而报ImportMismatch，保留工具输出；限定项目tests后通过，不是机器人失败。
- 54组真实冻结状态（主队列/补扫）默认选择与剩余队列和C032一致，运动/恢复辅助函数未改；组件重放不计新实扫。最终冷会话`20261121T170511_563869Z_d7ab8726`默认关闭实验且源码快照匹配；取消后42份独立新鲜odom跨.82秒全部停稳，无自动回充；六项HTTP产物字节一致，取消覆盖/栅格/轨迹/SVG/里程/停车独立审计通过。手动回充.10632m/.09685rad/.46秒通过，不追认为整房85%通过。
- 证据统一`results/development/cleaning_budget_20261122/`，精选入口沿用[清扫收据](../evidence/cleaning_coverage_20261121.json)的`budget_selection`及[连接图](../evidence/cleaning_connector_failure_20261122.png)。两会话shutdown stopped/无所属残留，宿主复核无本轮观察器/控制台、8767释放；原源码、C032失败、地图和真值保留。文件含清扫调度/候选估计、console/runtime开关及3组相关工程测试，导航配置与共用动作客户端未改。
- 用户询问可否人工预排路线：当前本就先排25条带，入房/连接/回充NavFn实时更新、条带FollowPath并检查实时掩码。固定安全连接路线适合作对照，仍需定位、实时避障及失败反馈，不能据预排路线认定故障消失。下一步先对照该连接的规划、实际odom/TF和恢复阶段，定位进入已知99格的环节，再改覆盖预算；原85%/.15m/.15rad及类别/最终.30m候选状态不变。快照按到达采样，不证明物理接触或具体传感器层。

- 追加离线归因：在sim424.06–430.144秒，map前向净位移约.0064m、侧向-.1527m；连续odom前向约.0125m、侧向-.2232m，期间/cmd_vel多次请求约.25–.26m/s。双图99出现比该连接首次spin恢复早约2.19秒，因此现有证据偏向运动执行/跟踪异常，不能仅以map定位显示跳变或后续恢复解释；完整连接全局Path未保存，仍不能排除规划贴障/安全余量、碰撞几何或执行动力学问题。数据按到达采样，非同步控制内部证明；详见connector_failure.json的attribution。未启动新仿真、未改源码或验收结论。

### C032：实时掩码、条带与恢复修整（2026-11-21，收尾；覆盖未通过）

- 沿用唯一总计划和现有摘要，无新平行计划。最终实现先保持原往复式主路线、按当前连通掩码切段，主遍历后重生成实际未扫条带；SciPy四邻Dijkstra仅估计补扫连接距离，实际NavFn/同一Nav2控制器不替换。连接和重排起点使用普通Nav2完整恢复/朝向，条带仍直接FollowPath/RotationShim+DWB/.12m Position checker。实际直达参考安全时优先使用；斜线穿邻障时，经≤.18m安全接入原条带。到起点后重新切段，发送的是新段实际终点，原段存`nominal_lane`。路径/预测不增加实扫。
- 静态规划中心增加一格四邻跟踪余量（格长约.05m），原eligible=11156、.50m刷宽、.35m候选间距、.26m/s和720秒不变；不对动态障碍整体侵蚀来改口径。默认两轮冻结掩码的几何潜力93.8%–94.3%，仅是规划核算；最终主条带假定刷盘85.46%也不是实扫。
- 每次选点/参考验证保存原始全局代价图、实际覆盖、时间、连通潜力和原条带受阻编号，合为`clean_plan.json`与去重`clean_navigation.npz`（最多256事件）。新增规划中心数组及`tracking_margin_cells`、`remaining_lane_attempts`；网页可下载。恢复原动作成功但连续odom平移<.20m记`no_measured_progress`，原action_status保留。此前默认试跑35次原地恢复成功共耗19.654秒，旧结果未改；新版本一次真实恢复实走.545m。标准Nav2恢复树仍可调用其原有清图/旋转/等待/后退，不停用传感器或修改障碍阈值。

| 冷会话 / 配置阶段 | 核心耗时 / 覆盖 | 固定回充与处理 |
|---|---|---|
| f1440a98，s/1280/.30m，逐段重选 | 475.44s / 48.91% | 回充通过；3份参考被安全检查拒绝，旧锚点实测不安全后停止 |
| 4625dbb0，同重载，保留条带/重新切段 | 266.62s / 31.15% | 中段侧偏约.034m进入99格，恢复/回充失败 |
| 01ff9e66，默认n/640/.22m，逐段重选 | 600.10s / 66.57% | 回充通过；后段35次零位移恢复循环，原失败保留 |
| c9fb4fda，默认，主路线/普通连接恢复 | 297.98s / 31.14% | 贴障起点再次锁死，回充失败 |
| **e8e7fcea，默认，再加静态一格余量** | **606.71s / 72.80%（8122格）** | **回充.12043m/.09489rad/.46秒通过；选用此运动实现** |
| d84e25cb，默认，普通DWB/Position连接候选 | 511.75s / 47.18% | 回充失败，不采用；已恢复上一行对应实现 |

- 6轮均未通过85%，各轮覆盖/原分母/里程/SVG/接受动作停车/冻结源码，以及选点和执行参考的实时掩码审计一致。前两轮与默认布局/相机/半径不同，不能据百分比作单因素性能结论。第5轮处理17/25个seeded条带，未到remaining_floor或10点补扫；入房42.34秒、连接213.80秒、条带244.31秒，550.328秒开始返航，距清扫截止仍13.752秒，因剩余时段不足以再恢复，不是已扫完。旧报告`navigation_recovery_failed`原样保留；最终仅报告补丁新增`recovery_budget_insufficient`和`cleaning_time_remaining_seconds`。
- 最终冷会话`20261121T152957_627641Z_7def673d`：统一UI取消清扫后43份独立新鲜odom跨.84秒全部停稳，不自动回充；手动回充.09822m/.09708rad/.46通过。6项HTTP产物逐字节与本地一致，取消轨迹/栅格/SVG/动作停车独立重放通过，冷快照与最终源一致。运动辅助函数、cleaning.py、BT和共用客户端与第5轮完全匹配，差异仅终止原因/剩余时段记录，见`final_source_comparison.json`与`final_reporting.patch`；不把冷取消追认为全预算85%通过。
- 工程325项通过/29条件跳过，18项隔离ROS两动作停车协议已有通过（共用客户端字节未变），两包构建通过。新增`tests/test_cleaning_remaining.py`13项，更新恢复/配置夹具。初版选路审计读错潜力字段，原工具保留并修正；组件探针房间外坐标返回空集，已用真实入口重算。机器人原结果、真值和失败未改。示意图仅是冻结掩码重放：[参考修复图](../evidence/cleaning_reference_masks_20261121.png)。
- 文件：`scripts/run_cleaning.py`、`src/semantic_search/semantic_search/cleaning.py`、控制台产物下载、`scripts/validation/motion_profile.py`只读采样与相关测试；`nav2.yaml`、导航半径/速度参数、地图和物品真值本轮不改。所有资料集中`results/development/cleaning_remaining_20261121/`，唯一精选入口为[清扫收据](../evidence/cleaning_coverage_20261121.json)的`remaining_coverage`。7会话shutdown stopped/无所属残留，宿主复核无本轮观察器或控制台、8767释放。
- 下一步：按现有计划提高预算内主遍历/补扫收益，利用本轮原始掩码和实走时长，避免预算全耗在低收益碎片及连接；继续原85%验收与固定回充。最终.30m安全候选4项日常避障、语义地图收益/16类稳定准入和真人麦克风仍未完成；导航算法比较继续暂缓。保存本摘要不等于宿主原生上下文压缩。

### C031：充电、流畅性与终止修整（2026-11-21，阶段收尾、覆盖未通过）

- 用户已授权优先修整这三项，沿用唯一总计划。`skills/context-compression`维护同一摘要；按grilling要求由只读代理核对Nav2 1.1.20和桥0.244.26，未重复询问既定决策。Git仍737aadb，所有改动未提交/推送，既有脏文件、地图和失败保留。
- **流畅性单次对照：** 同GUI、s/1280 GPU、1280×960/8Hz和旧出生(0,0)，桥大数据publisher及adapter/detector/guard队列改KEEP_LAST(1)，可靠性不变，旧帧在处理前丢弃且不重盖stamp，.4秒停车门槛不变。112秒采样中，过滤后非零而末端零速20.738→.302秒（29.71%→.364%），过期原因相关15.792→0秒，采样零速转换42→3，请求期间odom线速中位.0292→.2463m/s。基线79.45秒提前结束、复测91.44秒由UI取消，不能当同路线完成时间或稳定8倍收益。桥实际GetParameters已证实depth=1；RMW depth=0标未知。
- **固定充电：** `config/charging_station.json`绑定地图YAML/PGM双SHA，客厅西侧map/world出生(-1.8,-4,0)，内置充电几何；当前/odom来自Fortress世界位姿，初始化AMCL按固定SE2作用于最新odom，不重复平移、不在模式恢复时重置回出生点。清扫actual start与dock target分开；搜索/盘点先完整保存原结果/观测/SVG及记忆，再串行公共回充并保持忙碌；取消优先停车且不自动回充，支持独立回充按钮/文字。建图结束切回导航后共用回充。
- **控制与路径：** local滚动图/behavior改map并加载局部StaticLayer，普通目标保持原DWB、.12m/.1rad；清扫专用`CleaningPath`使用原生RotationShim包装DWB（入口.4/退出.1rad，采样.15m、.6rad/s、closed_loop），去清扫RotateToGoal，原生Position .12/stateful:false。本机短路径采样不足会回落DWB，不能保证每次都先纯转向。PoseProgressChecker .20m/.50rad/10秒，单目标/总截止继续生效。NavFn Dijkstra仍用于入房、连接和回充；核验的清扫条带以半格加密map Path直接交同一Nav2 FollowPath，含静态/实时/斜角格检查，不按计划线涂覆盖。
- **恢复与停车：** `navigation_client.py`共用两类动作的迟到接受、取消、终态及重置后新鲜≥.45秒停车屏障；已在真实.12m内且fresh parked的条带目标记already_reached，无action_status，不冒充Nav2成功。优先安全连通条带重排再回旧锚点：每轮最多2起点、全局最多4轮，原失败条带最多尾部重试一次；成功到端点、实测安全且连续odom≥.20m才恢复。保留原失败、.18m既有部分续作和固定分母，未直接发布恢复速度或启用实验逃脱。

| 实跑阶段 | 结果与限制 |
|---|---|
| 新BT首次冷启动`97a9c23d` | 中文路径经Humble YAML被转义，导航未激活、未跑任务；改用既有ASCII别名，补路径回归，旧失败/正常shutdown保留 |
| 固定充电首集成`65a5e6d5` | 四房寻物/盘点公共回充、2取消/手动回充通过；完整gym20.34%/回充失败5.819m。global当前/邻格99、local81–85，后续规划被围；失败保留 |
| map/static+.05候选`90bfec9a` | 仍在换道弧线中进入global/local99，.05还增加末端迟滞；主动UI取消并保存，审计通过不等于覆盖通过，正常关闭 |
| 原生转向衔接`dbc6333f` | 631.99秒、47.88%，回充.12031m/.08501rad/.46通过；3次客户端限时取消、一次旧锚点折返实际6.839m未完成后重排恢复，85%失败 |
| 直接参考条带`4757d1c6` | 613.73秒、66.31%（7398/11156），清扫预算截止，回充.07109m/.11752rad/.46通过；无旧锚点折返，安全重排实走3.145m恢复。五区回充、取消/手动、建图保存→恢复导航→回充全部通过，整房覆盖仍失败 |
| 最终发送前补丁`60b3ddbf` | 默认n/640盘椅4、16/16点、最大XY.1361m/回充通过；90秒清扫取消独立odom24样本/.46秒停稳、手动回充通过。仅补发送前复查/原因字段，全跑旧快照与最终版分开留证 |

- **真实剩余阻碍：** 第四候选有6条带被实时可通行掩码跳过，18份参考路径的刷盘并集仅7251/11156（65.00%）；其中197格未被实扫，实际连接轨迹另覆盖344格，不能用假定路径补齐66.31%的实测。当时逐条完整live mask未保存，尚不能区分真实障碍、残留深度标记和路线偏移需求。另5个FollowPath末端进展失败，4个距目标.122–.136m，1个.235m；末10秒请求线速常为0、guard ready无过期门控，支持控制器末端停滞，不足以归因某critic。仅移除GoalAlign/PathAlign的候选完成源码审查、未启用；不继续盲调容差代替补扫。
- **关键回归/证据边界：** 历史卡点目标(-2.085,1.995)在第四候选实际成功到达且锚点安全，来路/初始姿态不同，不是同轨迹A/B。审计覆盖/里程/原分母/SVG/动作停车/冻结源码全部通过。五区回充只证明停靠生命周期；厨房椅子实际返回5、事后场景评估4（16/16点，导航失败0），两条记录XY相距.207m、3D相距.361m，疑似可见表面变化导致重复，物理身份未确认，原5条结果/记忆未改，不视为规模5或数量通过。
- **建图切换：** 独立新鲜odom实测移动.349m，另存YAML/PGM、原底图双SHA不变；恢复导航后从移动后的实际位置自动回充，误差.08964m/.09480rad/.46通过，未把初始化伪装成回到家。
- **最终检查与源码归属：** 312工程通过/29条件跳过，Navigate/Follow两动作共18项隔离ROS成功/失败/超时×延迟停车/持续移动/过期里程计通过，两包构建通过。纯夹具修补前3项失败、修补后通过：路径准备跨截止、收到停止、定位失效时均不得发送。全跑源与最终补丁差异见`final_checks/final_fix.json/.patch`；默认冷回归单独保存；初版验证工具误读字段层级，原报告保留，正确coverage字段离线审计通过且最终源快照全部匹配。原生动作收到结果后仍要新鲜停车，不放松85%、.50m刷宽、.35m间距、.30m候选安全半径、.26m/s或.15m/.15rad停靠。
- **文件轨迹：** sensor_qos/cloud_adapter/detector/velocity_guard、development与navigation launch、nav2_depth/safety和三份BT；charging_station/docking、development设施/出生、initialize_sim_amcl、robot_runtime/robot_console、navigation_client/run_return/run_cleaning、cleaning.py、UI及相关测试。旧nav2.yaml/地图/物品真值不改。源码原件与实跑均集中`results/development/service_motion_20261121/`；唯一精选收据仍为[cleaning_coverage_20261121.json](../evidence/cleaning_coverage_20261121.json)，固定设施网页图见[截图](../evidence/charging_station_ui_20261121.png)。
- **下一步沿总计划：** C031已正常收尾；C032已采集实时掩码并继续验证未扫连通区域与可达补扫段，在原分母/720秒预算下复验85%与固定回充；穿插家具多视角几何关联反例。4项日常避障仍按每项一次实跑，最终配置未验收；真人麦克风最后。

### C030增量：跨房预算修复实测通过，完整覆盖未通过；用户要求停止并排查（2026-11-21）

- 用户截图对应同一可视化会话请求`e3d58ab2-1660-4a02-b0ba-385ff7342e8d`。起点厨房(8.80787,2.11985)，卧室入口(-2.9,-.5)；正常移动9.53146m后，第40秒被清扫客户端固定时限取消，尚距入口3.32264m，故覆盖0/7975、尚未生成清扫目标。不是历史清扫末端卡点的同一失败。返航Nav2成功但实际位置误差.160574m略超.15m，原判定停靠失败正确；缺口在于成功回执跳过了实测超差校正。
- `cleaning.py`按实际距离提供40–180秒有界入房/跨房预算，仍受任务总截止和Nav2进展检查约束；按房间可达中心范围至本次起点的距离预留返航时间。`run_cleaning.py`记录请求/有效时限与返航预留，Nav2回执成功后仍核验实际XY/朝向，近起点超差走原approach/alignment校正。短程预算边界、720秒产品总预算、.50m扫幅、85%和.15m/.15rad/.45秒停靠不变；清扫两项实验仍关闭。
- 修改前2项停靠回归失败，修复后清扫35项、工程274项通过/17条件跳过，两包构建通过。旧失败产物原样保留，报告/轨迹/SVG逐格重放、7975原分母和动作停车顺序审计一致。
- 现场复测`clean_bedroom_transit_fix_01`从实际返航后的厨房(8.65054,2.15194)出发，入房动作预算131.10秒、实际62.14秒成功；返回厨房动作预算144.24秒、实际58.69秒成功。总411.44秒（控制台412.54秒），覆盖32.71%（2609/7975）、停靠.064782m/.094835rad、停稳.46秒，结果partial且产物saved。17个目标停稳顺序、原分母、覆盖/里程/SVG逐格重放和源码散列一致。停靠首目标已达标，没有触发新增近起点校正分支，该分支本轮仅有回归测试。
- 为保留用户窗口，复测未重启Console/Gazebo/Nav2；新清扫子进程加载修复文件，启动时快照仍是旧版本，另存请求`validation_sources.json`及修复源码散列，不能把旧启动指纹当作本次清扫源码。监视脚本exec报告143、发送者未知；独立API确认机器人任务继续运行并完成，后续人工读取最终结果，不将监视脚本退出误写为机器人任务被取消。
- 离线诊断对齐17个Nav2开始日志与目标记录，时差漂移<.063秒。本轮9个异常目标累计192.774秒、9次Failed to make progress；最后条带终点尚差.28043m，回退3.033m旧锚点实际移动3.00771m/31.46秒后超时，终点仍差.21436m/2.86353rad。`lane_navigation_ready=false`使余下条带和补扫跳过，338.676秒开始返航；清扫截止510秒、总预算720秒均未耗尽。不是“已扫完”或此次整房预算太短。
- 进展配置.5m/10秒只算XY，和.35m换道及末端转向存在不匹配：索引3（第4个导航目标）附近轨迹约11.01仿真秒，平移最大.36571m，原Nav2失败时XY差.09835m但朝向仍差.14875rad。短移动/转向会被进展检查判失败；RotateToGoal状态保持和定位/障碍输入的因果仍需同步控制链采样。未改导航参数或重开已失败的位置端点实验。
- 卡顿证据：本轮78条深度来源时间差警告（阈值.4秒），安全门控遇过期会输出0；没有同步cmd_vel/guard状态序列，不能量化实际停车次数或认定GPU是根因。本轮没有20Hz控制丢周期警告；全任务仿真时钟/墙钟估计.975，仅排除持续大幅低速仿真的解释，不能排除短卡顿。可视化实例使用手机候选s/1280和1280×960/8Hz，线速上限.26m/s；重复失败与多段对齐是已确认的耗时来源。
- 固定充电点现状：`spatial_v4.json`明确home(0,0,0)不是充电处；仅清扫回任务起点，搜索/计数无公共返航。用户新要求已记入总计划，尚未实现。建议客厅西侧下半段靠杂物间隔墙(-1.8,-4.0)，静态中心间距.65m、1.2m前方接近区域最小间距.55m且与原起点连通；[位置图](../evidence/charging_location_candidate_20261121.png)。仅静态设计候选，仍需模型/出生点/地图位姿一致性与五区实跑，不作为已验收充电处。
- 用户要求先停止后，已核实控制台身份并SIGINT正常关闭，shutdown无所属残留，另做宿主PID/start_ticks、域67及端口复核。文件：两处清扫实现与测试、只读审计/诊断工具；证据集中`results/development/cleaning_transit_budget/`，沿用[清扫收据](../evidence/cleaning_coverage_20261121.json)。Git仍737aadb、未提交/推送。恢复后先处理深度数据积压、短目标/转向进展与有界恢复重排，再接入固定充电位姿及公共返航；85%、扫幅、原分母与停车门槛不变。

### C029增量：手机移位记忆更新通过子检查，完整计数失败（2026-11-21）

- 按总计划交替推进语义地图。已有历史手机空间记录`b9281253cdfd4d60a7280a17f53f0d45`：卧室，2次任务观测。C026已修复完整空盘点的not_found状态，当前用现场任务验证旧位置待核验、新位置由感知新增空间记录。
- 独立评估布局`results/development/semantic_phone_move/layout_moved.json`沿用v3资产，将唯一手机从卧室书桌移至客厅茶几；苹果移回餐区符合新常用区域安排，其余不变。布局真值仅供场景生成/事后评估，搜索继续既有rooms_objects_v1视点，不读布局答案。
- 两会话沿用1280×960/1.4rad、1.2m/.15rad、s/1280 GPU，仅显式开启cell phone，既有rooms_objects_v1视点不变，主动补点关闭。首会话`20261121T072140_528724Z_015bb299`恢复原命名空间与旧ID，卧室盘点10/10点、观测完整，0/not_found、142.50墙钟秒；旧ID变needs_verification，last_seen/位置/证据及原2次观测保留。随后客厅实际找到1个，115.83墙钟秒，位置(1.09264,-1.66006,.35730)，事后XY偏差.112m；新增空间ID`3a7b17ccca5f465f985f8dd6aa306ddc`，Spark-DSG19节点/18边可读。find提前确认后原观察计划未完成，不当作完整盘点。
- 冷启动会话`20261121T072829_353834Z_2f494a41`逐字段恢复旧待核验/新观测记录及命名空间。客厅完整计数121.76墙钟秒，实际完成10点但计2/预期1，数量验收失败；两簇各64次命中。真实手机更新同一客厅空间ID到2次观测，旧卧室记录保持不变；错误的额外手机记录`09285aabaab74a5794e35dd6b2486bec`由实际误识产生，原记录保留，未用真值回写生产数据库。
- 诊断：任务结束且UI空闲后，经既有Nav2工具回到索引5（第6个视点，0,0,-.7854），重采RGB-D/TF。同一s/1280/.35/.30/FP32重现两个独立手机框；一处是新增手机，另一处为AWS原有`Tablet_01_001`（原世界位姿约1.573,-1.776,.402）的平板误识，深度投影与第二簇吻合。不是同一手机的重复空间记录，不能扩大关联半径合成1个；没有移除平板、改标签、改真值或修改失败结果。实测可见尺寸与框/位置保存供后续通用方法验证，新类别仍不准入。
- 证据：集中`results/development/semantic_phone_move/`；现有[多类收据](../evidence/target_expansion_20261121.json)的`memory_phone_move`和[记忆收据](../evidence/semantic_memory_20261121.json)的`phone_move_live_recheck`，精选[同视点平板误识图](../evidence/phone_tablet_confusion_20261121.png)。原帧为任务后重采，并非原任务RGB；原任务逐帧观测保存。首次离线探针因沙箱不可见CUDA失败，宿主GPU重试通过，非在线检测器失败。
- 收尾：首会话shutdown无所属残留；冷会话在请求SIGINT后终端退出143，缺少正常shutdown收据，信号发送者未跟踪。另按UID+会话token+start_ticks核验并用pidfd清理29个所属残留，外部收据`cold_external_cleanup.json`显示0剩余；不称正常退出通过。数据库只读quick_check=ok，宿主复核无机器人进程、8767释放。
- 当前限制/下一步：物品记忆的旧位置待核验、新位置更新及冷重载已有真实子用例，完整手机计数、物理身份、记忆引导效率和至少16类正式验收仍待完成。接续先诊断清扫转向末端/TF及受阻起点；穿插手机/平板等负例与外观关联方法，保留全部失败，真人麦克风仍最后。

### C028增量：局部静态层候选未通过，恢复上一配置（2026-11-21）

- 继续原计划排查全局/局部差异，查到`.30m`导航候选`nav2_safety.yaml`局部代价图定义了`static_layer`，但plugins列表未加载；全局已加载。复用官方Humble StaticLayer的滚动窗口/TF适配实现，仅补局部插件列表这一项。旧候选原件保存于`results/development/local_static_layer/nav2_safety_before.yaml`，历史会话快照保留；原nav2_depth默认配置不变。
- 独立冷启动会话`20261121T071346_472492Z_ec915a13`的GetParameters与日志均证实已加载静态层（半径仍.30、odom）；本机无parameter_client Python封装，检查改用真实GetParameters服务。28项配置/Runtime测试通过。240秒测试预算实跑`clean_local_static_01`在171.45秒结束：19.31%（2154/11156）、返航失败2.82994m/.62230rad；.28556m旧锚点恢复仅产生.00421m连续TF采样位移后超时。实测没有解决卡点，按原件逐字节恢复上一候选配置，失败与候选原件/会话快照保留。原Nav2默认配置不变。报告/轨迹/SVG及停车顺序审计通过，shutdown无所属残留。

### C027增量：恢复锚点实测校验与受阻起点诊断（2026-11-21）

- 用户要求持续按总计划开发。C026已收尾并关闭全部实例，本阶段完成诊断与一次修复实跑；当前所属实例均已关闭。近程恢复和位置端点实验关闭，沿用`.30m`安全候选及C025停车屏障，不改导航算法或验收门槛。
- 独立只读采集工具`results/development/cleaning_stall_diagnosis/capture.py`订阅实际`/map`、全局/局部代价图和TF；通过统一UI执行清扫，失败时保存压缩栅格、机器人坐标/格值、时间新鲜度和日志摘录。连续3个失败目标位置不变或240秒诊断预算后经UI取消，不发布速度或读取场景真值。
- 初轮诊断会话`20261121T065838_216995Z_65a380b9`达到240秒采集预算后经UI取消，产物保存且shutdown无所属残留。3个失败起点全局代价54/61/46、静态障碍距离.50/.522/.55m，未复现历史卡死。历史C026复测位姿静态间距仅.25m，对应上个原Nav2成功回执的实测位置距目标.257m；不能据当前诊断认定所有失败都由起点碰撞引起，真实漂移原因仍待查。
- 已修复任务层缺口：`CleaningRun.remember_safe_arrival`只接纳新鲜、在静态中心与实时可通行掩码内的实测锚点，否则保留旧锚点；恢复动作成功后同样再核验，不合格记`unsafe_arrival`并停止清扫。原Nav2状态保留，不降低门槛。历史真实位姿/静态图隔离重放已验证不再把该.25m位置当作安全锚点；实时掩码在重放中明确采用全true作静态拒绝对照，不冒充历史实况。
- 5种锚点输入及不合格恢复回归通过，工程270项通过/17条件跳过。独立冷启动会话`20261121T070354_588365Z_5024b9c0`使用测试进程240秒预算实跑`clean_anchor_recheck_01`（产品仍720秒，近程与位置端点实验关闭），171.18秒结束，覆盖20.32%（2267/11156），返航失败（2.84027m/2.31595rad，停稳.46秒）。6次锚点校验中实际拒绝1个不合格位置，原Nav2成功状态保留；清扫截止尚余不足20秒，所以未执行条带恢复，不能声称实际脱困已验证。11个目标停稳、报告/轨迹/SVG重放通过，全部产物保存，shutdown无所属残留，8767释放。证据集中于`results/development/cleaning_stall_diagnosis/`，仍沿用既有清扫收据，不提升完整覆盖或日常避障状态。
- 失败后在停稳位置采到实况：全局代价99（既有可通行掩码排除）、局部89、静态障碍间距约.20m，位姿约(-2.225,1.770,2.321)。证据`stuck_after_recheck.json/.npz`；先前历史位置.25m间距与新实况相互支持，但全局/局部来源、坐标校正与末端转向漂移的因果仍待验证。已查Humble官方SimpleGoalChecker及RotateToGoal源码，stateful行为作为后续诊断线索，未改候选控制器参数。
- 本阶段限制与下一步：锚点记账缺口已修复并触发真实拒绝；导航脱困、覆盖和本次返航未通过。下一小任务应冻结受阻前后的map→odom、odom→base与全局/局部障碍输入，核对末端转向的实测漂移及目标检查器行为，再选择修复；沿用总计划继续语义地图现场核验与4项日常避障。用户授权持续开发有效，无关键待确认取舍。


### C026增量：近程恢复试验与空盘点记忆修复（2026-11-21）

- 清扫实现：`cleaning.py`新增`RoomSweep.recovery_anchor`，`run_cleaning.py`仅在显式实验开启且旧端点>1m时，优先选最近30秒连续实测轨迹中距当前.4–.85m、累计回溯≤1.5m、当前静态与实时栅格可通行的位置；不跨采样断点，保留样本朝向，仍由普通Nav2执行一次有界恢复。新增原端点/选点来源、距离、耗时与连续TF采样里程，新版带轨迹起止索引供重放；覆盖统计不改。
- 离线诊断：精确复现历史7655/11156，轨迹与SVG绿色格逐格一致。首个3.79m恢复25.16秒、随后重新前进24.30秒；遗漏3501格中2606在y≥3m。静态理想条带90.99%只是预测。ROS地图分辨率是float32的`0.05000000074505806`，重放必须沿用，不能用Python字面.05改变刷盘边界/分母。
- 首次720秒预算会话`20261121T064200_484229Z_8c80378a`/`clean_local_recovery_full_01`提前在183.09秒结束：25.98%（2898/11156）、返航.10097m/.09361rad/停稳.46秒通过。近程选点.42189m代替旧端点3.65731m，但按短距离算的14.6368秒预算使恢复超时，连续TF采样累计.92554m；12个已接受目标均停稳确认。原失败保留，不按选点距离变短认定收益。
- 复测：保留原长回退时间预算，新增选点异常终态记录及轨迹索引。720秒预算会话`20261121T064725_541761Z_c25bbabc`/`clean_local_recovery_full_02`在150.28秒提前结束：10.45%（1166/11156）、返航.07153m/.10381rad/停稳.46秒通过，63个已接受目标停稳顺序通过。未触发近程选点；28次旧端点近零位移恢复立即成功，而后续规划继续失败，未验证修正预算的近程实际效果。两轮报告/轨迹/SVG逐格重放、动作顺序与冻结源码散列审计一致，shutdown均无所属残留。
- 最终决定：没有覆盖收益证据，近程恢复仅保留为`--cleaning-local-recovery`显式实验，默认关闭，传至客户端`--local-recovery`并记入会话与报告。试验时尚未加入开关、自动启用的源码由会话快照保留。日常继续原端点恢复+C025停车屏障；位置端点实验也关闭，不更改85%、刷宽、分母或停靠容差。最终短程回归会话`20261121T065250_198002Z_4c32a942`使用测试进程135秒预算（产品仍720秒），耗时101.32秒，覆盖12.94%正确partial，返航.09832m/.09665rad/停稳.46秒通过，7个目标停稳审计通过，实验开关false且全部产物保存；shutdown无所属残留。
- 语义记忆修复：`semantic_memory.py`此前仅将`completed`盘点未见旧记录置待核验，遗漏了真实完整空盘点的`not_found`。现两种终态均需观测计划/数据完整才更新状态；保留历史坐标、last_seen、证据，不删记录，不用记忆补本次0计数。`tests/test_semantic_memory.py`覆盖真实状态、缺口、部分/寻找、重载和幂等。使用两份未改写历史真实结果在临时SQLite按模拟顺序重放，复现旧问题并验证修复；Spark-DSG真实导出/重载保留待核验状态及历史证据，未修改生产数据库。这是协议重放，不是新增现场移除/移动验收。
- 验证与文件：完整工程264项通过/17条件跳过，Spark-DSG独立3项通过，两个包构建通过；C025独立ROS协议未重复。首次构建被专用缓存的沙箱写权限阻断后按原路径重试通过；重放工具相对导入及mappingproxy序列化问题已修复，不属于机器人运行失败。新增`tests/test_cleaning_recovery.py`13项及清扫/控制台/Runtime显式开关测试。证据集中于`results/development/cleaning_local_recovery/`，沿用[清扫收据](../evidence/cleaning_coverage_20261121.json)的`local_recovery`与[记忆收据](../evidence/semantic_memory_20261121.json)的`complete_empty_count_fix`，未另立计划。
- 下一步：优先诊断零位移恢复成功但后续持续规划失败，捕获失败起点与实时全局/局部代价图，核对机器人所在栅格及可通行连通性，再处理上半区遗漏/补扫；继续语义记忆现场核验。完整覆盖最佳仍68.62%，最终.30m配置4项日常避障、16类稳定准入和真人麦克风均未提升验收状态。

### C025增量：清扫恢复前停车确认（2026-11-21）

- 根因：`CleaningRun.go`超时取消后仅凭动作终态置`settled=true`；位置端点取消的停车等待超时也被同一异常分支吞掉。真实历史报告另确认恢复目标曾距当前位置约3.8m；停车屏障属于先行修复，尚未优化恢复选点。
- 修改：`scripts/run_cleaning.py`对所有已接受目标，在终态后重新累计0.45秒停稳，最新里程计不超过0.40秒，等待上限2秒墙钟。未确认则保留`navigation_settled=false`并拒发下一目标；`scripts/robot_console.py`沿用现有关闭本次运行/禁用提交机制，更正反馈为“终态或停稳未确认”。原动作状态保留，轨迹目标新增终态/停稳时间、确认结果与错误。
- 验证：`tests/test_cleaning.py`增加超时、失败、位置端点、迟到接受、用户取消和过期里程计回归；修改前6项失败记录保留。新增`tests/test_cleaning_stop_ros.py`在域69以真实动作与里程计消息检查6项，明确是协议夹具。首轮夹具错误使用未初始化的默认executor，改为显式独立context后通过，失败日志保留。
- 实跑：会话`20261121T051144_350014Z_5f8e8cbc`通过UI取消清扫，12/12个已接受目标停稳确认，包含2次abort和最终cancel，JSON/轨迹/SVG保存；shutdown无所属残留。首次误将`--task-timeout 135`当作清扫预算，核对源码确认它仅控制搜索、清扫仍720秒；本次按取消验证记录，不作为短预算或覆盖验收。随后采用历史短程验证方法，仅在测试控制台进程覆盖`CLEAN_TIMEOUT_SECONDS=135`，冷启动会话`20261121T051608_569189Z_3e0a7225`在102.83秒后返回本次起点，位置.10321m/朝向.10265rad/停稳.46秒；覆盖13.22%（1475/11156），正确partial并保存全部产物。7/7个目标停稳确认，含预算截止取消；与首轮合计19/19，逐目标时间审计未发现停车确认前发送下一目标。两会话shutdown均无所属残留，宿主进程复核为空、8767端口已释放。
- 文件与证据：本轮详细证据集中在`results/development/cleaning_stop_barrier/`，沿用[清扫收据](../evidence/cleaning_coverage_20261121.json)的`stop_barrier`增量，包含旧源码、失败、测试、会话/配置与新源码散列；同步现有接口、运行说明、总计划进度、验证概览和本摘要。未改导航配置、扫幅、分母、85%或停靠标准，位置端点实验仍默认关闭；不提升里程碑状态。
- 限制与下一步：本轮小任务完成，无关键待确认取舍。停车确认不证明恢复路径或覆盖已经改善；仍须沿用总计划排查杂物间受阻和清扫长距离恢复/补扫，同步推进语义记忆现场核验。完整预算覆盖及最终配置4项日常避障仍待完成，真人麦克风最后联调。

### 最新决策：验收范围与优先级收敛（2026-11-21）

- 已确定：至少16类稳定识别与计数目标保留，按常用区域验收。碗/水果仅餐区，手机/书在卧室与客厅，球在健身区与杂物间；其余逐项见TARGET_CATALOG.md的T01–T16。同一常用区域内保留至少3份独立变化布局、选定正式物品案例5次重复和冷启动；数量用例在该类布局集合中覆盖，检查合并到同一案例。
- 已确定：避障正式检查为家具/箱子绕行、移动物体让行、正常门口通行、持续堵路停车反馈4项，每项一次完整实跑，失败修复后复测相关项并做关键路线回归。取消、请求幂等和数据过期停车沿用已有基础检查，既有专项证据和失败保留。原10类×多姿态×5次的避障要求由此替换；物品正式案例的5次要求不变。
- 已确定：清扫85%覆盖与安全通行、语义地图质量为重点；语义记忆引导现场查找、移动/增减更新、冲突/不确定性和主动观察收益需实测。导航算法比较暂缓，待当前版本完全做好后再评估，不占本轮工时；真人麦克风仍最后联调。
- 估计：常用区域物品验收18–30小时、4项日常避障3–6小时；首轮开发/文本验收/报告合计44–76小时，包含语义地图重点8–14小时。仅为重新粗估，需按实际失败率校准，不能据此认定问题已解决。
- 文件与证据：更新既有DEPLOYMENT_PLAN.md、TARGET_CATALOG.md、REQUIREMENTS_STATUS.md、DEVELOPMENT_VALIDATION.md和本摘要；未修改运行代码、场景或历史验收结果，未启动新批次。新范围尚未完成验收，无关键待确认问题。
- 下次接续：先排查房间间受阻和清扫长距离回退，按4项日常情况验证；交替打磨语义记忆更新、现场核验与实际补拍收益，穿插约定区域的16类验收。已知冰箱漏检、水果混淆、照片误识和家具定位偏差仍须解决。

### 最新文档核对与地图约定（2026-11-21）

- 已确定：每个场景/地图版本共用占据栅格底图，通过图层形成6类空间视图，另附语义关系图；变化对比为语义图层模式，代价图与规划路径为调试显示。唯一清单维护在[总计划地图方案](DEPLOYMENT_PLAN.md#地图数据与输出视图)，不独立维护多份展示底图。
- 已核查文件：当前默认载入`scenes/aws_house/r0_v1/maps/house.yaml`，与`scenes/aws_house/maps/house.*`、`maps/aws_house/house.*`的同版YAML/PGM分别逐字节一致（SHA-256前缀0dac305d71af、fd3b7f0c4924）。兼容副本及历史版本保留，代码统一载入入口仍待完成。现有清扫SVG合并轨迹/覆盖，独立图层切换、统一导出和关系图可视化仍待开发。
- 已修正文档：核对`docs/maintained/`全部11份及7个入口页。总计划/要求对照/清单统一验收与优先级；接口更正已有进度、持久数据库及两种ID；运行/资源/部署/来源更正GPU、候选模型、资产与部署版本；验证/本摘要区分历史和当前。另更新`README.md`、`docs/README.md`、`scripts/README.md`、`scenes/aws_house/README.md`；根HANDOFF/SOURCES和baseline说明核对后沿用。无新增文档。
- 静态核验：184个本地链接（含19个标题锚点）均有效；脚本索引43个文件均存在；6类空间视图、4项日常避障、T01–T16和44–76小时预算逐项一致。此次仅核对文档与已有文件，未重跑机器人或修改运行代码，不新增实验通过结论。
- 未决与下一步：无需要用户新判断的关键取舍。本节文档核对结束时机器人开发保持暂停；本轮已恢复，沿用下方次序，新增实现仍需完成最终配置与干净副本回归。保存本摘要不等于执行宿主原生上下文压缩。

### 最近开发收尾：桌面观察与结果保存

- 手机完整计数执行10个原视点、2个桌面线索视点、4个几何补点；16/16到点符合既有.20m/.15rad审计标准，最大.1146m/.1014rad。最终计数1，XY偏差.124m；新增类别定位标准及跨布局重复仍待正式校准验收。
- 实测可见采样698/1012→872/1012（68.97%→86.17%，新增174）。全部44帧有效手机投影仍来自原视点，两个桌面近景视点为0；不能宣称该策略提高手机识别或计数。需检查遮挡/朝向，不能只增加视点或换大模型。
- 寻找和计数汇入同一持久记录b9281253cdfd4d60a7280a17f53f0d45，2个任务、1条手机记录，Spark-DSG图可读；类别仍为验证中。
- 修复首次观察前取消时误要求coverage_samples.json的保存误报。真实早期取消已完整保存JSON/SVG/观测记录；已创建采样网格而文件缺失时仍报告partial，3项回归覆盖两种情况。
- 本轮完整231项通过/11条件跳过，随后显式记录搜索门槛的Runtime检查20项通过，两个包构建通过；实际Firefox158宽1440/500px、桌面提示及记忆定位通过。搜索默认2次确认/.30m关联/.35置信度，今后显式记录并传入；被动筛查独立使用3次确认。
- 早期无桌面线索版本手机未找到（几何采样86.56%），跨区前往杂物间连续无进展，408秒后由验证器取消，0个有效观察。原结果标partial保存实为采样文件期望错误；原失败不改写，修复通过由新会话另证。详见active_target_recheck/及support_inspection/。

### 最新增量：C024 原生宽视场筛查与清扫复测

- 清扫后两次分别49.21%（5490/11156格，350.35秒）和68.62%（7655/11156格，668.43秒）；后者处理全部46个计划端点，6次恢复成功，返航位置误差.14983m/朝向.00263rad、停稳.46秒。这是单次临界通过停靠，不能宣称稳定裕量。`results/development/cleaning_partial_lane/report.json`、`cleaning_navigation_margin/report.json`；两会话均已关闭。固定分母、刷宽和85%标准不变。
- 当前安全导航候选半径.30m，用于协调实体底盘与CollisionMonitor的.27m停车圈；此前普通/12cm低矮/悬空各5次通过的是.25m版本，原件在 `navigation_safety/separate_layers/configuration/`。新.30m尚未完成最终配置的4项日常场景验收；旧专项矩阵保留为历史证据。原默认导航配置不改。
- 新 `layout_objects_v3.json` 共有17个添加实例，保留v1/v2和原布局：增加另一外观水瓶、塑料杯、卧室平放书，手机屏幕朝上，苹果移到客厅形成跨区变化及厨房空目标。实际调用仍只正式准入杯/瓶/椅。
- 原水瓶GLB经系统Assimp5.2.0临时转换为OBJ、隔离材质纹理并处理轴向，原资源不改；实体尺寸和本轮Gazebo渲染已验证。PBR到OBJ存在材质表现限制，不能据此宣称该外观已完成任务验收。
- 原生相机实际深度960×1280，K的fx759.835对应水平视角1.4rad，RGB-D8Hz、scan5Hz，深度有效69.19%，GPU cuda:0/FP32。证据 `objects_v3/native_wide/sensor_validation.json`、`initial_frame/`。默认640×480/1.02974rad及1m/.25rad保留。
- 只读 `survey_objects.py` 已记录真实停留帧和同时间TF，厨房被动筛查见双碗、双瓶、香蕉等，但出现椅子分裂多计、橙子误为苹果、冰箱未检出；不写入正式记忆或提升类别准入。s与YOLO11m的三张冻结原生图对照保存在 `objects_v3/native_wide/model_comparison.json`，两者均未解决冰箱/橙子问题，没有全面优胜结论。
- 官方YOLO11m-seg权重已下载并核对官方SHA256，记录于 `resources/runtime.lock.json`；目前仅离线候选，在线启动选项尚只支持n/s。未新训练模型。
- 同步深度地面拟合显示约1cm机身高度与约-.005rad俯仰；`tf_frame_audit.json`显示AMCL在map→odom中抵消了部分原生机身倾斜。尚未修改TF，需区分机械高度、里程计和定位框架后验证，禁止凭场景物品真值校正。
- 下次接续：优先排查杂物间受阻位置(-3.70,-.86附近)与清扫回退，推进85%覆盖；同步打磨语义记忆和主动核验，穿插常用区域的物品验收。日常避障按新4项安排，真人麦克风仍最后联调。
- 宽视场续测 `20261121T032325_671204Z_3d3aff75`：床1/164.98秒、健身区球1/226.73秒、杂物间球0/154.45秒。下一任务接受前曾遇瞬时未就绪409，客户端保留原报告后用幂等请求有界重试，客厅杯2/193.32秒完成；`native_wide/continuation/` 与 `living_retry/`。退出跟踪未发现异常信号，本次正常关闭。正式定位阈值与跨布局重复尚待验收，不能只按数量吻合判断通过。
- 被动筛查发现相框内苹果被识别为实体、椅子部件分裂；PCA只能解释部分照片误识，未加入过滤。原生冻结图GPU/CPU结果吻合；被动筛查按3次、实际搜索按2次确认，旧记录中的混用已更正。家具仍是可见表面中心，整体定位偏差待修，不能改标签或降低门槛掩盖问题。
- 清扫位置端点原型仅在新鲜实测位置误差≤.12m时经Nav2取消，保留原动作状态；入口、恢复和停靠仍检查完整位姿。实跑未改善覆盖，故默认关闭；覆盖分母、85%与停靠标准不变。
- 位置端点实际24次按.12m以内取消，整体64.88%（7238/11156）、643秒，处理42/46计划端点；7次恢复最后一次失败，故未补扫。`cleaning_position_completion/` 保留原源码。未采用为默认，显式`--cleaning-position-goals`才启用；后加新鲜停稳屏障避免Humble父动作取消回执早于FollowPath子动作停车，未知终态不继续发目标。这一屏障仅通过12项清扫测试，尚未在完整清扫重测，不将新版本追认为上次实测。
- 主动观察可优先补最多2个语义近景视点：未确认目标，或实际高置信检测且重复投影的桌面线索；仍共用6个补点/420秒预算，只在--active-observation开启。线索来自传感器，预测不增加确认数或已见采样。桌面分支已真实执行，暂定目标分支本批未触发，不能一并宣称实测通过。

### 已确定的长期约定

- 完成同一家庭机器人系统的语音建图、清扫、寻物、盘点。清扫覆盖与补扫、至少 16 类物品、局部避障按问题交替推进；语义地图和自主补充观察进入首轮完整版本，作为项目亮点重点打磨。首轮功能稳定后统一真人麦克风联调；P5导航比较暂缓，当前版本完全做好后再评估其余拓展。
- Ubuntu22.04/Humble/Fortress，NavFn Dijkstra+DWB，YOLOv8n-seg（默认GPU、保留CPU基线）、640输入、置信度.35、AWS IoU .30。不改原基线推进主要功能。
- 现有可调用目标为 chair/cup/bottle，按 3→8→12→至少 16 类规划。已确认 10 类便携物品为杯、瓶、碗、书、手机、花瓶、苹果、香蕉、橙子、球，6 类家具家电为椅子、电视、冰箱、沙发、床、餐桌；均须实际通过识别、寻找、定位、去重和计数后开放。每类在清单约定常用区域内至少3套独立变化布局，选定正式物品案例重复5次并包含冷启动。数量用例在该类布局集合中覆盖，新增验收尚待完成。
- 总计划现按4项日常避障检查：家具/箱子绕行、移动物体让行、正常门口通行、持续堵路反馈。每项一次完整实跑，失败修复后复测相关项；既有安全保护和专项记录保留，最终配置的代表实跑仍待完成。
- 物品和区域关联用于常见摆放、观察点和后续分组查询。实际房间由检测位置确定，各房间接受已接入类别。已核对本地模型标签以及 AWS 的哑铃、球和餐具模型文件。刀叉勺和水果属于现有标签，哑铃需要新增类别数据与微调。成组餐具的独立计数、食品和餐具合计查询均待实现，详情在物品清单第 6 节。
- 房间采用人工多边形、类别固定视点。原独立多位置布局layout_coverage_v1为9杯、7瓶、10椅、1碗、1本书，共28个实例；后续v3另加17个便携实例，两个布局独立，不能混用数量。场景真值只供设计和评估，新增类别通过后同步接入解析、过滤、视点、UI 和部署资源。
- 网页由 `bash scripts/start_robot.sh` 统一启动，已支持寻物、盘点和建图。用户已授权在既定范围内自主实施与本地验证。
- 语义地图、主动核验、清扫与观察协同是已认可的发展方向；模拟充电的课程表达待正式验收前核对。
- 2026-11-21 确认用文本、网页选择及自动化客户端驱动实际任务，按需用合成音频复测语音链路。保留已有录音与转写接口，真人语音待验收状态继续记录。后续功能推进依赖其文本执行和稳定性结果。

### 当前澄清与文件状态（2026-11-21）

- C019至C024的实现与证据见下方历史记录；当时停止机器人开发，仅更新既有文档；本轮恢复见C025增量。运行与来源说明按对应功能同步，不另建总计划。
- 已读取 `skills/grill-me/SKILL.md` 和 `skills/grilling/SKILL.md`，当前通过读取文件执行访谈流程。首轮已确认类别构成和验收标准；用户要求先整体完成、再逐步完善，避免陷入单项优化，也要具备变化场景下的实际能力。时间信息仅作会话排期参考，不写入计划。
- 已确认正常可观察案例计数正确；遮挡或受阻先补充观察、尝试绕行，仍不能确认时保存部分结果与原因。新增标准不能追认为历史实验已通过。
- 第二轮已确认语义地图及自主补充观察必须进入首轮整机版本，而且应重点打磨质量；代表类别先采用至少两种模型或明显不同外观验证，其余类别随后补齐。原因是需要形成能应对变化、具有环境记忆的家庭机器人系统。
- 关键方向已达成共同理解，恢复开发后继续已授权的实现与本地验证。哑铃仍按现有计划列为后续自定义类别；仅在出现影响功能或验收的新取舍时继续 grilling。
- 统一物品目录与跨任务记忆已有子任务实测。用户收敛验收范围后，总计划剩余粗估更新为44–76小时，包含语义地图重点、修复、文本验收与报告；待实际任务时长及失败率进一步校准。

## 历史开发记录（按阶段保留）

以下“当前”“待做”“下一步”和测试数量均对应记录当时的代码与配置；最新状态以顶部摘要及唯一总计划为准。失败、旧版本和当时未执行项保留，不追认为新版本已通过。

### C023 导航防碰撞与数据时效保护（2026-11-21，阶段记录）

- 已安装 Nav2 CollisionMonitor 1.1.20。隔离 ROS 域 71 的真实节点实测：source_timeout=.5 秒后仍放行 .1 m/s；`results/development/navigation_safety/monitor_probe.json` 及日志保留。核对 Humble 官方源码是忽略过期来源，不据此停车；不能照用新版本文档声称其失效保护已经有效。
- 复用该组件做激光/深度几何防碰撞与接近减速，新增 `velocity_guard.py` 在末端检查雷达、有效深度图、障碍云、里程计、动态 TF、仿真时钟和指令时效。稳态墙钟 20 Hz，时钟暂停仍能发零速；传感器/TF .4 秒、指令 .3 秒。可选 `--navigation-safety` 先保持默认关闭。
- 速度链为原 `/cmd_vel`→官方 CollisionMonitor→`/cmd_vel_collision_filtered`→末端保护→`/cmd_vel_safe`→Gazebo；启用后仿真桥接只接收最后一个话题。原导航/建图发布逻辑保留，监控和 UI 增加防护状态，就绪依赖真实新鲜数据和 CollisionMonitor active。配置 `collision_monitor.yaml`、启动 `navigation_safety.launch.py`；原场景入口未变。
- 组合链路在隔离域 71 用真实官方库通过 10 段测试：正常、雷达过期/恢复、无效深度/恢复、TF 过期、倒退、指令过期、障碍停车及解除。`navigation_safety/guard_probe.json`；它不是 Gazebo 避障矩阵验收。
- 初个实际会话 `20261120T182434_302726Z_2337b974` 定位到候选配置错误：Humble approach 的初始检测用 points_inside>=max_points，0 阈值使空场景也停车。已改成 1；保留 `navigation_safety/integration/initial_failure.json`、取消结果及 shutdown。该初轮驱动错误列出 v2 文件散列，报告已另附真实 session 冻结配置/散列并说明差异。
- 候选改用可靠深度图订阅；安全配置的点云适配器改为可靠输入、.1 秒最小周期、仅紧凑 XYZ（保留原采样点、不裁剪范围）。旧基线仍为 BE/.25 秒/原记录格式。紧凑布局含行填充、额外字段和大小端测试通过。工程当前 217 项通过、10 跳过，独立图 3 项通过，两个包构建通过。
- 用实际候选配置的真实组件隔离测试已重复 5 轮×10 段，50/50 通过；工具 `scripts/validation/navigation_safety_isolated.py`，证据 `navigation_safety/isolated_repeated/report.json`。后来仅加强该工具的错误收据、域检查及失败退出，未改变已通过的核心流程。
- 修正后会话 `20261120T183205_505829Z_0eff158b` 厨房找杯 38.17 秒、跨房间客厅找杯约 48 秒通过，端点已证实 `/cmd_vel` 仅被 CollisionMonitor 订阅，Gazebo 仅订阅 `/cmd_vel_safe`。`navigation_safety/integration_retry/search*_report.json`。原点云中断测试输出正确归零并报告 cloud_stale，但暂停可靠订阅者时所有桥接数据含 odom/clock 同时停更；缓存里程计不能证明实体停车，原失败与解释在 `cloud_outage.json` / `cloud_outage_analysis.json`。
- 已正常关闭上述会话，shutdown 无所属残留。安全候选已分离控制（cmd_vel/clock/odom/scan）、RGB-D、点云三组桥接进程；原基线仍单桥接。会话 `20261120T183842_388782Z_96544ba4`（exec 25395，67/8767）首轮通过，随后重复批因客户端没有等待短暂未就绪而在两项通过后退出，旧报告保留。验证器增加 20 秒就绪等待后，`navigation_safety/integration_split/repeated_trials_retry/report.json` 的 5 次实际点云中断、5 次实际取消全部通过新鲜里程计、零输出及任务反馈；恢复后寻物均成功。
- 验证工具 `scripts/validation/navigation_safety_trials.py`；只暂停按 UID/所有权/启动时间/pidfd 核对的本会话点云适配器，物理反馈必须在 .2 秒内且有至少 5 个新时间戳，缓存旧速度不能过关。Firefox 158 的 1440/500 CSS px 无横向溢出，记忆冲突和运动防护显示通过；`integration_split/ui_check.json` 与 `docs/evidence/navigation_safety_ui_20261121.png`，临时浏览器/配置已清理。
- 同会话的静态障碍累计 5/5 通过，分为 `integration_split/obstacle_matrix/report.json` 前三次与 `obstacle_matrix_resumed/report.json` 后两次；首批移除确认超时，已按独有模型名查场景后有界重试，原失败保留。低矮 12 cm 障碍首次发生真实 `waffle::base_link::base_collision` 接触，判失败；悬空尚未执行。场景已恢复，不因后来找杯成功而通过该例。旧报告保存全部接触事件；验证器现改为首次接触即取消、最多保留 64 段样本及总计数，避免持续接触和大日志。
- `integration_split/low_depth_diagnostic/report.json`：在实际位姿 (4.3,-.2,-π) 放置同低障碍，47 帧点云能看到障碍，两个代价图均有致命占据；低障碍有效点高约 .08–.102 m，雷达平面 .121 m。原全局层混用二维激光/深度清除，局部 .1 m 高体素混用两来源；运动时误清除为待验证假设。夹具已核对移除，旧会话已发正常关闭。
- 新独立 `nav2_safety.yaml` 将激光层和深度三维体素层分开最大值融合，并按实体底盘后角约 .237 m 使用 .25 m 外接圆。仅 `--navigation-safety` 选择并冻结该配置，原 `nav2_depth.yaml` 保留；下一步先低障碍复测，再普通/悬空与清扫。尚未证明修复有效，不提升默认配置或验收状态。
- C024 已准备可选官方 `yolov8s-seg.pt`、锁定权重并通过离线资源核验；启动 `--model` 显式记录选项和散列，默认 n 不变，尚未在线比较。当前工程 218 通过、10 跳过，独立场景图 3 通过；后续改动需按影响复测。至少 16 类仍未验收。
- 分层候选会话 `20261120T191441_872639Z_2e4dcb1e`（exec 44155，67/8767）：低障碍 5/5 无接触且找杯成功，来自 `separate_layers/low_probe_retry/` 首次和 `separate_layers/matrix/` 后四次。初个探针仅 DDS 清图回执超时，未运行障碍案例；清图加入有界幂等重试。普通两次通过后批次收到来源未知的 SIGINT，正确取消和恢复夹具，不能算第三次通过；`matrix_resumed/` 在同会话续接余下普通/悬空，exec 28215，`resume_signals.log` 捕获后续发送者。所有旧失败保留，不复用尚未执行的案例。
- 同帧 CPU FP32 对照 n/s ×640/1280 各 8 张真实 RGB-D：s/640 覆盖到两只碗，苹果/橙子误识仍有；只是初探且未覆盖所有房间，不能认定更大模型全面改善。`objects_v2/model_comparison/report.json` 与物品集中收据已记录。
- 记忆 UI 改为默认虚线圈、选中才显示名称/编号，记录按钮可在地图定位；展开状态轮询时保留。真实 Firefox158 的 1440/500 CSS px、按键、实际画布标注和无溢出通过；`separate_layers/ui_check.json` 与 `docs/evidence/semantic_memory_selection_20261121.png`。当前 UI 文件较本运行初始散列有改动，未影响冻结导航配置。
- 后续视觉要核对的已知代码限制：`depth.instance_geometry` 固定排除 map 高度≤.08 m，低于此高度的地面薄小物无法投影；近深度窗为 .7 m，大件家具中心需单独标定。当前低障碍静止点云的地面约 -.018 m，存在约 2 cm 高度偏差，具体机械/仿真来源待查，不能凭假设改 TF。现有桌面基线不改。
- 分层配置的三类障碍15次现已全部通过，夹具恢复；会话2e4dcb1e正常关闭，无所属残留。参数原件在 `separate_layers/configuration/`，保存前逐一匹配启动散列；收据 [navigation_safety_20261121.json](../evidence/navigation_safety_20261121.json)。动态/窄门/后侧向等仍待执行，不启用为默认。
- 清扫冷启动87082798遇到生命周期配置回执丢失，未开始清扫，已关闭并保留 `cleaning_separate_layers/startup_failure.json`。新增 `lifecycle_startup.py` 有界查询实际状态后再转换，避免重复已完成配置；`velocity_guard` 状态查询增加2秒截止。ROS域69的迟到回执协议测试通过，保护组合额外10段通过。测试首轮仅因读取stdout而漏看ROS stderr失败，修正断言后通过；不是产品状态转换失败。
- 修复后冷启动29ed8f0e已实际就绪，清扫157秒返回partial：22.13%（2469/11156），返航误差.0821m/.0933rad、停稳.46秒，成功模拟充电；覆盖仍失败。近端点导航中止后，从已接近的条带末端反向回退4.36m，却只给20秒恢复，导致提前结束。`cleaning_separate_layers/report.json` 与清扫集中收据保留；实例已关闭且无残留。
- 当前清扫候选沿用已有.18m条带起点处理到末端，原动作失败状态保持，并记录实测部分到达后继续的原因，不把它算Nav2成功或用于入口/停靠。恢复时限按距离有界估算；刷盘圆盘跨区域线时只计算实际落在可扫区域的部分。分母11156和85%目标不改。相关9项测试通过，正在完整复测。
- 只读实际代价图显示，若把所有中心限制到cost<60，理论刷盘可达上限只有81.4%，会低于85%目标；未采用该方案。`cleaning_separate_layers/live_costmap_assessment.json`。新增 `survey_objects.py` 被动记录真实搜索停留中的多类掩膜/深度/TF，用于一次路线筛查多类，不能当作准入或完整盘点，尚待实际运行。
- 新会话除关键参数 `configuration_snapshots`，还保存已散列的小型运行源码 `source_snapshots`；权重只记散列，不复制。避免未提交源码继续修改后无法恢复失败版本，证据仍集中在会话目录。

### C022 清扫恢复复测（2026-11-21，未通过）

- 原相机 1.0 m / .25 rad、原白黄杯布局及默认 v4 冷启动，完整任务预算 720 秒。会话 `20261120T181716_570344Z_024d36b6` 实际 276.93 秒返回 partial：覆盖 36.17%，4035/11156 格，返航位置误差 4.223 m、朝向 .380 rad。
- 在 (2.773,3.124) 附近局部受困，回到已成功位姿 (3.342,2.644) 的标准 Nav2 恢复仍失败。新增有界恢复避免了后续连续无效目标，但没有解决覆盖与返航。接下来核对实时深度障碍、规划安全中心及机器人组件通行条件，不能靠加时长或缩减覆盖分母宣称完成。
- 原始 `results/development/cleaning_recovery/report.json`，精选 [cleaning_coverage_20261121.json](../evidence/cleaning_coverage_20261121.json)。已正常关闭，shutdown 无所属残留。新语义记忆冲突字段在该冷启动会话 HTTP 已验证，苹果/橙子两条标为待核验，图为新版适配。

### C021 主动补充观察（2026-11-21，首轮子任务验证通过，稳定性待测）

- 新增 `active_observation.py`，复用已有 RGB-D 可见性和占据地图，以未观察采样增益及路程代价选择后续视点。仅测量深度才能增加已观察量；预测只用于选点。实时安全连通、位姿/代价图新鲜度、最多 6 个新增视点及 420 秒选择预算限制已接入搜索，覆盖不足返回 partial。已读 ETH NBV 官方方法说明；当前为地面机器人启发式适配，不是其 RRT/OctoMap 算法复现。
- 显式 `--active-observation` 启用，默认关闭；`--image-size 640/960/1280` 可独立记录和复现，默认仍 640。UI 显示实测可见采样比例与补点数，保存 `coverage_samples.json`。这不等于识别完整或连续空间全覆盖。
- 清扫旧失败中发现快速清扫行为树无恢复，局部受困后连续目标大量中止。初版增加最多两次标准 Nav2 恢复到已确认位置的尝试（后续已移除全局两次配额，改由有限条带、每次有界恢复及总预算约束）；仍失败则结束后续清扫并尝试返航，不继续空转。实际效果待测，不改变覆盖分母与停靠阈值。
- 会话 `20261120T181137_196801Z_da8caab5` 实跑厨房碗计数：239.92 秒，16/16 视点按 .2 m / .15 rad 审计通过，6 个新增点。实测可见采样从 677/1172（57.76%）到 850/1172（72.53%），新增 173；未到 .85 目标，正确 partial。两只碗坐标误差均≤.25 m，但逐帧确认在原视点 0 和 9，不能把数量收益归因于补点。全部 JSON/SVG/覆盖采样已保存，实例正常关闭，无所属残留。集中收据 `target_expansion_20261121.json` 已增量记录；仅单布局、单次，尚无稳定性结论。
- 从真实苹果/橙子混淆补充了记忆冲突提示：不同便携类别历史位置相距≤8 cm、高差≤10 cm 时，UI 与图标为“类别或物品变化待核验”，不自动挑标签或修改任务结果。纯 SQL 查询覆盖旧记录及按类别过滤，家具支撑重叠排除；图适配版本升为 2，旧图需再导出。相关记忆/UI 70 项及独立图 3 项测试通过，待新会话 HTTP 验证。
- 下一步：完成主动观察实测，处理安全或数据问题；随后按原 1.0 m / .25 rad 相机配置验证清扫恢复和完整覆盖，继续其余类别与局部避障。移动俯仰组件尚未实现，原型资料线索见下一节。

### C020 候选类别接入与多物品布局（2026-11-21，子任务已记录，类别验收未通过）

- `--candidate-categories` 传至 Runtime、只读搜索参数、解析和 UI；新增 13 类显式显示“验证中”，正式准入仍三类。独立 `layout_objects_v1/v2.json` 与 `rooms_aws_house_objects_v1.json` 保留默认布局，观察点不读取新增物品真值。手机仅去掉源 SDF 的 SubT proximity / thermal 插件，原资源保留。
- 官方 YCB 三种水果已恢复，资产总数 12；原网格、纹理、CC BY 4.0 署名、归档与 SDF 散列已锁定。v2 分别在厨房放水果及双碗、客厅放书、卧室放手机，均带评估用几何信息。几何尺寸在 `results/development/objects_v1/ycb_geometry.json`。
- 早期初探遇到未知发送者的控制台退出、批次驱动 143、YCB 材质路径尾空格及多个 OBJ 同名材质/纹理串用。已修复临时派生资源的命名隔离和路径空格；原资产不改。旧中断、失败与串纹理图像保留，不能用这些图像下模型能力结论。信号发送者尚未查明；后续 strace 已能核对主动正常关闭的发送者。各实例均有 shutdown，无所属残留。
- 修复后会话 `20261120T180139_758436Z_5649697e` 实跑 6 项，以类别、数量和旋转后的资产中心核对：香蕉、橙子、书寻找通过（XY 误差 .057/.053/.097 m）；苹果返回位于橙子处，误差 1.339 m；双碗只计 1；手机未找到。每项仅一次，不能作为多布局稳定准入。相机为 1.2 m / .4 rad，n 模型 640 GPU，未替换默认相机或权重。
- 原 n/1280 离线同帧对照可检出手机与更多薄小目标，但有其他类误检；官方 s 权重也仅用于离线比较，尚未替换在线权重。文件在 `objects_v1/frame_detections_n1280.json` 及 `objects_v2/material_isolation/first_frame*_detections.json`。不做标签重映射修补苹果/橙子误识。
- 集中收据 [target_expansion_20261121.json](../evidence/target_expansion_20261121.json) 保存所有前序运行路径、配置、原始结果和一对一位置审计。材质修复实例已正常关闭，只读采集保留 8/29 计划视点，不称完整覆盖；旧采集器已退出。
- 动态相机目前仅调研：Fortress 6.18 有 JointPositionController / JointStatePublisher，支持 use_velocity_commands / initial_position；ros_gz_bridge 有 JointState↔Model 转换。若实现须同时调整 SDF 的两级固定相机链与 URDF，并核对物理关节和动态 TF。高相机大俯角有利桌面，但会限制高家具的完整视野，后续须分高度验证。

### C019 统一物品目录、语义记忆与开源场景图（2026-11-21，子任务验证通过）

- 用户追加：语义地图应复用已有方法和开源成果，在其基础上验证改进；已授权继续逐步开发、测试、验收和优化。已查阅 ConceptGraphs、Hydra、Spark-DSG、Clio、SemExp 官方代码与安装说明，选型和接入状态维护在 `SOURCES.md`。当前复用 Spark-DSG 图结构，尚未复现 ConceptGraphs 的外观/几何融合或 SemExp 策略。
- `objects.py` 统一 16 类标签、中文名和准入状态；原三类继续开放，新增 13 类在 UI 中标为待验证。`semantic_memory.py` 以 SQLite 保存真实结果、来源、时间及空间关联记录，按实际占据地图和房间几何隔离，处理重复导入、相邻物品、歧义和旧观测。没有把记忆写回本次计数，也没有导入场景真值。
- `robot_console.py` 接入搜索结果写库、按房间和类别查询及地图版本检查，UI 增加历史位置与证据查看。`scene_graph.py` 调用 Spark-DSG 1.1.3 构建家庭—房间—物品图并重载核对，保存空间记录 ID；完整外观身份和移动后重识别仍未实现。
- 独立 `.venv-semantic` 准备脚本和 `requirements-semantic.txt` 已验证，默认 `deploy.sh` 已调用。图适配及记忆测试 18 项通过；完整 ROS 环境工程测试 186 项通过，7 项隔离 ROS 客户端和 3 项独立语义 SDK 用例跳过，后者已在语义环境另测 3 项通过。
- 本机旧安装仍引用旧构建目录，新构建首次遇到安装链接冲突。仅备份并重建生成的 `install/semantic_search` 后两个包构建通过，默认环境可导入新增模块；备份已清理。可选 SDK 的模块级跳过曾触发 ROS 测试插件整目录跳过，已改为逐用例 fixture 跳过并完整重跑。
- 第一会话 `results/sessions/20261120T170938_902296Z_e56bd1d9/` 实际 GPU 厨房找杯通过：38.07 秒，找到 1 个，任务 `8b296103-88ea-4732-a7cf-7f755b832d12`，写入记录 `22143b292048415da50faaecb759cca9`。已正常关闭该会话。
- 第二会话 `results/sessions/20261120T171509_481652Z_103575db/` 冷启动恢复原 ID、时间和次数；实际盘点 151.58 秒确认 1 杯，更新同一记录为 2 次任务观测。Spark-DSG 自动保存 7 节点、6 条边，HTTP 重载与证据、房间及修订号一致。
- Firefox 158 实际网页验证通过：1440 与 500 CSS px 无横向溢出，显示物品记忆、地图及图导出；请求 390 px 时浏览器最小宽度为 500，按实际值记录。正常 Snap 入口和项目 downloads 临时配置解决二进制 glibc / 私有临时目录问题；浏览器、配置与临时驱动已清理。
- 两次运行均正常关闭，shutdown 回执无所属残留，8767 已释放。单份收据 `docs/evidence/semantic_memory_20261121.json` 与网页截图集中保存；产品记忆与图保留在 results。下一步实现可显式启用的候选类别验证入口，随后开展资产与 RGB-D 多布局验证，同时推进清扫覆盖、局部避障与主动观察。本子任务通过不代表 16 类或完整 P6 已验收。

### C018 新电脑部署验证（2026-11-19）

- 新增 `scripts/deploy.sh`，用系统 Python 还原资源、安装 CPU 依赖并构建。按默认布局自动还原白黄杯和芥末瓶，固定与 colcon 兼容的 `setuptools==78.1.0`。每个检出目录拥有独立的构建路径和 ASCII 别名。
- 临时干净副本在线恢复资源并构建成功。CPU 模式网页就绪，实际传感器检查和厨房找 1 杯通过，重新准备后的离线语音可转写合成音频。工程测试 167 项通过，临时副本、缓存及日志已清理。用户确认发布到现有公开仓库。[部署说明](GITHUB_DEPLOYMENT.md)

### C017 清扫后返航与停靠通过（2026-11-19）

- `scripts/run_cleaning.py` 使用实际记录的起点和已标定的出房间路径返航，为最终对位预留时间。靠近起点且原目标失败时，可分开尝试位置接近与朝向恢复。仍须同时满足 0.15 m、0.15 rad 并停稳至少 0.45 秒。单元测试核对朝向超差时保持返航未完成。
- 首次测试在记录起点后未更新定位新鲜度计时，导致首个导航目标被过早终止。修复为每次发送目标前用已确认的新鲜位姿刷新计时，冷启动后续测通过。
- Gazebo 健身区短程试验将任务时限设为 135 秒，实际清扫后经出口返回初始位姿，耗时 109.82 秒，位置误差 0.116 m、朝向误差 0.097 rad、停稳 0.46 秒。覆盖率 13.7%，任务正确保存为部分完成，Firefox 显示模拟充电及清扫地图。工程测试 167 项通过，7 项独立 ROS 用例按开关跳过。两次测试实例已关闭，测试端口释放，域 67 无节点。[阶段收据](../evidence/p4b_docking_20261119.json)
- 暂停点。恢复后优先按完整预算试验的遗漏图诊断不可达区、条带与补扫，再做同标准覆盖验证和四功能连续演示。基本任务与报告预算 12–19 小时，详见总计划。真人麦克风和课程对模拟充电的确认仍待安排。

### C016 P4b/G2 清扫与返航首轮（2026-11-18）

- 网页新增“清扫房间”，接受按房间选择和确认后的语音指令。执行入口为 `scripts/run_cleaning.py`，占据栅格、往返条带和覆盖计算位于 `src/semantic_search/semantic_search/cleaning.py`。沿用现有 Nav2、入口坐标及五区地图。
- 覆盖口径为机器人中心可通行并可由 0.50 m 假定扫幅触达的已知地面。按实际地图位姿计数，目标 85%。返程使用本次记录的起点和朝向，0.15 m / 0.15 rad 内停稳才显示“模拟充电”。覆盖不足或停靠不达标时返回部分完成并保存结果。
- 首轮健身区完成 42.4% 覆盖，返航停在距起点 2.13 m 处，已保存 JSON、实际轨迹和 SVG。实时 Nav2 代价地图显示部分静态空闲位置受障碍影响。改为按连续条带分组、使用实时代价图拆分受阻条带，并缩短清扫目标的恢复时间；入口和返航仍使用原导航行为。
- 一次复测因 Nav2 初始化脚本漏收 DDS 状态回执而中断，已增加有时限的查询重试。其后同场景完整预算复测覆盖 34.9%，耗时 261.14 秒，停在距起点 0.426 m 处，朝向误差 2.679 rad。条带分组方案仍需优化，覆盖未达到 85%。
- Firefox 以合成普通话“请打扫卧室”启动实际清扫，途中取消后的 51 个里程计样本线、角速度均为零，随后厨房寻物找到 1 杯。原始数据集中于 `results/development/p4b_g2/`。真人麦克风与课程对模拟充电的认可待正式验收。

### C015 P4a/G1 自动验收完成（2026-11-18）

- 网页建图依次退出 Nav2 和搜索、启动 SLAM 和 `mapping_motion`。核心文件为 `scripts/robot_console.py`、`scripts/robot_runtime.py`、`scripts/robot_monitor.py`、`scripts/run_mapping_motion.py`、`src/semantic_search/semantic_search/mapping_motion.py`、同目录 `mapping_control.py` 与 `ui/`。
- 键盘、网页按钮和确认后的语音文字共用运动保护。单次短动最多 1.5 秒，行进限速 0.06–0.18 m/s。合成普通话经 Firefox 转写并驱动前进约 0.180 m。前后移动、转向、加减速、取消、长按超时及忙碌时拒绝切换通过。
- 前后障碍距约 0.35 m 时立刻停止。补扫后绕过小箱净移约 1 m，绕行中取消后观察到连续零速度。宽屏障及初次未探索通道拒绝绕行。绕行须下达新指令，由已探索栅格与当前激光计算路线。
- 新图保存 YAML/PGM，独立重载 83,402 格逐格一致，保留 51,801 个未知格。恢复原五区导航后，厨房找杯、盘点各得到 1 个，JSON/SVG 已保存，原地图散列一致。新图用于五区任务前须核对定位与房间标定。
- 切回导航的首轮验证将正常的 6 个速度发布端点误判为冲突，修正为核验发布节点。另有初次未就绪 409 与重载测试的 DDS 回执超时，已续测。工程 158 项和独立 ROS 7 项通过，测试实例已关闭，66/67/69 域无节点。原始数据集中在 `results/development/p4a_g1/`。[P4a 阶段收据](../evidence/p4a_g1_20261118.json)
- 下一步沿用既有地图与 Nav2，先为选定房间生成可清扫栅格及往返路线，再实测覆盖、遗漏和补扫。随后以实际起点验证返航、停靠和 UI 模拟充电，最后综合演示。真人试用可单独安排。

### C014 P4/G0 自动验收完成（2026-11-18）

- 搜索节点在 `/search/progress` 发布实际导航、观察、等帧、取消及保存阶段。网页以 `request_id` 对应任务、进度和停止。共用任务记录覆盖搜索、转写和传感器检查。修改涉及 `search_node.py`、`semantic_map.py`、`run_search.py`、`robot_monitor.py`、`robot_console.py` 和 `ui/`。
- 浏览器录音由 `.venv-voice` 的离线 Whisper 转写，显示可编辑文字并等待确认。合成普通话经 Firefox MediaRecorder 实测找到1杯、盘点4椅、杂物间未找到、取消、静音拒绝。取消两秒后的202个里程计样本速度为零。真人麦克风尚待试用。精选 [P4验收](../evidence/p4_g0_20261118.json)，原始数据集中于 `results/development/p4_g0/`。
- 首次盘点因首视点多计1把椅，第一候选又有一次漏左前排，保留 `voice_ui_initial.json` 和 `kitchen_initial_candidate_audit.json`。第二候选调整首点并加入两个前排补看点，厨房椅子路线由14增至16点。同配置在两个独立冷启动会话及后续热运行中完成五次盘点，共5/5数量、定位、到点和产物审计通过。最大物品XY .16775m、到点XY .13826m。当前默认 v4 已提升，旧快照 `rooms_before_calibration.json` 与 `profile_selection.json` 保留。其余房间和类别路线按配置逐一比对一致。
- 前排探测工具曾退出143，发送者未知。在核验原导航目标完成、客户端已退出后另采剩余两个点。复测脚本的环境加载问题和缺失参数均在发布任务前发生，已修正并用完整批次重跑，未计作通过。完整失败路径见阶段收据。
- 键盘建图通过，实际位移 .524m 并生成激光占据地图。修正 `scripts/save_map.sh` 的 trinary PGM 空闲阈值为 .19，并允许显式输出新路径。重载82,806格与 SLAM 原图一致，未知格保留，原地图文件散列一致。YAML 原点舍入误差最大约4.6mm。短路线用于链路验证。
- 工程154项通过，7项 ROS 客户端测试另在域69通过，提升默认后9项配置测试通过。各自动测试会话 clean，当时确认67/68/69域无残留。

### 真人麦克风验收（统一安排在最后）

- 原待测会话 `results/sessions/20261118T061411_635301Z_406acd34` 已关闭，未收到真人试用结果。恢复试用时重新启动当前版本，核对真人语音转写和实际执行产物。C014 合成语音的证据继续保存在原收据。
- 全部功能开发和自动回归稳定后，再由操作者统一测试录音权限、转写、确认、实际执行和停止。基础功能和拓展开发先按文本及合成音频的实测结果继续。

### C013：GPU及P1–P3基线验收完成（2026-11-18）

**目标与授权**：用户要求GPU验证后继续完成P1/P2/P3，已撤销C012结束时的停止要求；常规实施和验证无需重复确认。完成本阶段后报告结果，后续开发顺序仍为P4/G0→P4a/G1→P4b/G2。

**已验证事实**：

- 独立`.venv-gpu`：torch2.14.1+cu130/torchvision0.29.1+cu130、CUDA13.0、Ultralytics8.4.207、numpy1.26.4；RTX4060 Laptop8GB、驱动580.178.04。原CPU环境保留，未改系统或驱动。`scripts/prepare_gpu.sh`负责项目内安装。
- `robot_console.py`/`robot_runtime.py`一键默认`cuda:0`，支持`--device cpu`；会话记录设备/环境/配置散列。旧分终端视觉入口仍默认CPU，可设`SEMANTIC_DETECTOR_DEVICE=cuda:0`。`detector.py`显式FP32，原权重、640/.35/.30不变。
- 同6张RGB-D图像各60帧：同环境CPU/GPU中位16.95/4.41ms，3.84倍；检测数一致，框/掩膜IoU最低.999786/.999010。实际GPU找杯1/数椅4通过，检测约7.99Hz、RGB-D8Hz、scan5Hz，进程显存约268MiB。不是整机加速比。见 [GPU收据](../evidence/gpu_inference_20261118.json)，原始`results/development/gpu_20261118/`。
- GPU遮挡12/12、异常恢复45/45及57项JSON/SVG/观测次数审计通过，夹具和参数恢复；证据`results/development/p123_gpu/{occlusion,fault_recovery,fault_artifact_audit.json}`。工程152项通过、7项ROS客户端本轮未重复（C012已有独立7项通过）。
- 正式案例未改动的15组×5次严格审计75/75：`p123_gpu/unchanged75_{report,audit}.json`。最大物品XY.12745m、到点XY.13283m/朝向.12463rad。按完整案例组保留全部5次，逐路线核实旧/新配置一致，不能称单会话连续100次。
- 原布局缺失24扫视点均Nav2到达并抓帧，最大XY.11973m/朝向.10004rad；`remaining_baseline_navigation.json`和`baseline_captures/manifest.json`组合61条记录。`baseline_visibility.json/png`按类别路线保留未观察采样点，几何可见不等于识别完整。
- 新布局`layout_coverage_v1.json`有9杯/7瓶/10椅/1碗/1书。首轮15项严格通过8项，`placement_probe/aws_house/`、`placement_probe/audit.json`；七项遗漏保留。书/碗仍未开放，现有碗图像未检出。
- 校准观察点后，新布局健身椅计数5/5严格通过，`gym_refined/{report,audit}.json`。七项补点诊断`supplement_count/audit.json`严格5/7：客厅杯3/椅1、健身瓶1、杂物间杯1/瓶1恢复，客厅/卧室各一只地面瓶仍漏检。单帧偶尔检出不等于完整任务可靠识别。

**修改、依据与未采用方案**：

- 默认v4已在正式审计通过后提升；提升收据`p123_gpu/promotion.json`。实测候选`p123_gpu/rooms_refined.json`仅将卧室杯/瓶首对视点x=-8.3改为-8.1，并给健身椅增加正面[0,2.6,2.3]、[-.1,2.9,2.4]替换桌后点；旧快照`rooms_v4_before_refinement.json`保留。独立新增布局配置为`src/semantic_search/config/rooms_aws_house_coverage_v1.json`；实测快照`p123_gpu/rooms_coverage_tested.json`，结束后仅修正说明字段，不改路线。
- `scripts/validation/audit_search_results.py`增加到点TF/动作结果审计；冻结XY≤.20m、yaw≤.15rad，控制器原.12m/.10rad不改。`tests/test_acceptance_audit.py`覆盖缺TF/超差；五区测试允许实测校准卧室位置，仍要求双朝向与完整扫视。
- 默认导航仍NavFn Dijkstra+DWB、`nav2_depth.yaml`。PoseProgressChecker候选仅8朝向对照均通过（原37.70s/候选37.93s，无收益证明），完整候选路线未验证；文件归`p123_gpu/nav2_observation_candidate.yaml`，不启用。
- 新布局杂物间驶出曾172秒进展失败，`bottle_chair_navigation.json`；实际连接方向[-3.4,-2]→[-2,-2]可退出，`bottle_chair_retry_navigation.json`。不据一次成功声称所有路线修复。靠墙间距.20m的校准候选已撤出，原4点实测和取消记录保留。
- 客厅地面芥末瓶多角度被误认fire hydrant，卧室地面瓶单帧检出而任务漏检；不改标签、不降阈值、不用真值补结果。`supplement_navigation.json`、`floor_angles*_navigation.json`、`*_frames.json`保存校准过程。

**失败与进程管理**：

- 原正式B50项严格46/50：卧室瓶首次两点到达约.213m；健身椅两次计数1/预期2，另一次数量正确但位置偏差约.85m。`formal_b/audit.json`保留失败。
- 原正式A前5次通过，第6次因服务退出超时900秒；`formal_a/`保留原报告，`formal_a_completed5.json`只收完整前缀。重启A完成35个未改动案例后由本代理按身份SIGTERM停止，余下旧卧室重复由候选新批替换；`formal_a_retry/superseded.json`、各`shutdown.json`可追溯。
- 早期外部终止来源仍未知；最初strace默认忽略跟踪器信号的空日志不能证明未发生。`motion_check/simple/adoption.json`记录核验PID/UID/启动时间后接管、完成34点并清理。后续独立进程会话保留正常信号处理及所属清理，不能称根因已解决。

**最终结果、文件与证据**：

- 域67独立冷启动`p123_gpu/refined_baseline/aws_house/`的五组×5次全部严格通过；与未改动75次合并的`final100_audit.json`覆盖20组×5、100个唯一任务ID。最大物品XY.19152m（卧室瓶）、到点XY.13283m/朝向.12463rad，最大任务墙钟303.75s。冻结标准未放宽。
- 精选 [阶段验收收据](../evidence/p123_gpu_acceptance_20261118.json) 包含100次来源、57项异常、原场景回归、覆盖、全部失败路径、配置散列及清理。不是连续单配置100次，早期失败不删除。
- `baseline_final_captures/`有65条同布局实测引用，`expanded_final_captures/`75条；两套配置所有观察点已采齐。`baseline_final_visibility.json`、`expanded_visibility.json`保留各高度未观察采样点；[基线可见性图](../evidence/p123_gpu_coverage_20261118.png)可直接查看，不宣称全房全部物体可见。
- 最终工程152通过/7跳过，`p123_gpu/final_tests.{json,log}`；首轮漏设scripts模块路径的收集失败另存`final_tests_missing_pythonpath.*`，修正调用后通过，没有对应产品缺陷。7项ROS专用用例已有C012独立验证。
- 所属正式批次退出均clean；新增布局会话`results/sessions/20261117T175718_684264Z_79372d02/shutdown.json`无残留。`p123_gpu/final_domain_checks.json`确认66/67/68无节点，监督脚本、控制台和只读采集器均已退出。没有待接管的运行任务。
- 总计划P1/P2/P3已标完成；README、RUNNING、DEVELOPMENT_VALIDATION、REQUIREMENTS_STATUS、TARGET_CATALOG同步。新视点已通过工程测试，不需为文档改动重复机器人实验。

**当时的限制与下一步（后续进展见顶部摘要）**：

1. 当前已完成的是固定家庭场景的传感器、地图、文本寻物/计数核心及覆盖诊断；新增布局的两处地面瓶漏检保留，不称任意位置完整识别，书/碗不开放。完整课程任务一至四仍未全部验收。
2. 下一开发阶段沿唯一总计划进入P4/G0：先在现有搜索协议/UI接真实导航/观察阶段反馈，再补共用任务接口与真实语音输入，验证语音寻物/统计、停止和失败反馈。随后P4a建图运动控制，P4b清扫/返航；本批未启动这些新功能。
3. 默认CUDA FP32，原CPU环境和旧配置/失败快照保留；日常`bash scripts/start_robot.sh`，回退加`--device cpu`。当前无需要用户重新确认的常规决定；后续模拟充电课程表达须在正式验收前核对。
4. 工作区修改未提交、未推送；保留已有C012变更。重要决策继续更新本摘要，实验具体过程集中在本批证据，不另建重复计划。

保存本摘要不等同于执行宿主原生上下文压缩；未恢复的信号发送者等历史保持未知。

### C012历史：P1–P3验收与多位置探测（当时已按要求停止，C013已恢复）

**当时目标与停止要求（历史）**：完成P1–P3剩余实现及验收，追加多物体/多位置覆盖检查。用户11月18日要求本批结束后停下；现在所有所属测试实例已关闭，不自动补测、不切换GPU、不继续P4。唯一总计划仍是DEPLOYMENT_PLAN；P1完成，P2/P3尚未完成。

**已验证事实与证据**：精选收据 [p123_acceptance_20261118.json](../evidence/p123_acceptance_20261118.json)，原始证据集中在 `results/development/p123_acceptance/`。

- 两个ROS包构建通过；工程149项通过，7项ROS用例在完整套件按开关跳过、随后独立域69实测7项通过（`client_discovery_fix_retry/`）。149项结果来自实际工具输出，7项另有逐例收据。最后仅调整离线覆盖图排版，无运行核心变更。
- P1五区连接/起点21次到点通过，最大XY0.1192m、朝向0.0986rad（`connections_navigation.json`）；scan约5Hz、RGB/depth约8Hz。18视点独立导航/RGB-D通过，最大XY0.1382m、朝向0.1106rad。冻结后续到点审计0.20m/0.15rad，控制器原0.12m/0.1rad不改。
- 原baseline找1/计数2通过；旧AWS首次计数3/预期4失败，独立复核找1/数4通过（`legacy_aws_retry/aws_house/`），偶发漏检不抹去。v3剩余20例与产物/定位审计通过（`v3_remaining20/`），与旧27次成功分开统计。
- 杂物间边缘球误识别为chair：调整观察点并过滤截断检测后，五次计数1通过（`utility_confirmation_retry/`）。客厅垃圾桶误识别为cup：可见尺寸检查排除它，离线六个真实杯瓶样本保留，后续客厅杯计数正确（`size_filter_calibration.json`、`expanded_remaining/`）。厨房椅子截断漏检经三处前/后排视点校准，五次计数4通过（`formal_kitchen_chair_v2/`）。
- 当前正式100例**累计33例通过严格数量/定位/ID/JSON/SVG/观测/路线审计**（`completed33_audit.json`），分为5+25+3，非连续通过。原95例批次中断，只抽取前25例；最新70例批次完成3例、第4例取消、66例未执行，退出143，需补67个有效案例。`formal_remaining70_retry/`保存中断及清理收据；原95例缺完整退出收据，不补写。
- 受控遮挡12例通过：两种视点基准、五次正面遮挡0/换侧面恢复1，屏障移除、参数恢复（`occlusion_retry/`）。异常/恢复45例通过：邻房过滤、不可达、TF、检测器中断、取消停车、隔离无效深度及恢复，各重复5次（`fault_recovery/`）。57项产物核对通过（`fault_artifact_audit.json`），隔离深度子节点和转发线程均已停止。
- 新增独立布局 `scenes/aws_house/layout_coverage_v1.json`：20个放置目标加原8把椅子，共28个（9杯、7瓶、10椅、1碗、1书）。15项计划仅完成厨房杯2/瓶1两项并通过定位/产物审计，椅子任务计数4但被取消，不能算通过，后12项未执行（`placement_coverage/`）。15张实测RGB-D离线检查中，厨房侧视画面可见的碗未检出；书及其他房间新增位置未验证，书/碗未开放任务调用。
- 基线覆盖已采37/61条清单记录，缺24个扫视记录；可见性报告明确缺失位姿，见`visibility_coverage_available.json`及 [覆盖图](../evidence/p123_coverage_20261118.png)。几何可见不等于识别充分，不能把未采集区域当作已验证覆盖。新增布局帧未混入基线覆盖。
- 浏览器桌面/真实390px只读检查通过（`ui/report.json`）；未在停止要求后另起UI任务测试。11月18日GPU检查为RTX4060 Laptop 8GB、驱动580.178.04；视觉环境torch2.14.1+cpu，当前推理没有CUDA加速，未切换配置。

**关键修改与决策**：

- v4各区增加8方向固定扫视，保留类别桌面首点；厨房补[5,-1.5,.8]、[6.5,-1.4,pi/2]、[8.9,2,-2.9]，杂物间两点改为[-6,-2.6,-2.35]、[-6.5,-3.1,-2.75]。`ui/app.js`合并同XY多朝向显示。模型、阈值和导航算法不变。
- `depth.py`/`search_node.py`增加可选截断过滤和分割深度尺寸检查，一键入口启用，旧入口默认关闭。杯XY包围盒对角线≤0.25m/高≤0.30m，瓶≤0.35m/0.60m；只作用于掩膜路径，是可见表面先验，不是真值或精确尺寸。修正整数观察点传入ROS浮点坐标问题。
- `run_search.py`发现判据要求同一节点既订阅command又发布result，避免被只读跟踪器误判为服务就绪。7项真实ROS客户端测试通过；初版Humble不支持API造成的失败在`client_discovery_fix/`保留。
- `robot_runtime.py`/`robot_console.py`支持启动时选择项目内rooms/layout并记录散列；`development.py`复用项目内已有家具资产目录。`navigate_route.py`及`validation/{audit_search_results,capture_observation_views,visibility_coverage,occlusion_recovery,fault_recovery}.py`增加事后审计和可恢复夹具。真值始终只用于设计/评估。

**阻碍、失败与清理**：

- 最新两个长批次均收到终止信号，驱动退出143；取消由退出清理送达客户端，**最初信号发送者未知**。不能归因于模型、用户或已修复的发现竞态。首次70例启动参数发现失败、早期外部SIGINT/取消、厨房计数3、球/垃圾桶误检和采集JSON错误均保留原路径。
- 主会话`results/sessions/20261117T154823_480004Z_bbbd81d1`已按核验PID/UID/启动时间退出；域68正式及域67新增布局均有`shutdown.json`确认clean。随后只读检查66/67/68域均无节点，未结束其他用户进程。
- 当前没有运行中工作或需要重复确认的常规决策。保存本摘要不等于执行宿主原生上下文压缩。

**当时待续步骤（现已由C013接续）**：先查明长批次终止原因；按精选收据逐案例补正式67次有效结果与24条基线扫视采集。再完成新增布局剩余13项有效任务及漏检定位，必要时调整独立候选视点。完整产物/覆盖/退出验证后再将P2/P3标完成，随后沿用P4/G0→P4a/G1→P4b/G2。当前不启动这些工作。

### C011：五区配置与标注图

- 用户确认五区并授权配置坐标、观察点、UI、绘图skill图片置于总计划前。当前一键入口/解析/UI已切至 `rooms_aws_house_v4.json`，原四区v3未改；中部以y=1.0拆为下方客厅/上方健身区，其余覆盖范围不变，无新增墙体。
- 新增 `scenes/aws_house/spatial_v4.json`、`tests/test_five_zones.py`，UI从后端配置读取五区轮廓、名称及可选观察点。139测试通过、5项隔离ROS测试跳过；静态坐标检查通过，健身区3个视点Nav2实走通过；浏览器12项通过，证据在 `results/development/five_zones/`。
- 会话 `results/sessions/20261117T105354_590939Z_9f841a29` 已停止且shutdown无残留；健身区找椅子在第2视点途中随会话停止而canceled，不能记为寻物成功，停止信号来源未确定。此前已走通3点的独立导航记录不受影响。尚未完成五区完整感知/覆盖验收。
- 内置imagegen已生成 `docs/assets/house_five_zones.png` 并插入总计划开头，精确坐标图为 `house_five_zones_coordinates.png`。用户指出左侧蓝紫边界偏离挡板：实际模型RoomWall_01_001的y=-1.496180，程序边界y=-1.5（差约4mm），生成图标注偏移已修正，程序坐标保留。
- 修正版图片已置于总计划前，旧图片草稿仅留本地results；RUNNING/接口已更新。验证摘要并入现有 `docs/evidence/oneclick_ui_20261117.json` 的 `five_zone_update`，不新建重复报告。
- 用户要求后续语言准确、简洁、清晰，减少无用运行记录/重复文档，已加入AGENTS。GitHub主体更新已发布并核验：`ca462b8`，文件树与本地提交一致；本地发布前提交保留在备份分支。日常继续使用main。

### C009–C011阶段已实现与已验证

- 原场景和AWS场景的传感器、SLAM、定位导航已实测；原baseline计数2椅、AWS厨房找1/计数4，结果/标记一致。
- 独立候选：实体相机支架、高1m/下俯.25rad、深度障碍输入；三房间桌面杯瓶和双杯5次重复已有通过记录。
- 搜索节点已有文本/JSON、取消、中文结果、map米制坐标、去重编号、JSON/SVG/RViz输出；逐视点到达/停留/数据诊断及有界补等已实现。
- 当前候选房间配置 `src/semantic_search/config/rooms_aws_house_v4.json`；布局 `scenes/aws_house/layout_r0_yellow_v1.json`；导航 `src/semantic_search/config/nav2_depth.yaml`；detector/search显式 `sensor_reliability:=reliable`。独立包装脚本默认仍是旧v1/BE；新一键入口已固定v4/reliable，分终端复现须显式指定，见 [RUNNING.md](RUNNING.md)。
- 旧45例为44通过/1 partial；补等后卧室15例通过。可靠输入新批27通过，第28次客户端发现失败且没有发任务，后17例未执行。客户端发现等待已修复：默认15墙钟秒，超时/中断前不发布任务；矩阵看门狗同步延长。
- C006工程66项及隔离ROS客户端5项通过。C009整理后的检查收据见 [目录整理核验](../evidence/reorganization_20261117.json)，不会把离线检查计成新机器人实验。

### 历史限制与失败决策

- 蓝杯被识别为bowl，降低相机/紧容差/960输入未解决；保留640及原阈值，改用白黄杯独立布局。失败数据已归档。
- 卧室v1/v2短程移动/恢复问题保留；v3同位置双朝向重复较稳定，实测朝向差仅约6°，不代表全房覆盖。`full_room_coverage_verified=false`。
- 旧客户端误收保留结果已改VOLATILE并排除旧任务ID；逐点缺帧用partial反馈和有界补等。RELIABLE短窗数据改善，但底层传输/调度根因未定。
- 当前仍是单任务串行执行；跨任务空间记录 ID 已在 C019 实现，移动后物理身份仍待验证；完整统一运动仲裁、清扫覆盖和语音人工联调仍待完成。
- 完整历史、具体参数、早期源文件散列及失败经过见 [归档交接](../archive/history/HANDOFF_before_cleanup_20261117.md) 和 [验证概览](DEVELOPMENT_VALIDATION.md)。历史未恢复部分不补写。

### C009结构整理

- 长期文档统一在 `docs/maintained/`；原始教材在 `docs/course_materials/`；历史在 `docs/archive/`；精选 `docs/evidence/`保持原路径及内容。
- 根HANDOFF/SOURCES只保留短入口，根README负责入门；[docs/README.md](../README.md)是阅读索引。
- 6个旧专项脚本及配套C++源码移入 `archive/tools/`；已结束的开发批次和旧日志压缩在 `archive/runs/`，逐文件校验后再清理原目录。保留最新可靠输入批次、用户manual_demo及已跟踪的原场景验收数据。
- 只删除可再生成的旧构建/Python/pytest缓存；运行源码、install、外置构建、依赖、资产、地图、权重和全部未提交修改保留。迁移/恢复索引见 [reorganization_20261117.json](../../resources/maintenance/reorganization_20261117.json)。
- C009为结构维护；C010已按新授权恢复启动/UI集成实验。相关代码和文档已随C011发布。保存摘要不等同于执行宿主原生上下文压缩。

### C010：一键启动与控制台

- 新增 `scripts/start_robot.sh`、`robot_runtime.py`、`robot_monitor.py`、`robot_console.py` 及 `ui/{index.html,app.js,style.css}`；入口无需激活venv，默认打开网页、Gazebo和RViz，绑定127.0.0.1:8765，默认域66，每次独立IGN分区与 `results/sessions/<时间_ID>/`。
- 实际数据驱动就绪判定、map/TF显示、文字/选择寻物与统计、单任务互斥/幂等、取消、结果链接与本次历史已接入。静态地图保留原点朝向，过期位姿不显示为实时定位；不使用场景真值控制搜索。
- 两次GUI冷启动通过；第一会话传感器检查通过（scan约5Hz、RGB-D约8Hz）、厨房找杯子和计数均1且JSON/SVG已保存；第二会话取消后恢复寻找成功。浏览器宽屏/390px、无JS错误、刷新不重发任务已有证据。
- 修复启动后写盘失败遗留子进程、取消等待过长、关闭时未等待任务记录，以及Popen后进程身份暂不可读导致取消无效的竞态。进程清理只处理本会话token/UID/启动标识核验后的进程，浏览器不带此标记。
- 实际浏览器开始/停止按钮也已验证；取消2秒后的193个odom样本速度为0。两次运行均正常清理；结束时最终会话无所属残留进程、8765端口已关闭，普通浏览器可留在断线页面。
- 工程测试134通过、5项ROS客户端测试本轮跳过；没有重复运行P3正式矩阵。本轮证据和原始会话路径统一见 [oneclick_ui_20261117.json](../evidence/oneclick_ui_20261117.json)。原10项基线散列保持不变。
- 首版仍是现有搜索协议的适配器：无跨功能ROS Action/运动仲裁、实时导航步骤、麦克风、建图操作、清扫或跨运行语义历史。请求ID与核心task_id分别保存；不要再从外部终端向同域并发发任务。

俯视截图：`results/screenshots/house_top_20261117/house_top.png`，来自当前白黄杯家庭场景的Gazebo实际窗口；仅调整临时GUI相机，未修改正式场景或房间配置。

本次计划复核仅修改既有文档：总计划纠正三房间旧表述，区分已完成的搜索UI接入与待完成的共用任务协议，明确v3/v4证据和五区验证顺序；要求对照、验证概览同步修正。未新增实验或验收结论，无新增待确认决策。

## 下次恢复开发

当前保持暂停。恢复后按[总计划第5节](DEPLOYMENT_PLAN.md#5-当前进度与下一步)，先处理清扫覆盖与受阻恢复，同步打磨语义地图和现场核验，穿插常用区域16类与4项日常避障，随后整机回归、部署与报告、最后真人麦克风。完成标准沿用总计划，不重复访谈已确定的决定。

技能位于`skills/`，发现入口`.agents/skills`保留；当前通过读取SKILL.md执行context-compression与grill-me/grilling。保存状态摘要不等于执行宿主原生上下文压缩。仅在出现影响执行或验收的新取舍时提问，每轮最多3个独立问题。
