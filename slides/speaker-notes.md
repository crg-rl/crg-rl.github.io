# 讲稿：Beyond Forgetting

## 01 · Beyond Forgetting
核心问题是持续扩展推理能力。不是只看旧任务有没有掉分，而是看逐个学习任务后，整体能不能接近同时学所有任务的模型。

来源与口径：公开论文完整标题、作者与单位；约 25 秒。

## 02 · Roadmap
先讲任务为什么会连续到来，再介绍 CRG 的环境和比较方式。随后诊断“少遗忘但落后”的矛盾，提出 CPR。实验用三个问题回答效果、增益来源和关键设计。

来源与口径：讲述路线；约 20 秒。

## 03 · New capabilities arrive after deployment
从部署后不断出现的新任务切入：新 API 或新需求会扩展任务集合。每次都重新在全部任务上做多任务 RLVR 成本很高。我们关注继续更新现有模型的方式。这里不讲 CPR，也不宣称当前实验是在线部署实验。

来源与口径：Introduction 的部署动机；约 50 秒。

## 04 · Can task-by-task RLVR match joint training?
要解决的目标有三个面：学会正在到来的任务、保留此前的能力，以及让学到的结构对未来任务有帮助。最终比较全任务平均表现，而不只比较旧任务遗忘。MTRL 作为同一任务集合的联合训练参照。

来源与口径：研究问题；背景不提前展开方法；约 45 秒。

## 05 · An environment, a diagnosis, and a method
贡献分三层：CRG 是可执行、可复用的环境；共享推理给出为什么不能只看遗忘的解释；CPR 把已有任务提示带回当前策略的训练。这里只给预览，细节随后展开。

来源与口径：Introduction 三项贡献；约 40 秒。

## 06 · CRG makes continual RLVR an executable environment
直接用论文原图讲环境。上方是算法推理的任务序列，中间是 prompt、生成、验证、更新的循环；每个阶段完成后对所有任务评测。CRG 不只是结果榜单，而是训练和诊断可共用的持续 RLVR 环境。

来源与口径：当前 CRG 原始环境图；只保留 PKU 标识，不移植 CAMP 的机构；约 65 秒。

## 07 · Five task sequences across text and visual reasoning
五条序列分属两个模态：文本算法、代数，视觉空间、位置和数量推理。原图给出每类具体任务，听众不需要记住所有任务名。训练模型分别是 Qwen3-4B 和 Qwen2.5-VL-7B。

来源与口径：当前作者论文 task-example 原图；旧版主结果与当前表格一致；约 45 秒。

## 08 · Evaluate every task after every stage
矩阵每行对应一个训练边界，每列对应任务；每个 score 都来自实际任务评测，图中只显示结构而不填造数。最后一行平均值是 FinalAvg。为了跨不同难度的任务序列比较，使用 FinalAvg 除以同任务集合的 MTRL FinalAvg，得到 CTM；1 表示到达联合训练水平。

来源与口径：Evaluation quantities；CTM 用各序列 ratio 再等权平均，不是 aggregate 分数比；约 60 秒。

## 09 · Modest forgetting still leaves a multitask gap
关键现象是：平均旧任务只掉 2.47 个百分点，但整体 CTM 只有 0.88。原图每个点是一条任务序列，横轴 BWT，纵轴 CTM。尤其算法任务有正向 BWT，仍明显低于 MTRL。这促使我们把剩余差距拆开，而不是只降低遗忘。

来源与口径：公开论文 Figure 3；当前同内容原图，数值不变；约 60 秒。

## 10 · Final performance depends on more than retention
这个恒等式将最终分数分成初始能力，加上学本任务之前、直接训练本任务、以及后续训练三个阶段的变化。FWT 与 BWT 按论文定义排除首尾没有对应阶段的任务，因此有 (T-1)/T 的系数。只改善 BWT，可能同时损失 FWT 和 TLG；少遗忘并不自动等于高最终分数。

来源与口径：Proposition 1；正式 FWT/TLG/BWT 定义，非单个任务案例的近似量；约 65 秒。

## 11 · CPR replays prompts and regenerates responses
CPR 的核心不是重放旧答案：存的是之前任务的题目，重放时让当前策略重新解答，再由该任务验证器给奖励。选择中间通过率的旧题，替换当前 batch 的一部分，保持每次更新的 prompt 和 rollout 预算。右上对照旧轨迹重放，下面是完整一次更新。目标是让先前任务提供对全任务集合更有用的训练方向。

来源与口径：当前原始 CPR 图；对应论文方法和 Algorithm 1；约 75 秒。

## 12 · Only CPR reaches MTRL-level performance on average
看五序列 CTM 的等权平均，所有比较方法都展示。CPR 为 1.03，Seq.RLVR 为 0.88；在所比较的持续学习方法里只有 CPR 达到 MTRL 水平。注意这不是每条序列都更高：四条高于 Seq.RLVR，位置推理低 1.5 个百分点。Muon 是不同优化器的控制项，MTRL 仍是固定参照，不称 optimizer-matched。

来源与口径：公开论文 Table 2；CTM=序列内比值再平均；数字按论文显示精度；约 75 秒。

## 13 · The gain comes from learning, not less forgetting
同一初始策略下，CPR 的最终平均分高 6.4 点。加权后的 FWT 贡献 +2.4，TLG +4.9，BWT -0.9，三者恰好相加为6.4。因此收益不是“旧任务忘得更少”，而是更好地学当前任务与迁移到未来任务。这些已经是对 FinalAvg 的贡献，不再乘一次系数。

来源与口径：公开论文 Table 2；对 Seq.RLVR 的加权百分点差，表中四舍五入；约 65 秒。

## 14 · Shared reasoning offers a useful update direction
两幅图回答相关但不同的问题。左图在 Seq.RLVR 下测算法任务两两梯度，平均 cosine 0.345，82.2% 为正，支持共享结构。右图在冻结 Qwen3-4B base 上，对 stage2到10 比较当前任务梯度和当前/以前任务梯度各占一半的组合；对全任务平均方向的 alignment 从0.43到0.79，九个阶段都更高。这是局部梯度诊断，不把 cosine 当作长期性能保证。

来源与口径：公开梯度热图 + 当前作者九阶段梯度诊断；右图固定base，左图Seq.RLVR；约 65 秒。

## 15 · Other tasks help jugs before and after its own stage
完整论文案例图，保留性能曲线和真实推理摘录。Jugs 在自己的训练阶段之前从0到24%，直接训练后39%，后续其他任务训练后44%。同一问题的推理从反复检查、不输出答案，到正确答案，再到更直接的推理。这里研究的是 Seq.RLVR 内的共享推理现象，不是 CPR 与基线配对个例。图中的早期/直接/后期增益是单任务区间变化，不称全序列平均 FWT/TLG/BWT。

来源与口径：当前原始 jugs 图，完整保留；推理长度按图中有效 think 内容；约 65 秒。

## 16 · Fresh responses turn replay into a learning benefit
不是“加 replay 就行”。在算法序列同预算对照中，旧轨迹重放47.5，甚至低于不重放49.9；保持题目但用当前策略重新生成，达到63.3，接近MTRL65.3。CPR相对不重放高13.5点（按未四舍五入值计算）。结论是题目可以复用，但训练答案应跟上当前策略。

来源与口径：公开论文 regeneration 消融；不把算法序列数字写成跨序列平均；约 60 秒。

## 17 · Takeaways
收尾留三个 insight。第一，不遗忘只是持续学习的一部分；第二，旧任务不是只能被保护，也可以成为学习新任务的资源；第三，RLVR 重放应复用问题、刷新答案。到这里停住，可直接进入问答，不追加 references 或 thank-you。

来源与口径：综合分解、梯度/行为观察与生成消融；不把操作步骤当 insight；约 35 秒。
