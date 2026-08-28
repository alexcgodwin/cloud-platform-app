pipeline {

    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        AWS_REGION   = 'ca-central-1'
        ECR_REGISTRY = '221082176287.dkr.ecr.ca-central-1.amazonaws.com'
        ECR_PREFIX   = 'portfolio-dev'
        VERSION      = "build-${BUILD_NUMBER}"
        GITOPS_REPO  = 'https://github.com/alexcgodwin/cloud-platform-gitops.git'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }


        stage('Tests') {
            steps {
                sh '''#!/usr/bin/env bash
set -euo pipefail

rm -rf .venv

python3 -m venv .venv

. .venv/bin/activate

pip install -q \
    -r services/api/requirements.txt \
    -r services/auth/requirements.txt

PYTHONPATH=services/api \
    pytest -q services/api/test_app.py

PYTHONPATH=services/auth \
    pytest -q services/auth/test_app.py
'''
            }
        }


        stage('Build Images') {
            steps {
                sh '''#!/usr/bin/env bash
set -euo pipefail

docker build \
    -t "$ECR_REGISTRY/$ECR_PREFIX/platform-frontend:$VERSION" \
    frontend

docker build \
    -t "$ECR_REGISTRY/$ECR_PREFIX/platform-api:$VERSION" \
    services/api

docker build \
    -t "$ECR_REGISTRY/$ECR_PREFIX/platform-auth:$VERSION" \
    services/auth

docker build \
    -t "$ECR_REGISTRY/$ECR_PREFIX/platform-worker:$VERSION" \
    services/worker
'''
            }
        }


        stage('Publish to Amazon ECR') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {

                    sh '''#!/usr/bin/env bash
set -euo pipefail

export AWS_DEFAULT_REGION="$AWS_REGION"

aws sts get-caller-identity > /dev/null

aws ecr get-login-password \
    --region "$AWS_REGION" |
docker login \
    --username AWS \
    --password-stdin "$ECR_REGISTRY"

for image in \
    platform-frontend \
    platform-api \
    platform-auth \
    platform-worker
do
    docker push \
        "$ECR_REGISTRY/$ECR_PREFIX/$image:$VERSION"
done
'''
                }
            }
        }


        stage('Update Dev GitOps') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-gitops-credentials',
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_TOKEN'
                    )
                ]) {

                    sh '''#!/usr/bin/env bash
set -euo pipefail

rm -rf /tmp/cloud-platform-gitops
rm -f /tmp/git-askpass.sh

cat > /tmp/git-askpass.sh <<'EOF'
#!/usr/bin/env sh

case "$1" in
    *Username*)
        printf '%s\\n' "$GIT_USER"
        ;;
    *Password*)
        printf '%s\\n' "$GIT_TOKEN"
        ;;
esac
EOF

chmod 700 /tmp/git-askpass.sh

export GIT_ASKPASS=/tmp/git-askpass.sh
export GIT_TERMINAL_PROMPT=0

git clone \
    "$GITOPS_REPO" \
    /tmp/cloud-platform-gitops

cd /tmp/cloud-platform-gitops

bash ./scripts/set-images.sh \
    dev \
    "$VERSION"

git config user.email \
    "jenkins@alexcg.local"

git config user.name \
    "Jenkins CI"

git add environments/dev/kustomization.yaml

git commit \
    -m "deploy(dev): release $VERSION"

git push origin main
'''
                }
            }
        }


        stage('Approve Staging') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    input(
                        message: "Promote ${VERSION} to staging?",
                        ok: 'Promote to Staging'
                    )
                }
            }
        }


        stage('Promote to Staging') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-gitops-credentials',
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_TOKEN'
                    )
                ]) {

                    sh '''#!/usr/bin/env bash
set -euo pipefail

rm -rf /tmp/cloud-platform-gitops
rm -f /tmp/git-askpass.sh

cat > /tmp/git-askpass.sh <<'EOF'
#!/usr/bin/env sh

case "$1" in
    *Username*)
        printf '%s\\n' "$GIT_USER"
        ;;
    *Password*)
        printf '%s\\n' "$GIT_TOKEN"
        ;;
esac
EOF

chmod 700 /tmp/git-askpass.sh

export GIT_ASKPASS=/tmp/git-askpass.sh
export GIT_TERMINAL_PROMPT=0

git clone \
    "$GITOPS_REPO" \
    /tmp/cloud-platform-gitops

cd /tmp/cloud-platform-gitops

bash ./scripts/set-images.sh \
    staging \
    "$VERSION"

git config user.email \
    "jenkins@alexcg.local"

git config user.name \
    "Jenkins CI"

git add environments/staging/kustomization.yaml

git commit \
    -m "deploy(staging): release $VERSION"

git push origin main
'''
                }
            }
        }


        stage('Approve Production') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    input(
                        message: "Promote ${VERSION} to production?",
                        ok: 'Promote to Production'
                    )
                }
            }
        }


        stage('Promote to Production') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-gitops-credentials',
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_TOKEN'
                    )
                ]) {

                    sh '''#!/usr/bin/env bash
set -euo pipefail

rm -rf /tmp/cloud-platform-gitops
rm -f /tmp/git-askpass.sh

cat > /tmp/git-askpass.sh <<'EOF'
#!/usr/bin/env sh

case "$1" in
    *Username*)
        printf '%s\\n' "$GIT_USER"
        ;;
    *Password*)
        printf '%s\\n' "$GIT_TOKEN"
        ;;
esac
EOF

chmod 700 /tmp/git-askpass.sh

export GIT_ASKPASS=/tmp/git-askpass.sh
export GIT_TERMINAL_PROMPT=0

git clone \
    "$GITOPS_REPO" \
    /tmp/cloud-platform-gitops

cd /tmp/cloud-platform-gitops

bash ./scripts/set-images.sh \
    prod \
    "$VERSION"

git config user.email \
    "jenkins@alexcg.local"

git config user.name \
    "Jenkins CI"

git add environments/prod/kustomization.yaml

git commit \
    -m "deploy(prod): release $VERSION"

git push origin main
'''
                }
            }
        }
    }


    post {

        always {

            sh '''
                rm -rf /tmp/cloud-platform-gitops || true
                rm -f /tmp/git-askpass.sh || true
                docker logout "$ECR_REGISTRY" >/dev/null 2>&1 || true
            '''
        }
    }
}