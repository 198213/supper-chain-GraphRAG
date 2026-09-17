import json
from neo4j import GraphDatabase
from openai import OpenAI

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = ""

OPENAI_API_KEY = "sk-*"
OPENAI_BASE_URL = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


CYPHER_TEMPLATES = {
    "supplier_delay_impact": {
        "cypher": """
            MATCH (s:Supplier {name:$name})-[:SUPPLIES]->(m:Material)
                  -[:USED_IN]->(p:Product)<-[:CONTAINS]-(o:Order)
            RETURN DISTINCT o.order_id AS order_id, p.sku AS sku, m.name AS material
            LIMIT 30
        """,
        "param": "name",
        "desc": "供应商延迟影响哪些订单和SKU"
    },
    "factory_shutdown_impact": {
        "cypher": """
            MATCH (f:Factory {name:$name})<-[:PRODUCED_AT]-(p:Product)
                  <-[:CONTAINS]-(o:Order)-[:PLACED_BY]->(c:Consumer)
            RETURN DISTINCT c.name AS consumer, o.order_id AS order_id, p.sku AS sku
            LIMIT 30
        """,
        "param": "name",
        "desc": "工厂停产影响哪些消费者订单"
    },
    "sku_dependency": {
        "cypher": """
            MATCH (p:Product {sku:$name})<-[:USED_IN]-(m:Material)
                  <-[:SUPPLIES]-(s:Supplier)
            RETURN DISTINCT s.name AS supplier, m.name AS material
            LIMIT 30
        """,
        "param": "name",
        "desc": "某SKU依赖哪些供应商和物料"
    },
    "order_trace": {
        "cypher": """
            MATCH (o:Order {order_id:$name})-[:CONTAINS]->(p:Product)
                  -[:PRODUCED_AT]->(f:Factory)
            MATCH (o)-[:PLACED_BY]->(c:Consumer)
            RETURN DISTINCT p.sku AS sku, f.name AS factory, c.name AS consumer
            LIMIT 30
        """,
        "param": "name",
        "desc": "某订单涉及哪些工厂和消费者"
    },
}


def classify_intent(question):
    prompt = f"""你是一个供应链问题意图分类器。从以下类别中选择最合适的一个：
- supplier_delay_impact: 询问某供应商延迟会影响哪些订单/SKU
- factory_shutdown_impact: 询问某工厂停产会影响哪些消费者订单
- sku_dependency: 询问某SKU依赖哪些供应商和物料
- order_trace: 询问某订单涉及哪些工厂和消费者

只输出类别名称，不要标点，不要解释。

问题：{question}
类别："""
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return resp.choices[0].message.content.strip()


def extract_entity(question, intent):
    prompt = f"""从下面的问题中提取关键实体名，只输出实体名本身，不要解释。
- 如果意图是 supplier_delay_impact，提取供应商名称（如"供应商3"）
- 如果意图是 factory_shutdown_impact，提取工厂名称（如"工厂2"）
- 如果意图是 sku_dependency，提取SKU编号（如"SKU0005"）
- 如果意图是 order_trace，提取订单编号（如"O0012"）

问题：{question}
实体名："""
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return resp.choices[0].message.content.strip().strip("。，,.!?？")


def query_graph(intent, entity):
    template = CYPHER_TEMPLATES.get(intent)
    if not template:
        return []
    with driver.session() as session:
        result = session.run(template["cypher"], **{template["param"]: entity})
        return [record.data() for record in result]


def generate_answer(question, rows):
    context = json.dumps(rows, ensure_ascii=False, indent=2)
    prompt = f"""你是一个供应链分析助手。请严格根据下面的【图谱查询结果】回答问题。

规则：
1. 只能使用图谱结果中出现的实体，不要编造。
2. 如果图谱结果为空，回答："根据当前知识图谱，未找到相关信息。"
3. 用简洁自然的中文回答。

问题：{question}
图谱查询结果：{context}
答案："""
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return resp.choices[0].message.content.strip()


def graphrag(question):
    intent = classify_intent(question)
    entity = extract_entity(question, intent)
    print(f"[意图] {intent} | [实体] {entity}")
    rows = query_graph(intent, entity)
    if not rows:
        return "根据当前知识图谱，未找到相关信息。"
    return generate_answer(question, rows)


if __name__ == "__main__":
    questions = [
        "供应商3延迟会影响哪些订单和SKU？",
        "工厂2停产会影响哪些消费者订单？",
        "SKU0005依赖哪些供应商和物料？",
        "订单O0012涉及哪些工厂和消费者？",
    ]
    for q in questions:
        print("=" * 50)
        print(f"问：{q}")
        print(f"答：{graphrag(q)}")
        print()
