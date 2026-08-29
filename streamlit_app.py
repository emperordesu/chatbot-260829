import streamlit as st
from openai import OpenAI
from urllib.parse import quote_plus

# ---- 페이지 설정 ----
st.set_page_config(page_title="💻 노트북 비교분석 챗봇", page_icon="💻", layout="wide")

# ---- 카드 스타일 CSS ----
st.markdown(
    """
    <style>
    .laptop-card {
        display: flex; gap: 16px; align-items: flex-start;
        border: 1px solid #e5e7eb; border-radius: 14px 14px 0 0; padding: 16px;
        margin-bottom: 0; background: #ffffff; transition: background 0.15s ease;
    }
    .laptop-card.selected {
        background: #dbeafe; border-color: #3b82f6; border-width: 2px;
    }
    .laptop-thumb {
        width: 130px; flex-shrink: 0; text-align: center;
    }
    .laptop-thumb-box {
        width: 130px; height: 90px; border-radius: 10px;
        background: linear-gradient(135deg,#1e293b,#334155);
        display: flex; align-items: center; justify-content: center;
        font-size: 34px;
    }
    .laptop-thumb-badge {
        margin-top: 6px; font-size: 12px; color: #334155; font-weight: 600;
        line-height: 1.4;
    }
    .laptop-info { flex: 1; }
    .laptop-tag {
        display: inline-block; background: #eff6ff; color: #2563eb;
        font-weight: 700; font-size: 12.5px; padding: 2px 8px;
        border-radius: 6px; margin-bottom: 6px;
    }
    .laptop-title { font-size: 17px; font-weight: 800; margin: 2px 0 8px 0; color: #111827; }
    .laptop-spec { font-size: 13.5px; color: #374151; line-height: 1.9; }
    .laptop-spec b { color: #111827; }
    .laptop-price { font-size: 15px; font-weight: 800; color: #dc2626; margin-top: 6px; }
    .yt-link {
        display: inline-flex; align-items: center; gap: 6px; margin-top: 10px;
        text-decoration: none; font-size: 13px; color: #111827;
    }
    .yt-thumb { width: 120px; border-radius: 8px; display: block; margin-top: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- 노트북 데이터베이스 ----
# 2025년 판매 기준 / CPU 조건: 인텔 코어 울트라5 이상(2023년~) 또는 AMD 라이젠AI 5 이상(2024년~), 애플 M4(맥 OS 옵션용) 포함
# 참고: 실제 가격/사양은 프로모션 등으로 자주 바뀌므로, 운영 환경에서는 가격비교 API 등으로 주기적 갱신을 권장합니다.
LAPTOP_DB = [
    {"brand": "삼성", "model": "갤럭시북5 프로 14", "screen": 14, "screen_label": "35.6cm(14인치)",
     "cpu_tier": "울트라5", "cpu_detail": "인텔 코어 울트라5(2세대) 226V",
     "ram": [16], "storage": [256], "os": "Windows 11 Home",
     "weight": 1.23, "price": 1799000, "video": "KX6cL4GoiBQ"},
    {"brand": "삼성", "model": "갤럭시북5 프로 16 (울트라5)", "screen": 16, "screen_label": "40.6cm(16인치)",
     "cpu_tier": "울트라5", "cpu_detail": "인텔 코어 울트라5(2세대) 226V",
     "ram": [16], "storage": [256], "os": "Windows 11 Home",
     "weight": 1.56, "price": 2099000, "video": "M-yOvBXNweE"},
    {"brand": "삼성", "model": "갤럭시북5 프로 16 (울트라7)", "screen": 16, "screen_label": "40.6cm(16인치)",
     "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(2세대) 258V",
     "ram": [16, 32], "storage": [512, 1024], "os": "Windows 11 Home",
     "weight": 1.56, "price": 2808000, "video": "M-yOvBXNweE"},
    {"brand": "삼성", "model": "갤럭시북5 프로360 16", "screen": 16, "screen_label": "40.6cm(16인치)",
     "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(2세대) 258V",
     "ram": [16, 32], "storage": [512, 1024], "os": "Windows 11 Home",
     "weight": 1.66, "price": 2926000, "video": "Y2Pn8rRZ92s"},
    {"brand": "LG", "model": "그램 프로16 (울트라5)", "screen": 16, "screen_label": "40.6cm(16인치)",
     "cpu_tier": "울트라5", "cpu_detail": "인텔 코어 울트라5(2세대) 225H",
     "ram": [16], "storage": [256], "os": "Windows 11 Home",
     "weight": 1.199, "price": 1799000, "video": "HUc5kJdy5PE"},
    {"brand": "LG", "model": "그램 프로16 (울트라7)", "screen": 16, "screen_label": "40.6cm(16인치)",
     "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(2세대) 255H",
     "ram": [32], "storage": [1024], "os": "Windows 11 Home",
     "weight": 1.199, "price": 2450000, "video": "HUc5kJdy5PE"},
    {"brand": "LG", "model": "그램 프로360 16", "screen": 16, "screen_label": "40.6cm(16인치)",
     "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(2세대) 255H",
     "ram": [32], "storage": [512, 1024], "os": "Windows 11 Home",
     "weight": 1.399, "price": 2700000, "video": "HUc5kJdy5PE"},
    {"brand": "LG", "model": "그램북 AI 16", "screen": 16, "screen_label": "40.6cm(16인치)",
     "cpu_tier": "라이젠AI5", "cpu_detail": "AMD 라이젠 AI5 435",
     "ram": [16], "storage": [512], "os": "Windows 11 Home",
     "weight": 1.199, "price": 1300000, "video": "HUc5kJdy5PE"},
    {"brand": "LG", "model": "그램 프로17", "screen": 17, "screen_label": "43.1cm(17인치)",
     "cpu_tier": "울트라5", "cpu_detail": "인텔 코어 울트라5(2세대) 225H",
     "ram": [16], "storage": [256], "os": "OS 미포함(프리도스)",
     "weight": 1.369, "price": 1998890, "video": "HUc5kJdy5PE"},
    {"brand": "LG", "model": "울트라PC 17", "screen": 17, "screen_label": "43.1cm(17인치)",
     "cpu_tier": "울트라5", "cpu_detail": "인텔 코어 울트라5(1세대) 125H",
     "ram": [8], "storage": [256], "os": "OS 미포함(프리도스)",
     "weight": 1.39, "price": 2210000, "video": None},
    {"brand": "에이서", "model": "Swift 16 AI", "screen": 16, "screen_label": "40.6cm(16인치)",
     "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(2세대) 258V",
     "ram": [32], "storage": [512], "os": "Windows 11 Home",
     "weight": 1.46, "price": 1999000, "video": "YSu4MHhK0ks"},
    {"brand": "에이서", "model": "Swift Edge 14 AI", "screen": 14, "screen_label": "35.6cm(14인치)",
     "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(2세대) 258V",
     "ram": [32], "storage": [1024], "os": "Windows 11 Home",
     "weight": 0.99, "price": 2190000, "video": None},
    {"brand": "에이서", "model": "Swift Go 14 AI", "screen": 14, "screen_label": "35.6cm(14인치)",
     "cpu_tier": "울트라5", "cpu_detail": "인텔 코어 울트라5(1세대)",
     "ram": [16], "storage": [512], "os": "Windows 11 Home",
     "weight": 1.32, "price": 969000, "video": None},
    {"brand": "MSI", "model": "모던 A15 AI+ (F3HMG)", "screen": 15, "screen_label": "39.6cm(15.6인치)",
     "cpu_tier": "라이젠AI5", "cpu_detail": "AMD 라이젠 AI5 330",
     "ram": [16], "storage": [512], "os": "OS 미포함(프리도스)",
     "weight": 1.6, "price": 1197470, "video": None},
    {"brand": "애플", "model": "맥북 에어 13 (M4)", "screen": 14, "screen_label": "13.6인치",
     "cpu_tier": "Apple M4", "cpu_detail": "애플 M4 (8코어 CPU)",
     "ram": [16, 24, 32], "storage": [256, 512, 1024, 2048], "os": "macOS",
     "weight": 1.24, "price": 1690000, "video": "532mVCw4MWQ"},
    {"brand": "애플", "model": "맥북 에어 15 (M4)", "screen": 15, "screen_label": "15.3인치",
     "cpu_tier": "Apple M4", "cpu_detail": "애플 M4 (10코어 CPU)",
     "ram": [16, 24, 32], "storage": [256, 512, 1024, 2048], "os": "macOS",
     "weight": 1.51, "price": 1990000, "video": "joQ9YhR46uY"},
]

# ---- 제목 및 설명 ----
st.title("💻 노트북 비교분석 챗봇")
st.write(
    "왼쪽에서 원하는 사양 조건을 선택하고 **검색 버튼**을 누르면 조건에 맞는 2025년 판매 노트북이 카드로 나타납니다. "
    "카드를 클릭해 2개를 선택하면 자동으로 비교분석을 시작해요. "
    "사용하려면 OpenAI API 키가 필요합니다. [여기서 발급받으세요](https://platform.openai.com/account/api-keys)."
)

# ---- API 키 처리 ----
openai_api_key = st.secrets.get("OPENAI_API_KEY", None)
if not openai_api_key:
    openai_api_key = st.text_input(
        "OpenAI API Key", type="password",
        help="secrets.toml에 키를 등록하면 이 입력창은 표시되지 않습니다.",
    )

if not openai_api_key:
    st.info("계속하려면 OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    SYSTEM_PROMPT = """당신은 노트북 구매를 도와주는 전문 컨설턴트입니다.
사용자가 제공하는 두 노트북의 사양 데이터를 바탕으로 마크다운 표를 이용해 비교분석해주세요.
표에는 최소한 화면크기, CPU, RAM, 저장공간, 운영체제, 무게, 가격 항목을 포함하고,
표 아래에는 다음 내용을 정리해주세요:
1. 두 노트북의 핵심 차이점
2. 각 노트북의 장단점
3. 어떤 사용자에게 어떤 모델이 더 적합한지 추천
정보가 주어지지 않은 부분은 추측하지 말고 "제공된 정보 없음"이라고 표시하세요."""

    # ================= 사이드바: 사양 조건 필터 (폼으로 묶어서 검색 버튼 클릭 시에만 반영) =================
    with st.sidebar:
        st.header("🔍 사양 조건으로 찾기")

        with st.form("filter_form"):
            sel_screen = st.multiselect("화면크기대 (인치)", [14, 15, 16, 17], placeholder="전체")
            sel_cpu = st.multiselect(
                "CPU (인텔 코어 울트라5 이상 / AMD 라이젠AI5 이상 / Apple M4)",
                ["울트라5", "울트라7", "라이젠AI5", "Apple M4"], placeholder="전체",
            )
            sel_ram = st.multiselect("램 용량 (GB)", [8, 16, 32], placeholder="전체")
            sel_storage = st.multiselect("저장 용량대 (GB)", [256, 512, 1024, 2048], placeholder="전체")
            sel_os = st.multiselect(
                "운영체제", ["Windows 11 Home", "OS 미포함(프리도스)", "macOS"], placeholder="전체",
            )
            sel_weight = st.slider("무게 (kg)", 0.9, 2.0, (0.9, 2.0), step=0.01)
            sel_price = st.slider("가격 (원)", 900000, 3000000, (900000, 3000000), step=50000)

            submitted = st.form_submit_button("🔍 검색", use_container_width=True, type="primary")

        st.divider()
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.session_state.selected = []
            st.session_state.last_compared = None
            st.rerun()

    # ---- 세션 상태 초기화 ----
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "filtered" not in st.session_state:
        st.session_state.filtered = None  # 검색 전에는 결과 없음
    if "selected" not in st.session_state:
        st.session_state.selected = []  # 카드 클릭으로 선택된 노트북 키 (최대 2개)
    if "last_compared" not in st.session_state:
        st.session_state.last_compared = None  # 중복 비교 요청 방지용

    # ---- 검색 버튼 클릭 시에만 필터링 실행 ----
    if submitted:
        def matches(item):
            if sel_screen and item["screen"] not in sel_screen:
                return False
            if sel_cpu and item["cpu_tier"] not in sel_cpu:
                return False
            if sel_ram and not set(item["ram"]) & set(sel_ram):
                return False
            if sel_storage and not set(item["storage"]) & set(sel_storage):
                return False
            if sel_os and item["os"] not in sel_os:
                return False
            if not (sel_weight[0] <= item["weight"] <= sel_weight[1]):
                return False
            if not (sel_price[0] <= item["price"] <= sel_price[1]):
                return False
            return True

        st.session_state.filtered = [item for item in LAPTOP_DB if matches(item)]

    filtered = st.session_state.filtered

    # ================= 메인 화면: 조건에 맞는 노트북 카드 목록 =================
    if filtered is None:
        st.info("👈 왼쪽에서 조건을 선택하고 **검색** 버튼을 눌러주세요.")
    elif not filtered:
        st.warning("조건에 맞는 노트북이 없습니다. 필터 조건을 완화해보세요.")
    else:
        st.subheader(f"📋 조건에 맞는 노트북 ({len(filtered)}개)")
        st.caption("카드를 클릭해서 선택하세요 (선택하면 파란색으로 표시됩니다). 2개를 선택하면 자동으로 비교분석을 시작해요.")

        for idx, it in enumerate(filtered):
            key = f'{it["brand"]} {it["model"]}'
            ram_txt = " / ".join(f"{r}GB" for r in it["ram"])
            storage_txt = " / ".join(f"{s}GB" for s in it["storage"])
            is_selected = key in st.session_state.selected

            video_html = ""
            if it["video"]:
                thumb_url = f'https://img.youtube.com/vi/{it["video"]}/mqdefault.jpg'
                watch_url = f'https://www.youtube.com/watch?v={it["video"]}'
                video_html = (
                    f'<a class="yt-link" href="{watch_url}" target="_blank">'
                    f'<img class="yt-thumb" src="{thumb_url}"/></a>'
                    f'<div><a class="yt-link" href="{watch_url}" target="_blank">▶ 리뷰 영상 보기 (YouTube)</a></div>'
                )
            else:
                query = quote_plus(f'{it["brand"]} {it["model"]} 리뷰')
                search_url = f'https://www.youtube.com/results?search_query={query}'
                video_html = f'<a class="yt-link" href="{search_url}" target="_blank">🔎 YouTube에서 리뷰 검색</a>'

            card_class = "laptop-card selected" if is_selected else "laptop-card"
            card_html = f"""
            <div class="{card_class}">
                <div class="laptop-thumb">
                    <div class="laptop-thumb-box">💻</div>
                    <div class="laptop-thumb-badge">{it["screen_label"]}<br/>{it["weight"]}kg</div>
                </div>
                <div class="laptop-info">
                    <span class="laptop-tag">{it["brand"]} · {it["cpu_detail"]}</span>
                    <div class="laptop-title">{it["model"]}</div>
                    <div class="laptop-spec">
                        <b>[화면]</b> {it["screen_label"]} &nbsp;/&nbsp;
                        <b>[CPU]</b> {it["cpu_detail"]}<br/>
                        <b>[구성]</b> RAM {ram_txt} / 저장공간 {storage_txt} &nbsp;/&nbsp; {it["os"]}<br/>
                        <b>[무게]</b> {it["weight"]}kg
                    </div>
                    <div class="laptop-price">{it["price"]:,}원~</div>
                    {video_html}
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            # 카드 바로 아래 선택 토글 버튼 (클릭 시 카드가 파란 배경으로 바뀜)
            btn_disabled = (not is_selected) and len(st.session_state.selected) >= 2
            btn_label = "✅ 선택됨 (클릭해서 해제)" if is_selected else "☐ 이 노트북 선택하기"
            btn_type = "primary" if is_selected else "secondary"
            if st.button(btn_label, key=f"sel_{idx}", use_container_width=True,
                         type=btn_type, disabled=btn_disabled):
                if is_selected:
                    st.session_state.selected.remove(key)
                else:
                    st.session_state.selected.append(key)
                st.rerun()

        # ---- 2개가 선택되면 자동으로 비교분석 프롬프트 생성 (같은 조합 중복 요청 방지) ----
        if len(st.session_state.selected) == 2:
            pair = tuple(sorted(st.session_state.selected))
            if st.session_state.last_compared != pair:
                selected_items = [it for it in filtered if f'{it["brand"]} {it["model"]}' in st.session_state.selected]
                spec_lines = []
                for it in selected_items:
                    spec_lines.append(
                        f'- {it["brand"]} {it["model"]}: 화면 {it["screen_label"]}, CPU {it["cpu_detail"]}, '
                        f'RAM {"/".join(f"{r}GB" for r in it["ram"])}, 저장공간 {"/".join(f"{s}GB" for s in it["storage"])}, '
                        f'{it["os"]}, 무게 {it["weight"]}kg, 가격 {it["price"]:,}원'
                    )
                auto_prompt = "다음 두 노트북을 비교분석해줘.\n" + "\n".join(spec_lines)
                st.session_state.messages.append({"role": "user", "content": auto_prompt})
                st.session_state.last_compared = pair

        if st.session_state.selected:
            if st.button("🔄 선택 초기화", use_container_width=False):
                st.session_state.selected = []
                st.session_state.last_compared = None
                st.rerun()

    # ---- 대화 표시 ----
    st.divider()
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ---- 응답 생성 함수 ----
    def generate_response():
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        stream = client.chat.completions.create(
            model="gpt-4o-mini", messages=api_messages, stream=True,
        )
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    if (
        st.session_state.messages
        and st.session_state.messages[-1]["role"] == "user"
    ):
        generate_response()

    # ---- 채팅 입력창 (자유 질문도 가능) ----
    if prompt := st.chat_input("노트북 관련 질문을 자유롭게 입력하세요"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        generate_response()
