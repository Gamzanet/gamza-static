#!/bin/bash

# name: script.sh
# description: semgrep 설치 스크립트

# 함수 정의
function print_usage() {
    echo "사용법: $0 [옵션]"
    echo "옵션:"
    echo "  -h, --help    도움말 출력"
    echo "  -v, --version 버전 정보 출력"
}

function print_version() {
   jq -r '.version' package.json
}

# 옵션 파싱
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) print_usage; exit 0 ;;
        -v|--version) print_version; exit 0 ;;
        *) echo "알 수 없는 옵션: $1"; print_usage; exit 1 ;;
    esac
    shift
done

# 메인 로직
function main() {
    echo "install start"
    pip install --upgrade pip -q
    pip install -U semgrep -q
    pip install -U python-dotenv -q
    pip install -U jmespath -q
    pip install -U PyYAML -q
    pip install -U pytest -q
    pip install -U slither-analyzer -q
    pip install -U openai -q
    pip freeze --require-virtualenv > requirements.txt
    echo "installed successfully"
}

# 스크립트 시작점
set -e
main




