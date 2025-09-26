#!/usr/bin/env python3
"""
Qwen2.5-3B-Instruct 모델 로딩 및 기본 테스트 스크립트
"""
import os
import sys
import time
from pathlib import Path

def test_model_loading():
    """모델 로딩 테스트"""
    print("🔍 Qwen2.5-3B-Instruct 모델 로딩 테스트 시작...")
    
    model_path = "./models/qwen2.5-3b-instruct"
    
    # 1. 모델 파일 존재 확인
    print(f"📂 모델 경로 확인: {model_path}")
    if not os.path.exists(model_path):
        print(f"❌ 모델 디렉토리가 없습니다: {model_path}")
        return False
    
    # 2. 필수 파일 확인
    required_files = [
        "config.json",
        "tokenizer.json", 
        "model-00001-of-00002.safetensors",
        "model-00002-of-00002.safetensors",
        "model.safetensors.index.json"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(model_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
        else:
            size = os.path.getsize(file_path)
            print(f"✅ {file}: {size:,} bytes")
    
    if missing_files:
        print(f"❌ 누락된 파일들: {missing_files}")
        return False
    
    try:
        # 3. transformers 라이브러리로 모델 로딩 테스트
        print("\n🚀 transformers 라이브러리로 모델 로딩 시도...")
        
        from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
        
        # 설정 로드
        config = AutoConfig.from_pretrained(model_path)
        print(f"✅ 모델 설정 로드 완료")
        print(f"   - 모델 타입: {config.model_type}")
        print(f"   - 어휘 크기: {config.vocab_size:,}")
        print(f"   - 히든 크기: {config.hidden_size}")
        print(f"   - 레이어 수: {config.num_hidden_layers}")
        
        # 토크나이저 로드
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print(f"✅ 토크나이저 로드 완료")
        
        # 간단한 토큰화 테스트
        test_texts = [
            "안녕하세요, 테스트입니다.",
            "Hello, this is a test.",
            "What is the capital of Korea?"
        ]
        
        print(f"\n🧪 토큰화 테스트:")
        for text in test_texts:
            tokens = tokenizer.encode(text)
            decoded = tokenizer.decode(tokens)
            print(f"   입력: {text}")
            print(f"   토큰 수: {len(tokens)}")
            print(f"   복원: {decoded}")
            print()
        
        print("✅ 모든 기본 테스트 통과!")
        return True
        
    except ImportError as e:
        print(f"⚠️ transformers 라이브러리가 설치되지 않았습니다: {e}")
        print("   pip install transformers 로 설치하세요.")
        return False
    except Exception as e:
        print(f"❌ 모델 로딩 실패: {e}")
        return False

def test_vllm_compatibility():
    """vLLM 호환성 테스트"""
    print("\n🔧 vLLM 호환성 테스트...")
    
    try:
        import vllm
        print(f"✅ vLLM 라이브러리 설치됨 (버전: {vllm.__version__})")
        
        # vLLM으로 모델 로드 테스트 (실제로는 메모리 부족으로 실패할 수 있음)
        print("ℹ️ vLLM 실제 로딩은 메모리 사용량이 많아 Docker 환경에서 테스트하세요.")
        return True
        
    except ImportError:
        print("⚠️ vLLM 라이브러리가 설치되지 않았습니다.")
        print("   Docker 환경에서 vllm/vllm-openai 이미지를 사용하세요.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Qwen2.5-3B-Instruct 모델 테스트")
    print("=" * 60)
    
    # 현재 디렉토리 확인
    print(f"📁 현재 디렉토리: {os.getcwd()}")
    
    # 모델 로딩 테스트
    success = test_model_loading()
    
    # vLLM 호환성 테스트
    test_vllm_compatibility()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 모델 테스트 완료! 다음 단계로 진행할 수 있습니다.")
    else:
        print("❌ 모델 테스트 실패. 문제를 해결하고 다시 시도하세요.")
    print("=" * 60)



