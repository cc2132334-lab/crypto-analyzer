import streamlit as st
import ccxt
import google.generativeai as genai

# Page config
st.set_page_config(page_title="Crypto Futures Signal", layout="centered")

st.title("🎯 Crypto Futures Setup Generator")

# API Key input or secret
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.text_input("Apni Gemini API Key daalein:", type="password")

symbol_input = st.text_input("Crypto Pair likhein (e.g., BTC/USDT, ETH/USDT):", "BTC/USDT")
timeframe = st.selectbox("Timeframe chunein:", ["15m", "1h", "4h", "1d"], index=1)

if st.button("Generate Analysis"):
    if not api_key:
        st.error("Kripya Gemini API Key daalein.")
    else:
        with st.spinner("Market data fetch aur analysis ho raha hai..."):
            try:
                # 1. Fetch live market candles
                exchange = ccxt.binance()
                formatted_symbol = symbol_input.upper().replace("/", "")
                # Format to standard CCXT pair
                if not "/" in symbol_input:
                    formatted_symbol = symbol_input.upper().replace("USDT", "/USDT")
                else:
                    formatted_symbol = symbol_input.upper()

                ohlcv = exchange.fetch_ohlcv(formatted_symbol, timeframe=timeframe, limit=30)
                current_price = ohlcv[-1][4]
                
                # 2. Setup AI Prompt
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")

                prompt = f"""
                You are an expert crypto futures trader with 20+ years of experience.
                Analyze this market data for {formatted_symbol} ({timeframe} timeframe):
                Current Price: {current_price}
                Recent Candles (Timestamp, Open, High, Low, Close, Volume): {ohlcv[-10:]}

                CRITICAL INSTRUCTION:
                Do NOT output Steps 1 to 5. Keep all calculations and reasoning internal. 
                ONLY output the final results for Step 6 and Step 7 in simple Hinglish (Hindi + English). 
                EVEN IF THE CURRENT STATUS IS "WAIT / NO TRADE", YOU MUST PROVIDE THE EXACT ENTRY LEVELS FOR BOTH UPCOMING SCENARIOS (WHEN TO LONG & WHEN TO SHORT).

                Output Format:
                ### 🎯 Step 6: Trade Entry Recommendation
                - **Current Status:** [DIRECT ENTRY / WAIT FOR BREAKOUT]

                🟢 **LONG (Buy) Setup:**
                  - **Condition:** [Konsa level todne par long lena hai]
                  - **Entry Zone:** [Exact Price Range]
                  - **Stop Loss:** [Exact Price Level]
                  - **Target 1:** [First Profit Level]
                  - **Target 2:** [Second Profit Level]
                  - **Risk:Reward Ratio:** [e.g., 1:2.2]

                🔴 **SHORT (Sell) Setup:**
                  - **Condition:** [Konsa level todne par short lena hai]
                  - **Entry Zone:** [Exact Price Range]
                  - **Stop Loss:** [Exact Price Level]
                  - **Target 1:** [First Profit Level]
                  - **Target 2:** [Second Profit Level]
                  - **Risk:Reward Ratio:** [e.g., 1:2.1]

                - **Confidence Level:** [Low / Medium / High + 1 line reason]
                - **Simple Explanation:** [Kyun wait karna hai, kya hone par trade trigger hoga, aur abhi entry kyu nahi leni]

                ---

                ### ⚠️ Step 7: Risk Warning & Invalidation
                - **Invalidation Level:** [Kis level pe analysis completely fail ho jaayegi]
                - **Exit Signal:** [Kis point pe turant trade cut karke nikalna hai]
                - **Worst Case Risk:** [Sideways chop ya fakeout ka danger]

                Rules:
                1. Minimum 2:1 Risk:Reward ratio required for all setups.
                2. Give exact price numbers, no vague zones.
                """

                response = model.generate_content(prompt)
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Error aaya: {str(e)}")

