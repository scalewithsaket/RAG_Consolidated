# Deployment Guide: Production RAG Application

## 🎯 Deployment Options

1. **Docker Containers** (Recommended for Phase 4)
2. **AWS Lambda + API Gateway** (Serverless)
3. **AWS ECS/Fargate** (Container orchestration)
4. **Kubernetes** (Advanced)

---

## 1. Docker Deployment

### Backend Dockerfile

**backend/Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY data/ ./data/

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

**frontend/Dockerfile:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Production image
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**frontend/nginx.conf:**
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: rag-backend
    ports:
      - "8000:8000"
    environment:
      - AWS_REGION=${AWS_REGION}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - KNOWLEDGE_BASE_ID=${KNOWLEDGE_BASE_ID}
    volumes:
      - ./backend/data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: rag-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  chroma_data:
```

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Push to Docker Hub

```bash
# Tag images
docker tag rag-backend:latest yourusername/rag-backend:v1.0
docker tag rag-frontend:latest yourusername/rag-frontend:v1.0

# Push to Docker Hub
docker push yourusername/rag-backend:v1.0
docker push yourusername/rag-frontend:v1.0
```

---

## 2. AWS Lambda Deployment (Serverless)

### Lambda Function Structure

```
lambda/
├── backend/
│   ├── src/
│   ├── requirements.txt
│   └── lambda_handler.py
└── layers/
    └── dependencies/
```

### Lambda Handler

**lambda_handler.py:**
```python
import json
from mangum import Mangum
from src.main import app

# Wrap FastAPI with Mangum for Lambda
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """AWS Lambda handler"""
    return handler(event, context)
```

### Requirements for Lambda

**requirements.txt:**
```
fastapi==0.109.0
mangum==0.17.0
boto3==1.34.0
pydantic==2.5.0
```

### Build Lambda Package

```bash
# Create deployment package
mkdir lambda-package
cd lambda-package

# Install dependencies
pip install -r requirements.txt -t .

# Copy source code
cp -r ../src .
cp ../lambda_handler.py .

# Create zip
zip -r lambda-function.zip .
```

### Deploy with AWS CLI

```bash
# Create Lambda function
aws lambda create-function \
  --function-name rag-backend \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda-function.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{KNOWLEDGE_BASE_ID=ABCD1234}"

# Update function code
aws lambda update-function-code \
  --function-name rag-backend \
  --zip-file fileb://lambda-function.zip
```

### API Gateway Setup

```bash
# Create REST API
aws apigateway create-rest-api \
  --name rag-api \
  --description "RAG Backend API"

# Create resource
aws apigateway create-resource \
  --rest-api-id API_ID \
  --parent-id ROOT_ID \
  --path-part query

# Create POST method
aws apigateway put-method \
  --rest-api-id API_ID \
  --resource-id RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE

# Integrate with Lambda
aws apigateway put-integration \
  --rest-api-id API_ID \
  --resource-id RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:REGION:lambda:path/2015-03-31/functions/LAMBDA_ARN/invocations

# Deploy API
aws apigateway create-deployment \
  --rest-api-id API_ID \
  --stage-name prod
```

### Terraform for Lambda (IaC)

**terraform/lambda.tf:**
```hcl
resource "aws_lambda_function" "rag_backend" {
  filename         = "lambda-function.zip"
  function_name    = "rag-backend"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_handler.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 512

  environment {
    variables = {
      KNOWLEDGE_BASE_ID = var.knowledge_base_id
      AWS_REGION       = var.aws_region
    }
  }
}

resource "aws_api_gateway_rest_api" "rag_api" {
  name        = "rag-api"
  description = "RAG Backend API"
}

resource "aws_api_gateway_deployment" "prod" {
  rest_api_id = aws_api_gateway_rest_api.rag_api.id
  stage_name  = "prod"
}
```

---

## 3. AWS ECS/Fargate Deployment

### Task Definition

**ecs-task-definition.json:**
```json
{
  "family": "rag-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "yourusername/rag-backend:v1.0",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KNOWLEDGE_BASE_ID",
          "value": "ABCD1234"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/rag-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Deploy to ECS

```bash
# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json

# Create ECS cluster
aws ecs create-cluster --cluster-name rag-cluster

# Create service
aws ecs create-service \
  --cluster rag-cluster \
  --service-name rag-backend-service \
  --task-definition rag-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## 4. Frontend Deployment (S3 + CloudFront)

### Build Frontend

```bash
cd frontend
npm run build
# Creates dist/ folder
```

### Deploy to S3

```bash
# Create S3 bucket
aws s3 mb s3://rag-frontend-bucket

# Enable static website hosting
aws s3 website s3://rag-frontend-bucket \
  --index-document index.html \
  --error-document index.html

# Upload files
aws s3 sync dist/ s3://rag-frontend-bucket --delete

# Set public read policy
aws s3api put-bucket-policy \
  --bucket rag-frontend-bucket \
  --policy file://bucket-policy.json
```

**bucket-policy.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::rag-frontend-bucket/*"
    }
  ]
}
```

### CloudFront Distribution

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name rag-frontend-bucket.s3.amazonaws.com \
  --default-root-object index.html
```

**Terraform for S3 + CloudFront:**
```hcl
resource "aws_s3_bucket" "frontend" {
  bucket = "rag-frontend-bucket"
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "S3-rag-frontend"
  }

  enabled             = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-rag-frontend"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
```

---

## 5. CI/CD Pipeline

### GitHub Actions

**.github/workflows/deploy.yml:**
```yaml
name: Deploy RAG Application

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/

  build-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: rag-backend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd backend
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster rag-cluster \
            --service rag-backend-service \
            --force-new-deployment

  build-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install and build
        run: |
          cd frontend
          npm ci
          npm run build
      
      - name: Deploy to S3
        run: |
          aws s3 sync frontend/dist/ s3://rag-frontend-bucket --delete
      
      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"
```

### GitLab CI/CD

**.gitlab-ci.yml:**
```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - cd backend
    - pip install -r requirements.txt
    - pip install pytest
    - pytest tests/

build-backend:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - cd backend
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA

deploy-backend:
  stage: deploy
  image: amazon/aws-cli
  script:
    - aws ecs update-service --cluster rag-cluster --service rag-backend-service --force-new-deployment
  only:
    - main
```

---

## 6. Monitoring & Logging

### CloudWatch Logs

**backend/src/main.py:**
```python
import logging
import watchtower

# Configure CloudWatch logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = watchtower.CloudWatchLogHandler(
    log_group='/rag/backend',
    stream_name='application'
)
logger.addHandler(handler)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

### CloudWatch Metrics

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def log_metric(metric_name, value):
    cloudwatch.put_metric_data(
        Namespace='RAG/Application',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': 'Count'
            }
        ]
    )

# Usage
log_metric('QueryCount', 1)
log_metric('ResponseTime', response_time)
```

### Application Performance Monitoring

**Using AWS X-Ray:**
```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

xray_recorder.configure(service='RAG-Backend')
XRayMiddleware(app, xray_recorder)

@xray_recorder.capture('query_knowledge_base')
def query_kb(question):
    # Your code here
    pass
```

---

## 7. Security Best Practices

### Environment Variables

```bash
# Never commit secrets!
# Use AWS Secrets Manager

aws secretsmanager create-secret \
  --name rag/credentials \
  --secret-string '{"api_key":"xxx","db_password":"yyy"}'
```

**Retrieve in code:**
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secret('rag/credentials')
```

### IAM Roles

**Lambda execution role:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock-agent-runtime:Retrieve",
        "bedrock-agent-runtime:RetrieveAndGenerate"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### API Authentication

**Add JWT authentication:**
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/query")
async def query_endpoint(request: QueryRequest, user=Depends(verify_token)):
    # Only authenticated users can query
    pass
```

---

## 8. Cost Optimization

### Auto-scaling

**ECS Auto-scaling:**
```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/rag-cluster/rag-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/rag-cluster/rag-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

### Lambda Reserved Concurrency

```bash
# Limit concurrent executions to control costs
aws lambda put-function-concurrency \
  --function-name rag-backend \
  --reserved-concurrent-executions 10
```

### CloudFront Caching

```javascript
// Cache static assets
const cacheControl = {
  'text/html': 'max-age=300',
  'application/javascript': 'max-age=31536000',
  'text/css': 'max-age=31536000',
  'image/*': 'max-age=31536000'
};
```

---

## 🎯 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Secrets stored in AWS Secrets Manager
- [ ] IAM roles created
- [ ] Docker images built and tested

### Deployment
- [ ] Backend deployed (Lambda/ECS/Docker)
- [ ] Frontend deployed (S3 + CloudFront)
- [ ] API Gateway configured
- [ ] DNS records updated
- [ ] SSL certificate installed

### Post-Deployment
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Logs flowing to CloudWatch
- [ ] Alerts configured
- [ ] Load testing completed
- [ ] Documentation updated

---

## 📊 Deployment Comparison

| Method | Complexity | Cost | Scalability | Best For |
|--------|-----------|------|-------------|----------|
| Docker | Low | Low | Medium | Development |
| Lambda | Medium | Low | High | Serverless |
| ECS/Fargate | Medium | Medium | High | Production |
| Kubernetes | High | High | Very High | Enterprise |

---

**Next: Testing Guide!** 🧪
