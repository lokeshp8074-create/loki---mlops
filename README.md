# GradeCast: Student Marks Prediction

GradeCast is a small Flask application that estimates student marks with a scikit-learn Linear Regression model. It is an educational demonstration, not an official assessment or a guarantee of examination results.

**Reference note:** `MLOPS project.pdf` was not available in this workspace. This implementation follows the practical requirements supplied in the project prompt; exact PDF-specific compliance cannot be confirmed.

## Problem and Objective

The project demonstrates how to turn a trained machine-learning model into a local web application, package it with Docker, and prepare it for AWS EC2 deployment. It is limited to Practicals 1, 2, and 3. No Google Cloud Platform deployment is included.

## Model and Data

The model is ordinary least-squares Linear Regression. Its inputs are:

| Feature | Accepted range | Meaning |
| --- | ---: | --- |
| `study_hours_per_week` | 0-40 | Weekly study hours |
| `attendance_percentage` | 0-100 | Class attendance percentage |
| `previous_score` | 0-100 | Previous marks |

`train_model.py` creates 1,200 deterministic synthetic demonstration records with a fixed random seed. They are generated for this assignment and are not real student records. The script uses an 80/20 train/test split with a fixed split seed, fits Linear Regression, reports MAE, MSE, RMSE, and R-squared on the test split, and saves the estimator and feature names to `model.pkl` with joblib.

Verified run in the current environment (Python 3.11.9, scikit-learn 1.9.1):

| Test metric | Value |
| --- | ---: |
| MAE | 4.0093 marks |
| MSE | 25.1084 marks squared |
| RMSE | 5.0108 marks |
| R-squared | 0.8885 |

These are results on the generated test split, not evidence about real students or future exam outcomes.

## Technologies

- Python 3.11
- Flask for the web interface and HTTP endpoints
- scikit-learn and NumPy for training and prediction
- joblib for model serialization
- pytest for automated tests
- Waitress as the WSGI server in the Docker image
- Docker Desktop for local containerization (image and container lifecycle verified)
- AWS EC2 and GitHub deployment details are pending account/repository access

## Project Structure

```text
venky/
|-- .dockerignore
|-- .gitignore
|-- .venv/                 # Local environment; ignored by Git and Docker
|-- Dockerfile
|-- README.md
|-- app.py
|-- model.pkl              # Required trained model artifact
|-- requirements.txt
|-- static/style.css
|-- templates/index.html
|-- tests/test_app.py
`-- train_model.py
```

## Practical 1: Local Flask Application

Run these PowerShell commands from `C:\projects\venky`. The existing `.venv` is already configured in this workspace. On a clean checkout, create it once with `py -3.11 -m venv .venv`.

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe train_model.py
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5000
```

The verified test run passed 8 tests. The verified training run saved `model.pkl`. The local Flask server was started and tested over HTTP. Open <http://127.0.0.1:5000/> for the form.

If PowerShell says port 5000 is in use, stop the existing server with Ctrl+C in its terminal or use another local port, such as `--port 5001`.

### Endpoints

| Method and path | Purpose |
| --- | --- |
| `GET /` | Prediction form |
| `GET /health` | Returns JSON with service and model status |
| `POST /prediction` | Accepts form data or a JSON object and returns a prediction |

Example JSON request fields:

```json
{
  "study_hours_per_week": 12,
  "attendance_percentage": 88,
  "previous_score": 74
}
```

PowerShell API check:

```powershell
$payload = @{
    study_hours_per_week = 12
    attendance_percentage = 88
    previous_score = 74
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:5000/prediction" -Method Post -ContentType "application/json" -Body $payload
```

The route rejects missing, non-numeric, non-finite, and out-of-range values with HTTP 400 and field-specific messages. One verified form submission returned HTTP 200 and an estimate of 51.14 marks for the example inputs above. The health endpoint returned `{"model_loaded":true,"status":"ok"}`. The model is loaded from `model.pkl` when a fresh Flask process starts.

## Practical 2: Docker

The Dockerfile uses Python 3.11, installs `requirements.txt`, copies the trained `model.pkl`, runs as a non-root user, serves Flask with Waitress, and exposes port 5000. `.dockerignore` excludes local environments, caches, tests, credentials, and Git metadata while retaining the model.

**Verified:** `gradecast:1.0` built successfully. Image inspection reported ID `sha256:6b2f1671ba6c1e72e2f485dd7b1d1aa78ce992ec09c5767556e58b6a5dbc0e66`, Linux/amd64, exposed port 5000, and non-root user `gradecast`. The container returned HTTP 200 from `/health` with `model_loaded: true` and returned the real 51.14 form prediction for the example inputs. Its status was `Up (healthy)`, logs showed Waitress listening on port 5000, and in-container checks confirmed Flask, scikit-learn, joblib, Waitress, and `/app/model.pkl`. Stop/start succeeded and health passed after restart; the container was then removed. The image remains locally as `gradecast:1.0`. The current local Flask process may occupy host port 5000, so the example maps host port 5001 to container port 5000.

From the project root in PowerShell:

```powershell
docker build -t gradecast:1.0 .
docker image inspect gradecast:1.0 --format '{{.Id}}'
docker run --detach --name gradecast -p 5001:5000 gradecast:1.0
docker ps --filter "name=gradecast"
docker logs gradecast
Invoke-RestMethod -Uri "http://127.0.0.1:5001/health"
```

Open <http://127.0.0.1:5001/> and submit the form. Test a JSON prediction using the same PowerShell request above, changing the port to 5001. Confirm the response is a real result before recording Practical 2 as complete.

Container lifecycle commands, run only after confirming the named container exists:

```powershell
docker stop gradecast
docker start gradecast
docker ps --filter "name=gradecast"
docker rm -f gradecast
```

Do not report an image ID, container state, logs, or successful endpoint check until those commands have actually succeeded.

## Practical 3: AWS EC2

**Status: pending.** AWS CLI was not found, no AWS account session or billing approval was available to this workspace, and no EC2 resource has been created. No public IP or deployment URL is claimed. The AWS Console is a valid alternative to AWS CLI for this practical.

### Cost and Security Check Before Launch

EC2 compute time, EBS storage, public IPv4 addresses, snapshots, and data transfer can incur charges. Before launching, check the current price for the selected region and instance type in the AWS Pricing Calculator and the EC2 launch summary. Confirm your account's current free-tier/credit eligibility; do not assume an instance is free. Stop or terminate the instance promptly after the practical and review/delete unused EBS volumes and snapshots. Stopping an instance does not necessarily stop storage or public-address charges.

Never paste credentials, passwords, access keys, or private keys into chat or commit them to this repository. Store the downloaded `.pem` key outside the project, for example under `%USERPROFILE%\.ssh\`, and keep it private.

### Console Deployment Outline

1. Sign in to the AWS Console and select Mumbai (`ap-south-1`) if it is available and suitable for your account.
2. In EC2, launch a current Ubuntu Server LTS image. Choose the smallest instance type that the console confirms is suitable and covered by your available free-tier eligibility or credits; check the price before launch.
3. Create/select a key pair and download the private key to `%USERPROFILE%\.ssh\gradecast-ap-south-1.pem`, not into this project.
4. Configure the security group: allow SSH (TCP 22) from **My IP** only. For a publicly viewable assignment page, allow TCP 5000 from the required audience; use your IP only if only you need to verify it. Do not open unrelated ports.
5. Record the actual public IPv4 address shown by EC2. Connect from PowerShell, substituting that real address:

   ```powershell
   ssh -i "$env:USERPROFILE\.ssh\gradecast-ap-south-1.pem" ubuntu@<ACTUAL_EC2_PUBLIC_IP>
   ```

6. In the remote Ubuntu SSH session only, install and start Docker:

   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io
   sudo systemctl enable --now docker
   sudo usermod -aG docker "$USER"
   exit
   ```

   Reconnect, then verify `docker --version` and `sudo docker info` before proceeding. Use `sudo docker` if group access is not active yet.

7. Reconnect and create the destination folder on Ubuntu:

   ```bash
   mkdir -p ~/gradecast
   ```

8. From a second local PowerShell terminal in the project root, transfer only the application files and model (use the actual key path):

   ```powershell
   scp -i "$env:USERPROFILE\.ssh\gradecast-ap-south-1.pem" .\Dockerfile .\.dockerignore .\requirements.txt .\app.py .\train_model.py .\model.pkl .\templates .\static ubuntu@<ACTUAL_EC2_PUBLIC_IP>:~/gradecast/
   ```

9. On Ubuntu, build and start the container:

   ```bash
   cd ~/gradecast
   sudo docker build -t gradecast:1.0 .
   sudo docker run --detach --restart unless-stopped --name gradecast -p 5000:5000 gradecast:1.0
   sudo docker ps
   sudo docker logs --tail 50 gradecast
   curl http://127.0.0.1:5000/health
   ```

10. From local PowerShell, verify `http://<ACTUAL_EC2_PUBLIC_IP>:5000/health`, open `http://<ACTUAL_EC2_PUBLIC_IP>:5000/`, and submit a real prediction. Only after these checks pass, record the actual URL here: **AWS deployment URL: Pending real EC2 deployment and verification.**
11. When finished, stop/remove the container and stop or terminate the EC2 instance. For no further use, terminate it and inspect/delete any unattached EBS volumes or snapshots. Verify the final AWS billing/resources page.

## GitHub

The workspace was not an existing Git repository and had no remote when inspected. A local repository has now been initialized with commit `d459495` (`Build GradeCast student marks prediction app`). The `.gitignore` excludes `.venv`, Python caches, local environment files, credentials, and private keys; `model.pkl` is intentionally retained because the app requires it.

No GitHub repository URL is verified yet: **GitHub repository: Pending repository creation and push.** Create an empty repository in your GitHub account, then from this folder add its actual URL and push the current branch:

```powershell
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY>.git
git push -u origin HEAD
```

Replace the URL placeholders with the repository you created. If a remote already exists by then, inspect it with `git remote -v` and do not add a duplicate. Complete GitHub authentication in the browser or credential manager; do not put tokens in commands, source files, or chat. After a successful push, replace the pending repository value above with the verified URL.

## Practical Screenshot Checklist

Capture your own readable screenshots only after each corresponding check succeeds. Save them in a `screenshots/` directory if desired. Do not use fabricated terminal output or screenshots as deployment evidence.

| Practical | Suggested filename | What to show |
| --- | --- | --- |
| 1: training and metrics | `p1-model-training.png` | VS Code PowerShell in the project folder showing the training command, split sizes, saved model, and MAE/MSE/RMSE/R-squared output |
| 1: successful web prediction | `p1-gradecast-prediction.png` | Browser at the local GradeCast URL, entered values, and the displayed prediction |
| 1: tests and health | `p1-tests-health.png` | Test terminal with all tests passing and browser/terminal showing the successful `/health` response |
| 2: image build | `p2-docker-image.png` | Docker build success and `docker image inspect` or `docker images` showing `gradecast:1.0` |
| 2: running container | `p2-container-running.png` | Docker Desktop or terminal showing the running container and port mapping |
| 2: container prediction | `p2-container-prediction.png` | Browser at the container-mapped URL with a genuine prediction result |
| 2: health and lifecycle | `p2-container-health-logs.png` | Successful container `/health`, logs, and stop/start status (capture before removing it) |
| 3: instance and security | `p3-ec2-security-group.png` | AWS Console showing the real running instance, region, and inbound SSH restricted to your IP |
| 3: Docker on EC2 | `p3-ec2-container.png` | SSH terminal showing Docker version, running container, and relevant logs |
| 3: public deployment | `p3-public-prediction.png` | Browser at the actual EC2 public URL with a real prediction and a successful health check |
| 3: cleanup | `p3-aws-cleanup.png` | AWS Console showing the instance stopped/terminated and no unintended running resource |

No screenshots have been captured for this workspace yet. Practical 2 and 3 screenshots are pending until their actual Docker/AWS checks succeed.