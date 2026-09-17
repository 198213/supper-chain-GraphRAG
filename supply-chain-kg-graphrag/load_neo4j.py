import json
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "llx875153394"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

NODE_MAP = {
    "suppliers": ("Supplier", "supplier_id"),
    "materials": ("Material", "material_id"),
    "products": ("Product", "product_id"),
    "factories": ("Factory", "factory_id"),
    "orders": ("Order", "order_id"),
    "consumers": ("Consumer", "consumer_id"),
    "shipments": ("Shipment", "shipment_id"),
}

ID_FIELD = {v[0]: v[1] for v in NODE_MAP.values()}

def load_all(tx, data):
    for key, (label, id_field) in NODE_MAP.items():
        for item in data[key]:
            props = {k: v for k, v in item.items()}
            query = f"MERGE (n:{label} {{{id_field}: $id}}) SET n += $props"
            tx.run(query, id=item[id_field], props=props)

    for rel in data["relations"]:
        src_label, src_id, rel_type, tgt_label, tgt_id = rel
        query = f"""
        MATCH (a:{src_label} {{{ID_FIELD[src_label]}: $src_id}})
        MATCH (b:{tgt_label} {{{ID_FIELD[tgt_label]}: $tgt_id}})
        MERGE (a)-[:{rel_type}]->(b)
        """
        tx.run(query, src_id=src_id, tgt_id=tgt_id)

def main():
    with open("data/sample/supply_chain.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    with driver.session() as session:
        session.execute_write(load_all, data)
    print("导入完成")
    driver.close()

if __name__ == "__main__":
    main()