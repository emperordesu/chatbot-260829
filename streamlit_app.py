import streamlit as st
from openai import OpenAI

# ---- 페이지 설정 ----
st.set_page_config(page_title="💻 노트북 비교분석 챗봇", page_icon="💻")

# ---- 브랜드별 2025년 이후 출시 모델 목록 ----
# 참고: 노트북 라인업은 자주 갱신되므로 최신 모델은 브랜드 공식 홈페이지에서 추가로 확인하는 것을 권장합니다.
LAPTOP_MODELS = {
    "삼성 (Samsung)": [
        "갤럭시북5 프로 (2025)",
        "갤럭시북5 프로 360 (2025)",
        "갤럭시북5 (2025)",
        "갤럭시북5 엣지 (2025)",
        "갤럭시북6 Pro (2026)",
        "갤럭시북6 Ultra (2026)",
        "갤럭시북6 (2026)",
    ],
    "LG (그램)": [
        "LG 그램 프로 (2025년형)",
        "LG 그램 프로 360 (2025년형)",
        "LG 그램 (2025년형)",
        "LG 그램북 (2025년형)",
        "LG 그램 프로 AI (2026년형, 16/17형)",
        "LG 그램 프로 360 AI (2026년형, 16형)",
        "LG 그램 AI (2026년형, 14/15형)",
        "LG 그램북 AI (2026년형, 15/16형)",
    ],
    "에이서 (Acer)": [
        "Acer Swift 14 AI (2025)",
        "Acer Swift 16 AI (2025)",
        "Acer Swift Go 16 AI (2026)",
        "Acer Aspire 16 (팬서레이크, 2026)",
        "Acer Aspire Lite 16 (2025)",
        "Acer Spin (2in1, 2025)",
        "Acer Nitro (게이밍, 2025~2026)",
        "Acer Predator (게이밍, 2025~2026)",
    ],
    "기타 브랜드 (직접 입력)": [],
}

# ---- 제목 및 설명 ----
st.title("💻 노트북 비교분석 챗봇")
st.write(
    "노트북 구매를 고민 중이신가요? 이 챗봇은 여러 노트북 모델의 사양, 성능, 가격대를 비교하고 "
    "사용 목적에 맞는 추천을 도와드립니다. "
    "사용하려면 OpenAI API 키가 필요합니다. [여기서 발급받으세요](https://platform.openai.com/account/api-keys)."
)

# ---- API 키 입력 ----
openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("계속하려면 OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    # ---- 시스템 프롬프트: 노트북 비교 전문가 역할 부여 ----
    SYSTEM_PROMPT = """당신은 노트북 구매를 도와주는 전문 컨설턴트입니다.
사용자가 비교하고 싶은 노트북 모델을 알려주면 다음 항목을 기준으로 비교분석해주세요:

1. 핵심 사양 (CPU, GPU, RAM, 저장공간, 디스플레이)
2. 성능 (게이밍, 영상편집, 일반 사무 등 용도별)
3. 배터리 사용시간 및 휴대성
4. 가격대 및 가성비
5. 장단점 요약
6. 사용자의 목적(예: 게이밍, 학습, 업무, 디자인 등)에 맞는 최종 추천

비교표 형식(마크다운 표)을 적극 활용하고, 정보가 불확실한 경우 반드시 그렇다고 밝혀주세요.
사용자가 아직 비교할 노트북을 알려주지 않았다면, 예산과 주 사용 목적을 먼저 물어봐서
적절한 추천을 할 수 있도록 대화를 이끌어주세요."""

    # ---- 사이드바: 브랜드/모델 선택 후 빠른 비교 ----
    with st.sidebar:
        st.header("⚡ 빠른 비교")
        st.caption("브랜드를 선택하면 2025년 이후 출시 모델이 표시됩니다. 여러 브랜드/모델을 함께 선택할 수 있어요.")

        selected_brands = st.multiselect(
            "브랜드 선택",
            options=list(LAPTOP_MODELS.keys()),
            placeholder="비교할 브랜드를 선택하세요",
        )

        # 선택된 브랜드에 속한 모델을 모두 모아 후보 목록 구성
        available_models = []
        for brand in selected_brands:
            available_models.extend(LAPTOP_MODELS[brand])

        selected_models = []
        if available_models:
            selected_models = st.multiselect(
                "모델 선택 (2개 이상)",
                options=available_models,
                placeholder="비교할 모델을 선택하세요",
            )

        # 기타 브랜드는 직접 입력
        custom_models_raw = ""
        if "기타 브랜드 (직접 입력)" in selected_brands:
            custom_models_raw = st.text_area(
                "기타 브랜드 모델 직접 입력 (쉼표로 구분)",
                placeholder="예: 에이수스 젠북 14, 맥북 에어 M4",
            )

        purpose = st.selectbox(
            "주 사용 목적",
            ["선택 안 함", "일반 사무/학습", "영상/사진 편집", "게이밍", "프로그래밍/개발", "휴대성 중시"],
        )
        compare_clicked = st.button("비교 분석 요청하기", use_container_width=True)

        st.divider()
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # ---- 세션 상태 초기화 ----
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ---- 사이드바 버튼 클릭 시 자동 프롬프트 생성 ----
    if compare_clicked:
        custom_models = [m.strip() for m in custom_models_raw.split(",") if m.strip()]
        models = selected_models + custom_models
        if len(models) < 2:
            st.sidebar.warning("최소 2개 이상의 노트북 모델을 선택(또는 입력)해주세요.")
        else:
            auto_prompt = f"다음 노트북들을 비교분석해줘: {', '.join(models)}."
            if purpose != "선택 안 함":
                auto_prompt += f" 주 사용 목적은 '{purpose}'이야."
            st.session_state.messages.append({"role": "user", "content": auto_prompt})

    # ---- 기존 대화 표시 ----
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ---- 응답 생성 함수 (중복 방지용) ----
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

    # ---- 사이드바에서 온 요청이면 바로 응답 생성 ----
    if compare_clicked and len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
        generate_response()

    # ---- 채팅 입력창 ----
    if prompt := st.chat_input("노트북 관련 질문을 입력하세요 (예: 게이밍용 노트북 추천해줘)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        generate_response()
