# 日化供应链知识图谱与 GraphRAG 

构建覆盖供应商、物料、工厂、SKU、订单、消费者、物流等 7 类节点、7 类关系的日化供应链知识图谱，基于 Neo4j 存储，实现 GraphRAG 智能问答与影响传播分析。

## 项目亮点

- 供应链知识图谱：7 类节点、7 类关系，Neo4j 存储，Cypher 多跳查询
- GraphRAG 智能问答：LLM 意图识别 → LLM 实体抽取 → Cypher 模板路由 → LLM 受控生成
- 影响传播分析：供应商延迟影响哪些订单/SKU、工厂停产影响哪些消费者、SKU 依赖追溯、订单全链路追踪
- 评估：20 条人工标注 QA，命中率 90%，平均召回 90%，空答案率 0%，平均响应 3.34s

## 架构

```mermaid
flowchart LR
  U[用户] --> S[graphrag.py]
  S --> I[LLM 意图识别]
  I --> E[LLM 实体抽取]
  E --> C[Cypher 模板路由]
  C --> N[(Neo4j 供应链知识图谱)]
  N --> R[图谱结果 JSON]
  R --> G[LLM 受控生成]
  G --> U
