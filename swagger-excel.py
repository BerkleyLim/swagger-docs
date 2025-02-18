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

        # 🔹 OUT (응답 데이터) 추출
        if "responses" in details and "200" in details["responses"]:
            response_content = details["responses"]["200"].get("content", {})

            # 🔹 JSON 형식의 응답인지 확인
            if "application/json" in response_content:
                schema = response_content["application/json"].get("schema", {})

                # 🔹 schema가 object일 경우만 처리
                if schema.get("type") == "object" and "properties" in schema:
                    for key, value in schema["properties"].items():
                        output_data.append([
                            api_name, path, method.upper(), key,
                            "O", value.get("type", "Unknown"), "-", "-"
                        ])

# 🔹 DataFrame 생성
df_input = pd.DataFrame(input_data, columns=["API 명", "경로", "HTTP 메서드", "파라미터 코드", "필수여부", "자료형", "데이터 크기", "샘플데이터"])
df_output = pd.DataFrame(output_data, columns=["API 명", "경로", "HTTP 메서드", "파라미터 코드", "필수여부", "자료형", "데이터 크기", "샘플데이터"])

# 🔹 엑셀 파일 저장
with pd.ExcelWriter("interface.xlsx") as writer:
    df_input.to_excel(writer, sheet_name="INPUT", index=False)
    df_output.to_excel(writer, sheet_name="OUTPUT", index=False)

print("✅ 엑셀 인터페이스 정의서 생성 완료! 🚀")