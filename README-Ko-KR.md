<p align="center"><img src="./cover.png" width="100%" /></p>

<h1 align="center">autoconference-skill</h1>
<p align="center">
  <em>자율 연구자들이 경쟁하고, 협력하며, 돌파구를 합성하는 컨퍼런스를 생성합니다.</em>
</p>
<p align="center">
  <a href="#commands">Commands</a> · <a href="#언제-사용하는가">언제 사용하는가</a> · <a href="#빠른-시작">빠른 시작</a> · <a href="#작동-방식">작동 방식</a> · <a href="#템플릿">템플릿</a> · <a href="#guide">Guide</a> · <a href="./README.md">English</a>
</p>
<p align="center">
  <img src="https://img.shields.io/github/stars/wjgoarxiv/autoconference-skill?style=social" />
  <img src="https://img.shields.io/badge/license-MIT-blue" />
  <img src="https://img.shields.io/badge/python-3.8+-green" />
  <img src="https://img.shields.io/badge/version-2.0.0-orange" />
  <img src="https://img.shields.io/badge/skill-Claude%20Code%20%7C%20Codex%20%7C%20OpenCode%20%7C%20Gemini-blueviolet" />
</p>

---

> [!NOTE]
> N개의 병렬 autoresearch 에이전트를 구조화된 컨퍼런스 라운드로 조율하는 Claude Code 스킬입니다 -- 적대적 동료 검토와 교차 연구자 합성을 포함합니다. 연구 목표를 정의하는 `conference.md`를 작성하면 컨퍼런스가 가설 생성, 실험, 평가, 다중 에이전트 반복을 처리합니다. [autoresearch-skill](https://github.com/wjgoarxiv/autoresearch-skill) 기반. Claude Code, Codex CLI, Gemini CLI에서 작동합니다.

### 예시: sII 수화물 + 물 .gro 파일 생성

| 라운드 1 (초기) | 최종 (수렴) |
|:---:|:---:|
| ![라운드 1](./examples/sii-hydrate-generation/snapshot_round1.png) | ![최종](./examples/sii-hydrate-generation/snapshot_final.png) |
| 복합 점수: 34.5 — 슬랩 내 물 존재 | 복합 점수: 99.9 — 깨끗한 분리 |

| 수렴 곡선 | 세부 지표 |
|:---:|:---:|
| ![수렴](./examples/sii-hydrate-generation/plot_composite_convergence.png) | ![세부](./examples/sii-hydrate-generation/plot_submetric_breakdown.png) |

> 3명의 연구자가 3라운드에 걸쳐 33회 반복. 컨퍼런스가 결정 구조 보존과 수화물 슬랩에서의 물 배제를 학습합니다. [전체 예시 보기 →](./examples/sii-hydrate-generation/)

## Commands

autoconference v2.0은 서브커맨드 아키텍처를 통해 7개의 커맨드를 제공합니다:

| Command | 설명 | 사용 사례 |
|---------|------|-----------|
| `/autoconference` | 핵심 컨퍼런스 루프 | N명의 연구자를 동료 검토가 포함된 구조화된 라운드로 진행 |
| `/autoconference:plan` | 8단계 설정 마법사 | dry-run 평가자 게이트와 함께 `conference.md`를 인터랙티브하게 생성 |
| `/autoconference:resume` | 체크포인트 복구 | 마지막으로 완료된 단계부터 중단된 컨퍼런스 재개 |
| `/autoconference:analyze` | 컨퍼런스 후 분석 | 인사이트, 실패 패턴, 전이 가능한 학습 내용 추출 |
| `/autoconference:debate` | 적대적 토론 | Opus 판사를 둔 2인 연구자 찬반 형식 |
| `/autoconference:survey` | 문헌 조사 | 인용 체인을 추적하는 다중 데이터베이스 체계적 리뷰 |
| `/autoconference:ship` | 결과 배포 | 결과물을 출판 형식으로 포맷하는 8단계 파이프라인 |

**Command chaining:**
```
plan ──> autoconference ──> ship              (표준 파이프라인)
plan ──> autoconference ──> analyze ──> ship  (사후 분석 포함)
debate ──> autoconference                     (토론 기반 실험)
survey ──> autoconference                     (문헌 기반 실험)
resume ──> autoconference                     (이어서 진행)
```

## 주요 기능

- **다중 에이전트 오케스트레이션** -- N명의 연구자가 검색 공간의 서로 다른 부분을 병렬로 탐색하고 각 라운드 후 발견 사항을 공유합니다.
- **적대적 동료 검토** -- Opus 기반 리뷰어 에이전트가 각 라운드마다 주장을 검증하여 결과가 전파되기 전 과적합 및 측정 노이즈를 포착합니다.
- **선택이 아닌 합성** -- 최종 결과물이 단순히 승자를 선택하는 것이 아니라 여러 연구자의 상호 보완적 인사이트를 결합합니다.
- **이중 모드** -- 수치 최적화를 위한 Metric 모드, 문헌 리뷰 및 가설 생성을 위한 Qualitative 모드.
- **7개 Subcommands** -- Plan, run, resume, analyze, debate, survey, ship — 완전한 연구 파이프라인으로 체이닝 가능.
- **Guard Parameters** -- 위반 시 지표 개선 여부와 관계없이 복구를 강제하는 컨퍼런스 수준 안전 제약 조건.
- **자동 수렴** -- 정체, 예산 소진, 정지를 감지하고 자동으로 최종 합성을 트리거합니다.
- **Crash Recovery** -- 중단된 컨퍼런스를 위한 5가지 복구 매트릭스 (mid-research, mid-poster, mid-review, mid-transfer, pre-synthesis).
- **완전한 감사 추적** -- 연구자별 로그, 포스터 세션, 동료 검토, 컨퍼런스 수준 TSV, JSONL 이벤트 스트림.
- **autoresearch-skill 기반** -- 각 연구자가 검증된 5단계 실험-평가-반복 루프를 실행합니다.
- **내장 안전 기능** -- 최대 반복 횟수, 시간 예산, 연구자 타임아웃, 금지 변경 경계, 자동 롤백.

## 언제 사용하는가

Autoconference는 [autoresearch-skill](https://github.com/wjgoarxiv/autoresearch-skill)의 단일 에이전트 루프 위에 병렬 탐색, 적대적 검증, 교차 연구자 합성을 올린 것입니다. 한 에이전트가 순차적으로 탐색하는 것으로 부족할 때 -- 검색 공간이 너무 넓거나, 자기 평가만으로는 신뢰할 수 없을 때 사용합니다.

### autoconference vs 대안

|  | autoresearch-skill | 에이전트 하네스 모드 (team, /batch, ouroboros 등) | autoconference |
|:---|:---|:---|:---|
| **에이전트 수** | 1 | N, 각각 다른 서브태스크 | N, 같은 문제에 다른 전략 |
| **탐색 방식** | 순차적 전략 전환 | 독립적 서브태스크 분할 | 검색 공간 파티셔닝 + 라운드간 지식 전달 |
| **검증** | 기계적 평가자 또는 에이전트 자기 판단 | 빌드/테스트 통과 | Opus 적대적 리뷰어 (과적합, 노이즈, 부당 주장 검출) |
| **결과 통합** | 최선 결과 하나 | 서브태스크별 결과 병합 | 합성 — 상호 보완적 인사이트 결합, 단순 선택이 아님 |
| **라운드 구조** | 없음 (연속 반복) | 없음 (일회성 분배) | 라운드별 포스터 세션 → 피어 리뷰 → 지식 전달 |

### autoconference를 선택할 때

- **검색 공간이 넓어서 파티셔닝이 가능할 때** — N명의 연구자가 서로 다른 영역을 병렬로 탐색하면 한 에이전트가 순차적으로 전략을 바꾸는 것보다 넓게 커버합니다
- **자기 평가에 사각지대가 있을 때** — 적대적 리뷰어(Opus)가 과적합, 측정 노이즈, Goodhart's Law 효과를 잡아냅니다
- **선택이 아닌 합성이 필요할 때** — 최종 결과물이 여러 접근법의 보완적 발견을 결합해야 할 때
- **정성적 연구**(문헌 종합, 가설 생성)에서 다각도 관점이 하나의 분류 체계로 수렴해야 할 때

### autoresearch-skill을 대신 사용할 때

- 검색 공간이 **한 에이전트로 충분히** 커버 가능할 때
- **기계적 평가자**가 있어 유지/복원 판단에 외부 검증이 불필요할 때
- **토큰 비용이 중요할 때** — autoconference는 라운드당 N명의 연구자 + 리뷰어 + 합성기를 실행하여, 단일 autoresearch 대비 대략 N+2배의 비용이 듭니다

## 빠른 시작

### 1. 복사-붙여넣기 설치

> [!TIP]
> 아래 블록을 Claude Code에 직접 붙여넣으세요. 저장소를 클론하고, 스킬을 설치하며, 설정을 한 번에 검증합니다.

```
I want to install the autoconference-skill. Do these steps:
1. git clone https://github.com/wjgoarxiv/autoconference-skill.git /tmp/autoconference-skill
2. mkdir -p ~/.claude/skills/autoconference-skill && cp -r /tmp/autoconference-skill/SKILL.md /tmp/autoconference-skill/scripts /tmp/autoconference-skill/assets /tmp/autoconference-skill/references ~/.claude/skills/autoconference-skill/
3. Test: python ~/.claude/skills/autoconference-skill/scripts/init_conference.py --goal "test" --metric "score" --direction minimize --researchers 2 --output /tmp/test-conference && echo "OK: autoconference-skill installed"
4. Say "autoconference-skill installed successfully"
```

### 2. 수동 설치

```bash
git clone https://github.com/wjgoarxiv/autoconference-skill.git
cd autoconference-skill

# 스킬 디렉토리에 심볼릭 링크 생성
mkdir -p ~/.claude/skills
ln -s "$(pwd)" ~/.claude/skills/autoconference-skill
```

### 3. 기타 도구

| 도구 | 설치 커맨드 |
|------|-------------|
| Claude Code | 위의 복사-붙여넣기 블록 사용 또는 수동 설치 |
| Codex CLI | `SKILL.md`를 Codex instructions 디렉토리에 복사 |
| Gemini CLI | `SKILL.md`를 Gemini context 디렉토리에 복사 |

### 다른 플랫폼

| 플랫폼 | Skills 경로 | 설치 커맨드 |
|--------|-------------|-------------|
| **Claude Code** | `~/.claude/skills/autoconference-skill/` | 위 참조 |
| **Codex CLI** | `~/.codex/skills/autoconference-skill/` | `mkdir -p ~/.codex/skills && ln -s "$(pwd)" ~/.codex/skills/autoconference-skill` |
| **OpenCode** | `~/.config/opencode/skills/autoconference-skill/` | `mkdir -p ~/.config/opencode/skills && ln -s "$(pwd)" ~/.config/opencode/skills/autoconference-skill` |
| **Gemini CLI** | `~/.gemini/skills/autoconference-skill/` | `mkdir -p ~/.gemini/skills && ln -s "$(pwd)" ~/.gemini/skills/autoconference-skill` |

## 사용법

### 프롬프트 최적화 토너먼트

세 명의 연구자가 프롬프트 정확도를 두고 경쟁합니다 — 각각 지시 표현, few-shot 선택, chain-of-thought 포맷에 특화됩니다.

```
Run an autoconference using templates/prompt-optimization.md.
Goal: maximize accuracy on my classification benchmark.
3 researchers, 3 rounds.
```

### 코드 성능 경쟁

알고리즘, 자료구조, 저수준 연구자가 동일한 코드베이스를 독립적으로 최적화한 후 각 라운드마다 검증된 성과를 교차 적용합니다.

```
Run an autoconference using templates/code-performance.md.
Metric: wall-clock time on my benchmark suite.
Direction: minimize. Target: < 200ms.
```

### 문헌 합성 컨퍼런스

Qualitative 모드. 세 명의 연구자가 기초, 최신, 교차 도메인 관점에서 동일한 주제를 조사한 후 통합 분류 체계를 합성합니다.

```
Run an autoconference in qualitative mode.
Goal: survey LLM agent papers from 2022-2025.
3 researchers, 2 rounds. Synthesize findings into a taxonomy.
```

### 새 컨퍼런스 스캐폴드 생성

```bash
python scripts/init_conference.py \
  --goal "Optimize inference latency" \
  --metric "p95_latency_ms" \
  --direction minimize \
  --target "< 50" \
  --researchers 3 \
  --strategy assigned \
  --output ./latency-conference/
```

생성된 `conference.md`의 `Current Approach`, `Search Space`, 연구자 집중 영역을 채워 넣으세요. 준비가 되면:

```
Run the autoconference on my conference.md
```

Claude가 `SKILL.md`를 로드하고, `conference.md`를 읽은 후, 모든 라운드, 동료 검토, 최종 합성을 포함한 전체 컨퍼런스를 오케스트레이션합니다.

## 작동 방식

```
+----------------------------------------------------------+
|                     CONFERENCE ROUND                     |
|                                                          |
|  Phase 1: INDEPENDENT RESEARCH (parallel)               |
|  +----------+  +----------+  +----------+               |
|  |Researcher|  |Researcher|  |Researcher|  Each runs N  |
|  |    A     |  |    B     |  |    C     |  autoresearch |
|  | (iter x N)|  | (iter x N)|  | (iter x N)|  iterations |
|  +----+-----+  +----+-----+  +----+-----+               |
|       |              |             |                     |
|  Phase 2: POSTER SESSION                                 |
|  +----------------------------------------------+       |
|  | Session Chair collects all logs,             |       |
|  | surfaces key findings & deltas               |       |
|  +----------------------+-----------------------+       |
|                         |                               |
|  Phase 3: PEER REVIEW (adversarial)                     |
|  +----------------------------------------------+       |
|  | Reviewer agent challenges claims:            |       |
|  | - "Did metric actually improve?"             |       |
|  | - "Is this overfitting?"                     |       |
|  | - "Could this be measurement noise?"         |       |
|  +----------------------+-----------------------+       |
|                         |                               |
|  Phase 4: KNOWLEDGE TRANSFER                            |
|  +----------------------------------------------+       |
|  | Validated findings shared back to            |       |
|  | all researchers for next round               |       |
|  +----------------------------------------------+       |
|                                                          |
+----------------------------------------------------------+
          |
          v  수렴 확인 -> 다음 라운드 또는 최종 합성
```

## `conference.md` 형식

| 섹션 | 용도 |
|------|------|
| `Goal` | 컨퍼런스가 달성해야 할 목표 |
| `Mode` | `metric` (수치 최적화) 또는 `qualitative` (추론 품질) |
| `Success Metric` | 지표 이름, 목표값, 방향 (metric 모드 전용) |
| `Success Criteria` | "좋음"에 대한 자연어 설명 (qualitative 모드 전용) |
| `Researchers` | 연구자 수, 라운드당 반복 횟수, 최대 라운드 수 |
| `Search Space` | 연구자가 수정할 수 있는 것과 없는 것 |
| `Search Space Partitioning` | `assigned` (각 연구자에게 집중 영역 지정) 또는 `free` (중복 허용) |
| `Constraints` | 최대 반복 횟수, 시간 예산, 연구자 타임아웃 |
| `Current Approach` | 기준선 설명 |
| `Shared Knowledge` | 각 라운드 후 검증된 발견 사항으로 자동 채워짐 |
| `Conference Log` | 라운드별 히스토리가 자동으로 유지됨 |

전체 템플릿은 `assets/conference_template.md`를 참조하세요.

## 에이전트 역할

| 역할 | 모델 | 수 | 책임 |
|------|------|----|------|
| **컨퍼런스 의장 (Conference Chair)** | Sonnet | 1 | 오케스트레이터 — 라운드 관리, 연구자 생성, 수렴 감지, 합성 트리거 |
| **연구자 (Researcher)** | Sonnet | N | 할당된 탐색 공간 내에서 autoresearch 5단계 루프 실행 |
| **세션 의장 (Session Chair)** | Haiku | 1 | 경량 요약기 — 로그 수집 및 각 라운드 후 포스터 세션 요약 생성 |
| **리뷰어 (Reviewer)** | Opus | 1 | 적대적 비평가 — 주장 검증, 과적합/노이즈 확인, 판정 부여 |
| **합성기 (Synthesizer)** | Opus | 1 | 최종 한 번 실행 — 모든 연구자의 상호 보완적 인사이트를 결합 |

## 템플릿

일반적인 작업에 바로 사용 가능한 `conference.md` 설정:

| 템플릿 | 모드 | 사용 사례 |
|--------|------|-----------|
| `templates/quick-conference.md` | metric | 연구자 2명, 2라운드 — 컨퍼런스 형식이 문제에 적합한지 테스트 |
| `templates/prompt-optimization.md` | metric | 3명의 전문 연구자를 통한 LLM 프롬프트 정확도 최적화 |
| `templates/code-performance.md` | metric | 알고리즘, 자료구조, 저수준 연구자를 통한 코드 속도 최적화 |
| `templates/research-synthesis.md` | qualitative | 기초, 최신, 교차 도메인 관점에서의 문헌 탐색 |
| `templates/debate-mode.md` | qualitative | 구조화된 라운드와 Opus 판사가 포함된 2인 연구자 적대적 토론 |
| `templates/survey-mode.md` | qualitative | 인용 체인 추적이 포함된 다중 데이터베이스 문헌 조사 |

## 설정 옵션

| 필드 | 기본값 | 설명 |
|------|--------|------|
| `mode` | `metric` | `metric` 또는 `qualitative` |
| `count` | — | 연구자 에이전트 수 |
| `iterations_per_round` | 5 | 라운드당 각 연구자가 실행하는 autoresearch 반복 횟수 |
| `max_rounds` | 4 | 강제 합성 전 최대 컨퍼런스 라운드 수 |
| `max_total_iterations` | — | 모든 연구자와 라운드에 걸친 하드 상한 |
| `time_budget` | — | 전체 컨퍼런스의 벽시계 시간 제한 |
| `researcher_timeout` | — | 라운드당 연구자별 타임아웃 |
| `strategy` | `free` | `assigned` (집중 영역) 또는 `free` (자유 탐색) |
| `guard` | — | 모든 연구자에게 적용되는 안전 제약 조건 (위반 시 지표 개선 여부와 관계없이 복구) |
| `noise_runs` | 1 | 노이즈 감소를 위해 평균화할 반복 평가 횟수 |
| `min_consensus_delta` | 0 | 다음 라운드 진행을 위한 유지된 연구자들의 최소 평균 개선치 |

## 출력 파일

| 파일 | 용도 |
|------|------|
| `conference.md` | 사용자 설정 (각 라운드마다 로그 항목이 업데이트됨) |
| `conference_results.tsv` | 모든 반복 및 동료 검토 판정이 포함된 마스터 컨퍼런스 수준 TSV |
| `researcher_A_log.md` | 연구자별 상세 반복 로그 |
| `researcher_A_results.tsv` | 연구자별 TSV (autoresearch와 동일한 형식) |
| `poster_session_round_N.md` | 각 라운드의 세션 의장 요약 |
| `peer_review_round_N.md` | 각 라운드의 리뷰어 판정 |
| `synthesis.md` | 합성기의 최종 합성 결과물 |
| `final_report.md` | 전체 컨퍼런스 히스토리가 포함된 요약 보고서 |

## 야간 실행

컨퍼런스를 야간에 실행하려면 범용 루프 스크립트를 사용하세요:

```bash
# 옵션 A: 포그라운드 (가장 간단)
bash scripts/autoconference-loop.sh ./my-conference/

# 옵션 B: nohup으로 백그라운드 실행 (tmux 불필요)
nohup bash scripts/autoconference-loop.sh ./my-conference/ > conference.log 2>&1 &

# 옵션 C: tmux로 백그라운드 실행 (최적의 경험)
tmux new-session -d -s conference 'bash scripts/autoconference-loop.sh ./my-conference/'

# 언제든지 진행 상황 확인
bash scripts/check_conference.sh ./my-conference/
```

이 스크립트는 CLI 도구를 자동으로 감지하고, 라운드 재시작을 처리하며, 컨퍼런스 완료 여부를 확인합니다. Claude Code, Codex CLI, OpenCode, Gemini CLI에서 작동합니다.

## autoresearch-skill과의 관계

컨퍼런스의 각 연구자는 **autoresearch 루프** — [autoresearch-skill](https://github.com/wjgoarxiv/autoresearch-skill)의 동일한 자율 실험-평가-반복 사이클 — 을 실행합니다. Autoconference는 그 위에 세 가지 레이어를 추가합니다:

1. **다중 에이전트 오케스트레이션** — N명의 연구자가 탐색 공간의 서로 다른 부분을 병렬로 탐색한 후 발견을 공유합니다
2. **적대적 동료 검토** — 리뷰어 에이전트가 각 라운드마다 발견 사항을 검증합니다 (자기 평가로는 놓칠 수 있는 것을 포착)
3. **합성** — 합성기가 단순히 최선의 결과를 선택하는 것이 아니라 상호 보완적인 인사이트를 결합합니다

탐색 공간이 단일 집중 연구 루프에 적합하다면 autoresearch-skill을 사용하세요. 탐색 공간이 충분히 커서 분할이 가능하거나, 접근 방식의 다양성이 중요하거나, 결과의 외부 검증이 필요할 때는 autoconference를 사용하세요.

## Guide

포괄적인 문서는 `guide/` 디렉토리에서 제공됩니다:

| Guide | 주제 |
|-------|------|
| [Getting Started](guide/getting-started.md) | 60초 빠른 시작 + 도메인 치트 시트 |
| [Core Conference](guide/autoconference.md) | 4단계 라운드 구조, 수렴, 야간 실행 |
| [Plan](guide/plan.md) | 8단계 설정 마법사 |
| [Resume](guide/resume.md) | 체크포인트 복구 |
| [Analyze](guide/analyze.md) | 컨퍼런스 후 인사이트 추출 |
| [Debate](guide/debate.md) | 적대적 2인 연구자 형식 |
| [Survey](guide/survey.md) | 다중 데이터베이스 문헌 조사 |
| [Ship](guide/ship.md) | 컨퍼런스 결과를 출판 형식으로 |
| [Chains](guide/chains-and-combinations.md) | 커맨드 체이닝 패턴 |
| [Advanced](guide/advanced-patterns.md) | Guard, 노이즈, worktree, CI/CD |
| [Troubleshooting](guide/troubleshooting.md) | 일반적인 실패 패턴 및 해결 방법 |

참고: [COMPARISON.md](./COMPARISON.md) — autoconference vs 대안 비교.

## 크로스 플랫폼 호환성

| 플랫폼 | 상태 | 설치 |
|--------|------|------|
| Claude Code | Ready | 플러그인 설치 또는 수동 심볼릭 링크 |
| Codex CLI | Ready | `.codex/INSTALL.md` 참조 |
| OpenCode | Ready | `.opencode/INSTALL.md` 참조 |
| Gemini CLI | Ready | `gemini-extension.json` 자동 검색 사용 |

## 요구사항

| 요구사항 | 상세 |
|----------|------|
| **Python** | 3.8+ (표준 라이브러리만 사용 — `scripts/init_conference.py` 전용) |
| **LLM CLI** | 서브에이전트 지원이 있는 모든 CLI (Claude Code, Codex CLI, OpenCode, Gemini CLI) |
| **autoresearch-skill** | 각 연구자 에이전트 프롬프트에서 참조됨 |

## 기여

자세한 가이드라인은 [CONTRIBUTING.md](./CONTRIBUTING.md)를 참조하세요.

1. 저장소를 Fork 하세요
2. Feature 브랜치를 생성하세요 (`git checkout -b feature/your-feature`)
3. 변경 사항을 커밋하세요 (`git commit -m 'Add your feature'`)
4. 브랜치에 Push 하세요 (`git push origin feature/your-feature`)
5. Pull Request를 여세요

## 라이선스

MIT — 자세한 내용은 [LICENSE](./LICENSE)를 참조하세요.
