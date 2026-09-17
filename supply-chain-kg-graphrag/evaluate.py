import csv
import time
from graphrag import graphrag

def evaluate(qa_path):
    total = 0
    hit = 0
    total_recall = 0
    empty = 0
    times = []

    with open(qa_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            total += 1
            q = row["question"]
            golds = row["gold_entities"].split("|")

            print(f"[{total}] {q}")

            t0 = time.time()
            try:
                ans = graphrag(q)
            except Exception as e:
                ans = f"[ERROR] {e}"
            times.append(time.time() - t0)

            if "未找到" in ans:
                empty += 1

            h = sum(1 for g in golds if g in ans)
            if h > 0:
                hit += 1
            total_recall += h / len(golds) if golds else 0

            print(f"    answer: {ans[:100]}")
            print(f"    hit {h}/{len(golds)}")
            print()

    print("=" * 50)
    print(f"QA 数量:        {total}")
    print(f"命中率:         {hit/total:.2%}")
    print(f"平均召回:       {total_recall/total:.2%}")
    print(f"空答案率:       {empty/total:.2%}")
    print(f"平均响应时间:   {sum(times)/len(times):.2f}s")

if __name__ == "__main__":
    evaluate("eval_qa_set.csv")