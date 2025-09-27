#!/bin/bash

# =========================================================
# 파일 분배 스크립트 (distribute_files.sh)
# 입력된 폴더의 모든 파일을 N개의 대상 폴더에 균등하게 분배합니다.
# 사용법: ./distribute_files.sh <원본_폴더_경로> <분할_폴더_개수_N>
# =========================================================

# 1. 인자 유효성 검사
if [ "$#" -ne 2 ]; then
    echo "사용법: $0 <원본_폴더_경로> <분할_폴더_개수_N>"
    echo "예시: $0 ./data 10"
    exit 1
fi

SOURCE_DIR="$1"
N=$2
TARGET_DIR_PREFIX="${SOURCE_DIR}_split_"
TEMP_FILE="/tmp/file_list_$$_$(date +%s).txt" # 고유한 임시 파일명 생성

# 원본 폴더 유효성 검사
if [ ! -d "$SOURCE_DIR" ]; then
    echo "오류: 원본 폴더 '$SOURCE_DIR'를 찾을 수 없습니다."
    exit 1
fi

# N이 유효한 숫자인지 확인
if ! [[ "$N" =~ ^[0-9]+$ ]] || [ "$N" -le 0 ]; then
    echo "오류: 분할 폴더 개수(N)는 1 이상의 정수여야 합니다."
    exit 1
fi

# 2. 파일 목록 생성 및 개수 계산
echo "1. '${SOURCE_DIR}' 폴더에서 파일 목록을 생성 중..."
# 원본 폴더의 모든 파일 목록을 생성 (경로 포함, 오름차순 정렬)
# find는 기본적으로 상대 경로를 출력합니다.
find "$SOURCE_DIR" -type f | sort > "$TEMP_FILE"

TOTAL_FILES=$(wc -l < "$TEMP_FILE")

if [ "$TOTAL_FILES" -eq 0 ]; then
    echo "경고: '${SOURCE_DIR}' 폴더에 파일이 없습니다. 작업을 종료합니다."
    rm "$TEMP_FILE"
    exit 0
fi

# 3. 각 폴더에 들어갈 파일 개수 계산 (올림 처리)
# bc 명령어를 사용하여 정밀한 나눗셈 및 올림 계산
FILES_PER_DIR=$(echo "($TOTAL_FILES + $N - 1) / $N" | bc)

echo "   -> 전체 파일 개수: $TOTAL_FILES"
echo "   -> 분할할 폴더 개수: $N"
echo "   -> 각 폴더에 들어갈 파일 개수: $FILES_PER_DIR"

# 4. 파일 목록 분할
echo "2. 파일 목록을 $N개로 분할 중..."
# split -l: 한 파일당 라인 수
split -l $FILES_PER_DIR "$TEMP_FILE" "$TEMP_FILE.part."

# 5. 분할된 목록을 순회하며 폴더 생성 및 파일 이동
echo "3. 파일을 새 폴더로 이동 중..."
COUNT=1
for PART_FILE in "$TEMP_FILE.part."*; do
    # 대상 폴더 이름 생성 (예: ./원본폴더_split_01, ./원본폴더_split_02, ...)
    TARGET_DIR="${TARGET_DIR_PREFIX}$(printf "%02d" $COUNT)"
    
    # 대상 폴더 생성
    mkdir -p "$TARGET_DIR"
    
    echo "   -> [${TARGET_DIR}] 로 파일 이동 중... ($(wc -l < "$PART_FILE")개 파일)"
    
    # 분할된 목록 파일을 읽어서 각 파일을 대상 폴더로 이동
    while IFS= read -r FILE_PATH; do
        # 파일의 전체 경로를 대상 폴더로 이동
        mv "$FILE_PATH" "$TARGET_DIR/"
    done < "$PART_FILE"
    
    COUNT=$((COUNT + 1))
done

# 6. 임시 파일 정리
echo "4. 임시 파일 정리 중..."
rm "$TEMP_FILE" "$TEMP_FILE.part."*

echo "✅ 파일 분배가 완료되었습니다. ${N}개의 폴더가 생성되었습니다."