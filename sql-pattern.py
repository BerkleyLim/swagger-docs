import re
import os
from flask import Flask, send_file

app = Flask(__name__)

sql_ddl = """
CREATE TABLE apps (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NULL COMMENT '앱이름',
    code VARCHAR(255) NULL COMMENT '앱코드',
    description VARCHAR(255) NULL COMMENT '앱설명',
    company_name VARCHAR(255) NULL COMMENT '법인명',
    businessRegistrationNumber VARCHAR(20) NULL COMMENT '사업자번호',
    corporateRegistrationNumber VARCHAR(255) NULL COMMENT '법인등록번호',
    business VARCHAR(255) NULL COMMENT '업태',
    event VARCHAR(255) NULL COMMENT '종목',
    representative VARCHAR(255) NULL COMMENT '대표자',
    email VARCHAR(255) NULL COMMENT '이메일주소',
    website VARCHAR(255) NULL COMMENT '홈페이지주소',
    ProductName VARCHAR(255) NULL COMMENT '생산제품명',
    postalCode1 VARCHAR(255) NULL COMMENT '우편번호1',
    postalCode2 VARCHAR(255) NULL COMMENT '우편번호2',
    address VARCHAR(255) NULL COMMENT '주소',
    phone VARCHAR(255) NULL COMMENT '전화번호',
    fax VARCHAR(255) NULL COMMENT '팩스번호',
    rep_phone VARCHAR(255) NULL COMMENT '대표자 휴대폰',
    bankAccountNumber VARCHAR(255) NULL COMMENT '계좌번호',
    bank VARCHAR(255) NULL COMMENT '은행명',
    remark LONGTEXT NULL COMMENT '비고',
    creator_id INT NULL COMMENT '최초등록자 user id',
    updater_id INT NULL COMMENT '최종수정자 user id',
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    introduction VARCHAR(255) NULL COMMENT '기업소개문구',
    address2 VARCHAR(255) NULL COMMENT '주소2',
    address3 VARCHAR(255) NULL COMMENT '주소3',
    bank_holder VARCHAR(255) NULL COMMENT '예금주',
    smtp_host VARCHAR(255) NULL COMMENT 'smtp 메일 서버명',
    smtp_port VARCHAR(255) NULL COMMENT 'smtp 메일 포트',
    smtp_username VARCHAR(255) NULL COMMENT 'smtp 메일 계정',
    smtp_password VARCHAR(255) NULL COMMENT 'smtp 메일 비밀번호'
);
"""

# ✅ 테이블명 추출 (정확한 테이블명만 추출)
table_name_match = re.search(r"CREATE TABLE\s+(\w+)", sql_ddl, re.IGNORECASE)
table_name = table_name_match.group(1).lower() if table_name_match else "unknown_table"

# ✅ 컬럼 정보 추출 (줄바꿈 포함 처리)
columns = re.findall(
    r"(\w+)[\s\n]+([\w\(\)\s]+(?:\s+UNSIGNED)?(?:\s+AUTO_INCREMENT)?(?:\s+PRIMARY KEY)?)"
    r"(?:[\s\n]+NULL)?(?:[\s\n]+COMMENT\s+'(.*?)')?",
    sql_ddl, re.IGNORECASE
)

# ✅ XML 템플릿 생성
xml_output = f"""<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
        xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
    http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.8.xsd">

    <!-- 1. 테이블 생성 -->
    <changeSet id="1" author="baseon">
        <preConditions onFail="MARK_RAN">
            <not>
                <tableExists tableName="{table_name}"/>
            </not>
        </preConditions>
        <createTable tableName="{table_name}">
"""

# ✅ 컬럼 추가 (대소문자 통일 및 COMMENT 필터링)
for col_name, col_type, col_comment in columns:
    col_name = col_name.lower()  # 컬럼명 소문자로 변환
    comment = f' remarks="{col_comment}"' if col_comment else ""
    xml_output += f'            <column name="{col_name}" type="{col_type}"{comment}/>\n'

xml_output += """        </createTable>
    </changeSet>\n\n

    <!-- ############## 개별 컬럼 추가 ############### -->"""


# ✅ 개별 컬럼 추가 (불필요한 컬럼 제외)
change_set_id = 2
excluded_columns = {
    "id", "code", "name", "remark", "creator_id", "updater_id", "deleted_at", "created_at", "updated_at"
}

for col_name, col_type, col_comment in columns:
    col_name = col_name.lower()  # 컬럼명 소문자로 변환

    if col_name not in excluded_columns:
        comment = f' remarks="{col_comment}"' if col_comment else ""
        xml_output += f"""
    <!-- {change_set_id}. {col_comment if col_comment else col_name} 컬럼 추가 -->
    <changeSet id="{change_set_id}" author="baseon">
        <preConditions onFail="MARK_RAN">
            <not>
                <columnExists tableName="{table_name}" columnName="{col_name}"/>
            </not>
        </preConditions>
        <addColumn tableName="{table_name}">
            <column name="{col_name}" type="{col_type}"{comment}/>
        </addColumn>
    </changeSet>
"""
        change_set_id += 1

xml_output += "</databaseChangeLog>"

# 콘솔 출력
print(xml_output)


####### 아래는 웹을 통한 다운로드 #########
# XML 파일 저장 경로
file_path = f"{table_name}_changelog.xml"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(xml_output)

# 파일 다운로드 경로 출력
print(f"파일 다운로드: sandbox:{file_path}")

# @app.route("/download")
# def download_file():
#     """ 파일 다운로드를 위한 API """
#     return send_file(file_path, as_attachment=True)
#
#
# if __name__ == "__main__":
#     # Flask 서버 실행
#     print(f"Download XML at: http://127.0.0.1:5000/download")
#     app.run(debug=True, port=5000)