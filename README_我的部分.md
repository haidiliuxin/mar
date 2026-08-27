# Markov 概率模型和绘图部分

我负责的部分分成三个步骤：训练 Markov 模型、计算论文中的概率评价指标、根据结果文件画图。

## 文件

`markov_model.py` 是主要模型代码，完成固定阶上下文计数、add-0.01 平滑、end-symbol 归一化、长度分布归一化以及口令概率计算。

`probability_metrics.py` 对测试集计算 probability-threshold 曲线、ANLL、ANLL_0.8 和指定概率阈值下的覆盖率。

`plot_results.py` 读取 CSV 和 JSON 结果，用 Matplotlib 生成 probability-threshold 曲线与 ANLL 对比图。

`run_probability_experiment.py` 把前面三个步骤连接起来。默认训练 3、4、5 阶模型，并分别使用 end-symbol 和 distribution 两种归一化。

`candidate_generator.py` 是小规模候选生成原型，用来说明概率模型如何转成候选搜索。千万级候选的分块排序和攻击测试由后续实验部分处理。

## 运行方法

先安装绘图库：

```powershell
py -3 -m pip install -r requirements.txt
```

运行 RockYou 训练、PhpBB 测试的六组概率评价：

```powershell
py -3 run_probability_experiment.py `
  --train data/rockyou-withcount.txt.bz2 `
  --test data/phpbb-withcount.txt.bz2 `
  --orders 3 4 5 `
  --normalizations end distribution `
  --delta 0.01 `
  --output probability_results
```

输出目录包含：

```text
probability_metrics.json
probability_threshold_curves.csv
probability_threshold_curves.svg
anll_comparison.svg
```

如果要复现论文中的其他训练与测试场景，只需要更换 `--train` 和 `--test` 文件。输入文件仍采用 SkullSecurity 的 `频数 口令` 格式，并执行长度 4 到 40、95 个可打印 ASCII 字符的清洗。

程序可以直接读取 `.bz2` 压缩文件，不需要先解压成体积较大的明文文件。

代码能够复现论文的模型计算和评价流程。要逐项得到论文原表中的数值，还必须使用论文相同版本的 RockYou、Yahoo、PhpBB、CSDN、Duduniu 和 178 数据，并按论文的场景划分训练集与测试集。
