import plotly.io as pio
import plotly.graph_objects as go

# Design Tokens (Inspired by TradingView & NVESTIQ)
COLORS = {
    "background": "#050a14",      # Deep Obsidian
    "card_bg": "rgba(10, 15, 29, 0.7)", # Glass Navy
    "accent": "#00d2ff",          # Electric Cyan
    "bullish": "#00ffcc",         # Neon Teal
    "bearish": "#ff4b2b",         # Vivid Red
    "text_primary": "#ffffff",
    "text_secondary": "#8f9bb3",
    "grid": "rgba(255, 255, 255, 0.05)"
}

# Custom Plotly Template
def get_tradingview_template():
    template = go.layout.Template()
    
    template.layout = go.Layout(
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        font=dict(color=COLORS["text_secondary"], family="Inter, sans-serif"),
        xaxis=dict(
            gridcolor=COLORS["grid"],
            linecolor=COLORS["grid"],
            zeroline=False,
            showgrid=True,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            gridcolor=COLORS["grid"],
            linecolor=COLORS["grid"],
            zeroline=False,
            showgrid=True,
            tickfont=dict(size=10)
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified",
        dragmode="pan"
    )
    
    return template

# Inject custom CSS for Streamlit
def get_custom_css():
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        /* Global Overrides */
        .stApp {{
            background-color: {COLORS["background"]};
            color: {COLORS["text_primary"]};
            font-family: 'Inter', sans-serif;
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: #03070b;
            border-right: 1px solid {COLORS["grid"]};
        }}
        
        /* Glassmorphism Cards */
        .metric-card {{
            background: {COLORS["card_bg"]};
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0, 210, 255, 0.2);
            border-color: {COLORS["accent"]};
        }}

        .metric-label {{
            color: {COLORS["text_secondary"]};
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05rem;
        }}

        .metric-value {{
            color: {COLORS["text_primary"]};
            font-size: 1.8rem;
            font-weight: 800;
            margin: 5px 0;
        }}

        .metric-delta {{
            font-size: 0.9rem;
            font-weight: 600;
        }}

        /* Buttons Enhancement */
        .stButton>button {{
            background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 1rem;
            width: 100%;
            transition: all 0.3s ease;
        }}

        .stButton>button:hover {{
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
            transform: scale(1.02);
        }}

        /* Hide Streamlit components for a cleaner look */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Custom Header Styling */
        .main-header {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(to right, #ffffff, #00d2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
    </style>
    """
