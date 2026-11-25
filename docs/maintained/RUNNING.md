# 当前候选运行指南

适用于已经准备好依赖的本机：家庭场景、默认v6/service_surfaces_v2布局、实体相机支架和可靠传感器订阅。新机器先阅读 [部署说明](GITHUB_DEPLOYMENT.md)。无需手动激活视觉虚拟环境。

## 答辩素材取用

优先取用[13页可编辑答辩演示稿](../../results/development/demo_two_rooms_20261123/delivery_preflight/defense_deck_styled/defense_presentation.pptx)、[PDF](../../results/development/demo_two_rooms_20261123/delivery_preflight/defense_deck_styled/defense_presentation.pdf)或[完整ZIP](../../results/development/demo_two_rooms_20261123/delivery_preflight/defense_deck.zip)：文字可编辑，原图嵌入，另附两段4倍UI片段和冻结证据。已实际Office打开/逐页核对；成员、学号、实际贡献和真人四功能仍待补。最新失败也在讲稿中，不能据此称全部验收。下方8页包仍保留为原始选材。

按老师四章模板整理的[可编辑报告草稿DOCX](../../results/development/demo_two_rooms_20261123/delivery_preflight/report_draft/project_report_draft.docx)与[PDF预览](../../results/development/demo_two_rooms_20261123/delivery_preflight/report_draft/project_report_draft.pdf)已生成并实际打开核对。报告保留原图/证据范围和失败，姓名、学号与实际分工待填；不是真人麦克风通过记录或最终提交稿。

打开[离线素材目录](../../results/development/demo_two_rooms_20261123/delivery_materials/index.html)，或解压同目录`delivery_materials.zip`后打开`index.html`。8张1920×1080 PNG可直接插入PPT，原图/视频和审计可单独取用，`manifest.json`保留原文件路径、SHA-256及5会话的冻结配置/源码。它是所选证据包，运行环境、模型和场景资产仍按部署说明恢复。

目录注明各自真实会话与验收范围：三球清扫partial仅作限制/避障子项，记忆更新不代表合格提速，UI视频不当相机录像；不同会话不拼称连续任务。实际搬移离线浏览、500px及视频全解码通过，见[素材审计](../../results/development/demo_two_rooms_20261123/delivery_preflight/materials_browser/audit.json)。需要重新生成时使用新输出目录，脚本拒绝覆盖已有包：

另提供[8页素材PPT](../../results/development/demo_two_rooms_20261123/delivery_preflight/presentation_materials.pptx)与[PDF预览](../../results/development/demo_two_rooms_20261123/delivery_preflight/presentation_materials.pdf)。均为已核验PNG整页置入的16:9素材页，可插页/重排，并非已写完的答辩叙事稿或可编辑图表；[实际Office打开与导出审计](../../results/development/demo_two_rooms_20261123/delivery_preflight/presentation_audit.json)核对8页与标准页面几何。

```bash
python3 scripts/package_demo_materials.py --output results/development/demo_materials_new
```

当前定位追加优化按用户安排暂缓，未新增AMCL候选；不因此升级image来源或语义收益的稳定性验收。当前配方的卧室书本连续文字预检find1/count2、两处必巡/≤.20m/接触0/时效0/回充通过；真人麦克风仍需实际联调。“找一本书”只找一个，需要全部用“统计卧室有多少本书”。

## 厨房碗与卧室书的新增布局候选

`layout_service_bowl_book_v1.json`保留原9个杯瓶实例，厨房餐桌、L形操作台各加1碗，卧室书桌、床头柜各加1本书。当前物品目录中碗/书仍为候选，首轮寻找/计数和原杯回归状态见[本次审计](../../results/development/demo_two_rooms_20261123/bowl_book/audit.json)，尚未完成3变化布局和5次正式重复。

```bash
bash scripts/start_robot.sh --domain 67 --port 8767 \
  --layout-file scenes/aws_house/layout_service_bowl_book_v1.json \
  --rooms-file src/semantic_search/config/rooms_aws_house_v14_bowl_book_near.json \
  --candidate-categories bowl book \
  --model yolov8s-seg.pt --image-size 1280 --camera-resolution 1280x960 \
  --auxiliary-model yoloe-11s-seg.pt --auxiliary-categories book
```

这是显式候选配方，原n640/v6默认不变。v14保留全部厨房/卧室两处必巡姿态，仅将卧室杯/书的两个远距离补充点收敛为原有近处互补点；不限制其他房间合法任务或用摆放真值填结果。较早v13/S1280出现卧室杯3/2（垃圾桶误识）；n640+书辅助的比较配方双碗/双书均只计1，原失败保留。不要把不同配方的成功拼作同一配置稳定验收。当前实例已运行时先核对会话、避免重复启动。

语义变化案例使用上述同一配方，把`--layout-file`改为`scenes/aws_house/layout_service_memory_cup_moved_v1.json`，并加`--memory-guidance`；只移动餐桌一只杯子，其他12目标和观察点不变。该案例的冷加载收据已保存；当前运行会话以HANDOFF为准，不能同时再开一套。公共任务仍不包含真值坐标。单轮现场find1/count2、旧位置待核验/新位置更新及重载通过，首次定位超差失败保留；厨房必巡前缀不变，不当提速演示。素材与限制见[阶段收据](../../results/development/demo_two_rooms_20261123/semantic_followup/audit.json)。

三静置球场景使用`scenes/aws_house/layout_service_cleaning_three_balls_v1.json`，与无新增球清扫单独留证。最近实跑79.68%/16of25仍partial，虽检出/绕行/继续/回充通过，可达残余未清完；不要当完整清扫通过素材。精确启动配置、补扫/漏扫分析和实际UI片段见[收据](../../results/development/demo_two_rooms_20261123/cleaning_followup/ball_trial/repair_followup/audit.json)，当前运行会话看HANDOFF。

## 点云传输候选（显式启用）

在现有启动命令追加`--depth-cloud-source image`，其余场景、相机、模型、导航和记忆参数仍按所选案例。默认`native`保留原生点云基线；image仅适用于当前Fortress相机。启动先核对三对不同源戳、完全同戳的原云/深度/内参，独立校准通过才输出；随后复用已有深度图，惰性原云桥接停止大载荷订阅。内参/尺寸/帧/编码仍逐帧核对，输入源龄.25秒和导航.4秒门槛保留，校准失败不会把缺失点当自由空间。

当前1280×960显式候选已通过实际载入/原云停流、真实障碍代价0→100→0及完整静态观察窗时效；两次实际find/返航134235次源时效检查0超界；语义对照因记忆组定位25.3cm超20cm停下，仍未通过整项。候选尚未替代默认或完成四项日常避障回归。[实际配置、校准和验证收据](../../results/development/cloud_continuity_20261122/depth_image_candidate_20261124/audit.json)。新模块不需额外Python依赖。运行状态见HANDOFF，已有实例时不要重复启动。

## 导出地图素材

地图区域“导出视图”选择栅格、分区、语义记忆、观察点方向、清扫实际轨迹、清扫实际覆盖、导航代价或关系图，点击“保存所选地图”下载PNG/SVG/原始JSON。语义和关系图沿用物品记忆的房间/类别筛选；任务视图先在本次运行历史选择相应已保存任务。跨会话旧素材按原证据路径查，不通过HTTP传文件路径。清扫轨迹和覆盖独立导出，原覆盖率/partial保留，目标房间外不标作不可达。

预设点与实测观察方向分开，方向图不代表全房视觉覆盖；关系边读取与记忆一致的真实Spark-DSG。导出时间和源采集戳分别记录，图片是快照。导航代价仅接受当前新鲜原生全局map帧；局部odom代价图尚未接入。旧后台仍只显示代价按钮，更新源码后正常重启加载统一入口。新机器按部署说明安装python3-pil和fonts-noto-cjk。

## 当前阶段与真人麦克风联调（2026-11-24）

按用户调整，以所选答辩案例打通四功能，再由用户真人麦克风验收；16类全面准入与全屋清扫不作前提。新增碗/书、语义定位追加优化按用户安排暂缓，已有失败保留。按后续C041决定，重点清扫房间以80%且全部可达原规划条带实扫验收，保留720秒预算；未达标如实partial，不以降低覆盖结果替代通过。真人联调可在基础链路预检后开展。数量错误、无法停车或回充失败仍属于需修复问题。预检状态以HANDOFF为准。

当前日常启动默认使用`rooms_aws_house_v6.json`与`layout_service_surfaces_v2.json`，厨房餐桌/L形操作台、卧室书桌/床头柜均必巡；本布局厨房杯瓶各2、卧室杯2仅供事后评估，计数由感知产生。C040床头柜杯2、定位/回充单次通过，原v1遮挡与修复前v2尺寸拒绝失败均保留。旧v4/v5及布局保留，可用原有`--rooms-file`/`--layout-file`显式回归。当前会话地址与是否仍运行见HANDOFF；已有实例时直接打开网页。

同一网页依次使用“录音转写”，允许麦克风，检查文字后提交；逐项核对转写与实际执行：

| 顺序 | 真人操作/指令 | 观察与保存 |
|---|---|---|
| 1 | 进入建图，录音“前进”“停止”，再按需测试后退、左右转、加减速 | 实际运动、停车及遇障反馈；地图变化，保存YAML/PGM |
| 2 | 返回导航，等待定位及自动回充结束 | 恢复原图、机器人位置正确、固定处模拟充电 |
| 3 | 录音“去厨房找杯子” | 餐桌及操作台均巡视、当前感知结果、位置/标记、报告和自动回充 |
| 4 | 录音“去厨房统计杯子” | 两区已巡视状态、数量按评估布局事后核对、去重编号、地图/记忆更新及回充 |
| 5 | 录音“清扫卧室”（或“清扫杂物间”） | 实走轨迹、覆盖≥80%及原条带实扫逐项核对，受阻/漏扫保持partial，核对正常回充 |
| 6 | 再启动任务并用停止按钮取消；另录音“返回充电处” | 取消应停稳且不自动回充，手动回充可单独执行 |

导航模式取消使用停止按钮；录音“停止”的运动指令在建图模式测试。逐项记录通过/失败/未测及会话请求ID；识别错字先改正再提交，原转写错误也要记录。自动预检和合成音频均不算真人麦克风通过。

### 当前可说的指令与数量含义

当前“去厨房找椅子/杯子/瓶子”寻找一个实例，完成必巡区域后可提前返回；需要找齐该类物品，请用“去厨房统计椅子”“去厨房清点杯子”“厨房有多少瓶子”。不要根据find返回1推断房间只有1个。房间可换为客厅、卧室、杂物间、健身区。未指定数量的“找”默认暂不改变。

展示清扫优先用“清扫卧室”或“清扫杂物间”；回充用“返回充电处”。建图模式可说前进、后退、左转、右转、加速、减速、停止、绕行。进入/退出建图、保存地图使用网页对应按钮。导航任务取消使用停止当前任务按钮；录音期间转写与任务共用互斥，当前不支持边执行边录音发起紧急语音停止。

### 在UI展示避障（2026-11-23）

地图下方“地图图层”可选“占据栅格底图”或“底图＋导航代价”。红色占据、橙色禁行膨胀、黄色通行代价、灰色未知；过期时保留上一帧并明确标记，不将缓存当作实时图。勾选“预设巡视点与朝向”查看实际房间配置的必巡点与类别视点；任务中跟随实际目标、显示已观察/当前方向，非实时物品检测点。原同位置8朝向路线仍保留，显示修复不代表路线效率已优化。

当前旧占据清除已按真实有限/经校验无回波射线修复，原标障流不变；只有重新观察到的自由空间才清除。箱阻计数2/2、同会话移除清除/旧通道重新通过及移动障碍回归通过；但第二次计数3/2失败仍需诊断，不称为连续稳定计数。[当前证据](../../results/development/demo_two_rooms_20261123/clearing/audit.json)。

刷新现有控制台，切到“运行地图”，勾选“实时激光与规划路径”。橙色点为实测激光，圈和数字标出当前方向近障；蓝色虚线为原生Nav2规划路径，任务实际轨迹沿用原图层。“实时避障观察”显示中心距离、方位、实测线/角速度及近障变化记录，终端同步打印`[避障观察]`。观察有效期.4秒，路径2.5秒；过期数据不画成当前观测。静止/运动是实测状态，任务绕行成功仍需看实际路线和最终结果，.70m提示阈值不改变导航控制。激光图层不覆盖所有仅深度可见障碍。

当前展示复测：卧室85.81%/18条完整通过，杂物间90.08%/25of26仍有一短条带漏扫；4项日常避障代表实跑及清理后卧室查找/两处必巡/回充通过。[集中收据](../../results/development/demo_two_rooms_20261123/audit.json)。当前端口/会话以HANDOFF为准。

## 1. 日常一键启动

```bash
cd "/home/willmatic/桌面/semantic_object_search"
bash scripts/start_robot.sh
```

不需要激活虚拟环境，也不需要分别打开六个终端。脚本加载 ROS 和桌面运行库，依次启动 **Gazebo → 定位导航 → 视觉/搜索 → RViz**，同时打开本地网页 **http://127.0.0.1:8765**。机器人默认出生于客厅西侧的固定充电处，地图以紫色方块标注。等待页面显示“就绪”后再发送任务。

网页支持以下操作。

- 查看组件、雷达、RGB-D、定位状态，以及实际占据地图、五区轮廓/名称和机器人位置；可打开所选物品的观察点。
- 选择房间、物品和“寻找/统计”，或输入“去厨房找杯子”等文字任务。
- 点击“录音转写”并允许访问麦克风，说完可提前结束，最长 8 秒。检查填入的文字，再点击“开始任务”。语音资源用 `bash scripts/prepare_voice.sh` 准备。
- 查看前往哪个观察点、扫描进度和当前确认数量，随时停止任务。任务结束后可查看坐标、编号、JSON/SVG 和本次运行历史。
- 寻物/盘点先保存和显示结果，再自动返回固定充电处；返航期间仍属于当前任务。清扫结束也回同一充电处，建图结束切回导航后回充。可用“返回充电处”按钮或文字指令单独回充。停止/取消会停车，不再自动返航；返航失败仍保留已确认物品和原报告。
- 点击“进入建图”，可用方向键、网页按钮、文字或语音控制底盘。建图操作见 [下节](#3-建图保存与地图重载)。
- 在导航模式选择“清扫房间”和目标房间，或输入“清扫卧室”。也可以录音转写并确认。全房遍历会花数分钟，右侧显示覆盖、补扫和返航进度，地图显示实际轨迹。
- 点击传感器检查，采样10秒并生成报告；这只检查基础数据与TF，不替代四项课程功能验收。

每次启动创建独立的 `results/sessions/<时间_ID>/`，保存配置、组件日志、请求、任务产物和退出收据，不覆盖以前的结果。刷新网页会恢复当前状态；关闭网页不会停止机器人。**在启动终端按 `Ctrl+C` 退出整套系统。** 不要再同时执行下面的分终端启动命令。

网页清扫预算固定为720秒；`--task-timeout`仅控制搜索任务，不调整清扫预算。短预算专项验证需明确记录测试进程中的预算设置。

2026-11-22起清扫目标为80%，同时检查全部原规划条带的实际覆盖，不能达到80%就提前退出。界面显示已完成条带数；未完整扫过或受阻的区域保留在结果中，仍可能显示部分完成。当前重点展示卧室与杂物间，新增球障碍另留partial与受阻明细。

C041补扫改为“保留主条带、未扫区域优先换方向短补扫”，同一可扫底图和.50m刷宽/.35m间距不变。它不会强制全房横竖各扫一遍；相隔的漏扫块分开规划，预测线不计实扫。是否实际进入补扫及收益以选路记录/实际新扫格为准，不能将未触发补扫的整房结果算作补扫提效对照。

家庭地图支持“语义地图 / 运行地图 / 房间与物品关系”切换。语义地图按类别着色，虚线历史位置需要现场核验，橙色提示待核验；点击标记或关系节点可打开实际观测档案。顶部历史记录数不代表当前房间物品总量。“运行地图”用于查看导航与清扫轨迹；关系图展示当前同版记忆中的房间归属，不是额外维护的底图。

新增点位实验需同时显式加`--memory-guidance --memory-safe-approach`，默认关闭。2026-11-24客厅香蕉ABBA四次正确性通过，但新增点均无有效投影，有记忆两组反而慢18.56/24.90秒；不推荐把该实验作为收益展示。原记忆排序功能保留，移动核验与提速分开验收。

`--precision-docking`为独立显式候选，仅充电处到达使用.05m执行目标和原生rotation shim最终朝向控制，独立验收仍.15m/.15rad及停稳；普通寻物/清扫控制参数保持。初版五次回充位置过、随后移动例终点朝向停滞失败，修复版以最新实测收据为准，不能凭配置称稳定通过。

候选记忆引导可在启动时显式加`--memory-guidance`，默认关闭，实际收益尚在对照验证；它优先历史成功的可选视点，必要时在已有近点增加最多一个朝向；保留必巡前缀及全部配置回退，不改变计数路线，也不会用历史记录补数量。实际到访数与完整预留计划分别记录。

书和球的文本视觉辅助候选可显式加`--auxiliary-model yoloe-11s-seg.pt --auxiliary-categories book 'sports ball'`，主模型保留、辅助最多2Hz。先执行`python3 scripts/prepare_runtime.py --model yoloe-11s-seg.pt`恢复官方基础权重并核验仓库内冻结提示嵌入；日常推理不需要下载或加载文本编码器。该配置仍在变化布局复测，类别准入看交接和清单，不能把19个词表标签当成19类已验收。

跨房清扫按实际距离给入房和返航有界时间，并从清扫预算中预留返航；短距离条带保持原时限。此前从厨房到卧室会在固定40秒时被过早取消，已修预算并增加实测停靠超差后的校正，完整复测结果见交接。若仍入房失败，结果会区分入房超时与导航失败，并显示返航停靠结果；原失败收据保持原样。

清扫结束可下载报告、轨迹 JSON 和清扫地图 SVG。覆盖率以底图和机器人可达性估算的可清扫地面为分母，按实际定位轨迹累加。返回固定充电处并停稳后，页面显示“模拟充电”。覆盖不足或返航未达标时，任务显示部分完成。总任务耗时包含返航；原感知结果仍保留感知阶段耗时。首个固定点回充已实跑通过，五区及完整清扫集成验证状态见交接。

充电配置为`src/semantic_search/config/charging_station.json`，绑定实际地图YAML/PGM双SHA，冷启动冻结到会话。默认位姿为map `(-1.8,-4.0,0)`，并用于场景出生。更换底图必须重新标定，不能只改坐标继续沿用旧地图绑定。历史“返回任务起点”回归可显式加`--no-charging-station`；日常保持固定充电处启用。

常用选项：

```bash
# 不打开Gazebo/RViz窗口，保留真实仿真和网页
bash scripts/start_robot.sh --headless

# 使用原CPU环境
bash scripts/start_robot.sh --device cpu

# 不自动打开浏览器，手动访问终端打印的地址
bash scripts/start_robot.sh --no-browser

# 原ROS域或网页端口已被其他程序占用时选择空闲值
bash scripts/start_robot.sh --domain 67 --port 8766
```

验证历史配置时可加 `--rooms-file <项目内JSON>` 或 `--layout-file <项目内JSON>`；实际选择与文件散列会写入会话记录，日常运行无需设置。当前v4包含周向观察，统计会执行完整路线，耗时通常比单物体寻找更长。

原生宽视场及多类开发候选可这样启动；候选尚未达到新增类别的正式准入标准。

```bash
python3 scripts/prepare_runtime.py --model yolov8s-seg.pt
python3 scripts/prepare_target_assets.py --layout scenes/aws_house/layout_objects_v3.json
bash scripts/start_robot.sh --model yolov8s-seg.pt --image-size 1280 \
  --camera-resolution 1280x960 --camera-fov 1.4 \
  --camera-height 1.2 --camera-pitch 0.15 --navigation-safety \
  --layout-file scenes/aws_house/layout_objects_v3.json \
  --rooms-file src/semantic_search/config/rooms_aws_house_objects_v1.json \
  --candidate-categories bowl book 'cell phone' vase tv refrigerator couch bed \
    'dining table' apple banana orange 'sports ball'
```

分辨率会改变实际仿真相机，`--image-size`改变模型输入，两者独立。默认启动仍使用原640×480相机和n/640。安全候选当前半径.30m，最终配置的4项日常避障仍待验证；先前15次障碍子集对应.25m配置，详见验证记录。

候选类别开发时可显式使用下列配置；UI 标为“验证中”，不表示类别已经通过验收。运行前用 `python3 scripts/prepare_target_assets.py --layout scenes/aws_house/layout_objects_v2.json` 还原该布局资产。

```bash
bash scripts/start_robot.sh --headless --no-browser \
  --layout-file scenes/aws_house/layout_objects_v2.json \
  --rooms-file src/semantic_search/config/rooms_aws_house_objects_v1.json \
  --camera-height 1.2 --camera-pitch 0.4 --active-observation \
  --candidate-categories bowl book 'cell phone' apple banana orange
```

主动补点和高相机仍在开发验收。结果保留未观察区域及部分完成原因；当前有苹果/橙子混淆、薄目标漏检。`--image-size 1280` 可另行对照，默认 640；先核对识别、误识和数据时效，再决定是否采用。

清扫近程恢复实验需显式添加`--cleaning-local-recovery`；默认关闭。它在旧端点距离超过1m时，从近期连续实测轨迹中选择当前可通行的近处回退位置，沿用原Nav2恢复。两次720秒预算试验分别提前以25.98%和10.45%部分完成，未证明覆盖收益；第二次暴露零位移恢复反复成功却不能继续规划的问题。日常保持关闭，详细失败与下一步见交接。位置端点实验也继续默认关闭。

C031另复用Nav2原生PositionGoalChecker处理清扫条带端点，当前候选使用原.12m位置门槛，清扫专用DWB移除RotateToGoal并由原生RotationShim衔接短换道方向；普通入房/恢复/回充仍保留.12m/.1rad完整朝向。局部滚动代价图与behavior使用map并加载静态层，使规划/控制/到达检查坐标一致；需冷启动，不能仅以改参回执作为生效。PoseProgressChecker同时计平移或转角进展，候选.20m/.50rad/10秒；单目标与总截止仍生效。导航失败后优先在实测安全停稳位置尝试有界重排，再尝试旧锚点恢复，固定分母与85%不变。这不同于旧客户端取消端点实验，实际收益见交接，不据配置认定覆盖达标。
条带末端直接提交经静态/实时逐格核验的密集参考Path，沿用Nav2 FollowPath/RotationShim+DWB；连接、入房与回充仍使用NavFn。C032选定默认n/640版本最高单次72.80%（8122/11156），固定回充通过，85%未达标。主路线按最新掩码切段，之后才重生成未扫补扫；原静态规划中心另留一格跟踪余量，原分母不变。实际直达参考安全时保留，仅穿邻障时回接原条带；Nav2成功而实际odom未平移.20m不当作恢复成功。清扫报告另可下载选路JSON及代价图/覆盖NPZ。停止原因会明确区分预算耗尽、恢复时间不足、受阻恢复、定位、路线/补扫耗尽及取消，不把规划轨迹计为已扫。五区及建图恢复后的固定回充已有通过，当前源/配置见交接与收据。

C033收益调度候选需显式添加`--cleaning-budget-selection`，默认关闭。它在预计单位时间新扫收益高25%时提前选择后排主条带或补扫，保留未选工作，并检查估计耗时能否适合剩余清扫窗口。整房实跑70.32%且连接受阻后回充失败，未替代默认路线。恢复默认后的冷启动取消停车、六项下载及手动回充通过；这不补足85%或整房稳定性验收。


C034默认开发导航配置已复用独立激光/深度层，轮廓由.22m增至.25m包住实体后角；普通FollowPath也由原生RotationShim衔接方向，底层仍原DWB和完整朝向检查。机身/支架接触只用于诊断，不采集持续轮地流量。清扫连接按当前掩码四邻距离估计40–180秒预算，总720秒及回充预留不变，不可达时仍用原欧氏后备；它不等于NavFn实际路径长度。整房单次61.35%、回充通过且无机身接触记录；原连接专项位置误差.1044m，但朝向超时，不能算完整到达。原85%和最终配置日常避障仍待验收，详见交接。

C041局部间距诊断：默认房间配置/附加1格不变，`rooms_aws_house_v11_margin0.json`仅为健身区附加0格候选。`scripts/validation/cleaning_clearance_probe.py`需显式指定同域空闲会话、离线候选路线和新输出目录，经当次传感代价图重验后才通过原生Nav2执行一段；它不是网页整房任务或80%验收。观察机身/支架接触、源时间戳和动作后停车；`--preflight-only`只检查准备条件、不发移动目标。可临时指定`--cloud-min-period 0.1`，退出确认停车后恢复原值，0.4秒门槛不改。高分辨率、轻量GUI及无GUI试验的失败均保留；不能据离线可规划就全局缩轮廓或删除未扫区域。

C041点云链路修复：普通开发启动也采用控制、RGB-D图像、原始点云、接触四个独立桥接进程；点云adapter以RELIABLE/depth1接收原云，处理周期.1秒，输出仅保留XYZ（同一采样密度）。原RGB图像/深度图和识别接口不变，最大输入源龄.25秒与运动诊断.4秒门槛保留。普通导航仍使用nav2_depth，未因此开启CollisionMonitor候选或调整安全半径。修复前/后及移动、GUI验证见`results/development/cloud_continuity_20261122/`。

导航保护候选使用 `--navigation-safety`，包含官方 CollisionMonitor、最终速度时效保护、独立控制/图像/点云桥接，以及 `nav2_safety.yaml` 的独立激光/深度三维障碍层。默认暂未开启，按最终配置完成4项日常避障与整机回归后再决定切换；验证情况见总计划和交接。

较大分割模型可显式对照，原 n 权重保留：

```bash
python3 scripts/prepare_runtime.py --model yolov8s-seg.pt
bash scripts/start_robot.sh --model yolov8s-seg.pt --image-size 1280
```

s权重已固定来源和散列，已用于原生宽视场多物品及手机寻找/计数实跑，仍有误识与漏检，默认n不变。YOLO11m与YOLOE免提示模型仅做过离线对照，未进入在线启动选项。

新增多物体测试布局可手动选择：

```bash
bash scripts/start_robot.sh \
  --layout-file scenes/aws_house/layout_coverage_v1.json \
  --rooms-file src/semantic_search/config/rooms_aws_house_coverage_v1.json
```

该布局配套独立补充观察点：首轮15项通过8项，七项遗漏补点复核通过5项；客厅、卧室的地面芥末瓶仍漏检，尚不适合用于全物体准确盘点。具体结果见 [验证概览](DEVELOPMENT_VALIDATION.md)。日常默认已使用餐桌/操作台两区布局；原yellow/v4保留为显式回归配置。一键入口默认GPU推理，使用独立`.venv-gpu`；原CPU环境保留，可加`--device cpu`运行。GPU环境首次安装执行`bash scripts/prepare_gpu.sh`。

同一项目只允许一个一键实例。启动失败时网页保留原因和日志，退出后修复再运行。地图中的机器人图标只使用新鲜的 `map→base_link` 位姿，数据过期时页面会禁用任务提交。

### 地图与结果查看

当前保留建图YAML/PGM、单次寻物/盘点SVG和清扫原始产物，并可从统一入口导出7类空间视图及关系图的PNG/SVG/原始JSON。清扫轨迹/覆盖可独立输出，观察点图不代替全房可见性验收，局部代价尚未接入；详见[地图方案](DEPLOYMENT_PLAN.md#地图数据与输出视图)。

当前导航经`map_resources.json`的`aws_house_v1`读取`scenes/aws_house/r0_v1/maps/house.yaml`，另外两处同版地图保留为兼容副本；现存副本分歧会在启动时拒绝混用并提示路径。控制台会话冻结主YAML/PGM及选择收据，实际显示/记忆仍依据运行时`/map`。建图保存为新版本快照，用于服务前需重新核对区域、观察点和充电标定，不手工分别修改多份底图。

分终端导航脚本支持显式`map_id:=aws_house_v1`或`map:=<项目内YAML>`；兼容路径自动指向主图，未注册版本保留独立选择。保存脚本`bash scripts/save_map.sh scene:=aws_house`默认写入新的`results/maps/aws_house/<版本>/map.yaml`及PGM；可用`map_output:=<新前缀>`指定位置。注册底图和已有输出均禁止覆盖，保存后不自动替换默认导航地图。此变化同样保护baseline及历史版本。

## 2. 构建与分终端调试

首次部署或修改ROS包后构建：

```bash
cd "/home/willmatic/桌面/semantic_object_search"
bash scripts/build.sh
```

### 每个调试终端的公共配置

下面六个终端都先执行：

```bash
cd "/home/willmatic/桌面/semantic_object_search"
export SEMANTIC_ROS_DOMAIN_ID=66
export IGN_PARTITION=semantic_manual_demo
source scripts/env.sh
```

同域不要重复启动两套机器人节点。以下命令相对于项目根目录执行。

### 分终端依次启动

**终端1：Gazebo。** 等场景加载完成。

```bash
bash scripts/development.sh gui:=true \
  layout_file:=scenes/aws_house/layout_r0_yellow_v1.json \
  evidence_dir:=results/development/manual_demo
```

**终端2：导航。** 等待 `Localization and navigation active`。

```bash
bash scripts/development_navigation.sh
```

**终端3：视觉。**

```bash
SEMANTIC_DETECTOR_DEVICE=cuda:0 bash scripts/development_detector.sh -p sensor_reliability:=reliable
# 复现原CPU基线时，将上面的cuda:0改为cpu
```

**终端4：搜索。**

```bash
bash scripts/development_search.sh \
  -p rooms_file:="$PWD/src/semantic_search/config/rooms_aws_house_v4.json" \
  -p scene_id:=aws_house_manual_demo \
  -p output_dir:="$PWD/results/development/manual_demo/tasks" \
  -p sensor_reliability:=reliable -p reject_clipped_detections:=true \
  -p validate_object_size:=true
```

**终端5：RViz。** 包装脚本处理已有桌面运行库冲突。

```bash
bash scripts/rviz.sh scene:=aws_house
```

**终端6：传感器检查及任务输入。**

```bash
python3 scripts/validate_sensors.py --seconds 10 --sensor-reliability reliable \
  --output "results/development/manual_demo/sensors_$(date +%Y%m%d_%H%M%S)"
```

检查通过后，每次执行一条任务，等待结束再发下一条：

```bash
python3 scripts/run_search.py '去厨房找杯子' --timeout 480 \
  --output "results/development/manual_demo/find_cup_$(date +%Y%m%d_%H%M%S).json"

python3 scripts/run_search.py '去客厅统计瓶子' --timeout 480 \
  --output "results/development/manual_demo/count_bottle_$(date +%Y%m%d_%H%M%S).json"
```

完整任务产物在 `results/development/manual_demo/tasks/<任务目录>/`，包含 `result.json`、`observations.json`和收到地图时的 `semantic_map.svg`。

### 手动栈停止与其他工具

取消当前任务：

```bash
ros2 topic pub --once /search/command std_msgs/msg/String "{data: '取消'}"
```

退出时先取消任务，再依次停止搜索、检测、导航及RViz，最后关闭Gazebo，各终端按 `Ctrl+C`。

- 基础场景和原AWS场景：见 [AWS_HOUSE.md](AWS_HOUSE.md)。
- 矩阵验证：`python3 scripts/run_search_matrix.py --help`，每批使用新输出目录，准确记录启动条件。
- 原场景回归准备脚本：`bash scripts/validation/legacy_regression.sh`，必须在结束现有测试栈后显式执行；已有CPU原场景回归及退出清理证据，旧AWS偶发漏检记录保留，见验证概览。
- 一键入口固定当前候选配置：white/yellow单杯布局、v4五区视点、可靠传感器订阅、原导航与视觉参数；查本次实际参数请读会话的 `session.json`。

## 3. 建图、保存与地图重载

1. 按日常方式启动。在网页点击“进入建图”，等实时地图和运动保护就绪。
2. 按住 W/A/S/D 或方向键连续移动，松开或按空格停车。网页方向按钮仍逐次执行。也可输入或录音转写“前进”“后退”“左转”“右转”“加速”“减速”，核对文字后执行。文字与语音的单次行进或转向持续最多 1.5 秒。
3. 遇障时停车并显示距离。需要绕开时下达“绕行”，系统只在已探索且足够宽的区域尝试通过。可随时停止。
4. 停车后点击“保存地图”，下载当前任务里的 YAML 和 PGM 文件。点击“返回导航”恢复使用已校准的默认地图及五区配置。

使用新地图开展五区任务前，应核对初始定位、区域和观察点。保存的地图可用下方地图服务器步骤独立重载。

### 带电动门的场景

启动增加 `--room-doors`。该模式给厨房、卧室、杂物间和健身区配置与客厅相连的实体推拉门，并为规划生成同坐标系的开放门洞底图。Gazebo 中门扇初始闭合，有碰撞体。机器人导航前先到对应门前停车，再发请求等待关节反馈，确认开到可通行位置后过门。门保持打开供后续返回；返回也核对出口。
建图模式可通过键盘开到门前、停稳后按「打开附近的门」。近门操作也接受文字“开门”“关门”。关门须避开门扇移动区域。新场景的实际清扫、寻物和回充需要按该配方单独验收。


### 网页 Gazebo 画面

一键启动后，网页可显示 Gazebo 发布的机器人相机画面。增加 `--gazebo-preview` 会启用独立全屋俯视相机，可在网页切换「全屋」和「机器人」。俯视相机以 4 Hz 仿真频率渲染，允许与 `--headless` 一起使用。实际帧率受机器负载和仿真倍率影响。性能对照时，两组使用相同的预览设置。

Gazebo 原生编辑、实体选择和相机漫游在桌面 Gazebo 窗口中使用。要同时打开该窗口，启动命令去掉 `--headless`。

### A* 全局规划试用

在一键启动命令后追加 `--astar`，可与 `--room-doors` 一起使用。该模式用 NavFn 在代价地图上优先对目标运行 A*，按代价地图的栅格中心转换路径坐标。无法提取到目标的路径时，转用 Dijkstra 搜索，包括原配置允许的目标容差范围。去掉 `--astar` 可使用原规划配置。

对照全局规划性能时，先固定代价地图、起终点和插件，只切换 A* 与 Dijkstra，再分别记录规划耗时和路径长度。实际机器人任务耗时另行测量。

### 分终端调试

退出一键控制台后，从项目根目录给各终端加载同一环境。

```bash
export SEMANTIC_ROS_DOMAIN_ID=68
export IGN_PARTITION=semantic_keyboard_mapping
source scripts/env.sh
```

1. 启动仿真，等待雷达开始发布数据。

   ```bash
   bash scripts/development.sh gui:=true \
     layout_file:=scenes/aws_house/layout_r0_yellow_v1.json \
     evidence_dir:=results/keyboard_mapping/scene
   ```

2. 在另一终端启动 SLAM，再用第三个终端控制底盘。此时仅由键盘节点发布速度，保持 Nav2 和 AMCL 关闭。

   ```bash
   # 第二个终端
   bash scripts/mapping.sh scene:=aws_house
   # 第三个终端
   ros2 run teleop_twist_keyboard teleop_twist_keyboard \
     --ros-args -p speed:=0.2 -p turn:=0.7
   ```

3. 在空旷位置用 `i` 前进、`j` 和 `l` 转向，按 `k` 停车。停车后另开终端保存到新目录。

   ```bash
   bash scripts/save_map.sh scene:=aws_house map_output:="$PWD/results/keyboard_mapping/house"
   ```

4. 停止键盘和 SLAM，启动地图服务器。在另一个终端配置并激活它，通过 RViz 或 `ros2 topic info /map` 查看。

   ```bash
   # 地图服务器终端
   ros2 run nav2_map_server map_server --ros-args \
     -p use_sim_time:=true -p yaml_filename:="$PWD/results/keyboard_mapping/house.yaml"
   # 生命周期控制终端
   ros2 lifecycle set /map_server configure
   ros2 lifecycle set /map_server activate
   ```

保存脚本将 PGM 的空闲阈值设为 0.19，重载时保留未探索栅格。键盘短路线可用来演示建图、保存和重载。将新地图用于五区服务前，还需走遍所需区域并重新核对地图坐标、初始定位、房间边界和观察点。


C040默认开发nav2_depth线速度上限由0.26提高到0.35m/s，FollowPath/CleaningPath和平滑器一致；原nav2.yaml与显式nav2_safety.yaml保持原速度。原轮廓、转速、加速度、停车容差及清扫预算不改。相邻.35m条带实跑80.13%、636.67秒、自动回充通过；实际仍partial，西侧诊断切片239/908、最左剩余条带未完成，85%/最终4项日常避障/稳定性仍待验收。不能把直线速度峰值当成整任务同比提速。详见C040交接和清扫收据。

C041清扫默认保留原主条带顺序，之后只对实际未扫区域优先换方向补扫，分开相隔的漏扫块，无有效安全路线时回退。已达80%且原条带全部实扫时无需第二遍。新杂物间单次88.60%/26条/回充通过；该次主遍历即满足目标，不能当作新补扫提效。客厅/厨房完整清扫验收按用户要求暂缓，其他历史配置成绩见HANDOFF。


健身器械后方轮廓候选（2026-11-23，未替换默认）：

```bash
source scripts/env.sh
python3 scripts/robot_console.py --domain 67 --port 8767 --no-browser \
  --body-footprint --rooms-file src/semantic_search/config/rooms_aws_house_v12_body_transit.json
```

启动前先检查已有实例，不并开同域控制源。该候选包含全部真实碰撞体，默认圆形配置与历史地图不改；v12仅健身区连接筛选.22m/附加0格，参考可扫11156格保持，Nav2完整轮廓检查仍执行。最小修复还将两层RGB-D最低障碍高度由.08降至.02，以保留实测低椅脚；历史局部.5m短段163格实扫及停车/回充已有单次通过，最新轮廓需重验，完整80%与全部原规划条带仍按当前收据核对；客厅/厨房清扫按用户要求暂缓验收。


11月23日安全恢复：共同service/through/清扫连接BT保留既有观测，原生Wait1秒等待更新后重试，不能把盲区内曾确认的障碍直接清空；旋转/后退和停止协议保留。body候选还关闭两depth层`footprint_clearing_enabled`，原minheight.02/真实外包/.01padding不变。完整80%及日常四项仍须按当前收据验收，局部绕杠铃通过不能代替整房通过。旧树原件在修整证据中保留。


11月23日显式body候选现为：global完整外包矩形.40×.36m（padding .01）/local真实8点（padding .03、6×6m），Footprint.scale=.4（有效.02），局部图与恢复行为配套odom、全局图map。显示轨迹和覆盖仍来自map实测位姿，切换局部图坐标系不生成任何覆盖。旧map局部候选整房25.41%且回充失败保留；连续局部图当前复测结果以HANDOFF与修整收据为准，不将默认圆形或历史局部通过当成新候选通过。


当前body显式候选local `static_layer.enabled=false`：全局/map底图保持，局部仅实时激光/深度/膨胀参与近身碰撞，避免AMCL修正将历史格投到机身边缘。原地单层对照及独立返航已实跑，冷启后方.5m/153格与回充通过；新双椅与整房状态按HANDOFF更新。没有清空实测障碍、降低原过滤/停车门槛或计入返航刷盘。


C041 11月23日最新body显式候选：先执行`bash scripts/build.sh`构建新增`service_navfn`原生适配包（现在共三包）。GridBased为`service_navfn/CellCenteredNavfn`，仍安装NavFn Dijkstra，仅统一floor索引/格心坐标；global laser/depth为`service_navfn/OdomObstacleLayer`和`service_navfn/OdomVoxelLayer`，原生感知/持久记忆存odom后以当前TF投回原map主图。全局静态底图/输出尺寸/膨胀保留；local6m/odom/真实8点/.03/staticFalse仍原值，默认nav2_depth/v6不变。TF失败或超出4m额外射线缓存范围时原生costmap current=false，不能把缺图当自由。仅body cleaning checker .04，general仍.12；lane_start父动作成功另须实测距原请求≤.12，否则adjusted_goal_unreached保留action_status=4及停稳证据，不把替代目标当到达。最新局部/整房结果以HANDOFF与修整收据为准，尚无新整房通过。


C041原条带小缺口：默认主遍历后优先`required_stripe_repair`，针对原中心线实际未扫且当前可达的格构造≥.14m片段，近似段最多2次，再进入普通换向残余区域补扫。仅此原必扫缺口允许低于.04m²增益；未扫/受阻不从原验收集合移除，计划不增覆盖，预算/刷宽/速度不变。日志保存`original_lane_id`和`required_centerline_cells`。此修复的真实整房结果按HANDOFF读取。


11月23日当前body/v12 gym另有`cleaning_turning_radius_m=.321`：只调整实际执行端点，最多沿原条带内收.15m；`execution_segment`保留原参考并记录入口转向判断，短段单点须实测原段全部刷到且停车才完成。原分母/原条带/预算不变。该显式候选最新整房56.615%/8/23未通过，所有试验根已停；Native Lattice仅在results内准备，尚未授权、没有可用产品启动开关，不能将其文档视作已部署。最新事实以HANDOFF和footprint_trial/audit.json为准。
