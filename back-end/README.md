# Django Project

A REST API for managing Alert and Report features, also acting as a proxy to the DO Estimator service.

## Project Structure

| File/Folder | Description |
|-------------|-------------|
| .github/workflows | GitHub CI/CD workflows |
| backend/ | Main Django source code |
| deploy/ | Terminal scripts to deploy the app on ECS |
| infra/ | Terraform scripts to provision AWS ECS infrastructure |
| utils/ | Python scripts for BASE64 encoding/decoding |
| docker-compose.yml | Docker Compose environment setup |
| Dockerfile | Docker container definition for the Django app |
| entrypoint.sh | Script to bootstrap Django correctly inside Docker |
| env-template.env | Template for generating a valid `.env` file |
| requirements.txt | Python project dependencies |
| smartrural_django_backend.postman_collection.json | Postman collection for testing the API |

## Environment Variables

See [env-template.env](env-template.env) for an example.

| Variable | Description |
|----------|-------------|
| SECRET_KEY | Django secret key used for cryptographic signing. |
| DEBUG | Enables debug mode (True for dev, False for prod). |
| DB_ENGINE | Django database backend (e.g., `django.db.backends.postgresql`). |
| DB_NAME | Database name. |
| DB_USER | Database username. |
| DB_PASSWORD | Database password. |
| DB_HOST | Database host address. |
| DB_PORT | Database port number. |
| ALLOWED_HOSTS | Comma-separated list of allowed hosts. |
| CORS_ALLOW_ALL_ORIGINS | Whether CORS is allowed for all origins. |
| CORS_ALLOW_CREDENTIALS | Whether credentials are allowed in CORS. |
| TB_URL | Base URL for ThingsBoard API. |
| TB_USERNAME | ThingsBoard username. |
| TB_PASSWORD | ThingsBoard password. |
| AWS_S3_BUCKET | AWS S3 bucket name. |
| AWS_S3_REGION | AWS region for the S3 bucket. |
| AWS_ACCESS_KEY_ID | AWS access key. |
| AWS_SECRET_ACCESS_KEY | AWS secret access key. |
| FIREBASE_BASE64_CREDS | Base64-encoded Firebase service account JSON. See [Firebase Config](#firebase-config). |
| DO_LSTM_ESTIMATOR_CONTAINER_URL | AWS ECR URL of the DO LSTM container. |
| DO_LSTM_ESTIMATOR_URL | URL of the DO LSTM Estimator API. |
| WHATSAPP_API_PHONE_NUMBER_ID | WhatsApp phone number ID from Facebook Developer. |
| WHATSAPP_API_ACCESS_TOKEN | WhatsApp API access token. |
| WHATSAPP_RECIPIENT_LIST | Comma-separated list of WhatsApp recipient phone numbers. |
| DJANGO_BACKEND_USERNAME | Username for Django API authentication. |
| DJANGO_BACKEND_PASSWORD | Password for Django API authentication. |
| DJANGO_BACKEND_URL | URL of the Django backend API. |

### Firebase Config

1. Create a `.env` file at the root of the repository.
2. In Firebase Console, go to `Project Settings > Service Accounts`.
3. Under `Firebase Admin SDK`, click `Generate New Private Key`. Download the JSON key and place it in the `utils/` directory.
4. In `utils/encode_to_base64.py`, set the variable `file_path` to the name of the JSON file.
5. Run the encoding script:
   ```bash
   cd utils
   python encode_to_base64.py
   ```
6. Copy the Base64 output and paste it into `.env` as:
   ```env
   FIREBASE_BASE64_CREDS='<base64-output>'
   ```

---

## Development Setup

### 1. Start PostgreSQL container

#### Windows
```powershell
mkdir C:\docker\postgres_data
docker run -d --name postgres-django -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -v C:\docker\postgres_data:/var/lib/postgresql/data -p 5432:5432 postgres:16.4
```

#### Linux
```bash
mkdir -p ~/docker/postgres_data
docker run -d --name postgres-django -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -v ~/docker/postgres_data:/var/lib/postgresql/data -p 5432:5432 postgres:16.4
```

### 2. Install Python dependencies

Create and activate virtual env
```bash
pip install virtualenv
virtualenv env
# Windows
.env\Scripts\activate
# Linux/macOS
source env/bin/activate
```

Installing dependencies
```bash
pip install -r requirements.txt
pip install .\python_modules\smartrural_thingsboard_services\
pip install .\python_modules\smartrural_firebase_services\
```

### 3. Django Setup

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```
Access the [admin page](http://localhost:8000/admin/) to manage users.

### 4. Create your `.env` file in the project root

### 5. Run the Django development server
```bash
python manage.py runserver
```

### 6. Useful Django commands

- Start development server: `python manage.py runserver`
- Run tests: `python manage.py test`
- Create app: `python manage.py startapp <app_name>`
- Create migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`

---

## Production Setup

### Option 1: AWS EC2

Assuming a PostgreSQL 16.4 instance is available and accessible:

1. Launch a VM and configure firewall rules:
   - Allow outbound port `TCP 8000`
   - Allow all inbound traffic
2. Clone the repository inside the VM
3. Create the `.env` file with the correct database credentials
4. Make sure the VM can connect to the database
5. Run the service:

```bash
docker-compose up -d --build
```

### Option 2 (Recommended): AWS ECS (Fargate)

Provision infrastructure and deploy the aplication in elastic container service (ECS). This method handles self scalable aplication already with https configured. This is divided in three steps: (1) creating the application https certificate; (2) creation AWS core ECS + RDS infra to run the services; and (3) deploying the services in ECR and buiding a ECS service with the container.

**Requirements**: 
- AWS CLI configured (AWS admin privileges)
- Terraform 1.11.2+

#### Step 1: HTTPS config with AWS Certificate Manager (ACM)

Init terraform
```bash
cd infra/1_https_cert
terraform init
```

Say we've choosen the subdomain `example.smartrural.com.br` for our backend. Create a file named `terraform.tfvars` like this in the current directory:
```hcl
app_subdomain = "example.smartrural.com.br"
```

Planning and creating certificate
```bash
terraform plan -out=tfplan
terraform apply "tfplan"
```

The output of this will be the DNS records you need to place in the DNS zones and the ARN of the certificate created. Output of this command will be something like this:

```bash
acm_cert_arn
   value = arn:aws:acm:us-east-1:1234567:certificate/aaaaaaaa-bbbb-cccc-ddddddddd

acm_dns_validation_records
   name  = _dfcf1e0f61ed490e236c8625f0f6ffb5.example.smartrural.com.br.
   type  = CNAME
   value = _050ba572e0414b568af4f4a86ba884d2.armvlfgvlj.acm-validations.aws.
```

The configuration in the DNS zones needs to be something like this:

|Tipo	|Nome	|Dados|
|--|--|--|
|CNAME|_dfcf1e0f61ed490e236c8625f0f6ffb5.test-123456789.smartrural.com.br|_050ba572e0414b568af4f4a86ba884d2.armvlfgvlj.acm-validations.aws.|

Wait until the AWS ACM verify the DNS records and display the certificate status as **Issued**. Then, follow for the next steps

#### Step 2: Infrastructure (Terraform)

Init terraform
```bash
cd infra/2_infra_core
terraform init
```

Create a file named `terraform.tfvars` and fill the desired name of the RDS DB, choose a very strong password and save somewhere safe. Also, retrieve the ACM certificate ARN created in the previous step. Set the file as below:
```hcl
db_password = "MySuperSecurePassword123!"

certificate_arn = "arn:aws:acm:us-east-1:1234567:certificate/aaaaaaaa-bbbb-cccc-ddddddddd"
```

Then run:
```bash
terraform plan -out=tfplan
terraform apply tfplan
```

The infra will be created. Use the output data of this command and some credentials as below to create the application .env. Follow the steps of [Environment Variables](#environment-variables):
- **s3_bucket_name**
- **alb_dns_name**
- **rds_endpoint**
- **rds_port**
- **db_password**
- **db_user** = postgres
- **db_name** = postgres

#### Step 3: ECS Deployment

🚧 **TODO:** Deployment instructions will be added here..

