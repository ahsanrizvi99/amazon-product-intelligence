from core.utils import md

def inject_css():
    md("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --bg: #f4f9fd;
        --surface: rgba(255,255,255,.85);
        --surface-solid: #ffffff;
        --line: #dcebf5;
        --line-strong: #b9d8ef;
        --ink: #102a43;
        --muted: #58738c;
        --blue: #5aa9e6;
        --blue-dark: #2e78b7;
        --blue-soft: #eaf5fd;
        --green: #16866a;
        --yellow: #996f18;
        --orange: #e5732f;
        --red: #b64b55;
        --shadow-sm: 0 8px 24px rgba(40,109,158,.08);
        --shadow-md: 0 16px 40px rgba(40,109,158,.12);
        --shadow-lg: 0 26px 70px rgba(40,109,158,.16);
    }
    html, body, [class*="css"], .stApp { font-family: "DM Sans", Arial, sans-serif; color: var(--ink); }
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(121,213,232,.20), transparent 28%),
            radial-gradient(circle at 92% 4%, rgba(90,169,230,.18), transparent 30%),
            linear-gradient(180deg, #f5fbff 0%, var(--bg) 36%, #edf6fd 100%);
    }
    .block-container { max-width: 1500px; padding: 2.1rem 3.2rem 4rem; }

    @keyframes fadeUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
    .animate-in { animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

    .topbar {
        position: relative; overflow: hidden;
        background: linear-gradient(115deg, #eaf7ff 0%, #cfeaff 46%, #bfe5f7 100%);
        border: 1px solid rgba(255,255,255,.82);
        box-shadow: var(--shadow-lg); border-radius: 28px 28px 18px 18px;
        margin: 0 0 1.5rem 0; padding: 1.35rem 1.7rem 1.25rem;
        display: flex; align-items: baseline; gap: 1rem;
    }
    .topbar .mark { color: #123a57; font-family: 'Manrope', sans-serif; font-size: 1.6rem; font-weight: 800; letter-spacing: -.045em; }
    .topbar .mark span { color: var(--blue-dark); }
    .topbar .tag { color: #55758f; font-size: .85rem; font-weight: 600; border-left: 1px solid #b4d3e8; padding-left: 1rem; }

    div[data-testid="stRadio"] > div[role="radiogroup"] {
        background: rgba(255,255,255,.72); border: 1px solid rgba(185,216,239,.8);
        box-shadow: var(--shadow-sm); border-radius: 14px; padding: 5px;
        display: flex; flex-wrap: wrap; gap: 5px !important; justify-content: center;
        margin-bottom: 1rem;
    }
    div[data-testid="stRadio"] label { border-radius: 10px; padding: 6px 14px; font-size: 0.85rem; font-weight: 600; color: #53728a; }
    div[data-testid="stRadio"] label:hover { background: var(--blue-soft); }

    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
    .stat {
        background: var(--surface); border: 1px solid rgba(185,216,239,.82);
        box-shadow: var(--shadow-sm); border-radius: 14px; padding: 1.25rem .9rem; text-align: center;
    }
    .stat-lbl { font-size: .65rem; letter-spacing: .13em; text-transform: uppercase; color: var(--muted); font-weight: 800; margin-bottom: .35rem; }
    .stat-val { font-family: 'Manrope', sans-serif; font-size: 1.8rem; font-weight: 800; color: var(--ink); line-height: 1; }

    .product-row {
        display: flex; align-items: center; gap: 1.5rem; background: var(--surface);
        border: 1px solid rgba(185,216,239,.82); box-shadow: var(--shadow-sm);
        border-radius: 22px; padding: 1.2rem 1.5rem; margin-bottom: 1rem;
    }
    .product-row img { width: 100px; height: 100px; object-fit: contain; border-radius: 12px; }
    .product-row-title { font-family: "Manrope", sans-serif; font-size: 1.2rem; font-weight: 800; color: var(--ink); margin-bottom: 0.3rem; line-height: 1.28; }
    .product-row-meta { font-size: 0.85rem; color: var(--muted); margin-bottom: 0.2rem; }
    .product-row-price { font-weight: 800; color: #1d6fa9; font-size: 1.2rem; }

    .carousel-container { display: flex; overflow-x: auto; gap: 1rem; padding: 0.5rem 0.5rem 1.5rem 0.5rem; }
    .carousel-container::-webkit-scrollbar { height: 8px; }
    .carousel-container::-webkit-scrollbar-thumb { background: var(--line-strong); border-radius: 999px; }
    .carousel-card {
        min-width: 220px; max-width: 220px; flex-shrink: 0; background: var(--surface-solid);
        border-radius: 16px; padding: 1.1rem; box-shadow: var(--shadow-sm); border: 1px solid var(--line);
    }
    .carousel-card img { width: 100%; height: 130px; object-fit: contain; margin-bottom: 0.8rem; border-radius: 8px; background: #fafcfe; }
    .carousel-title { font-size: 0.83rem; font-weight: 700; height: 2.4em; overflow: hidden; margin-bottom: 0.4rem; line-height: 1.2; }
    .carousel-price { font-size: 1.15rem; font-weight: 800; color: #1d6fa9; margin-bottom: 0.35rem; }
    .carousel-sim { font-size: 0.7rem; color: var(--muted); margin-bottom: 3px; }
    .sim-track { width: 100%; background: var(--line); border-radius: 999px; height: 6px; margin-bottom: 0.7rem; overflow: hidden; }
    .sim-fill { background: var(--blue-dark); height: 100%; border-radius: 999px; }

    .tag-pill { display: inline-block; padding: 3px 8px; border-radius: 6px; font-size: 0.68rem; font-weight: 700; margin: 2px 3px 0 0; }
    .tag-green { background: #e8f7f1; color: var(--green); border: 1px solid #b8e5d6; }
    .tag-orange { background: #fff4ec; color: var(--orange); border: 1px solid #fedbc5; }
    .tag-blue { background: #eaf5fd; color: var(--blue-dark); border: 1px solid #b9d8ef; }

    .cluster-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 1.2rem; padding: 0.5rem 0; }
    .cluster-card { background: var(--surface-solid); border: 1px solid var(--line); border-radius: 16px; padding: 0.9rem; text-align: center; box-shadow: var(--shadow-sm); }
    .cluster-card img { width: 100%; height: 130px; object-fit: contain; margin-bottom: 0.8rem; border-radius: 8px; background: #fafcfe; }
    .cluster-title { font-size: 0.78rem; font-weight: 600; color: var(--ink); line-height: 1.32; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 2.6em; }
    .target-glow { border: 2px solid var(--blue-dark); box-shadow: 0 0 15px rgba(46,120,183,0.3); }

    .pill { display: inline-block; border-radius: 999px; padding: .32rem .82rem; font-size: .76rem; font-weight: 800; margin-right: .4rem; margin-bottom: .35rem; }
    .pos { background: #e6f8f1; color: #15785f; border: 1px solid #a6dfcd; }
    .neu { background: #fff7df; color: #8e6517; border: 1px solid #e7cf8f; }
    .neg { background: #ffeded; color: #a94b54; border: 1px solid #e8b4b9; }

    .panel-head { font-family: 'Manrope'; font-size: 0.95rem; font-weight: 800; color: var(--ink); text-align: center; margin-bottom: 0.6rem; }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
        box-shadow: var(--shadow-sm);
        background: var(--surface-solid);
    }

    div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 18px; overflow: hidden; box-shadow: var(--shadow-sm); }

    .product-tile-inner {
        background: var(--surface-solid);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 0.9rem 0.9rem 0.7rem;
        box-shadow: var(--shadow-sm);
        margin-bottom: -0.6rem;
        transition: transform .28s cubic-bezier(.16,1,.3,1), box-shadow .28s ease, border-color .28s ease;
    }
    .product-tile-inner:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-md);
        border-color: var(--line-strong);
    }
    .product-tile-inner img { width: 100%; height: 118px; object-fit: contain; border-radius: 10px; background: #fafcfe; margin-bottom: .6rem; }
    .pt-cat { font-size: .62rem; font-weight: 800; letter-spacing: .07em; color: var(--muted); text-transform: uppercase; margin-bottom: .3rem; }
    .pt-title { font-size: .85rem; font-weight: 700; line-height: 1.3; height: 2.6em; overflow: hidden; margin-bottom: .5rem; color: var(--ink); }
    .pt-bottom { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: .3rem; }
    .pt-price { font-weight: 800; color: #1d6fa9; font-size: 1.02rem; }
    .pt-rating { font-size: .72rem; color: var(--muted); }

    .stButton > button {
        border-radius: 999px !important;
        border: 1px solid var(--line-strong) !important;
        background: var(--surface-solid) !important;
        color: var(--blue-dark) !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        padding: 0.45rem 1rem !important;
        transition: all .2s cubic-bezier(.16,1,.3,1) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .stButton > button:hover {
        background: var(--blue-dark) !important;
        color: #fff !important;
        border-color: var(--blue-dark) !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md) !important;
    }
    .stLinkButton > a {
        border-radius: 999px !important;
        font-weight: 700 !important;
        transition: all .2s cubic-bezier(.16,1,.3,1) !important;
    }

    div[data-testid="stDialog"] { animation: piOverlayFade .22s ease-out; }
    div[data-testid="stDialog"] [role="dialog"],
    div[data-testid="stDialog"] > div > div {
        animation: piDialogPop .38s cubic-bezier(0.16, 1, 0.3, 1);
        border-radius: 26px !important;
        box-shadow: var(--shadow-lg) !important;
    }
    @keyframes piOverlayFade { from { opacity: 0; } to { opacity: 1; } }
    @keyframes piDialogPop {
        from { opacity: 0; transform: scale(.93) translateY(18px); }
        to   { opacity: 1; transform: scale(1) translateY(0); }
    }
    </style>
    """)