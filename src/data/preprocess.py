import pandas as pd

# 1. read the data
df = pd.read_csv("data/raw/2026-4-02_raw/2026-04-02_merged_all_areas.csv")

# 2. select the columns we need and drop rows with missing values in those columns
df = df[[
    "area_name",
    "walk",
    "age",
    "total_floors",
    "floor",
    "layout_type",
    "area",
    "rent_man_yen",
    "management_fee_yen"
]]
df = df.dropna(subset=["area_name", "walk", "age", "total_floors", "floor", "rent_man_yen", "layout_type", "area", "management_fee_yen"])

# 3. convert numeric columns to numeric types
cols = ["walk", "age", "total_floors", "floor", "area", "rent_man_yen", "management_fee_yen"]
for col in cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=cols)

# 4. merge the rent and management fee into a single target variable "rent"
df["rent"] = df["rent_man_yen"] * 10000 + df["management_fee_yen"]
df = df.drop(columns=["rent_man_yen", "management_fee_yen"])

# 5. convert 全角 to alaphabets and only keep the layout types from 1R to 2LDK
allowed = ["1R", "1K", "1DK", "1LDK", "2K", "2DK", "2LDK"]
df["layout_type"] = df["layout_type"].str.upper()
mapping_layout = {
    "ワンルーム": "1R",
    "１Ｒ": "1R",
    "１Ｋ": "1K",
    "１ＤＫ": "1DK",
    "１ＬＤＫ": "1LDK",
    "２Ｋ": "2K",
    "２ＤＫ": "2DK",
    "２ＬＤＫ": "2LDK"
}
df["layout_type"] = df["layout_type"].replace(mapping_layout)
df = df[df["layout_type"].isin(allowed)]

#divide the type column into two columns, one for the number of rooms and one for the layout type
#df["rooms"] = df["layout_type"].str.extract(r'(\d+)')
#df["layout"] = df["layout_type"].str.extract(r'([A-Za-z]+)')[0].str.upper()

# 6. convert the location names to English
mapping_location = {
    "渋谷区": "Shibuya",
    "港区": "Minato",
    "新宿区": "Shinjuku",
    "中央区": "Chuo",
    "千代田区": "Chiyoda",
    "世田谷区": "Setagaya",
    "杉並区": "Suginami",
    "練馬区": "Nerima",
    "目黒区": "Meguro",
    "大田区": "Ota",
    "品川区": "Shinagawa",
    "豊島区": "Toshima",
    "中野区": "Nakano",
    "北区": "Kita",
    "板橋区": "Itabashi",
    "足立区": "Adachi",
    "葛飾区": "Katsushika",
    "江戸川区": "Edogawa",
    "文京区": "Bunkyo",
    "台東区": "Taito",
    "墨田区": "Sumida",
    "荒川区": "Arakawa",
    "江東区": "Koto",
    "八王子市": "Hachioji",
    "立川市": "Tachikawa",
    "武蔵野市": "Musashino",
    "三鷹市": "Mitaka",
    "青梅市": "Ome",
    "府中市": "Fuchu",
    "昭島市": "Akishima",
    "調布市": "Chofu",
    "町田市": "Machida",
    "小金井市": "Koganei",
    "小平市": "Kodaira",
    "日野市": "Hino",
    "東村山市": "Higashimurayama",
    "国分寺市": "Kokubunji",
    "国立市": "Kunitachi",
    "多摩市": "Tama",
    "稲城市": "Inagi",
    "西東京市": "Nishitokyo"
}
df["area_name"] = df["area_name"].replace(mapping_location)

# 7. Rename
df = df.rename(columns={
    "area_name": "location",
    "layout_type": "layout",
})

df = df[[
    "location",
    "walk",
    "age",
    "total_floors",
    "floor",
    "layout",
    "area",
    "rent"
]]

# 8. save data
df.to_csv("data/processed/2026-04-02_data/clean_data.csv", index=False)
print(df.head())