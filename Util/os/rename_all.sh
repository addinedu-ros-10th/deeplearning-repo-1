#!/bin/bash

# =========================================================
# 여러 폴더 내 파일 통합 순차적 이름 변경 스크립트
# 사용법: ./rename_all.sh <폴더1> <폴더2> [폴더3] ...
# 예시: ./rename_all.sh ./a ./b ./c
# =========================================================

# 1. 인자 유효성 검사
if [ "$#" -eq 0 ]; then
    echo "사용법: $0 <폴더1> <폴더2> [폴더3] ..."
    echo "예시: $0 ./a ./b ./c"
    exit 1
fi

# 2. 변수 설정
TEMP_FILE="/tmp/all_files_to_rename_$$_$(date +%s).txt" # 고유한 임시 파일명 생성
COUNTER=1 # 시작 번호

echo "1. 지정된 모든 폴더에서 파일 목록을 수집 중..."

# 3. 모든 폴더의 파일 목록을 생성하고 임시 파일에 저장
# -type f: 파일만 찾기
# -print0: 파일명에 공백이나 특수문자가 있어도 안전하게 처리
find "$@" -type f -print0 > "$TEMP_FILE"

# 파일이 없는 경우 처리
if [ ! -s "$TEMP_FILE" ]; then
    echo "경고: 지정된 폴더에 파일을 찾을 수 없습니다. 작업을 종료합니다."
    rm -f "$TEMP_FILE"
    exit 0
fi

echo "2. 파일 이름 변경을 시작합니다..."

# 4. 임시 파일을 읽어 각 파일을 순회하며 이름 변경
# read -d $'\0': -print0로 출력된 널(null) 문자로 구분된 파일 목록을 안전하게 읽어옴
while IFS= read -r -d $'\0' FILE_PATH; do
    
    # 원본 파일 경로에서 확장자(extension) 추출
    # ${FILE_PATH##*.}는 파일 경로에서 마지막 '.' 이후 문자열(확장자)을 추출
    # 만약 확장자가 없는 파일이라면 빈 문자열이 됩니다.
    EXTENSION="${FILE_PATH##*.}"
    
    # 새로운 파일명 생성 (예: 1.jpg, 2.png)
    if [ -n "$EXTENSION" ] && [ "$EXTENSION" != "$FILE_PATH" ]; then
        # 확장자가 있는 경우 (예: 1.jpg)
        NEW_NAME="${COUNTER}.${EXTENSION}"
    else
        # 확장자가 없는 경우 (예: 1)
        NEW_NAME="${COUNTER}"
    fi

    # 파일이 있는 폴더 경로 추출 (새 파일명을 해당 폴더에 저장해야 함)
    # dirname "$FILE_PATH": 파일의 부모 디렉토리 경로 추출
    TARGET_DIR="$(dirname "$FILE_PATH")"
    
    # 파일 이름 변경 (이동)
    mv -i "$FILE_PATH" "${TARGET_DIR}/${NEW_NAME}"
    
    echo "   -> [${FILE_PATH}] 를 [${TARGET_DIR}/${NEW_NAME}] 로 변경"
    
    # 카운터 1 증가
    COUNTER=$((COUNTER + 1))
    
done < "$TEMP_FILE"

# 5. 임시 파일 정리
echo "3. 임시 파일 정리 중..."
rm -f "$TEMP_FILE"

echo "✅ 모든 폴더의 파일 이름 변경이 완료되었습니다. 총 $((COUNTER - 1))개 파일."