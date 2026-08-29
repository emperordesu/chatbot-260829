import streamlit as st
from openai import OpenAI

# ---- 페이지 설정 ----
st.set_page_config(page_title="💻 노트북 비교분석 챗봇", page_icon="💻", layout="wide")

# ---- 노트북 데이터베이스 ----
# 2025년 판매 기준 / CPU 조건: 인텔 코어 울트라5 이상(2023년 출시 시리즈1~) 또는 AMD 라이젠AI 5 이상(2024년 출시~)
# 참고: 실제 가격/사양은 프로모션, 메모리 가격 변동 등에 따라 수시로 바뀌므로
#       운영 환경에서는 이 표를 브랜드 공식 사이트나 가격비교 API로 주기적으로 갱신하는 것을 권장합니다.
LAPTOP_DB = [
    {
        "brand": "삼성", "model": "갤럭시북5 프로 14",
        "screen": 14, "cpu_tier": "울트라5", "cpu_detail": "인텔 코어 울트라5(시리즈2) 226V",
        "ram": [16], "storage": [256], "os": "Windows 11 Home",
        "weight": 1.23, "price": 1799000,
    },
    {
        "brand": "삼성", "model": "갤럭시북5 프로 16 (울트라5)",
        "screen": 16, "cpu_tier": "울트라5", "cpu_detail": "인텔 코어 울트라5(시리즈2) 226V",
        "ram": [16], "storage": [256], "os": "Windows 11 Home",
        "weight": 1.56, "price": 2099000,
    },
    {
        "brand": "삼성", "model": "갤럭시북5 프로 16 (울트라7)",
        "screen": 16, "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(시리즈2) 258V",
        "ram": [16, 32], "storage": [512, 1024], "os": "Windows 11 Home",
        "weight": 1.56, "price": 2808000,
    },
    {
        "brand": "삼성", "model": "갤럭시북5 프로 360 16",
        "screen": 16, "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(시리즈2) 258V",
        "ram": [16, 32], "storage": [512, 1024], "os": "Windows 11 Home",
        "weight": 1.66, "price": 2926000,
    },
    {
        "brand": "LG", "model": "그램 프로16 (울트라5)",
        "screen": 16, "cpu_tier": "울트라5", "cpu_detail": "인텔 코어 울트라5(시리즈2) 225H",
        "ram": [16], "storage": [256], "os": "Windows 11 Home",
        "weight": 1.199, "price": 1990000,
    },
    {
        "brand": "LG", "model": "그램 프로16 (울트라7)",
        "screen": 16, "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(시리즈2) 255H",
        "ram": [32], "storage": [1024], "os": "Windows 11 Home",
        "weight": 1.199, "price": 2450000,
    },
    {
        "brand": "LG", "model": "그램 프로360 16",
        "screen": 16, "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(시리즈2) 255H",
        "ram": [32], "storage": [512, 1024], "os": "Windows 11 Home",
        "weight": 1.399, "price": 2700000,
    },
    {
        "brand": "LG", "model": "그램북 AI 16",
        "screen": 16, "cpu_tier": "라이젠AI5", "cpu_detail": "AMD 라이젠 AI5 435",
        "ram": [16], "storage": [512], "os": "Windows 11 Home",
        "weight": 1.199, "price": 1300000,
    },
    {
        "brand": "에이서", "model": "Swift 16 AI",
        "screen": 16, "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(시리즈2) 258V",
        "ram": [32], "storage": [512], "os": "Windows 11 Home",
        "weight": 1.46, "price": 1999000,
    },
    {
        "brand": "에이서", "model": "Swift Edge 14 AI",
        "screen": 14, "cpu_tier": "울트라7", "cpu_detail": "인텔 코어 울트라7(시리즈2) 258V",
        "ram": [32], "storage": [1024], "os": "Windows 11 Home",
        "weight": 0.99, "price": 2190000,
    },
    {
        "brand": "에이서", "model": "Swift Go 14 AI",
        "screen": 14, "cpu_tier": "울트라5", "cpu_detail": "인텔 코어 울트라5(시리즈1)",
        "ram": [16], "storage": [512], "os": "Windows 11 Home",
        "weight": 1.32, "price": 969000,
    },
    {
        "brand": "에이서", "model": "Swift 14 AI (라이젠)",
        "screen": 14, "cpu_tier": "라이젠AI7", "cpu_detail": "AMD 라이젠 AI7 350",
        "ram": [16, 32], "storage": [512, 1024], "os": "Windows 11 Home",
        "weight": 1.3, "price": 1600000,
    },
]

# ---- 제목 및 설명 ----
st.title("💻 노트북 비교분석 챗봇")
st.write(
    "원하는 사양 조건을 선택하면 조건에 맞는 2025년 판매 노트북 목록이 나타납니다. "
    "그중 2개를 골라 비교분석을 요청해보세요. "
    "사용하려면 OpenAI API 키가 필요합니다. [여기서 발급받으세요](https://platform.openai.com/account/api-keys)."
)

# ---- API 키 처리 ----
openai_api_key = st.secrets.get("OPENAI_API_KEY", None)
if not openai_api_key:
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
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

    # ================= 사이드바: 사양 조건 필터 =================
    with st.sidebar:
        st.header("🔍 사양 조건으로 찾기")

        screen_opts = sorted({item["screen"] for item in LAPTOP_DB})
        cpu_opts = sorted({item["cpu_tier"] for item in LAPTOP_DB})
        ram_opts = sorted({r for item in LAPTOP_DB for r in item["ram"]})
        storage_opts = sorted({s for item in LAPTOP_DB for s in item["storage"]})
        os_opts = sorted({item["os"] for item in LAPTOP_DB})
        weight_min = min(item["weight"] for item in LAPTOP_DB)
        weight_max = max(item["weight"] for item in LAPTOP_DB)
        price_min = min(item["price"] for item in LAPTOP_DB)
        price_max = max(item["price"] for item in LAPTOP_DB)

        sel_screen = st.multiselect("화면크기대 (인치)", screen_opts, placeholder="전체")
        sel_cpu = st.multiselect(
            "CPU (인텔 코어 울트라5 이상 / AMD 라이젠AI5 이상)",
            cpu_opts, placeholder="전체",
        )
        sel_ram = st.multiselect("램 용량 (GB)", ram_opts, placeholder="전체")
        sel_storage = st.multiselect("저장 용량대 (GB)", storage_opts, placeholder="전체")
        sel_os = st.multiselect("운영체제", os_opts, placeholder="전체")
        sel_weight = st.slider(
            "무게 (kg)", min_value=float(weight_min), max_value=float(weight_max),
            value=(float(weight_min), float(weight_max)), step=0.01,
        )
        sel_price = st.slider(
            "가격 (원)", min_value=int(price_min), max_value=int(price_max),
            value=(int(price_min), int(price_max)), step=50000,
        )

        st.divider()
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # ---- 필터링 ----
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

    filtered = [item for item in LAPTOP_DB if matches(item)]

    # ================= 메인 화면: 조건에 맞는 노트북 목록 =================
    st.subheader(f"📋 조건에 맞는 노트북 ({len(filtered)}개)")

    if not filtered:
        st.warning("조건에 맞는 노트북이 없습니다. 필터 조건을 완화해보세요.")
    else:
        table_rows = [
            {
                "브랜드": it["brand"],
                "모델": it["model"],
                "화면크기": f'{it["screen"]}인치',
                "CPU": it["cpu_detail"],
                "RAM": " / ".join(f"{r}GB" for r in it["ram"]),
                "저장공간": " / ".join(f"{s}GB" for s in it["storage"]),
                "OS": it["os"],
                "무게": f'{it["weight"]}kg',
                "가격": f'{it["price"]:,}원',
            }
            for it in filtered
        ]
        st.dataframe(table_rows, use_container_width=True, hide_index=True)

        options = [f'{it["brand"]} {it["model"]}' for it in filtered]
        picked = st.multiselect(
            "비교할 노트북을 정확히 2개 선택하세요",
            options=options,
            max_selections=2,
        )
        compare_clicked = st.button("📊 선택한 2개 비교분석 요청", type="primary", disabled=len(picked) != 2)

    # ---- 세션 상태 초기화 ----
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ---- 비교 요청 시 자동 프롬프트 생성 ----
    if filtered and "compare_clicked" in dir() and compare_clicked and len(picked) == 2:
        selected_items = [it for it in filtered if f'{it["brand"]} {it["model"]}' in picked]
        spec_lines = []
        for it in selected_items:
            spec_lines.append(
                f'- {it["brand"]} {it["model"]}: 화면 {it["screen"]}인치, CPU {it["cpu_detail"]}, '
                f'RAM {"/".join(f"{r}GB" for r in it["ram"])}, 저장공간 {"/".join(f"{s}GB" for s in it["storage"])}, '
                f'{it["os"]}, 무게 {it["weight"]}kg, 가격 {it["price"]:,}원'
            )
        auto_prompt = "다음 두 노트북을 비교분석해줘.\n" + "\n".join(spec_lines)
        st.session_state.messages.append({"role": "user", "content": auto_prompt})

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
            model="gpt-4o-mini",
            messages=api_messages,
            stream=True,
        )
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    if (
        filtered and "compare_clicked" in dir() and compare_clicked and len(picked) == 2
        and st.session_state.messages
        and st.session_state.messages[-1]["role"] == "user"
    ):
        generate_response()

    # ---- 채팅 입력창 (자유 질문도 가능) ----
    if prompt := st.chat_input("노트북 관련 질문을 자유롭게 입력하세요"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        generate_response()
