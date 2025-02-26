import re

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

# 정규식을 이용해 컬럼 정보 추출
columns = re.findall(r"(\w+)\s+([\w\(\)]+)\s+NULL(?: COMMENT '(.*?)')?", sql_ddl, re.IGNORECASE)

# 기본 XML 템플릿
xml_output = """<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
        xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
    http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.8.xsd">

    <changeSet id="1" author="baseon">
        <preConditions onFail="MARK_RAN">
            <not>
                <tableExists tableName="apps"/>
            </not>
        </preConditions>
        <createTable tableName="apps">
"""

# 테이블 생성 부분 추가
for col_name, col_type, col_comment in columns:
    comment = f' remarks="{col_comment}"' if col_comment else ""
    xml_output += f'            <column name="{col_name}" type="{col_type}"{comment}/>\n'

xml_output += """        </createTable>
    </changeSet>\n"""

# 컬럼 추가 부분 추가
change_set_id = 2
for col_name, col_type, col_comment in columns:
    if col_name not in ["id", "code", "name", "remark", "creator_id", "updater_id", "deleted_at", "created_at", "updated_at"]:
        comment = f' remarks="{col_comment}"' if col_comment else ""
        xml_output += f"""
    <changeSet id="{change_set_id}" author="baseon">
        <preConditions onFail="MARK_RAN">
            <not>
                <columnExists tableName="apps" columnName="{col_name}"/>
            </not>
        </preConditions>
        <addColumn tableName="apps">
            <column name="{col_name}" type="{col_type}"{comment}/>
        </addColumn>
    </changeSet>
"""
        change_set_id += 1

xml_output += "</databaseChangeLog>"

# 결과 출력
print(xml_output)