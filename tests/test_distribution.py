import os
import shutil
import datetime
import unittest
from core.distribution import MailDistributionContext, ExcelParser, HtmlTableRenderer, TemplateEngine

class TestMailDistributionContext(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_run_env"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        self.logs_dir = "logs"
        if os.path.exists(self.logs_dir):
            shutil.rmtree(self.logs_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.logs_dir):
            shutil.rmtree(self.logs_dir)

    def test_log_cleanup_retention(self):
        """7일 보존 기한이 지난 감사 로그 파일만 안전하게 자동 삭제되는지 자가 클린업 검증."""
        # 1. logs 폴더 및 더미 로그 파일 생성
        os.makedirs(self.logs_dir, exist_ok=True)
        
        old_log = os.path.join(self.logs_dir, "distribution_20260610_000000.log")
        new_log = os.path.join(self.logs_dir, "distribution_20260628_000000.log")
        
        with open(old_log, "w", encoding="utf-8") as f:
            f.write("Old Log Content")
        with open(new_log, "w", encoding="utf-8") as f:
            f.write("New Log Content")
            
        # 2. 파일 수정 시간 조작 (old_log를 10일 전으로 설정)
        now = datetime.datetime.now()
        old_time = (now - datetime.timedelta(days=10)).timestamp()
        new_time = now.timestamp()
        
        os.utime(old_log, (old_time, old_time))
        os.utime(new_log, (new_time, new_time))
        
        # 3. MailDistributionContext 생성 및 자가 청소 실행
        context = MailDistributionContext("dummy.xlsx")
        context._cleanup_old_logs(retention_days=7)
        
        # 4. 결과 단언 (Assertion)
        try:
            self.assertFalse(os.path.exists(old_log), "10일 전 로그 파일은 자가 청소 정책에 의해 삭제되어야 합니다.")
            self.assertTrue(os.path.exists(new_log), "오늘 생성한 신규 로그 파일은 안전하게 유지되어야 합니다.")
        finally:
            context.close()

    def test_html_table_renderer(self):
        """HtmlTableRenderer가 인라인 CSS 스타일을 가진 미려한 표를 렌더링하는지 검증."""
        headers = ["제품코드", "수량", "단가"]
        renderer = HtmlTableRenderer(headers)
        
        rows = [
            {"제품코드": "P1001", "수량": 10, "단가": 5000},
            {"제품코드": "P1002", "수량": 5, "단가": 12000}
        ]
        
        html = renderer.render(rows)
        self.assertIn("<table", html)
        self.assertIn("번호", html)
        self.assertIn("P1001", html)
        self.assertIn("P1002", html)
        self.assertIn("solid windowtext 1.0pt", html)
        # 1과 2 번호가 표의 td에 정상 삽입되었는지 검증
        self.assertIn(">1</td>", html)
        self.assertIn(">2</td>", html)

    def test_template_engine(self):
        """TemplateEngine이 대소문자 무관하게 플레이스홀더 치환을 완료하는지 검증."""
        content = "안녕하세요, {{고객명}}님. 주문하신 내역: {{table}}."
        engine = TemplateEngine(content)
        
        replace_dict = {
            "고객명": "홍길동",
            "table": "<table>test</table>"
        }
        
        rendered = engine.render(replace_dict)
        self.assertEqual(rendered, "안녕하세요, 홍길동님. 주문하신 내역: <table>test</table>.")

    def test_strict_prefix_matching(self):
        """제품코드 매칭 시 '제품코드_' 규격을 지켜 이름이 겹치는 다른 제품의 파일이 오첨부되지 않는지 검증."""
        os.makedirs(self.test_dir, exist_ok=True)
        valid_file = os.path.join(self.test_dir, "P1003_MSDS.pdf")
        invalid_file = os.path.join(self.test_dir, "P1003000000123.pdf")
        
        with open(valid_file, "w") as f: f.write("valid")
        with open(invalid_file, "w") as f: f.write("invalid")
        
        excel_path = os.path.join(self.test_dir, "temp_rec.xlsx")
        import openpyxl
        wb = openpyxl.Workbook()
        ws_rec = wb.active
        ws_rec.title = "Recipients"
        ws_rec.append(["To", "Subject", "Body"])
        ws_rec.append(["target@example.com", "Test", "Content"])
        
        ws_tbl = wb.create_sheet("TableData")
        ws_tbl.append(["Email", "제품코드", "제품명"])
        ws_tbl.append(["target@example.com", "P1003", "알파"])
        
        wb.save(excel_path)
        wb.close()
        
        context = MailDistributionContext(excel_path, msds_dir=self.test_dir)
        try:
            jobs = context.load_jobs()
            self.assertEqual(len(jobs), 1)
            attachments = jobs[0].attachments
            self.assertTrue(any("P1003_MSDS.pdf" in path for path in attachments))
            self.assertFalse(any("P1003000000123.pdf" in path for path in attachments))
        finally:
            context.close()

    def test_mail_signature_injection(self):
        """기본 signature.html 또는 커스텀 서명 파일이 존재할 때 본문 최하단에 서명이 자동 결합되는지 검증."""
        os.makedirs(self.test_dir, exist_ok=True)
        sig_file = os.path.join(self.test_dir, "custom_sig.html")
        with open(sig_file, "w", encoding="utf-8") as f:
            f.write("<div class='sig'>Best Regards, Sun Chemical.</div>")
            
        excel_path = os.path.join(self.test_dir, "temp_sig_rec.xlsx")
        import openpyxl
        wb = openpyxl.Workbook()
        ws_rec = wb.active
        ws_rec.title = "Recipients"
        ws_rec.append(["To", "Subject", "Body"])
        ws_rec.append(["sig_test@example.com", "Hello Subject", "Here is main body."])
        wb.save(excel_path)
        wb.close()
        
        # signature_path 주입하여 생성
        context = MailDistributionContext(excel_path, msds_dir=self.test_dir, signature_path=sig_file)
        try:
            jobs = context.load_jobs()
            self.assertEqual(len(jobs), 1)
            # 본문에 서명 내용이 정상 병합되어 랩핑되었는지 검사
            self.assertIn("Here is main body.", jobs[0].body)
            self.assertIn("Best Regards, Sun Chemical.", jobs[0].body)
        finally:
            context.close()

    def test_mail_signature_default_fallback_search(self):
        """--signature를 지정하지 않았을 때, signature/signature.html 또는 signature.html을 예비 탐색해 로드하는지 검증."""
        os.makedirs(os.path.join(self.test_dir, "signature"), exist_ok=True)
        sig_file = os.path.join(self.test_dir, "signature", "signature.html")
        with open(sig_file, "w", encoding="utf-8") as f:
            f.write("<div class='sig'>Best Regards, Fallback.</div>")
            
        excel_path = os.path.join(self.test_dir, "temp_fallback_rec.xlsx")
        import openpyxl
        wb = openpyxl.Workbook()
        ws_rec = wb.active
        ws_rec.title = "Recipients"
        ws_rec.append(["To", "Subject", "Body"])
        ws_rec.append(["fallback@example.com", "Hello", "Body content"])
        wb.save(excel_path)
        wb.close()
        
        # signature_path를 지정하지 않고, 작업 디렉토리가 아닌 msds_dir 등 우회는 없으므로
        # load_jobs의 CWD 탐색을 위해 signature/signature.html 로컬 파일을 생성하고 직접 테스트
        # 실제 로컬 signature/signature.html 생성을 시뮬레이션하기 위해
        # MailDistributionContext 내부 경로를 mock하거나 혹은 OS CWD를 기반으로 signature/signature.html에 임시 생성
        # (주의: 실제 루트의 signature/signature.html을 덮어쓰지 않도록, os.chdir 등을 임시 적용)
        import sys
        old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        context = MailDistributionContext("temp_fallback_rec.xlsx")
        try:
            # test_dir 내에 signature/signature.html이 있으므로 CWD=test_dir 상태에서 signature_path 미지정 구동
            jobs = context.load_jobs()
            self.assertEqual(len(jobs), 1)
            self.assertIn("Best Regards, Fallback.", jobs[0].body)
        finally:
            context.close()
            os.chdir(old_cwd)

    def test_mail_bcc_parsing_and_mapping(self):
        """엑셀 Recipients 시트에 Bcc 컬럼이 존재할 때 MailJob.bcc 에 올바르게 주입되는지 검증."""
        os.makedirs(self.test_dir, exist_ok=True)
        excel_path = os.path.join(self.test_dir, "temp_bcc_rec.xlsx")
        import openpyxl
        wb = openpyxl.Workbook()
        ws_rec = wb.active
        ws_rec.title = "Recipients"
        ws_rec.append(["To", "Cc", "Bcc", "Subject", "Body"])
        ws_rec.append(["target@example.com", "cc@example.com", "bcc1@example.com;bcc2@example.com", "Bcc Test", "Body content"])
        wb.save(excel_path)
        wb.close()
        
        context = MailDistributionContext(excel_path, msds_dir=self.test_dir)
        try:
            jobs = context.load_jobs()
            self.assertEqual(len(jobs), 1)
            self.assertEqual(jobs[0].bcc_addr, "bcc1@example.com;bcc2@example.com")
        finally:
            context.close()


if __name__ == "__main__":
    unittest.main()
