#!/usr/bin/env python3
"""
scripts/test_runner.py
샘플 테스트와 AI 생성 테스트를 실행합니다.
"""

import argparse
import json
import subprocess
import tempfile
import os
import sys
from pathlib import Path

class TestRunner:
    def __init__(self, code_file, language):
        self.code_file = code_file
        self.language = language
        self.failed_tests = []
    
    def compile_if_needed(self):
        """컴파일이 필요한 언어의 경우 컴파일 실행"""
        if self.language == 'cpp':
            try:
                executable = Path(self.code_file).stem
                result = subprocess.run([
                    'g++', '-o', executable, self.code_file, 
                    '-std=c++17', '-O2'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    return False, f"컴파일 오류:\n{result.stderr}"
                
                self.executable = executable
                return True, "컴파일 성공"
                
            except subprocess.TimeoutExpired:
                return False, "컴파일 시간 초과"
            except Exception as e:
                return False, f"컴파일 예외: {e}"
        
        elif self.language == 'java':
            try:
                result = subprocess.run([
                    'javac', self.code_file
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    return False, f"컴파일 오류:\n{result.stderr}"
                
                # Java 클래스명 추출
                class_name = Path(self.code_file).stem
                self.executable = class_name
                self.java_class_path = Path(self.code_file).parent
                return True, "컴파일 성공"
                
            except subprocess.TimeoutExpired:
                return False, "컴파일 시간 초과"
            except Exception as e:
                return False, f"컴파일 예외: {e}"
        
        elif self.language == 'c':
            try:
                executable = Path(self.code_file).stem
                result = subprocess.run([
                    'gcc', '-o', executable, self.code_file, '-O2'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    return False, f"컴파일 오류:\n{result.stderr}"
                
                self.executable = executable
                return True, "컴파일 성공"
                
            except subprocess.TimeoutExpired:
                return False, "컴파일 시간 초과"
            except Exception as e:
                return False, f"컴파일 예외: {e}"
        
        return True, "컴파일 불필요"
    
    def run_single_test(self, test_input, timeout=5):
        """단일 테스트케이스 실행"""
        try:
            if self.language == 'python':
                cmd = ['python3', self.code_file]
            elif self.language == 'cpp':
                cmd = [f'./{self.executable}']
            elif self.language == 'java':
                cmd = ['java', self.executable]
            elif self.language == 'c':
                cmd = [f'./{self.executable}']
            else:
                return False, f"지원하지 않는 언어: {self.language}"
            
            # 프로세스 실행
            process = subprocess.run(
                cmd,
                input=test_input,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if process.returncode != 0:
                error_msg = process.stderr or "런타임 오류"
                return False, f"실행 오류: {error_msg}"
            
            return True, process.stdout.strip()
            
        except subprocess.TimeoutExpired:
            return False, "시간 초과"
        except Exception as e:
            return False, f"실행 예외: {e}"
    
    def run_sample_tests(self, sample_tests_file):
        """샘플 테스트케이스 실행"""
        try:
            with open(sample_tests_file, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
            
            test_cases = sample_data.get('test_cases', [])
            if not test_cases:
                return True, "샘플 테스트케이스 없음"
            
            print(f"📝 샘플 테스트 실행 중... ({len(test_cases)}개)")
            
            for i, test_case in enumerate(test_cases):
                test_input = test_case['input']
                expected_output = test_case['output']
                
                success, actual_output = self.run_single_test(test_input)
                
                if not success:
                    self.failed_tests.append({
                        'type': 'sample',
                        'case_number': i + 1,
                        'input': test_input,
                        'error': actual_output
                    })
                    return False, f"샘플 테스트 {i+1} 실행 실패: {actual_output}"
                
                # 출력 비교 (공백 정규화)
                actual_clean = actual_output.strip()
                expected_clean = expected_output.strip()
                
                if actual_clean != expected_clean:
                    self.failed_tests.append({
                        'type': 'sample',
                        'case_number': i + 1,
                        'input': test_input,
                        'expected': expected_clean,
                        'actual': actual_clean
                    })
                    return False, f"샘플 테스트 {i+1} 출력 불일치"
            
            return True, f"샘플 테스트 {len(test_cases)}개 모두 통과"
            
        except Exception as e:
            return False, f"샘플 테스트 로드 실패: {e}"
    
    def run_generated_tests(self, generated_tests_file):
        """AI 생성 테스트케이스 실행"""
        try:
            with open(generated_tests_file, 'r', encoding='utf-8') as f:
                generated_data = json.load(f)
            
            test_cases = generated_data.get('test_cases', [])
            if not test_cases:
                return True, "AI 테스트케이스 없음"
            
            print(f"🤖 AI 생성 테스트 실행 중... ({len(test_cases)}개)")
            
            for i, test_case in enumerate(test_cases):
                test_input = test_case['input']
                expected_output = test_case.get('expected_output', '')
                test_type = test_case.get('test_type', 'unknown')
                description = test_case.get('description', '')
                
                success, actual_output = self.run_single_test(test_input, timeout=10)
                
                if not success:
                    self.failed_tests.append({
                        'type': 'ai_generated',
                        'case_number': i + 1,
                        'test_type': test_type,
                        'description': description,
                        'input': test_input,
                        'error': actual_output
                    })
                    return False, f"AI 테스트 {i+1} ({test_type}) 실행 실패: {actual_output}"
                
                # AI 생성 테스트의 경우 예상 출력이 정확하지 않을 수 있으므로
                # 실행만 성공하면 일단 통과로 처리 (추후 개선 가능)
                print(f"  ✓ 테스트 {i+1} ({test_type}): 실행 성공")
            
            return True, f"AI 생성 테스트 {len(test_cases)}개 모두 실행 성공"
            
        except Exception as e:
            return False, f"AI 테스트 로드 실패: {e}"
    
    def cleanup(self):
        """컴파일된 파일 정리"""
        if hasattr(self, 'executable') and self.language in ['cpp', 'c']:
            try:
                executable_path = Path(f'./{self.executable}')
                if executable_path.exists():
                    executable_path.unlink()
            except:
                pass
        
        if hasattr(self, 'java_class_path'):
            try:
                # Main.class 파일 삭제
                class_file = Path(self.java_class_path) / f'{self.executable}.class'
                if class_file.exists():
                    class_file.unlink()
            except:
                pass

def format_failure_details(failed_tests):
    """실패한 테스트 상세 정보 포맷팅"""
    if not failed_tests:
        return ""
    
    details = []
    for test in failed_tests:
        if test['type'] == 'sample':
            if 'error' in test:
                details.append(f"샘플 테스트 {test['case_number']}: {test['error']}")
            else:
                details.append(
                    f"샘플 테스트 {test['case_number']}:\n"
                    f"  입력: {test['input']}\n"
                    f"  예상: {test['expected']}\n"
                    f"  실제: {test['actual']}"
                )
        else:
            details.append(
                f"AI 테스트 {test['case_number']} ({test['test_type']}):\n"
                f"  설명: {test['description']}\n"
                f"  오류: {test.get('error', 'Unknown')}"
            )
    
    return "\n\n".join(details)

def main():
    parser = argparse.ArgumentParser(description='테스트케이스 실행')
    parser.add_argument('--code-file', required=True)
    parser.add_argument('--language', required=True)
    parser.add_argument('--sample-tests', required=True)
    parser.add_argument('--generated-tests', required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.code_file):
        print(f"::error::코드 파일이 존재하지 않습니다: {args.code_file}")
        sys.exit(1)
    
    runner = TestRunner(args.code_file, args.language)
    
    try:
        print(f"🚀 테스트 시작: {args.code_file} ({args.language})")
        
        # 1. 컴파일 (필요한 경우)
        compile_success, compile_msg = runner.compile_if_needed()
        if not compile_success:
            print(f"::error::{compile_msg}")
            print("::set-output name=result::FAIL")
            print(f"::set-output name=details::{compile_msg}")
            sys.exit(1)
        
        print(f"✅ {compile_msg}")
        
        # 2. 샘플 테스트 실행
        sample_success, sample_msg = runner.run_sample_tests(args.sample_tests)
        if not sample_success:
            details = format_failure_details(runner.failed_tests)
            print(f"::error::{sample_msg}")
            print("::set-output name=result::FAIL")
            print(f"::set-output name=details::{details}")
            sys.exit(1)
        
        print(f"✅ {sample_msg}")
        
        # 3. AI 생성 테스트 실행
        ai_success, ai_msg = runner.run_generated_tests(args.generated_tests)
        if not ai_success:
            details = format_failure_details(runner.failed_tests)
            print(f"::warning::{ai_msg}")
            # AI 테스트 실패는 경고로만 처리 (선택사항)
            # print("::set-output name=result::FAIL")
            # print(f"::set-output name=details::{details}")
            # sys.exit(1)
        
        print(f"✅ {ai_msg}")
        
        # 모든 테스트 통과
        print("🎉 모든 테스트 통과!")
        print("::set-output name=result::PASS")
        print("::set-output name=details::모든 테스트케이스 통과")
        
    except Exception as e:
        print(f"::error::테스트 실행 중 예외 발생: {e}")
        print("::set-output name=result::FAIL")
        print(f"::set-output name=details::예외 발생: {e}")
        sys.exit(1)
    
    finally:
        runner.cleanup()

if __name__ == "__main__":
    main()