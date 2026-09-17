import pandas as pd
import numpy as np
from prophet import Prophet
import math

def forecast_sku(product_id, weeks=8):
    dates = pd.date_range("2024-01-01", periods=52, freq="W")
    values = [100 + i * 2 + (i % 4) * 10 + np.random.randint(-10, 10) for i in range(52)]
    df = pd.DataFrame({"ds": dates, "y": values})

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=weeks, freq="W")
    forecast = model.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(weeks)

def safety_stock(demand_std, lead_time_days, z=1.65):
    return z * demand_std * math.sqrt(lead_time_days)

def reorder_point(avg_daily_demand, lead_time_days, ss):
    return avg_daily_demand * lead_time_days + ss

if __name__ == "__main__":
    result = forecast_sku("P001")
    print(result)
    ss = safety_stock(demand_std=15, lead_time_days=7)
    rop = reorder_point(avg_daily_demand=20, lead_time_days=7, ss=ss)
    print(f"安全库存: {ss:.1f}, 再订货点: {rop:.1f}")