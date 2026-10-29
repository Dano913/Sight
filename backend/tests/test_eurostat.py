from app.clients.eurostat_client import EurostatClient

df = EurostatClient.get_trade()

print("SHAPE:", df.shape)
print(df.columns.tolist())
print(df[[
    "geo\\TIME_PERIOD",
    "freq",
    "stk_flow",
    "indic_et",
    "partner",
    "sitc06"
]].head())

print(df["geo\\TIME_PERIOD"].unique())
print(df["stk_flow"].unique())
print(df["partner"].unique())
print(df["sitc06"].unique())