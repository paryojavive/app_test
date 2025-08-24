# Simple Python Backend for Azure App Service

Azure App Service 배포 테스트를 위한 간단한 Python Flask 백엔드 애플리케이션입니다.

## 기능

- `/` - 홈페이지 (기본 정보 반환)
- `/health` - 헬스체크 엔드포인트
- `/api/echo` - POST 요청으로 받은 데이터를 에코
- `/api/info` - 애플리케이션 정보

## 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 애플리케이션 실행
python app.py
```

## Azure App Service 배포

### 1. Azure CLI를 사용한 배포

```bash
# Azure CLI 로그인
az login

# 리소스 그룹 생성 (필요시)
az group create --name myResourceGroup --location eastus

# App Service Plan 생성
az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku B1 --is-linux

# Web App 생성
az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name myPythonApp --runtime "PYTHON|3.9"

# 배포
az webapp deployment source config-zip --resource-group myResourceGroup --name myPythonApp --src <your-zip-file>
```

### 2. GitHub Actions를 사용한 배포

`.github/workflows/azure-deploy.yml` 파일을 참조하세요.

## 환경 변수

- `ENVIRONMENT`: 실행 환경 (development/production)
- `PORT`: 서버 포트 (기본값: 5000)

## 테스트

```bash
# 홈페이지 테스트
curl http://localhost:5000/

# 헬스체크 테스트
curl http://localhost:5000/health

# API 정보 테스트
curl http://localhost:5000/api/info

# Echo API 테스트
curl -X POST http://localhost:5000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello World"}'
```
