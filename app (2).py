import streamlit as st
import pandas as pd
from datetime import date, datetime
from pathlib import Path
import random

# ---------------------------------------------------------
# SHOPIMPACT - Conscious Shopping Dashboard
# Student project built with Python + Streamlit
# ---------------------------------------------------------

st.set_page_config(
    page_title="ShopImpact | Conscious Shopping",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Earthy, welcoming design
st.markdown("""
<style>
.stApp { background: #f5f7f1; }
[data-testid="stSidebar"] { background: #e5eee2; }
.hero {
    background: linear-gradient(120deg, #244f3d, #6b9b69);
    padding: 28px 32px; border-radius: 20px; color: white;
    margin-bottom: 18px;
}
.hero h1 { color: white; font-size: 2.5rem; margin: 0; }
.hero p { color: #eff8ec; font-size: 1.05rem; margin-bottom: 0; }
div[data-testid="stMetric"] {
    background: white; border: 1px solid #e2e9dc;
    padding: 14px; border-radius: 14px;
}
.tip {
    background: #e7f1df; border-left: 5px solid #5e8d54;
    border-radius: 10px; padding: 14px 18px; color: #294b35;
}
.badge-card {
    background: white; border: 1px solid #dce8d8;
    border-radius: 14px; padding: 16px; min-height: 125px;
}
.muted { color: #667565; font-size: 0.88rem; }
</style>
""", unsafe_allow_html=True)

# Estimated classroom multipliers in kg CO2e per Rs. 100 spent.
# These are illustrative values, not verified product life-cycle data.
CO2_MULTIPLIERS = {
    "Clothing": 1.8,
    "Leather goods": 2.6,
    "Electronics": 2.4,
    "Footwear": 1.7,
    "Groceries": 0.5,
    "Books & stationery": 0.7,
    "Home products": 1.3,
    "Personal care": 1.1,
    "Second-hand items": 0.3,
    "Other": 1.0
}

GREEN_ALTERNATIVES = {
    "Clothing": [
        "Choose durable clothes that can be worn for a long time.",
        "Consider second-hand or clothes made with recycled fibres.",
        "Repair or reuse clothing before replacing it."
    ],
    "Leather goods": [
        "Consider durable products made from recycled or lower-impact materials.",
        "Choose pre-owned items when suitable."
    ],
    "Electronics": [
        "Repair or upgrade a device before buying a new one.",
        "Look for energy-efficient products and longer warranties.",
        "Recycle old electronics through an authorised collection point."
    ],
    "Footwear": [
        "Choose durable footwear and repair it when possible.",
        "Consider pre-owned or responsibly made options."
    ],
    "Groceries": [
        "Choose local and seasonal products where practical.",
        "Carry reusable bags and avoid unnecessary packaging.",
        "Plan meals to reduce food waste."
    ],
    "Books & stationery": [
        "Borrow, exchange or buy second-hand books.",
        "Choose recycled paper and refillable stationery."
    ],
    "Home products": [
        "Choose durable products instead of disposable ones.",
        "Consider repaired, reused or second-hand furniture."
    ],
    "Personal care": [
        "Look for refill packs or products with less packaging.",
        "Choose products that suit your needs and can be used fully."
    ],
    "Second-hand items": [
        "Buying pre-owned can extend a product's useful life.",
        "Look after the item so it can be reused for longer."
    ],
    "Other": [
        "Pause and consider whether the purchase is necessary.",
        "Choose durable products with less packaging."
    ]
}

ECO_TIPS = [
    "Carry a reusable shopping bag on your next shopping trip.",
    "Before buying something new, ask whether you can repair or reuse what you already own.",
    "Choose durable products that will last longer.",
    "Compare packaging and look for refillable or recyclable options.",
    "Buying second-hand can give a useful item a longer life.",
    "Plan your purchases to avoid impulse buying and unnecessary waste."
]

# -------------------- SESSION DATA --------------------
if "purchases" not in st.session_state:
    st.session_state.purchases = []

if "tip_number" not in st.session_state:
    st.session_state.tip_number = 0

# -------------------- HELPER FUNCTIONS --------------------
def estimate_co2(price, product_type):
    """Return illustrative CO2e estimate based on price and category."""
    multiplier = CO2_MULTIPLIERS.get(product_type, 1.0)
    return (float(price) / 100.0) * multiplier

def month_key(purchase_date):
    return purchase_date.strftime("%Y-%m")

def get_month_purchases(purchases, chosen_month):
    return [
        item for item in purchases
        if item["date"][:7] == chosen_month
    ]

def calculate_badges(month_items):
    """Award simple motivational badges from recorded monthly purchases."""
    badges = []
    if not month_items:
        return badges

    month_total = sum(item["co2"] for item in month_items)
    categories = {item["product_type"] for item in month_items}

    if month_total <= 5:
        badges.append(("🌱", "Eco Saver of the Month",
                       "Your recorded monthly estimate is 5 kg CO2e or less."))
    if "Second-hand items" in categories:
        badges.append(("♻️", "Reuse Champion",
                       "You recorded at least one second-hand purchase."))
    if "Groceries" in categories or "Books & stationery" in categories:
        badges.append(("🍃", "Mindful Choice",
                       "You recorded a purchase in a lower-multiplier category."))
    if len(month_items) >= 5:
        badges.append(("🏅", "Conscious Shopper",
                       "You have tracked five or more purchases this month."))
    return badges

def make_purchase(product, product_type, brand, price, purchase_date):
    impact = estimate_co2(price, product_type)
    return {
        "product": product.strip(),
        "product_type": product_type,
        "brand": brand.strip() if brand.strip() else "Not specified",
        "price": float(price),
        "date": purchase_date.isoformat(),
        "co2": impact
    }

def show_turtle_art():
    """
    Display a Turtle-style leaf illustration in the Streamlit app.
    The separate turtle_art.py file uses Python's turtle module to draw
    a real Turtle graphic in a local desktop window.
    """
    st.markdown("""
    <div style="background:#e7f1df;border-radius:18px;padding:18px;text-align:center;">
      <div style="font-size:62px;">🐢 🌿</div>
      <div style="font-size:19px;font-weight:700;color:#315b3d;">Small choices grow into a greener future!</div>
      <div style="color:#58745c;">Keep tracking your choices and celebrate mindful shopping.</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.title("🌿 ShopImpact")
st.sidebar.caption("Conscious shopping companion")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Log a Purchase", "Impact Dashboard",
     "Greener Alternatives", "My Purchase History"]
)
st.sidebar.divider()
st.sidebar.markdown("**Shop mindfully. Waste less.**")
st.sidebar.caption("Student project • Python + Streamlit")

# -------------------- CALCULATE OVERALL DATA --------------------
all_purchases = st.session_state.purchases
today_month = date.today().strftime("%Y-%m")
available_months = sorted({p["date"][:7] for p in all_purchases})
if today_month not in available_months:
    available_months.append(today_month)
available_months = sorted(set(available_months), reverse=True)

# -------------------- HOME --------------------
if page == "Home":
    st.markdown("""
    <div class="hero">
      <h1>🌿 Welcome to ShopImpact</h1>
      <p>Make every purchase count. Understand your shopping impact,
      discover greener alternatives and celebrate better choices.</p>
    </div>
    """, unsafe_allow_html=True)

    month_items = get_month_purchases(all_purchases, today_month)
    monthly_spend = sum(p["price"] for p in month_items)
    monthly_co2 = sum(p["co2"] for p in month_items)

    c1, c2, c3 = st.columns(3)
    c1.metric("Purchases this month", len(month_items))
    c2.metric("Monthly spending", f"₹{monthly_spend:,.2f}")
    c3.metric("Estimated monthly CO₂e", f"{monthly_co2:.2f} kg")

    st.subheader("Your mindful shopping journey")
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown("""
        **What you can do with ShopImpact**
        - Record planned or completed purchases.
        - Estimate the CO₂ impact using category multipliers.
        - View monthly spending and impact dashboards.
        - Find greener alternatives for product categories.
        - Earn badges for mindful shopping habits.
        """)
        st.info("Start by selecting **Log a Purchase** from the sidebar.")
    with right:
        show_turtle_art()

    st.subheader("🌱 A little eco inspiration")
    st.markdown(
        f"<div class='tip'>💡 {ECO_TIPS[date.today().day % len(ECO_TIPS)]}</div>",
        unsafe_allow_html=True
    )

# -------------------- LOG PURCHASE --------------------
elif page == "Log a Purchase":
    st.markdown("""
    <div class="hero">
      <h1>🛒 Log a Purchase</h1>
      <p>Enter the product details to estimate its environmental impact.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("purchase_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            product = st.text_input("Product name", placeholder="e.g. Cotton T-shirt")
            product_type = st.selectbox("Product type", list(CO2_MULTIPLIERS.keys()))
            brand = st.text_input("Brand", placeholder="e.g. Example brand")
        with col2:
            price = st.number_input("Price (₹)", min_value=0.0,
                                    max_value=10000000.0, value=500.0, step=50.0)
            purchase_date = st.date_input("Purchase date", value=date.today())
            purchase_kind = st.radio("Purchase status", ["Planned", "Purchased"],
                                     horizontal=True)

        submitted = st.form_submit_button("🌿 Calculate and save", use_container_width=True)

    if submitted:
        if not product.strip():
            st.error("Please enter a product name.")
        elif price <= 0:
            st.error("Please enter a price greater than zero.")
        else:
            item = make_purchase(product, product_type, brand, price, purchase_date)
            item["status"] = purchase_kind
            st.session_state.purchases.append(item)
            st.success("Purchase saved successfully!")
            st.metric("Estimated CO₂e impact", f"{item['co2']:.2f} kg")
            st.caption(
                f"Calculation: ₹{price:,.2f} ÷ 100 × "
                f"{CO2_MULTIPLIERS[product_type]} = {item['co2']:.2f} kg CO₂e"
            )
            st.subheader("A greener alternative to consider")
            for suggestion in GREEN_ALTERNATIVES[product_type]:
                st.write("🍃 " + suggestion)

    st.caption("You can record both planned and completed purchases.")

# -------------------- MONTHLY DASHBOARD --------------------
elif page == "Impact Dashboard":
    st.markdown("""
    <div class="hero">
      <h1>📊 Monthly Impact Dashboard</h1>
      <p>See your spending and estimated footprint over time.</p>
    </div>
    """, unsafe_allow_html=True)

    selected_month = st.selectbox("Choose month", available_months,
                                  index=available_months.index(today_month))
    month_items = get_month_purchases(all_purchases, selected_month)

    if month_items:
        df = pd.DataFrame(month_items)
        total_spend = df["price"].sum()
        total_impact = df["co2"].sum()
        count = len(df)

        a, b, c = st.columns(3)
        a.metric("Purchases logged", count)
        b.metric("Total spending", f"₹{total_spend:,.2f}")
        c.metric("Estimated CO₂e", f"{total_impact:.2f} kg")

        st.subheader("Estimated impact by product type")
        by_type = df.groupby("product_type")["co2"].sum().sort_values(ascending=False)
        st.bar_chart(by_type)

        st.subheader("Spending by product type")
        spend_by_type = df.groupby("product_type")["price"].sum()
        st.bar_chart(spend_by_type)

        st.subheader("🏆 Your monthly badges")
        badges = calculate_badges(month_items)
        if badges:
            cols = st.columns(min(4, len(badges)))
            for index, (emoji, name, description) in enumerate(badges):
                with cols[index]:
                    st.markdown(
                        f"<div class='badge-card'><div style='font-size:34px'>{emoji}</div>"
                        f"<b>{name}</b><p class='muted'>{description}</p></div>",
                        unsafe_allow_html=True
                    )
            show_turtle_art()
        else:
            st.info("Keep logging purchases to unlock your first badge.")
    else:
        st.info("No purchases found for this month. Add a purchase to see your dashboard.")

    st.caption("Monthly totals are based on the purchase date entered in the form.")

# -------------------- GREENER ALTERNATIVES --------------------
elif page == "Greener Alternatives":
    st.markdown("""
    <div class="hero">
      <h1>🍃 Greener Alternatives</h1>
      <p>Explore simple ideas that may help reduce the impact of everyday shopping.</p>
    </div>
    """, unsafe_allow_html=True)

    chosen_type = st.selectbox("Choose a product category",
                               list(GREEN_ALTERNATIVES.keys()))
    st.subheader(f"Suggestions for {chosen_type}")
    for suggestion in GREEN_ALTERNATIVES[chosen_type]:
        st.markdown(f"🌱 **{suggestion}**")

    st.divider()
    st.subheader("💚 Random eco tip")
    if st.button("Show me an eco tip"):
        st.session_state.tip_number = random.randrange(len(ECO_TIPS))
    st.success(ECO_TIPS[st.session_state.tip_number])

    st.caption("Suggestions are general ideas. Check product details and certifications before making a purchase.")

# -------------------- PURCHASE HISTORY --------------------
elif page == "My Purchase History":
    st.markdown("""
    <div class="hero">
      <h1>🧾 My Purchase History</h1>
      <p>Review the purchases you have recorded in this session.</p>
    </div>
    """, unsafe_allow_html=True)

    if all_purchases:
        df = pd.DataFrame(all_purchases)
        display_columns = ["date", "status", "product", "product_type",
                           "brand", "price", "co2"]
        display_df = df[display_columns].copy()
        display_df.columns = ["Date", "Status", "Product", "Product type",
                              "Brand", "Price (₹)", "Estimated CO₂e (kg)"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download purchase history (CSV)",
            data=csv_data,
            file_name="shopimpact_purchase_history.csv",
            mime="text/csv"
        )

        if st.button("Clear all recorded purchases"):
            st.session_state.purchases = []
            st.rerun()
    else:
        st.info("Your purchase history is empty. Use Log a Purchase to begin.")

# -------------------- FOOTER --------------------
st.sidebar.divider()
st.sidebar.caption("ShopImpact © 2026")
st.sidebar.caption("Small choices. Greener future. 🌍")
st.caption(
    "CO₂e figures are illustrative classroom estimates based on price-category "
    "multipliers. They are not verified product-specific life-cycle assessments. "
    "Data is kept in the current app session and may reset when the session restarts."
)
