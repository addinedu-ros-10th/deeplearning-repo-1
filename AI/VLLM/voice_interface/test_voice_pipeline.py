#!/usr/bin/env python3
"""
Voice Interface 전체 파이프라인 테스트 스크립트
STT → LLM → TTS 통합 테스트
"""
import asyncio
import aiohttp
import time
import json
from pathlib import Path

class VoicePipelineTester:
    def __init__(self, base_url="http://localhost:8010", vllm_url="http://localhost:8001"):
        self.base_url = base_url
        self.vllm_url = vllm_url
        
    async def test_health(self):
        """헬스체크 테스트"""
        print("🏥 헬스체크 테스트...")
        try:
            async with aiohttp.ClientSession() as session:
                # Voice API 헬스체크
                async with session.get(f"{self.base_url}/health") as resp:
                    if resp.status == 200:
                        print("✅ Voice API 정상 동작")
                    else:
                        print(f"❌ Voice API 응답 오류: {resp.status}")
                        return False
                
                # vLLM 헬스체크
                async with session.get(f"{self.vllm_url}/health") as resp:
                    if resp.status == 200:
                        print("✅ vLLM 서버 정상 동작")
                    else:
                        print(f"❌ vLLM 서버 응답 오류: {resp.status}")
                        return False
                
                return True
        except Exception as e:
            print(f"❌ 헬스체크 실패: {e}")
            return False
    
    async def test_llm_direct(self):
        """vLLM 직접 테스트"""
        print("\n🤖 vLLM 직접 테스트...")
        
        test_messages = [
            {"role": "user", "content": "안녕하세요! 간단한 자기소개를 해주세요."},
            {"role": "user", "content": "What is the capital of South Korea?"},
            {"role": "user", "content": "Python으로 'Hello World'를 출력하는 코드를 작성해주세요."}
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for i, message in enumerate(test_messages, 1):
                    print(f"\n테스트 {i}: {message['content']}")
                    
                    payload = {
                        "model": "qwen2.5-3b-instruct",  # 모델명 명시
                        "messages": [message],
                        "max_tokens": 256,
                        "temperature": 0.7
                    }
                    
                    start_time = time.time()
                    async with session.post(
                        f"{self.vllm_url}/v1/chat/completions",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as resp:
                        end_time = time.time()
                        
                        if resp.status == 200:
                            result = await resp.json()
                            response_text = result['choices'][0]['message']['content']
                            print(f"✅ 응답 시간: {end_time - start_time:.2f}초")
                            print(f"📝 응답: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
                        else:
                            error_text = await resp.text()
                            print(f"❌ LLM 오류 ({resp.status}): {error_text}")
                            return False
                
                return True
        except Exception as e:
            print(f"❌ LLM 테스트 실패: {e}")
            return False
    
    async def test_voice_llm_endpoint(self):
        """Voice API의 LLM 엔드포인트 테스트"""
        print("\n🎙️ Voice API LLM 엔드포인트 테스트...")
        
        test_prompts = [
            {
                "messages": [{"role": "user", "content": "안녕하세요! 오늘 날씨가 어떤가요?"}],
                "max_tokens": 100,
                "temperature": 0.5
            },
            {
                "messages": [{"role": "user", "content": "간단한 Python 함수를 하나 만들어주세요."}],
                "max_tokens": 150,
                "temperature": 0.3
            }
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for i, prompt in enumerate(test_prompts, 1):
                    print(f"\n테스트 {i}: {prompt['messages'][0]['content']}")
                    
                    start_time = time.time()
                    async with session.post(
                        f"{self.base_url}/voice/llm",
                        json=prompt,
                        headers={"Content-Type": "application/json"}
                    ) as resp:
                        end_time = time.time()
                        
                        if resp.status == 200:
                            result = await resp.json()
                            response_text = result['choices'][0]['message']['content']
                            print(f"✅ 응답 시간: {end_time - start_time:.2f}초")
                            print(f"📝 응답: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
                        else:
                            error_text = await resp.text()
                            print(f"❌ Voice LLM 오류 ({resp.status}): {error_text}")
                            return False
                
                return True
        except Exception as e:
            print(f"❌ Voice LLM 테스트 실패: {e}")
            return False
    
    async def test_tts_endpoint(self):
        """TTS 엔드포인트 테스트"""
        print("\n🔊 TTS 엔드포인트 테스트...")
        
        test_texts = [
            "안녕하세요, 음성 합성 테스트입니다.",
            "Hello, this is a text-to-speech test.",
            "테스트가 성공적으로 완료되었습니다."
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for i, text in enumerate(test_texts, 1):
                    print(f"\n테스트 {i}: {text}")
                    
                    payload = {"text": text}
                    
                    start_time = time.time()
                    async with session.post(
                        f"{self.base_url}/voice/tts",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as resp:
                        end_time = time.time()
                        
                        if resp.status == 200:
                            audio_data = await resp.read()
                            print(f"✅ TTS 성공 - 응답 시간: {end_time - start_time:.2f}초")
                            print(f"🎵 오디오 데이터 크기: {len(audio_data)} bytes")
                            
                            # WAV 파일로 저장 (선택사항)
                            output_file = f"test_tts_{i}.wav"
                            with open(output_file, "wb") as f:
                                f.write(audio_data)
                            print(f"💾 오디오 파일 저장: {output_file}")
                        else:
                            error_text = await resp.text()
                            print(f"❌ TTS 오류 ({resp.status}): {error_text}")
                            return False
                
                return True
        except Exception as e:
            print(f"❌ TTS 테스트 실패: {e}")
            return False
    
    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 80)
        print("🎯 Voice Interface 통합 테스트 시작")
        print("=" * 80)
        
        tests = [
            ("헬스체크", self.test_health),
            ("vLLM 직접 테스트", self.test_llm_direct),
            ("Voice API LLM", self.test_voice_llm_endpoint),
            ("TTS 엔드포인트", self.test_tts_endpoint)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                results[test_name] = await test_func()
            except Exception as e:
                print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
                results[test_name] = False
        
        # 결과 요약
        print("\n" + "="*80)
        print("📊 테스트 결과 요약")
        print("="*80)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results.items():
            status = "✅ 통과" if success else "❌ 실패"
            print(f"{test_name:20} : {status}")
            if success:
                passed += 1
        
        print(f"\n🎯 전체 결과: {passed}/{total} 테스트 통과")
        
        if passed == total:
            print("🎉 모든 테스트가 성공했습니다! Voice Interface가 정상 작동합니다.")
        else:
            print("⚠️ 일부 테스트가 실패했습니다. 로그를 확인하고 문제를 해결하세요.")
        
        return passed == total

async def main():
    """메인 함수"""
    tester = VoicePipelineTester()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    # 비동기 실행
    success = asyncio.run(main())
    exit(0 if success else 1)



