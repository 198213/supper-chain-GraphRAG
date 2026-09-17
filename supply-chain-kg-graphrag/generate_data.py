import json
import random
import os

random.seed(42)

N_SUPPLIERS = 20
N_MATERIALS = 50
N_PRODUCTS = 30
N_FACTORIES = 10
N_ORDERS = 100
N_CONSUMERS = 50
N_SHIPMENTS = 120

def gen_suppliers():
    regions = ["华东", "华南", "华北", "西南"]
    return [
        {"supplier_id": f"S{i:03d}", "name": f"供应商{i}",
         "region": random.choice(regions),
         "lead_time_days": random.randint(3, 30),
         "risk_score": round(random.uniform(0.1, 0.9), 2)}
        for i in range(1, N_SUPPLIERS + 1)
    ]

def gen_materials():
    categories = ["原料", "包材", "辅料", "添加剂"]
    return [
        {"material_id": f"M{i:03d}", "name": f"物料{i}",
         "category": random.choice(categories)}
        for i in range(1, N_MATERIALS + 1)
    ]

def gen_products():
    categories = ["洗护", "护肤", "家清", "口腔"]
    return [
        {"product_id": f"P{i:03d}", "sku": f"SKU{i:04d}",
         "name": f"产品{i}", "category": random.choice(categories)}
        for i in range(1, N_PRODUCTS + 1)
    ]

def gen_factories():
    cities = ["广州", "上海", "成都", "天津"]
    return [
        {"factory_id": f"F{i:02d}", "name": f"工厂{i}",
         "location": random.choice(cities),
         "capacity": random.randint(1000, 10000)}
        for i in range(1, N_FACTORIES + 1)
    ]

def gen_orders():
    return [
        {"order_id": f"O{i:04d}",
         "order_date": f"2025-{random.randint(1,9):02d}-{random.randint(1,28):02d}",
         "status": random.choice(["已下单", "已发货", "已完成"]),
         "quantity": random.randint(1, 500)}
        for i in range(1, N_ORDERS + 1)
    ]

def gen_consumers():
    cities = ["北京", "上海", "广州", "深圳", "杭州", "成都"]
    return [
        {"consumer_id": f"C{i:03d}", "name": f"消费者{i}",
         "city": random.choice(cities)}
        for i in range(1, N_CONSUMERS + 1)
    ]

def gen_shipments():
    return [
        {"shipment_id": f"SH{i:04d}",
         "ship_date": f"2025-{random.randint(1,9):02d}-{random.randint(1,28):02d}",
         "status": random.choice(["运输中", "已签收", "异常"])}
        for i in range(1, N_SHIPMENTS + 1)
    ]

def gen_relations(suppliers, materials, products, factories, orders, consumers, shipments):
    rels = []
    for m in materials:
        rels.append(["Supplier", random.choice(suppliers)["supplier_id"],
                     "SUPPLIES", "Material", m["material_id"]])
    for p in products:
        for _ in range(random.randint(1, 3)):
            rels.append(["Material", random.choice(materials)["material_id"],
                         "USED_IN", "Product", p["product_id"]])
    for p in products:
        rels.append(["Product", p["product_id"],
                     "PRODUCED_AT", "Factory", random.choice(factories)["factory_id"]])
    for o in orders:
        for _ in range(random.randint(1, 3)):
            rels.append(["Order", o["order_id"],
                         "CONTAINS", "Product", random.choice(products)["product_id"]])
        rels.append(["Order", o["order_id"],
                     "PLACED_BY", "Consumer", random.choice(consumers)["consumer_id"]])
    for s in shipments:
        rels.append(["Shipment", s["shipment_id"],
                     "FROM", "Factory", random.choice(factories)["factory_id"]])
        rels.append(["Shipment", s["shipment_id"],
                     "TO", "Consumer", random.choice(consumers)["consumer_id"]])
    return rels

def main():
    os.makedirs("data/sample", exist_ok=True)
    suppliers = gen_suppliers()
    materials = gen_materials()
    products = gen_products()
    factories = gen_factories()
    orders = gen_orders()
    consumers = gen_consumers()
    shipments = gen_shipments()
    rels = gen_relations(suppliers, materials, products, factories, orders, consumers, shipments)

    data = {
        "suppliers": suppliers, "materials": materials, "products": products,
        "factories": factories, "orders": orders, "consumers": consumers,
        "shipments": shipments, "relations": rels
    }
    with open("data/sample/supply_chain.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"生成完成: {len(rels)} 条关系")

if __name__ == "__main__":
    main()