import json
import pandas as pd

# 🔹 Swagger JSON 파일 로드
with open("api-docs.json", "r", encoding="utf-8") as f:
    swagger_data = json.load(f)

# 🔹 IN/OUT 데이터 저장할 리스트
input_data = []
output_data = []

# 🔹 API 경로별로 데이터 추출
for path, methods in swagger_data["paths"].items():
    for method, details in methods.items():
        api_name = details.get("summary", path)  # API 이름 (없으면 경로 사용)

        # 🔹 IN (요청 파라미터) 추출
        if "parameters" in details:
            for param in details["parameters"]:
                input_data.append([
                    api_name, path, method.upper(), param["name"],
                    "O" if param.get("required", False) else "",
                    param.get("schema", {}).get("type", "Unknown"),  # 'schema'가 없으면 'Unknown' 처리
                    "-", "-"
                ])

        # 🔹 REQUEST BODY 처리 (PUT, POST 등에서 사용)
        if "requestBody" in details:
            request_body = details["requestBody"].get("content", {}).get("application/json", {})
            schema = request_body.get("schema", {})
            if schema.get("type") == "object" and "properties" in schema:
                for key, value in schema["properties"].items():
                    input_data.append([
                        api_name, path, method.upper(), key,
                        "O", value.get("type", "Unknown"), "-", "-"
                    ])
            elif schema.get("type") == "array":
                items = schema.get("items", {})
                if items.get("type") == "object" and "properties" in items:
                    for key, value in items["properties"].items():
                        input_data.append([
                            api_name, path, method.upper(), key,
                            "O", value.get("type", "Unknown"), "-", "-"
                        ])
            else:
                input_data.append([
                    api_name, path, method.upper(), "Body",
                    "O", schema.get("type", "Unknown"), "-", "-"
                ])

        # 🔹 OUT (응답 데이터) 추출
        if "responses" in details:
            for status_code, response in details["responses"].items():
                response_content = response.get("content", {})

                if "application/json" in response_content:
                    schema = response_content["application/json"].get("schema", {})

                    # 🔹 schema가 object일 경우
                    if schema.get("type") == "object" and "properties" in schema:
                        for key, value in schema["properties"].items():
                            output_data.append([
                                api_name, path, method.upper(), key,
                                "O", value.get("type", "Unknown"), "-", "-"
                            ])

                    # 🔹 schema가 없고 example만 있는 경우
                    elif "example" in response_content["application/json"]:
                        example_data = response_content["application/json"]["example"]
                        for key, value in example_data.items():
                            output_data.append([
                                api_name, path, method.upper(), key,
                                "O", type(value).__name__, "-", "-"
                            ])

                    # 🔹 아무 데이터도 없을 경우 기본 응답 추가
                    else:
                        output_data.append([
                            api_name, path, method.upper(), "응답 없음",
                            "-", "-", "-", "-"
                        ])

# 🔹 DataFrame 생성
df_input = pd.DataFrame(input_data, columns=["API 명", "경로", "HTTP 메서드", "파라미터 코드", "필수여부", "자료형", "데이터 크기", "샘플데이터"])
df_output = pd.DataFrame(output_data, columns=["API 명", "경로", "HTTP 메서드", "파라미터 코드", "필수여부", "자료형", "데이터 크기", "샘플데이터"])

# 🔹 엑셀 파일 저장 (engine="openpyxl" 추가!)
with pd.ExcelWriter("interface.xlsx", engine="openpyxl") as writer:
    df_input.to_excel(writer, sheet_name="INPUT", index=False)
    df_output.to_excel(writer, sheet_name="OUTPUT", index=False)

print("✅ 엑셀 인터페이스 정의서 생성 완료! 🚀")