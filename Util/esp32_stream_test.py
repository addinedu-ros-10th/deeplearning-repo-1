#!/usr/bin/env python3
"""
ESP32 영상 스트림 테스트 도구

ESP32에서 송출하는 영상 스트림을 확인하고 테스트하는 도구입니다.
- HTTP 스트림 연결 테스트
- 영상 프레임 캡처 및 저장
- 스트림 상태 모니터링
- 네트워크 연결 진단

사용법:
    python3 esp32_stream_test.py
    python3 esp32_stream_test.py --url http://192.168.0.61:81/stream
    python3 esp32_stream_test.py --capture-frames --output-dir ./captured_frames
"""

import cv2
import requests
import time
import argparse
import os
import threading
from datetime import datetime
from urllib.parse import urlparse
import json


class ESP32StreamTester:
    """ESP32 영상 스트림 테스트 클래스"""
    
    def __init__(self, stream_url: str = "http://192.168.0.61:81/stream"):
        self.stream_url = stream_url
        self.cap = None
        self.is_streaming = False
        self.frame_count = 0
        self.start_time = None
        self.fps_counter = 0
        self.fps_start_time = None
        
    def test_connection(self) -> bool:
        """스트림 연결 테스트"""
        print(f"🔍 스트림 연결 테스트: {self.stream_url}")
        
        try:
            # HTTP HEAD 요청으로 연결 가능성 확인
            response = requests.head(self.stream_url, timeout=5)
            print(f"  ✅ HTTP 응답: {response.status_code}")
            print(f"  📋 Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"  📏 Content-Length: {response.headers.get('Content-Length', 'Unknown')}")
            return True
            
        except requests.exceptions.ConnectTimeout:
            print("  ❌ 연결 시간 초과 - ESP32가 실행 중인지 확인하세요")
            return False
        except requests.exceptions.ConnectionError:
            print("  ❌ 연결 실패 - IP 주소와 포트를 확인하세요")
            return False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 요청 오류: {e}")
            return False
    
    def test_stream_quality(self, duration: int = 10) -> dict:
        """스트림 품질 테스트"""
        print(f"\n📊 스트림 품질 테스트 ({duration}초)")
        
        if not self.test_connection():
            return {"success": False, "error": "연결 실패"}
        
        try:
            # OpenCV로 스트림 연결
            self.cap = cv2.VideoCapture(self.stream_url)
            
            if not self.cap.isOpened():
                print("  ❌ OpenCV로 스트림을 열 수 없습니다")
                return {"success": False, "error": "OpenCV 연결 실패"}
            
            # 스트림 정보 수집
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"  📐 해상도: {width}x{height}")
            print(f"  🎬 FPS: {fps}")
            
            # 실제 FPS 측정
            self.start_time = time.time()
            self.fps_counter = 0
            self.fps_start_time = time.time()
            
            print(f"  ⏱️  {duration}초간 프레임 수집 중...")
            
            while time.time() - self.start_time < duration:
                ret, frame = self.cap.read()
                if ret:
                    self.fps_counter += 1
                    self.frame_count += 1
                    
                    # 1초마다 FPS 출력
                    if time.time() - self.fps_start_time >= 1.0:
                        current_fps = self.fps_counter / (time.time() - self.fps_start_time)
                        print(f"    📈 현재 FPS: {current_fps:.2f}")
                        self.fps_counter = 0
                        self.fps_start_time = time.time()
                else:
                    print("  ⚠️  프레임 읽기 실패")
                    break
            
            # 결과 계산
            total_time = time.time() - self.start_time
            actual_fps = self.frame_count / total_time if total_time > 0 else 0
            
            result = {
                "success": True,
                "resolution": f"{width}x{height}",
                "reported_fps": fps,
                "actual_fps": actual_fps,
                "total_frames": self.frame_count,
                "duration": total_time,
                "frame_loss_rate": max(0, 1 - (actual_fps / fps)) if fps > 0 else 0
            }
            
            print(f"  ✅ 테스트 완료:")
            print(f"    📊 실제 FPS: {actual_fps:.2f}")
            print(f"    📈 총 프레임: {self.frame_count}")
            print(f"    ⏱️  총 시간: {total_time:.2f}초")
            print(f"    📉 프레임 손실률: {result['frame_loss_rate']:.2%}")
            
            return result
            
        except Exception as e:
            print(f"  ❌ 스트림 품질 테스트 오류: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if self.cap:
                self.cap.release()
    
    def capture_frames(self, output_dir: str = "./captured_frames", max_frames: int = 10) -> bool:
        """프레임 캡처 및 저장"""
        print(f"\n📸 프레임 캡처 시작 (최대 {max_frames}개)")
        
        if not self.test_connection():
            return False
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            self.cap = cv2.VideoCapture(self.stream_url)
            
            if not self.cap.isOpened():
                print("  ❌ OpenCV로 스트림을 열 수 없습니다")
                return False
            
            captured_count = 0
            print(f"  📁 저장 경로: {os.path.abspath(output_dir)}")
            
            while captured_count < max_frames:
                ret, frame = self.cap.read()
                if ret:
                    # 타임스탬프가 포함된 파일명
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    filename = f"esp32_frame_{timestamp}_{captured_count:03d}.jpg"
                    filepath = os.path.join(output_dir, filename)
                    
                    # 프레임 저장
                    cv2.imwrite(filepath, frame)
                    captured_count += 1
                    
                    print(f"    📸 프레임 {captured_count}/{max_frames} 저장: {filename}")
                    
                    # 0.5초 대기 (너무 빠른 캡처 방지)
                    time.sleep(0.5)
                else:
                    print("  ⚠️  프레임 읽기 실패")
                    break
            
            print(f"  ✅ {captured_count}개 프레임 캡처 완료")
            return True
            
        except Exception as e:
            print(f"  ❌ 프레임 캡처 오류: {e}")
            return False
        finally:
            if self.cap:
                self.cap.release()
    
    def monitor_stream(self, duration: int = 30) -> None:
        """스트림 모니터링 (실시간 프레임 표시)"""
        print(f"\n👁️  스트림 모니터링 ({duration}초)")
        print("  💡 'q' 키를 눌러 조기 종료할 수 있습니다")
        
        if not self.test_connection():
            return
        
        try:
            self.cap = cv2.VideoCapture(self.stream_url)
            
            if not self.cap.isOpened():
                print("  ❌ OpenCV로 스트림을 열 수 없습니다")
                return
            
            self.start_time = time.time()
            self.frame_count = 0
            
            print("  🎬 실시간 스트림 시작...")
            
            while time.time() - self.start_time < duration:
                ret, frame = self.cap.read()
                if ret:
                    self.frame_count += 1
                    
                    # 프레임에 정보 오버레이
                    current_time = time.time() - self.start_time
                    fps = self.frame_count / current_time if current_time > 0 else 0
                    
                    # 텍스트 오버레이
                    cv2.putText(frame, f"ESP32 Stream - FPS: {fps:.1f}", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Frame: {self.frame_count}", 
                              (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Time: {current_time:.1f}s", 
                              (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # 프레임 표시
                    cv2.imshow('ESP32 Stream Monitor', frame)
                    
                    # 'q' 키로 종료
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("  ⏹️  사용자에 의해 중단됨")
                        break
                else:
                    print("  ⚠️  프레임 읽기 실패")
                    break
            
            print(f"  ✅ 모니터링 완료 - 총 {self.frame_count}개 프레임 수신")
            
        except Exception as e:
            print(f"  ❌ 모니터링 오류: {e}")
        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
    
    def network_diagnosis(self) -> dict:
        """네트워크 진단"""
        print(f"\n🔧 네트워크 진단")
        
        try:
            parsed_url = urlparse(self.stream_url)
            host = parsed_url.hostname
            port = parsed_url.port or 80
            
            print(f"  🌐 호스트: {host}")
            print(f"  🔌 포트: {port}")
            
            # Ping 테스트 (간단한 TCP 연결 테스트)
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            try:
                result = sock.connect_ex((host, port))
                if result == 0:
                    print(f"  ✅ TCP 연결 성공 ({host}:{port})")
                    tcp_ok = True
                else:
                    print(f"  ❌ TCP 연결 실패 ({host}:{port}) - 오류 코드: {result}")
                    tcp_ok = False
            finally:
                sock.close()
            
            # HTTP 응답 시간 측정
            start_time = time.time()
            try:
                response = requests.get(self.stream_url, timeout=10, stream=True)
                response_time = time.time() - start_time
                print(f"  ⏱️  HTTP 응답 시간: {response_time:.3f}초")
                print(f"  📊 HTTP 상태: {response.status_code}")
                http_ok = response.status_code == 200
            except Exception as e:
                print(f"  ❌ HTTP 요청 실패: {e}")
                http_ok = False
                response_time = None
            
            return {
                "host": host,
                "port": port,
                "tcp_connection": tcp_ok,
                "http_response": http_ok,
                "response_time": response_time
            }
            
        except Exception as e:
            print(f"  ❌ 네트워크 진단 오류: {e}")
            return {"error": str(e)}


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="ESP32 영상 스트림 테스트 도구")
    parser.add_argument("--url", default="http://192.168.0.61:81/stream", 
                       help="ESP32 스트림 URL (기본값: http://192.168.0.61:81/stream)")
    parser.add_argument("--test-connection", action="store_true", 
                       help="연결 테스트만 실행")
    parser.add_argument("--test-quality", type=int, metavar="SECONDS", 
                       help="스트림 품질 테스트 (초 단위)")
    parser.add_argument("--capture-frames", action="store_true", 
                       help="프레임 캡처 실행")
    parser.add_argument("--output-dir", default="./captured_frames", 
                       help="캡처된 프레임 저장 디렉토리")
    parser.add_argument("--max-frames", type=int, default=10, 
                       help="최대 캡처 프레임 수")
    parser.add_argument("--monitor", type=int, metavar="SECONDS", 
                       help="실시간 스트림 모니터링 (초 단위)")
    parser.add_argument("--diagnosis", action="store_true", 
                       help="네트워크 진단 실행")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ESP32 영상 스트림 테스트 도구")
    print("=" * 60)
    print(f"스트림 URL: {args.url}")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ESP32 스트림 테스터 생성
    tester = ESP32StreamTester(args.url)
    
    # 네트워크 진단
    if args.diagnosis:
        diagnosis_result = tester.network_diagnosis()
        print(f"\n📋 진단 결과: {json.dumps(diagnosis_result, indent=2, ensure_ascii=False)}")
    
    # 연결 테스트
    if args.test_connection or not any([args.test_quality, args.capture_frames, args.monitor]):
        connection_ok = tester.test_connection()
        if not connection_ok:
            print("\n❌ 연결 실패 - 다른 테스트를 건너뜁니다")
            return
    
    # 스트림 품질 테스트
    if args.test_quality:
        quality_result = tester.test_stream_quality(args.test_quality)
        print(f"\n📊 품질 테스트 결과: {json.dumps(quality_result, indent=2, ensure_ascii=False)}")
    
    # 프레임 캡처
    if args.capture_frames:
        capture_success = tester.capture_frames(args.output_dir, args.max_frames)
        if capture_success:
            print(f"\n✅ 프레임 캡처 완료: {os.path.abspath(args.output_dir)}")
        else:
            print("\n❌ 프레임 캡처 실패")
    
    # 실시간 모니터링
    if args.monitor:
        tester.monitor_stream(args.monitor)
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

