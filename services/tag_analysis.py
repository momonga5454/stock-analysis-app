from db import get_conn
from itertools import combinations

def analyze_tags(user_id: int):

    db = get_conn()
    cursor = db.cursor()

    cursor.execute("""
    SELECT tags.name,
           AVG(trades.profit) as avg_profit,
           COUNT(*) as count,
           SUM(CASE WHEN trades.profit > 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as win_rate
    FROM trades
    JOIN taggings ON trades.id = taggings.trade_id
    JOIN tags ON tags.id = taggings.tag_id
    WHERE trades.user_id = ?
    GROUP BY tags.name
    """, (user_id,))

    result = cursor.fetchall()

    db.close()

    return result

def analyze_tag_combinations(user_id: int):

    db = get_conn()
    cursor = db.cursor()

    # ✅ 全トレードとタグ取得
    cursor.execute("""
    SELECT trades.id, trades.profit, tags.name
    FROM trades
    JOIN taggings ON trades.id = taggings.trade_id
    JOIN tags ON tags.id = taggings.tag_id
    WHERE trades.user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()

    db.close()

    # ✅ tradeごとにタグまとめる
    trade_dict = {}
    for trade_id, profit, tag_name in rows:
        if trade_id not in trade_dict:
            trade_dict[trade_id] = {
                "profit": profit,
                "tags": []
            }
        trade_dict[trade_id]["tags"].append(tag_name)

    # ✅ 組み合わせ分析
    combo_result = {}

    for trade in trade_dict.values():
        tags = trade["tags"]
        profit = trade["profit"]

        for r in range(2, len(tags)+1):  # 2個以上の組み合わせ
            for combo in combinations(tags, r):
                key = " × ".join(sorted(combo))

                if key not in combo_result:
                    combo_result[key] = {
                        "profits": []
                    }

                combo_result[key]["profits"].append(profit)

    # ✅ 集計
    results = []

    for name, data in combo_result.items():
        profits = data["profits"]

        avg = sum(profits) / len(profits)
        win = len([p for p in profits if p > 0])
        win_rate = win / len(profits)

        results.append({
            "name": name,
            "avg_profit": avg,
            "count": len(profits),
            "win_rate": win_rate
        })

    return results

