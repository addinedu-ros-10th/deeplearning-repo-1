#!/bin/bash

# Git Message Template 설정 스크립트 (모노레포용)
# 사용법: ./scripts/setup_git_template.sh

echo "🔧 Git Message Template 설정을 시작합니다..."

# 모노레포 루트 디렉토리로 이동
REPO_ROOT="$(git rev-parse --show-toplevel)"
echo "📁 모노레포 루트: $REPO_ROOT"

# .gitmessage 파일 확인
if [ ! -f "$REPO_ROOT/.gitmessage" ]; then
    echo "❌ .gitmessage 파일을 찾을 수 없습니다."
    echo "   모노레포 루트에 .gitmessage 파일이 있는지 확인해주세요."
    exit 1
fi

# Git 전역 설정 (모든 프로젝트에 적용)
echo "📝 Git 전역 메시지 템플릿을 설정합니다..."
git config --global commit.template "$REPO_ROOT/.gitmessage"

# 현재 프로젝트 설정 (현재 프로젝트에만 적용)
echo "📝 현재 프로젝트 메시지 템플릿을 설정합니다..."
git config commit.template "$REPO_ROOT/.gitmessage"

# 설정 확인
echo "✅ 설정이 완료되었습니다!"
echo ""
echo "📋 현재 Git 설정:"
echo "   전역 커밋 템플릿: $(git config --global commit.template)"
echo "   로컬 커밋 템플릿: $(git config commit.template)"
echo ""
echo "🚀 사용법:"
echo "   git commit  # 템플릿이 자동으로 로드됩니다"
echo "   git commit -m \"feat(api): 새로운 기능 추가\"  # 직접 메시지 작성"
echo ""
echo "📖 자세한 사용법은 docs/git_message_template_guide.md를 참고하세요."
