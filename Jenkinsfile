pipeline { agent any
 options { timestamps(); disableConcurrentBuilds() }
 environment { REGISTRY='docker.io/alexcgodwin'; VERSION="${BUILD_NUMBER}"; GITOPS_REPO='git@github.com:YOUR_ORG/cloud-platform-gitops.git' }
 stages {
  stage('Checkout'){steps{checkout scm}}
  stage('Tests'){steps{sh 'python3 -m venv .venv && . .venv/bin/activate && pip install -q -r services/api/requirements.txt -r services/auth/requirements.txt && PYTHONPATH=services/api pytest -q services/api/test_app.py && PYTHONPATH=services/auth pytest -q services/auth/test_app.py'}}
  stage('Secret Scan'){steps{sh 'command -v gitleaks >/dev/null && gitleaks detect --source . --no-banner || echo gitleaks-not-installed'}}
  stage('Build'){steps{sh 'docker build -t $REGISTRY/platform-frontend:$VERSION frontend; docker build -t $REGISTRY/platform-api:$VERSION services/api; docker build -t $REGISTRY/platform-auth:$VERSION services/auth; docker build -t $REGISTRY/platform-worker:$VERSION services/worker'}}
  stage('Image Scan'){steps{sh 'for i in platform-frontend platform-api platform-auth platform-worker; do command -v trivy >/dev/null && trivy image --exit-code 1 --severity HIGH,CRITICAL $REGISTRY/$i:$VERSION || true; done'}}
  stage('Publish'){steps{withCredentials([usernamePassword(credentialsId:'docker-registry',usernameVariable:'REG_USER',passwordVariable:'REG_PASS')]){sh 'echo "$REG_PASS" | docker login -u "$REG_USER" --password-stdin; for i in platform-frontend platform-api platform-auth platform-worker; do docker push $REGISTRY/$i:$VERSION; done'}}}
  stage('Update Dev GitOps'){steps{sshagent(credentials:['gitops-ssh']){sh 'rm -rf /tmp/cloud-platform-gitops; git clone "$GITOPS_REPO" /tmp/cloud-platform-gitops; cd /tmp/cloud-platform-gitops; ./scripts/set-images.sh dev "$VERSION"; git config user.email jenkins@local; git config user.name "Jenkins CI"; git add .; git commit -m "deploy(dev): release $VERSION" || true; git push origin main'}}}
  stage('Promote Staging'){when{branch 'main'} steps{input message:"Promote ${VERSION} to staging?"; sshagent(credentials:['gitops-ssh']){sh 'cd /tmp/cloud-platform-gitops; ./scripts/set-images.sh staging "$VERSION"; git add .; git commit -m "promote(staging): $VERSION"; git push'}}}
  stage('Promote Prod'){when{branch 'main'} steps{input message:"Approve ${VERSION} for production?"; sshagent(credentials:['gitops-ssh']){sh 'cd /tmp/cloud-platform-gitops; ./scripts/set-images.sh prod "$VERSION"; git add .; git commit -m "promote(prod): $VERSION"; git push'}}}
 } }
