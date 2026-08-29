import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# ---- 페이지 설정 ----
st.set_page_config(page_title="수업 못 들었어요? 제가 알려줄게요", page_icon="🎬", layout="wide")

# ---- 테마 CSS (보라/틸 톤) ----
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    }
    section[data-testid="stSidebar"] * { color: #ede9fe !important; }
    section[data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        width: 100%;
        display: flex;
        justify-content: flex-start !important;
        text-align: left !important;
    }
    section[data-testid="stSidebar"] .stButton button p {
        text-align: left !important;
        width: 100%;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.16);
        border-color: #a78bfa;
    }
    .cat-header {
        font-size: 22px; font-weight: 800; color: #312e81;
        margin-bottom: 4px;
    }
    .cat-time {
        display: inline-block; background: #ede9fe; color: #6d28d9;
        font-weight: 700; font-size: 13px; padding: 3px 10px;
        border-radius: 999px; margin-bottom: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Vimeo 영상 정보 ----
VIMEO_VIDEO_ID = "1221651006"
VIMEO_HASH = "ecf1d87214"

# ---- 카테고리 데이터 (영상 흐름 순서대로) ----
CATEGORIES = [
    {
        "icon": "📚", "title": "커리큘럼 소개", "start_seconds": 0,
        "time_label": "00:00:00",
        "summary": """
수업 시작과 함께 화면·음성이 잘 전달되는지 확인하고, **Discord를 이번 과정의 공식 소통 채널**로 지정합니다. 이해도 체크는 이해했으면 **O**, 애매하면 **물음표(?)**, 잘 모르겠으면 **X**로 표시하는 방식이며, 아직 가입·체크를 완료하지 못한 수강생이 많아 1교시 안에 완료해달라고 당부합니다. 설치·세팅이 어려운 경우 1교시 이후 20~30분간 원격으로 개별 지원하겠다고 안내합니다.

이어서 커리큘럼을 소개합니다.

- 총 **160시간** 과정이며, 사전에 공유된 커리큘럼은 확정본이 아니라 초안이라는 점을 분명히 합니다. 실제 진도는 수강생들의 이해 속도에 맞춰 유동적으로 조절됩니다.
- 학습 순서는 기본 개념(터미널 사용, 파일 구조 등)을 먼저 다진 뒤, AI 기능을 점진적으로 얹어가는 방식으로 설계되어 있습니다.
- 왕초보 수강생을 배려해 사전에 Claude Code로 직접 제작한 학습 자료를 준비했다고 소개하며, 오리엔테이션 동안 관련 체크리스트를 함께 완료해나갈 것을 권장합니다.
""",
    },
    {
        "icon": "🛠️", "title": "필요 도구 준비", "start_seconds": 511,
        "time_label": "00:08:31",
        "summary": """
수업에 필요한 계정과 도구는 다음과 같습니다. 가입 링크를 눌러 미리 준비해두세요.

**필수**
| 도구 | 용도 | 가입/설치 링크 |
|---|---|---|
| ChatGPT | AI 서비스 | [chat.openai.com](https://chat.openai.com) |
| Claude | AI 서비스 | [claude.ai](https://claude.ai) |
| Google Gemini | AI 서비스 | [gemini.google.com](https://gemini.google.com) |
| GitHub | 코드 저장·배포 | [github.com/join](https://github.com/join) |
| Notion | 문서·자료 정리 | [notion.so](https://www.notion.so/ko-kr) |

**선택사항**
| 도구 | 비고 | 링크 |
|---|---|---|
| Qwen | 중국계 AI. 정부 통제로 인한 개인정보 이슈가 있어 신경 쓰이면 사용하지 않아도 됩니다 | [chat.qwen.ai](https://chat.qwen.ai) |

강사는 한 가지 AI 서비스만 고집하지 말고 상황에 따라 비교해가며 사용해볼 것을 권장하며, 본인도 Claude Code와 Claude, 가끔 Gemini까지 병행해서 쓴다고 언급합니다.
""",
    },
    {
        "icon": "💻", "title": "터미널 · VS Code 설치", "start_seconds": 8141,
        "time_label": "02:15:41",
        "summary": """
이 구간은 영상 내용 요약이 아니라, **터미널과 VS Code를 실제로 설치하는 방법**을 별도로 정리한 안내입니다.

**1) 터미널 준비**
- **Windows**: Windows 11에는 Windows Terminal이 기본 내장되어 있습니다. Windows 10이라면 Microsoft Store에서 "Windows Terminal"을 검색해 설치하거나, PowerShell에서 아래 명령으로 설치할 수 있습니다.
  ```powershell
  winget install Microsoft.WindowsTerminal
  ```
- **Mac**: 별도 설치가 필요 없습니다. `Finder → 응용 프로그램 → 유틸리티 → 터미널`에서 바로 열 수 있습니다.

**2) VS Code 설치**
1. 공식 다운로드 페이지 접속: **[code.visualstudio.com/download](https://code.visualstudio.com/download)**
2. 사용 중인 OS에 맞는 설치 파일 다운로드 (Windows: `.exe` / Mac: `.zip`)
3. 설치 파일 실행 — **Windows에서는 설치 중 "PATH에 추가" 옵션을 반드시 체크**해야 터미널에서 `code` 명령으로 바로 실행할 수 있습니다.
4. 설치 완료 후 터미널(또는 CMD)에 아래 명령을 입력해 정상 설치를 확인합니다.
   ```bash
   code --version
   ```
   버전 정보가 출력되면 설치가 완료된 것입니다.
""",
    },
    {
        "icon": "🤖", "title": "Claude Code 설치 & 실습", "start_seconds": 10709,
        "time_label": "02:58:29",
        "summary": """
Node.js와 Claude Code를 설치하고, 첫 실습(간단한 웹페이지 만들기)까지 진행하는 구간입니다. Windows와 Mac 환경을 번갈아 시연하며, 최근에는 Node.js 없이 Claude Code만 단독 설치하는 방법도 생겼다는 점을 언급합니다.

첨부해주신 Windows 설치 가이드 기준으로 핵심을 정리하면 다음과 같습니다.

**왜 Node.js가 필요한가**
Claude Code는 원래 npm(자바스크립트 패키지 관리자)을 통해 배포되던 도구라, npm으로 설치하려면 Node.js가 필요합니다. 다만 최근에는 Node.js 없이 실행 파일만 받아 바로 쓰는 **네이티브 설치** 방식도 공식 지원됩니다. 두 방식 모두 결국 실행되는 건 동일한 실행 파일(binary)이며, npm은 그것을 받아오는 방법 중 하나일 뿐입니다.

**1) Node.js 설치 (Windows, PowerShell)**
```powershell
winget install OpenJS.NodeJS.LTS
```
설치 후 PowerShell을 재시작해야 PATH가 반영됩니다. 아래 명령으로 설치를 확인합니다.
```powershell
node --version
npm --version
```
최신 Claude Code는 Node.js 22 이상을 요구합니다.

**2) PowerShell 실행 정책 오류 대처**
`npm --version` 실행 시 Windows 기본 실행 정책(Restricted)으로 스크립트 실행이 막히는 경우가 있습니다. 아래 명령으로 현재 계정 범위에서만 정책을 완화해 해결할 수 있습니다 (관리자 권한 불필요).
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
적용 후 터미널을 재시작해야 반영됩니다.

**3) Claude Code 설치**
- npm 방식: `npm install -g @anthropic-ai/claude-code`
- 네이티브 방식(권장): `irm https://claude.ai/install.ps1 | iex`

설치 후 `claude --version`으로 확인하고, 프로젝트 폴더에서 `claude` 명령으로 실행 및 인증을 진행합니다.

**실습**: 설치를 마친 수강생들은 실제로 간단한 웹페이지(예: 벽돌깨기 게임)를 Claude Code로 직접 만들어보는 시간을 갖습니다.
""",
    },
]

# ---- 세션 상태 초기화 ----
if "selected_cat" not in st.session_state:
    st.session_state.selected_cat = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= 사이드바: 카테고리 목록 (왼쪽 정렬, 시간 표시 없음) =================
with st.sidebar:
    st.markdown("## 🎬 강의 목차")
    st.caption("260826_2기 인공지능 특급")
    st.write("")
    for i, cat in enumerate(CATEGORIES):
        label = f'{cat["icon"]}  {cat["title"]}'
        if st.button(label, key=f"cat_{i}", use_container_width=True):
            st.session_state.selected_cat = i

# ================= 메인 화면 =================
st.title("수업 못 들었어요? 제가 알려줄게요")

cat = CATEGORIES[st.session_state.selected_cat]

st.markdown(f'<div class="cat-header">{cat["icon"]} {cat["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<span class="cat-time">▶ {cat["time_label"]} 부터 자동 재생</span>', unsafe_allow_html=True)

# ---- Vimeo 임베드: Player SDK로 특정 시간부터 강제 seek + 재생 ----
# URL 프래그먼트(#t=)만으로는 이 환경에서 안정적으로 동작하지 않아,
# Vimeo Player JS SDK(player.setCurrentTime + player.play)로 직접 제어합니다.
player_html = f"""
<div style="border-radius:12px; overflow:hidden;">
  <iframe id="vimeo_player_{st.session_state.selected_cat}"
          src="https://player.vimeo.com/video/{VIMEO_VIDEO_ID}?h={VIMEO_HASH}&muted=1"
          width="100%" height="420" frameborder="0"
          allow="autoplay; fullscreen; picture-in-picture"
          allowfullscreen></iframe>
</div>
<script src="https://player.vimeo.com/api/player.js"></script>
<script>
  (function() {{
    var iframe = document.getElementById('vimeo_player_{st.session_state.selected_cat}');
    var player = new Vimeo.Player(iframe);
    player.ready().then(function() {{
      player.setCurrentTime({cat["start_seconds"]}).then(function() {{
        player.play();
      }});
    }});
  }})();
</script>
"""
components.html(player_html, height=440)
st.caption("🔇 자동재생은 브라우저 정책상 음소거로 시작됩니다. 플레이어의 음소거 버튼을 눌러 소리를 켜주세요.")

# ---- 핵심 요약 ----
with st.container(border=True):
    st.markdown("**📝 이 구간 핵심 요약**")
    st.markdown(cat["summary"])

st.divider()

# ================= 강의 내용 Q&A 챗봇 (스트리밍) =================
st.subheader("💬 강의 내용 물어보기")

openai_api_key = st.secrets.get("OPENAI_API_KEY", None)
if not openai_api_key:
    openai_api_key = st.text_input(
        "OpenAI API Key", type="password",
        help="secrets.toml에 키를 등록하면 이 입력창은 표시되지 않습니다.",
    )

if not openai_api_key:
    st.info("강의 내용에 대해 질문하려면 OpenAI API 키를 입력해주세요.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    all_summary_text = "\n\n".join(
        f'[{c["time_label"]} {c["title"]}]\n{c["summary"]}' for c in CATEGORIES
    )
    SYSTEM_PROMPT = (
        "당신은 '260826_2기 인공지능 특급' 강의 영상 내용에 대해 답변하는 도우미입니다. "
        "아래는 강의를 구간별로 정리한 상세 요약입니다. 이 정보를 바탕으로 사용자의 질문에 답하세요. "
        "설치 명령어를 물어보면 요약에 포함된 코드를 정확히 안내하세요. "
        "요약에 없는 세부 내용은 추측하지 말고 모른다고 답하세요.\n\n"
        f"{all_summary_text}"
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("예: Claude Code 설치는 어떻게 진행됐나요?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]
        stream = client.chat.completions.create(
            model="gpt-4o-mini", messages=api_messages, stream=True,
        )
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
