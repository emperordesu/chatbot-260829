import streamlit as st
from openai import OpenAI

# ---- 페이지 설정 ----
st.set_page_config(page_title="💻 노트북 비교분석 챗봇", page_icon="💻")

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

    # ---- 사이드바: 빠른 비교 입력 ----
    with st.sidebar:
        st.header("⚡ 빠른 비교")
        st.caption("비교할 노트북 모델을 입력하면 바로 분석해드립니다.")
        laptop_a = st.text_input("노트북 A", placeholder="예: LG 그램 17")
        laptop_b = st.text_input("노트북 B", placeholder="예: 맥북 에어 M3")
        laptop_c = st.text_input("노트북 C (선택)", placeholder="예: 삼성 갤럭시북4 프로")
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
        models = [m for m in [laptop_a, laptop_b, laptop_c] if m.strip()]
        if len(models) < 2:
            st.sidebar.warning("최소 2개 이상의 노트북 모델을 입력해주세요.")
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
