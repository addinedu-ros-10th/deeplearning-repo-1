-- =========================================================
-- 스키마 준비
-- =========================================================
CREATE SCHEMA IF NOT EXISTS notify;
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid()

-- updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION notify.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- ENUM 타입 정의 (의미/정렬 순서가 중요)
-- =========================================================

-- 1) 위기 단계(낮음→높음) : green < blue < yellow < orange < red
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='severity_enum') THEN
    CREATE TYPE notify.severity_enum AS ENUM ('green','blue','yellow','orange','red');
  END IF;
END $$;

COMMENT ON TYPE notify.severity_enum IS
$$
위기 5단계 ENUM.
정렬/비교는 정의 순서를 따름: green < blue < yellow < orange < red

- green(정상): 서비스 초기 2–4주 평균으로 개인 기준선 유지. 월간 기준선 리프레시, 계절 보정.
- blue(권고): 경미한 변동(알람 피로 방지). 주1–2회, 기준선 ±20% 내 이탈은 교육/안내 중심 대응.
- yellow(주의): 원인 탐색·생활 코칭·1주 재평가. 수면위생/활동/환경/약물 등 24 시나리오 점검.
- orange(고위험): 단기간 급격한 이탈(예: 야간배뇨 급증, PDC<80%, 활동 급감). 당일 전화확인/방문 검토.
- red(위급): 무반응·즉시 신고(119/911), 스피커폰 대기, long lie(1h 이상) 위험, 가족/보호자 동시 알림.
$$;

-- 2) 메시지 성격(또는 출처/용도)
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='kind_enum') THEN
    CREATE TYPE notify.kind_enum AS ENUM ('system','schedule','info','contact','marketing','inbound');
  END IF;
END $$;

COMMENT ON TYPE notify.kind_enum IS
$$
메시지 성격/용도.
- system: 시스템 공지/이상징후/안전경보(낙상 의심 등)
- schedule: 일정 알림(복약/진료/활동/방문 일정)
- info: 일반 정보성 알림(안내/업데이트)
- contact: 연락/콜백 요청(요양사/가족 연락)
- marketing: 프로모션/캠페인(동의 기반)
- inbound: 사용자/클라이언트 기원 메시지(문의/버튼응답/피드백)
$$;

-- 3) 전달 채널
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='channel_enum') THEN
    CREATE TYPE notify.channel_enum AS ENUM ('websocket','sse','push','email','sms','voice','kakao');
  END IF;
END $$;

COMMENT ON TYPE notify.channel_enum IS
$$
전달 채널.
- websocket: 실시간 양방향(대시보드/웹앱)
- sse: 서버→클라이언트 단방향 스트림
- push: 모바일 푸시(FCM/APNs)
- email: 이메일
- sms: 문자
- voice: 자동 통화/콜봇
- kakao: 카카오 채널/알림톡(정책 준수 필요)
$$;

-- 4) 딜리버리 상태(최소 셋)
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='delivery_status_enum') THEN
    CREATE TYPE notify.delivery_status_enum AS ENUM
      ('queued','sent','delivered','read','ack','failed','expired','canceled');
  END IF;
END $$;

COMMENT ON TYPE notify.delivery_status_enum IS
$$
전송 상태 타임라인(일반 흐름 예시):
queued(대기) → sent(전송) → delivered(전달) → read(열람) → ack(확인/응급승인)
실패/종료: failed(전송 실패), expired(유효기간 경과), canceled(정책/사용자 취소)
$$;

-- =========================================================
-- 1) 메시지(본문/성격) - 최소 본체
-- =========================================================
CREATE TABLE IF NOT EXISTS notify.notify_message (
  message_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),           -- 메시지 식별자(논리 단위)
  kind         notify.kind_enum NOT NULL,                            -- 메시지 성격/용도
  severity     notify.severity_enum NOT NULL DEFAULT 'green',        -- 위기 5단계(정렬/비교 가능)
  title        TEXT,                                                 -- 제목(없을 수 있음)
  body         TEXT,                                                 -- 본문(마크다운/평문)
  data         JSONB,                                                -- 추가 메타(링크/센서값/버튼 등)
  scheduled_at TIMESTAMPTZ,                                          -- 예약 발송 시각(선택)
  expires_at   TIMESTAMPTZ,                                          -- 유효기간(만료 후 미전송/미노출)
  created_by   UUID,                                                 -- 생성자(운영자/시스템/사용자)
  created_ip   INET,                                                 -- 생성 시점 IP(감사)
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE notify.notify_message IS
$$
알림 메시지 본문/성격을 보관하는 최소 테이블.
- 하나의 message_id는 동일한 콘텐츠 단위를 의미(여러 사용자에게 재사용 가능).
- severity는 green→red 순으로 위험도가 증가하며, 임계 비교(WHERE severity >= 'orange')가 직관적.
- expires_at 이후에는 신규 전송/노출을 차단(배치 또는 애플리케이션 로직에서 만료 처리).
$$;

COMMENT ON COLUMN notify.notify_message.kind IS '메시지 성격(공지/일정/정보/연락/마케팅/인바운드)';
COMMENT ON COLUMN notify.notify_message.severity IS '위기 5단계(ENUM). green<blue<yellow<orange<red';
COMMENT ON COLUMN notify.notify_message.data IS '템플릿 변수/버튼/링크/센서 값 등 확장 메타(JSONB)';

CREATE INDEX IF NOT EXISTS idx_notify_message_kind_sev
  ON notify.notify_message(kind, severity);
CREATE INDEX IF NOT EXISTS idx_notify_message_expires
  ON notify.notify_message(expires_at);

CREATE TRIGGER trg_notify_message_updated
BEFORE UPDATE ON notify.notify_message
FOR EACH ROW EXECUTE FUNCTION notify.set_updated_at();

-- =========================================================
-- 2) 딜리버리(수신자×채널 상태) - 최소 추적
-- =========================================================
CREATE TABLE IF NOT EXISTS notify.notify_delivery (
  delivery_id  BIGSERIAL PRIMARY KEY,
  message_id   UUID NOT NULL REFERENCES notify.notify_message(message_id) ON DELETE CASCADE,
  user_id      UUID NOT NULL,                                        -- 수신자(또는 인바운드 시 송신자)
  channel      notify.channel_enum NOT NULL,                         -- 전달 채널
  endpoint     TEXT,                                                 -- 실제 엔드포인트(푸시토큰/이메일/WS-ID 등)
  status       notify.delivery_status_enum NOT NULL DEFAULT 'queued',-- 전송 상태
  send_at      TIMESTAMPTZ,                                          -- 전송 시각
  delivered_at TIMESTAMPTZ,                                          -- 전달(네트워크 수신) 시각
  read_at      TIMESTAMPTZ,                                          -- 열람 시각
  ack_at       TIMESTAMPTZ,                                          -- 응급확인/승인 시각
  error_text   TEXT,                                                 -- 실패 사유(옵션)
  payload      JSONB,                                                -- 채널별 렌더링된 페이로드(보낸 내용 스냅샷)
  client_meta  JSONB,                                                -- 클라이언트 콜백 시 메타(UA/OS/위치 등)
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(message_id, user_id, channel)                               -- 같은 메시지/수신자/채널 중복 방지
);

COMMENT ON TABLE notify.notify_delivery IS
$$
메시지의 사용자별·채널별 전송 상태를 추적하는 최소 테이블.
- 오프라인/재전송/열람/ACK/만료 여부를 타임스탬프와 status로 일관되게 관리.
- 브로커(WebSocket/푸시/SMS 등)로 내보낸 후 결과 콜백을 반영해 status와 타임스탬프 갱신.
- payload는 전송 당시 렌더링 스냅샷을 보관(사후 감사/재현/다국어 확인).
$$;

COMMENT ON COLUMN notify.notify_delivery.status IS
'전송 상태: queued→sent→delivered→read→ack / 실패/종료: failed, expired, canceled';

CREATE INDEX IF NOT EXISTS idx_notify_delivery_user_status
  ON notify.notify_delivery(user_id, status);
CREATE INDEX IF NOT EXISTS idx_notify_delivery_message
  ON notify.notify_delivery(message_id);
CREATE INDEX IF NOT EXISTS idx_notify_delivery_status
  ON notify.notify_delivery(status);
CREATE INDEX IF NOT EXISTS idx_notify_delivery_created
  ON notify.notify_delivery(created_at);

CREATE TRIGGER trg_notify_delivery_updated
BEFORE UPDATE ON notify.notify_delivery
FOR EACH ROW EXECUTE FUNCTION notify.set_updated_at();


-- 스키마가 없다면 먼저 생성
CREATE SCHEMA IF NOT EXISTS notify;

-- 채널 ENUM 선행 정의: 테이블에서 사용되기 전에 반드시 만들어야 함
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'channel_enum') THEN
    CREATE TYPE notify.channel_enum AS ENUM ('websocket','sse','push','email','sms','voice','kakao');
  END IF;
END $$;

-- (선택) 의미 설명을 COMMENT 로 남겨 가독성/운영성 향상
COMMENT ON TYPE notify.channel_enum IS
$$
전달 채널 ENUM.
- websocket: 실시간 양방향(웹/대시보드)
- sse: 서버→클라이언트 단방향 스트림
- push: 모바일 푸시(FCM/APNs)
- email: 이메일
- sms: 문자
- voice: 자동 통화/콜봇
- kakao: 카카오 채널/알림톡(정책 준수 필요)
$$;


-- updated_at 자동 갱신 트리거 함수(이미 있다면 생략)
CREATE OR REPLACE FUNCTION notify.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 디바이스/엔드포인트 레지스트리
CREATE TABLE IF NOT EXISTS notify.notify_device (
  device_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID NOT NULL,
  channel        notify.channel_enum NOT NULL,          -- ← 방금 만든 ENUM 사용
  endpoint       TEXT NOT NULL,                         -- 토큰/이메일/전화/WS-ID
  is_active      BOOLEAN NOT NULL DEFAULT TRUE,
  device_meta    JSONB,                                 -- OS/브라우저/앱버전 등
  last_seen_at   TIMESTAMPTZ,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(channel, endpoint)
);
CREATE INDEX IF NOT EXISTS idx_device_user ON notify.notify_device(user_id);
CREATE TRIGGER trg_device_updated BEFORE UPDATE ON notify.notify_device
  FOR EACH ROW EXECUTE FUNCTION notify.set_updated_at();

-- (선택) 컬럼 주석으로 의미 문서화
COMMENT ON TABLE notify.notify_device IS
'사용자별 알림 엔드포인트(푸시 토큰/이메일/전화/WS 세션 등) 관리 테이블';
COMMENT ON COLUMN notify.notify_device.channel IS '전달 채널 ENUM(websocket/sse/push/email/sms/voice/kakao)';
COMMENT ON COLUMN notify.notify_device.endpoint IS '실제 전송 주소/토큰/세션 식별자';


-- =========================================================
-- notify.notify_message : "무엇을 보낼지" (알림 본문/성격/유효기간)
-- =========================================================
COMMENT ON TABLE notify.notify_message IS
$$
알림 메시지의 본문과 성격(종류/위험도)을 보관하는 최소 본체 테이블.
- 하나의 message_id는 동일 콘텐츠 단위를 의미하며, 여러 사용자에게 재사용될 수 있음.
- severity는 green→blue→yellow→orange→red 순서(정렬/비교에 의미 있음).
- expires_at 이후에는 신규 전송/노출을 차단(애플리케이션/배치에서 만료 처리).
$$;

COMMENT ON COLUMN notify.notify_message.message_id IS
'메시지 식별자(논리 단위). 동일 콘텐츠 묶음. gen_random_uuid() 기본값 사용 권장.';

COMMENT ON COLUMN notify.notify_message.kind IS
$$
메시지 성격/용도(kind_enum).
- system: 시스템 공지/이상징후/안전경보(낙상 의심 등)
- schedule: 일정 알림(복약/진료/활동/방문 일정)
- info: 일반 정보성 알림(안내/업데이트)
- contact: 연락/콜백 요청(요양사/가족 연락)
- marketing: 프로모션/캠페인(동의 기반)
- inbound: 사용자/클라이언트 기원 메시지(문의/버튼응답/피드백)
$$;

COMMENT ON COLUMN notify.notify_message.severity IS
$$
위기 5단계(severity_enum). 정의된 순서가 중요: green < blue < yellow < orange < red
- green(정상): 개인 기준선 유지(2–4주 평균), 월간 리프레시/계절 보정
- blue(권고): 경미 변동(알람 피로 방지), 교육/안내 중심 대응
- yellow(주의): 원인 탐색·생활 코칭·1주 재평가(수면/활동/환경/약물 등 24 시나리오)
- orange(고위험): 단기간 급격 이탈(야간배뇨 급증·PDC<80%·활동 급감 등), 당일 전화/방문 검토
- red(위급): 무반응·즉시 신고(119/911), long lie(≥1h) 위험, 보호자 동시 알림
임계 비교 예) WHERE severity >= 'orange'
$$;

COMMENT ON COLUMN notify.notify_message.title IS
'알림 제목. 채널별 템플릿을 쓰지 않는 경우 즉시 표시용으로 사용.';

COMMENT ON COLUMN notify.notify_message.body IS
'알림 본문(평문/마크다운 허용). 중요 링크/설명/지시사항 포함 가능.';

COMMENT ON COLUMN notify.notify_message.data IS
$$
추가 메타데이터(JSONB).
예) {"sensor":"fall_v2","prob":0.93,"link":"/alert/123","buttons":[{"id":"ack","label":"확인"}]}
템플릿 변수/링크/버튼/센서값 등 확장 필드 보관.
$$;

COMMENT ON COLUMN notify.notify_message.scheduled_at IS
'예약 발송 시각(선택). 지정되면 디스패처가 이 시각 이후에 전송 큐잉.';

COMMENT ON COLUMN notify.notify_message.expires_at IS
'유효기간(선택). 이 시각 이후 신규 전송/노출 금지. 만료 배치/정책에 활용.';

COMMENT ON COLUMN notify.notify_message.created_by IS
'메시지 생성 주체(운영자/시스템/사용자) 식별자. 감사/추적용.';

COMMENT ON COLUMN notify.notify_message.created_ip IS
'메시지 생성 시 클라이언트 IP(감사/보안 로그용).';

COMMENT ON COLUMN notify.notify_message.created_at IS
'레코드 생성 시각(UTC 권장).';

COMMENT ON COLUMN notify.notify_message.updated_at IS
'레코드 갱신 시각. BEFORE UPDATE 트리거(set_updated_at)로 자동 갱신.';


-- =========================================================
-- notify.notify_delivery : "누구에게/어떤 채널로/어떻게 보냈는지" (수신자×채널 상태 추적)
-- =========================================================
COMMENT ON TABLE notify.notify_delivery IS
$$
메시지의 사용자별·채널별 전송 상태를 추적하는 테이블.
- queued→sent→delivered→read→ack 순서로 진행(실패/종료: failed/expired/canceled).
- 각 단계의 타임스탬프를 보관해 오프라인 재전송/에스컬레이션/리포팅이 용이.
- payload는 전송 당시 렌더링 스냅샷(사후 감사/재현/다국어 확인).
UNIQUE(message_id, user_id, channel)로 중복 전송 방지(정책에 따라 완화 가능).
$$;

COMMENT ON COLUMN notify.notify_delivery.delivery_id IS
'딜리버리(전송 시도) 식별자. BIGSERIAL PK.';

COMMENT ON COLUMN notify.notify_delivery.message_id IS
'원본 알림 메시지 FK. notify_message.message_id 참조.';

COMMENT ON COLUMN notify.notify_delivery.user_id IS
'수신자 사용자 ID(인바운드 라우팅 시 송신자 개념으로도 재사용 가능).';

COMMENT ON COLUMN notify.notify_delivery.channel IS
$$
전달 채널(channel_enum).
- websocket: 웹 대시보드/앱 실시간 양방향
- sse: 서버→클라이언트 단방향 스트림
- push: 모바일 푸시(FCM/APNs)
- email: 이메일
- sms: 문자
- voice: 자동 통화/콜봇
- kakao: 카카오 채널/알림톡(정책 준수 필요)
$$;

COMMENT ON COLUMN notify.notify_delivery.endpoint IS
'해당 채널에서 실제 전송할 엔드포인트(푸시 토큰/이메일/전화/WS 세션ID 등).';

COMMENT ON COLUMN notify.notify_delivery.status IS
$$
전송 상태(delivery_status_enum).
일반 플로우: queued(대기) → sent(전송) → delivered(네트워크 전달) → read(열람) → ack(확인).
실패/종료: failed(전송 실패), expired(유효기간 경과로 중단), canceled(정책/사용자 취소).
$$;

COMMENT ON COLUMN notify.notify_delivery.send_at IS
'전송 시각(서버가 실제로 브로커/채널로 보낸 시간).';

COMMENT ON COLUMN notify.notify_delivery.delivered_at IS
'전달 시각(네트워크/클라이언트에 도달 확인된 시간).';

COMMENT ON COLUMN notify.notify_delivery.read_at IS
'열람(읽음) 시각(클라이언트 콜백 또는 트래킹 픽셀/WS 이벤트 기반).';

COMMENT ON COLUMN notify.notify_delivery.ack_at IS
'확인/응급 ACK 시각(사용자 명시 동작). 에스컬레이션 중단/완료 판단 기준.';

COMMENT ON COLUMN notify.notify_delivery.error_text IS
'실패 사유/오류 메시지(전송 API 응답/예외 메시지 기록).';

COMMENT ON COLUMN notify.notify_delivery.payload IS
$$
전송 당시 렌더링된 페이로드(JSONB 스냅샷).
예) 푸시: {"title":"…","body":"…","data":{…}} / 이메일: {"subject":"…","html":"…"}
$$;

COMMENT ON COLUMN notify.notify_delivery.client_meta IS
'클라이언트 회신 메타(JSONB): UA/OS/앱버전/위치/네트워크/버튼ID 등 콜백 시 수집 정보.';

COMMENT ON COLUMN notify.notify_delivery.created_at IS
'레코드 생성 시각(큐잉 생성 시점).';

COMMENT ON COLUMN notify.notify_delivery.updated_at IS
'레코드 갱신 시각. BEFORE UPDATE 트리거(set_updated_at)로 자동 갱신.';


-- =========================================================
-- notify.notify_device : "어디로 보낼지" (사용자 단말/엔드포인트 관리)
-- =========================================================
COMMENT ON TABLE notify.notify_device IS
$$
사용자별 디바이스/엔드포인트 레지스트리.
- 채널별 실제 전송 주소/토큰/세션을 저장하여 라우팅에 사용.
- is_active=false로 비활성(앱 삭제/로그아웃/토큰 만료) 관리 시 비용 절감.
- device_meta에 OS/앱 버전/브라우저 등 부가정보를 보관해 운영/통계/디버깅에 활용.
UNIQUE(channel, endpoint)로 동일 엔드포인트 중복 등록 방지.
$$;

COMMENT ON COLUMN notify.notify_device.device_id IS
'디바이스/엔드포인트 식별자. gen_random_uuid() 기본값.';

COMMENT ON COLUMN notify.notify_device.user_id IS
'해당 디바이스가 속한 사용자 ID. 한 사용자가 여러 디바이스를 가질 수 있음.';

COMMENT ON COLUMN notify.notify_device.channel IS
'디바이스/엔드포인트가 속한 알림 채널(channel_enum). 예: push/email/sms/websocket …';

COMMENT ON COLUMN notify.notify_device.endpoint IS
'실제 전송 주소/토큰/세션 식별자(FCM 토큰/이메일/전화번호/WebSocket 세션 ID 등).';

COMMENT ON COLUMN notify.notify_device.is_active IS
'활성 여부. false면 전송 대상에서 제외(앱 삭제/로그아웃/반복 실패 등).';

COMMENT ON COLUMN notify.notify_device.device_meta IS
'부가 메타(JSONB): OS/브라우저/앱 버전/모델/UA 등 운영 및 디버깅용 정보.';

COMMENT ON COLUMN notify.notify_device.last_seen_at IS
'마지막 통신 시각(최근 활동 디바이스 판단/정리 배치 기준).';

COMMENT ON COLUMN notify.notify_device.created_at IS
'레코드 생성 시각.';

COMMENT ON COLUMN notify.notify_device.updated_at IS
'레코드 갱신 시각. BEFORE UPDATE 트리거(set_updated_at)로 자동 갱신.';
